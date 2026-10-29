export function StatTile({ label, value, loading, error }) {
  return (
    <div className="stat-tile">
      <span className="stat-tile__label">{label}</span>
      {loading ? (
        <span className="stat-tile__value stat-tile__value--muted">Cargando…</span>
      ) : error ? (
        <span className="stat-tile__value stat-tile__value--error">—</span>
      ) : (
        <span className="stat-tile__value">{value}</span>
      )}
    </div>
  );
}
