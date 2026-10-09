# Guion de Video de Sustentación - Hito 2
**Proyecto:** Predicción de Ganadores en Carreras de Caballos Mediante Datos Abiertos y Transferencia de Dominio entre Hipódromos  
**Asignatura:** Principios y Técnicas de Inteligencia Artificial (PTIA)  
**Grupo:** Grupo 2 - Escuela Colombiana de Ingeniería Julio Garavito  
**Duración Total Estimada:** 5:00 minutos (Ritmo: 130-140 palabras por minuto)

---

## Estructura General y Tiempos

| Bloque | Tiempo | Tema Principal | Apoyo Visual en Pantalla |
| :--- | :---: | :--- | :--- |
| **Bloque 1** | 0:00 - 0:45 (45s) | Introducción y Objetivo del Proyecto | Portada del documento y logo RacePulse |
| **Bloque 2** | 0:45 - 1:45 (60s) | Retroalimentación Formativa y Correcciones | Documento Word (Índices, Estado del Arte formal, Walk-Forward) |
| **Bloque 3** | 1:45 - 2:45 (60s) | Marco PEAS y Dataset Enriquecido | Tabla PEAS del documento y dataset CSV / código |
| **Bloque 4** | 2:45 - 4:15 (90s) | Demostración en Vivo: Prototipos Móvil y Desktop | Navegador con `prototipo_hito2.html` y `prototipo_desktop.html` |
| **Bloque 5** | 4:15 - 5:00 (45s) | Conclusiones y Próximos Pasos (Hito 3) | Diapositiva final / Vista de métricas consolidadas |

---

## Desglose Paso a Paso del Guion

