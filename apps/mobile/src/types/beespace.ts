export type HiveStatus = 'normal' | 'attention' | 'critical';

export type HiveTelemetry = {
  deviceId: string;
  hiveName: string;
  locationLabel: string;
  lastSync: string;
  status: HiveStatus;
  temperatureC: number;
  humidityPercent: number;
  weightKg: number;
  batteryPercent: number;
  lightLux: number;
  beeInCount: number;
  beeOutCount: number;
  stressScore: number;
  motionAlert: boolean;
};

export type VisionClass = 'mel' | 'nectar' | 'polen' | 'ovos' | 'larvas' | 'crias';

export type VisionDetection = {
  label: VisionClass;
  percent: number;
};

export type CopernicusLayer = 'Sentinel-2 NDVI' | 'HR-VPP' | 'Sentinel-5P/CAMS' | 'C3S/ERA5';

export type EnvironmentalAlert = {
  id: string;
  title: string;
  description: string;
  layer: CopernicusLayer;
  severity: HiveStatus;
};
