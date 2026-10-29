import './App.css';
import { api } from './api';
import { AgentPanel } from './components/AgentPanel';
import { RecentSalesTable } from './components/RecentSalesTable';
import { SaleForm } from './components/SaleForm';
import { SalesByCategoryChart } from './components/SalesByCategoryChart';
import { StatTile } from './components/StatTile';
import { formatCurrency, formatNumber } from './format';
import { useApiResource } from './hooks/useApiResource';

function App() {
  const productosResource = useApiResource(api.getProductos);
  const ventasResource = useApiResource(api.getVentas);
  const indicadoresResource = useApiResource(api.getIndicadores);

  const productos = productosResource.data ?? [];
  const ventas = ventasResource.data ?? [];
  const indicadores = indicadoresResource.data;

  function handleVentaCreada() {
    ventasResource.refetch();
    indicadoresResource.refetch();
  }

  const connectionError =
    productosResource.error || ventasResource.error || indicadoresResource.error;

  return (
    <div className="dashboard">
      <header className="dashboard__header">
        <h1>InsightDesk AI</h1>
        <p>Panel comercial</p>
      </header>

      {connectionError && (
        <div className="banner banner--error">
          No se pudo conectar con el backend ({connectionError}). Verifica que
          la API esté corriendo en {import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}.
        </div>
      )}

      <div className="dashboard__layout">
        <main className="dashboard__main">
          <section className="kpi-row">
            <StatTile
              label="Ingresos totales"
              value={indicadores ? formatCurrency(indicadores.ingresos_totales) : '—'}
              loading={indicadoresResource.loading}
              error={indicadoresResource.error}
            />
            <StatTile
              label="Unidades vendidas"
              value={indicadores ? formatNumber(indicadores.cantidad_vendida) : '—'}
              loading={indicadoresResource.loading}
              error={indicadoresResource.error}
            />
            <StatTile
              label="Ticket promedio"
              value={indicadores ? formatCurrency(indicadores.ticket_promedio) : '—'}
              loading={indicadoresResource.loading}
              error={indicadoresResource.error}
            />
          </section>

          <section className="dashboard__row">
            {indicadoresResource.loading ? (
              <div className="card chart-card">
                <h3 className="card__title">Ventas por categoría</h3>
                <p className="card__empty">Cargando gráfico…</p>
              </div>
            ) : (
              <SalesByCategoryChart data={indicadores?.ventas_por_categoria ?? []} />
            )}

            <SaleForm productos={productos} onCreated={handleVentaCreada} />
          </section>

          <section>
            {ventasResource.loading ? (
              <div className="card table-card">
                <h3 className="card__title">Ventas recientes</h3>
                <p className="card__empty">Cargando ventas…</p>
              </div>
            ) : (
              <RecentSalesTable ventas={ventas} productos={productos} />
            )}
          </section>
        </main>

        <AgentPanel />
      </div>
    </div>
  );
}

export default App;
