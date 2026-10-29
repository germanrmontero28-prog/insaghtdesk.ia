import { useState } from 'react';

import { api } from '../api';

export function AgentPanel() {
  const [mensaje, setMensaje] = useState('');
  const [historial, setHistorial] = useState([]);
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(event) {
    event.preventDefault();
    const texto = mensaje.trim();
    if (!texto || enviando) return;

    setError(null);
    setHistorial((prev) => [...prev, { rol: 'usuario', texto }]);
    setMensaje('');
    setEnviando(true);

    try {
      const respuesta = await api.chatAgente(texto);
      setHistorial((prev) => [
        ...prev,
        {
          rol: 'agente',
          texto: respuesta.respuesta,
          herramientas: respuesta.herramientas,
        },
      ]);
    } catch (err) {
      setError(err.message || 'No se pudo consultar al agente.');
    } finally {
      setEnviando(false);
    }
  }

  return (
    <aside className="card agent-panel">
      <h3 className="card__title">Asistente IA</h3>

      <div className="agent-panel__historial">
        {historial.length === 0 ? (
          <p className="agent-panel__placeholder">
            Pregúntame por el resumen de ventas, un producto o una categoría.
          </p>
        ) : (
          historial.map((entrada, index) => (
            <div key={index} className={`agent-message agent-message--${entrada.rol}`}>
              <p>{entrada.texto}</p>
              {entrada.herramientas?.length > 0 && (
                <span className="agent-message__tools">
                  Consultó: {entrada.herramientas.join(', ')}
                </span>
              )}
            </div>
          ))
        )}
        {enviando && <p className="agent-panel__placeholder">Pensando…</p>}
      </div>

      {error && <p className="form-error">{error}</p>}

      <form className="agent-panel__form" onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Escribe tu pregunta…"
          value={mensaje}
          onChange={(event) => setMensaje(event.target.value)}
          disabled={enviando}
        />
        <button type="submit" className="button" disabled={enviando || !mensaje.trim()}>
          Enviar
        </button>
      </form>
    </aside>
  );
}
