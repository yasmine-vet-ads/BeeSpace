/**
 * BeeSpace - firmware de produção para biossensor inteligente de colmeias.
 *
 * Alvo: ESP32-S3 DevKitC-1 / PlatformIO / Arduino Framework.
 * Arquitetura: FreeRTOS + EventGroups + mutexes + MQTT/JSON + deep sleep agressivo.
 *
 * O GPS é energizado por MOSFET somente quando há necessidade real:
 *   - uma vez a cada 24 horas para atualização de geolocalização; ou
 *   - imediatamente em wake EXT1 causado pelo INT do MPU6050, indicando possível furto.
 */

#include <Arduino.h>
#include <math.h>
#include <freertos/FreeRTOS.h>
#include <freertos/event_groups.h>
#include <freertos/semphr.h>
#include <freertos/task.h>
#include <Wire.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <TinyGPSPlus.h>
#include <Adafruit_BME280.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <BH1750.h>
#include <HX711.h>
#include <driver/i2s.h>
#include <esp_idf_version.h>
#include <esp_sleep.h>
#include <esp_wifi.h>

// -----------------------------------------------------------------------------
// Credenciais simuladas: em produção, substituir por NVS/provisioning seguro.
// -----------------------------------------------------------------------------
#define WIFI_SSID "BeeSpace_Field_WiFi"
#define WIFI_PASSWORD "troque-esta-senha"
#define MQTT_HOST "broker.beespace.local"
#define MQTT_PORT 1883
#define MQTT_USER "beespace-node"
#define MQTT_PASSWORD "troque-este-token"
#define MQTT_TOPIC_TELEMETRY "beespace/hives/hive-001/telemetry"
#define MQTT_TOPIC_ALERTS "beespace/hives/hive-001/alerts"
#define DEVICE_ID "beespace-hive-001"

// -----------------------------------------------------------------------------
// Agenda, timeouts e janelas de operação.
// -----------------------------------------------------------------------------
static constexpr uint64_t SCHEDULER_TICK_SECONDS = 15ULL * 60ULL;
static constexpr uint32_t ACTIVE_COUNT_WINDOW_MS = 8000;
static constexpr uint32_t SENSOR_TASK_TIMEOUT_MS = 15000;
static constexpr uint32_t WIFI_CONNECT_TIMEOUT_MS = 20000;
static constexpr uint32_t MQTT_CONNECT_TIMEOUT_MS = 15000;
static constexpr uint32_t MQTT_PUBLISH_GRACE_MS = 500;
static constexpr uint32_t GPS_FIX_TIMEOUT_MS = 3UL * 60UL * 1000UL;
static constexpr uint32_t GPS_BAUD = 9600;

static constexpr uint32_t ENVIRONMENT_INTERVAL_MINUTES = 120;
static constexpr uint32_t AUDIO_INTERVAL_MINUTES = 30;
static constexpr uint32_t GPS_INTERVAL_HOURS = 24;
static constexpr uint32_t SCALE_INTERVAL_DAYS = 7;
static constexpr uint32_t ENVIRONMENT_INTERVAL_TICKS =
    (ENVIRONMENT_INTERVAL_MINUTES * 60UL) / SCHEDULER_TICK_SECONDS;
static constexpr uint32_t AUDIO_INTERVAL_TICKS =
    (AUDIO_INTERVAL_MINUTES * 60UL) / SCHEDULER_TICK_SECONDS;
static constexpr uint32_t GPS_INTERVAL_TICKS =
    (GPS_INTERVAL_HOURS * 60UL * 60UL) / SCHEDULER_TICK_SECONDS;
static constexpr uint32_t SCALE_INTERVAL_TICKS =
    (SCALE_INTERVAL_DAYS * 24UL * 60UL * 60UL) / SCHEDULER_TICK_SECONDS;

// -----------------------------------------------------------------------------
// Pinout ESP32-S3.
// -----------------------------------------------------------------------------
static constexpr gpio_num_t PIN_I2C_SDA = GPIO_NUM_8;
static constexpr gpio_num_t PIN_I2C_SCL = GPIO_NUM_9;

static constexpr gpio_num_t PIN_I2S_BCLK = GPIO_NUM_12;
static constexpr gpio_num_t PIN_I2S_WS = GPIO_NUM_13;
static constexpr gpio_num_t PIN_I2S_DIN = GPIO_NUM_14;

static constexpr gpio_num_t PIN_TCRT_ENTRY = GPIO_NUM_4;
static constexpr gpio_num_t PIN_TCRT_EXIT = GPIO_NUM_5;
static constexpr gpio_num_t PIN_MPU_INT = GPIO_NUM_6;

static constexpr uint8_t GPS_EN_PIN = 7;
static constexpr int8_t GPS_RX_PIN = 43; // ESP32-S3 RX <- TX do NEO-6M.
static constexpr int8_t GPS_TX_PIN = 44; // ESP32-S3 TX -> RX do NEO-6M.

static constexpr uint8_t PIN_HX711_DOUT = 16;
static constexpr uint8_t PIN_HX711_SCK = 17;
static constexpr uint8_t PIN_BATTERY_ADC = 1;
static constexpr uint8_t PIN_STATUS_LED = 21;

static constexpr uint64_t WAKEUP_PIN_MASK =
    (1ULL << static_cast<uint8_t>(PIN_TCRT_ENTRY)) |
    (1ULL << static_cast<uint8_t>(PIN_TCRT_EXIT)) |
    (1ULL << static_cast<uint8_t>(PIN_MPU_INT));

