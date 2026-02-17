
const API_BASE = "http://127.0.0.1:5000";

const analyzeBtn = document.getElementById("analyzeBtn");
const emailInput = document.getElementById("emailInput");
const resultDiv = document.getElementById("result");

function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderEmailResult(data) {
  if (!data || data.ok !== true) {
    const msg = data && data.error ? data.error : "Unknown error";
    resultDiv.innerHTML = `<p style="color:#ef5350;font-weight:700">${escapeHtml(msg)}</p>`;
    return;
  }

  const label = (data.email && data.email.label) || "unknown";
  const confidence = (data.email && data.email.confidence) ?? "-";
  const riskScore = (data.risk && data.risk.score) ?? "-";
  const riskLevel = (data.risk && data.risk.level) || "-";

  const cls = String(label).toLowerCase();

  resultDiv.innerHTML = `
    <div style="display:flex; align-items:center; gap:12px;">
      <div style="width:14px; height:14px; border-radius:50%; background:#5aa2ff; box-shadow:0 0 12px rgba(90,162,255,0.75);"></div>
      <div style="font-size:1.15rem; font-weight:800;">Verdict: <span class="${escapeHtml(cls)}">${escapeHtml(label)}</span></div>
    </div>
    <div style="margin-top:10px; line-height:1.75;">
      <div><b>Confidence:</b> ${escapeHtml(confidence)}%</div>
      <div><b>Risk:</b> ${escapeHtml(riskScore)} / 100 (<b>${escapeHtml(riskLevel)}</b>)</div>
    </div>
  `;
}

async function analyzeEmail() {
  const email = (emailInput && emailInput.value ? emailInput.value : "").trim();
  if (!email) {
    alert("Please paste an email to analyze.");
    return;
  }

  resultDiv.innerHTML = `
    <div class="scanner-loader">
      <div class="scanner-ring"></div>
      <div class="scanner-text">Analyzing Email...</div>
    </div>`;
  try {
    const res = await fetch(`${API_BASE}/analyze-email`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email })
    });

    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      renderEmailResult({ ok: false, error: data.error || `HTTP error ${res.status}` });
      return;
    }

    renderEmailResult(data);
  } catch (err) {
    renderEmailResult({ ok: false, error: `Error connecting to backend: ${err.message}` });
  }
}

if (analyzeBtn && emailInput && resultDiv) {
  analyzeBtn.addEventListener("click", analyzeEmail);
}

