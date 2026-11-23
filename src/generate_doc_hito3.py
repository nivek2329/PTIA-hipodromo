"""
Script oficial de generación del Documento Final Hito 3 (RacePulse AI).
Toma como base el documento del Hito 2 (Proyecto_PTIA_Grupo2_Hito2.docx),
actualiza la portada y declaraciones al Hito 3, inserta la Sección 7 (Análisis de Resultados),
la Sección 8 (Conclusiones) y transforma la Sección 9 en:
"9. Evolución del Proyecto hacia la Solución Tecnológica: Arquitectura Backend, Interfaz de Usuario y MVP Funcional",
con todas las explicaciones de Backend, Base de Datos, PBKDF2, Roles PEAS, Interfaz Dark & Gold,
Diseño Responsivo Móvil/Tablet y Módulo de Carreras en Vivo, junto con las figuras 8 a 12.
"""

import json
import os
from copy import deepcopy

import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
import matplotlib.pyplot as plt
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "..", "docs")
ARTIFACTS_PATH = os.path.join(BASE_DIR, "mvp_artifacts_hito3.json")
HITO2_DOCX = os.path.join(DOCS_DIR, "Proyecto_PTIA_Grupo2_Hito2.docx")
HITO3_DOCX = os.path.join(DOCS_DIR, "Proyecto_PTIA_Grupo2_Hito3.docx")


def generate_charts(artifacts: dict):
    """Genera las figuras de resultados Hito 3 con la paleta visual RacePulse."""
    plt.rcParams["font.sans-serif"] = "DejaVu Sans"
    plt.rcParams["axes.edgecolor"] = "#cbd5e1"
    plt.rcParams["axes.linewidth"] = 0.8

    # Figura 6: Comparativa de Modelos en Test 2020 (HR@1 y Log-Loss)
    g = artifacts["global_results"]
    names = [
        "Azar\n(Uniforme)",
        "Baseline\nLogReg (H2)",
        "RacePulse\nPlackett-Luce",
        "RacePulse\nGBDT+Softmax",
        "Benchmark\nMercado",
    ]
    keys = [
        "Azar / Uniforme",
        "Baseline LogReg (Hito 2)",
        "RacePulse Plackett-Luce (L2)",
        "RacePulse GBDT + Softmax",
        "Benchmark Mercado (Favorito)",
    ]
    hr1 = [g[k]["hit_rate_1"] * 100 for k in keys]
    ll = [g[k]["log_loss"] for k in keys]
    colors = ["#94a3b8", "#64748b", "#0062ff", "#0d2238", "#10b981"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.2), dpi=220)
    bars1 = ax1.bar(names, hr1, color=colors, width=0.58, zorder=3)
    ax1.set_title("Acierto Top-1 (Hit Rate@1 %) en Test 2020", fontsize=10.5, fontweight="bold", color="#0d2238", pad=10)
    ax1.set_ylabel("Hit Rate@1 (%)", fontsize=9, color="#334155")
    ax1.set_ylim(0, 39)
    ax1.grid(axis="y", linestyle="--", alpha=0.45, zorder=0)
    ax1.tick_params(axis="x", labelsize=8)
    for b, val in zip(bars1, hr1):
        ax1.text(b.get_x() + b.get_width() / 2, val + 0.8, f"{val:.2f}%", ha="center", va="bottom", fontsize=8, fontweight="bold", color="#0f172a")

    bars2 = ax2.bar(names, ll, color=colors, width=0.58, zorder=3)
    ax2.set_title("Calibración: Log-Loss Multiclase (Menor es mejor)", fontsize=10.5, fontweight="bold", color="#0d2238", pad=10)
    ax2.set_ylabel("Log-Loss", fontsize=9, color="#334155")
    ax2.set_ylim(1.5, 2.45)
    ax2.grid(axis="y", linestyle="--", alpha=0.45, zorder=0)
    ax2.tick_params(axis="x", labelsize=8)
    for b, val in zip(bars2, ll):
        ax2.text(b.get_x() + b.get_width() / 2, val + 0.02, f"{val:.4f}", ha="center", va="bottom", fontsize=8, fontweight="bold", color="#0f172a")

    plt.tight_layout()
    fig6_path = os.path.join(DOCS_DIR, "fig_hito3_modelos.png")
    plt.savefig(fig6_path, dpi=220, bbox_inches="tight")
    plt.close()

    # Figura 7: Curva de Transferencia de Dominio Sha Tin -> Happy Valley
    tr = artifacts["transfer_results"]
    fracs = [int(t["fraction"] * 100) for t in tr]
    tr_hr = [t["transfer_hr1"] * 100 for t in tr]
    loc_hr = [t["local_hr1"] * 100 if t["local_hr1"] is not None else np.nan for t in tr]

    fig, ax = plt.subplots(figsize=(8.2, 4.0), dpi=220)
    ax.plot(fracs, tr_hr, marker="o", linewidth=2.4, color="#0062ff", label="Transferencia Sha Tin + Fine-Tuning HV", zorder=4)
    ax.plot(fracs[1:], loc_hr[1:], marker="s", linewidth=2.2, linestyle="--", color="#f59e0b", label="Solo Local (Happy Valley)", zorder=3)
    ax.axhline(13.76, color="#94a3b8", linestyle=":", linewidth=1.6, label="Modelo Global Multiregión (13.76%)")
    ax.axhline(23.83, color="#10b981", linestyle="-.", linewidth=1.5, label="Techo Mercado en Happy Valley (23.83%)")

    ax.set_title("Transferencia de Dominio: Sha Tin (HK) → Happy Valley (HK) en Test 2020 (n=298)", fontsize=10.5, fontweight="bold", color="#0d2238", pad=10)
    ax.set_xlabel("Porcentaje de carreras locales de Happy Valley usadas en ajuste (%)", fontsize=9, color="#334155")
    ax.set_ylabel("Hit Rate@1 (%)", fontsize=9, color="#334155")
    ax.set_xticks(fracs)
    ax.set_xticklabels([f"{f}%\n({t['n_local_races']} carr.)" for f, t in zip(fracs, tr)], fontsize=8)
    ax.set_ylim(12, 26)
    ax.grid(True, linestyle="--", alpha=0.45)
    ax.legend(fontsize=8, loc="lower right")
    plt.tight_layout()
    fig7_path = os.path.join(DOCS_DIR, "fig_hito3_transferencia.png")
    plt.savefig(fig7_path, dpi=220, bbox_inches="tight")
    plt.close()

    return fig6_path, fig7_path


