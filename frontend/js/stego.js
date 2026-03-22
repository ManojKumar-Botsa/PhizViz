
const API_BASE = "";

const analyzeBtn = document.getElementById("analyzeBtn");
const imageInput = document.getElementById("imageInput");
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

async function readImageDimensions(file) {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => {
      const width = img.naturalWidth || img.width;
      const height = img.naturalHeight || img.height;
      URL.revokeObjectURL(url);
      resolve({ width, height });
    };
    img.onerror = (e) => {
      URL.revokeObjectURL(url);
      reject(e);
    };
    img.src = url;
  });
}

function renderStegoResult(data) {
  if (!data || data.ok !== true) {
    const msg = data && data.error ? data.error : "Unknown error";
    resultDiv.innerHTML = `<p style="color:#ef5350;font-weight:700">${escapeHtml(msg)}</p>`;
    return;
  }

  const stego = data.steganography || {};
  const signals = stego.signals || {};
  const meta = stego.metadata_flags || {};

  const signalsPretty = escapeHtml(JSON.stringify(signals, null, 2));
  const metaPretty = escapeHtml(JSON.stringify(meta, null, 2));

  resultDiv.innerHTML = `
    <div style="line-height:1.6;">
      <div style="margin-top:8px;"><b>Signals</b></div>
      <pre style="white-space:pre-wrap; background:#0f1c3f; border:1px solid #26315f; border-radius:12px; padding:14px; margin:8px 0 0;">${signalsPretty}</pre>
      <div style="margin-top:14px;"><b>Metadata flags</b></div>
      <pre style="white-space:pre-wrap; background:#0f1c3f; border:1px solid #26315f; border-radius:12px; padding:14px; margin:8px 0 0;">${metaPretty}</pre>
    </div>
  `;
}

async function scanImage() {
  const file = imageInput && imageInput.files ? imageInput.files[0] : null;
  if (!file) {
    alert("Please choose an image.");
    return;
  }

  resultDiv.innerHTML = `
    <div class="scanner-loader">
      <div class="scanner-ring"></div>
      <div class="scanner-text">Scanning Image...</div>
    </div>`;
  try {
    const head_base64 = await readFileHeadBase64(file, 4096);
    let width;
    let height;
    try {
      const dims = await readImageDimensions(file);
      width = dims.width;
      height = dims.height;
    } catch (_) {
      width = undefined;
      height = undefined;
    }

    const payload = {
      filename: file.name,
      mime: file.type || "",
      size_bytes: file.size,
      width,
      height,
      head_base64
    };

    const res = await fetch(`${API_BASE}/stego-scan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      renderStegoResult({ ok: false, error: data.error || `HTTP error ${res.status}` });
      return;
    }

    renderStegoResult(data);
  } catch (err) {
    renderStegoResult({ ok: false, error: `Error connecting to backend: ${err.message}` });
  }
}

if (analyzeBtn && imageInput && resultDiv) {
  analyzeBtn.addEventListener("click", scanImage);
}


