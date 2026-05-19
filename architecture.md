# Folía — Architecture Overview

> **Última actualización**: 2026-05-19
> **Stack**: FastAPI (Python) + Expo (React Native) + PostgreSQL

---

## 1. Backend Architecture

### 1.1 Layered Modular Structure

Cada feature es un módulo independiente dentro de `app/modules/`. Un módulo contiene TODO lo que necesita: rutas, esquemas, lógica, y acceso a datos.

```
backend/app/
├── main.py                     # FastAPI app entry point
├── core/                       # Shared infrastructure
│   ├── config.py               # Settings + env vars (pydantic-settings)
│   ├── database.py             # Async engine + session (SQLAlchemy 2.0)
│   └── security.py             # Google OAuth verification
│
├── modules/                    # ─────── Cada feature es su mundo ───────
│   ├── auth/
│   │   ├── router.py           #   POST /auth/google
│   │   ├── schemas.py          #   Pydantic request/response
│   │   ├── models.py           #   User model (SQLAlchemy)
│   │   ├── service.py          #   Lógica de autenticación
│   │   └── repository.py       #   Consultas a DB
│   │
│   ├── plants/
│   │   ├── router.py           #   CRUD /plants
│   │   ├── schemas.py          #   PlantDTO, CareConfigDTO
│   │   ├── models.py           #   Plant + CareConfig + PlantPhoto
│   │   ├── service.py          #   Lógica de gestión de plantas
│   │   └── repository.py       #   Consultas a DB
│   │
│   ├── care/
│   │   ├── router.py           #   GET /tasks, POST /tasks/{id}/complete
│   │   ├── schemas.py          #   TaskDTO, CareLogDTO
│   │   ├── models.py           #   CareTask + CareLog
│   │   ├── service.py          #   Generación de tareas, notificaciones
│   │   └── repository.py       #   Consultas a DB
│   │
│   └── diagnosis/
│       ├── router.py           #   POST /diagnose, GET /diagnoses
│       ├── schemas.py          #   DiagnosisDTO
│       ├── models.py           #   Diagnosis model
│       ├── service.py          #   Llamada a PlantNet + IA
│       └── repository.py       #   Consultas a DB
│
└── common/                     # Utilities compartidas
    ├── exceptions.py           #   HTTPException personalizadas
    └── pagination.py           #   Paginación cursor-based
```

### 1.2 Responsabilidades por capa

| Capa | Responsabilidad | No hace |
|:-----|:----------------|:--------|
| **router.py** | Define endpoints, valida input, devuelve response | No tiene lógica de negocio |
| **schemas.py** | Schemas Pydantic de entrada/salida | No tiene lógica |
| **models.py** | Modelos SQLAlchemy (tablas) | Solo define estructura de DB |
| **service.py** | Reglas de negocio, orquestación | No habla directo a DB |
| **repository.py** | Consultas SQL, filtros, joins | Solo acceso a datos |

### 1.3 Flujo de una request

```
Request → router.py → service.py → repository.py → DB
              │            │
              │       (reglas de     (SQL queries)
              │        negocio)
              │
         schemas.py (validación)
```

---

## 2. Data Model

### 2.1 Entidades

```
User ───────┬── Plant ──────┬── CareConfig     ← acciones configuradas
            │               ├── PlantPhoto      ← galería
            │               ├── CareTask        ← tareas programadas
            │               ├── CareLog         ← historial
            │               └── Diagnosis       ← diagnósticos
            │
            └── Diagnosis   (US-11: sin planta)
```

### 2.2 Campos por entidad

**User**
| Campo | Tipo | Notas |
|:------|:-----|:------|
| id | UUID | PK |
| google_id | TEXT | Unique, de Google OAuth |
| email | TEXT | |
| name | TEXT | |
| timezone | TEXT | Ej: "America/Argentina/Buenos_Aires" |
| notification_hour | INT | Hora para push diario (0-23) |
| created_at | TIMESTAMPTZ | |

