export function toLocalISODate(d: Date | string): string {
  if (typeof d === 'string') return d.substring(0, 10);
  const pad = (n: number) => n.toString().padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
} 