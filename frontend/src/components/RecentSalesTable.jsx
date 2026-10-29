import { formatCurrency } from '../format';

export function RecentSalesTable({ ventas, productos }) {
  const productoPorId = new Map(productos.map((p) => [p.id, p]));
  const recientes = [...ventas]
    .sort((a, b) => {
      if (a.fecha !== b.fecha) return a.fecha < b.fecha ? 1 : -1;
      return b.id - a.id;
    })
    .slice(0, 10);

  return (
    <div className="card table-card">
      <h3 className="card__title">Ventas recientes</h3>
      {recientes.length === 0 ? (
        <p className="card__empty">No hay ventas registradas todavía.</p>
      ) : (
        <table className="sales-table">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Producto</th>
              <th>Categoría</th>
              <th className="num">Cantidad</th>
              <th className="num">Importe</th>
            </tr>
          </thead>
          <tbody>
            {recientes.map((venta) => {
              const producto = productoPorId.get(venta.producto_id);
              return (
                <tr key={venta.id}>
                  <td>{venta.fecha}</td>
                  <td>{producto?.nombre ?? `#${venta.producto_id}`}</td>
                  <td>{producto?.categoria ?? '—'}</td>
                  <td className="num">{venta.cantidad}</td>
                  <td className="num">{formatCurrency(venta.cantidad * venta.precio_unitario)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}
