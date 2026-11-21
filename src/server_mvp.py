"""
Proyecto PTIA - Grupo 2: RacePulse AI (Hito 3 - Servidor MVP Funcional)
Servidor web ligero (sin dependencias externas adicionales) que sirve la interfaz
RacePulse MVP y expone un endpoint REST (/api/predict) para inferencia en tiempo real
con los pesos entrenados del modelo Softmax Plackett-Luce.
"""

import json
import os
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS_PATH = os.path.join(BASE_DIR, "mvp_artifacts_hito3.json")
MVP_HTML_PATH = os.path.join(BASE_DIR, "..", "prototipos", "mvp_hito3.html")

with open(ARTIFACTS_PATH, "r", encoding="utf-8") as f:
    ARTIFACTS = json.load(f)

META = ARTIFACTS["metadata"]
W = np.array(META["pl_weights"], dtype=np.float64)
MEAN = np.array(META["pl_mean"], dtype=np.float64)
STD = np.array(META["pl_std"], dtype=np.float64)
FEAT_COLS = META["feature_cols"]


def run_live_plackett_luce_inference(horses: list, race_ctx: dict) -> dict:
    """Ejecuta inferencia Softmax Plackett-Luce en tiempo real y calcula contribuciones por factor."""
    t0 = time.perf_counter()
    n = len(horses)
    if n == 0:
        return {"error": "No hay caballos en la carrera"}

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
        "engine": "Python Live Plackett-Luce Softmax (Hito 3)",
    }


class RacePulseHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload: dict, status: int = 200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            with open(MVP_HTML_PATH, "r", encoding="utf-8") as f:
                html = f.read().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
        elif parsed.path == "/api/artifacts":
            self._send_json(ARTIFACTS)
        else:
            self._send_json({"error": "Not found"}, status=404)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/predict":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            payload = json.loads(raw.decode("utf-8"))
            res = run_live_plackett_luce_inference(
                payload.get("horses", []),
                payload.get("race_ctx", {}),
            )
            self._send_json(res)
        else:
            self._send_json({"error": "Not found"}, status=404)

    def log_message(self, fmt, *args):
        print(f"[RacePulse MVP] {fmt % args}")


def main():
    port = int(os.environ.get("RACEPULSE_PORT", 8050))
    server = HTTPServer(("127.0.0.1", port), RacePulseHandler)
    url = f"http://127.0.0.1:{port}"
    print("=" * 68)
    print(f"RacePulse AI MVP (Hito 3) corriendo en {url}")
    print("Presiona Ctrl+C para detener el servidor.")
    print("=" * 68)
    try:
        webbrowser.open(url)
    except Exception:
        pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
        server.server_close()


if __name__ == "__main__":
    main()