// -----------------------------------------------------------------------------
// Sensores e calibração.
// -----------------------------------------------------------------------------
static constexpr uint8_t BME280_ADDR = 0x76;
static constexpr uint8_t MPU6050_ADDR = 0x68;
static constexpr float SEALEVELPRESSURE_HPA = 1013.25F;
static constexpr float HX711_CALIBRATION_FACTOR = -7050.0F;
static constexpr long HX711_OFFSET = 0L;
static constexpr float BATTERY_DIVIDER_RATIO = 2.0F;
static constexpr float ADC_REFERENCE_MV = 3300.0F;
static constexpr uint16_t ADC_MAX_READING = 4095;

static constexpr i2s_port_t I2S_PORT = I2S_NUM_0;
static constexpr uint32_t I2S_SAMPLE_RATE = 16000;
static constexpr size_t I2S_DMA_SAMPLES = 512;
static constexpr uint32_t AUDIO_CAPTURE_MS = 5UL * 60UL * 1000UL;

static constexpr uint32_t TCRT_DEBOUNCE_US = 6000;


struct HiveTelemetry {
  char deviceId[32];
  uint32_t bootCount;
  uint32_t scheduleTick;
  esp_sleep_wakeup_cause_t wakeupCause;
  uint64_t ext1WakeMask;

  uint32_t beeEntriesTotal;
  uint32_t beeExitsTotal;
  uint32_t beeEntriesSession;
  uint32_t beeExitsSession;
  bool theftAlert;
  uint32_t theftEventsTotal;

  float temperatureC;
  float humidityPct;
  float pressureHpa;
  float altitudeM;
  float weightKg;
  float luminosityLux;
  float weightKg;
  float batteryVoltage;
  uint8_t batteryPct;

  float accelX;
  float accelY;
  float accelZ;
  float gyroX;
  float gyroY;
  float gyroZ;

  float audioRms;
  int32_t audioPeak;
  float zeroCrossingRate;

  double latitude;
  double longitude;
  double altitudeGpsM;
  double speedKmph;
  double courseDeg;
  uint32_t gpsAgeMs;
  uint32_t gpsSatellites;
  bool gpsFixValid;
  bool gpsTimeout;
  bool gpsPowerCycled;

  bool environmentFresh;
  bool audioFresh;
  bool scaleFresh;
  bool batteryFresh;
  bool imuFresh;
  bool countersFresh;
  bool gpsFresh;

  bool bmeOk;
  bool bh1750Ok;
  bool hx711Ok;
  bool mpuOk;
  bool audioOk;
  bool gpsOk;
  bool mqttOk;
};

static HiveTelemetry telemetry = {};
static SemaphoreHandle_t telemetryMutex;
static EventGroupHandle_t cycleEvents;

static constexpr EventBits_t BIT_AUDIO_DONE = BIT0;
static constexpr EventBits_t BIT_SENSORS_DONE = BIT1;
static constexpr EventBits_t BIT_MQTT_DONE = BIT2;

struct AcquisitionSchedule {
  bool firstBoot;
  bool timerWake;
  bool extWake;
  bool mpuWake;
  bool environmentDue;
  bool audioDue;
  bool scaleDue;
  bool gpsDue;
  bool eventWake;
  bool shouldReadBattery;
  bool shouldReadMpu;
  bool publishExpected;
};

static HiveTelemetry telemetry = {};
static AcquisitionSchedule acquisitionSchedule = {};
static SemaphoreHandle_t telemetryMutex;
static SemaphoreHandle_t i2cMutex;
static EventGroupHandle_t cycleEvents;

static constexpr EventBits_t BIT_AUDIO_DONE = BIT0;
static constexpr EventBits_t BIT_I2C_DONE = BIT1;
static constexpr EventBits_t BIT_GPS_DONE = BIT2;
static constexpr EventBits_t BIT_MQTT_DONE = BIT3;

static WiFiClient wifiClient;
static PubSubClient mqttClient(wifiClient);
static Adafruit_BME280 bme;
static Adafruit_MPU6050 mpu;
static BH1750 lightMeter;
static HX711 scale;
static HardwareSerial gpsSerial(1);
static TinyGPSPlus gps;

// RTC RAM: preservada em deep sleep.
RTC_DATA_ATTR uint32_t rtcBootCount = 0;
RTC_DATA_ATTR uint32_t rtcScheduleTick = 0;
RTC_DATA_ATTR uint32_t rtcBeeEntriesTotal = 0;
RTC_DATA_ATTR uint32_t rtcBeeExitsTotal = 0;
RTC_DATA_ATTR uint32_t rtcTheftEventsTotal = 0;
RTC_DATA_ATTR uint32_t rtcLastGpsTick = 0;

static portMUX_TYPE isrMux = portMUX_INITIALIZER_UNLOCKED;
static volatile uint32_t sessionEntries = 0;
static volatile uint32_t sessionExits = 0;
static volatile uint32_t lastEntryPulseUs = 0;
static volatile uint32_t lastExitPulseUs = 0;
static volatile bool theftInterruptSeen = false;

void IRAM_ATTR onEntryBeamBreak() {
  const uint32_t now = micros();
    portENTER_CRITICAL_ISR(&isrMux);
  if ((now - lastEntryPulseUs) > TCRT_DEBOUNCE_US) {
    sessionEntries++;
    lastEntryPulseUs = now;
    portEXIT_CRITICAL_ISR(&isrMux);
  }
}

