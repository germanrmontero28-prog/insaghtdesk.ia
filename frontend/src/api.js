const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function request(path, options) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const detail = body?.detail;
    const message = Array.isArray(detail)
      ? detail.map((item) => item.msg).join(', ')
      : detail ?? `Error ${response.status}`;
    throw new Error(message);
  }

  return response.json();
}

export const api = {
  getProductos: () => request('/api/productos'),
  crearProducto: (producto) =>
    request('/api/productos', { method: 'POST', body: JSON.stringify(producto) }),
  getVentas: () => request('/api/ventas'),
  crearVenta: (venta) =>
    request('/api/ventas', { method: 'POST', body: JSON.stringify(venta) }),
  getIndicadores: () => request('/api/indicadores'),
  chatAgente: (mensaje) =>
    request('/api/agente/chat', { method: 'POST', body: JSON.stringify({ mensaje }) }),
};
