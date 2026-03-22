const API_BASE = "";

const statsDiv = document.getElementById("dashboardStats");
const historyDiv = document.getElementById("dashboardHistory");

function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderDashboard(data) {
  if (!statsDiv || !historyDiv) return;

  if (!data || data.ok !== true) {
    const msg = data && data.error ? data.error : "Unknown error";
    statsDiv.innerHTML = `<div id="result"><p style="color:#ef5350;font-weight:700">${escapeHtml(msg)}</p></div>`;
    historyDiv.innerHTML = "";
    return;
  }

  const stats = data.stats || {};
  const total = stats.total ?? 0;
  const high = stats.HIGH ?? 0;
  const medium = stats.MEDIUM ?? 0;
  const low = stats.LOW ?? 0;

  statsDiv.innerHTML = `
    <div style="display:grid; grid-template-columns: repeat(4, minmax(140px, 1fr)); gap:12px;" class="badges__row">
      <div class="badge"><span class="dot"></span> Total: <b>${escapeHtml(total)}</b></div>
      <div class="badge"><span class="dot"></span> HIGH: <b>${escapeHtml(high)}</b></div>
      <div class="badge"><span class="dot"></span> MEDIUM: <b>${escapeHtml(medium)}</b></div>
      <div class="badge"><span class="dot"></span> LOW: <b>${escapeHtml(low)}</b></div>
    </div>
  `;

  const items = Array.isArray(data.recent) ? data.recent : [];
  if (!items.length) {
    historyDiv.innerHTML = `<div id="result"><p style="color:#cfd7ff">No scans yet. Run Email/Link/Document/Stego scans first.</p></div>`;
    return;
  }

  historyDiv.innerHTML = `
    <div id="result">
      <div style="font-weight:800; font-size:1.1rem; margin-bottom:10px;">Recent activity</div>
      <div style="display:flex; flex-direction:column; gap:10px;">
        ${items
      .map((e) => {
        const t = e.type || "scan";
        const ts = e.ts || "";
        const summary = e.summary || "";
        const riskScore = e.risk && e.risk.score != null ? e.risk.score : "-";
        const riskLevel = e.risk && e.risk.level ? e.risk.level : "-";
        return `
              <div style="padding:12px; border-radius:12px; border:1px solid rgba(255,255,255,0.08); background:rgba(255,255,255,0.03);">
                <div style="display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap;">
                  <div><b>${escapeHtml(t)}</b> — ${escapeHtml(summary)}</div>
                  <div style="color:#b6c0ff;">${escapeHtml(ts)}</div>
                </div>
                <div style="margin-top:6px;"><b>Risk:</b> ${escapeHtml(riskScore)} / 100 (<b>${escapeHtml(riskLevel)}</b>)</div>
              </div>
            `;
      })
      .join("")}
      </div>
    </div>
  `;
}

async function loadDashboard() {
  if (!statsDiv || !historyDiv) return;

  statsDiv.innerHTML = `
    <div class="scanner-loader">
      <div class="scanner-ring"></div>
      <div class="scanner-text">Loading Dashboard...</div>
    </div>`;
  historyDiv.innerHTML = "";

  try {
    const res = await fetch(`${API_BASE}/dashboard`, { method: "GET" });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      renderDashboard({ ok: false, error: data.error || `HTTP error ${res.status}` });
      return;
    }
    renderDashboard(data);
  } catch (err) {
    renderDashboard({ ok: false, error: `Error connecting to backend: ${err.message}` });
  }
}

loadDashboard();

