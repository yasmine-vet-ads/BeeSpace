import { StyleSheet, Text, View } from 'react-native';

import { colors, spacing } from '../theme';

type MetricTileProps = {
  label: string;
  value: string;
  helper?: string;
};

export function MetricTile({ label, value, helper }: MetricTileProps) {
  return (
    <View style={styles.tile}>
      <Text style={styles.label}>{label}</Text>
      <Text style={styles.value}>{value}</Text>
      {helper ? <Text style={styles.helper}>{helper}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  helper: {
    color: colors.muted,
    fontSize: 12,
    marginTop: spacing.xs
  },
  label: {
    color: colors.muted,
    fontSize: 12,
    fontWeight: '700',
    textTransform: 'uppercase'
  },
  tile: {
    backgroundColor: colors.background,
    borderRadius: 18,
    flexBasis: '48%',
    flexGrow: 1,
    padding: spacing.md
  },
  value: {
    color: colors.ink,
    fontSize: 24,
    fontWeight: '900',
    marginTop: spacing.xs
  }
});
