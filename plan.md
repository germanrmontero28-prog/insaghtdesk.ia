# plan.md — Plan de implementación

## Fase 1 — Inicialización
- [x] Crear frontend React + Vite.
- [x] Crear backend FastAPI.
- [x] Configurar Git y .gitignore.
- [x] Instalar dependencias autorizadas.

**Estado: completada (2026-10-28).** Verificaciones:
- `npm run build` en `frontend/` compila sin errores (dist generado).
- `pytest` en `backend/` pasa (1/1, test de `/api/health`).
- Repo git inicializado, `.gitignore` excluye `node_modules/`, `.venv/`, `dist/`, `*.db`, `.env`.
- Commit inicial `7b184e7`.

Dependencias instaladas:
- Frontend: react, react-dom, vite (scaffold) + recharts.
- Backend: fastapi, sqlalchemy, google-genai, pytest (de la especificación) + uvicorn, pydantic, python-dotenv, httpx (necesarias para ejecutar/probar el stack especificado, no son funcionalidades adicionales).

Riesgos detectados (no bloquean Fase 1):
- Falta definir `GEMINI_API_KEY` en `backend/.env` antes de la Fase 4 (se añadió `backend/.env.example` como plantilla).
- Node.js y Git no estaban instalados en el entorno; se instalaron vía winget (Node LTS 26.13.0, Git 2.56.0.3) con autorización del usuario.

No se avanza a la Fase 2 sin autorización.

## Fase 2 — Datos
- [x] Crear modelos Producto y Venta.
- [x] Configurar SQLite.
- [x] Generar datos de demostración.
- [x] Implementar endpoints REST.
- [x] Verificar indicadores con pruebas.

**Estado: completada (2026-10-28).** Implementación:
- `backend/app/database.py`: engine SQLite (`insightdesk.db`, archivo persistente) + `SessionLocal` + `get_db`.
- `backend/app/models.py`: `Producto` (id, nombre, categoria, precio) y `Venta` (id, producto_id FK, cantidad, precio_unitario, fecha).
- `backend/app/schemas.py`: validación Pydantic (precio/cantidad/precio_unitario > 0, nombre/categoria no vacíos, fecha tipada).
- `backend/app/crud.py`: queries SQLAlchemy para productos, ventas e indicadores (ingresos totales, cantidad vendida, ticket promedio, ventas por categoría vía `GROUP BY`).
- `backend/app/seed.py`: seed reproducible (`random.Random(42)`) — 8 productos demo fijos + 50 ventas generadas deterministamente; idempotente (no duplica si ya hay datos).
- `backend/app/main.py`: endpoints `GET/POST /api/productos`, `GET/POST /api/ventas`, `GET /api/indicadores`; 404 si `producto_id` no existe en una venta; CORS habilitado para el frontend.

Verificaciones ejecutadas:
- `pytest -q` → **17/17 passed** (incluye `test_productos.py`, `test_ventas.py`, `test_indicadores.py`, `test_seed.py`, `test_health.py`).
- Pruebas de indicadores recalculan ingresos/cantidad/ticket/categoría a partir de `/api/ventas` y los comparan contra `/api/indicadores` (sin cifras inventadas fuera del seed).
- Pruebas de reproducibilidad: dos bases sembradas por separado producen ventas idénticas; sembrar dos veces no duplica registros.
- Verificación manual de persistencia: se levantó la app, se confirmaron 8 productos / 50 ventas, se reinició el proceso contra el mismo `insightdesk.db` y los 50 registros persistieron sin duplicarse.
- Indicadores de ejemplo (datos reales del seed): `ingresos_totales=36915.0`, `cantidad_vendida=142`, `ticket_promedio≈259.96`, 4 categorías.
- Corregido antes de ejecutar pruebas: el `lifespan` de FastAPI tocaba el motor de producción incluso en tests vía `TestClient`; se aisló con `monkeypatch` en `conftest.py` para que las pruebas usen una base en memoria y nunca escriban en `insightdesk.db`.

No se avanza a la Fase 3 sin autorización.

## Fase 3 — Frontend
- [x] Construir dashboard.
- [x] Mostrar indicadores y gráficos.
- [x] Crear formulario de ventas.
- [x] Conectar frontend con backend.

**Estado: completada (2026-10-28).** Implementación:
- `frontend/src/api.js`: cliente fetch hacia el backend (`VITE_API_BASE_URL`, por defecto `http://localhost:8000`); único punto de acceso a la API. No hay datos simulados en el frontend.
- `frontend/src/hooks/useApiResource.js`: hook reutilizable con `data/loading/error/refetch`, usado por los tres recursos (productos, ventas, indicadores).
- Componentes reutilizables en `frontend/src/components/`: `StatTile` (KPI con estado de carga/error), `SalesByCategoryChart` (Recharts, un solo hue de acento, sin leyenda al ser una sola serie — paleta y specs de marca tomadas de la skill `dataviz`), `RecentSalesTable` (últimas 10 ventas, columnas numéricas con `tabular-nums`), `SaleForm` (valida en el backend; muestra 404/422 como error legible), `AgentPanel` (panel lateral placeholder, sin lógica — Fase 4 pendiente).
- `App.jsx` conecta los tres recursos, muestra un banner de error si falla la conexión con el backend, y refresca ventas + indicadores tras registrar una venta.
- Paleta y tokens de color en `index.css`/`App.css` siguiendo la paleta validada de la skill `dataviz` (`references/palette.md`), con modo oscuro vía `prefers-color-scheme`.

Verificaciones ejecutadas:
- `npm run build` → compila sin errores (`vite build`, 600 módulos). Aviso no bloqueante de Vite sobre el tamaño del bundle (Recharts); no requiere acción en esta fase.
- `npm run lint` (oxlint) → 1 warning no bloqueante (`react(set-state-in-effect)` en `useApiResource.js`, patrón estándar de fetch-on-mount); sin errores.
- Smoke test manual: se levantaron ambos servidores de desarrollo (`uvicorn` en :8000, `vite` en :5173) en segundo plano; se confirmó `GET /api/health`, `/api/productos` (8), `/api/indicadores` (cifras consistentes con el seed, UTF-8 correcto) y que Vite sirve el HTML del dashboard sin errores en consola del dev server. Ambos procesos se detuvieron al finalizar.
- **No se pudo verificar visualmente en un navegador real** (no hay herramienta de navegador disponible en este entorno): no se confirmó el renderizado final, la interacción del formulario ni el gráfico a simple vista. Recomendado: abrir `http://localhost:5173` manualmente con el backend corriendo en `:8000` antes de dar por buena la Fase 3 en términos visuales.

No se avanza a integrar Gemini (Fase 4) sin autorización.

## Fase 4 — Agente
- [ ] Configurar Gemini.
- [ ] Implementar herramientas de consulta.
- [ ] Integrar function calling.
- [ ] Crear endpoint de chat.
- [ ] Construir interfaz conversacional.

## Fase 5 — Calidad
- [ ] Ejecutar pytest.
- [ ] Compilar frontend.
- [ ] Validar manejo de errores.
- [ ] Revisar seguridad de secretos.
- [ ] Documentar ejecución en README.

## Regla de trabajo
Codex debe implementar una fase a la vez, ejecutar las verificaciones correspondientes y actualizar este plan. No avanzar automáticamente si existen errores sin resolver.
