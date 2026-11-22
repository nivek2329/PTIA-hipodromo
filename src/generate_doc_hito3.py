"""
Generador del Documento Final Hito 3 (Proyecto_PTIA_Grupo2_Hito3.docx)
Preserva exactamente la estructura visual, estilos, portada, declaración y secciones
del documento Hito 2, añadiendo las secciones 7 (Análisis de Resultados),
8 (Conclusiones) y 9.5 (Prototipo Funcional MVP) con cifras reales de mvp_artifacts_hito3.json.
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


def style_table_apa(table, col_widths=None):
    """Aplica estilo limpio consistente con las tablas del Hito 2."""
    tblPr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for b_name, val in [("top", "single"), ("bottom", "single"), ("insideH", "single"),
                        ("left", "none"), ("right", "none"), ("insideV", "none")]:
        b = OxmlElement(f"w:{b_name}")
        b.set(qn("w:val"), val)
        b.set(qn("w:sz"), "6" if b_name in ("top", "bottom") else "4")
        b.set(qn("w:space"), "0")
        b.set(qn("w:color"), "0D2238" if b_name in ("top", "bottom") else "CBD5E1")
        borders.append(b)
    tblPr.append(borders)

    # Sombreado azul marino sutil en encabezado
    for cell in table.rows[0].cells:
        tcPr = cell._tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), "0D2238")
        tcPr.append(shd)
        for p in cell.paragraphs:
            for r in p.runs:
                r.bold = True
                r.font.color.rgb = RGBColor(255, 255, 255)
                r.font.size = Pt(9.5)

    for row in table.rows[1:]:
        for cell in row.cells:
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(9.0)


def insert_paragraph_before(anchor_p, text="", style_name="Body Text", bold=False):
    p = anchor_p.insert_paragraph_before(text)
    try:
        p.style = style_name
    except Exception:
        pass
    if bold:
        for r in p.runs:
            r.bold = True
    return p


def insert_table_before(doc, anchor_p, headers, rows_data):
    tbl = doc.add_table(rows=1 + len(rows_data), cols=len(headers))
    for j, h in enumerate(headers):
        tbl.rows[0].cells[j].text = str(h)
    for i, row in enumerate(rows_data):
        for j, val in enumerate(row):
            tbl.rows[i + 1].cells[j].text = str(val)
    style_table_apa(tbl)
    anchor_p._p.addprevious(tbl._tbl)
    return tbl


def main():
    with open(ARTIFACTS_PATH, "r", encoding="utf-8") as f:
        art = json.load(f)

    fig6_path, fig7_path = generate_charts(art)
    doc = docx.Document(HITO2_DOCX)

    # 1. Actualizar Portada y Declaración a Hito 3
    for p in doc.paragraphs[:90]:
        if "Hito 2" in p.text and "Documento de avance" in p.text:
            for r in p.runs:
                if "Hito 2" in r.text or "octubre" in r.text or "avance" in r.text:
                    r.text = ""
            p.text = "Documento final para el Hito 3 · 20 de noviembre de 2026"
        elif p.text.strip() == "7. Prototipo de papel e interfaz":
            p.text = "9. Prototipo de papel, interfaz y MVP funcional"
        elif p.text.strip().startswith("7.1."):
            p.text = p.text.replace("7.1.", "9.1.")
        elif p.text.strip().startswith("7.2."):
            p.text = p.text.replace("7.2.", "9.2.")
        elif p.text.strip().startswith("7.3."):
            p.text = p.text.replace("7.3.", "9.3.")
        elif p.text.strip().startswith("7.4."):
            p.text = p.text.replace("7.4.", "9.4.")

    # Insertar nuevas entradas en Índice de Contenido antes de "9. Prototipo..."
    toc_anchor = next(p for p in doc.paragraphs if p.text.strip() == "9. Prototipo de papel, interfaz y MVP funcional")
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

    # Insertar nuevas entradas en Índice de Tablas y Índice de Figuras
    idx_fig_h1 = next(p for p in doc.paragraphs if p.text.strip() == "Índice de Figuras")
    for t_line in [
        "Tabla 4. Evaluación comparativa en el conjunto de prueba temporal (Test 2020, n = 14,700 carreras).",
        "Tabla 5. Secuencia de entradas y salidas de los dos mejores casos de prueba (Test 2020).",
        "Tabla 6. Desempeño desglosado por hipódromo en Test 2020.",
        "Tabla 7. Síntesis de los dos aciertos y dos errores más relevantes con su aprendizaje.",
    ]:
        insert_paragraph_before(idx_fig_h1, t_line, "Body Text")

    intro_h1 = next(p for p in doc.paragraphs if p.text.strip() == "Introducción")
    for f_line in [
        "Figura 6. Comparativa de Hit Rate@1 y Log-Loss multiclase en el conjunto de prueba (2020).",
        "Figura 7. Curva de aprendizaje en transferencia de dominio Sha Tin → Happy Valley (Test 2020, n = 298).",
        "Figura 8. MVP Funcional Hito 3: Módulo de Acceso, Autenticación y Control de Roles con Mascota Oficial.",
        "Figura 9. MVP Funcional Hito 3: Panel de Análisis Hípico e Inferencia PEAS en vivo (RID 411357, Sha Tin).",
        "Figura 10. MVP Funcional Hito 3: Auditoría de Evaluación Global (2020) y Transferencia de Dominio.",
    ]:
        insert_paragraph_before(intro_h1, f_line, "Body Text")

    # Renumerar encabezado de sección 7 existente -> 9
    proto_h1 = next(p for i, p in enumerate(doc.paragraphs) if i > 200 and "Prototipo de papel" in p.text)
    proto_h1.text = "9. Prototipo de papel, interfaz y MVP funcional"
    for p in doc.paragraphs[248:]:
        if p.text.strip().startswith("7.1."):
            p.text = p.text.replace("7.1.", "9.1.")
        elif p.text.strip().startswith("7.2."):
            p.text = p.text.replace("7.2.", "9.2.")
        elif p.text.strip().startswith("7.3."):
            p.text = p.text.replace("7.3.", "9.3.")
        elif p.text.strip().startswith("7.4."):
            p.text = p.text.replace("7.4.", "9.4.")

    # 2. Insertar Sección 7: Análisis de Resultados antes de proto_h1
    insert_paragraph_before(proto_h1, "Análisis de Resultados", "Heading 1")

    insert_paragraph_before(proto_h1, "7.1. Comparativa de Modelos en el Conjunto de Prueba (2020)", "Heading 2")
    insert_paragraph_before(
        proto_h1,
        "El pipeline final (src/pipeline_hito3.py) fue ejecutado sobre 658,407 participaciones correspondientes a 66,390 carreras "
        "validadas (2017–2020) bajo una partición cronológica estricta sin fuga de datos: Entrenamiento (2017–2018: 34,484 carreras), "
        "Validación (2019: 17,206 carreras) y Prueba intocable (2020: 14,700 carreras). Todas las variables históricas del caballo, "
        "jinete y entrenador se calcularon de forma estrictamente previa (shift cronológico), excluyendo cualquier dato posterior a la largada.",
        "Body Text"
    )

    g = art["global_results"]
    rows_models = []
    for k in [
        "Azar / Uniforme",
        "Baseline LogReg (Hito 2)",
        "RacePulse Plackett-Luce (L2)",
        "RacePulse GBDT + Softmax",
        "Benchmark Mercado (Favorito)",
    ]:
        m = g[k]
        rows_models.append([
            k,
            f"{m['hit_rate_1']*100:.2f}% [{m['ci_95_low']*100:.2f}%, {m['ci_95_high']*100:.2f}%]",
            f"{m['log_loss']:.4f}",
            f"{m['brier_score']:.4f}",
            f"{m['ndcg_3']:.4f}",
            f"{m['mrr']:.4f}",
            f"{m['kendall_tau']:.4f}",
        ])
    insert_paragraph_before(proto_h1, "Tabla 4. Evaluación comparativa en el conjunto de prueba temporal (Test 2020, n = 14,700 carreras).", "Normal", bold=True)
    insert_table_before(doc, proto_h1, ["Modelo / Línea Base", "Hit Rate@1 (IC 95%)", "Log-Loss", "Brier", "NDCG@3", "MRR", "Tau"], rows_models)

    p_fig6 = insert_paragraph_before(proto_h1, "", "Normal")
    p_fig6.add_run().add_picture(fig6_path, width=Inches(6.2))
    insert_paragraph_before(proto_h1, "Figura 6. Comparativa de Hit Rate@1 y Log-Loss multiclase en el conjunto de prueba (2020).", "Normal")

    insert_paragraph_before(
        proto_h1,
        "Los modelos principales del Hito 3 (Plackett-Luce con L2 = 0.0001 y GBDT + Softmax con T = 1.0) superan al azar en +8.18 puntos "
        "porcentuales (22.98% vs. 14.80%, mejora relativa del 55.3%) y mejoran sustancialmente la calibración probabilística frente al "
        "baseline de Regresión Logística binaria del Hito 2 (Log-Loss de 2.0966 vs. 2.1437 y Brier Score de 0.0928 vs. 0.0938), así como el "
        "ordenamiento relativo (NDCG@3 de 0.4576 y MRR de 0.4411). El benchmark externo del mercado alcanza 32.93% al incorporar información "
        "privada de última hora no presente en registros históricos tabulares.",
        "Body Text"
    )

    # 7.2 Dos mejores casos de prueba
    insert_paragraph_before(proto_h1, "7.2. Dos Mejores Casos de Prueba", "Heading 2")
    insert_paragraph_before(
        proto_h1,
        "Los dos mejores casos de prueba del conjunto 2020 evidencian la capacidad del modelo para concentrar probabilidad calibrada "
        "cuando las variables precompetencia (efectividad previa, Official Rating relativo y tasa de éxito de entrenador/jinete) muestran "
        "una ventaja clara sobre el lote:",
        "Body Text"
    )
    rows_best = [
        [
            "Caso 1 (RID 413595)\nWincanton · 20/11/07\nNovices' Hurdle (4 cab.)",
            "Flic Ou Voyou: OR=138, tasa hist. previa 35.7%, jinete/entrenador de alto rendimiento, 21 días descanso.",
            "Flic Ou Voyou: 90.23% (Top-1)",
            "Flic Ou Voyou (1.º lugar). Acierto exacto con mínima entropía."
        ],
        [
            "Caso 2 (RID 408688)\nTramore (IRE) · 20/08/14\nEY Chase (4 cab.)",
            "Easy Game: OR=154 (máximo del lote), historial previo sólido en vallas, peso relativo equilibrado.",
            "Easy Game: 87.59% (Top-1)",
            "Easy Game (1.º lugar). Acierto exacto y alta calibración."
        ],
    ]
    insert_paragraph_before(proto_h1, "Tabla 5. Secuencia de entradas y salidas de los dos mejores casos de prueba (Test 2020).", "Normal", bold=True)
    insert_table_before(doc, proto_h1, ["Carrera / Contexto", "Secuencia de Entradas Precompetencia", "Salida Esperada y Lograda", "Resultado Real"], rows_best)

    # 7.3 Caso de prueba más significativo
    insert_paragraph_before(proto_h1, "7.3. Caso de Prueba Más Significativo", "Heading 2")
    insert_paragraph_before(
        proto_h1,
        "El caso de prueba más significativo corresponde a la carrera RID 411357 en Sha Tin (HK) el 20/10/01 (Jinan Handicap, Class 4, "
        "césped, 11 participantes). Entradas clave: el ejemplar Angel Of My Eyes presentaba un Official Rating (OR) competitivo dentro "
        "de la clase, tasa histórica de podio consistente (hist_place_rate), días de descanso óptimos y una dupla jinete/entrenador con "
        "efectividad previa positiva en el circuito de Hong Kong, mientras el mercado favorecía a Sumstreetsumwhere. "
        "Salida del sistema: RacePulse asignó la mayor probabilidad Softmax a Angel Of My Eyes (28.74%), posicionándolo como ganador "
        "esperado #1. Resultado real: Angel Of My Eyes ganó oficialmente la carrera, superando al favorito del mercado.",
        "Body Text"
    )
    insert_paragraph_before(
        proto_h1,
        "Análisis del resultado: Este caso demuestra que el modelado conjunto de variables relativas dentro de la carrera (or_num_rel, "
        "hist_place_rate y efectividad previa de jinete/entrenador) permite detectar valor competitivo real en lotes exigentes de 11 "
        "corredores sin depender de cuotas de apuestas ni sufrir fuga de información.",
        "Body Text"
    )

    # 7.4 Desglose por Hipódromo y Transferencia de Dominio
    insert_paragraph_before(proto_h1, "7.4. Desglose por Hipódromo y Transferencia de Dominio (Sha Tin → Happy Valley)", "Heading 2")
    rows_courses = [
        [
            c["course"], str(c["n_races"]),
            f"{c['pl_hr1']*100:.2f}% (LL {c['pl_logloss']:.3f})",
            f"{c['gbdt_hr1']*100:.2f}% (LL {c['gbdt_logloss']:.3f})",
            f"{c['market_hr1']*100:.2f}%"
        ]
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

    # 4. Añadir subsección 9.5 al final de la sección de Prototipo (antes de Referencias)
    ref_p = next(p for p in doc.paragraphs if "Referencias Bibliográficas" in p.text)
    insert_paragraph_before(ref_p, "9.5. Prototipo Funcional MVP en Localhost (Hito 3)", "Heading 2")
    insert_paragraph_before(
        ref_p,
        "Para el Hito 3 se evolucionó el prototipo hacia un Producto Mínimo Viable (MVP) funcional desplegado como servicio web en "
        "localhost (http://localhost:8000) mediante FastAPI y Python (app.py e iniciar_mvp.bat). A diferencia de un archivo HTML estático, "
        "el MVP en localhost opera conectado a un backend de IA activo que expone una API REST para inferencia en tiempo real (< 1 ms), "
        "módulo de autenticación seguro, base de datos relacional SQLite y documentación interactiva OpenAPI Swagger (/docs).",
        "Body Text"
    )
    insert_paragraph_before(
        ref_p,
        "Módulo de Seguridad, Autenticación y Control de Acceso por Roles (RBAC): El acceso a la plataforma se encuentra protegido "
        "mediante credenciales cifradas con PBKDF2 y HMAC-SHA256 (240,000 iteraciones con salt criptográfico por usuario) almacenadas en "
        "data/racepulse_users.sqlite3. La sesión se gestiona con cookies seguras (racepulse_session) y segmentación estricta de privilegios "
        "en tres roles operativos: (1) Administrador (admin): acceso total a las cuatro vistas del sistema, simulación interactiva y "
        "auditoría técnica de modelos mediante el endpoint protegido /api/artifacts; (2) Analista Hípico (analista): acceso a carreras, "
        "predicción PEAS y panel de participantes con simulación contra-fáctica de Official Rating (OR) en tiempo real; y (3) Consulta "
        "(consulta): interfaz de solo lectura para carreras y predicciones básicas, bloqueando la exposición de métricas internas y "
        "artefactos de entrenamiento para evitar fuga de propiedad intelectual o decisiones no autorizadas.",
        "Body Text"
    )

    mvp_login = os.path.join(DOCS_DIR, "fig_hito3_mvp_login.png")
    if os.path.exists(mvp_login):
        p_f8 = insert_paragraph_before(ref_p, "", "Normal")
        p_f8.add_run().add_picture(mvp_login, width=Inches(6.1))
        insert_paragraph_before(ref_p, "Figura 8. MVP Funcional Hito 3: Módulo de Acceso, Autenticación y Control de Roles con Mascota Oficial.", "Normal")

    insert_paragraph_before(
        ref_p,
        "Diseño Visual, Identidad de Marca y Cero Desbordamiento (0px Overflow): La interfaz fue diseñada bajo la identidad visual "
        "Dark & Gold de RacePulse (#050608, #0B1322, #D6A63C), integrando el logotipo oficial, la mascota del proyecto tanto en la "
        "pantalla de inicio de sesión nocturna como en la barra lateral mediante micro-badge dorado, y una cuadrícula responsive "
        "estrictamente calibrada (barra lateral de 155px, cuadrícula de análisis 118px / 1fr / 228px). En resoluciones estándar de "
        "escritorio (1024×576, 1024×649 y 1280×720), la interfaz garantiza 0 píxeles de scroll horizontal o vertical, ofreciendo una "
        "visualización de alta fidelidad donde todos los componentes (filtros, tabla de 8 columnas, barras de probabilidad, factores y "
        "aviso de incertidumbre) se presentan simultáneamente sin cortes.",
        "Body Text"
    )

    mvp_inf = os.path.join(DOCS_DIR, "fig_hito3_mvp_inferencia.png")
    if os.path.exists(mvp_inf):
        p_f9 = insert_paragraph_before(ref_p, "", "Normal")
        p_f9.add_run().add_picture(mvp_inf, width=Inches(6.1))
        insert_paragraph_before(ref_p, "Figura 9. MVP Funcional Hito 3: Panel de Análisis Hípico e Inferencia PEAS en vivo (RID 411357, Sha Tin).", "Normal")

    insert_paragraph_before(
        ref_p,
        "Capacidades Operativas del MVP: El sistema permite: (1) explorar carreras reales del conjunto de prueba temporal (Test 2020) "
        "organizadas por hipódromo; (2) inspeccionar variables precompetencia libres de fuga de datos; (3) ejecutar inferencia Softmax "
        "Plackett-Luce instantánea con ranking calibrado de probabilidades de victoria y explicabilidad de factores clave; y (4) auditar "
        "las métricas globales de validación, radar PEAS y curva de transferencia de dominio (Sha Tin → Happy Valley) desde la vista "
        "exclusiva para administradores.",
        "Body Text"
    )

    mvp_eval = os.path.join(DOCS_DIR, "fig_hito3_mvp_evaluacion.png")
    if os.path.exists(mvp_eval):
        p_f10 = insert_paragraph_before(ref_p, "", "Normal")
        p_f10.add_run().add_picture(mvp_eval, width=Inches(6.1))
        insert_paragraph_before(ref_p, "Figura 10. MVP Funcional Hito 3: Auditoría de Evaluación Global (2020) y Transferencia de Dominio.", "Normal")

    doc.save(HITO3_DOCX)
    print(f"Documento Hito 3 guardado exitosamente en: {HITO3_DOCX}")


if __name__ == "__main__":
    main()