void IRAM_ATTR onExitBeamBreak() {
  const uint32_t now = micros();
    portENTER_CRITICAL_ISR(&isrMux);
  if ((now - lastExitPulseUs) > TCRT_DEBOUNCE_US) {
    sessionExits++;
    lastExitPulseUs = now;
  }
      portEXIT_CRITICAL_ISR(&isrMux);
}

void IRAM_ATTR onMpuMotionAlert() {
  portENTER_CRITICAL_ISR(&isrMux);
  theftInterruptSeen = true;
  portEXIT_CRITICAL_ISR(&isrMux);
}

static uint8_t batteryPercentFromVoltage(float voltage) {

  if (voltage >= 4.20F) return 100;
  if (voltage >= 4.10F) return 90;
  if (voltage >= 4.00F) return 80;
  if (voltage >= 3.92F) return 70;
  if (voltage >= 3.85F) return 60;
  if (voltage >= 3.79F) return 50;
  if (voltage >= 3.73F) return 40;
  if (voltage >= 3.68F) return 30;
  if (voltage >= 3.60F) return 20;
  if (voltage >= 3.45F) return 10;
  return 0;
}

static float readBatteryVoltage() {
  uint32_t rawSum = 0;
  constexpr uint8_t samples = 16;
  for (uint8_t i = 0; i < samples; i++) {
    rawSum += analogRead(PIN_BATTERY_ADC);
    delay(2);
  }
  const float raw = static_cast<float>(rawSum) / samples;
  const float pinVoltage = (raw / ADC_MAX_READING) * (ADC_REFERENCE_MV / 1000.0F);
  return pinVoltage * BATTERY_DIVIDER_RATIO;
}

static bool isFirstBoot() {
  return rtcBootCount == 1;
}
static bool didWakeFromMpu(uint64_t ext1WakeMask) {
  return (ext1WakeMask & (1ULL << static_cast<uint8_t>(PIN_MPU_INT))) != 0;
}
static void updateSchedulerTick(esp_sleep_wakeup_cause_t wakeupCause) {
  if (wakeupCause == ESP_SLEEP_WAKEUP_TIMER) {
    rtcScheduleTick++;
  }
}

static AcquisitionSchedule determineAcquisitionSchedule(esp_sleep_wakeup_cause_t wakeupCause,
                                                        uint64_t ext1WakeMask) {
  AcquisitionSchedule schedule = {};
  schedule.firstBoot = isFirstBoot();
  schedule.timerWake = wakeupCause == ESP_SLEEP_WAKEUP_TIMER;
  schedule.extWake = wakeupCause == ESP_SLEEP_WAKEUP_EXT1;
  schedule.mpuWake = schedule.extWake && didWakeFromMpu(ext1WakeMask);
  schedule.environmentDue = schedule.firstBoot ||
                            (schedule.timerWake && (rtcScheduleTick % ENVIRONMENT_INTERVAL_TICKS == 0));
  schedule.audioDue = schedule.firstBoot ||
                      (schedule.timerWake && (rtcScheduleTick % AUDIO_INTERVAL_TICKS == 0));
  schedule.scaleDue = schedule.firstBoot ||
                      (schedule.timerWake && (rtcScheduleTick % SCALE_INTERVAL_TICKS == 0));
  schedule.gpsDue = schedule.mpuWake || schedule.firstBoot ||
                    (schedule.timerWake && ((rtcScheduleTick - rtcLastGpsTick) >= GPS_INTERVAL_TICKS));
  schedule.eventWake = schedule.extWake;
  schedule.publishExpected = schedule.environmentDue || schedule.audioDue || schedule.scaleDue ||
                             schedule.gpsDue || schedule.eventWake;
  schedule.shouldReadBattery = schedule.publishExpected;
  schedule.shouldReadMpu = schedule.publishExpected;
  return schedule;
}

static void seedWakeupEventsFromExt1(uint64_t wakeMask) {
  if (!acquisitionSchedule.extWake) {
    return;
  }

    portENTER_CRITICAL(&isrMux);
  if (wakeMask & (1ULL << static_cast<uint8_t>(PIN_TCRT_ENTRY))) {
    sessionEntries++;
  }
  if (wakeMask & (1ULL << static_cast<uint8_t>(PIN_TCRT_EXIT))) {
    sessionExits++;
  }
  if (wakeMask & (1ULL << static_cast<uint8_t>(PIN_MPU_INT))) {
    theftInterruptSeen = true;
  }
  portEXIT_CRITICAL(&isrMux);
}

static bool hasNewDataToPublish(const HiveTelemetry &snapshot) {
  return snapshot.environmentFresh || snapshot.audioFresh || snapshot.scaleFresh || snapshot.batteryFresh ||
         snapshot.imuFresh || snapshot.countersFresh || snapshot.gpsFresh || snapshot.theftAlert;
}

static void copyCountersToTelemetry() {
  uint32_t entries;
  uint32_t exits;
  bool theft;

  portENTER_CRITICAL(&isrMux);
  entries = sessionEntries;
  exits = sessionExits;
  theft = theftInterruptSeen;
  portEXIT_CRITICAL(&isrMux);

  rtcBeeEntriesTotal += entries;
  rtcBeeExitsTotal += exits;
  if (theft) {
    rtcTheftEventsTotal++;
  }

  if (xSemaphoreTake(telemetryMutex, pdMS_TO_TICKS(1000)) == pdTRUE) {
    telemetry.beeEntriesSession = entries;
    telemetry.beeExitsSession = exits;
    telemetry.beeEntriesTotal = rtcBeeEntriesTotal;
    telemetry.beeExitsTotal = rtcBeeExitsTotal;
    telemetry.theftAlert = theft;
    telemetry.theftEventsTotal = rtcTheftEventsTotal;
    telemetry.countersFresh = entries > 0 || exits > 0;
    xSemaphoreGive(telemetryMutex);
  }
}

