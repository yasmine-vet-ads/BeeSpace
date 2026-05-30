import { currentHive, environmentalAlerts, visionDetections } from '../data/mockHive';
import type { EnvironmentalAlert, HiveTelemetry, VisionDetection } from '../types/beespace';

export async function fetchHiveTelemetry(): Promise<HiveTelemetry> {
  return currentHive;
}

export async function fetchVisionDetections(): Promise<VisionDetection[]> {
  return visionDetections;
}

export async function fetchEnvironmentalAlerts(): Promise<EnvironmentalAlert[]> {
  return environmentalAlerts;
}
