# Folía — Product Backlog

App de cuidado de plantas con社区 integrada. Identificación por IA, cuidado diario, y descubrimiento de especies apoyado en datos reales de usuarios.

**Stack**: _Por definir_

---

## User Stories

### Auth

| ID | Feature | Descripción | Prioridad | Estado |
|:---|:--------|:------------|:----------|:-------|
| US-01 | Sign up y onboarding | Registro con email/password, Google o Apple + tour de 4 pantallas | Alta | ✅ Definida |
| US-02 | Sign in | Login con credenciales o OAuth | Alta | ✅ Definida |
| US-03 | Recuperar contraseña | Reset por email válido 30 min sin revelar si el email existe | Alta | ✅ Definida |

### Plantas

| ID | Feature | Descripción | Prioridad | Estado |
|:---|:--------|:------------|:----------|:-------|
| US-04 | Añadir planta con IA | Foto → PlantNet → 3-5 sugerencias → cuidados pre-rellenados + diagnóstico inicial | Alta | ✅ Definida |
| US-05 | Añadir planta manual | Búsqueda manual cuando la IA falla o sin conexión | Media | ✅ Definida |
| US-06 | Editar planta | Nombre, foto, especie, frecuencias de cuidado | Media | ✅ Definida |
| US-07 | Archivar planta | Ocultar del jardín activo manteniendo historial | Media | ✅ Definida |
| US-08 | Eliminar planta | Borrado permanente con confirmación | Media | ✅ Definida |
| US-09 | Ver historial de planta | Timeline cronológico inverso con filtros por tipo de evento | Media | ✅ Definida |
| US-10 | Diagnosticar enfermedad | Foto → IA → enfermedades con probabilidad → tratamiento → estado "En tratamiento" | Alta | ✅ Definida |
| US-11 | Diagnosticar planta no en jardín | Diagnóstico sin planta guardada + opción de añadirla después | Baja | ✅ Definida |
| US-30 | Comportamiento estacional | Ajuste automático de frecuencias de cuidado según estación del año | Media | ❓ Por definir |
| US-31 | Estrategia offline | Qué funciona sin conexión y qué no en toda la app | Media | ❓ Por definir |

**Notas**:
- US-04: Dependencia PlantNet a abstraer
- US-10: Añadir umbral mínimo de confianza (40 %)

### Cuidado Diario

| ID | Feature | Descripción | Prioridad | Estado |
|:---|:--------|:------------|:----------|:-------|
| US-12 | Ver tareas del día | Pantalla "Hoy" como landing tab con tareas agrupadas por tipo | Alta | ✅ Definida |
| US-13 | Completar tarea | Check → guarda fecha → programa siguiente ocurrencia | Alta | ✅ Definida |
| US-14 | Posponer tarea | Swipe → +1 día o +3 días sin alterar el ciclo base | Media | ✅ Definida |
| US-15 | Notificación push diaria | Resumen de qué plantas necesitan atención ese día | Alta | ✅ Definida |
| US-16 | Recordatorio de revisión de tratamiento | Notificación 7 días después del diagnóstico | Media | ✅ Definida |
| US-17 | Estadísticas del jardín | Total plantas, estados, racha, próxima tarea | Baja | ✅ Definida |
| US-22 | Cerrar tratamiento / recuperación | Foto nueva (re-diagnóstico) o marcar recuperada manualmente → estado "Sana" | Alta | ✅ Definida |

### Ajustes

| ID | Feature | Descripción | Prioridad | Estado |
|:---|:--------|:------------|:----------|:-------|
| US-18 | Preferencias de notificación | Activar/desactivar y configurar hora de notificación diaria | Media | ✅ Definida |
| US-19 | Timezone y apariencia | Zona horaria, idioma, tema | Baja | ✅ Definida |
| US-20 | Gestionar cuenta | Nombre, contraseña, cerrar sesión | Media | ✅ Definida |
| US-21 | Eliminar cuenta | Borrado completo con reautenticación | Media | ✅ Definida |
| US-23 | Relanzar guía contextual | Re-activar cualquier tutorial desde Ajustes > Ayuda | Baja | ✅ Definida |

