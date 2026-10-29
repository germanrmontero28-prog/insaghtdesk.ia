const currencyFormatter = new Intl.NumberFormat('es-CO', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 0,
});

const numberFormatter = new Intl.NumberFormat('es-CO');

export function formatCurrency(value) {
  return currencyFormatter.format(value ?? 0);
}

export function formatNumber(value) {
  return numberFormatter.format(value ?? 0);
}
