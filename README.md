# RacePulse AI — Predicción de Ganadores en Carreras de Caballos y Transferencia de Dominio entre Hipódromos

[![Asignatura](https://img.shields.io/badge/Asignatura-PTIA-blue.svg)](https://www.escuelaing.edu.co/)
[![Institución](https://img.shields.io/badge/Institución-Escuela%20Colombiana%20de%20Ingeniería-red.svg)](https://www.escuelaing.edu.co/)
[![Hito](https://img.shields.io/badge/Entrega-Hito%203%20(Solución%20Final%20y%20Evaluación)-green.svg)]()
[![Licencia](https://img.shields.io/badge/Licencia-CC%20BY--NC%204.0-orange.svg)]()

> **Principios y Técnicas de Inteligencia Artificial (PTIA)**  
> **Grupo 2**  
> **Integrantes:**  
> • Kevin Andrey Angel  
> • Nicolas Santiago Sanchez  

---

##  Enlaces Rápidos de la Entrega (Hito 3)

*  **Documento Técnico Final (Hito 3):** [`docs/Proyecto_PTIA_Grupo2_Hito3.docx`](docs/Proyecto_PTIA_Grupo2_Hito3.docx)
*  **Aplicación Web MVP en Localhost (Hito 3):** [`app.py`](app.py) o [`iniciar_mvp.bat`](iniciar_mvp.bat) (`http://localhost:8000`)
*  **Documentación Interactiva API REST:** [`http://localhost:8000/docs`](http://localhost:8000/docs) (OpenAPI / Swagger UI)
*  **Pipeline Final y Evaluación (Hito 3):** [`src/pipeline_hito3.py`](src/pipeline_hito3.py)
*  **Prototipos Anteriores de Interfaz (Hito 2):** [`prototipos/prototipo_hito2.html`](prototipos/prototipo_hito2.html) y [`prototipos/prototipo_desktop.html`](prototipos/prototipo_desktop.html)

---

##  Descripción General del Proyecto

**RacePulse AI** es un sistema inteligente diseñado para modelar la dinámica estocástica de las carreras hípicas y predecir probabilidades calibradas de victoria a partir de datos abiertos (*Hong Kong Jockey Club* / corpus hwaitt). 

El factor diferencial y núcleo de investigación del proyecto radica en la **Transferencia de Dominio (Domain Adaptation)** entre pistas con características físicas, geométricas y microclimáticas distintas (p. ej., desde el hipódromo principal de **Sha Tin** hacia **Happy Valley**), adaptando modelos base preentrenados mediante ajuste fino (*fine-tuning*) con una fracción reducida de datos locales.

---

##  Marco PEAS del Agente Racional (Hito 2)

El agente predictivo está formalizado bajo el marco **PEAS** (Russell & Norvig):

| Componente | Definición Formal | Implementación en RacePulse AI |
| :--- | :--- | :--- |
| **P (Performance / Rendimiento)** | Métrica cuantitativa de éxito de la predicción y toma de decisiones. | • **Calibración Probabilística:** Brier Score < 0.10 y Log-Loss multiclase.<br>• **Acierto Top-1 por carrera (Hit Rate@1):** > 35%.<br>• **Retorno de Inversión simulado:** ROI esperado positivo (+14.2%). |
| **E (Environment / Entorno)** | Propiedades formales del entorno de tareas. | • Parcialmente observable, altamente estocástico, secuencial, dinámico, continuo/discreto y multiagente competitivo. |
| **A (Actuators / Actuadores)** | Mecanismos de salida y visualización de decisiones. | • Interfaz web interactiva (móvil y escritorio).<br>• Distribución de probabilidad de victoria normalizada vía Softmax.<br>• Panel de explicabilidad algorítmica (SHAP / Feature Importance). |
| **S (Sensors / Sensores)** | Percepción y captura de datos del entorno y los competidores. | • Pipeline de ingesta tabular de datos históricos.<br>• Extractor de variables precompetencia: **edad**, **historial y efectividad previa**, **régimen nutricional y calorías diarias (kcal)**, **días de descanso**, **estado de salud veterinario**, **cajón/puesto de salida**, **tipo de superficie** y **humedad de pista**. |

---

##  Estructura del Repositorio

```text
PTIA-hipodromo/
│
├── README.md                              # Documentación general y guía técnica del repositorio
├── .gitignore                             # Exclusión de temporales y datasets masivos
├── app.py                                 # Servidor web FastAPI con endpoints REST, inferencia PEAS y autenticación
├── iniciar_mvp.bat                        # Lanzador automático del MVP en Windows
│
├── prototipos/                            # Aplicación web oficial y prototipos anteriores
│   ├── mvp_hito3.html                     # Interfaz oficial del MVP Hito 3 (tema Dark & Gold, 0px overflow)
│   ├── assets/                            # Logotipo, mascota oficial, estilos CSS y scripts cliente
│   │   ├── css/racepulse_dashboard.css    # Hoja de estilos del dashboard y modal de autenticación
│   │   ├── js/racepulse_app.js            # Controlador cliente, gestión de roles y vistas
│   │   ├── js/racepulse_api.js            # Cliente API con protección anti-fuga de artefactos
│   │   └── js/racepulse_charts.js         # Renderizado de gráficos de probabilidad y radar PEAS
│   ├── prototipo_hito2.html               # Prototipo conceptual móvil (Hito 2)
│   └── prototipo_desktop.html             # Prototipo conceptual de escritorio (Hito 2)
│
├── src/                                   # Modelos, pipelines de entrenamiento y generación de reportes
│   ├── pipeline_hito3.py                  # Pipeline cronológico anti-fuga (2017–2020) y transferencia
│   ├── generate_doc_hito3.py              # Generador automatizado del documento Word formal Hito 3
│   └── mvp_artifacts_hito3.json           # Pesos calibrados Plackett-Luce y métricas de evaluación
│
├── data/                                  # Bases de datos y muestras
│   ├── racepulse_users.sqlite3            # Base de datos relacional SQLite con usuarios y roles (RBAC)
│   └── forward.csv                        # Muestra representativa 2020 con variables precompetencia
│
└── docs/                                  # Documentación académica y figuras del Hito 3
    ├── Proyecto_PTIA_Grupo2_Hito3.docx    # Documento final formal Hito 3 (con capturas reales y APA 7)
    ├── Proyecto_PTIA_Grupo2_Hito2.docx    # Documento de entrega Hito 2
    ├── fig_hito3_mvp_login.png            # Captura de pantalla de inicio de sesión con mascota
    ├── fig_hito3_mvp_inferencia.png       # Captura del panel principal de análisis (1280x720)
    ├── fig_hito3_mvp_evaluacion.png       # Captura de la vista de evaluación global y transferencia
    └── RESUMEN_HITO3.md                   # Resumen ejecutivo de la entrega Hito 3
```

---

##  Instrucciones de Ejecución

### 1. Visualización de los Prototipos Web (Sin dependencias)
Los prototipos son aplicaciones web interactivas completamente autocontenidas:
* **Prototipo Móvil:** Abre el archivo [`prototipos/prototipo_hito2.html`](prototipos/prototipo_hito2.html) en cualquier navegador moderno o actívalo con emulación de dispositivo móvil (`Ctrl + Shift + M` en Google Chrome).
* **Prototipo de Escritorio:** Abre el archivo [`prototipos/prototipo_desktop.html`](prototipos/prototipo_desktop.html) en pantalla completa.
  * Haz clic en el botón azul **"Simular Carrera y Ejecutar Inferencia PEAS"** para observar el cálculo probabilístico en tiempo real, latencia de inferencia (18 ms), selección del caballo ganador (*Waterproof* con 38.4%) y el panel de explicabilidad.

### 2. Ejecución del MVP Funcional en Localhost (Hito 3)
A diferencia de los prototipos conceptuales del Hito 2, el **Hito 3** es una aplicación web funcional desplegada en **localhost** conectada en tiempo real al backend de Inteligencia Artificial mediante una API REST:

```bash
# Clonar la rama hito-3 (si es primera vez)
git clone -b hito-3 https://github.com/nivek2329/PTIA-hipodromo.git
cd PTIA-hipodromo

# Opción A (Recomendada en Windows):
# Haz doble clic en iniciar_mvp.bat o ejecútalo en consola:
.\iniciar_mvp.bat

# Opción B (Directamente con Python):
python app.py
```

La aplicación abrirá automáticamente en tu navegador:
* **Aplicación Web MVP:** [http://localhost:8000](http://localhost:8000)
* **Documentación Interactiva Swagger:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Endpoint de Inferencia en Tiempo Real:** `POST http://localhost:8000/api/predict` (latencia < 1 ms)

#### Cuentas de Acceso por Roles (Base de Datos SQLite)
La aplicación cuenta con control de acceso por roles (RBAC) y contraseñas cifradas (PBKDF2 + HMAC-SHA256):

| Usuario / Nombre | Correo Electrónico | Rol | Contraseña | Vistas Disponibles en la App |
| :--- | :--- | :--- | :--- | :--- |
| **Kevin** | `kevin@racepulse.local` | `admin` | `RacePulse-Kevin-2026!` | **Acceso total:** Carreras, Participantes, Predicción, Evaluación |
| **Nicolaz** | `nicolaz@racepulse.local` | `analista` | `RacePulse-Nicolaz-2026!` | Carreras, Participantes (simulador de ratings), Predicción |
| **Andrey** | `andrey@racepulse.local` | `consulta` | `RacePulse-Andrey-2026!` | Carreras, Predicción básica (métricas internas bloqueadas) |

> **Nota:** También es posible registrar nuevas cuentas desde el modal de acceso (las cuentas creadas desde la interfaz se asignan por defecto al rol `consulta`).

---

### 3. Re-entrenamiento y Pipeline de IA

**Métricas reales verificadas en Test 2020 (14,700 carreras):**
* **Azar / Uniforme:** Hit Rate@1 `14.80%` | Log-Loss `2.2596` | Brier `0.0971`
* **Baseline LogReg (Hito 2):** Hit Rate@1 `23.09%` | Log-Loss `2.1437` | Brier `0.0938`
* **RacePulse Plackett-Luce (L2):** Hit Rate@1 `22.80%` | Log-Loss `2.1106` | Brier `0.0930` | NDCG@3 `0.4558`
* **RacePulse GBDT + Softmax:** Hit Rate@1 `22.98%` | Log-Loss `2.0966` | Brier `0.0928` | NDCG@3 `0.4576`
* **Transferencia Zero-Shot (Sha Tin → Happy Valley, n=298):** Hit Rate@1 `21.81%` (vs. `13.76%` modelo global multiregión)

---

##  Estado del Arte y Literatura Científica Indexada

El diseño metodológico se fundamenta en 6 investigaciones indexadas (IEEE, Springer, Elsevier):
1. **Pudaruth, Medardo & Kishnah (2013):** Modelos probabilísticos con Naive Bayes y KNN (58% accuracy en Top-3).
2. **Lessmann, Sung & Johnson (2012):** Calibración de probabilidad y Brier Score (0.0894) con retornos de inversión sostenibles (+12.4%).
3. **Chen, Zhang & Liu (2020):** Algoritmos de *Learning to Rank* (LambdaMART GBDT) sobre datos del HKJC (NDCG@3: 0.782).
4. **Davoodi & Khanteymoori (2010):** Redes neuronales perceptrón multicapa para estimación de tiempos de llegada (MAE: 0.42s).
5. **Passos, Araújo & Couceiro (2021):** *Isolation Forests* y detección de anomalías biomecánicas (AUC-ROC: 0.864).
6. **Bontemps et al. (2016):** Autoencoders LSTM para series temporales y degradación de rendimiento.

---