static const char *wakeupCauseToString(esp_sleep_wakeup_cause_t cause) {
  switch (cause) {
    case ESP_SLEEP_WAKEUP_TIMER: return "timer";
    case ESP_SLEEP_WAKEUP_EXT0: return "ext0";
    case ESP_SLEEP_WAKEUP_EXT1: return "ext1";
    case ESP_SLEEP_WAKEUP_TOUCHPAD: return "touchpad";
    case ESP_SLEEP_WAKEUP_ULP: return "ulp";
    default: return "power_on_or_reset";
  }
}

static bool setupI2sMicrophone() {
  const i2s_config_t i2sConfig = {
      .mode = static_cast<i2s_mode_t>(I2S_MODE_MASTER | I2S_MODE_RX),
      .sample_rate = I2S_SAMPLE_RATE,
      .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
      .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
#if ESP_IDF_VERSION_MAJOR >= 5
      .communication_format = I2S_COMM_FORMAT_STAND_I2S,
#else
      .communication_format = I2S_COMM_FORMAT_I2S,
#endif
      .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
      .dma_buf_count = 4,
      .dma_buf_len = I2S_DMA_SAMPLES,
      .use_apll = false,
      .tx_desc_auto_clear = false,
      .fixed_mclk = 0};

  const i2s_pin_config_t pinConfig = {
      .bck_io_num = static_cast<int>(PIN_I2S_BCLK),
      .ws_io_num = static_cast<int>(PIN_I2S_WS),
      .data_out_num = I2S_PIN_NO_CHANGE,
      .data_in_num = static_cast<int>(PIN_I2S_DIN)};

  if (i2s_driver_install(I2S_PORT, &i2sConfig, 0, nullptr) != ESP_OK) {
    return false;
  }
  if (i2s_set_pin(I2S_PORT, &pinConfig) != ESP_OK) {
    i2s_driver_uninstall(I2S_PORT);
    return false;
  }
  i2s_zero_dma_buffer(I2S_PORT);
  return true;
}

static void setupMpuInterruptMode() {
  mpu.setHighPassFilter(MPU6050_HIGHPASS_0_63_HZ);
  mpu.setMotionDetectionThreshold(6);
  mpu.setMotionDetectionDuration(20);
  mpu.setInterruptPinLatch(true);
  mpu.setInterruptPinPolarity(true);
  mpu.setMotionInterrupt(true);
}

static void TaskAudio(void *parameter) {
  (void)parameter;

  if (!acquisitionSchedule.audioDue) {
    xEventGroupSetBits(cycleEvents, BIT_AUDIO_DONE);
    vTaskDelete(nullptr);
  }

  float rms = 0.0F;
  int32_t peak = 0;
  float zeroCrossingRate = 0.0F;
  bool audioOk = setupI2sMicrophone();

  if (audioOk) {
    int32_t buffer[I2S_DMA_SAMPLES];
    uint64_t sumSquares = 0;
    uint32_t sampleCount = 0;
    uint32_t zeroCrossings = 0;
    int32_t previousSample = 0;
    const uint32_t startMs = millis();

    while ((millis() - startMs) < AUDIO_CAPTURE_MS) {
      size_t bytesRead = 0;
      const esp_err_t result = i2s_read(I2S_PORT, buffer, sizeof(buffer), &bytesRead, pdMS_TO_TICKS(250));
      if (result != ESP_OK || bytesRead == 0) {
        continue;
      }

      const size_t samplesRead = bytesRead / sizeof(int32_t);
      for (size_t i = 0; i < samplesRead; i++) {
        const int32_t sample = buffer[i] >> 14;
        const int32_t absSample = abs(sample);
        peak = max(peak, absSample);
        const int64_t sample64 = static_cast<int64_t>(sample);
        sumSquares += static_cast<uint64_t>(sample64 * sample64);
        if (sampleCount > 0 && ((sample >= 0 && previousSample < 0) ||
                                (sample < 0 && previousSample >= 0))) {
        }
        previousSample = sample;
        sampleCount++;
      }
    }

    if (sampleCount > 0) {
      rms = sqrt(static_cast<double>(sumSquares) / sampleCount);
      zeroCrossingRate = static_cast<float>(zeroCrossings) / static_cast<float>(sampleCount);
    }

    i2s_driver_uninstall(I2S_PORT);
  }

  if (xSemaphoreTake(telemetryMutex, pdMS_TO_TICKS(1000)) == pdTRUE) {
    telemetry.audioRms = rms;
    telemetry.audioPeak = peak;
    telemetry.zeroCrossingRate = zeroCrossingRate;
    telemetry.audioFresh = true;
    telemetry.audioOk = audioOk;
    xSemaphoreGive(telemetryMutex);
  }

  xEventGroupSetBits(cycleEvents, BIT_AUDIO_DONE);
  vTaskDelete(nullptr);
}