**Plant**
| Campo | Tipo | Notas |
|:------|:-----|:------|
| id | UUID | PK |
| user_id | UUID | FK → User |
| name | TEXT | Ej: "Pothos de la cocina" |
| species | TEXT | Nombre científico |
| species_common | TEXT | Nombre común (opcional) |
| status | ENUM | `healthy`, `treatment` |
| avatar_url | TEXT | Foto principal |
| created_at | TIMESTAMPTZ | |

**CareConfig** — flexible, cada planta tiene las que necesita
| Campo | Tipo | Notas |
|:------|:-----|:------|
| id | UUID | PK |
| plant_id | UUID | FK → Plant |
| action | ENUM | `water`, `fertilize`, `transplant`, `prune`, `clean`, `fumigate` |
| interval_value | INT | Cada cuánto (ej: 7) |
| interval_unit | ENUM | `days`, `months` |
| json_metadata | JSONB | Datos extra: `{amount_ml: 200, method: "immersion"}` |
| season_start | INT | Mes de inicio (1-12, nullable) |
| season_end | INT | Mes de fin (1-12, nullable) |
| created_at | TIMESTAMPTZ | |

*Ejemplo: Una Calathea tiene 3 CareConfig: riego c/7 días, abono c/30 días en primavera/verano, limpieza c/15 días.*

**PlantPhoto**
| Campo | Tipo | Notas |
|:------|:-----|:------|
| id | UUID | PK |
| plant_id | UUID | FK → Plant |
| url | TEXT | Storage URL |
| taken_at | TIMESTAMPTZ | Cuándo se sacó la foto |

**CareTask** — tarea concreta generada a partir de CareConfig
| Campo | Tipo | Notas |
|:------|:-----|:------|
| id | UUID | PK |
| plant_id | UUID | FK → Plant |
| action | ENUM | `water`, `fertilize`, `transplant`, `prune`, `clean`, `fumigate`, `review` |
| due_date | DATE | Fecha esperada |
| completed | BOOL | |
| completed_at | TIMESTAMPTZ | Nullable |
| postponed_count | INT | Veces que se pospuso |

**CareLog** — registro inmutable de acciones hechas
| Campo | Tipo | Notas |
|:------|:-----|:------|
| id | UUID | PK |
| plant_id | UUID | FK → Plant |
| action | ENUM | Mismo que CareTask |
| completed_at | TIMESTAMPTZ | |
| notes | TEXT | Opcional |

**Diagnosis**
| Campo | Tipo | Notas |
|:------|:-----|:------|
| id | UUID | PK |
| user_id | UUID | FK → User |
| plant_id | UUID | FK → Plant (nullable, US-11) |
| photo_url | TEXT | Foto del diagnóstico |
| diseases | JSONB | `[{name, probability, treatment}]` |
| status | ENUM | `active`, `resolved` |
| created_at | TIMESTAMPTZ | |
| review_at | TIMESTAMPTZ | Fecha de revisión (+7 días, US-16) |

### 2.3 Reglas de negocio clave

- **Completar tarea** → marcar completed + crear CareLog + programar próxima tarea según CareConfig
- **Posponer tarea** → +1 o +3 días a due_date, no altera el ciclo base
- **Diagnóstico** → umbral mínimo de confianza 40 % (US-10)
- **Revisión de tratamiento** → notificación 7 días después del diagnóstico (US-16)

---

## 3. Mobile Architecture

### 3.1 Navegación

```
Tab Navigator (inferior)
│
├── ? Jardín         → Stack: Lista → Detalle Planta → Historial
├── ? Diagnóstico    → Cámara → Resultados → (opcional) Añadir Planta
├── ? HOY            → Tareas del día (tab por defecto al abrir la app)
└── ? Ajustes        → Notificaciones, Tema, Idioma
```

4 tabs en la barra inferior. "HOY" es el tab central destacado (más grande o con distinto color) porque es lo que se usa a diario.

