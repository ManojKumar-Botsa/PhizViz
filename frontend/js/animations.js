
/* =========================================
   ANIMATIONS & INTERACTIVITY
   - Particle Network Background
   - Scroll Reveal
   - 3D Tilt Effect for Cards
   - Button Ripple Effect
   ========================================= */

document.addEventListener('DOMContentLoaded', () => {
  initParticles();
  initScrollReveal();
  initTiltEffect();
  initButtonRipple();
});

/* -----------------------------------------
   1. PARTICLE NETWORK
   ----------------------------------------- */
function initParticles() {
  const canvas = document.getElementById('particles');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let width, height;
  let particles = [];

  // Configuration
  const particleCount = 60;
  const connectionDistance = 100;
  const particleColor = '#5aa2ff';

  function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = canvas.parentElement.offsetHeight || 300;
  }

  class Particle {
    constructor() {
      this.x = Math.random() * width;
      this.y = Math.random() * height;
      this.vx = (Math.random() - 0.5) * 1.5;
      this.vy = (Math.random() - 0.5) * 1.5;
      this.size = Math.random() * 2 + 1;
    }

    update() {
      this.x += this.vx;
      this.y += this.vy;

      if (this.x < 0 || this.x > width) this.vx *= -1;
      if (this.y < 0 || this.y > height) this.vy *= -1;
    }

    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fillStyle = particleColor;
      ctx.fill();
    }
  }

  function init() {
    resize();
    particles = [];
    for (let i = 0; i < particleCount; i++) {
      particles.push(new Particle());
    }
  }

  function animate() {
    ctx.clearRect(0, 0, width, height);
    
    // Update and draw particles
    for (let i = 0; i < particles.length; i++) {
      particles[i].update();
      particles[i].draw();

      // Draw connections
      for (let j = i; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < connectionDistance) {
          ctx.beginPath();
          ctx.strokeStyle = `rgba(90, 162, 255, ${1 - distance / connectionDistance})`;
          ctx.lineWidth = 1;
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.stroke();
        }
      }
    }
    requestAnimationFrame(animate);
  }

  window.addEventListener('resize', () => {
    resize();
    init();
  });

  init();
  animate();
}

/* -----------------------------------------
   2. SCROLL REVEAL (IntersectionObserver)
   ----------------------------------------- */
function initScrollReveal() {
  const options = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px"
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, options);

  // Select elements to reveal
  const elements = document.querySelectorAll('.card, .hero__content > *, .actions, .badges__row > *');
  elements.forEach(el => {
    el.classList.add('reveal-on-scroll');
    observer.observe(el);
  });
}

/* -----------------------------------------
   3. 3D TILT EFFECT for Cards
   ----------------------------------------- */
function initTiltEffect() {
  const cards = document.querySelectorAll('.card');

  cards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      const rotateX = ((y - centerY) / centerY) * -5; // Max 5 deg
      const rotateY = ((x - centerX) / centerX) * 5;

      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
    });

    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)';
    });
  });
}

/* -----------------------------------------
   4. BUTTON RIPPLE EFFECT
   ----------------------------------------- */
function initButtonRipple() {
  const buttons = document.querySelectorAll('.btn');

  buttons.forEach(btn => {
    btn.addEventListener('click', function(e) {
      let x = e.clientX - e.target.offsetLeft;
      let y = e.clientY - e.target.offsetTop;
      
      let ripples = document.createElement('span');
      ripples.style.left = x + 'px';
      ripples.style.top = y + 'px';
      ripples.classList.add('ripple');
      
      this.appendChild(ripples);
      
      setTimeout(() => {
        ripples.remove();
      }, 1000);
    });
  });
}
