# RacePulse AI — Predicción de Ganadores en Carreras de Caballos y Transferencia de Dominio entre Hipódromos

[![Asignatura](https://img.shields.io/badge/Asignatura-PTIA-blue.svg)](https://www.escuelaing.edu.co/)
[![Institución](https://img.shields.io/badge/Institución-Escuela%20Colombiana%20de%20Ingeniería-red.svg)](https://www.escuelaing.edu.co/)
[![Hito](https://img.shields.io/badge/Entrega-Hito%202%20(Problema%20y%20Avance%20Solución)-green.svg)]()
[![Licencia](https://img.shields.io/badge/Licencia-CC%20BY--NC%204.0-orange.svg)]()

> **Principios y Técnicas de Inteligencia Artificial (PTIA)**  
> **Grupo 2**  
> **Integrantes:**  
> • Kevin Andrey Angel  
> • Nicolas Santiago Sanchez  

---

## 📌 Enlaces Rápidos de la Entrega (Hito 2)

* 🎬 **Video de Sustentación (5 Minutos):** `[Enlace al Video de Sustentación - YouTube/Drive]` *(Ver guion técnico en `docs/Guion_Video_Hito2_Dos_Personas.docx`)*
* 🎨 **Prototipo Conceptual en Figma:** `[Enlace a Prototipo Figma Original]`
* 📄 **Documento Técnico de Avance (Hito 2):** [`docs/Proyecto_PTIA_Grupo2_Hito2.docx`](docs/Proyecto_PTIA_Grupo2_Hito2.docx)
* 📱 **Prototipo Móvil Interactivo:** [`prototipos/prototipo_hito2.html`](prototipos/prototipo_hito2.html)
* 🖥️ **Prototipo de Escritorio (Dashboard Panorámico):** [`prototipos/prototipo_desktop.html`](prototipos/prototipo_desktop.html)

---

## 🎯 Descripción General del Proyecto

**RacePulse AI** es un sistema inteligente diseñado para modelar la dinámica estocástica de las carreras hípicas y predecir probabilidades calibradas de victoria a partir de datos abiertos (*Hong Kong Jockey Club* / corpus hwaitt). 

El factor diferencial y núcleo de investigación del proyecto radica en la **Transferencia de Dominio (Domain Adaptation)** entre pistas con características físicas, geométricas y microclimáticas distintas (p. ej., desde el hipódromo principal de **Sha Tin** hacia **Happy Valley**), adaptando modelos base preentrenados mediante ajuste fino (*fine-tuning*) con una fracción reducida de datos locales.

---

## 🧠 Marco PEAS del Agente Racional (Hito 2)

El agente predictivo está formalizado bajo el marco **PEAS** (Russell & Norvig):

| Componente | Definición Formal | Implementación en RacePulse AI |
| :--- | :--- | :--- |
| **P (Performance / Rendimiento)** | Métrica cuantitativa de éxito de la predicción y toma de decisiones. | • **Calibración Probabilística:** Brier Score < 0.10 y Log-Loss multiclase.<br>• **Acierto Top-1 por carrera (Hit Rate@1):** > 35%.<br>• **Retorno de Inversión simulado:** ROI esperado positivo (+14.2%). |
| **E (Environment / Entorno)** | Propiedades formales del entorno de tareas. | • Parcialmente observable, altamente estocástico, secuencial, dinámico, continuo/discreto y multiagente competitivo. |
| **A (Actuators / Actuadores)** | Mecanismos de salida y visualización de decisiones. | • Interfaz web interactiva (móvil y escritorio).<br>• Distribución de probabilidad de victoria normalizada vía Softmax.<br>• Panel de explicabilidad algorítmica (SHAP / Feature Importance). |
| **S (Sensors / Sensores)** | Percepción y captura de datos del entorno y los competidores. | • Pipeline de ingesta tabular de datos históricos.<br>• Extractor de variables precompetencia: **edad**, **historial y efectividad previa**, **régimen nutricional y calorías diarias (kcal)**, **días de descanso**, **estado de salud veterinario**, **cajón/puesto de salida**, **tipo de superficie** y **humedad de pista**. |

---

## 🗂️ Estructura del Repositorio

```text
PTIA-hipodromo/
│
├── README.md                              # Documentación general y guía del repositorio
├── .gitignore                             # Exclusión de temporales y datasets masivos
│
├── prototipos/                            # Fuentes de diseño y experiencia de usuario
│   ├── prototipo_hito2.html               # Interfaz móvil interactiva (RacePulse mobile)
│   └── prototipo_desktop.html             # Interfaz widescreen panorámica para analistas (Desktop)
│
├── src/                                   # Fuentes del código y pipeline de IA
│   └── pipeline_preprocesamiento_hito2.py # Preprocesamiento, auditoría de variables y modelo baseline
│
├── data/                                  # Datos precompetencia enriquecidos
│   └── forward.csv                        # Muestra representativa 2020 con variables fisiológicas y de pista (33.708 filas)
│
└── docs/                                  # Documentación académica formal
    ├── Proyecto_PTIA_Grupo2_Hito2.docx    # Documento de entrega Hito 2 (Norma APA 7, 6 papers, PEAS)
    ├── Guion_Video_Hito2_Dos_Personas.docx# Guion técnico del video cronometrado para 2 presentadores
    └── Guion_Video_Hito2_5min.md          # Versión Markdown del guion de video (5 minutos)
```

---

## 🚀 Instrucciones de Ejecución

### 1. Visualización de los Prototipos Web (Sin dependencias)
Los prototipos son aplicaciones web interactivas completamente autocontenidas:
* **Prototipo Móvil:** Abre el archivo [`prototipos/prototipo_hito2.html`](prototipos/prototipo_hito2.html) en cualquier navegador moderno o actívalo con emulación de dispositivo móvil (`Ctrl + Shift + M` en Google Chrome).
* **Prototipo de Escritorio:** Abre el archivo [`prototipos/prototipo_desktop.html`](prototipos/prototipo_desktop.html) en pantalla completa.
  * Haz clic en el botón azul **"Simular Carrera y Ejecutar Inferencia PEAS"** para observar el cálculo probabilístico en tiempo real, latencia de inferencia (18 ms), selección del caballo ganador (*Waterproof* con 38.4%) y el panel de explicabilidad.

### 2. Ejecución del Pipeline en Python
Para auditar las variables fisiológicas del dataset y evaluar el modelo base:

```bash
# Clonar el repositorio
git clone -b develop https://github.com/nivek2329/PTIA-hipodromo.git
cd PTIA-hipodromo

# Ejecutar el script de preprocesamiento y auditoría PEAS
python src/pipeline_preprocesamiento_hito2.py
```

**Métricas arrojadas por la línea base en consola:**
* Brier Score de calibración: `0.0979`
* Log-Loss multiclase: `0.3470`
* Acierto Top-1 estimado: `38.1%`
* Ingesta verificada: 33.708 registros precompetencia con edad, dieta, calorías, descanso, cajón y salud.

---

## 🔬 Estado del Arte y Literatura Científica Indexada

El diseño metodológico se fundamenta en 6 investigaciones indexadas (IEEE, Springer, Elsevier):
1. **Pudaruth, Medardo & Kishnah (2013):** Modelos probabilísticos con Naive Bayes y KNN (58% accuracy en Top-3).
2. **Lessmann, Sung & Johnson (2012):** Calibración de probabilidad y Brier Score (0.0894) con retornos de inversión sostenibles (+12.4%).
3. **Chen, Zhang & Liu (2020):** Algoritmos de *Learning to Rank* (LambdaMART GBDT) sobre datos del HKJC (NDCG@3: 0.782).
4. **Davoodi & Khanteymoori (2010):** Redes neuronales perceptrón multicapa para estimación de tiempos de llegada (MAE: 0.42s).
5. **Passos, Araújo & Couceiro (2021):** *Isolation Forests* y detección de anomalías biomecánicas (AUC-ROC: 0.864).
6. **Bontemps et al. (2016):** Autoencoders LSTM para series temporales y degradación de rendimiento.

---

## 👥 Equipo de Trabajo
* **Kevin Andrey Angel** — Escuela Colombiana de Ingeniería Julio Garavito
* **Nicolas Santiago Sanchez** — Escuela Colombiana de Ingeniería Julio Garavito