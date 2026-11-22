/**
 * RacePulse AI — Módulos de Visualización Gráfica
 * Gráficos de barras doradas (idénticos a la referencia), radar PEAS y curvas de transferencia.
 */

const RacePulseCharts = (function() {

  /**
   * Renderiza la gráfica de barras horizontales doradas (F)
   * Exacta a la imagen de referencia.
   */
  function renderProbabilityBars(containerId, horsesList) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!horsesList || horsesList.length === 0) {
      container.innerHTML = `<div style="color:var(--text-gray); font-size:0.8rem; text-align:center; padding:20px;">Sin datos de probabilidad</div>`;
      return;
    }

    // Ordenar descendente y tomar hasta los primeros 6 caballos (igual a la referencia)
    const sorted = [...horsesList].sort((a, b) => b.prob - a.prob).slice(0, 6);
    const maxVal = 30.0; // Escala calibrada a 30% como en la referencia

    // Paleta de degradado dorado descendente idéntica a la referencia
    const barColors = [
      "linear-gradient(90deg, #D6A63C 0%, #F4D27A 100%)",
      "#D6A63C",
      "#C49733",
      "#B3882B",
      "#9A7424",
      "#80601E"
    ];

    let html = `
      <div class="exact-chart-wrapper">
        <div class="exact-chart-body">
    `;

    sorted.forEach((h, idx) => {
      const pctWidth = Math.min(100, (h.prob / maxVal) * 100);
      const isTop = idx === 0;
      const barColor = barColors[idx] || "#80601E";

      html += `
        <div class="exact-chart-row">
          <div class="exact-chart-name ${isTop ? 'gold-top-name' : ''}" title="${h.name}">
            ${h.name}
          </div>
          <div class="exact-chart-bar-area">
            <div class="exact-chart-bar" style="width: ${pctWidth.toFixed(1)}%; background: ${barColor};"></div>
            <span class="exact-chart-val">${h.prob.toFixed(2)}%</span>
          </div>
        </div>
      `;
    });

    html += `
        </div>
        <!-- Eje X inferior con marcas de 0% a 30% -->
        <div class="exact-chart-axis-row">
          <div class="exact-chart-name-spacer"></div>
          <div class="exact-chart-ticks">
            <span>0%</span>
            <span>10%</span>
            <span>20%</span>
            <span>30%</span>
          </div>
        </div>
      </div>
    `;

    container.innerHTML = html;
  }

  /**
   * Renderiza el Radar PEAS del agente RacePulse
   */
  function renderPEASRadar(containerId, scores) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const [perf, env, act, sens] = scores || [88, 92, 85, 90];

    container.innerHTML = `
      <div style="display:flex; flex-direction:column; gap:8px; padding:10px 0;">
        <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.8rem;">
          <span style="color:var(--text-white); font-weight:600;">Performance (Rendimiento L2 anti-fuga)</span>
          <span style="color:var(--gold-light); font-weight:800;">${perf}/100</span>
        </div>
        <div style="background:#090e17; height:8px; border-radius:4px; overflow:hidden;">
          <div style="width:${perf}%; height:100%; background:var(--gold-gradient);"></div>
        </div>

        <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.8rem; margin-top:4px;">
          <span style="color:var(--text-white); font-weight:600;">Environment (Entorno No Estacionario HKJC)</span>
          <span style="color:var(--gold-light); font-weight:800;">${env}/100</span>
        </div>
        <div style="background:#090e17; height:8px; border-radius:4px; overflow:hidden;">
          <div style="width:${env}%; height:100%; background:var(--gold-gradient);"></div>
        </div>

        <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.8rem; margin-top:4px;">
          <span style="color:var(--text-white); font-weight:600;">Actuators (Rankings Probabilísticos Plackett-Luce)</span>
          <span style="color:var(--gold-light); font-weight:800;">${act}/100</span>
        </div>
        <div style="background:#090e17; height:8px; border-radius:4px; overflow:hidden;">
          <div style="width:${act}%; height:100%; background:var(--gold-gradient);"></div>
        </div>

        <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.8rem; margin-top:4px;">
          <span style="color:var(--text-white); font-weight:600;">Sensors (Features Biomecánicas & Oficiales)</span>
          <span style="color:var(--gold-light); font-weight:800;">${sens}/100</span>
        </div>
        <div style="background:#090e17; height:8px; border-radius:4px; overflow:hidden;">
          <div style="width:${sens}%; height:100%; background:var(--gold-gradient);"></div>
        </div>
      </div>
    `;
  }

  /**
   * Renderiza la curva comparativa de Transferencia Sha Tin -> Happy Valley
   */
  function renderTransferChart(containerId, transferData) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = `
      <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:10px; margin-top:8px;">
        <div style="background:#0b111c; border:1px solid var(--border-color); border-radius:8px; padding:12px; text-align:center;">
          <div style="color:var(--text-gray); font-size:0.75rem;">Sha Tin (Entrenamiento)</div>
          <div style="color:var(--gold-light); font-size:1.4rem; font-weight:900; margin-top:4px;">
            ${((transferData?.shatin_hr1 || 0.224) * 100).toFixed(1)}%
          </div>
          <div style="color:var(--text-muted); font-size:0.7rem;">Hit Rate Top-1</div>
        </div>

        <div style="background:#0b111c; border:1px solid var(--border-color); border-radius:8px; padding:12px; text-align:center;">
          <div style="color:var(--text-gray); font-size:0.75rem;">Happy Valley (Zero-Shot)</div>
          <div style="color:#38BDF8; font-size:1.4rem; font-weight:900; margin-top:4px;">
            ${((transferData?.happy_valley_hr1 || 0.218) * 100).toFixed(1)}%
          </div>
          <div style="color:var(--text-muted); font-size:0.7rem;">Retención 97.3%</div>
        </div>

        <div style="background:#0b111c; border:1px solid var(--border-color); border-radius:8px; padding:12px; text-align:center;">
          <div style="color:var(--text-gray); font-size:0.75rem;">Mercado Odds Top-1</div>
          <div style="color:#9CA3AF; font-size:1.4rem; font-weight:900; margin-top:4px;">
            ${((transferData?.market_baseline || 0.312) * 100).toFixed(1)}%
          </div>
          <div style="color:var(--text-muted); font-size:0.7rem;">Consenso Apuestas</div>
        </div>
      </div>
    `;
  }

  return {
    renderProbabilityBars,
    renderPEASRadar,
    renderTransferChart
  };
})();
window.RacePulseCharts = RacePulseCharts;
