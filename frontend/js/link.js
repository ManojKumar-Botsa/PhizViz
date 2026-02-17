
const API_BASE = "http://127.0.0.1:5000";

const analyzeBtn = document.getElementById("analyzeBtn");
const urlInput = document.getElementById("urlInput");
const resultDiv = document.getElementById("result");

function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderLinkResult(data) {
  if (!data || data.ok !== true) {
    const msg = data && data.error ? data.error : "Unknown error";
    resultDiv.innerHTML = `<p style="color:#ef5350;font-weight:700">${escapeHtml(msg)}</p>`;
    return;
  }

  const url = data.url || "";
  const verdict = (data.verdict && data.verdict.verdict) || "-";
  const riskLevel = (data.verdict && data.verdict.risk_level) || "-";
  const riskScore = (data.risk && data.risk.score) ?? "-";
  const riskBand = (data.risk && data.risk.level) || "-";

  const indicators = Array.isArray(data.indicators) ? data.indicators : [];
  const indicatorHtml = indicators.length
    ? `<div style="margin-top:12px;"><b>Indicators:</b><ul style="margin:8px 0 0; padding-left:18px;">${indicators
      .map(i => `<li><b>${escapeHtml(i.type || "")}</b> (${escapeHtml(i.severity || "")}): ${escapeHtml(i.details || "")}</li>`)
      .join("")}</ul></div>`
    : `<div style="margin-top:12px;"><b>Indicators:</b> None</div>`;

  resultDiv.innerHTML = `
    <div style="line-height:1.8;">
      <div><b>URL:</b> ${escapeHtml(url)}</div>
      <div><b>Verdict:</b> ${escapeHtml(verdict)} (<b>${escapeHtml(riskLevel)}</b>)</div>
      <div><b>Risk:</b> ${escapeHtml(riskScore)} / 100 (<b>${escapeHtml(riskBand)}</b>)</div>
      ${indicatorHtml}
    </div>
  `;
}

async function scanLink() {
  const url = (urlInput && urlInput.value ? urlInput.value : "").trim();
  if (!url) {
    alert("Please paste a URL.");
    return;
  }

  resultDiv.innerHTML = `
    <div class="scanner-loader">
      <div class="scanner-ring"></div>
      <div class="scanner-text">Scanning URL...</div>
    </div>`;
  try {
    const res = await fetch(`${API_BASE}/scan-link`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url })
    });

    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      renderLinkResult({ ok: false, error: data.error || `HTTP error ${res.status}` });
      return;
    }

    renderLinkResult(data);
  } catch (err) {
    renderLinkResult({ ok: false, error: `Error connecting to backend: ${err.message}` });
  }
}

if (analyzeBtn && urlInput && resultDiv) {
  analyzeBtn.addEventListener("click", scanLink);
}


