import type { EnvironmentalAlert, HiveTelemetry, VisionDetection } from '../types/beespace';

export const currentHive: HiveTelemetry = {
  deviceId: 'beespace-hive-0001',
  hiveName: 'Colmeia Matriz 01',
  locationLabel: 'Raio monitorado: 3 km • 28,27 km²',
  lastSync: '2026-05-30T00:00:00Z',
  status: 'attention',
  temperatureC: 34.8,
  humidityPercent: 61.2,
  weightKg: 42.5,
  batteryPercent: 86,
  lightLux: 1800,
  beeInCount: 128,
  beeOutCount: 119,
  stressScore: 0.12,
  motionAlert: false
};

export const visionDetections: VisionDetection[] = [
  { label: 'mel', percent: 28 },
  { label: 'nectar', percent: 18 },
  { label: 'polen', percent: 16 },
  { label: 'ovos', percent: 11 },
  { label: 'larvas', percent: 13 },
  { label: 'crias', percent: 14 }
];

export const environmentalAlerts: EnvironmentalAlert[] = [
  {
    id: 'ndvi-001',
    title: 'Vigor vegetal em observação',
    description: 'NDVI abaixo da média histórica no pasto apícola monitorado pela Sentinel-2.',
    layer: 'Sentinel-2 NDVI',
    severity: 'attention'
  },
  {
    id: 'air-001',
    title: 'Cruzamento ar + acústica normal',
    description: 'Sentinel-5P/CAMS indica qualidade do ar estável e a assinatura acústica segue normal.',
    layer: 'Sentinel-5P/CAMS',
    severity: 'normal'
  },
  {
    id: 'climate-001',
    title: 'Validação climática concluída',
    description: 'C3S/ERA5 está compatível com os sensores físicos BME280 da colmeia.',
    layer: 'C3S/ERA5',
    severity: 'normal'
  }
];
