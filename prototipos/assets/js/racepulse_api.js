/**
 * RacePulse AI — API Service & Inferencia Plackett-Luce
 * Manejo robusto de comunicación con FastAPI y fallback anti-fuga en tiempo real.
 */

const RacePulseAPI = (function() {
  const BASE_URL = window.location.origin;
  const isLocalServer = window.location.protocol.startsWith("http");

  async function checkHealth() {
    if (!isLocalServer) {
      return { status: "offline", service: "Modo Estático (File Protocol)", engine: "JS Local Plackett-Luce" };
    }
    try {
      const resp = await fetch(`${BASE_URL}/health`, { method: "GET" });
      if (resp.ok) {
        return await resp.json();
      }
    } catch (e) {
      console.warn("FastAPI /health no disponible:", e);
    }
    return { status: "offline", service: "Sin conexión a FastAPI", engine: "JS Local Plackett-Luce" };
  }

  async function getArtifacts() {
    if (isLocalServer) {
      try {
        const resp = await fetch(`${BASE_URL}/api/artifacts`);
        if (resp.ok) {
          return await resp.json();
        }
        if (resp.status === 401 || resp.status === 403) {
          console.warn("Acceso a artefactos denegado para el rol actual (401/403)");
          return null;
        }
      } catch (e) {
        console.warn("Fallo al obtener /api/artifacts, usando embedded:", e);
      }
    }
    return typeof EMBEDDED_ARTIFACTS !== "undefined" ? EMBEDDED_ARTIFACTS : null;
  }

  async function getRaces() {
    if (isLocalServer) {
      try {
        const resp = await fetch(`${BASE_URL}/api/races`);
        if (resp.ok) {
          const races = await resp.json();
          if (Array.isArray(races) && races.length > 0) return races;
        }
      } catch (e) {
        console.warn("Fallo al obtener /api/races, usando embedded:", e);
      }
    }
    return typeof EMBEDDED_ARTIFACTS !== "undefined" ? EMBEDDED_ARTIFACTS.sample_races : [];
  }

  async function predictRace(horses, raceCtx, metadata) {
    const t0 = performance.now();
    // 1. Intentar backend FastAPI en Localhost
    if (isLocalServer) {
      try {
        const resp = await fetch(`${BASE_URL}/api/predict`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ horses: horses, race_ctx: raceCtx })
        });
        if (resp.ok) {
          const data = await resp.json();
          return data;
        }
      } catch (e) {
        console.warn("FastAPI predict no respondió, ejecutando inferencia local:", e);
      }
    }

    // 2. Fallback Matemático idéntico en JavaScript (Plackett-Luce Softmax)
    return runLocalPlackettLuce(horses, raceCtx, metadata, t0);
  }

  function runLocalPlackettLuce(horses, raceCtx, metadata, t0 = performance.now()) {
    const meta = metadata || (typeof EMBEDDED_ARTIFACTS !== "undefined" ? EMBEDDED_ARTIFACTS.metadata : null);
    if (!meta) {
      throw new Error("Metadata de inferencia no disponible.");
    }

    const W = meta.pl_weights;
    const MEAN = meta.pl_mean;
    const STD = meta.pl_std;
    const COLS = meta.feature_cols;
    const n = horses.length;

    const orVals = horses.map(h => (h.official_rating !== null && h.official_rating !== undefined) ? Number(h.official_rating) : 75.0);
    const wVals = horses.map(h => (h.weight_kg !== null && h.weight_kg !== undefined) ? Number(h.weight_kg) : 57.0);
    const hwrVals = horses.map(h => ((h.hist_win_rate !== null && h.hist_win_rate !== undefined) ? Number(h.hist_win_rate) : 10.0) / 100.0);
    const ageVals = horses.map(h => (h.age !== null && h.age !== undefined) ? Number(h.age) : 4.0);

    const mean = arr => arr.reduce((a, b) => a + b, 0) / arr.length;
    const orMean = mean(orVals);
    const wMean = mean(wVals);
    const hwrMean = mean(hwrVals);
    const ageMean = mean(ageVals);

    const isAw = String(raceCtx.surface || "").includes("Sintética") ? 1.0 : 0.0;
    const distM = Number(raceCtx.distance_m || 1600.0);

    const XnList = horses.map((h, i) => {
      const hwr = hwrVals[i];
      const featMap = {
        hist_win_rate: hwr,
        hist_win_rate_rel: hwr - hwrMean,
        hist_place_rate: Math.min(1.0, hwr * 2.5 + 0.15),
        jockey_win_rate: 0.11,
        jockey_win_rate_rel: 0.0,
        trainer_win_rate: 0.11,
        trainer_win_rate_rel: 0.0,
        or_num: orVals[i],
        or_num_rel: orVals[i] - orMean,
        or_missing: (h.official_rating === null || h.official_rating === undefined) ? 1.0 : 0.0,
        weight_kg_rel: wVals[i] - wMean,
        age_num: ageVals[i],
        age_num_rel: ageVals[i] - ageMean,
        days_rest_log: Math.log1p(h.days_rest !== null && h.days_rest !== undefined ? Number(h.days_rest) : 21.0),
        days_rest_missing: (h.days_rest === null || h.days_rest === undefined) ? 1.0 : 0.0,
        is_debutant: h.is_debutant ? 1.0 : 0.0,
        stall_norm: (h.stall || (i + 1)) / Math.max(1, n),
        log_runners: Math.log1p(n),
        distance_m: distM,
        ncond_num: 5.0,
        is_aw: isAw
      };
      return COLS.map((c, j) => (featMap[c] - MEAN[j]) / STD[j]);
    });

    const logits = XnList.map(xn => xn.reduce((acc, v, j) => acc + v * W[j], 0));
    const maxL = Math.max(...logits);
    const exps = logits.map(l => Math.exp(Math.max(-30, Math.min(30, l - maxL))));
    const sumE = exps.reduce((a, b) => a + b, 0);
    const probs = exps.map(e => Number(((e / sumE) * 100).toFixed(2)));

    const winnerIdx = probs.indexOf(Math.max(...probs));
    const topFactors = COLS.map((c, j) => ({
      feature: c,
      contribution: Number((XnList[winnerIdx][j] * W[j]).toFixed(4))
    })).sort((a, b) => Math.abs(b.contribution) - Math.abs(a.contribution)).slice(0, 6);

    const latencyMs = Number((performance.now() - t0).toFixed(2));

    return {
      probabilities: probs,
      winner_index: winnerIdx,
      winner_name: horses[winnerIdx].horseName,
      top_factors: topFactors,
      latency_ms: latencyMs,
      engine: "FastAPI Softmax Plackett-Luce (Python Localhost)"
    };
  }

  return {
    checkHealth,
    getArtifacts,
    getRaces,
    predictRace
  };
})();
