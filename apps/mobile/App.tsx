import { StatusBar } from 'expo-status-bar';
import { useEffect, useState } from 'react';
import { SafeAreaView, ScrollView, StyleSheet, Text, View } from 'react-native';

import { MetricTile } from './src/components/MetricTile';
import { ProgressBar } from './src/components/ProgressBar';
import { SectionCard } from './src/components/SectionCard';
import { fetchEnvironmentalAlerts, fetchHiveTelemetry, fetchVisionDetections } from './src/services/api';
import { colors, spacing } from './src/theme';
import type { EnvironmentalAlert, HiveTelemetry, VisionDetection } from './src/types/beespace';
import { formatPercent, formatSyncDate, statusColor, statusLabel } from './src/utils/status';

export default function App() {
  const [telemetry, setTelemetry] = useState<HiveTelemetry | null>(null);
  const [detections, setDetections] = useState<VisionDetection[]>([]);
  const [alerts, setAlerts] = useState<EnvironmentalAlert[]>([]);

  useEffect(() => {
    void Promise.all([fetchHiveTelemetry(), fetchVisionDetections(), fetchEnvironmentalAlerts()]).then(
      ([hiveTelemetry, visionDetections, environmentalAlerts]) => {
        setTelemetry(hiveTelemetry);
        setDetections(visionDetections);
        setAlerts(environmentalAlerts);
      }
    );
  }, []);

  if (!telemetry) {
    return (
      <SafeAreaView style={styles.safeArea}>
        <Text style={styles.loading}>Carregando colmeia inteligente...</Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar style="dark" />
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.hero}>
          <Text style={styles.logo}>🐝 BeeSpace</Text>
          <Text style={styles.tagline}>Biodiversidade em Órbita 🛰️</Text>
          <Text style={styles.heroCopy}>
            Manejo presencial, telemetria IoT, visão computacional e Copernicus em uma experiência mobile.
          </Text>
        </View>

        <SectionCard eyebrow="Colmeia ativa" title={telemetry.hiveName}>
          <View style={styles.statusRow}>
            <View style={[styles.statusPill, { backgroundColor: statusColor[telemetry.status] }]}>
              <Text style={styles.statusText}>{statusLabel[telemetry.status]}</Text>
            </View>
            <Text style={styles.syncText}>Sync: {formatSyncDate(telemetry.lastSync)}</Text>
          </View>
          <Text style={styles.location}>{telemetry.locationLabel}</Text>
          <View style={styles.metricsGrid}>
            <MetricTile label="Temperatura" value={`${telemetry.temperatureC.toFixed(1)} °C`} helper="BME280" />
            <MetricTile label="Umidade" value={formatPercent(telemetry.humidityPercent)} helper="BME280" />
            <MetricTile label="Peso" value={`${telemetry.weightKg.toFixed(1)} kg`} helper="HX711" />
            <MetricTile label="Bateria" value={formatPercent(telemetry.batteryPercent)} helper="18650 + solar" />
            <MetricTile label="Entrada" value={`${telemetry.beeInCount}`} helper="TCRT5000" />
            <MetricTile label="Saída" value={`${telemetry.beeOutCount}`} helper="TCRT5000" />
          </View>
        </SectionCard>

        <SectionCard eyebrow="Visão computacional" title="Classificação dos alvéolos">
          <Text style={styles.bodyText}>
            Pipeline preparado para receber fotos do manejo, enviar para inferência YOLO e retornar percentuais de mel,
            néctar, pólen, ovos, larvas e crias.
          </Text>
          {detections.map((detection) => (
            <ProgressBar key={detection.label} label={detection.label} percent={detection.percent} />
          ))}
        </SectionCard>

        <SectionCard eyebrow="Copernicus" title="Do micro ao macro">
          <Text style={styles.bodyText}>
            Alertas cruzam sensores da colmeia com Sentinel-2, HR-VPP, Sentinel-5P/CAMS e C3S/ERA5 para reduzir
            greenwashing com dados verificáveis.
          </Text>
          {alerts.map((alert) => (
            <View key={alert.id} style={styles.alertBox}>
              <View style={styles.alertHeader}>
                <Text style={styles.alertTitle}>{alert.title}</Text>
                <View style={[styles.alertDot, { backgroundColor: statusColor[alert.severity] }]} />
              </View>
              <Text style={styles.alertLayer}>{alert.layer}</Text>
              <Text style={styles.alertDescription}>{alert.description}</Text>
            </View>
          ))}
        </SectionCard>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  alertBox: {
    backgroundColor: colors.background,
    borderRadius: 18,
    padding: spacing.md
  },
  alertDescription: {
    color: colors.muted,
    fontSize: 14,
    lineHeight: 20,
    marginTop: spacing.xs
  },
  alertDot: {
    borderRadius: 999,
    height: 12,
    width: 12
  },
  alertHeader: {
    alignItems: 'center',
    flexDirection: 'row',
    gap: spacing.sm,
    justifyContent: 'space-between'
  },
  alertLayer: {
    color: colors.honeyDark,
    fontSize: 12,
    fontWeight: '800',
    marginTop: spacing.xs
  },
  alertTitle: {
    color: colors.ink,
    flex: 1,
    fontSize: 15,
    fontWeight: '800'
  },
  bodyText: {
    color: colors.muted,
    fontSize: 15,
    lineHeight: 22
  },
  hero: {
    backgroundColor: colors.forest,
    borderRadius: 30,
    marginBottom: spacing.lg,
    padding: spacing.xl
  },
  heroCopy: {
    color: '#E8F3E8',
    fontSize: 15,
    lineHeight: 22,
    marginTop: spacing.md
  },
  loading: {
    color: colors.ink,
    fontSize: 18,
    fontWeight: '700',
    padding: spacing.xl
  },
  location: {
    color: colors.muted,
    fontSize: 14,
    lineHeight: 20
  },
  logo: {
    color: colors.surface,
    fontSize: 34,
    fontWeight: '900'
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.md
  },
  safeArea: {
    backgroundColor: colors.background,
    flex: 1
  },
  scrollContent: {
    padding: spacing.lg,
    paddingBottom: spacing.xxl
  },
  statusPill: {
    borderRadius: 999,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm
  },
  statusRow: {
    alignItems: 'center',
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
    justifyContent: 'space-between'
  },
  statusText: {
    color: colors.surface,
    fontSize: 12,
    fontWeight: '900',
    letterSpacing: 0.8,
    textTransform: 'uppercase'
  },
  syncText: {
    color: colors.muted,
    fontSize: 12,
    fontWeight: '700'
  },
  tagline: {
    color: colors.honey,
    fontSize: 18,
    fontWeight: '800',
    marginTop: spacing.xs
  }
});
