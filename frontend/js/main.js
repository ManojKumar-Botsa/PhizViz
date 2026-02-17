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

    resultDiv.innerHTML = `
    <div class="scanner-loader">
      <div class="scanner-ring"></div>
      <div class="scanner-text">Analyzing...</div>
    </div>`;

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


