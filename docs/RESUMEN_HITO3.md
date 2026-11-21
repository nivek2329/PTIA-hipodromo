# Resumen de Proyecto y Sesión — RacePulse AI (Hito 3)

- **Rama Git:** `hito-3` (en `c:\Users\kevin\Downloads\ptia proyecto\PTIA-hipodromo`)
- **ID de Conversación Antigravity:** `1c90860b-be76-4b73-9b76-104ea465561e`

## MVP Funcional Oficial en Localhost
Para el **Hito 3**, el sistema opera obligatoriamente como aplicación cliente-servidor en **`localhost:8000`** (no como archivo HTML estático):
- **Servidor Web / Backend:** `app.py` (FastAPI + Uvicorn + Inferencia en tiempo real con pesos Plackett-Luce Softmax).
- **Lanzador Directo en Windows:** `iniciar_mvp.bat` (doble clic o desde CMD).
- **URL de la App Web:** `http://localhost:8000`
- **Documentación Swagger API:** `http://localhost:8000/docs`
- **Endpoint REST:** `POST http://localhost:8000/api/predict`

## Comandos para Abrir en CMD
```cmd
cd /d "c:\Users\kevin\Downloads\ptia proyecto\PTIA-hipodromo"
iniciar_mvp.bat
```
O directamente con python:
```cmd
python app.py
```

Abrir el documento final de Word (Hito 3):
```cmd
start "" "c:\Users\kevin\Downloads\ptia proyecto\PTIA-hipodromo\docs\Proyecto_PTIA_Grupo2_Hito3.docx"
```

## Archivos Clave del Hito 3
1. `app.py` & `iniciar_mvp.bat`: Servidor web oficial y lanzador del MVP en localhost.
2. `docs/Proyecto_PTIA_Grupo2_Hito3.docx`: Documento formal del Hito 3 (Sección 7 Análisis de Resultados, Sección 8 Conclusiones, Sección 9.5 MVP en Localhost).
3. `src/pipeline_hito3.py`: Pipeline anti-fuga temporal (2017–2020) y experimento de transferencia Sha Tin -> Happy Valley.
4. `src/mvp_artifacts_hito3.json`: Artefactos exportados para inferencia y visualización.
5. `prototipos/mvp_hito3.html`: Interfaz servida en `http://localhost:8000/` con pulido visual Impeccable (0 hallazgos en detector).

## Pendientes Opcionales
- Subir la rama a GitHub: `git push -u origin hito-3`
- Grabar video de presentación (máx. 10 min) mostrando la app corriendo en `http://localhost:8000` y las diapositivas/documento.
