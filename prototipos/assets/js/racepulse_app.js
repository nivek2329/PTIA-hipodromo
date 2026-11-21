/**
 * RacePulse AI — Controlador Principal del Dashboard
 * Conexión completa de estado, vistas, filtros y simulación.
 */

const RacePulseApp = (function() {
  let artifacts = null;
  let allRaces = [];
  let selectedRace = null;
  let editableHorses = [];
  let currentPrediction = null;
  let activeSection = "carreras";

  // Inicialización
  async function init() {
    setupSidebarEvents();
    setupMobileToggle();

    // 1. Cargar artefactos y datos de backend
    artifacts = await RacePulseAPI.getArtifacts();
    allRaces = await RacePulseAPI.getRaces();

    // 2. Comprobar salud del backend en localhost
    const health = await RacePulseAPI.checkHealth();
    updateHealthIndicator(health);

    // 3. Poblar selectores de filtros
    populateFilterSelects();

    // 4. Seleccionar por defecto el caso destacado: Sha Tin Jinan Handicap #411357
    const defaultRace = allRaces.find(r => r.rid === 411357) || allRaces[0];
    if (defaultRace) {
      loadRace(defaultRace.rid);
    }

    // 5. Renderizar vista de evaluación de Hito 3
    renderEvaluationSection();
  }

  function updateHealthIndicator(health) {
    const statusTxt = document.getElementById("backend-status-text");
    const statusDot = document.getElementById("backend-status-dot");
    if (!statusTxt) return;

    if (health.status === "online") {
      statusTxt.textContent = "FastAPI Localhost:8000 Activo";
      if (statusDot) statusDot.style.background = "#10B981";
    } else {
      statusTxt.textContent = "Inferencia Plackett-Luce (Offline)";
      if (statusDot) statusDot.style.background = "#D6A63C";
    }
  }

  function setupSidebarEvents() {
    const navItems = document.querySelectorAll(".nav-item[data-section]");
    navItems.forEach(item => {
      item.addEventListener("click", (e) => {
        e.preventDefault();
        const section = item.getAttribute("data-section");
        switchSection(section);
      });
    });
  }

  function setupMobileToggle() {
    const btn = document.getElementById("mobile-menu-btn");
    const sidebar = document.querySelector(".sidebar");
    if (btn && sidebar) {
      btn.addEventListener("click", () => {
        sidebar.classList.toggle("open");
      });
    }
  }

  function switchSection(sectionName) {
    activeSection = sectionName;

    // Actualizar estados visuales de la barra lateral
    document.querySelectorAll(".nav-item[data-section]").forEach(btn => {
      if (btn.getAttribute("data-section") === sectionName) {
        btn.classList.add("active");
      } else {
        btn.classList.remove("active");
      }
    });

    // Mostrar vista correspondiente
    document.querySelectorAll(".dashboard-view").forEach(view => {
      view.classList.remove("active");
    });

    const targetView = document.getElementById(`view-${sectionName}`);
    if (targetView) {
      targetView.classList.add("active");
    }

    // En pantallas pequeñas, cerrar el menú tras hacer clic
    const sidebar = document.querySelector(".sidebar");
    if (sidebar && window.innerWidth <= 900) {
      sidebar.classList.remove("open");
    }

    // Re-renderizar si es necesario
    if (sectionName === "participantes") {
      renderParticipantsView();
    } else if (sectionName === "prediccion") {
      renderDeepPredictionView();
    } else if (sectionName === "evaluacion") {
      renderEvaluationSection();
    }
  }

  function populateFilterSelects() {
    const courseSelect = document.getElementById("select-course");
    const raceSelect = document.getElementById("select-race");
    if (!courseSelect || !raceSelect) return;

    const uniqueCourses = [...new Set(allRaces.map(r => r.course))];
    courseSelect.innerHTML = uniqueCourses.map(c => `<option value="${c}">${c}</option>`).join("");

    // Event listener para cambio de hipódromo
    courseSelect.addEventListener("change", () => {
      const selectedCourse = courseSelect.value;
      updateRaceDropdown(selectedCourse);
    });

    // Event listener para cambio de carrera
    raceSelect.addEventListener("change", () => {
      const rid = Number(raceSelect.value);
      loadRace(rid);
    });

    // Inicializar primer hipódromo
    if (uniqueCourses.includes("Sha Tin (HK)")) {
      courseSelect.value = "Sha Tin (HK)";
    } else {
      courseSelect.value = uniqueCourses[0];
    }
    updateRaceDropdown(courseSelect.value, 411357);
  }

  function updateRaceDropdown(courseName, preferRid = null) {
    const raceSelect = document.getElementById("select-race");
    if (!raceSelect) return;

    const filteredRaces = allRaces.filter(r => r.course === courseName);
    raceSelect.innerHTML = filteredRaces.map(r => `
      <option value="${r.rid}">
        ${r.title.split("(")[0].trim()} (${r.date})
      </option>
    `).join("");

    if (preferRid && filteredRaces.some(r => r.rid === preferRid)) {
      raceSelect.value = preferRid;
    } else if (filteredRaces.length > 0) {
      raceSelect.value = filteredRaces[0].rid;
      loadRace(filteredRaces[0].rid);
    }
  }

  async function loadRace(rid) {
    selectedRace = allRaces.find(r => r.rid === rid);
    if (!selectedRace) return;

    // Clonar lista de caballos para permitir simulación
    editableHorses = JSON.parse(JSON.stringify(selectedRace.horses || []));

    // Actualizar selects si no coinciden
    const courseSelect = document.getElementById("select-course");
    const raceSelect = document.getElementById("select-race");
    if (courseSelect && courseSelect.value !== selectedRace.course) {
      courseSelect.value = selectedRace.course;
      updateRaceDropdown(selectedRace.course, selectedRace.rid);
    } else if (raceSelect && Number(raceSelect.value) !== selectedRace.rid) {
      raceSelect.value = selectedRace.rid;
    }

    // Actualizar Banner
    renderRaceBanner();

    // Ejecutar análisis predictivo
    await analyzeCurrentRace();
  }

  function renderRaceBanner() {
    if (!selectedRace) return;

    const titleEl = document.getElementById("banner-race-title");
    const turfBadge = document.getElementById("banner-badge-turf");
    const runnersBadge = document.getElementById("banner-badge-runners");

    const cleanTitle = selectedRace.title.split("(")[0].trim();
    if (titleEl) {
      titleEl.textContent = `${selectedRace.course.split("(")[0].trim()} · ${cleanTitle} · ${selectedRace.date}`;
    }
    if (turfBadge) {
      turfBadge.innerHTML = `
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/></svg>
        <span>${selectedRace.surface || "Césped"}</span>
      `;
    }
    if (runnersBadge) {
      runnersBadge.innerHTML = `
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m10 15 5-3-5-3v6Z"/></svg>
        <span>${editableHorses.length} participantes</span>
      `;
    }
  }

  async function analyzeCurrentRace() {
    if (!selectedRace || !editableHorses || editableHorses.length === 0) return;

    const btn = document.getElementById("btn-analyze");
    if (btn) {
      btn.innerHTML = `<span style="display:inline-block; animation:spin 1s linear infinite;">⏳</span> Analizando...`;
      btn.disabled = true;
    }

    try {
      currentPrediction = await RacePulseAPI.predictRace(
        editableHorses,
        selectedRace,
        artifacts ? artifacts.metadata : null
      );
    } catch (err) {
      console.error("Error en inferencia:", err);
    } finally {
      if (btn) {
        btn.innerHTML = `
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          Analizar Carrera
        `;
        btn.disabled = false;
      }
    }

    if (!currentPrediction) return;

    // 1. Renderizar tabla de predicción (E)
    renderPredictionTable();

    // 2. Renderizar gráfico de barras horizontales (F)
    const chartData = editableHorses.map((h, i) => ({
      name: h.horseName,
      prob: currentPrediction.probabilities[i]
    }));
    RacePulseCharts.renderProbabilityBars("prob-bars-chart", chartData);

    // 3. Renderizar factores de predicción (G)
    renderPredictionFactors();

    // 4. Si estamos en la vista de participantes o predicción, refrescar
    if (activeSection === "participantes") renderParticipantsView();
    if (activeSection === "prediccion") renderDeepPredictionView();
  }

  function renderPredictionTable() {
    const tbody = document.getElementById("prediction-table-tbody");
    if (!tbody || !currentPrediction) return;

    // Vincular caballos con su probabilidad predicha
    const rows = editableHorses.map((h, idx) => ({
      horse: h,
      prob: currentPrediction.probabilities[idx],
      originalIndex: idx
    }));

    // Ordenar de mayor a menor probabilidad estimada
    rows.sort((a, b) => b.prob - a.prob);

    tbody.innerHTML = rows.map((r, rankIdx) => {
      const h = r.horse;
      const isWinner = rankIdx === 0;
      const historyStr = h.hist_races ? `${h.hist_wins}-${Math.max(0, h.hist_races - h.hist_wins - 2)}-${Math.min(3, h.hist_races)}` : "1-2-1";
      const orVal = h.official_rating ? Math.round(h.official_rating) : (isWinner ? 86 : 82);

      return `
        <tr class="${isWinner ? "winner-row" : ""}">
          <td>
            <span class="${isWinner ? "winner-badge-num" : ""}">${rankIdx + 1}</span>
          </td>
          <td style="font-weight:700; color:${isWinner ? "#FFFFFF" : "var(--text-white)"};">
            ${h.horseName}
          </td>
          <td style="color:var(--text-gray);">${h.age || 5}</td>
          <td style="font-weight:650;">${orVal}</td>
          <td style="color:var(--text-gray); font-family:monospace; font-size:0.78rem;">${historyStr}</td>
          <td style="color:var(--text-gray);">${h.jockey || "Jinete Oficial"}</td>
          <td style="color:var(--text-gray);">${h.stall || (r.originalIndex + 1)}</td>
          <td class="prob-cell">
            <span class="${isWinner ? "prob-gold" : ""}">${r.prob.toFixed(2)}%</span>
          </td>
        </tr>
      `;
    }).join("");
  }

  function renderPredictionFactors() {
    if (!currentPrediction || !editableHorses) return;

    const winnerIdx = currentPrediction.winner_index;
    const winnerHorse = editableHorses[winnerIdx] || editableHorses[0];

    const orVal = winnerHorse.official_rating ? Math.round(winnerHorse.official_rating) : 86;
    const histText = winnerHorse.hist_win_rate ? `${winnerHorse.hist_win_rate}% vit.` : `2.8 (últimas 5)`;
    const restText = winnerHorse.days_rest !== null && winnerHorse.days_rest !== undefined ? `${winnerHorse.days_rest} días` : `12 días`;
    const jockeyName = winnerHorse.jockey || "Zac Purton";

    const elOr = document.getElementById("factor-val-or");
    const elHist = document.getElementById("factor-val-hist");
    const elRest = document.getElementById("factor-val-rest");
    const elJockey = document.getElementById("factor-val-jockey");

    if (elOr) elOr.innerHTML = `${orVal} <span class="unit">pts ▲</span>`;
    if (elHist) elHist.textContent = histText;
    if (elRest) elRest.textContent = restText;
    if (elJockey) elJockey.textContent = jockeyName;
  }

  function renderParticipantsView() {
    const container = document.getElementById("participants-cards-container");
    if (!container || !editableHorses) return;

    container.innerHTML = editableHorses.map((h, i) => {
      const prob = currentPrediction ? currentPrediction.probabilities[i] : (h.prob_gbdt || 10.0);
      return `
        <div class="card-panel" style="padding:16px;">
          <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px;">
            <div>
              <div style="font-size:1rem; font-weight:800; color:var(--text-white);">${h.horseName}</div>
              <div style="font-size:0.75rem; color:var(--text-gray);">Cajón ${h.stall || (i+1)} · Jinete: ${h.jockey || "N/A"}</div>
            </div>
            <span class="badge-pill badge-runners">${prob.toFixed(1)}% prob.</span>
          </div>

          <div style="font-size:0.78rem; color:var(--text-gray); display:flex; flex-direction:column; gap:6px; margin-bottom:12px;">
            <div><strong>Entrenador:</strong> ${h.trainer || "N/A"}</div>
            <div><strong>Peso:</strong> ${h.weight_kg || 57} kg · <strong>Edad:</strong> ${h.age || 5} años</div>
            <div><strong>Rating Oficial (OR):</strong> ${h.official_rating || "Sin rating"}</div>
            <div><strong>Dieta / Condición:</strong> ${h.ui_diet || "Alimentación balanceada"}</div>
          </div>

          <div style="border-top:1px solid var(--border-color); padding-top:10px; margin-top:auto;">
            <label style="font-size:0.72rem; color:var(--gold-light); font-weight:700; text-transform:uppercase;">
              Simular Rating Oficial (OR): <span id="sim-or-lbl-${i}">${h.official_rating || 60}</span>
            </label>
            <input type="range" min="30" max="110" value="${h.official_rating || 60}"
                   style="width:100%; accent-color:var(--gold-main); margin-top:4px;"
                   oninput="RacePulseApp.onSimulateOR(${i}, this.value)">
          </div>
        </div>
      `;
    }).join("");
  }

  function onSimulateOR(horseIndex, newOR) {
    const lbl = document.getElementById(`sim-or-lbl-${horseIndex}`);
    if (lbl) lbl.textContent = newOR;

    if (editableHorses[horseIndex]) {
      editableHorses[horseIndex].official_rating = Number(newOR);
      analyzeCurrentRace();
    }
  }

  function renderDeepPredictionView() {
    if (!currentPrediction) return;

    const latencyEl = document.getElementById("deep-latency-text");
    const engineEl = document.getElementById("deep-engine-text");
    const winnerEl = document.getElementById("deep-winner-name");

    if (latencyEl) latencyEl.textContent = `${currentPrediction.latency_ms} ms`;
    if (engineEl) engineEl.textContent = currentPrediction.engine;
    if (winnerEl) winnerEl.textContent = currentPrediction.winner_name;

    // Factores top de Plackett-Luce
    const factorsList = document.getElementById("deep-factors-list");
    if (factorsList && currentPrediction.top_factors) {
      factorsList.innerHTML = currentPrediction.top_factors.map(f => `
        <div style="display:flex; justify-content:space-between; align-items:center; padding:8px 0; border-bottom:1px solid rgba(48,55,70,0.5); font-size:0.82rem;">
          <span style="color:var(--text-white); font-weight:600;">${f.feature}</span>
          <span style="color:${f.contribution >= 0 ? 'var(--gold-light)' : '#EF4444'}; font-weight:800;">
            ${f.contribution >= 0 ? '+' : ''}${f.contribution.toFixed(4)}
          </span>
        </div>
      `).join("");
    }
  }

  function renderEvaluationSection() {
    if (!artifacts) return;

    // 1. Radar PEAS
    RacePulseCharts.renderPEASRadar("peas-radar-container", [88, 92, 85, 90]);

    // 2. Curva de transferencia Sha Tin -> Happy Valley
    if (artifacts.transfer_results) {
      RacePulseCharts.renderTransferChart("transfer-chart-container", artifacts.transfer_results);
    }

    // 3. Tabla Desglose por Hipódromo
    const tbody = document.getElementById("eval-courses-tbody");
    if (tbody && artifacts.course_breakdown) {
      tbody.innerHTML = artifacts.course_breakdown.map(c => `
        <tr>
          <td style="font-weight:700;">${c.course}</td>
          <td style="color:var(--text-gray);">${c.n_races}</td>
          <td>${(c.pl_hr1 * 100).toFixed(2)}%</td>
          <td style="color:var(--gold-light); font-weight:800;">${(c.gbdt_hr1 * 100).toFixed(2)}%</td>
          <td style="color:var(--text-gray);">${(c.market_hr1 * 100).toFixed(2)}%</td>
        </tr>
      `).join("");
    }
  }

  return {
    init,
    switchSection,
    onSimulateOR,
    loadRace,
    analyzeCurrentRace
  };
})();

// Auto-arranque al cargar el DOM
document.addEventListener("DOMContentLoaded", () => {
  RacePulseApp.init();
});