static void TaskI2C(void *parameter) {
  (void)parameter;

  HiveTelemetry local = {};

  if (xSemaphoreTake(i2cMutex, pdMS_TO_TICKS(2000)) == pdTRUE) {
    if (acquisitionSchedule.environmentDue) {
      local.bmeOk = bme.begin(BME280_ADDR, &Wire);
      local.bh1750Ok = lightMeter.begin(BH1750::ONE_TIME_HIGH_RES_MODE, 0x23, &Wire);

      if (local.bmeOk) {
        local.temperatureC = bme.readTemperature();
        local.humidityPct = bme.readHumidity();
        local.pressureHpa = bme.readPressure() / 100.0F;
        local.altitudeM = bme.readAltitude(SEALEVELPRESSURE_HPA);
      }

    }

      if (local.bh1750Ok) {
        delay(180);
        local.luminosityLux = lightMeter.readLightLevel();
    if (acquisitionSchedule.shouldReadMpu) {
      local.mpuOk = mpu.begin(MPU6050_ADDR, &Wire);
      if (local.mpuOk) {
        setupMpuInterruptMode();
        sensors_event_t accel;
        sensors_event_t gyro;
        sensors_event_t temp;
        mpu.getEvent(&accel, &gyro, &temp);
        local.accelX = accel.acceleration.x;
        local.accelY = accel.acceleration.y;
        local.accelZ = accel.acceleration.z;
        local.gyroX = gyro.gyro.x;
        local.gyroY = gyro.gyro.y;
        local.gyroZ = gyro.gyro.z;
      }
    }
    xSemaphoreGive(i2cMutex);
  }

  if (acquisitionSchedule.shouldReadBattery) {
    local.batteryVoltage = readBatteryVoltage();
    local.batteryPct = batteryPercentFromVoltage(local.batteryVoltage);
  }

  if (xSemaphoreTake(telemetryMutex, pdMS_TO_TICKS(1000)) == pdTRUE) {
    telemetry.temperatureC = local.temperatureC;
    telemetry.humidityPct = local.humidityPct;
    telemetry.pressureHpa = local.pressureHpa;
    telemetry.altitudeM = local.altitudeM;
    telemetry.luminosityLux = local.luminosityLux;
    telemetry.weightKg = local.weightKg;
    telemetry.batteryVoltage = local.batteryVoltage;
    telemetry.batteryPct = local.batteryPct;
    telemetry.accelX = local.accelX;
    telemetry.accelY = local.accelY;
    telemetry.accelZ = local.accelZ;
    telemetry.gyroX = local.gyroX;
    telemetry.gyroY = local.gyroY;
    telemetry.gyroZ = local.gyroZ;
    telemetry.environmentFresh = acquisitionSchedule.environmentDue;
    telemetry.scaleFresh = acquisitionSchedule.scaleDue;
    telemetry.batteryFresh = acquisitionSchedule.shouldReadBattery;
    telemetry.imuFresh = acquisitionSchedule.shouldReadMpu;
    telemetry.bmeOk = local.bmeOk;
    telemetry.bh1750Ok = local.bh1750Ok;
    telemetry.hx711Ok = local.hx711Ok;
    telemetry.mpuOk = local.mpuOk;
    xSemaphoreGive(telemetryMutex);
  }

  xEventGroupSetBits(cycleEvents, BIT_I2C_DONE);
  vTaskDelete(nullptr);
}

static void TaskGPS(void *parameter) {
  (void)parameter;

  if (!acquisitionSchedule.gpsDue) {
    digitalWrite(GPS_EN_PIN, LOW);
    xEventGroupSetBits(cycleEvents, BIT_GPS_DONE);
    vTaskDelete(nullptr);
  }

  bool fixValid = false;
  bool timedOut = false;
  uint32_t satellites = 0;
  uint32_t fixAgeMs = 0;
  double latitude = 0.0;
  double longitude = 0.0;
  double altitudeM = 0.0;
  double speedKmph = 0.0;
  double courseDeg = 0.0;

  digitalWrite(GPS_EN_PIN, HIGH);
  delay(250);
  gpsSerial.begin(GPS_BAUD, SERIAL_8N1, GPS_RX_PIN, GPS_TX_PIN);

  const uint32_t startMs = millis();
  while ((millis() - startMs) < GPS_FIX_TIMEOUT_MS) {
    while (gpsSerial.available() > 0) {
      gps.encode(static_cast<char>(gpsSerial.read()));
    }

    satellites = gps.satellites.isValid() ? gps.satellites.value() : 0;
    fixAgeMs = gps.location.age();
    if (gps.location.isValid() && gps.location.age() < 5000 && satellites >= 3) {
      fixValid = true;
      latitude = gps.location.lat();
      longitude = gps.location.lng();
      altitudeM = gps.altitude.isValid() ? gps.altitude.meters() : 0.0;
      speedKmph = gps.speed.isValid() ? gps.speed.kmph() : 0.0;
      courseDeg = gps.course.isValid() ? gps.course.deg() : 0.0;
      break;
    }

    vTaskDelay(pdMS_TO_TICKS(100));
  }

  if (!fixValid) {
    timedOut = true;
  }

  // A tentativa periódica é registrada mesmo em timeout para evitar drenar
  // bateria repetindo cold starts de 3 minutos a cada tick de 15 minutos.
  // Em wake de furto, não mexemos na cadência periódica de 24 horas.
  if (!acquisitionSchedule.mpuWake) {
    rtcLastGpsTick = rtcScheduleTick;
  }

  gpsSerial.end();
  digitalWrite(GPS_EN_PIN, LOW);

  if (xSemaphoreTake(telemetryMutex, pdMS_TO_TICKS(1000)) == pdTRUE) {
    telemetry.latitude = latitude;
    telemetry.longitude = longitude;
    telemetry.altitudeGpsM = altitudeM;
    telemetry.speedKmph = speedKmph;
    telemetry.courseDeg = courseDeg;
    telemetry.gpsAgeMs = fixAgeMs;
    telemetry.gpsSatellites = satellites;
    telemetry.gpsFixValid = fixValid;
    telemetry.gpsTimeout = timedOut;
    telemetry.gpsPowerCycled = true;
    telemetry.gpsFresh = true;
    telemetry.gpsOk = fixValid;
    xSemaphoreGive(telemetryMutex);
  }

  xEventGroupSetBits(cycleEvents, BIT_GPS_DONE);
  vTaskDelete(nullptr);
}

static bool connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(true);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  const uint32_t startMs = millis();
  while (WiFi.status() != WL_CONNECTED && (millis() - startMs) < WIFI_CONNECT_TIMEOUT_MS) {
    delay(250);
  }
  return WiFi.status() == WL_CONNECTED;
}

