import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import { formatCurrency } from '../format';

const ACCENT = '#2a78d6';

function compactTick(value) {
  if (value >= 1000) {
    return `${Math.round(value / 1000)}K`;
  }
  return value;
}

export function SalesByCategoryChart({ data }) {
  const hasData = data && data.length > 0;

  return (
    <div className="card chart-card">
      <h3 className="card__title">Ventas por categoría</h3>
      {!hasData ? (
        <p className="card__empty">Sin ventas registradas todavía.</p>
      ) : (
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
            <CartesianGrid vertical={false} stroke="var(--gridline)" />
            <XAxis
              dataKey="categoria"
              tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
              axisLine={{ stroke: 'var(--baseline)' }}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
              axisLine={false}
              tickLine={false}
              tickFormatter={compactTick}
              width={48}
            />
            <Tooltip
              formatter={(value) => formatCurrency(value)}
              labelStyle={{ color: 'var(--text-primary)' }}
              contentStyle={{
                borderRadius: 8,
                border: '1px solid var(--gridline)',
                background: 'var(--surface-1)',
              }}
            />
            <Bar dataKey="ingresos" fill={ACCENT} radius={[4, 4, 0, 0]} maxBarSize={24} />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
