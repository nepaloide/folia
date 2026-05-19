# Folía — Product Backlog (MVP)

App de cuidado de plantas con identificación por IA, gestión de jardín personal, y notificaciones de cuidado.

**Stack**:
- **Frontend**: Expo (React Native) + TypeScript — mobile-only
- **Backend**: Python + FastAPI

---

## MVP — User Stories

### Auth

| ID | Feature | Descripción | Prioridad | Estado |
|:---|:--------|:------------|:----------|:-------|
| US-01 | Sign up con Google/Apple | Registro y login con Google o Apple + tour de onboarding | Alta | ✅ Definida |

### Plantas

| ID | Feature | Descripción | Prioridad | Estado |
|:---|:--------|:------------|:----------|:-------|
| US-04 | Añadir planta con IA | Foto → PlantNet → 3-5 sugerencias → cuidados pre-rellenados + diagnóstico inicial | Alta | ✅ Definida |
| US-05 | Añadir planta manual | Búsqueda manual cuando la IA falla o sin conexión | Media | ✅ Definida |
| US-06 | Editar planta | Nombre, fotos, especie, frecuencias de cuidado (riego, abono, transplante, etc.) | Media | ✅ Definida |

| US-08 | Eliminar planta | Borrado permanente con confirmación | Media | ✅ Definida |
| US-09 | Ver historial de planta | Timeline cronológico inverso con eventos de cuidado (riego, abono, transplante, diagnósticos) | Media | ✅ Definida |
| US-10 | Diagnosticar enfermedad | Foto → IA → enfermedades con probabilidad → tratamiento → estado "En tratamiento" | Alta | ✅ Definida |
| US-11 | Diagnosticar planta no en jardín | Diagnóstico sin planta guardada + opción de añadirla después | Baja | ✅ Definida |
| US-22 | Cerrar tratamiento / recuperación | Foto nueva (re-diagnóstico) o marcar recuperada manualmente → estado "Sana" | Alta | ✅ Definida |
| US-32 | Galería de fotos por planta | Múltiples fotos a lo largo del tiempo para ver la evolución de cada planta | Media | ✅ Definida |
| US-33 | Buscar y filtrar plantas | Buscar por nombre, filtrar por estado (sana, en tratamiento, archivada) | Media | ✅ Definida |

**Notas**:
- US-04: Dependencia PlantNet a abstraer
- US-10: Añadir umbral mínimo de confianza (40 %)
- US-32: Las fotos se muestran como galería en la pantalla de detalle de la planta, ordenadas por fecha

### Cuidado Diario

| ID | Feature | Descripción | Prioridad | Estado |
|:---|:--------|:------------|:----------|:-------|
| US-12 | Ver tareas del día | Pantalla "Hoy" como landing tab con tareas agrupadas por tipo (riego, abono, transplante, revisión) | Alta | ✅ Definida |
| US-13 | Completar tarea | Check → guarda fecha → programa siguiente ocurrencia según frecuencia | Alta | ✅ Definida |
| US-14 | Posponer tarea | Swipe → +1 día o +3 días sin alterar el ciclo base | Media | ✅ Definida |
| US-15 | Notificación push diaria | Resumen de qué plantas necesitan atención ese día | Alta | ✅ Definida |
| US-16 | Recordatorio de revisión de tratamiento | Notificación 7 días después del diagnóstico | Media | ✅ Definida |
| US-17 | Estadísticas del jardín | Total plantas, sanas/en tratamiento, racha de cuidado, próxima tarea | Baja | ✅ Definida |

### Ajustes

| ID | Feature | Descripción | Prioridad | Estado |
|:---|:--------|:------------|:----------|:-------|
| US-18 | Preferencias de notificación | Activar/desactivar y configurar hora de notificación diaria | Media | ✅ Definida |
| US-19 | Timezone y apariencia | Zona horaria, idioma, tema (claro/oscuro) | Baja | ✅ Definida |

---

## Ideas Descartadas o Aplazadas

| ID | Idea | Motivo |
|:---|:-----|:-------|
| US-02 | Sign in con credenciales | No hace falta: solo Google/Apple OAuth |
| US-03 | Recuperar contraseña | No hace falta: OAuth maneja la identidad |
| US-07 | Archivar planta | No aporta al MVP: eliminar cubre el caso de limpieza |
| US-20 | Gestionar cuenta (nombre, contraseña, cerrar sesión) | No hace falta: Google maneja la cuenta |
| US-21 | Eliminar cuenta | No hace falta: Google maneja la identidad |
| US-23 | Relanzar guía contextual | Baja prioridad, no esencial para MVP |
| US-24 | Asistente de cuidados RAG | Chat innecesario: el core es cuidado + comunidad |
| US-25 | Página de especie | Fase futura (Social) |
| US-26 | Rareza de especie | Fase futura (Social) |
| US-27 | Identificar y ver comunidad | Fase futura (Social) |
| US-28 | Intercambio de esquejes | Fase futura (Social) |
| US-29 | Perfil público de planta | Fase futura (Social) |
| US-30 | Comportamiento estacional | Fase futura |
| US-31 | Estrategia offline | Fase futura |
| — | Feed cronológico tipo Instagram | Genera ruido. El contenido debe estar ligado a una especie o planta concreta |
| — | Sistema de likes y seguidores | Convierte la app en una red social genérica. No es el objetivo |
| — | Comunidad de diagnóstico colaborativo | El cuidado lo gestiona la IA, no la comunidad |

---

## Análisis de Competencia

| App | Fortaleza | Debilidad | Hueco que Folía cubre |
|:---|:----------|:----------|:----------------------|
| **Greg** | Comunidad activa + recordatorios personalizados por clima | Comunidad genérica desconectada de los datos de tus plantas | Comunidad centrada en especies, no en personas |
| **PictureThis** | Identificación muy precisa (400k+ especies) | Paywall agresivo + cuidados básicos + comunidad solo Q&A | Identificación → página de especie viva con comunidad |
| **Planta / Blossom** | Mejor UX de cuidado del mercado | Sin comunidad real | IA de cuidado + comunidad integrada |
| **PlantLife** | Red social pura de plantas estilo TikTok | No tiene cuidado ni datos reales de plantas | Parte social apoyada en datos reales de cada planta |
| **Propa** | Intercambio de esquejes con comunidad | Nicho muy específico sin cuidado | Esquejes integrados con el jardín que ya tienes |
| **PlantNet** | Identificación colaborativa validada por botánicos | Sin cuidado ni gestión de jardín personal | Usar su API + añadir la capa social y de cuidado encima |
