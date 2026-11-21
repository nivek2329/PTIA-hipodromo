"""
Proyecto PTIA - Grupo 2: RacePulse AI (Hito 3 - Solución Final y Evaluación)
Pipeline Anti-Fuga de Datos, Entrenamiento Softmax Plackett-Luce / GBDT,
Transferencia de Dominio entre Hipódromos (Sha Tin -> Happy Valley)
y Exportación de Artefactos para el MVP Funcional.
"""

import json
import os
import time
import warnings
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# 1. UTILIDADES DE MÉTRICAS E INTERVALOS DE CONFIANZA
# ---------------------------------------------------------------------------

def wilson_ci(k: int, n: int, z: float = 1.96) -> Tuple[float, float]:
    """Intervalo de confianza de Wilson al 95% para una proporción k/n."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denom
    half = (z * np.sqrt((p * (1.0 - p) + z * z / (4.0 * n)) / n)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def compute_race_metrics(df_eval: pd.DataFrame, prob_col: str) -> Dict[str, float]:
    """
    Calcula métricas por carrera (Hit Rate@1 con IC 95%, Brier Score,
    Log-Loss multiclase, NDCG@3, Tau de Kendall y MRR del ganador).
    """
    probs = df_eval[prob_col].values.astype(np.float64)
    y = df_eval["res_win"].values.astype(np.float64)
    pos = df_eval["pos_clean"].values.astype(np.float64)
    rids = df_eval["rid"].values

    # Agrupar índices por carrera (asumiendo df_eval ordenado o agrupado por rid)
    order = np.argsort(rids, kind="mergesort")
    rids_s = rids[order]
    probs_s = probs[order]
    y_s = y[order]
    pos_s = pos[order]

    _, start_idx = np.unique(rids_s, return_index=True)
    end_idx = np.append(start_idx[1:], len(rids_s))

    n_races = len(start_idx)
    hits = 0
    brier_list = []
    logloss_list = []
    ndcg3_list = []
    mrr_list = []
    tau_list = []

    eps = 1e-12
    for s, e in zip(start_idx, end_idx):
        p_r = probs_s[s:e]
        y_r = y_s[s:e]
        pos_r = pos_s[s:e]
        if len(p_r) < 2 or y_r.sum() != 1:
            continue

        # Normalizar probabilidades por seguridad
        p_sum = p_r.sum()
        p_r = p_r / p_sum if p_sum > 0 else np.ones_like(p_r) / len(p_r)

        # Hit Rate@1
        pred_winner = np.argmax(p_r)
        true_winner = np.argmax(y_r)
        if pred_winner == true_winner:
            hits += 1

        # Brier Score de la carrera (promedio cuadrático por participante)
        brier_list.append(np.mean((p_r - y_r) ** 2))

        # Log-Loss multiclase (NLL del ganador real)
        p_win = np.clip(p_r[true_winner], eps, 1.0)
        logloss_list.append(-np.log(p_win))

        # Ranking predicho (descendente por probabilidad)
        rank_order = np.argsort(-p_r, kind="mergesort")
        win_rank = int(np.where(rank_order == true_winner)[0][0]) + 1
        mrr_list.append(1.0 / win_rank)

        # NDCG@3 (relevancia graduada: 1ro=3, 2do=2, 3ro=1, resto=0)
        rel = np.where(pos_r == 1, 3.0, np.where(pos_r == 2, 2.0, np.where(pos_r == 3, 1.0, 0.0)))
        rel_pred = rel[rank_order[:3]]
        rel_ideal = np.sort(rel)[::-1][:3]
        discounts = 1.0 / np.log2(np.arange(2, 2 + len(rel_pred)))
        dcg = np.sum(rel_pred * discounts)
        idcg = np.sum(rel_ideal * discounts[:len(rel_ideal)])
        ndcg3_list.append(dcg / idcg if idcg > 0 else 0.0)

        # Kendall tau simplificado (concordancia entre -p_r y pos_r)
        n_k = len(p_r)
        if n_k >= 2:
            # Pares concordantes vs discordantes
            c_pairs = 0
            d_pairs = 0
            for i in range(n_k):
                for j in range(i + 1, n_k):
                    if pos_r[i] == pos_r[j]:
                        continue
                    diff_p = p_r[i] - p_r[j]
                    diff_pos = pos_r[j] - pos_r[i]  # mayor prob => menor pos
                    prod = diff_p * diff_pos
                    if prod > 0:
                        c_pairs += 1
                    elif prod < 0:
                        d_pairs += 1
            denom = c_pairs + d_pairs
            if denom > 0:
                tau_list.append((c_pairs - d_pairs) / denom)

    eval_races = len(logloss_list)
    hr = hits / eval_races if eval_races > 0 else 0.0
    ci_low, ci_high = wilson_ci(hits, eval_races)
    return {
        "n_races": int(eval_races),
        "hits": int(hits),
        "hit_rate_1": float(hr),
        "ci_95_low": float(ci_low),
        "ci_95_high": float(ci_high),
        "brier_score": float(np.mean(brier_list)) if brier_list else 0.0,
        "log_loss": float(np.mean(logloss_list)) if logloss_list else 0.0,
        "ndcg_3": float(np.mean(ndcg3_list)) if ndcg3_list else 0.0,
        "mrr": float(np.mean(mrr_list)) if mrr_list else 0.0,
        "kendall_tau": float(np.mean(tau_list)) if tau_list else 0.0,
    }


# ---------------------------------------------------------------------------
# 2. CARGA, LIMPIEZA Y PROTOCOLO ANTI-FUGA DE DATOS (2017 - 2020)
# ---------------------------------------------------------------------------

def infer_surface(course: str, condition: str) -> str:
    c = str(course).upper()
    cond = str(condition).upper()
    if "(AW)" in c or "POLYTRACK" in cond or "TAPETA" in cond or "FIBRESAND" in cond or "STANDARD" in cond:
        return "Sintética (AW)"
    if "DIRT" in cond or "MUDDY" in cond or "SLOPPY" in cond:
        return "Arena"
    return "Césped"


def load_and_prepare_data(data_dir: str, years: List[int] = [2017, 2018, 2019, 2020]) -> pd.DataFrame:
    """Carga carreras y caballos, une por rid, valida ganador único y ordena cronológicamente."""
    races_list = []
    horses_list = []
    cols_keep = [
        "rid", "horseName", "age", "saddle", "decimalPrice", "isFav",
        "trainerName", "jockeyName", "position", "weightSt", "weightLb",
        "OR", "runners", "weight", "res_win", "res_place"
    ]
    for y in years:
        r_path = os.path.join(data_dir, f"races_{y}.csv")
        h_path = os.path.join(data_dir, f"horses_{y}.csv")
        r_df = pd.read_csv(r_path, low_memory=False)
        r_df["year"] = y
        races_list.append(r_df)

        h_df = pd.read_csv(h_path, usecols=lambda c: c in cols_keep or c in [
            "tipo_comida", "calorias_diarias_kcal", "suplemento_nutricional",
            "estado_salud", "puesto_salida"
        ], low_memory=False)
        h_df["year"] = y
        horses_list.append(h_df)

    races = pd.concat(races_list, ignore_index=True)
    horses = pd.concat(horses_list, ignore_index=True)

    # Limpieza de fechas y horas para ordenamiento cronológico estricto
    races["date_clean"] = races["date"].astype(str).str.strip().str[:8]
    races["time_clean"] = races["time"].fillna("00:00").astype(str).str.strip().str[:5]
    races["race_dt"] = pd.to_datetime(
        races["date_clean"] + " " + races["time_clean"],
        format="%y/%m/%d %H:%M",
        errors="coerce"
    )
    # Fallback si alguna fecha tiene otro formato
    mask_nat = races["race_dt"].isna()
    if mask_nat.any():
        races.loc[mask_nat, "race_dt"] = pd.to_datetime(races.loc[mask_nat, "date_clean"], errors="coerce")

    races = races.dropna(subset=["race_dt"]).drop_duplicates(subset=["rid"])

    # Unión por rid
    df = horses.merge(
        races[["rid", "course", "race_dt", "date_clean", "time_clean", "title", "rclass",
               "distance", "condition", "metric", "countryCode", "ncond", "class", "prize"]],
        on="rid",
        how="inner"
    )

    # Control de calidad: asegurar res_win numérico y exactamente 1 ganador oficial por carrera
    df["res_win"] = pd.to_numeric(df["res_win"], errors="coerce").fillna(0.0)
    df["res_place"] = pd.to_numeric(df["res_place"], errors="coerce").fillna(0.0)
    df["pos_clean"] = pd.to_numeric(df["position"], errors="coerce").fillna(99.0)

    race_stats = df.groupby("rid").agg(
        n_runners=("horseName", "count"),
        n_winners=("res_win", "sum")
    )
    valid_rids = race_stats[(race_stats["n_runners"] >= 2) & (race_stats["n_winners"] == 1)].index
    df = df[df["rid"].isin(valid_rids)].copy()

    # Orden cronológico estricto
    df = df.sort_values(["race_dt", "rid", "saddle"], kind="mergesort").reset_index(drop=True)
    return df


def build_anti_leakage_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Componente Principal (Hito 2, Sec. 6.6): Generador de variables precompetencia.
    Calcula estadísticas históricas acumuladas usando ÚNICAMENTE carreras anteriores (shift).
    """
    # Normalizar nombres
    df["horse_id"] = df["horseName"].fillna("UNKNOWN").astype(str).str.strip().str.lower()
    df["jockey_id"] = df["jockeyName"].fillna("UNKNOWN").astype(str).str.strip().str.lower()
    df["trainer_id"] = df["trainerName"].fillna("UNKNOWN").astype(str).str.strip().str.lower()

    # --- Historial del Caballo (estrictamente previo) ---
    g_horse = df.groupby("horse_id", sort=False)
    df["hist_races"] = g_horse.cumcount().astype(np.float32)
    df["hist_wins"] = (g_horse["res_win"].cumsum() - df["res_win"]).astype(np.float32)
    df["hist_places"] = (g_horse["res_place"].cumsum() - df["res_place"]).astype(np.float32)

    # Tasa suavizada bayesiana (prior = 10% victoria, 30% podio)
    df["hist_win_rate"] = ((df["hist_wins"] + 0.1) / (df["hist_races"] + 1.0)).astype(np.float32)
    df["hist_place_rate"] = ((df["hist_places"] + 0.3) / (df["hist_races"] + 1.0)).astype(np.float32)
    df["is_debutant"] = (df["hist_races"] == 0).astype(np.float32)

    # Días de descanso desde última carrera
    prev_dt = g_horse["race_dt"].shift(1)
    days_rest = (df["race_dt"] - prev_dt).dt.total_seconds() / 86400.0
    df["days_rest_raw"] = days_rest.astype(np.float32)
    df["days_rest_missing"] = df["days_rest_raw"].isna().astype(np.float32)

    # --- Historial del Jinete (estrictamente previo) ---
    g_jockey = df.groupby("jockey_id", sort=False)
    j_races = g_jockey.cumcount().astype(np.float32)
    j_wins = (g_jockey["res_win"].cumsum() - df["res_win"]).astype(np.float32)
    df["jockey_win_rate"] = ((j_wins + 0.5) / (j_races + 5.0)).astype(np.float32)

    # --- Historial del Entrenador (estrictamente previo) ---
    g_trainer = df.groupby("trainer_id", sort=False)
    t_races = g_trainer.cumcount().astype(np.float32)
    t_wins = (g_trainer["res_win"].cumsum() - df["res_win"]).astype(np.float32)
    df["trainer_win_rate"] = ((t_wins + 0.5) / (t_races + 5.0)).astype(np.float32)

    # --- Variables de Competencia y Pista (precompetencia) ---
    df["age_num"] = pd.to_numeric(df["age"], errors="coerce")
    df["or_num"] = pd.to_numeric(df["OR"], errors="coerce")
    df["or_missing"] = df["or_num"].isna().astype(np.float32)

    # Peso en kg
    w_kg = pd.to_numeric(df["weight"], errors="coerce")
    w_st = pd.to_numeric(df["weightSt"], errors="coerce").fillna(0)
    w_lb = pd.to_numeric(df["weightLb"], errors="coerce").fillna(0)
    w_calc = w_st * 6.35029 + w_lb * 0.453592
    df["weight_kg"] = np.where(w_kg.notna() & (w_kg > 20), w_kg, np.where(w_calc > 20, w_calc, np.nan))

    # Puesto de salida (cajón) o dorsal
    stall_col = df["puesto_salida"] if "puesto_salida" in df.columns else df["saddle"]
    df["stall_num"] = pd.to_numeric(stall_col, errors="coerce").fillna(pd.to_numeric(df["saddle"], errors="coerce"))
    df["runners_num"] = pd.to_numeric(df["runners"], errors="coerce").fillna(df.groupby("rid")["horseName"].transform("count"))
    df["stall_norm"] = (df["stall_num"] / df["runners_num"].clip(lower=1.0)).clip(0.0, 1.5).fillna(0.5)
    df["log_runners"] = np.log1p(df["runners_num"]).astype(np.float32)

    # Distancia y superficie
    df["distance_m"] = pd.to_numeric(df["metric"], errors="coerce").fillna(1600.0)
    df["ncond_num"] = pd.to_numeric(df["ncond"], errors="coerce").fillna(5.0)
    df["surface"] = [infer_surface(c, cond) for c, cond in zip(df["course"], df["condition"])]
    df["is_aw"] = (df["surface"] == "Sintética (AW)").astype(np.float32)

    # Cuota de mercado (solo para Benchmark Externo, NO entra al modelo puro)
    df["market_prob_raw"] = pd.to_numeric(df["decimalPrice"], errors="coerce").fillna(0.05).clip(0.001, 0.99)
    df["market_prob_norm"] = df["market_prob_raw"] / df.groupby("rid")["market_prob_raw"].transform("sum").clip(lower=1e-6)

    return df


