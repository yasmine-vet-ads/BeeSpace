# Firmware BeeSpace ESP32-S3

Firmware de produção para o biossensor inteligente de colmeias BeeSpace, estruturado para PlatformIO/Arduino com FreeRTOS, MQTT/JSON e deep sleep.

## 1. Pinout sugerido

| Periférico | Função | GPIO ESP32-S3 | Observações |
|---|---:|---:|---|
| I2C comum | SDA | GPIO 8 | Barramento para BME280, MPU6050 e BH1750. |
| I2C comum | SCL | GPIO 9 | Usar pull-ups de 4,7 kΩ para 3V3. |
| INMP441 | I2S SCK/BCLK | GPIO 12 | Evita GPIOs de strapping e USB nativo. |
| INMP441 | I2S WS/LRCLK | GPIO 13 | Configurado como RX mono 32 bits. |
| INMP441 | I2S SD/DOUT | GPIO 14 | Entrada I2S com DMA. |
| TCRT5000 entrada | Digital/RTC wake | GPIO 4 | Interrupção com debounce; pino RTC para EXT1 wake. |
| TCRT5000 saída | Digital/RTC wake | GPIO 5 | Interrupção com debounce; pino RTC para EXT1 wake. |
| HX711 | DOUT | GPIO 16 | Entrada digital da célula de carga. |
| HX711 | SCK | GPIO 17 | Clock do HX711. |
| MPU6050 | INT | GPIO 6 | Interrupção de movimento; acorda por EXT1. |
| BH1750 | ADDR | GND | Endereço padrão `0x23`. |
| Bateria | ADC | GPIO 1 | ADC1; divisor resistivo de alta impedância com capacitor de filtro. |
| Status opcional | LED | GPIO 21 | Pode ser removido em produção para menor consumo. |

> Evite usar GPIO 0, 3, 45 e 46 para periféricos críticos por serem pinos de strapping/boot ou entrada-only em placas ESP32-S3 comuns. Evite também GPIO 19/20 se a placa usa USB nativo.

## 2. Definição de bibliotecas

O firmware usa as seguintes bibliotecas e APIs:

- `Wire.h`
- `WiFi.h`
- `PubSubClient`
- `ArduinoJson`
- `Adafruit_BME280`
- `Adafruit_MPU6050`
- `BH1750`
- `HX711`
- `driver/i2s.h`
- APIs ESP-IDF/Arduino para FreeRTOS, GPIO, ADC e deep sleep (`esp_sleep.h`, `freertos/*`).

## 3. Compilação

```bash
cd firmware/esp32-s3
pio run
```

As credenciais de Wi-Fi/MQTT estão simuladas via `#define` em `src/main.cpp`; substitua por segredo de build ou provisioning antes de campo.

## 4. Agenda de aquisição

| Dado | Frequência configurada | Comportamento de energia/MQTT |
|---|---:|---|
| BME280 + BH1750 | A cada 120 minutos | Sensores ambientais só são energizados/lidos no tick agendado. |
| INMP441 | A cada 30 minutos | O microfone I2S captura por 5 minutos com DMA e publica métricas acústicas. |
| HX711 | A cada 7 dias | A balança é ligada, lida com fator/offset calibrados e colocada em `power_down()` após a leitura. |
| MQTT | Sob demanda | Wi-Fi/MQTT só conecta quando há dado novo, contagem de catraca ou alerta crítico. |

A agenda usa um tick RTC de 15 minutos preservado em `RTC_DATA_ATTR`; wakes por EXT1 não avançam o relógio periódico, então eventos de catraca/furto não antecipam leituras de BME280/BH1750, áudio ou HX711.

## 5. Memorial descritivo da arquitetura

O ESP32-S3 acorda por temporizador ou por EXT1, avalia a agenda de aquisição e executa apenas as tasks que realmente têm dados novos: ambiente/luz a cada 120 minutos, áudio INMP441 a cada 30 minutos por 5 minutos e balança HX711 a cada 7 dias. As tasks FreeRTOS de áudio, sensores e comunicação compartilham uma estrutura de telemetria protegida por mutex; event groups sinalizam conclusão de coleta, e a task MQTT só ativa Wi-Fi quando `hasNewDataToPublish()` detecta dados frescos, contadores de abelhas ou alerta de furto.

Durante o deep sleep, a melhor estratégia prática no Arduino é manter os sensores críticos em pinos RTC e usar `esp_sleep_enable_ext1_wakeup()` para acordar em eventos da catraca TCRT5000 ou do pino `INT` do MPU6050. Contadores ficam em `RTC_DATA_ATTR`, preservados entre sleeps; o firmware semeia o primeiro evento a partir da máscara EXT1 e permanece uma pequena janela ativa contando pulsos por ISR com debounce. Para contagem contínua em sono profundo total, a evolução recomendada é mover os TCRT5000 para o coprocessador ULP RISC-V do ESP32-S3 ou para um contador externo ultrabaixo consumo alimentado permanentemente.