static bool connectMqtt() {
  mqttClient.setServer(MQTT_HOST, MQTT_PORT);
  mqttClient.setKeepAlive(20);
  mqttClient.setSocketTimeout(8);

  const uint32_t startMs = millis();
  uint8_t attempt = 0;
  while (!mqttClient.connected() && (millis() - startMs) < MQTT_CONNECT_TIMEOUT_MS) {
    char clientId[64];
    snprintf(clientId, sizeof(clientId), "%s-%lu", DEVICE_ID, static_cast<unsigned long>(rtcBootCount));
    if (mqttClient.connect(clientId, MQTT_USER, MQTT_PASSWORD)) {
      return true;
    }

    const uint32_t backoffMs = min<uint32_t>(5000, 500U * (1U << min<uint8_t>(attempt, 3)));
    attempt++;
    delay(backoffMs);
  }
  return mqttClient.connected();
}

static size_t buildTelemetryJson(char *buffer, size_t bufferSize, const HiveTelemetry &snapshot) {
  StaticJsonDocument<2048> doc;

  doc["device_id"] = snapshot.deviceId;
  doc["boot_count"] = snapshot.bootCount;
  doc["schedule_tick"] = snapshot.scheduleTick;
  doc["wakeup"] = wakeupCauseToString(snapshot.wakeupCause);
  doc["ext1_wake_mask"] = snapshot.ext1WakeMask;

  JsonObject schedule = doc["schedule"].to<JsonObject>();
  schedule["tick_seconds"] = SCHEDULER_TICK_SECONDS;
  schedule["environment_interval_min"] = ENVIRONMENT_INTERVAL_MINUTES;
  schedule["audio_interval_min"] = AUDIO_INTERVAL_MINUTES;
  schedule["audio_window_min"] = AUDIO_CAPTURE_MS / 60000UL;
  schedule["gps_interval_hours"] = GPS_INTERVAL_HOURS;
  schedule["scale_interval_days"] = SCALE_INTERVAL_DAYS;

  JsonObject fresh = doc["fresh"].to<JsonObject>();
  fresh["environment"] = snapshot.environmentFresh;
  fresh["audio"] = snapshot.audioFresh;
  fresh["scale"] = snapshot.scaleFresh;
  fresh["battery"] = snapshot.batteryFresh;
  fresh["imu"] = snapshot.imuFresh;
  fresh["counters"] = snapshot.countersFresh;
  fresh["gps"] = snapshot.gpsFresh;

  if (snapshot.countersFresh || snapshot.theftAlert) {
    JsonObject counters = doc["bee_counter"].to<JsonObject>();
    counters["entries_total"] = snapshot.beeEntriesTotal;
    counters["exits_total"] = snapshot.beeExitsTotal;
    counters["entries_session"] = snapshot.beeEntriesSession;
    counters["exits_session"] = snapshot.beeExitsSession;
  }

  if (snapshot.environmentFresh) {
    JsonObject environment = doc["environment"].to<JsonObject>();
    environment["temperature_c"] = snapshot.temperatureC;
    environment["humidity_pct"] = snapshot.humidityPct;
    environment["pressure_hpa"] = snapshot.pressureHpa;
    environment["altitude_m"] = snapshot.altitudeM;
    environment["luminosity_lux"] = snapshot.luminosityLux;
  }

  if (snapshot.scaleFresh) {
    JsonObject scaleJson = doc["scale"].to<JsonObject>();
    scaleJson["weight_kg"] = snapshot.weightKg;
  }

  if (snapshot.imuFresh) {
    JsonObject imu = doc["imu"].to<JsonObject>();
    imu["accel_x"] = snapshot.accelX;
    imu["accel_y"] = snapshot.accelY;
    imu["accel_z"] = snapshot.accelZ;
    imu["gyro_x"] = snapshot.gyroX;
    imu["gyro_y"] = snapshot.gyroY;
    imu["gyro_z"] = snapshot.gyroZ;
  }

  if (snapshot.audioFresh) {
    JsonObject audio = doc["audio"].to<JsonObject>();
    audio["rms"] = snapshot.audioRms;
    audio["peak"] = snapshot.audioPeak;
    audio["zero_crossing_rate"] = snapshot.zeroCrossingRate;
  }

  if (snapshot.batteryFresh) {
    JsonObject battery = doc["battery"].to<JsonObject>();
    battery["voltage"] = snapshot.batteryVoltage;
    battery["percent"] = snapshot.batteryPct;
  }
      if (snapshot.gpsFresh) {
    JsonObject gpsJson = doc["gps"].to<JsonObject>();
    gpsJson["enabled_by_theft"] = acquisitionSchedule.mpuWake;
    gpsJson["power_cycled"] = snapshot.gpsPowerCycled;
    gpsJson["fix_valid"] = snapshot.gpsFixValid;
    gpsJson["timeout"] = snapshot.gpsTimeout;
    gpsJson["satellites"] = snapshot.gpsSatellites;
    gpsJson["age_ms"] = snapshot.gpsAgeMs;
    if (snapshot.gpsFixValid) {
      gpsJson["lat"] = snapshot.latitude;
      gpsJson["lon"] = snapshot.longitude;
      gpsJson["altitude_m"] = snapshot.altitudeGpsM;
      gpsJson["speed_kmph"] = snapshot.speedKmph;
      gpsJson["course_deg"] = snapshot.courseDeg;
    }
  }

  JsonObject health = doc["health"].to<JsonObject>();
  if (snapshot.environmentFresh) {
    health["bme280"] = snapshot.bmeOk;
    health["bh1750"] = snapshot.bh1750Ok;
  }
  if (snapshot.scaleFresh) {
    health["hx711"] = snapshot.hx711Ok;
  }
  if (snapshot.imuFresh) {
    health["mpu6050"] = snapshot.mpuOk;
  }
  if (snapshot.audioFresh) {
    health["audio"] = snapshot.audioOk;
  }
  if (snapshot.gpsFresh) {
    health["gps"] = snapshot.gpsOk;
    health["gps_timeout"] = snapshot.gpsTimeout;
  }
  health["mqtt"] = snapshot.mqttOk;

  JsonObject alert = doc["alert"].to<JsonObject>();
  alert["theft"] = snapshot.theftAlert;
  alert["theft_events_total"] = snapshot.theftEventsTotal;

  return serializeJson(doc, buffer, bufferSize);
}

