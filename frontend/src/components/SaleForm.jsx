import { useState } from 'react';

import { api } from '../api';

function today() {
  return new Date().toISOString().slice(0, 10);
}

export function SaleForm({ productos, onCreated }) {
  const [productoId, setProductoId] = useState('');
  const [cantidad, setCantidad] = useState('1');
  const [precioUnitario, setPrecioUnitario] = useState('');
  const [fecha, setFecha] = useState(today());
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  function handleProductoChange(event) {
    const id = event.target.value;
    setProductoId(id);
    const producto = productos.find((p) => String(p.id) === id);
    if (producto) setPrecioUnitario(String(producto.precio));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError(null);

    if (!productoId) {
      setError('Selecciona un producto.');
      return;
    }

    setSubmitting(true);
    try {
      await api.crearVenta({
        producto_id: Number(productoId),
        cantidad: Number(cantidad),
        precio_unitario: Number(precioUnitario),
        fecha,
      });
      setCantidad('1');
      setFecha(today());
      onCreated();
    } catch (err) {
      setError(err.message || 'No se pudo registrar la venta.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="card sale-form" onSubmit={handleSubmit}>
      <h3 className="card__title">Registrar venta</h3>

      <label className="sale-form__field">
        Producto
        <select value={productoId} onChange={handleProductoChange} required>
          <option value="" disabled>
            Selecciona un producto…
          </option>
          {productos.map((producto) => (
            <option key={producto.id} value={producto.id}>
              {producto.nombre} ({producto.categoria})
            </option>
          ))}
        </select>
      </label>

      <label className="sale-form__field">
        Cantidad
        <input
          type="number"
          min="1"
          step="1"
          value={cantidad}
          onChange={(event) => setCantidad(event.target.value)}
          required
        />
      </label>

      <label className="sale-form__field">
        Precio unitario
        <input
          type="number"
          min="0.01"
          step="0.01"
          value={precioUnitario}
          onChange={(event) => setPrecioUnitario(event.target.value)}
          required
        />
      </label>

      <label className="sale-form__field">
        Fecha
        <input
          type="date"
          value={fecha}
          onChange={(event) => setFecha(event.target.value)}
          required
        />
      </label>

      {error && <p className="form-error">{error}</p>}

      <button type="submit" className="button" disabled={submitting}>
        {submitting ? 'Guardando…' : 'Registrar venta'}
      </button>
    </form>
  );
}