### BLOQUE 1: Introducción y Contexto del Proyecto [0:00 - 0:45]
* **En Pantalla:** Abrir el documento Word [`Proyecto_PTIA_Grupo2_Hito2.docx`](file:///c:/Users/Manolo/Downloads/Hito1/Hito1/Proyecto_PTIA_Grupo2_Hito2.docx) en la portada y resumen. Mostrar el título oficial.
* **Tono:** Dinámico, profesional y seguro.

> **[Voz en off / Presentador]:**  
> *"Hola a todos y profesor. Somos el Grupo 2 de Inteligencia Artificial y hoy presentamos la sustentación del Hito 2 de nuestro proyecto: **Predicción de Ganadores en Carreras de Caballos Mediante Datos Abiertos y Transferencia de Dominio entre Hipódromos**.*  
>  
> *El objetivo principal de nuestro sistema, denominado **RacePulse AI**, es modelar la complejidad estocástica de las carreras hípicas mediante un agente inteligente capaz de estimar probabilidades calibradas de victoria, y más importante aún, adaptarse mediante transferencia de dominio entre pistas con características físicas y climáticas distintas, como Sha Tin y Happy Valley en Hong Kong.*  
>  
> *En este video mostraremos cómo atendimos punto por punto la retroalimentación formativa de Hito 1, la formalización del marco PEAS, el enriquecimiento fisiológico de los datos y la implementación de nuestros prototipos interactivos tanto móvil como de escritorio."*

---

### BLOQUE 2: Cumplimiento de la Retroalimentación Formativa [0:45 - 1:45]
* **En Pantalla:** Desplazarse por el documento Word mostrando la **Tabla de Contenido**, la **Lista de Figuras y Tablas**, y luego la sección del **Estado del Arte** con los artículos científicos.
* **Tono:** Riguroso, académico y reflexivo.

> **[Voz en off / Presentador]:**  
> *"Iniciamos revisando las correcciones estructurales derivadas del informe de retroalimentación de Hito 1.*  
>  
> *Primero, depuramos por completo el documento: eliminamos las preguntas guía del formato original y consolidamos una redacción académica fluida en tercera persona, incorporando tabla de contenido, índice de tablas e índice de figuras bajo norma APA 7.*  
>  
> *Segundo, atendiendo la observación sobre la revisión de literatura, reemplazamos las menciones a librerías estándar como scikit-learn o XGBoost por **seis artículos científicos indexados** de IEEE, Springer y Elsevier. Cada problema fue desglosado bajo la estructura metodológica formal de: **¿Qué hicieron?, ¿Cómo lo hicieron? y ¿Para qué sirvió?**, reportando métricas empíricas comparativas como Brier Scores inferiores a 0.09, NDCG de 0.78 y áreas bajo la curva ROC de 0.86.*  
>  
> *Tercero, blindamos la metodología contra el data leakage implementando una validación temporal **Walk-Forward**, y formalizamos la estrategia de **Domain Adaptation** mediante ajuste fino de pesos en capas densas para compensar el drift entre hipódromos."*

---

### BLOQUE 3: Implementación de Hito 2 - Marco PEAS y Datos Fisiológicos [1:45 - 2:45]
* **En Pantalla:** Mostrar la **Tabla 1 (Marco PEAS)** en el documento Word. Luego alternar rápidamente a la terminal o archivo CSV mostrando las nuevas columnas (`age`, `tipo_comida`, `calorias_diarias_kcal`, `carreras_previas`, `estado_terreno`, `humedad_pista_pct`, etc.).
* **Tono:** Explicativo y técnico.

> **[Voz en off / Presentador]:**  
> *"En los lineamientos del Hito 2, el núcleo central es la definición del agente racional bajo el marco **PEAS**:*  
>  
> * * **Rendimiento (Performance):** Calibración de probabilidades medida por Brier Score menor a 0.10, Log-Loss multiclase y Retorno de Inversión esperado simulado positivo.*  
> * * **Entorno (Environment):** Accesible pero parcialmente observable, estocástico, secuencial y dinámico.*  
> * * **Actuadores (Actuators):** Distribución de probabilidad normalizada vía Softmax, ranking ordenado de competidores y alertas tempranas de riesgo de sobreentrenamiento.*  
> * * **Sensores (Sensors):** Ingesta de telemetría de pista, cuotas en vivo y registros veterinarios.*  
>  
> *En paralelo, robustecimos nuestro dataset. Atendiendo la necesidad de modelar el estado real del caballo, agregamos variables fisiológicas y ambientales clave: la **edad**, **historial de carreras y victorias**, **régimen nutricional y calorías diarias**, **días de descanso**, **estado de salud veterinario**, y variables de pista como el **cajón o puesto de salida**, **tipo de superficie**, y el **porcentaje de humedad del terreno**."*

---

### BLOQUE 4: Demostración en Vivo de los Prototipos (Móvil y Escritorio) [2:45 - 4:15]
* **En Pantalla:**  
  1. Abrir en Chrome [`prototipo_hito2.html`](file:///c:/Users/Manolo/Downloads/Hito1/Hito1/prototipo_hito2.html) en modo móvil.
  2. Abrir luego en pantalla completa [`prototipo_desktop.html`](file:///c:/Users/Manolo/Downloads/Hito1/Hito1/prototipo_desktop.html).
  3. Hacer clic en **"Simular Carrera y Ejecutar Inferencia PEAS"** en vivo.
* **Tono:** Entusiasta, demostrativo y ágil.

> **[Voz en off / Presentador]:**  
> *"Pasemos ahora a la validación empírica con nuestros prototipos funcionales.*  
>  
> *(Mostrando `prototipo_hito2.html`)*  
> *Aquí observamos el prototipo móvil **RacePulse**, rediseñado fielmente a partir de los mockups conceptuales de Figma. Ofrece al usuario una experiencia intuitiva para consultar la carrera activa, las condiciones climáticas del hipódromo de Sha Tin y el análisis probabilístico de los ejemplares.*  
>  
> *(Cambiando a pantalla completa a `prototipo_desktop.html`)*  
> *Para entornos de analistas y operadores de hipódromo, desarrollamos esta versión de escritorio independiente. Contamos con una barra de navegación con telemetría en tiempo real, selector de hipódromos para transferencia de dominio y una grilla panorámica de carreras.*  
>  
> *En la tabla central observamos las variables enriquecidas de cada competidor: edad, cajón de salida, nutrición, historial y estado de salud.*  
>  
> *Al ejecutar la simulación de inferencia PEAS en tiempo real —con una latencia de solo 18 milisegundos— el modelo procesa la información y despliega a la izquierda al ganador proyectado: **Waterproof**, con un 38.4% de probabilidad, favorecido por su cajón interior número 1 y su óptimo descanso de 21 días.*  
>  
> *A la derecha, el agente retroalimenta sus métricas PEAS con un Brier Score de 0.0979 y un panel de explicabilidad mediante importancia de variables, confirmando la transparencia del algoritmo."*

---

### BLOQUE 5: Conclusiones y Próximos Pasos - Hito 3 [4:15 - 5:00]
* **En Pantalla:** Volver a la sección de Conclusiones del documento Word o mostrar la vista final del dashboard.
* **Tono:** Conclusivo, propositivo y formal.

> **[Voz en off / Presentador]:**  
> *"En conclusión, para este Hito 2 logramos cumplir a cabalidad con la retroalimentación docente y los lineamientos del curso:*  
> * *Transformamos el documento técnico en un informe formal y riguroso con base científica indexada.*  
> * *Implementamos formalmente el marco PEAS y un dataset enriquecido con fisiología animal y condiciones de pista.*  
> * *Y desarrollamos dos prototipos interactivos, móvil y de escritorio, listos para desplegar inferencia en tiempo real.*  
>  
> *Como próximos pasos para el Hito 3, avanzaremos hacia el entrenamiento y ajuste fino de los modelos de ensamble y redes neuronales, evaluando empíricamente la tasa de transferencia de dominio entre hipódromos y el impacto financiero de las predicciones.*  
>  
> *Muchas gracias por su atención."*

---

## Consejos para la Grabación del Video (Checklist)

1. **Resolución:** Graba la pantalla a 1080p (Full HD) usando OBS Studio, Loom o la barra de juegos de Windows (`Win + G`).
2. **Pestañas Listas:**  
   - Pestaña 1: Documento Word `Proyecto_PTIA_Grupo2_Hito2.docx` abierto en la portada.  
   - Pestaña 2: `prototipo_hito2.html` centrado en emulación de celular.  
   - Pestaña 3: `prototipo_desktop.html` maximizado en Google Chrome.
3. **Interacción:** No olvides hacer clic en el botón azul **"Simular Carrera y Ejecutar Inferencia PEAS"** en el minuto 3:40 para que se aprecie la animación y el cambio de probabilidades en tiempo real.
