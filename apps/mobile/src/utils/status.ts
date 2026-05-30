import type { HiveStatus } from '../types/beespace';

export const statusLabel: Record<HiveStatus, string> = {
  normal: 'Normal',
  attention: 'Atenção',
  critical: 'Crítico'
};

export const statusColor: Record<HiveStatus, string> = {
  normal: '#2E7D32',
  attention: '#D98E04',
  critical: '#B42318'
};

export function formatPercent(value: number): string {
  return `${Math.round(value)}%`;
}

export function formatSyncDate(isoDate: string): string {
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(isoDate));
}
