
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

  resultDiv.innerHTML = `<p style="color:#ffc107;font-weight:700">Scanning…</p>`;
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

const canvas = document.getElementById("particles");
if (canvas) {
  const ctx = canvas.getContext("2d");
  const setSize = () => {
    canvas.width = window.innerWidth;
    canvas.height = 260;
  };
  setSize();
  window.addEventListener("resize", setSize);

  const particles = Array.from({ length: 60 }, () => ({
    x: Math.random() * canvas.width,
    y: Math.random() * canvas.height,
    r: Math.random() * 2 + 1,
    dx: (Math.random() - 0.5) * 0.6,
    dy: (Math.random() - 0.5) * 0.6
  }));

  function animateParticles() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => {
      p.x += p.dx;
      p.y += p.dy;
      if (p.x < 0 || p.x > canvas.width) p.dx *= -1;
      if (p.y < 0 || p.y > canvas.height) p.dy *= -1;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = "#5aa2ff";
      ctx.fill();
    });
    requestAnimationFrame(animateParticles);
  }
  animateParticles();
}