static void publishCriticalAlertIfNeeded(const HiveTelemetry &snapshot) {
  if (!snapshot.theftAlert || !mqttClient.connected()) {
    return;
  }

  StaticJsonDocument<384> alertDoc;
  alertDoc["device_id"] = snapshot.deviceId;
  alertDoc["priority"] = "critical";
  alertDoc["type"] = "theft_or_tipover";
  alertDoc["wakeup"] = wakeupCauseToString(snapshot.wakeupCause);
  alertDoc["events_total"] = snapshot.theftEventsTotal;
  if (snapshot.gpsFixValid) {
    alertDoc["lat"] = snapshot.latitude;
    alertDoc["lon"] = snapshot.longitude;
  }


  char payload[384];
  serializeJson(alertDoc, payload, sizeof(payload));
  mqttClient.publish(MQTT_TOPIC_ALERTS, payload, false);
}

static void TaskMQTT(void *parameter) {
  (void)parameter;

  const uint32_t dataWaitMs = (acquisitionSchedule.audioDue ? AUDIO_CAPTURE_MS : 0) +
                              (acquisitionSchedule.gpsDue ? GPS_FIX_TIMEOUT_MS : 0) +
                              SENSOR_TASK_TIMEOUT_MS;
  xEventGroupWaitBits(
      cycleEvents,
      BIT_AUDIO_DONE | BIT_I2C_DONE | BIT_GPS_DONE,
      pdFALSE,
      pdTRUE,
      pdMS_TO_TICKS(dataWaitMs));

  copyCountersToTelemetry();

  HiveTelemetry snapshot = {};
  if (xSemaphoreTake(telemetryMutex, pdMS_TO_TICKS(1000)) == pdTRUE) {
    snapshot = telemetry;
    xSemaphoreGive(telemetryMutex);
  }

  bool published = false;
  if (hasNewDataToPublish(snapshot) && connectWiFi() && connectMqtt()) {
    snapshot.mqttOk = true;
    publishCriticalAlertIfNeeded(snapshot);

    char payload[2048];
    const size_t length = buildTelemetryJson(payload, sizeof(payload), snapshot);
    if (length > 0 && length < sizeof(payload)) {
      published = mqttClient.publish(MQTT_TOPIC_TELEMETRY, payload, false);
      const uint32_t graceStart = millis();
      while ((millis() - graceStart) < MQTT_PUBLISH_GRACE_MS) {
        mqttClient.loop();
        delay(10);
      }
    }
  }

  if (xSemaphoreTake(telemetryMutex, pdMS_TO_TICKS(1000)) == pdTRUE) {
    telemetry.mqttOk = published;
    xSemaphoreGive(telemetryMutex);
  }

  mqttClient.disconnect();
  WiFi.disconnect(true);
  WiFi.mode(WIFI_OFF);
  esp_wifi_stop();

  xEventGroupSetBits(cycleEvents, BIT_MQTT_DONE);
  vTaskDelete(nullptr);
}

static uint64_t calculateNextTimerWakeSeconds() {
  const uint64_t activeSeconds = (millis() + 999ULL) / 1000ULL;
  if (activeSeconds >= SCHEDULER_TICK_SECONDS) {
    return 60ULL;
  }
  return max<uint64_t>(60ULL, SCHEDULER_TICK_SECONDS - activeSeconds);
}

