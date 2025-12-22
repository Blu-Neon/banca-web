(function () {
  // ---- Snow (canvas) ----
  const canvas = document.getElementById("snow");
  const ctx = canvas?.getContext("2d");
  if (!canvas || !ctx) return;

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

    const g = ctx.createRadialGradient(W * 0.5, H * 0.25, 40, W * 0.5, H * 0.25, Math.max(W, H));
    g.addColorStop(0, "rgba(255,255,255,0.05)");
    g.addColorStop(1, "rgba(0,0,0,0.35)");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);

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
  const lightsEl = document.getElementById("treeLights");
  const lightColors = [
    "rgba(255, 92, 120, 0.95)",
    "rgba(255, 220, 120, 0.95)",
    "rgba(120, 220, 255, 0.95)",
    "rgba(170, 255, 170, 0.95)"
  ];

  function placeLights() {
    if (!lightsEl) return;
    lightsEl.innerHTML = "";
    const count = 38;

    for (let i = 0; i < count; i++) {
      const d = document.createElement("div");
      d.className = "light";
      d.style.background = lightColors[i % lightColors.length];

      // percentuali: mobile perfetto
      const y = 18 + Math.random() * 68;
      const t = (y - 18) / 68;
      const half = 10 + t * 36;
      const x = 50 + (Math.random() * 2 - 1) * half;

      d.style.left = x + "%";
      d.style.top = y + "%";
      d.style.transform = `scale(${0.9 + Math.random() * 0.6})`;
      lightsEl.appendChild(d);
    }
  }

  function twinkle() {
    if (!lightsEl) return;
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
    if (!music || !btnMusic) return;
    try {
      if (music.paused) {
        await music.play();
        btnMusic.textContent = "⏸︎ Musica";
      } else {
        music.pause();
        btnMusic.textContent = "▶︎ Musica";
      }
    } catch {
      btnMusic.textContent = "▶︎ Musica";
    }
  }

  btnMusic?.addEventListener("click", toggleMusic);

  // ---- Gallery ----
  const photo = document.getElementById("photo");
  const counter = document.getElementById("counter");
  const prev = document.getElementById("prev");
  const next = document.getElementById("next");
  const frame = photo?.closest(".frame");

  const total = 18;
  let idx = 0;

  function candidatesFor(n) {
    const base = `foto${n}`;
    return [`${base}.jpg`, `${base}.JPG`, `${base}.jpeg`, `${base}.JPEG`];
  }

  function setFrameBg(url) {
    if (frame) frame.style.setProperty("--bg", `url("${url}")`);
  }

  function loadWithFallback(list) {
    if (!photo || list.length === 0) return;

    const name = list[0];
    const url = `/xmas-asset/${encodeURIComponent(name)}`;

    setFrameBg(url);
    photo.onerror = () => loadWithFallback(list.slice(1));
    photo.src = url;
  }

  function setPhoto(i) {
    idx = (i + total) % total;
    if (counter) counter.textContent = `${idx + 1} / ${total}`;
    loadWithFallback(candidatesFor(idx + 1));
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
