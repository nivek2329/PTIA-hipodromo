# Resumen de Proyecto y Solución Oficial — RacePulse AI (Hito 3)

- **Rama Git Oficial:** `hito-3` (en `c:\Users\kevin\Downloads\ptia proyecto\PTIA-hipodromo`)
- **ID de Conversación Antigravity:** `1c90860b-be76-4b73-9b76-104ea465561e`
- **Fecha de Consolidación:** 22 de noviembre de 2026
- **Integrantes:** Kevin Andrey Angel / Nicolas Santiago Sanchez

---

## 1. MVP Funcional Oficial en Localhost

Para el **Hito 3**, el sistema opera obligatoriamente como aplicación cliente-servidor en **`localhost:8000`** conectada a un backend activo de Inteligencia Artificial (FastAPI + Uvicorn + SQLite):
- **Servidor Web / Backend:** `app.py` (FastAPI + Uvicorn + Inferencia en tiempo real con pesos Plackett-Luce Softmax).
- **Lanzador Directo en Windows:** `iniciar_mvp.bat` (doble clic o desde CMD/PowerShell).
- **URL de la App Web:** `http://localhost:8000`
- **Documentación Swagger API REST:** `http://localhost:8000/docs`
- **Endpoint de Inferencia en Tiempo Real:** `POST http://localhost:8000/api/predict` (latencia < 1 ms).

---

## 2. Sistema de Autenticación, Seguridad y Roles (RBAC)

El acceso a la aplicación está protegido mediante un módulo de autenticación con base de datos relacional SQLite (`data/racepulse_users.sqlite3`), cookies seguras de sesión (`racepulse_session`) y contraseñas hasheadas con **PBKDF2 + HMAC-SHA256 (240,000 iteraciones)**:

| Usuario | Correo Electrónico | Rol | Contraseña | Vistas y Privilegios en la Aplicación |
| :--- | :--- | :--- | :--- | :--- |
| **Kevin** | `kevin@racepulse.local` | `admin` | `RacePulse-Kevin-2026!` | **Acceso Total:** Carreras, Participantes, Predicción, Evaluación y API `/api/artifacts` |
| **Nicolaz** | `nicolaz@racepulse.local` | `analista` | `RacePulse-Nicolaz-2026!` | Carreras, Participantes (simulador interactivo de ratings) y Predicción PEAS |
| **Andrey** | `andrey@racepulse.local` | `consulta` | `RacePulse-Andrey-2026!` | Carreras y Predicción básica (métricas internas protegidas contra fugas) |

> La pantalla de inicio de sesión incorpora la mascota oficial en un entorno panorámico nocturno del hipódromo (`fig_hito3_mvp_login.png`) y permite el registro de nuevas cuentas (asignadas por defecto al rol Consulta).

---

## 3. Identidad Visual, Mascota y Cero Desbordamiento (0px Overflow)

- **Paleta Oficial:** Dark & Gold (`#050608`, `#0B1322`, `#D6A63C`).
- **Mascota Oficial:**
  - En la pantalla de login: escena completa con pista iluminada de noche (`pulse_login_background.png`).
  - En la barra lateral del dashboard: avatar circular con borde dorado de 48px (`mascot_char.jpg`) y tarjeta "IA + Datos Hípicos".
- **Resoluciones Verificadas:** $1024 \times 576$, $1024 \times 649$ y $1280 \times 720$.
- **Desbordamiento:** **0 píxeles de scroll horizontal o vertical**. Todas las 8 columnas de la tabla de predicción, filtros, barras y factores son visibles sin cortes.

---

## 4. Documento Formal Word (Hito 3)

El documento técnico formal cumple con los lineamientos institucionales y la norma APA 7:
- **Ruta del Archivo:** [`docs/Proyecto_PTIA_Grupo2_Hito3.docx`](docs/Proyecto_PTIA_Grupo2_Hito3.docx) *(2.25 MB, 362 párrafos, 7 tablas formales)*
- **Script Generador Automatizado:** [`src/generate_doc_hito3.py`](src/generate_doc_hito3.py)
- **Figuras Oficiales Embebidas:**
  - *Figura 6:* Comparativa de Hit Rate@1 y Log-Loss multiclase (Test 2020).
  - *Figura 7:* Curva de transferencia Sha Tin $\rightarrow$ Happy Valley.
  - *Figura 8:* MVP Funcional Hito 3 — Módulo de Acceso, Autenticación PBKDF2 y Control de Roles con Mascota Oficial.
  - *Figura 9:* MVP Funcional Hito 3 — Panel de Análisis Hípico e Inferencia PEAS en vivo (RID 411357, Sha Tin).
  - *Figura 10:* MVP Funcional Hito 3 — Auditoría de Evaluación Global (2020) y Transferencia de Dominio.
  - *Figura 11:* MVP Funcional Hito 3 — Módulo de Creación de Carreras en Vivo e Inferencia Inmediata de Cartelera Matutina.

---

## 5. Justificaciones de Decisiones de Arquitectura e IA

1. **Control de Acceso RBAC (3 Roles vs. 1 Usuario):**
   - *Fundamento PEAS:* Los actuadores del agente impactan decisiones humanas de diferente criticidad.
   - *Admin:* MLOps, drift temporal, métricas out-of-time y salud del modelo.
   - *Analista:* Simulación contrafáctica (sliders de OR y peso) y panel táctico sin exponer pesos internos.
   - *Consulta:* Lectura de predicciones para apuestas; sin manipulación de datos ni acceso a propiedad intelectual.
2. **Modelo Plackett-Luce Softmax & GBDT vs. LLMs:**
   - La tarea es ranking multi-agente de suma cero con calibración estricta ($\sum p_i = 1.0$), determinismo y latencia < 1 ms (0.44 ms en CPU).
   - Los LLMs alucinan números, no garantizan suma unitaria, tienen sesgo de prompt y latencias superiores a 1000 ms.
3. **Módulo de Cartelera en Vivo ("Crear Carrera en Vivo"):**
   - En la vida real, el programa oficial de la tarde sale en la mañana. Permite ingresar hipódromo (nacional/internacional), distancia, pista y competidores (OR, jinete, cajón) para predecir antes de que se corra.

---

## 6. Comandos para Ejecución y Pruebas

```cmd
cd /d "c:\Users\kevin\Downloads\ptia proyecto\PTIA-hipodromo"

:: 1. Iniciar servidor FastAPI y abrir navegador automáticamente
iniciar_mvp.bat

:: 2. Re-entrenar y evaluar el pipeline temporal (2017–2020) desde cero
python src\pipeline_hito3.py

:: 3. Regenerar el documento Word oficial Hito 3
python src\generate_doc_hito3.py

:: 4. Abrir directamente el documento Word en Windows
start "" "docs\Proyecto_PTIA_Grupo2_Hito3.docx"
```
