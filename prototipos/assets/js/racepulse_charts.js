/**
 * RacePulse AI — Módulos de Visualización Gráfica
 * Gráficos de barras doradas, radar PEAS y curvas de transferencia.
 */

const RacePulseCharts = (function() {

  /**
   * Renderiza la gráfica de barras horizontales doradas (F)
   */
  function renderProbabilityBars(containerId, horsesList) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!horsesList || horsesList.length === 0) {
      container.innerHTML = `<div style="color:var(--text-gray); font-size:0.8rem; text-align:center; padding:20px;">Sin datos de probabilidad</div>`;
      return;
    }

    // Ordenar descendente y tomar hasta los primeros 6-8 caballos
    const sorted = [...horsesList].sort((a, b) => b.prob - a.prob).slice(0, 7);
    const maxVal = Math.max(...sorted.map(h => h.prob), 30); // Eje escala a al menos 30%

    let html = `<div class="prob-chart-container">`;

    sorted.forEach((h, idx) => {
      const pctWidth = Math.min(100, (h.prob / maxVal) * 100);
      html += `
        <div class="prob-chart-row">
          <span class="prob-horse-name" title="${h.name}">${h.name}</span>
          <div class="prob-bar-track">
            <div class="prob-bar-fill" style="width: ${pctWidth.toFixed(1)}%;"></div>
          </div>
          <span class="prob-val-text">${h.prob.toFixed(2)}%</span>
        </div>
      `;
    });

    // Eje X inferior
    html += `
      <div class="prob-x-axis">
        <span>0%</span>
        <span>5%</span>
        <span>10%</span>
        <span>15%</span>
        <span>20%</span>
        <span>25%</span>
        <span>30%</span>
      </div>
    </div>`;

    container.innerHTML = html;
  }

  /**
   * Renderiza el Radar PEAS en SVG para la sección de Evaluación
   */
  function renderPEASRadar(containerId, scores = [88, 92, 85, 90]) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const size = 260;
    const center = size / 2;
    const radius = 95;
    const labels = ["Performance", "Environment", "Actuators", "Sensors"];

    // Coordenadas de los 4 ejes
    const angles = [ -Math.PI / 2, 0, Math.PI / 2, Math.PI ];
    
    // Polígonos de referencia (25%, 50%, 75%, 100%)
    let gridSvg = "";
    [0.25, 0.5, 0.75, 1.0].forEach(level => {
      const pts = angles.map(a => {
        const r = radius * level;
        return `${(center + r * Math.cos(a)).toFixed(1)},${(center + r * Math.sin(a)).toFixed(1)}`;
      }).join(" ");
      gridSvg += `<polygon points="${pts}" fill="none" stroke="#303746" stroke-width="1" stroke-dasharray="${level < 1 ? '3 3' : 'none'}"/>`;
    });

    // Ejes radiales
    angles.forEach((a, i) => {
      const x2 = center + radius * Math.cos(a);
      const y2 = center + radius * Math.sin(a);
      gridSvg += `<line x1="${center}" y1="${center}" x2="${x2}" y2="${y2}" stroke="#303746" stroke-width="1.2"/>`;
    });

    // Polígono de datos del agente
    const dataPts = angles.map((a, i) => {
      const r = radius * (scores[i] / 100);
      return `${(center + r * Math.cos(a)).toFixed(1)},${(center + r * Math.sin(a)).toFixed(1)}`;
    }).join(" ");

    // Etiquetas
    let labelsSvg = "";
    const labelOffsets = [
      { x: center, y: 16, anchor: "middle" },
      { x: size - 10, y: center + 4, anchor: "end" },
      { x: center, y: size - 10, anchor: "middle" },
      { x: 10, y: center + 4, anchor: "start" }
    ];

    labels.forEach((lbl, i) => {
      const pos = labelOffsets[i];
      labelsSvg += `<text x="${pos.x}" y="${pos.y}" fill="#A7AFBD" font-size="10.5" font-weight="700" text-anchor="${pos.anchor}">${lbl}</text>`;
    });

    container.innerHTML = `
      <svg viewBox="0 0 ${size} ${size}" style="width:100%; max-width:280px; height:auto; display:block; margin:0 auto;">
        ${gridSvg}
        <polygon points="${dataPts}" fill="rgba(214, 166, 60, 0.22)" stroke="#D6A63C" stroke-width="2.4"/>
        ${angles.map((a, i) => {
          const r = radius * (scores[i] / 100);
          const cx = (center + r * Math.cos(a)).toFixed(1);
          const cy = (center + r * Math.sin(a)).toFixed(1);
          return `<circle cx="${cx}" cy="${cy}" r="4" fill="#F4D27A" stroke="#080B10" stroke-width="1.5"/>`;
        }).join("")}
        ${labelsSvg}
      </svg>
    `;
  }

  /**
   * Renderiza la curva de transferencia Sha Tin -> Happy Valley en SVG
   */
  function renderTransferChart(containerId, transferList) {
    const container = document.getElementById(containerId);
    if (!container || !transferList || transferList.length === 0) return;

    const W = 480, H = 200;
    const padL = 45, padR = 20, padT = 20, padB = 30;
    const plotW = W - padL - padR;
    const plotH = H - padT - padB;

    const yMin = 8, yMax = 26;
    const xPos = idx => padL + (idx / (transferList.length - 1)) * plotW;
    const yPos = val => padT + plotH - ((val - yMin) / (yMax - yMin)) * plotH;

    const ptsTransfer = transferList.map((t, i) => `${xPos(i).toFixed(1)},${yPos(t.transfer_hr1 * 100).toFixed(1)}`).join(" ");
    const ptsLocal = transferList.map((t, i) => t.local_hr1 !== null ? `${xPos(i).toFixed(1)},${yPos(t.local_hr1 * 100).toFixed(1)}` : null).filter(Boolean).join(" ");

    const yMkt = yPos(23.83).toFixed(1);
    const yGlobal = yPos(13.76).toFixed(1);

    container.innerHTML = `
      <svg viewBox="0 0 ${W} ${H}" style="width:100%; height:auto; display:block;">
        <!-- Línea Referencia Mercado -->
        <line x1="${padL}" y1="${yMkt}" x2="${W - padR}" y2="${yMkt}" stroke="#10B981" stroke-width="1.2" stroke-dasharray="4 3"/>
        <text x="${W - padR}" y="${yMkt - 4}" fill="#34D399" font-size="9" text-anchor="end" font-weight="700">Mercado HV (23.8%)</text>

        <!-- Línea Referencia Multiregión -->
        <line x1="${padL}" y1="${yGlobal}" x2="${W - padR}" y2="${yGlobal}" stroke="#6B7280" stroke-width="1.2" stroke-dasharray="3 3"/>
        <text x="${W - padR}" y="${Number(yGlobal) + 10}" fill="#9CA3AF" font-size="9" text-anchor="end">Multiregión (13.8%)</text>

        <!-- Curva Solo Local -->
        ${ptsLocal ? `<polyline fill="none" stroke="#F59E0B" stroke-width="1.8" stroke-dasharray="4 3" points="${ptsLocal}"/>` : ""}

        <!-- Curva Transferencia (Dorado) -->
        <polyline fill="none" stroke="#D6A63C" stroke-width="2.6" points="${ptsTransfer}"/>

        <!-- Puntos y Etiquetas X -->
        ${transferList.map((t, i) => {
          const cx = xPos(i).toFixed(1);
          const cy = yPos(t.transfer_hr1 * 100).toFixed(1);
          const pct = Math.round(t.fraction * 100);
          return `
            <circle cx="${cx}" cy="${cy}" r="4.5" fill="#D6A63C" stroke="#080B10" stroke-width="1.5"/>
            <text x="${cx}" y="${H - 10}" fill="#A7AFBD" font-size="9.5" text-anchor="middle" font-weight="700">${pct}%</text>
          `;
        }).join("")}
      </svg>
      <div style="display:flex; justify-content:center; gap:20px; font-size:0.75rem; color:var(--text-gray); margin-top:8px;">
        <span style="display:flex; align-items:center; gap:6px;"><span style="width:12px; height:3px; background:#D6A63C;"></span>Transferencia Sha Tin + Fine-Tuning</span>
        <span style="display:flex; align-items:center; gap:6px;"><span style="width:12px; height:3px; background:#F59E0B; border-style:dashed;"></span>Entrenamiento Solo Local</span>
      </div>
    `;
  }

  return {
    renderProbabilityBars,
    renderPEASRadar,
    renderTransferChart
  };
})();
