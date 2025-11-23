---
layout: default
title: Cool Stuff
---

<div id="matrix-container">
  <canvas id="matrix-canvas"></canvas>
  <div id="matrix-overlay">
    <h2>Cool Stuff</h2>
    <p>Click anywhere to pause/resume the matrix</p>
    <div class="content-section">
      <h3>What's falling?</h3>
      <p>Economic equations, Python code snippets from my research, variable names from my models, and mathematical symbols used in computational economics.</p>

      <h3>The Code Behind This</h3>
      <p>This Matrix rain effect is built with vanilla JavaScript and HTML5 Canvas. Each column drops characters from my actual research code - everything from SHAP analysis to cultural distance calculations to neural network implementations.</p>

      <h3>Easter Eggs</h3>
      <p>Watch closely - you might spot equations from my dissertation, snippets from my QuantEcon work, or variables from the CMIE-CPHS dataset analysis.</p>
    </div>
  </div>
</div>

<style>
#matrix-container {
  position: relative;
  width: 100%;
  min-height: 600px;
  margin: 20px 0;
  background: #000;
  overflow: hidden;
  border: 1px solid #333;
}

#matrix-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: block;
}

#matrix-overlay {
  position: relative;
  z-index: 10;
  padding: 40px;
  color: #00ff00;
  pointer-events: none;
}

#matrix-overlay h2 {
  font-size: 24px;
  margin-bottom: 10px;
  color: #00ff00;
  text-shadow: 0 0 10px #00ff00;
}

#matrix-overlay h3 {
  font-size: 16px;
  margin-top: 30px;
  margin-bottom: 10px;
  color: #00dd00;
}

#matrix-overlay p {
  font-size: 12px;
  line-height: 1.8;
  color: #00cc00;
  max-width: 600px;
}

.content-section {
  margin-top: 40px;
  background: rgba(0, 0, 0, 0.7);
  padding: 20px;
  border: 1px solid #003300;
  pointer-events: auto;
}

#matrix-container.paused #matrix-overlay p:first-of-type {
  color: #ffff00;
}
</style>

<script>
(function() {
  const canvas = document.getElementById('matrix-canvas');
  const ctx = canvas.getContext('2d');
  const container = document.getElementById('matrix-container');

  // Set canvas size
  function resizeCanvas() {
    canvas.width = container.offsetWidth;
    canvas.height = Math.max(container.offsetHeight, 600);
  }
  resizeCanvas();
  window.addEventListener('resize', resizeCanvas);

  // Matrix characters - mix of code, equations, and symbols
  const matrixChars = [
    // Economic variables
    'GDP', 'β', 'δ', 'α', 'σ', 'λ', 'θ', 'ρ', 'γ',
    // Python snippets
    'import', 'numpy', 'pandas', 'def', 'class', 'return',
    'for', 'if', 'else', 'while', 'sklearn', 'torch',
    // Math symbols
    '∑', '∫', '∂', '≈', '≤', '≥', '∞', '∇', '⊗',
    // Research terms
    'SHAP', 'CMIE', 'CPHS', 'ASER', 'SHRUG', 'RBI',
    'caste', 'income', 'education', 'culture', 'debt',
    // Code snippets
    'model.fit()', 'np.array', 'pd.DataFrame', 'plt.plot',
    'tf.keras', 'shap.values', 'OLS', 'DiD', 'IV',
    // Numbers and symbols
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    '{', '}', '[', ']', '(', ')', '<', '>', '=', '+', '-', '*', '/'
  ];

  const fontSize = 14;
  const columns = Math.floor(canvas.width / fontSize);
  const drops = new Array(columns).fill(1);

  let animationId;
  let isPaused = false;

  function draw() {
    // Fade effect
    ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = '#0F0';
    ctx.font = fontSize + 'px monospace';

    for (let i = 0; i < drops.length; i++) {
      // Random character from our matrix chars
      const text = matrixChars[Math.floor(Math.random() * matrixChars.length)];
      const x = i * fontSize;
      const y = drops[i] * fontSize;

      // Gradient effect - brighter at the front
      const brightness = Math.random();
      if (brightness > 0.975) {
        ctx.fillStyle = '#fff';
      } else if (brightness > 0.95) {
        ctx.fillStyle = '#0f0';
      } else {
        ctx.fillStyle = '#0a0';
      }

      ctx.fillText(text, x, y);

      // Reset drop randomly
      if (y > canvas.height && Math.random() > 0.975) {
        drops[i] = 0;
      }

      drops[i]++;
    }
  }

  function animate() {
    draw();
    animationId = requestAnimationFrame(animate);
  }

  // Start animation
  animate();

  // Pause/resume on click
  container.addEventListener('click', function(e) {
    if (e.target.tagName === 'A' || e.target.closest('.content-section')) {
      return; // Don't pause if clicking links or content
    }

    if (isPaused) {
      animate();
      container.classList.remove('paused');
      isPaused = false;
    } else {
      cancelAnimationFrame(animationId);
      container.classList.add('paused');
      isPaused = true;
    }
  });
})();
</script>
