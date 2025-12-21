(function () {
  // ---- Snow (canvas) ----
  const canvas = document.getElementById("snow");
  const ctx = canvas.getContext("2d");
  const DPR = Math.min(2, window.devicePixelRatio || 1);

  let W = 0, H = 0;
  let flakes = [];
  let wind = 0;

  function resize() {
    const rect = canvas.getBoundingClientRect();
    W = Math.floor(rect.width);
    H = Math.floor(rect.height);
    canvas.width = Math.floor(W * DPR);
    canvas.height = Math.floor(H * DPR);
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);

    const target = Math.max(90, Math.floor(W * 0.18));
    flakes = new Array(target).fill(0).map(() => ({
      x: Math.random() * W,
      y: Math.random() * H,
      r: 1 + Math.random() * 2.2,
      s: 0.6 + Math.random() * 1.8,
      p: Math.random() * Math.PI * 2
    }));
  }

  function step() {
    ctx.clearRect(0, 0, W, H);

    // soft vignette so the snow reads better
    const g = ctx.createRadialGradient(W * 0.5, H * 0.25, 40, W * 0.5, H * 0.25, Math.max(W, H));
    g.addColorStop(0, "rgba(255,255,255,0.05)");
    g.addColorStop(1, "rgba(0,0,0,0.35)");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);

    // snow
    ctx.fillStyle = "rgba(255,255,255,0.85)";
    wind += (Math.random() - 0.5) * 0.02;
    wind = Math.max(-0.35, Math.min(0.35, wind));

    for (const f of flakes) {
      f.p += 0.02;
      f.y += f.s;
      f.x += wind * 1.8 + Math.sin(f.p) * 0.35;

      if (f.y > H + 6) { f.y = -6; f.x = Math.random() * W; }
      if (f.x < -10) f.x = W + 10;
      if (f.x > W + 10) f.x = -10;

      ctx.beginPath();
      ctx.arc(f.x, f.y, f.r, 0, Math.PI * 2);
      ctx.fill();
    }

    requestAnimationFrame(step);
  }

  // ---- Lights ----
  const lightsEl = document.getElementById("lights");
  const lightColors = [
    "rgba(255, 92, 120, 0.95)",
    "rgba(255, 220, 120, 0.95)",
    "rgba(120, 220, 255, 0.95)",
    "rgba(170, 255, 170, 0.95)"
  ];

  function placeLights() {
    lightsEl.innerHTML = "";
    const count = 38;

    for (let i = 0; i < count; i++) {
      const d = document.createElement("div");
      d.className = "light";
      d.style.background = lightColors[i % lightColors.length];

      // positions roughly inside a tree silhouette (triangle-ish)
      const y = 86 + Math.random() * 250;
      const t = (y - 86) / 250; // 0 top, 1 bottom
      const half = 22 + t * 105; // width expands toward bottom
      const x = 50 + (Math.random() * 2 - 1) * half;

      d.style.left = x + "%";
      d.style.top = y + "px";
      d.style.transform = `scale(${0.9 + Math.random() * 0.6})`;
      lightsEl.appendChild(d);
    }
  }

  function twinkle() {
    const nodes = lightsEl.querySelectorAll(".light");
    nodes.forEach((n, idx) => {
      const on = Math.random() > 0.35;
      n.style.opacity = on ? "0.95" : "0.35";
      if (idx % 7 === 0) n.style.transform = `scale(${on ? 1.15 : 0.85})`;
    });
    setTimeout(twinkle, 420);
  }

  // ---- Music ----
  const music = document.getElementById("music");
  const btnMusic = document.getElementById("btnMusic");

  async function toggleMusic() {
    if (!music) return;

    try {
      if (music.paused) {
        await music.play();
        btnMusic.textContent = "⏸︎ Musica";
      } else {
        music.pause();
        btnMusic.textContent = "▶︎ Musica";
      }
    } catch (e) {
      // iOS might block if not a user gesture; button click is a gesture, so usually OK.
      btnMusic.textContent = "▶︎ Musica";
    }
  }

  btnMusic?.addEventListener("click", toggleMusic);

  // ---- Gallery (protected assets) ----
  const photo = document.getElementById("photo");
  const counter = document.getElementById("counter");
  const prev = document.getElementById("prev");
  const next = document.getElementById("next");

  // Keep it simple: rename your files to foto1.jpg ... foto18.jpg (lowercase).
  // If you have .JPG, rename them or adjust the list here.
  const photos = Array.from({ length: 18 }, (_, i) => `foto${i + 1}.jpg`);
  let idx = 0;

  function setPhoto(i) {
    idx = (i + photos.length) % photos.length;
    const name = photos[idx];
    if (photo) photo.src = `/xmas-asset/${encodeURIComponent(name)}`;
    if (counter) counter.textContent = `${idx + 1} / ${photos.length}`;
  }

  prev?.addEventListener("click", () => setPhoto(idx - 1));
  next?.addEventListener("click", () => setPhoto(idx + 1));

  // init
  resize();
  placeLights();
  twinkle();
  step();
  setPhoto(0);

  window.addEventListener("resize", resize, { passive: true });
})();
