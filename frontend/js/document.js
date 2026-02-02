
const API_BASE = "http://127.0.0.1:5000";

const analyzeBtn = document.getElementById("analyzeBtn");
const fileInput = document.getElementById("fileInput");
const resultDiv = document.getElementById("result");

function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function arrayBufferToBase64(buffer) {
  const bytes = new Uint8Array(buffer);
  let binary = "";
  const chunkSize = 0x8000;
  for (let i = 0; i < bytes.length; i += chunkSize) {
    binary += String.fromCharCode.apply(null, bytes.subarray(i, i + chunkSize));
  }
  return btoa(binary);
}

async function readFileHeadBase64(file, maxBytes) {
  const slice = file.slice(0, maxBytes);
  const buf = await slice.arrayBuffer();
  return arrayBufferToBase64(buf);
}

function renderDocumentResult(data) {
  if (!data || data.ok !== true) {
    const msg = data && data.error ? data.error : "Unknown error";
    resultDiv.innerHTML = `<p style="color:#ef5350;font-weight:700">${escapeHtml(msg)}</p>`;
    return;
  }

  const riskScore = (data.risk && data.risk.score) ?? "-";
  const riskLevel = (data.risk && data.risk.level) || "-";

  const doc = data.document || {};
  const fileChecks = doc.file_checks || {};
  const macroScan = doc.macro_scan || {};
  const embedded = doc.embedded_links || {};

  resultDiv.innerHTML = `
    <div style="line-height:1.8;">
      <div><b>Risk:</b> ${escapeHtml(riskScore)} / 100 (<b>${escapeHtml(riskLevel)}</b>)</div>

      <div style="margin-top:14px;"><b>File checks</b></div>
      <div style="margin-top:6px;">
        <div>Double extension: <b>${escapeHtml(Boolean(fileChecks.double_extension))}</b></div>
        <div>Signature mismatch: <b>${escapeHtml(Boolean(fileChecks.signature_mismatch))}</b></div>
        <div>Size anomaly: <b>${escapeHtml(Boolean(fileChecks.size_anomaly))}</b></div>
      </div>

      <div style="margin-top:14px;"><b>Macro scan</b></div>
      <div style="margin-top:6px;">Suspected macros: <b>${escapeHtml(Boolean(macroScan.suspected_macros))}</b></div>

      <div style="margin-top:14px;"><b>Embedded links</b></div>
      <div style="margin-top:6px;">Suspicious: <b>${escapeHtml(Boolean(embedded.suspicious))}</b></div>
    </div>
  `;
}

async function scanDocument() {
  const file = fileInput && fileInput.files ? fileInput.files[0] : null;
  if (!file) {
    alert("Please choose a file.");
    return;
  }

  resultDiv.innerHTML = `<p style="color:#ffc107;font-weight:700">Scanning…</p>`;

  try {
    const head_base64 = await readFileHeadBase64(file, 4096);
    const payload = {
      filename: file.name,
      mime: file.type || "",
      size_bytes: file.size,
      head_base64
    };

    const res = await fetch(`${API_BASE}/scan-document`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      renderDocumentResult({ ok: false, error: data.error || `HTTP error ${res.status}` });
      return;
    }

    renderDocumentResult(data);
  } catch (err) {
    renderDocumentResult({ ok: false, error: `Error connecting to backend: ${err.message}` });
  }
}

if (analyzeBtn && fileInput && resultDiv) {
  analyzeBtn.addEventListener("click", scanDocument);
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

