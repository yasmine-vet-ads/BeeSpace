import { StyleSheet, Text, View } from 'react-native';

import { colors, spacing } from '../theme';
import { formatPercent } from '../utils/status';

type ProgressBarProps = {
  label: string;
  percent: number;
};

export function ProgressBar({ label, percent }: ProgressBarProps) {
  return (
    <View style={styles.container}>
      <View style={styles.row}>
        <Text style={styles.label}>{label}</Text>
        <Text style={styles.percent}>{formatPercent(percent)}</Text>
      </View>
      <View style={styles.track}>
        <View style={[styles.fill, { width: `${Math.min(percent, 100)}%` }]} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    gap: spacing.xs
  },
  fill: {
    backgroundColor: colors.honey,
    borderRadius: 999,
    height: '100%'
  },
  label: {
    color: colors.ink,
    fontSize: 14,
    fontWeight: '700',
    textTransform: 'capitalize'
  },
  percent: {
    color: colors.muted,
    fontSize: 14,
    fontWeight: '800'
  },
  row: {
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'space-between'
  },
  track: {
    backgroundColor: '#F0E2B8',
    borderRadius: 999,
    height: 10,
    overflow: 'hidden'
  }
});