static void configureWakeupSources(uint64_t timerWakeSeconds) {
  esp_sleep_enable_timer_wakeup(timerWakeSeconds * 1000000ULL);

  esp_sleep_enable_ext1_wakeup(WAKEUP_PIN_MASK, ESP_EXT1_WAKEUP_ANY_HIGH);

  gpio_pullup_dis(PIN_TCRT_ENTRY);
  gpio_pullup_dis(PIN_TCRT_EXIT);
  gpio_pullup_dis(PIN_MPU_INT);
  gpio_pulldown_en(PIN_TCRT_ENTRY);
  gpio_pulldown_en(PIN_TCRT_EXIT);
  gpio_pulldown_en(PIN_MPU_INT);
}

static void enterDeepSleep() {
    digitalWrite(GPS_EN_PIN, LOW);  
    digitalWrite(PIN_STATUS_LED, LOW);
  configureWakeupSources(calculateNextTimerWakeSeconds());
  Serial.flush();
  esp_deep_sleep_start();
}

void setup() {
  Serial.begin(115200);
  delay(200);

  pinMode(PIN_STATUS_LED, OUTPUT);
  digitalWrite(PIN_STATUS_LED, HIGH);
  pinMode(GPS_EN_PIN, OUTPUT);
  digitalWrite(GPS_EN_PIN, LOW);

  rtcBootCount++;
  const esp_sleep_wakeup_cause_t wakeupCause = esp_sleep_get_wakeup_cause();
  const uint64_t ext1WakeMask = wakeupCause == ESP_SLEEP_WAKEUP_EXT1 ? esp_sleep_get_ext1_wakeup_status() : 0ULL;
  updateSchedulerTick(wakeupCause);
  acquisitionSchedule = determineAcquisitionSchedule(wakeupCause, ext1WakeMask);

  memset(&telemetry, 0, sizeof(telemetry));
  strlcpy(telemetry.deviceId, DEVICE_ID, sizeof(telemetry.deviceId));
  telemetry.bootCount = rtcBootCount;
  telemetry.scheduleTick = rtcScheduleTick;
  telemetry.wakeupCause = wakeupCause;
  telemetry.ext1WakeMask = ext1WakeMask;
  telemetry.beeEntriesTotal = rtcBeeEntriesTotal;
  telemetry.beeExitsTotal = rtcBeeExitsTotal;
  telemetry.theftEventsTotal = rtcTheftEventsTotal;

  telemetryMutex = xSemaphoreCreateMutex();
  i2cMutex = xSemaphoreCreateMutex();
  cycleEvents = xEventGroupCreate();

  pinMode(PIN_TCRT_ENTRY, INPUT_PULLDOWN);
  pinMode(PIN_TCRT_EXIT, INPUT_PULLDOWN);
  pinMode(PIN_MPU_INT, INPUT_PULLDOWN);
  attachInterrupt(digitalPinToInterrupt(PIN_TCRT_ENTRY), onEntryBeamBreak, RISING);
  attachInterrupt(digitalPinToInterrupt(PIN_TCRT_EXIT), onExitBeamBreak, RISING);
  attachInterrupt(digitalPinToInterrupt(PIN_MPU_INT), onMpuMotionAlert, RISING);
  seedWakeupEventsFromExt1(ext1WakeMask);

  analogReadResolution(12);
  analogSetPinAttenuation(PIN_BATTERY_ADC, ADC_11db);

  Wire.begin(static_cast<int>(PIN_I2C_SDA), static_cast<int>(PIN_I2C_SCL));
  Wire.setClock(400000);

  if (telemetry.wakeupCause == ESP_SLEEP_WAKEUP_EXT1) {
    const uint32_t windowStart = millis();
    while ((millis() - windowStart) < ACTIVE_COUNT_WINDOW_MS) {
      delay(10);
    }
  }

  xTaskCreatePinnedToCore(TaskAudio, "TaskAudio", 8192, nullptr, 2, nullptr, 0);
  xTaskCreatePinnedToCore(TaskI2C, "TaskI2C", 8192, nullptr, 2, nullptr, 1);
  xTaskCreatePinnedToCore(TaskGPS, "TaskGPS", 6144, nullptr, acquisitionSchedule.mpuWake ? 3 : 2, nullptr, 1);
  xTaskCreatePinnedToCore(TaskMQTT, "TaskMQTT", 8192, nullptr, 1, nullptr, 1);

  xEventGroupWaitBits(
      cycleEvents,
      BIT_MQTT_DONE,
      pdFALSE,
      pdTRUE,
      pdMS_TO_TICKS((acquisitionSchedule.audioDue ? AUDIO_CAPTURE_MS : 0) +
                    (acquisitionSchedule.gpsDue ? GPS_FIX_TIMEOUT_MS : 0) +
                    SENSOR_TASK_TIMEOUT_MS + WIFI_CONNECT_TIMEOUT_MS + MQTT_CONNECT_TIMEOUT_MS + 5000));

  detachInterrupt(digitalPinToInterrupt(PIN_TCRT_ENTRY));
  detachInterrupt(digitalPinToInterrupt(PIN_TCRT_EXIT));
  detachInterrupt(digitalPinToInterrupt(PIN_MPU_INT));

  enterDeepSleep();
}

void loop() {
// Ciclo task-driven: setup() cria as tasks, aguarda MQTT e retorna ao deep sleep.
}