def style_table_apa(tbl):
    """Aplica estilo limpio consistente con las tablas del Hito 2."""
    tbl.autofit = False
    for r_idx, row in enumerate(tbl.rows):
        for c_idx, cell in enumerate(row.cells):
            tcPr = cell._tc.get_or_add_tcPr()
            tcBorders = OxmlElement("w:tcBorders")

            top = OxmlElement("w:top")
            top.set(qn("w:val"), "single" if (r_idx == 0 or r_idx == 1) else "none")
            top.set(qn("w:sz"), "6" if r_idx == 0 else "4")
            top.set(qn("w:space"), "0")
            top.set(qn("w:color"), "0f172a" if r_idx == 0 else "cbd5e1")
            tcBorders.append(top)

            bottom = OxmlElement("w:bottom")
            is_last = (r_idx == len(tbl.rows) - 1)
            bottom.set(qn("w:val"), "single" if (r_idx == 0 or is_last) else "none")
            bottom.set(qn("w:sz"), "6" if is_last else "4")
            bottom.set(qn("w:space"), "0")
            bottom.set(qn("w:color"), "0f172a")
            tcBorders.append(bottom)

            for side in ["left", "right"]:
                el = OxmlElement(f"w:{side}")
                el.set(qn("w:val"), "none")
                tcBorders.append(el)

            tcPr.append(tcBorders)

            if r_idx == 0:
                shd = OxmlElement("w:shd")
                shd.set(qn("w:val"), "clear")
                shd.set(qn("w:color"), "auto")
                shd.set(qn("w:fill"), "f1f5f9")
                tcPr.append(shd)
            elif r_idx % 2 == 1:
                shd = OxmlElement("w:shd")
                shd.set(qn("w:val"), "clear")
                shd.set(qn("w:color"), "auto")
                shd.set(qn("w:fill"), "fafafa")
                tcPr.append(shd)

            for p in cell.paragraphs:
                p.paragraph_format.space_before = Pt(3)
                p.paragraph_format.space_after = Pt(3)
                p.paragraph_format.line_spacing = 1.05
                for r in p.runs:
                    r.font.size = Pt(8.5)
                    r.font.name = "Calibri"
                    if r_idx == 0:
                        r.font.bold = True
                        r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)


def insert_paragraph_before(target_p, text, style_name="Body Text", bold=False):
    """Inserta un párrafo antes del objetivo con el estilo especificado."""
    p_obj = target_p.insert_paragraph_before(text, style=style_name)
    if bold:
        for r in p_obj.runs:
            r.bold = True
    p_obj.paragraph_format.space_before = Pt(4)
    p_obj.paragraph_format.space_after = Pt(4)
    p_obj.paragraph_format.line_spacing = 1.15
    return p_obj


def insert_table_before(doc, target_p, headers, rows):
    """Inserta una tabla con formato APA antes del párrafo objetivo."""
    tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    for c_idx, h in enumerate(headers):
        tbl.rows[0].cells[c_idx].paragraphs[0].text = h
    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            tbl.rows[r_idx + 1].cells[c_idx].paragraphs[0].text = str(val)
    style_table_apa(tbl)
    target_p._element.addprevious(tbl._element)
    space_p = doc.add_paragraph()
    space_p.paragraph_format.space_before = Pt(0)
    space_p.paragraph_format.space_after = Pt(4)
    target_p._element.addprevious(space_p._element)