### 3.2 Estructura de carpetas

```
mobile/src/
├── app/
│   ├── navigation.tsx   # Tab + Stack navigators
│   └── App.tsx          # Entry point
│
├── modules/                  # Misma separación que backend
│   ├── auth/
│   ├── plants/
│   ├── care/
│   └── diagnosis/
│
├── screens/                  # Screens atómicos (llaman a modules)
│   ├── hoy/
│   ├── garden/
│   ├── diagnosis/
│   └── settings/
│
├── components/               # UI reutilizable
│   ├── ui/                   # Botones, inputs, cards
│   └── plant/               # PlantCard, TaskItem, etc.
│
├── services/
│   └── api.ts                # Cliente HTTP (fetch a FastAPI)
│
├── types/
│   └── index.ts              # Interfaces globales
│
└── utils/
    ├── date.ts               # Fechas, timezone
    └── notifications.ts      # Push notifications
```

### 3.3 Estado

- **Local state** dentro de cada screen → por ahora, sin estado global
- Si surge la necesidad → **Zustand** (liviano, simple, buena integración con IA)

---

## 4. API Design

### 4.1 Endpoints principales

```
Base: /api/v1

Auth
  POST /auth/google     → login con Google token

Plants
  GET    /plants            → listar plantas del usuario
  POST   /plants            → crear planta (con foto opcional)
  GET    /plants/{id}       → detalle de planta
  PATCH  /plants/{id}       → editar planta
  DELETE /plants/{id}       → eliminar planta
  GET    /plants/{id}/photos → galería de fotos
  POST   /plants/{id}/photos → añadir foto
  POST   /plants/{id}/identify  → identificar especie (PlantNet)

Care Config
  GET    /plants/{id}/config    → acciones configuradas
  POST   /plants/{id}/config    → crear CareConfig
  PATCH  /plants/{id}/config/{cfg_id} → editar configuración
  DELETE /plants/{id}/config/{cfg_id} → eliminar acción

Care Tasks
  GET    /tasks                     → tareas del día (filtro opcional por fecha)
  PATCH  /tasks/{id}/complete       → marcar completada
  PATCH  /tasks/{id}/postpone       → posponer (+1d o +3d)

Care Log
  GET    /plants/{id}/log           → historial de eventos

Diagnosis
  POST   /diagnose                  → diagnosticar foto
  GET    /diagnoses                 → historial de diagnósticos
  PATCH  /diagnoses/{id}/resolve    → marcar como resuelta
```

---

## 5. External Dependencies

| Servicio | Propósito | Abstraction |
|:---------|:----------|:------------|
| **PlantNet API** | Identificación de especies | Servicio intercambiable |
| **Google OAuth** | Autenticación | Core security.py |
| **AI (a definir)** | Diagnóstico de enfermedades | Servicio intercambiable |
| **Push notifications** | Recordatorios | Expo push / Firebase |
| **Image storage** | Fotos de plantas | A definir (S3/Cloudinary/...) |

---

## 6. Decisiones Arquitectónicas

| Decisión | Opción elegida | Alternativas | Motivo |
|:---------|:---------------|:-------------|:-------|
| Arquitectura backend | Modular por feature | Clean Architecture, Capas | Balance entre estructura y velocidad |
| ORM | SQLAlchemy 2.0 async | SQLModel, Tortoise | Madurez, async nativo, alembic |
| DB | PostgreSQL | SQLite, MySQL | pgvector futuro, open source |
| Frontend framework | Expo + React Native | Flutter, Kotlin | Mejor soporte IA, TypeScript |
| Navegación | React Navigation | Expo Router | Ecosistema maduro |
| Estado global | Por ahora local → Zustand | Redux, Jotai, Context | Arrancar simple, escalar después |
| Auth | Google OAuth + Apple | Email/password, Firebase Auth | Sin gestión de contraseñas |
| API Style | REST | GraphQL | Simple, predecible, buena tooling |
