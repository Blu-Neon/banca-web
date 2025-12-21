/*
  🎄 Effetto neve "soft" (molto leggero)
  - Si attiva solo se <html> ha class="theme-xmas"
  - Rispetta prefers-reduced-motion
*/

(function () {
  const root = document.documentElement;
  if (!root.classList.contains("theme-xmas")) return;
  if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  const canvas = document.createElement("canvas");
  canvas.id = "xmas-snow";
  canvas.setAttribute("aria-hidden", "true");
  canvas.style.position = "fixed";
  canvas.style.inset = "0";
  canvas.style.pointerEvents = "none";
  canvas.style.zIndex = "9996"; // sotto al menu (che sta a 9997+)
  canvas.style.opacity = "0.55";
  document.body.appendChild(canvas);

  const ctx = canvas.getContext("2d", { alpha: true });
  if (!ctx) return;

  let w = 0, h = 0, dpr = 1;

  function resize() {
    dpr = Math.max(1, Math.min(2, window.devicePixelRatio || 1));
    w = Math.floor(window.innerWidth);
    h = Math.floor(window.innerHeight);
    canvas.width = Math.floor(w * dpr);
    canvas.height = Math.floor(h * dpr);
    canvas.style.width = w + "px";
    canvas.style.height = h + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  const flakes = [];
  const maxFlakes = Math.max(36, Math.min(90, Math.floor((window.innerWidth * window.innerHeight) / 26000)));

  function rand(min, max) { return min + Math.random() * (max - min); }

  function spawn(initial = false) {
    const r = rand(0.9, 2.2);
    flakes.push({
      x: rand(0, w),
      y: initial ? rand(0, h) : -10,
      r,
      vx: rand(-0.25, 0.25),
      vy: rand(0.45, 1.25) * (2.2 - r),
      a: rand(0.35, 0.85)
    });
  }

  function init() {
    resize();
    flakes.length = 0;
    for (let i = 0; i < maxFlakes; i++) spawn(true);
  }

  let raf = 0;
  let running = true;

  function tick() {
    if (!running) return;
    ctx.clearRect(0, 0, w, h);

    // colore neve soft (quasi bianco, leggermente "ghiaccio")
    ctx.fillStyle = "rgba(224,242,254,0.9)";

    for (let i = 0; i < flakes.length; i++) {
      const f = flakes[i];
      f.x += f.vx;
      f.y += f.vy;

      // lieve oscillazione
      f.x += Math.sin((f.y / 28) + i) * 0.12;

      if (f.y > h + 12) {
        f.y = -10;
        f.x = rand(0, w);
      }
      if (f.x < -10) f.x = w + 10;
      if (f.x > w + 10) f.x = -10;

      ctx.globalAlpha = f.a;
      ctx.beginPath();
      ctx.arc(f.x, f.y, f.r, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;

    raf = window.requestAnimationFrame(tick);
  }

  // stop quando tab non è visibile
  document.addEventListener("visibilitychange", () => {
    running = document.visibilityState === "visible";
    if (running) {
      window.cancelAnimationFrame(raf);
      raf = window.requestAnimationFrame(tick);
    } else {
      window.cancelAnimationFrame(raf);
    }
  });

  window.addEventListener("resize", () => {
    init();
  }, { passive: true });

  init();
  raf = window.requestAnimationFrame(tick);
})();
