# Resumen de Proyecto y Sesión — RacePulse AI (Hito 3)

- **Rama Git:** `hito-3` (creada desde `develop` en `c:\Users\kevin\Downloads\ptia proyecto\PTIA-hipodromo`)
- **ID de Conversación Antigravity:** `1c90860b-be76-4b73-9b76-104ea465561e`

## Archivos Clave del Hito 3
1. **Documento Final (Word):** `docs/Proyecto_PTIA_Grupo2_Hito3.docx`
   - Mantiene portada, estilos y estructura visual del Hito 2.
   - Incluye Secciones 7 (Análisis de Resultados), 8 (Conclusiones) y 9.5 (MVP Funcional con capturas reales).
2. **Pipeline ML Anti-Fuga y Transferencia:** `src/pipeline_hito3.py`
   - Evalúa 2017–2020 (66,390 carreras; Test 2020 = 14,700 carreras).
   - Exporta métricas y casos reales a `src/mvp_artifacts_hito3.json`.
3. **MVP Funcional (Backend + Frontend):**
   - Backend en vivo: `src/server_mvp.py` (puerto `8050`, endpoint `/api/predict`).
   - Interfaz Web: `prototipos/mvp_hito3.html` (pulido visual con `impeccable`, 0 hallazgos en detector).

## Comandos Rápidos para Abrir Mañana (CMD)
```cmd
cd /d "c:\Users\kevin\Downloads\ptia proyecto\PTIA-hipodromo"
python src\server_mvp.py
```
Abrir el documento de Word:
```cmd
start "" "c:\Users\kevin\Downloads\ptia proyecto\PTIA-hipodromo\docs\Proyecto_PTIA_Grupo2_Hito3.docx"
```

## Pendientes Opcionales para Mañana
- Subir la rama a GitHub: `git push -u origin hito-3`
- Grabar el video de presentación (máx. 10 min) mostrando resultados y demo del MVP.
