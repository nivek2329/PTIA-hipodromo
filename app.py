"""
Proyecto PTIA - Grupo 2: RacePulse AI (Hito 3 - Solución y Evaluación)
Servidor Web Oficial en Localhost (FastAPI + Uvicorn + Inferencia en Tiempo Real)
"""

import json
import os
import sys
import threading
import time
import webbrowser
from typing import Any, Dict, List, Optional

import numpy as np
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS_PATH = os.path.join(BASE_DIR, "src", "mvp_artifacts_hito3.json")
MVP_HTML_PATH = os.path.join(BASE_DIR, "prototipos", "mvp_hito3.html")
ASSETS_DIR = os.path.join(BASE_DIR, "prototipos", "assets")

if not os.path.exists(ARTIFACTS_PATH):
    # Fallback si se ejecuta desde dentro de src/
    ARTIFACTS_PATH = os.path.join(BASE_DIR, "mvp_artifacts_hito3.json")
    MVP_HTML_PATH = os.path.join(BASE_DIR, "..", "prototipos", "mvp_hito3.html")
    ASSETS_DIR = os.path.join(BASE_DIR, "..", "prototipos", "assets")

with open(ARTIFACTS_PATH, "r", encoding="utf-8") as f:
    ARTIFACTS = json.load(f)

META = ARTIFACTS["metadata"]
W = np.array(META["pl_weights"], dtype=np.float64)
MEAN = np.array(META["pl_mean"], dtype=np.float64)
STD = np.array(META["pl_std"], dtype=np.float64)
FEAT_COLS = META["feature_cols"]

app = FastAPI(
    title="RacePulse AI · MVP Funcional (PTIA Grupo 2 · Hito 3)",
    description=(
        "Servicio web en localhost para la predicción de ganadores en carreras de caballos "
        "mediante modelos Softmax Plackett-Luce anti-fuga y transferencia de dominio (Sha Tin -> Happy Valley)."
    ),
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_no_cache_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if os.path.exists(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")


class PredictRequest(BaseModel):
    horses: List[Dict[str, Any]]
    race_ctx: Dict[str, Any] = {}


def run_live_plackett_luce_inference(horses: list, race_ctx: dict) -> dict:
    """Ejecuta inferencia Softmax Plackett-Luce en Python y calcula contribuciones por factor."""
    t0 = time.perf_counter()
    n = len(horses)
    if n == 0:
        return {"error": "No hay participantes en la carrera"}

    or_vals = [float(h.get("official_rating") or 75.0) for h in horses]
    w_vals = [float(h.get("weight_kg") or 57.0) for h in horses]
    hwr_vals = [float(h.get("hist_win_rate") or 10.0) / 100.0 for h in horses]
    age_vals = [float(h.get("age") or 4.0) for h in horses]

    or_mean = float(np.mean(or_vals))
    w_mean = float(np.mean(w_vals))
    hwr_mean = float(np.mean(hwr_vals))
    age_mean = float(np.mean(age_vals))

    dist_m = float(race_ctx.get("distance_m") or 1600.0)
    is_aw = 1.0 if "Sintética" in str(race_ctx.get("surface", "")) else 0.0
    ncond = float(race_ctx.get("ncond") or 5.0)

    X = np.zeros((n, len(FEAT_COLS)), dtype=np.float64)
    for i, h in enumerate(horses):
        or_v = or_vals[i]
        or_miss = 1.0 if h.get("official_rating") is None else 0.0
        hwr = hwr_vals[i]
        hpr = min(1.0, hwr * 2.5 + 0.15)
        jwr = 0.11
        twr = 0.11
        days_r = h.get("days_rest")
        days_miss = 1.0 if days_r is None else 0.0
        days_log = float(np.log1p(days_r if days_r is not None else 21.0))
        is_deb = 1.0 if h.get("is_debutant") else 0.0
        stall_norm = float(h.get("stall") or (i + 1)) / max(1.0, float(n))

        feat_map = {
            "hist_win_rate": hwr,
            "hist_win_rate_rel": hwr - hwr_mean,
            "hist_place_rate": hpr,
            "jockey_win_rate": jwr,
            "jockey_win_rate_rel": 0.0,
            "trainer_win_rate": twr,
            "trainer_win_rate_rel": 0.0,
            "or_num": or_v,
            "or_num_rel": or_v - or_mean,
            "or_missing": or_miss,
            "weight_kg_rel": w_vals[i] - w_mean,
            "age_num": age_vals[i],
            "age_num_rel": age_vals[i] - age_mean,
            "days_rest_log": days_log,
            "days_rest_missing": days_miss,
            "is_debutant": is_deb,
            "stall_norm": stall_norm,
            "log_runners": float(np.log1p(n)),
            "distance_m": dist_m,
            "ncond_num": ncond,
            "is_aw": is_aw,
        }
        X[i] = [feat_map[col] for col in FEAT_COLS]

    Xn = (X - MEAN) / STD
    logits = Xn @ W
    logits_shift = logits - np.max(logits)
    exp_l = np.exp(np.clip(logits_shift, -30, 30))
    probs = exp_l / np.sum(exp_l)

    winner_idx = int(np.argmax(probs))
    contribs = Xn[winner_idx] * W
    top_factors = sorted(
        [{"feature": f, "contribution": round(float(c), 4)} for f, c in zip(FEAT_COLS, contribs)],
        key=lambda x: abs(x["contribution"]),
        reverse=True,
    )[:6]

    latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)
    return {
        "probabilities": [round(float(p) * 100.0, 2) for p in probs],
        "winner_index": winner_idx,
        "winner_name": horses[winner_idx].get("horseName"),
        "top_factors": top_factors,
        "latency_ms": latency_ms,
        "engine": "FastAPI + Python Softmax Plackett-Luce (Localhost)",
    }


@app.get("/", response_class=HTMLResponse)
async def serve_root():
    """Sirve la interfaz web interactiva del MVP en localhost."""
    with open(MVP_HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()
    return HTMLResponse(
        content=html,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )


@app.get("/health")
async def health_check():
    """Verifica estado de salud del servicio en localhost."""
    return {
        "status": "online",
        "service": "RacePulse AI MVP (Hito 3)",
        "model": "Softmax Plackett-Luce (L2 anti-fuga)",
        "host": "localhost:8000",
    }


@app.get("/api/artifacts")
async def get_artifacts():
    """Retorna metadata del modelo, resultados en Test 2020 y carreras de muestra."""
    return ARTIFACTS


@app.get("/api/races")
async def get_sample_races():
    """Retorna el catálogo de carreras reales de prueba (2020) con sus participantes."""
    return ARTIFACTS.get("sample_races", [])


@app.post("/api/predict")
async def predict_race(req: PredictRequest):
    """Ejecuta inferencia PEAS en tiempo real sobre los caballos dados."""
    res = run_live_plackett_luce_inference(req.horses, req.race_ctx)
    return res


def open_browser():
    time.sleep(1.2)
    try:
        webbrowser.open("http://localhost:8000")
    except Exception:
        pass


def main():
    port = int(os.environ.get("PORT", 8000))
    print("=" * 72)
    print("   🐎 RACEPULSE AI · MVP FUNCIONAL (HITO 3 - PTIA GRUPO 2)")
    print("=" * 72)
    print(f"-> Servidor activo en:        http://localhost:{port}")
    print(f"-> Documentacion Swagger API: http://localhost:{port}/docs")
    print(f"-> Verificacion de Salud:     http://localhost:{port}/health")
    print("=" * 72)
    print("Iniciando navegador automaticamente...")
    print("Presiona Ctrl + C para detener el servidor.")
    print("=" * 72)

    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    main()