def finalize_imputation_and_relative(df: pd.DataFrame, train_mask: np.ndarray) -> Tuple[pd.DataFrame, List[str]]:
    """Ajusta imputaciones SOLO con Train (anti-fuga) y calcula variables relativas por carrera."""
    train_df = df[train_mask]
    medians = {
        "age_num": float(train_df["age_num"].median()),
        "or_num": float(train_df["or_num"].median()),
        "weight_kg": float(train_df["weight_kg"].median()),
        "days_rest_raw": float(train_df["days_rest_raw"].median()),
    }
    for col, med in medians.items():
        df[col] = df[col].fillna(med).astype(np.float32)

    df["days_rest_log"] = np.log1p(df["days_rest_raw"].clip(0, 730)).astype(np.float32)

    # Diferencias relativas dentro de cada carrera (clave para modelos Plackett-Luce)
    for col in ["or_num", "weight_kg", "hist_win_rate", "jockey_win_rate", "trainer_win_rate", "age_num"]:
        race_mean = df.groupby("rid")[col].transform("mean")
        df[f"{col}_rel"] = (df[col] - race_mean).astype(np.float32)

    feature_cols = [
        "hist_win_rate", "hist_win_rate_rel", "hist_place_rate",
        "jockey_win_rate", "jockey_win_rate_rel",
        "trainer_win_rate", "trainer_win_rate_rel",
        "or_num", "or_num_rel", "or_missing",
        "weight_kg_rel", "age_num", "age_num_rel",
        "days_rest_log", "days_rest_missing", "is_debutant",
        "stall_norm", "log_runners", "distance_m", "ncond_num", "is_aw"
    ]
    return df, feature_cols


