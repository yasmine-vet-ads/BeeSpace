import type { ReactNode } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { colors, spacing } from '../theme';

type SectionCardProps = {
  title: string;
  eyebrow?: string;
  children: ReactNode;
};

export function SectionCard({ title, eyebrow, children }: SectionCardProps) {
  return (
    <View style={styles.card}>
      {eyebrow ? <Text style={styles.eyebrow}>{eyebrow}</Text> : null}
      <Text style={styles.title}>{title}</Text>
      <View style={styles.content}>{children}</View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderRadius: 24,
    borderWidth: 1,
    elevation: 2,
    marginBottom: spacing.lg,
    padding: spacing.lg,
    shadowColor: colors.shadow,
    shadowOffset: { height: 6, width: 0 },
    shadowOpacity: 0.08,
    shadowRadius: 18
  },
  content: {
    gap: spacing.md,
    marginTop: spacing.md
  },
  eyebrow: {
    color: colors.honeyDark,
    fontSize: 12,
    fontWeight: '800',
    letterSpacing: 1.2,
    marginBottom: spacing.xs,
    textTransform: 'uppercase'
  },
  title: {
    color: colors.ink,
    fontSize: 20,
    fontWeight: '800'
  }
});