def main():
    print("Iniciando generación completa del documento Hito 3...")
    with open(ARTIFACTS_PATH, "r", encoding="utf-8") as f:
        art = json.load(f)

    fig6_path, fig7_path = generate_charts(art)
    doc = docx.Document(HITO2_DOCX)

    SECTION9_TITLE = "9. Evolución del Proyecto hacia la Solución Tecnológica: Arquitectura Backend, Interfaz de Usuario y MVP Funcional"

    # 1. Actualizar Portada y Declaración a Hito 3
    for p in doc.paragraphs[:90]:
        if "Hito 2" in p.text and "Documento de avance" in p.text:
            for r in p.runs:
                if "Hito 2" in r.text or "octubre" in r.text or "avance" in r.text:
                    r.text = ""
            p.text = "Documento final para el Hito 3 · 20 de noviembre de 2026"
        elif p.text.strip() == "7. Prototipo de papel e interfaz":
            p.text = SECTION9_TITLE
        elif p.text.strip().startswith("7.1."):
            p.text = "9.1. Prototipo Conceptual en Papel y Bocetos Iniciales (Hito 2)"
        elif p.text.strip().startswith("7.2."):
            p.text = "9.1.1. Prototipo de Interfaz Navegable Interactivo (Hito 2)"
        elif p.text.strip().startswith("7.3."):
            p.text = "9.1.2. Detalle de Pantallas Iniciales y Validación de Interacción"
        elif p.text.strip().startswith("7.4."):
            p.text = "9.1.3. Manejo de Estados con Datos Incompletos y Caballos Debutantes"

    # Insertar nuevas entradas en Índice de Contenido antes de Sección 9
    toc_anchor = next(p for p in doc.paragraphs if p.text.strip() == SECTION9_TITLE)
    for line in [
        "7. Análisis de Resultados",
        "7.1. Comparativa de Modelos en el Conjunto de Prueba (2020)",
        "7.2. Dos Mejores Casos de Prueba",
        "7.3. Caso de Prueba Más Significativo",
        "7.4. Desglose por Hipódromo y Transferencia de Dominio (Sha Tin → Happy Valley)",
        "8. Conclusiones",
        "8.1. Dos Aciertos y Dos Errores Más Relevantes",
        "8.2. Conclusiones Evidentes y Trabajo Futuro",
    ]:
        insert_paragraph_before(toc_anchor, line, "Body Text")

    # Insertar subsecciones 9.2 a 9.5 en Índice de Contenido después de 9.1.3
    try:
        p_913 = next(p for i, p in enumerate(doc.paragraphs) if i < 120 and "9.1.3" in p.text)
        insert_paragraph_before(p_913, "9.2. Transición y Justificación Arquitectónica: Ranking Plackett-Luce vs. Modelos de Lenguaje (LLMs)", "Body Text")
        insert_paragraph_before(p_913, "9.3. Arquitectura del Backend, Almacenamiento y Control de Acceso (RBAC)", "Body Text")
        insert_paragraph_before(p_913, "9.4. Interfaz de Usuario Final (Frontend) y Diseño Responsivo Multiplataforma", "Body Text")
        insert_paragraph_before(p_913, "9.5. Módulo de Cartelera en Vivo: Ingesta de Nuevas Carreras Matutinas", "Body Text")
    except StopIteration:
        pass

    # Insertar nuevas entradas en Índice de Tablas
    idx_fig_h1 = next(p for p in doc.paragraphs if p.text.strip() == "Índice de Figuras")
    for t_line in [
        "Tabla 4. Evaluación comparativa en el conjunto de prueba temporal (Test 2020, n = 14,700 carreras).",
        "Tabla 5. Secuencia de entradas y salidas de los dos mejores casos de prueba (Test 2020).",
        "Tabla 6. Desempeño desglosado por hipódromo en Test 2020.",
        "Tabla 7. Síntesis de los dos aciertos y dos errores más relevantes con su aprendizaje.",
    ]:
        insert_paragraph_before(idx_fig_h1, t_line, "Body Text")

    # Insertar nuevas entradas en Índice de Figuras
    intro_h1 = next(p for p in doc.paragraphs if p.text.strip() == "Introducción")
    for f_line in [
        "Figura 6. Comparativa de Hit Rate@1 y Log-Loss multiclase en el conjunto de prueba (2020).",
        "Figura 7. Curva de aprendizaje en transferencia de dominio Sha Tin → Happy Valley (Test 2020, n = 298).",
        "Figura 8. MVP Funcional Hito 3: Módulo de Acceso, Autenticación PBKDF2 y Control de Roles con Mascota Oficial.",
        "Figura 9. MVP Funcional Hito 3: Panel de Análisis Hípico e Inferencia PEAS en vivo (Dashboard Web en Localhost).",
        "Figura 10. MVP Funcional Hito 3: Auditoría de Evaluación Global (2020) y Transferencia de Dominio.",
        "Figura 11. MVP Funcional Hito 3: Adaptación Móvil Responsiva de RacePulse AI (Vista Smartphone con Barra Inferior Táctil).",
        "Figura 12. MVP Funcional Hito 3: Módulo de Creación de Carreras en Vivo e Inferencia Inmediata de Cartelera Matutina.",
    ]:
        insert_paragraph_before(intro_h1, f_line, "Body Text")

    # Renombrar encabezado de sección 7 en el CUERPO del documento (i > 200) -> 9
    proto_h1 = next(p for i, p in enumerate(doc.paragraphs) if i > 200 and "Prototipo de papel" in p.text)
    proto_h1.text = SECTION9_TITLE
    for p in doc.paragraphs[240:]:
        if p.text.strip().startswith("7.1."):
            p.text = "9.1. Prototipo Conceptual en Papel y Bocetos Iniciales (Hito 2)"
        elif p.text.strip().startswith("7.2."):
            p.text = "9.1.1. Prototipo de Interfaz Navegable Interactivo (Hito 2)"
        elif p.text.strip().startswith("7.3."):
            p.text = "9.1.2. Detalle de Pantallas Iniciales y Validación de Interacción"
        elif p.text.strip().startswith("7.4."):
            p.text = "9.1.3. Manejo de Estados con Datos Incompletos y Caballos Debutantes"

    # 2. Insertar Sección 7: Análisis de Resultados antes de proto_h1
    insert_paragraph_before(proto_h1, "Análisis de Resultados", "Heading 1")
    insert_paragraph_before(proto_h1, "7.1. Comparativa de Modelos en el Conjunto de Prueba (2020)", "Heading 2")
    insert_paragraph_before(
        proto_h1,
        "La evaluación cuantitativa del Hito 3 se llevó a cabo sobre el conjunto de prueba temporal estricto (Test 2020, "
        "n = 14,700 carreras), respetando el protocolo anti-fuga de datos cronológico. Ninguna carrera ni participante de dicho "
        "período intervino en el ajuste de hiperparámetros ni en el entrenamiento del modelo. Se evaluaron cuatro aproximaciones "
        "técnicas y se contrastaron contra las cuotas implícitas finales del mercado de apuestas.",
        "Body Text"
    )

    g = art["global_results"]
    rows_modelos = [
        ["Azar (Uniforme)", f"{g['Azar / Uniforme']['hit_rate_1']*100:.2f}%", f"{g['Azar / Uniforme']['brier_score']:.4f}", f"{g['Azar / Uniforme']['log_loss']:.4f}", "Pérdida simétrica sin información previa"],
        ["Baseline LogReg (Hito 2)", f"{g['Baseline LogReg (Hito 2)']['hit_rate_1']*100:.2f}%", f"{g['Baseline LogReg (Hito 2)']['brier_score']:.4f}", f"{g['Baseline LogReg (Hito 2)']['log_loss']:.4f}", "Regresión logística binaria sin acoplamiento intra-carrera"],
        ["RacePulse Plackett-Luce (L2)", f"{g['RacePulse Plackett-Luce (L2)']['hit_rate_1']*100:.2f}%", f"{g['RacePulse Plackett-Luce (L2)']['brier_score']:.4f}", f"{g['RacePulse Plackett-Luce (L2)']['log_loss']:.4f}", "Modelo Softmax multiclase con regularización L2 (alpha=1e-4)"],
        ["RacePulse GBDT + Softmax", f"{g['RacePulse GBDT + Softmax']['hit_rate_1']*100:.2f}%", f"{g['RacePulse GBDT + Softmax']['brier_score']:.4f}", f"{g['RacePulse GBDT + Softmax']['log_loss']:.4f}", "Gradiente Boosted Trees con normalización de ranking por carrera"],
        ["Benchmark Mercado (Cuotas)", f"{g['Benchmark Mercado (Favorito)']['hit_rate_1']*100:.2f}%", f"{g['Benchmark Mercado (Favorito)']['brier_score']:.4f}", f"{g['Benchmark Mercado (Favorito)']['log_loss']:.4f}", "Cuotas finales de taquilla pública (con margen del operador 15-20%)"]
    ]
    insert_paragraph_before(proto_h1, "Tabla 4. Evaluación comparativa en el conjunto de prueba temporal (Test 2020, n = 14,700 carreras).", "Normal", bold=True)
    insert_table_before(doc, proto_h1, ["Modelo / Enfoque", "Hit Rate @ 1", "Brier Score", "Log-Loss", "Descripción Técnica"], rows_modelos)

    p_fig6 = insert_paragraph_before(proto_h1, "", "Normal")
    p_fig6.add_run().add_picture(fig6_path, width=Inches(6.0))
    insert_paragraph_before(proto_h1, "Figura 6. Comparativa de Hit Rate@1 y Log-Loss multiclase en el conjunto de prueba (2020).", "Normal")

    insert_paragraph_before(
        proto_h1,
        "Análisis de hallazgos (Objetivo 5.4 y 5.5): El modelo RacePulse GBDT + Softmax alcanzó un acierto Top-1 del 22.98% "
        "(3,378 victorias predichas de 14,700 carreras), superando holgadamente la cota del azar (+8.18 puntos porcentuales) y mejorando "
        "el baseline de Regresión Logística binaria del Hito 2 (Log-Loss de 2.0966 vs. 2.1437 y Brier Score de 0.0928 vs. 0.0938). "
        "El modelo lineal Plackett-Luce regularizado demostró gran robustez (21.75% HR@1 y Log-Loss 2.1465), operando con latencia inferior "
        "a 1 milisegundo por carrera, lo que fundamenta su selección como motor analítico en el MVP funcional.",
        "Body Text"
    )

    insert_paragraph_before(proto_h1, "7.2. Dos Mejores Casos de Prueba", "Heading 2")
    insert_paragraph_before(
        proto_h1,
        "Para verificar la coherencia de la inferencia, se auditaron las secuencias de entrada y salida de los dos casos de prueba con mayor "
        "margen de calibración en el conjunto de test (Test 2020):",
        "Body Text"
    )

    tc = art["test_cases"]
    rows_cases = [
        [
            f"Caso 1 (RID {tc[0]['rid']})\n{tc[0]['course']} - {tc[0]['race_name']}",
            f"{tc[0]['horses'][0]['horseName']} (OR: {tc[0]['horses'][0]['official_rating']}, {tc[0]['horses'][0]['weight_kg']} kg, Cajón {tc[0]['horses'][0]['stall']})\nHistorial: {tc[0]['horses'][0]['hist_win_rate']}% ganadas",
            f"P(Victoria) = {tc[0]['predicted_probs'][0]:.2f}%\nPosición predicha: 1°\nPosición real: 1° (Ganador)\nCuota taquilla: {tc[0]['horses'][0]['market_odds']}",
            "Ventaja clara en Official Rating (+7 pts sobre promedio) y asignación favorable en cajón interior."
        ],
        [
            f"Caso 2 (RID {tc[1]['rid']})\n{tc[1]['course']} - {tc[1]['race_name']}",
            f"{tc[1]['horses'][0]['horseName']} (OR: {tc[1]['horses'][0]['official_rating']}, {tc[1]['horses'][0]['weight_kg']} kg, Cajón {tc[1]['horses'][0]['stall']})\nHistorial: {tc[1]['horses'][0]['hist_win_rate']}% ganadas",
            f"P(Victoria) = {tc[1]['predicted_probs'][0]:.2f}%\nPosición predicha: 1°\nPosición real: 1° (Ganador)\nCuota taquilla: {tc[1]['horses'][0]['market_odds']}",
            "Consistencia en historial previo (3 victorias consecutivas) y balance peso-distancia óptimo en 1400m."
        ]
    ]
    insert_paragraph_before(proto_h1, "Tabla 5. Secuencia de entradas y salidas de los dos mejores casos de prueba (Test 2020).", "Normal", bold=True)
    insert_table_before(doc, proto_h1, ["Caso / Identificador", "Entradas Precompetencia Clave", "Salida del Agente PEAS", "Explicabilidad del Agente"], rows_cases)

    insert_paragraph_before(proto_h1, "7.3. Caso de Prueba Más Significativo", "Heading 2")
    insert_paragraph_before(
        proto_h1,
        "El caso de prueba más representativo corresponde a la carrera Jinan Handicap en el hipódromo de Sha Tin "
        "(RID 411357, fecha: 2020-10-20, superficie: Césped, distancia: 1400m). En esta prueba, "
        "el caballo 'Angel Of My Eyes' presentaba un Official Rating sobresaliente (86 puntos) con monta de "
        "Zac Purton en el cajón 3. El modelo RacePulse le otorgó una probabilidad del 28.74%, "
        "superando al segundo competidor ('Packing Angel': 22.17%) por un margen decisivo de "
        "+6.57 pp. El caballo resultó vencedor de la prueba, confirmando la capacidad del modelo para ponderar "
        "el handicap oficial y la ventaja biomecánica del cajón en carreras de césped de distancia media.",
        "Body Text"
    )

    insert_paragraph_before(proto_h1, "7.4. Desglose por Hipódromo y Transferencia de Dominio (Sha Tin → Happy Valley)", "Heading 2")
    rows_courses = [
        [c["course"], f"{c['n_races']:,}", f"{c['pl_hit_rate_1']*100:.2f}%", f"{c['gbdt_hit_rate_1']*100:.2f}%", f"{c['market_hit_rate_1']*100:.2f}%"]
        for c in art["course_breakdown"]
    ]
    insert_paragraph_before(proto_h1, "Tabla 6. Desempeño desglosado por hipódromo en Test 2020.", "Normal", bold=True)
    insert_table_before(doc, proto_h1, ["Hipódromo", "Carreras", "Plackett-Luce", "GBDT + Softmax", "Mercado"], rows_courses)

    p_fig7 = insert_paragraph_before(proto_h1, "", "Normal")
    p_fig7.add_run().add_picture(fig7_path, width=Inches(5.8))
    insert_paragraph_before(proto_h1, "Figura 7. Curva de aprendizaje en transferencia de dominio Sha Tin → Happy Valley (Test 2020, n = 298).", "Normal")

    insert_paragraph_before(
        proto_h1,
        "Hallazgo clave de transferencia de dominio (Objetivo 5.5): Mientras el modelo global entrenado con 34,484 carreras de múltiples "
        "países obtuvo 13.76% (Plackett-Luce) y 17.11% (GBDT) en Happy Valley (2020), la transferencia Zero-Shot desde Sha Tin (HK) "
        "alcanzó 21.81% Hit Rate@1 (Log-Loss 2.2972), acercándose al techo del mercado en esa pista (23.83%). Al realizar ajuste fino "
        "(fine-tuning) con 10% a 25% de carreras locales (90–225 carreras), la transferencia superó al entrenamiento exclusivamente local "
        "(18.79% vs. 17.45% con 10% de datos), confirmando que compartir la representación de un hipódromo hermano del mismo circuito "
        "(HKJC) evita el sobreajuste en pistas con muestra limitada.",
        "Body Text"
    )

    # 3. Insertar Sección 8: Conclusiones antes de proto_h1
    insert_paragraph_before(proto_h1, "Conclusiones", "Heading 1")
    insert_paragraph_before(proto_h1, "8.1. Dos Aciertos y Dos Errores Más Relevantes", "Heading 2")
    rows_learn = [
        [
            "Acierto 1: Protocolo Anti-Fuga y Softmax Plackett-Luce por Carrera",
            "Calcular estadísticas históricas con desplazamiento cronológico estricto y entrenar con pérdida Softmax intra-carrera produjo probabilidades calibradas (Log-Loss 2.0966 en GBDT+Softmax) y superó al azar en +8.18 pp.",
            "Aprendizaje: La normalización relativa dentro de cada carrera es indispensable en competencia multiagente; la regresión binaria independiente subestima la interacción entre rivales."
        ],
        [
            "Acierto 2: Transferencia Intra-Circuito (Sha Tin → Happy Valley)",
            "Transferir el modelo desde Sha Tin hacia Happy Valley (Zero-Shot: 21.81%) superó por +8.05 pp al modelo global multiregión (13.76%) y mejoró el entrenamiento local con pocos datos.",
            "Aprendizaje: La similitud institucional y de participantes (mismo circuito HKJC) pesa más que el volumen bruto de datos heterogéneos de otros países."
        ],
        [
            "Error 1: Sobreconfianza en Carreras de Vallas con Pocos Participantes",
            "En Sandown (RID 415054, 4 corredores), el modelo asignó 93.73% a Grand Mogul (quien también era favorito del mercado) y perdió ante Golden Boy Grey (3.03%).",
            "Aprendizaje: En carreras de obstáculos (Novices' Hurdle) existe riesgo de caída o fallo en salto no capturado por el rating previo; se requiere suavizado de temperatura o cota máxima de probabilidad."
        ],
        [
            "Error 2: Degradación por Muestra Pequeña en Fine-Tuning Local (Fakenham / HV)",
            "En Fakenham (RID 403137: Fix Sun 82.04% vs. Fraternel 1.84%) y al hacer fine-tuning agresivo en Happy Valley (de 21.81% Zero-Shot bajó a ~18.5%), el ajuste local sobreajustó ruido.",
            "Aprendizaje: En pistas altamente estocásticas, un prior fuerte hacia los pesos fuente o regularización L2 elevada previene la degradación por varianza muestral."
        ],
    ]
    insert_paragraph_before(proto_h1, "Tabla 7. Síntesis de los dos aciertos y dos errores más relevantes con su aprendizaje.", "Normal", bold=True)
    insert_table_before(doc, proto_h1, ["Hito / Caso", "Evidencia Cuantitativa", "Aprendizaje Técnico"], rows_learn)

    insert_paragraph_before(proto_h1, "8.2. Conclusiones Evidentes y Trabajo Futuro", "Heading 2")
    for c_txt in [
        "1. Viabilidad técnica comprobada sin fuga de datos: Es posible predecir ganadores hípicos con 22.98% de acierto Top-1 (vs. 14.80% al azar) y probabilidades calibradas (Log-Loss 2.0966) usando únicamente variables históricas precompetencia auditadas.",
        "2. Valor de la explicabilidad y la separación UI/Modelo: Aislar las variables simuladas de nutrición y veterinaria de la etapa de entrenamiento garantizó métricas honestas, mientras que los pesos Plackett-Luce explican cada decisión en tiempo real (< 1 ms).",
        "3. La transferencia de dominio requiere afinidad de circuito: Entrenar en un hipódromo hermano del mismo organismo (Sha Tin → Happy Valley) resulta más efectivo que mezclar miles de carreras de circuitos incompatibles.",
        "Trabajo futuro: Integrar series temporales de cuotas precompetencia con marca temporal verificable, incorporar embeddings de pedigrí (padre/madre/abuelo) y clima meteorológico por hora mediante APIs históricas, y evaluar pérdidas de ranking completo (LambdaRank / Plackett-Luce top-k)."
    ]:
        insert_paragraph_before(proto_h1, c_txt, "Body Text")

    # 4. AHORA EN LA SECCIÓN 9: Insertar las subsecciones 9.2 a 9.5 AL FINAL DE LA SECCIÓN 9
    # Buscamos la verdadera sección "Referencias Bibliográficas" al final del documento (índice > 240)
    real_ref_p = next(p for i, p in enumerate(doc.paragraphs) if i > 240 and "Referencias Bibliográficas" in p.text)

    # 9.2 Transición y Justificación Arquitectónica
    insert_paragraph_before(real_ref_p, "9.2. Transición y Justificación Arquitectónica: Ranking Plackett-Luce vs. Modelos de Lenguaje (LLMs)", "Heading 2")
    insert_paragraph_before(
        real_ref_p,
        "La evolución desde las maquetas conceptuales del Hito 2 hacia un Producto Mínimo Viable (MVP) operativo requirió tomar decisiones "
        "arquitectónicas determinantes sobre el paradigma de inteligencia artificial. Aunque en la actualidad existe una fuerte tendencia hacia el uso "
        "de Modelos de Lenguaje Masivos (LLMs), un análisis riguroso de la tarea hípica motivó el descarte de modelos generativos textuales en favor "
        "de arquitecturas dedicadas de Aprendizaje de Ranking Discreto (Learning to Rank - Plackett-Luce Softmax y GBDT), fundamentado en tres razones:",
        "Body Text"
    )
    insert_paragraph_before(
        real_ref_p,
        "1. Calibración Probabilística Estricta: Una carrera hípica es una competencia cerrada de suma cero entre N competidores mutuamente excluyentes "
        "(8 a 14 caballos). La probabilidad de victoria exige la restricción matemática formal sum_{i=1}^N P(Y_i=1) = 1.0. Los LLMs, al ser modelos autoregresivos "
        "token a token, son propensos a la alucinación numérica y no garantizan suma unitaria sin post-procesamiento. En contraste, la formulación "
        "Plackett-Luce optimiza directamente la probabilidad de elección discreta mediante Softmax multiclase acoplada a una utilidad latente w^T x_i, "
        "produciendo probabilidades calibradas con un Log-Loss de 2.0966 en test.",
        "Body Text"
    )
    insert_paragraph_before(
        real_ref_p,
        "2. Determinismo, Repetibilidad y Sin Sesgo de Prompt: El análisis cuantitativo exige que idénticas variables precompetencia produzcan resultados "
        "estrictamente reproducibles. Los LLMs introducen variabilidad estocástica por temperatura y son sensibles al orden de los caballos en el texto. "
        "El modelo Plackett-Luce regularizado garantiza invarianza matemática y neutralidad.",
        "Body Text"
    )
    insert_paragraph_before(
        real_ref_p,
        "3. Latencia Ultrabaja (< 1 ms) y Eficiencia Computacional: El motor en Python ejecuta la inferencia matricial de 14 ejemplares en 0.44 milisegundos "
        "en CPU estándar sin GPU ni conexión a nubes externas, mientras un LLM demandaría entre 800 y 3,500 ms con costos por token prohibitivos.",
        "Body Text"
    )

    # 9.3 Arquitectura del Backend, Almacenamiento y Control de Acceso (RBAC)
    insert_paragraph_before(real_ref_p, "9.3. Arquitectura del Backend, Almacenamiento y Control de Acceso (RBAC)", "Heading 2")
    insert_paragraph_before(
        real_ref_p,
        "A diferencia de una maqueta estática, el MVP funcional opera bajo una arquitectura cliente-servidor real desplegada localmente "
        "(http://localhost:8000 o en red local Wi-Fi mediante enlace 0.0.0.0). El backend está construido en Python mediante el framework "
        "asíncrono FastAPI y el servidor de alto rendimiento Uvicorn (app.py). Sus componentes arquitectónicos principales son:",
        "Body Text"
    )
    insert_paragraph_before(
        real_ref_p,
        "• API REST y Documentación Interactiva OpenAPI: Expone endpoints estructurados para inferencia (/api/predict), catálogo de pruebas (/api/races), "
        "autenticación (/api/auth/login, /api/auth/me, /api/auth/logout) y auditoría técnica (/api/artifacts), completamente documentados en tiempo real mediante Swagger (/docs).\n"
        "• Motor de Inferencia en Tiempo Real (run_live_plackett_luce_inference): Módulo en Python que realiza el preprocesamiento vectorial, estandarización "
        "Z-score por carrera, cálculo del producto punto w^T x_i y distribución Softmax en 0.44 ms, retornando además la contribución de los 4 factores explicativos dominantes.\n"
        "• Base de Datos Relacional y Seguridad PBKDF2: Los usuarios se gestionan en SQLite (data/racepulse_users.sqlite3). Las contraseñas se almacenan con salt aleatorio "
        "de 16 bytes y derivación de clave criptográfica PBKDF2-HMAC-SHA256 con 240,000 iteraciones. Las sesiones activas se manejan mediante tokens seguros "
        "en cookies HttpOnly con SameSite=Lax (racepulse_session), previniendo ataques XSS y CSRF.\n"
        "• Control de Acceso Basado en Roles (RBAC) bajo el Marco PEAS: Para responder a las responsabilidades de los diferentes actores del entorno, se implementaron 3 perfiles:",
        "Body Text"
    )
    insert_paragraph_before(
        real_ref_p,
        "1. Administrador (admin / Data Scientist & MLOps - Kevin): Acceso total a las 4 vistas del sistema. Habilita la vista de Evaluación (/api/artifacts) "
        "para auditar métricas fuera de muestra, curvas de aprendizaje temporal, drift del modelo y transferencia de dominio Sha Tin → Happy Valley.\n"
        "2. Analista Hípico (analista / Entrenador o Cuantitativo - Nicolaz): Acceso a Carreras, Predicción y al módulo de Participantes con simuladores contrafácticos "
        "de peso y rating, permitiendo evaluar escenarios hipotéticos ('qué pasaría si...') sin exponer la telemetría interna del servidor.\n"
        "3. Consulta (consulta / Apostador General o Aficionado - Andrey): Vista restringida para el público general, con acceso a predicciones y probabilidades "
        "oficiales pero con bloqueo de sliders de simulación y del panel de evaluación técnica, preservando la propiedad intelectual y evitando errores por datos ficticios.",
        "Body Text"
    )

    mvp_login = os.path.join(DOCS_DIR, "fig_hito3_mvp_login.png")
    if os.path.exists(mvp_login):
        p_f8 = insert_paragraph_before(real_ref_p, "", "Normal")
        p_f8.add_run().add_picture(mvp_login, width=Inches(6.1))
        insert_paragraph_before(real_ref_p, "Figura 8. MVP Funcional Hito 3: Módulo de Acceso, Autenticación PBKDF2 y Control de Roles con Mascota Oficial.", "Normal")

    # 9.4 Interfaz de Usuario Final (Frontend) y Diseño Responsivo Multiplataforma
    insert_paragraph_before(real_ref_p, "9.4. Interfaz de Usuario Final (Frontend) y Diseño Responsivo Multiplataforma", "Heading 2")
    insert_paragraph_before(
        real_ref_p,
        "La interfaz del MVP fue construida bajo la identidad visual Dark & Gold de RacePulse (#050608, #0B1322, #D6A63C), garantizando una experiencia "
        "estética de nivel profesional y alta legibilidad nocturna en cabinas de análisis. Entre sus elementos destacados se encuentran:",
        "Body Text"
    )
    insert_paragraph_before(
        real_ref_p,
        "• Hero Panorámico Superior Unificado: Bloque superior de 204 px de altura calibrado exactamente al nivel del botón 'Evaluación' de la barra lateral. "
        "Integra en alta resolución la imagen panorámica de la carrera en Sha Tin sin cortes, mostrando el ejemplar #3 con su jinete en plena acción, "
        "mientras en la columna izquierda se disponen los títulos y la tarjeta de carrera con datos de pista y participantes.\n"
        "• Cuadrícula de Análisis de 3 Columnas: Organiza los filtros de carrera (izquierda), la tabla detallada de participantes con resaltado dorado del "
        "ganador predicho (centro) y las barras horizontales de probabilidad de victoria con escala porcentual (derecha).\n"
        "• Cero Desbordamiento (0px Overflow) en Escritorio: En resoluciones estándar de portátiles y monitores (1024×576, 1280×720, 1366×768 y 1920×1080), "
        "las tarjetas inferiores de factores y notas se extienden hasta la base de la pantalla, logrando una presentación sin scrollbars innecesarios.\n"
        "• Diseño Responsivo para Smartphones y Tablets: Para su uso en campo (paddock o tribunas), el sistema cuenta con media queries fluidas (<= 880px). "
        "La barra lateral se transforma en una barra de navegación inferior táctil fija estilo aplicación móvil nativa, el contenido se apila en flujo vertical "
        "y la tabla de participantes incorpora desplazamiento horizontal táctil suave (-webkit-overflow-scrolling: touch) para preservar la integridad de sus 8 columnas.",
        "Body Text"
    )

    mvp_inf = os.path.join(DOCS_DIR, "fig_hito3_mvp_inferencia.png")
    if os.path.exists(mvp_inf):
        p_f9 = insert_paragraph_before(real_ref_p, "", "Normal")
        p_f9.add_run().add_picture(mvp_inf, width=Inches(6.1))
        insert_paragraph_before(real_ref_p, "Figura 9. MVP Funcional Hito 3: Panel de Análisis Hípico e Inferencia PEAS en vivo (Dashboard Web en Localhost).", "Normal")

    mvp_eval = os.path.join(DOCS_DIR, "fig_hito3_mvp_evaluacion.png")
    if os.path.exists(mvp_eval):
        p_f10 = insert_paragraph_before(real_ref_p, "", "Normal")
        p_f10.add_run().add_picture(mvp_eval, width=Inches(6.1))
        insert_paragraph_before(real_ref_p, "Figura 10. MVP Funcional Hito 3: Auditoría de Evaluación Global (2020) y Transferencia de Dominio.", "Normal")

    mvp_movil = os.path.join(DOCS_DIR, "fig_hito3_mvp_movil.png")
    if os.path.exists(mvp_movil):
        p_f11 = insert_paragraph_before(real_ref_p, "", "Normal")
        p_f11.add_run().add_picture(mvp_movil, width=Inches(2.7))
        insert_paragraph_before(real_ref_p, "Figura 11. MVP Funcional Hito 3: Adaptación Móvil Responsiva de RacePulse AI (Vista Smartphone con Barra Inferior Táctil).", "Normal")

    # 9.5 Módulo de Cartelera en Vivo: Ingesta de Nuevas Carreras Matutinas
    insert_paragraph_before(real_ref_p, "9.5. Módulo de Cartelera en Vivo: Ingesta de Nuevas Carreras Matutinas", "Heading 2")
    insert_paragraph_before(
        real_ref_p,
        "Una limitación crítica identificada durante la validación del prototipo fue que un sistema limitado exclusivamente a visualizar pruebas históricas "
        "carece de utilidad práctica en el día a día. En los hipódromos, las carteleras oficiales se publican durante la mañana para carreras que se corren en la tarde. "
        "Para que la solución sea verdaderamente funcional, el sistema debe permitir ingresar eventos nuevos y calcular probabilidades antes de la partida.",
        "Body Text"
    )
    insert_paragraph_before(
        real_ref_p,
        "Por esta razón, se desarrolló el módulo '+ Crear Carrera en Vivo' (#custom-race-modal). Este componente permite: (1) ingresar el hipódromo "
        "(circuitos locales o pistas internacionales); (2) fijar los parámetros físicos (nombre de la prueba, distancia en metros y superficie: Césped o Arena); "
        "y (3) matricular dinámicamente hasta 14 competidores con su nombre, Official Rating (OR), peso asignado en libras, cajón de salida (draw) y jinete. "
        "Al confirmar, el motor de inferencia calcula de inmediato las probabilidades de victoria, actualiza el hero banner, genera las barras de distribución "
        "doradas y habilita la simulación de escenarios contrafácticos al instante.",
        "Body Text"
    )

    mvp_custom = os.path.join(DOCS_DIR, "fig_hito3_mvp_carrera_en_vivo.png")
    if os.path.exists(mvp_custom):
        p_fc = insert_paragraph_before(real_ref_p, "", "Normal")
        p_fc.add_run().add_picture(mvp_custom, width=Inches(6.1))
        insert_paragraph_before(real_ref_p, "Figura 12. MVP Funcional Hito 3: Módulo de Creación de Carreras en Vivo e Inferencia Inmediata de Cartelera Matutina.", "Normal")

    doc.save(HITO3_DOCX)
    print(f"Documento Hito 3 generado y guardado exitosamente en: {HITO3_DOCX}")


if __name__ == "__main__":
    main()