### Social (pendiente de definir)

| ID | Feature | Descripción | Prioridad | Estado |
|:---|:--------|:------------|:----------|:-------|
| US-25 | Página de especie | Página viva por especie con fotos reales de usuarios + rareza + esquejes disponibles | Alta | ❓ Por definir |
| US-26 | Rareza de especie | Índice dinámico calculado por n.º de usuarios que tienen cada especie | Alta | ❓ Por definir |
| US-27 | Identificar planta y ver comunidad | Foto → identificación → página de especie con fotos reales de otros usuarios y esquejes cercanos | Alta | ❓ Por definir |
| US-28 | Intercambio de esquejes | Publicar esquejes disponibles y solicitar esquejes de otros usuarios por especie | Alta | ❓ Por definir |
| US-29 | Perfil público de planta | Historia pública y opcional de una planta con fotos a lo largo del tiempo | Media | ❓ Por definir |

---

## Sistema de Rareza

Las especies se clasifican dinámicamente según cuántos usuarios las tienen registradas en Folía.

| Nivel | Nombre | Color | Criterio | Ejemplo |
|:-----|:-------|:------|:---------|:--------|
| 1 | Common | Gris | +10 % de usuarios | Pothos, Aloe, Sansevieria |
| 2 | Uncommon | Verde | 1–10 % de usuarios | Monstera Deliciosa, Ficus |
| 3 | Rare | Azul | 0.1–1 % de usuarios | Calathea Orbifolia, Alocasia |
| 4 | Epic | Morado | 0.01–0.1 % de usuarios | Monstera Albo, Hoya Kerrii Var. |
| 5 | Legendary | Dorado | <0.01 % de usuarios | Variegadas únicas y especies muy difíciles |

**Nota**: Al inicio, sin usuarios suficientes, la rareza se calcula con datos reales de abundancia de cada especie en el mundo (fuentes botánicas). Se va refinando con datos reales de Folía.

---

## Ideas para la Comunidad

| Idea | Descripción | Por qué encaja | Prioridad sugerida |
|:----|:------------|:---------------|:-------------------|
| Biblioteca de especies viva | Cada especie tiene página propia con fotos reales de usuarios / rareza / esquejes disponibles | Es el eje que conecta cuidado + comunidad sin ser un feed genérico | Alta |
| Intercambio de esquejes | Publicar y buscar esquejes por especie con radio de distancia configurable | Resuelve un problema real que ahora pasa en grupos de FB y Wallapop | Alta |
| Identificar y descubrir comunidad | Foto → qué es → quién la tiene cerca → solicitar esqueje | Momento de descubrimiento mágico: como encontrar a alguien con tu mismo Pokémon | Alta |
| Evolución pública de planta | Timeline público opcional de una planta con fotos a lo largo del tiempo | Ver cómo le creció a otro la misma especie en condiciones similares | Media |
| Jardín de otro usuario | Ver el jardín público de otro usuario como inspiración | No es un feed cronológico — es un catálogo de colección | Media |
| Racha social | Las rachas individuales de cuidado son visibles en el perfil | Pequeño pero engancha sin ser Instagram | Baja |

---

## Ideas Descartadas o Aplazadas

| ID | Idea | Motivo |
|:---|:----|:-------|
| US-24 | Asistente de cuidados RAG | Chat en lenguaje natural sobre una planta. Innecesario: el core de Folía es cuidado + comunidad, no un chat genérico |
| — | Feed cronológico tipo Instagram | Genera ruido y necesita masa crítica. El contenido en Folía debe estar ligado a una especie o planta concreta |
| — | Sistema de likes y seguidores | Convierte la app en una red social genérica. No es el objetivo |
| — | Comunidad de diagnóstico colaborativo | Buena idea pero el cuidado lo gestiona la IA — la comunidad es para compartir, no para resolver dudas técnicas |

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