# ---------------------------------------------------------------------------
# 3. MODELO PRINCIPAL: SOFTMAX CONDICIONAL POR CARRERA (PLACKETT-LUCE L2)
# ---------------------------------------------------------------------------

class RaceSoftmaxPlackettLuce:
    """
    Modelo de elección discreta condicional por carrera (Plackett-Luce para ganador único).
    Minimiza la log-verosimilitud negativa softmax por carrera + penalización L2.
    Soporta Transferencia de Dominio mediante regularización hacia pesos fuente (prior w_init).
    """
    def __init__(self, l2_reg: float = 1e-3, lr: float = 0.08, epochs: int = 120):
        self.l2_reg = l2_reg
        self.lr = lr
        self.epochs = epochs
        self.w = None
        self.mean = None
        self.std = None

    def _prepare_groups(self, rids: np.ndarray):
        order = np.argsort(rids, kind="mergesort")
        _, start_idx = np.unique(rids[order], return_index=True)
        end_idx = np.append(start_idx[1:], len(rids))
        return order, start_idx, end_idx

    def fit(self, X: np.ndarray, y: np.ndarray, rids: np.ndarray,
            w_prior: np.ndarray = None, prior_reg: float = 0.0,
            mean_ref: np.ndarray = None, std_ref: np.ndarray = None):
        if mean_ref is None:
            self.mean = X.mean(axis=0)
            self.std = X.std(axis=0) + 1e-6
        else:
            self.mean = mean_ref
            self.std = std_ref

        Xn = (X - self.mean) / self.std
        order, start_idx, end_idx = self._prepare_groups(rids)
        Xn_s = Xn[order]
        y_s = y[order]

        n_features = Xn.shape[1]
        if w_prior is not None:
            self.w = w_prior.copy()
        else:
            self.w = np.zeros(n_features, dtype=np.float64)

        # Optimización con Adam sobre gradiente exacto por carrera
        m = np.zeros_like(self.w)
        v = np.zeros_like(self.w)
        beta1, beta2, eps = 0.9, 0.999, 1e-8
        n_races = len(start_idx)

        # Construir mapeo vectorizado por carrera usando add.reduceat
        for epoch in range(1, self.epochs + 1):
            logits = Xn_s @ self.w
            # Estabilidad numérica por carrera: restar máximo de cada carrera
            race_max = np.maximum.reduceat(logits, start_idx)
            logits_shifted = logits - np.repeat(race_max, end_idx - start_idx)
            exp_l = np.exp(np.clip(logits_shifted, -30, 30))
            race_sum = np.add.reduceat(exp_l, start_idx)
            probs = exp_l / np.repeat(race_sum, end_idx - start_idx)

            diff = (probs - y_s)[:, None]
            grad = (Xn_s.T @ diff).ravel() / n_races + self.l2_reg * self.w
            if w_prior is not None and prior_reg > 0:
                grad += prior_reg * (self.w - w_prior)

            m = beta1 * m + (1 - beta1) * grad
            v = beta2 * v + (1 - beta2) * (grad ** 2)
            m_hat = m / (1 - beta1 ** epoch)
            v_hat = v / (1 - beta2 ** epoch)
            self.w -= self.lr * m_hat / (np.sqrt(v_hat) + eps)

        return self

    def predict_proba_race(self, X: np.ndarray, rids: np.ndarray) -> np.ndarray:
        Xn = (X - self.mean) / self.std
        logits = Xn @ self.w
        order = np.argsort(rids, kind="mergesort")
        _, start_idx = np.unique(rids[order], return_index=True)
        end_idx = np.append(start_idx[1:], len(rids))

        logits_s = logits[order]
        race_max = np.maximum.reduceat(logits_s, start_idx)
        exp_l = np.exp(np.clip(logits_s - np.repeat(race_max, end_idx - start_idx), -30, 30))
        race_sum = np.add.reduceat(exp_l, start_idx)
        probs_s = exp_l / np.repeat(race_sum, end_idx - start_idx)

        probs = np.empty_like(probs_s)
        probs[order] = probs_s
        return probs


