const analyzeBtn = document.getElementById("analyzeBtn");
const emailInput = document.getElementById("emailInput");
const resultDiv = document.getElementById("result");

if (analyzeBtn && emailInput && resultDiv) {
analyzeBtn.addEventListener("click", async () => {
  const email = emailInput.value.trim();
  if (!email) {
    alert("Please paste an email to analyze.");
    return;
  }

  resultDiv.innerHTML = `<p style="color:#ffa500;font-weight:bold">Analyzing…</p>`;

  try {
    const response = await fetch("http://127.0.0.1:5000/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email })
    });
 

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    renderResult(data);

  } catch (err) {
    resultDiv.innerHTML = `
      <p style="color:red;font-weight:bold">
        Error connecting to backend: ${err.message}
      </p>`;
  }
});
}

function renderResult(data) {
  const {
    verdict,
    confidence
  } = data;

  const colors = {
    safe: "#28a745",
    suspicious: "#ffc107",
    phishing: "#dc3545"
  };

  const color = colors[verdict] || "#6c757d";

  resultDiv.innerHTML = `
    <div style="
      display:flex;
      align-items:center;
      gap:10px;
      margin-bottom:10px;
      animation: fadeIn 0.8s;
    ">
      <div style="
        width:22px;
        height:22px;
        border-radius:50%;
        background:${color};
        box-shadow:0 0 15px ${color};
      "></div>

      <strong style="
        font-size:1.3em;
        text-transform:uppercase;
        color:${color};
      ">
        ${verdict}
      </strong>
    </div>

    <div style="line-height:1.6;">
      <b>Confidence:</b> ${confidence}%<br>
    </div>
  `;
}

/* ===== Particle Background (unchanged but simplified) ===== */
const canvas = document.getElementById("particles");
if (canvas) {
  const ctx = canvas.getContext("2d");
  canvas.width = window.innerWidth;
  canvas.height = 250;
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
      ctx.fillStyle = "#ffa500";
      ctx.fill();
    });
    requestAnimationFrame(animateParticles);
  }
  animateParticles();
}

/* Simple fade animation */
const style = document.createElement("style");
style.innerHTML = `
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-6px); }
  to { opacity: 1; transform: translateY(0); }
}`;
document.head.appendChild(style);
