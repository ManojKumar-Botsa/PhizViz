const API_BASE = "http://127.0.0.1:5000";

const refreshBtn = document.getElementById("refreshBtn");
const downloadBtn = document.getElementById("downloadBtn");
const contentDiv = document.getElementById("reportsContent");

let lastData = null;

function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderReports(data) {
  if (!contentDiv) return;

  if (!data || data.ok !== true) {
    const msg = data && data.error ? data.error : "Unknown error";
    contentDiv.innerHTML = `<div id="result"><p style="color:#ef5350;font-weight:700">${escapeHtml(msg)}</p></div>`;
    return;
  }

  const history = Array.isArray(data.history) ? data.history : [];
  if (!history.length) {
    contentDiv.innerHTML = `<div id="result"><p style="color:#cfd7ff">No reports yet. Run some scans first.</p></div>`;
    return;
  }

  contentDiv.innerHTML = `
    <div id="result">
      <div style="font-weight:800; font-size:1.1rem; margin-bottom:10px;">History (${escapeHtml(history.length)})</div>
      <div style="display:flex; flex-direction:column; gap:10px;">
        ${history
      .slice()
      .reverse()
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

async function loadReports() {
  if (!contentDiv) return;
  contentDiv.innerHTML = `
    <div class="scanner-loader">
      <div class="scanner-ring"></div>
      <div class="scanner-text">Loading Reports...</div>
    </div>`;

  try {
    const res = await fetch(`${API_BASE}/reports`, { method: "GET" });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      lastData = null;
      renderReports({ ok: false, error: data.error || `HTTP error ${res.status}` });
      return;
    }
    lastData = data;
    renderReports(data);
  } catch (err) {
    lastData = null;
    renderReports({ ok: false, error: `Error connecting to backend: ${err.message}` });
  }
}

function downloadJson() {
  if (!lastData || lastData.ok !== true) {
    alert("Nothing to download yet. Please refresh.");
    return;
  }
  const blob = new Blob([JSON.stringify(lastData, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `phishviz-reports-${Date.now()}.json`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

if (refreshBtn) refreshBtn.addEventListener("click", loadReports);
if (downloadBtn) downloadBtn.addEventListener("click", downloadJson);

loadReports();

