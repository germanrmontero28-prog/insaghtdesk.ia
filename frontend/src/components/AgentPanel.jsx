export function AgentPanel() {
  return (
    <aside className="card agent-panel">
      <h3 className="card__title">Asistente IA</h3>
      <p className="agent-panel__placeholder">
        El agente conversacional con Gemini se integrará en la Fase 4. Desde
        aquí podrás preguntar por indicadores y recibir recomendaciones
        basadas en los datos de ventas.
      </p>
      <div className="agent-panel__input-mock" aria-hidden="true">
        <span>Disponible próximamente…</span>
      </div>
    </aside>
  );
}