def per_race_softmax_from_scores(scores: np.ndarray, rids: np.ndarray, temp: float = 1.0) -> np.ndarray:
    order = np.argsort(rids, kind="mergesort")
    _, start_idx = np.unique(rids[order], return_index=True)
    end_idx = np.append(start_idx[1:], len(rids))
    s_ord = scores[order] / temp
    r_max = np.maximum.reduceat(s_ord, start_idx)
    exp_s = np.exp(np.clip(s_ord - np.repeat(r_max, end_idx - start_idx), -30, 30))
    r_sum = np.add.reduceat(exp_s, start_idx)
    probs_ord = exp_s / np.repeat(r_sum, end_idx - start_idx)
    probs = np.empty_like(probs_ord)
    probs[order] = probs_ord
    return probs


# ---------------------------------------------------------------------------
# 4. PIPELINE PRINCIPAL HITO 3
# ---------------------------------------------------------------------------

def main():
    t0 = time.time()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "..", "data")

    print("=" * 74)
    print("RACEPULSE AI · PIPELINE FINAL HITO 3 (ANTI-FUGA + TRANSFERENCIA + MVP)")
    print("=" * 74)

    df = load_and_prepare_data(data_dir, [2017, 2018, 2019, 2020])
    print(f"[1] Datos cargados y validados (2017-2020): {len(df):,} participaciones en {df['rid'].nunique():,} carreras.")

    df = build_anti_leakage_features(df)

    # Partición cronológica estricta (Hito 2, Sec. 6.7)
    train_mask = df["year"].isin([2017, 2018]).values
    val_mask = (df["year"] == 2019).values
    test_mask = (df["year"] == 2020).values

    df, feature_cols = finalize_imputation_and_relative(df, train_mask)
    print(f"[2] Partición temporal:")
    print(f"    - Train (2017-2018): {df[train_mask]['rid'].nunique():,} carreras ({train_mask.sum():,} filas)")
    print(f"    - Valid (2019):      {df[val_mask]['rid'].nunique():,} carreras ({val_mask.sum():,} filas)")
    print(f"    - Test  (2020):      {df[test_mask]['rid'].nunique():,} carreras ({test_mask.sum():,} filas)")

    X_train = df.loc[train_mask, feature_cols].values.astype(np.float64)
    y_train = df.loc[train_mask, "res_win"].values.astype(np.float64)
    rid_train = df.loc[train_mask, "rid"].values

    X_val = df.loc[val_mask, feature_cols].values.astype(np.float64)
    y_val = df.loc[val_mask, "res_win"].values.astype(np.float64)
    rid_val = df.loc[val_mask, "rid"].values

    X_test = df.loc[test_mask, feature_cols].values.astype(np.float64)
    rid_test = df.loc[test_mask, "rid"].values

    df_val = df.loc[val_mask].copy()
    df_test = df.loc[test_mask].copy()

    # --- A. Baseline Uniforme ---
    df_test["prob_uniform"] = 1.0 / df_test["runners_num"].clip(lower=1.0)

    # --- B. Baseline Regresión Logística Binaria (estilo Hito 2) ---
    # Entrenamiento binario independiente (sin normalización softmax durante entrenamiento)
    mean_tr = X_train.mean(axis=0)
    std_tr = X_train.std(axis=0) + 1e-6
    Xn_tr = np.hstack([np.ones((len(X_train), 1)), (X_train - mean_tr) / std_tr])
    Xn_te = np.hstack([np.ones((len(X_test), 1)), (X_test - mean_tr) / std_tr])
    w_bin = np.zeros(Xn_tr.shape[1])
    for _ in range(150):
        z = np.clip(Xn_tr @ w_bin, -25, 25)
        p_bin = 1.0 / (1.0 + np.exp(-z))
        grad = (Xn_tr.T @ (p_bin - y_train)) / len(y_train) + 1e-3 * w_bin
        w_bin -= 0.1 * grad
    raw_bin_te = 1.0 / (1.0 + np.exp(-np.clip(Xn_te @ w_bin, -25, 25)))
    df_test["prob_logreg_hito2"] = raw_bin_te / df_test.groupby("rid")["runners_num"].transform(
        lambda s: 1.0  # placeholder replaced below
    )
    # Normalizar por carrera para evaluación probabilística justa
    df_test["prob_logreg_hito2"] = raw_bin_te
    df_test["prob_logreg_hito2"] = df_test["prob_logreg_hito2"] / df_test.groupby("rid")["prob_logreg_hito2"].transform("sum")

    # --- C. Modelo Principal: Softmax Plackett-Luce (Tuning L2 en Validación 2019) ---
    best_l2, best_val_ll, best_pl_model = 1e-3, 999.0, None
    for l2 in [1e-4, 1e-3, 1e-2, 5e-2]:
        m_pl = RaceSoftmaxPlackettLuce(l2_reg=l2, lr=0.08, epochs=120)
        m_pl.fit(X_train, y_train, rid_train)
        df_val["prob_tmp"] = m_pl.predict_proba_race(X_val, rid_val)
        val_m = compute_race_metrics(df_val, "prob_tmp")
        if val_m["log_loss"] < best_val_ll:
            best_val_ll = val_m["log_loss"]
            best_l2 = l2
            best_pl_model = m_pl

    print(f"[3] Mejor L2 en Validación 2019 (Plackett-Luce): lambda={best_l2} | Val Log-Loss={best_val_ll:.4f}")
    df_test["prob_plackett_luce"] = best_pl_model.predict_proba_race(X_test, rid_test)

    # --- D. Modelo Avanzado: HistGradientBoosting + Calibración Softmax por Carrera ---
    gbdt = HistGradientBoostingClassifier(
        max_iter=150, max_depth=5, learning_rate=0.06, l2_regularization=1.0, random_state=42
    )
    gbdt.fit(X_train, y_train)
    val_scores_gbdt = gbdt.decision_function(X_val)
    best_temp, best_gbdt_ll = 1.0, 999.0
    for temp in [0.7, 0.85, 1.0, 1.15, 1.3]:
        df_val["prob_tmp"] = per_race_softmax_from_scores(val_scores_gbdt, rid_val, temp=temp)
        val_m = compute_race_metrics(df_val, "prob_tmp")
        if val_m["log_loss"] < best_gbdt_ll:
            best_gbdt_ll = val_m["log_loss"]
            best_temp = temp

    print(f"[4] Mejor Temperatura en Validación 2019 (GBDT+Softmax): T={best_temp} | Val Log-Loss={best_gbdt_ll:.4f}")
    test_scores_gbdt = gbdt.decision_function(X_test)
    df_test["prob_gbdt_softmax"] = per_race_softmax_from_scores(test_scores_gbdt, rid_test, temp=best_temp)

    # --- E. Evaluación Global en Test 2020 ---
    models_eval = {
        "Azar / Uniforme": "prob_uniform",
        "Baseline LogReg (Hito 2)": "prob_logreg_hito2",
        "RacePulse Plackett-Luce (L2)": "prob_plackett_luce",
        "RacePulse GBDT + Softmax": "prob_gbdt_softmax",
        "Benchmark Mercado (Favorito)": "market_prob_norm",
    }

    print("\n[5] RESULTADOS EN CONJUNTO DE PRUEBA (TEST 2020):")
    global_results = {}
    for name, col in models_eval.items():
        res = compute_race_metrics(df_test, col)
        global_results[name] = res
        print(
            f"  • {name:30s} | HR@1={res['hit_rate_1']*100:5.2f}% "
            f"[{res['ci_95_low']*100:5.2f}%, {res['ci_95_high']*100:5.2f}%] | "
            f"LogLoss={res['log_loss']:.4f} | Brier={res['brier_score']:.4f} | "
            f"NDCG@3={res['ndcg_3']:.4f} | MRR={res['mrr']:.4f} | Tau={res['kendall_tau']:.4f}"
        )

    # Desglose por Hipódromos Representativos
    print("\n[6] DESGLOSE POR HIPÓDROMO (TEST 2020 - RacePulse Plackett-Luce vs Mercado):")
    top_courses = ["Sha Tin (HK)", "Happy Valley (HK)", "Gulfstream Park (USA)", "Wolverhampton (AW)", "Kempton (AW)"]
    course_breakdown = []
    for c in top_courses:
        sub = df_test[df_test["course"] == c]
        if len(sub) == 0:
            continue
        m_pl_c = compute_race_metrics(sub, "prob_plackett_luce")
        m_gb_c = compute_race_metrics(sub, "prob_gbdt_softmax")
        m_mk_c = compute_race_metrics(sub, "market_prob_norm")
        course_breakdown.append({
            "course": c,
            "n_races": m_pl_c["n_races"],
            "pl_hr1": m_pl_c["hit_rate_1"],
            "pl_logloss": m_pl_c["log_loss"],
            "gbdt_hr1": m_gb_c["hit_rate_1"],
            "gbdt_logloss": m_gb_c["log_loss"],
            "market_hr1": m_mk_c["hit_rate_1"],
            "market_logloss": m_mk_c["log_loss"],
        })
        print(
            f"  • {c:22s} (n={m_pl_c['n_races']:3d}): "
            f"PL HR@1={m_pl_c['hit_rate_1']*100:5.2f}% (LL={m_pl_c['log_loss']:.3f}) | "
            f"GBDT HR@1={m_gb_c['hit_rate_1']*100:5.2f}% (LL={m_gb_c['log_loss']:.3f}) | "
            f"Mercado HR@1={m_mk_c['hit_rate_1']*100:5.2f}%"
        )

    # --- F. Experimento de Transferencia de Dominio: Sha Tin (HK) -> Happy Valley (HK) ---
    print("\n[7] EXPERIMENTO DE TRANSFERENCIA DE DOMINIO (Sha Tin -> Happy Valley):")
    st_train = df[df["year"].isin([2017, 2018, 2019]) & (df["course"] == "Sha Tin (HK)")]
    hv_train_all = df[df["year"].isin([2017, 2018, 2019]) & (df["course"] == "Happy Valley (HK)")]
    hv_test = df_test[df_test["course"] == "Happy Valley (HK)"].copy()

    m_source = RaceSoftmaxPlackettLuce(l2_reg=1e-2, lr=0.08, epochs=140)
    m_source.fit(
        st_train[feature_cols].values.astype(np.float64),
        st_train["res_win"].values.astype(np.float64),
        st_train["rid"].values
    )

    hv_rids = hv_train_all["rid"].unique()
    X_hv_te = hv_test[feature_cols].values.astype(np.float64)
    rid_hv_te = hv_test["rid"].values

    transfer_results = []
    # 0% local (Zero-shot)
    hv_test["prob_tmp"] = m_source.predict_proba_race(X_hv_te, rid_hv_te)
    z_m = compute_race_metrics(hv_test, "prob_tmp")
    transfer_results.append({
        "fraction": 0.0, "n_local_races": 0,
        "transfer_hr1": z_m["hit_rate_1"], "transfer_logloss": z_m["log_loss"],
        "local_hr1": None, "local_logloss": None
    })
    print(f"  • 0% local (Zero-shot Sha Tin -> HV): Transfer HR@1={z_m['hit_rate_1']*100:5.2f}% | LL={z_m['log_loss']:.4f}")

    for frac in [0.10, 0.25, 0.50, 0.75, 1.0]:
        k_rids = int(len(hv_rids) * frac)
        # Últimas k_rids carreras cronológicas de entrenamiento en Happy Valley
        sub_rids = hv_rids[-k_rids:]
        sub_hv = hv_train_all[hv_train_all["rid"].isin(sub_rids)]
        X_sub = sub_hv[feature_cols].values.astype(np.float64)
        y_sub = sub_hv["res_win"].values.astype(np.float64)
        rid_sub = sub_hv["rid"].values

        # Modelo Solo Local
        m_local = RaceSoftmaxPlackettLuce(l2_reg=2e-2, lr=0.08, epochs=120)
        m_local.fit(X_sub, y_sub, rid_sub)
        hv_test["prob_tmp"] = m_local.predict_proba_race(X_hv_te, rid_hv_te)
        loc_m = compute_race_metrics(hv_test, "prob_tmp")

        # Modelo Transferido + Fine-Tuning (regularizado hacia w_source)
        m_trans = RaceSoftmaxPlackettLuce(l2_reg=5e-3, lr=0.05, epochs=80)
        m_trans.fit(
            X_sub, y_sub, rid_sub,
            w_prior=m_source.w, prior_reg=0.15,
            mean_ref=m_source.mean, std_ref=m_source.std
        )
        hv_test["prob_tmp"] = m_trans.predict_proba_race(X_hv_te, rid_hv_te)
        tr_m = compute_race_metrics(hv_test, "prob_tmp")

        transfer_results.append({
            "fraction": frac, "n_local_races": int(k_rids),
            "transfer_hr1": tr_m["hit_rate_1"], "transfer_logloss": tr_m["log_loss"],
            "local_hr1": loc_m["hit_rate_1"], "local_logloss": loc_m["log_loss"]
        })
        print(
            f"  • {int(frac*100):3d}% local ({k_rids:3d} carreras): "
            f"Transfer+FT HR@1={tr_m['hit_rate_1']*100:5.2f}% (LL={tr_m['log_loss']:.4f}) vs "
            f"Solo Local HR@1={loc_m['hit_rate_1']*100:5.2f}% (LL={loc_m['log_loss']:.4f})"
        )

    # --- G. Explicabilidad: Pesos del Modelo Plackett-Luce ---
    feature_weights = [
        {"feature": f, "weight": float(w)}
        for f, w in sorted(zip(feature_cols, best_pl_model.w), key=lambda x: abs(x[1]), reverse=True)
    ]
    print("\n[8] TOP 8 FACTORES MÁS INFLUYENTES (Plackett-Luce):")
    for fw in feature_weights[:8]:
        print(f"  • {fw['feature']:24s}: {fw['weight']:+.4f}")

    # --- H. Exportar Casos de Prueba Reales y Muestra de Carreras para el MVP ---
    # Seleccionar 12 carreras reales de Test 2020 (incluyendo Sha Tin, Happy Valley, Cheltenham, Wolverhampton, Fakenham)
    sample_courses = ["Sha Tin (HK)", "Happy Valley (HK)", "Cheltenham", "Wolverhampton (AW)", "Fakenham", "Gulfstream Park (USA)"]
    sample_rids = []
    for c in sample_courses:
        c_rids = df_test[df_test["course"] == c]["rid"].unique()
        if len(c_rids) > 0:
            # Tomar carreras donde el modelo acertó y también donde falló para análisis real
            sample_rids.extend(c_rids[:2].tolist())

    # Encontrar los 2 mejores aciertos (mayor probabilidad asignada al ganador real) y 2 errores relevantes
    race_summaries = []
    for rid, grp in df_test.groupby("rid"):
        if len(grp) < 4:
            continue
        p_col = "prob_gbdt_softmax"
        pred_idx = grp[p_col].idxmax()
        win_idx = grp["res_win"].idxmax()
        race_summaries.append({
            "rid": int(rid),
            "course": grp.iloc[0]["course"],
            "date": grp.iloc[0]["date_clean"],
            "title": str(grp.iloc[0]["title"]),
            "runners": int(len(grp)),
            "pred_horse": grp.loc[pred_idx, "horseName"],
            "pred_prob": float(grp.loc[pred_idx, p_col]),
            "true_winner": grp.loc[win_idx, "horseName"],
            "true_winner_prob": float(grp.loc[win_idx, p_col]),
            "market_fav": grp.loc[grp["market_prob_norm"].idxmax(), "horseName"],
            "hit": bool(pred_idx == win_idx),
            "beat_market": bool((pred_idx == win_idx) and (grp["market_prob_norm"].idxmax() != win_idx)),
        })

    rs_df = pd.DataFrame(race_summaries)
    best_hits = rs_df[rs_df["hit"]].sort_values("pred_prob", ascending=False).head(3)
    beat_market_hits = rs_df[rs_df["beat_market"] & rs_df["course"].isin(["Sha Tin (HK)", "Happy Valley (HK)"])].sort_values("pred_prob", ascending=False).head(2)
    notable_errors = rs_df[~rs_df["hit"]].sort_values("pred_prob", ascending=False).head(3)

    # Asegurar que esos rids estén en sample_rids para poder inspeccionarlos en el MVP
    for rid_val in pd.concat([best_hits, beat_market_hits, notable_errors])["rid"].tolist():
        if rid_val not in sample_rids:
            sample_rids.append(rid_val)

    # Construir JSON de carreras reales para el MVP
    mvp_races = []
    for rid in sample_rids:
        grp = df_test[df_test["rid"] == rid].copy()
        if len(grp) == 0:
            continue
        first = grp.iloc[0]
        horses_json = []
        for _, row in grp.iterrows():
            horses_json.append({
                "horseName": str(row["horseName"]),
                "saddle": int(row["saddle"]) if pd.notna(row["saddle"]) else 0,
                "stall": int(row["stall_num"]) if pd.notna(row["stall_num"]) else 0,
                "age": int(row["age_num"]),
                "jockey": str(row["jockeyName"]) if pd.notna(row["jockeyName"]) else "No registrado",
                "trainer": str(row["trainerName"]) if pd.notna(row["trainerName"]) else "No registrado",
                "weight_kg": round(float(row["weight_kg"]), 1),
                "official_rating": None if row["or_missing"] > 0.5 else round(float(row["or_num"]), 1),
                "hist_races": int(row["hist_races"]),
                "hist_wins": int(row["hist_wins"]),
                "hist_win_rate": round(float(row["hist_win_rate"]) * 100, 1),
                "days_rest": None if row["days_rest_missing"] > 0.5 else int(round(float(row["days_rest_raw"]))),
                "is_debutant": bool(row["is_debutant"] > 0.5),
                "prob_pl": round(float(row["prob_plackett_luce"]) * 100, 2),
                "prob_gbdt": round(float(row["prob_gbdt_softmax"]) * 100, 2),
                "prob_market": round(float(row["market_prob_norm"]) * 100, 2),
                "res_win": int(row["res_win"]),
                "pos_real": int(row["pos_clean"]),
                # Variables simuladas solo UI (aisladas del modelo, según Hito 2 Sec. 5.2)
                "ui_diet": str(row["tipo_comida"]) if "tipo_comida" in row and pd.notna(row["tipo_comida"]) else "Forraje balanceado (Simulado UI)",
                "ui_kcal": int(row["calorias_diarias_kcal"]) if "calorias_diarias_kcal" in row and pd.notna(row["calorias_diarias_kcal"]) else 31500,
                "ui_health": str(row["estado_salud"]) if "estado_salud" in row and pd.notna(row["estado_salud"]) else "Óptimo (Simulado UI)",
            })
        mvp_races.append({
            "rid": int(rid),
            "course": str(first["course"]),
            "date": str(first["date_clean"]),
            "time": str(first["time_clean"]),
            "title": str(first["title"]),
            "surface": str(first["surface"]),
            "condition": str(first["condition"]) if pd.notna(first["condition"]) else "N/A",
            "distance_m": int(first["distance_m"]),
            "runners": int(len(grp)),
            "rclass": str(first["rclass"]) if pd.notna(first["rclass"]) else "General",
            "horses": horses_json,
        })

    artifact = {
        "metadata": {
            "train_years": [2017, 2018],
            "val_years": [2019],
            "test_years": [2020],
            "n_train_races": int(df[train_mask]["rid"].nunique()),
            "n_val_races": int(df[val_mask]["rid"].nunique()),
            "n_test_races": int(df[test_mask]["rid"].nunique()),
            "best_l2": best_l2,
            "best_gbdt_temp": best_temp,
            "feature_cols": feature_cols,
            "pl_weights": best_pl_model.w.tolist(),
            "pl_mean": best_pl_model.mean.tolist(),
            "pl_std": best_pl_model.std.tolist(),
        },
        "global_results": global_results,
        "course_breakdown": course_breakdown,
        "transfer_results": transfer_results,
        "feature_weights": feature_weights,
        "test_cases": {
            "best_hits": best_hits.to_dict("records"),
            "beat_market_hk": beat_market_hits.to_dict("records"),
            "notable_errors": notable_errors.to_dict("records"),
        },
        "sample_races": mvp_races,
    }

    out_json = os.path.join(base_dir, "mvp_artifacts_hito3.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(artifact, f, ensure_ascii=False, indent=2)

    print(f"\n[9] Artefactos exportados en {out_json} ({os.path.getsize(out_json)/1024:.1f} KB)")
    print(f"Tiempo total de ejecución: {time.time() - t0:.1f}s")
    print("=" * 74)


if __name__ == "__main__":
    main()
