// Elements
const analyzeBtn = document.getElementById("analyzeBtn");
const emailInput = document.getElementById("emailInput");
const resultDiv = document.getElementById("result");
const graphDiv = document.getElementById("graph");

// Analyze email
analyzeBtn.addEventListener("click", async () => {
  const email = emailInput.value.trim();
  if (!email) {
    alert("Paste an email to analyze!");
    return;
  }

  resultDiv.innerHTML = "<p style='color:#ffa500;font-weight:bold'>Analyzing...</p>";

  try {
    const response = await fetch("https://phishviz.onrender.com/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email })
    });

    if (!response.ok) throw new Error("Network response not ok");

    const data = await response.json();
    displayResult(data);

  } catch (err) {
    resultDiv.innerHTML = `<p style="color:red;font-weight:bold">Error connecting to backend: ${err.message}</p>`;
  }
});

// Display results with animated colored ovals and details
function displayResult(data) {
  const { verdict, details, color, graph } = data;

  resultDiv.innerHTML = `
    <div class="verdict-container" style="display:flex;align-items:center;gap:10px;margin-bottom:10px;animation: fadeIn 1s;">
      <div class="verdict-oval" style="
        width:25px;height:25px;border-radius:50%;
        background:${color};box-shadow:0 0 20px ${color};
        animation: glow 1.5s infinite alternate;"></div>
      <strong style="font-size:1.2em;text-transform:uppercase;">${verdict}</strong>
    </div>
    <div class="verdict-details" style="animation: fadeIn 1.5s;line-height:1.5;">${details.replace(/\n/g,"<br>")}</div>
  `;

  renderGraph(graph || []);
}

// D3 Graph with colors
function renderGraph(data) {
  d3.select("#graph").selectAll("*").remove();
  if (!data.length) return;

  const width = graphDiv.offsetWidth;
  const height = graphDiv.offsetHeight;

  const svg = d3.select("#graph")
    .append("svg")
    .attr("width", width)
    .attr("height", height);

  const links = data
    .filter(d => d.source && d.target)
    .map(d => ({ source: d.source, target: d.target }));

  const simulation = d3.forceSimulation(data)
    .force("link", d3.forceLink(links).id(d => d.id).distance(120))
    .force("charge", d3.forceManyBody().strength(-300))
    .force("center", d3.forceCenter(width / 2, height / 2));

  const colorMap = { safe: "#28a745", suspicious: "#ffc107", phishing: "#dc3545", user:"#00bfff" };

  const link = svg.selectAll("line")
    .data(links)
    .enter()
    .append("line")
    .attr("stroke", "#aaa")
    .attr("stroke-width", 2);

  const node = svg.selectAll("circle")
    .data(data)
    .enter()
    .append("circle")
    .attr("r", 20)
    .attr("fill", d => colorMap[d.group] || "#ffa500")
    .attr("stroke","#fff")
    .attr("stroke-width",2)
    .call(d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended)
    );

  const labels = svg.selectAll("text")
    .data(data)
    .enter()
    .append("text")
    .text(d => d.id)
    .attr("font-size","12px")
    .attr("fill","#fff")
    .attr("text-anchor","middle")
    .attr("dy",4);

  simulation.on("tick", () => {
    link
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);

    node
      .attr("cx", d => d.x)
      .attr("cy", d => d.y);

    labels
      .attr("x", d => d.x)
      .attr("y", d => d.y);
  });

  function dragstarted(event,d) { if(!event.active) simulation.alphaTarget(0.3).restart(); d.fx=d.x; d.fy=d.y;}
  function dragged(event,d){ d.fx=event.x; d.fy=event.y; }
  function dragended(event,d){ if(!event.active) simulation.alphaTarget(0); d.fx=null; d.fy=null; }
}

// Particles background
const canvas = document.getElementById("particles");
const ctx = canvas.getContext("2d");
canvas.width = canvas.offsetWidth;
canvas.height = canvas.offsetHeight;

const particles = Array.from({length:70},() => ({
  x: Math.random()*canvas.width,
  y: Math.random()*canvas.height,
  r: Math.random()*2+1.5,
  dx: (Math.random()-0.5)/1.5,
  dy: (Math.random()-0.5)/1.5
}));

function animateParticles() {
  ctx.clearRect(0,0,canvas.width,canvas.height);
  particles.forEach(p=>{
    p.x+=p.dx; p.y+=p.dy;
    if(p.x<0||p.x>canvas.width)p.dx*=-1;
    if(p.y<0||p.y>canvas.height)p.dy*=-1;
    ctx.beginPath();
    ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
    ctx.fillStyle="#ffa500";
    ctx.fill();
  });
  requestAnimationFrame(animateParticles);
}
animateParticles();

/* CSS Animations */
const style = document.createElement("style");
style.innerHTML = `
@keyframes glow {0%{box-shadow:0 0 10px #ffa500;}50%{box-shadow:0 0 25px #ff7f50;}100%{box-shadow:0 0 10px #ffa500;}}
@keyframes fadeIn {0%{opacity:0; transform:translateY(-10px);}100%{opacity:1; transform:translateY(0);}}
.verdict-oval { transition: box-shadow 0.5s ease-in-out; }
`;
document.head.appendChild(style);
