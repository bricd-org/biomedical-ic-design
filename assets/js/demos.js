/* Shared helpers for the interactive demos (_includes/demos/*.html). No dependencies. */
(function () {
  if (window.BD) return;
  var C = { grid: 'rgba(140,190,240,.14)', axis: 'rgba(170,205,240,.62)', blue: '#7fb8f0', gold: '#e0b85a',
            red: '#f08a6a', green: '#7fe0a0', teal: '#7fd0b8', white: '#ffffff', dim: 'rgba(170,205,240,.45)' };
  var FONT = '9.5px "IBM Plex Mono", monospace';

  function setup(c) {
    var dpr = window.devicePixelRatio || 1, w = c.clientWidth, h = c.clientHeight;
    if (c.width !== Math.round(w * dpr) || c.height !== Math.round(h * dpr)) { c.width = Math.round(w * dpr); c.height = Math.round(h * dpr); }
    var g = c.getContext('2d'); g.setTransform(dpr, 0, 0, dpr, 0, 0); g.clearRect(0, 0, w, h);
    g.font = FONT; g.lineJoin = 'round';
    return { g: g, w: w, h: h };
  }
  function lg(v) { return Math.log10(v); }
  /* plot frame: o = {x:[min,max], y:[min,max], xlog, ylog, xt:[[v,'label']], yt:[...], xl, yl, pad:{l,r,t,b}} */
  function frame(d, o) {
    var p = Object.assign({ l: 48, r: 12, t: 22, b: 26 }, o.pad || {}), g = d.g;
    var x0 = o.xlog ? lg(o.x[0]) : o.x[0], x1 = o.xlog ? lg(o.x[1]) : o.x[1];
    var y0 = o.ylog ? lg(o.y[0]) : o.y[0], y1 = o.ylog ? lg(o.y[1]) : o.y[1];
    var X = function (v) { var u = o.xlog ? lg(Math.max(v, 1e-300)) : v; return p.l + (d.w - p.l - p.r) * (u - x0) / (x1 - x0); };
    var Y = function (v) { var u = o.ylog ? lg(Math.max(v, 1e-300)) : v; return d.h - p.b - (d.h - p.t - p.b) * (u - y0) / (y1 - y0); };
    g.strokeStyle = C.grid; g.lineWidth = 1; g.fillStyle = C.axis;
    (o.xt || []).forEach(function (t) { var x = X(t[0]); g.beginPath(); g.moveTo(x, p.t); g.lineTo(x, d.h - p.b); g.stroke();
      g.textAlign = 'center'; g.fillText(t[1], x, d.h - p.b + 12); });
    (o.yt || []).forEach(function (t) { var y = Y(t[0]); g.beginPath(); g.moveTo(p.l, y); g.lineTo(d.w - p.r, y); g.stroke();
      g.textAlign = 'right'; g.fillText(t[1], p.l - 5, y + 3); });
    g.textAlign = 'right'; if (o.xl) g.fillText(o.xl, d.w - p.r, d.h - 4);
    g.textAlign = 'left'; if (o.yl) g.fillText(o.yl, 4, p.t - 8 + 0);
    g.textAlign = 'left';
    return { X: X, Y: Y, p: p, d: d, clipIn: function () { g.save(); g.beginPath(); g.rect(p.l, p.t, d.w - p.l - p.r, d.h - p.t - p.b); g.clip(); },
             clipOut: function () { g.restore(); } };
  }
  function line(f, xs, ys, col, w, dash) {
    var g = f.d.g; f.clipIn(); g.strokeStyle = col; g.lineWidth = w || 1.6; g.setLineDash(dash || []); g.beginPath();
    var started = false;
    for (var i = 0; i < xs.length; i++) {
      if (!isFinite(ys[i])) { started = false; continue; }
      var x = f.X(xs[i]), y = f.Y(ys[i]);
      if (!started) { g.moveTo(x, y); started = true; } else g.lineTo(x, y);
    }
    g.stroke(); g.setLineDash([]); f.clipOut();
  }
  function hline(f, y, col, dash, label) {
    var g = f.d.g, yy = f.Y(y); g.strokeStyle = col; g.setLineDash(dash || [5, 4]); g.lineWidth = 1.1;
    g.beginPath(); g.moveTo(f.p.l, yy); g.lineTo(f.d.w - f.p.r, yy); g.stroke(); g.setLineDash([]);
    if (label) { g.fillStyle = col; g.textAlign = 'right'; g.fillText(label, f.d.w - f.p.r - 2, yy - 4); g.textAlign = 'left'; }
  }
  function vline(f, x, col, dash, label) {
    var g = f.d.g, xx = f.X(x); g.strokeStyle = col; g.setLineDash(dash || [5, 4]); g.lineWidth = 1.1;
    g.beginPath(); g.moveTo(xx, f.p.t); g.lineTo(xx, f.d.h - f.p.b); g.stroke(); g.setLineDash([]);
    if (label) { g.fillStyle = col; g.fillText(label, xx + 4, f.p.t + 10); }
  }
  function dot(f, x, y, col, r) { var g = f.d.g; g.fillStyle = col; g.beginPath(); g.arc(f.X(x), f.Y(y), r || 3.5, 0, 7); g.fill(); }
  function logticks(a, b, unit) {
    var t = [];
    for (var e = Math.floor(lg(a)); e <= Math.ceil(lg(b)); e++) { var v = Math.pow(10, e); if (v >= a * 0.999 && v <= b * 1.001) t.push([v, eng(v) + (unit || '')]); }
    return t;
  }
  function eng(v) {
    var a = Math.abs(v); if (a === 0) return '0';
    var s = [[1e9, 'G'], [1e6, 'M'], [1e3, 'k'], [1, ''], [1e-3, 'm'], [1e-6, 'µ'], [1e-9, 'n'], [1e-12, 'p'], [1e-15, 'f']];
    for (var i = 0; i < s.length; i++) if (a >= s[i][0] * 0.9995) { var x = v / s[i][0]; return (Math.abs(x) >= 100 ? x.toFixed(0) : Math.abs(x) >= 10 ? x.toFixed(1).replace(/\.0$/, '') : x.toPrecision(2).replace(/\.?0+$/, '')) + ' ' + s[i][1]; }
    return v.toExponential(1);
  }
  function fft(re, im) {                 // in place, radix 2
    var n = re.length;
    for (var i = 1, j = 0; i < n; i++) { var bit = n >> 1; for (; j & bit; bit >>= 1) j ^= bit; j ^= bit;
      if (i < j) { var t = re[i]; re[i] = re[j]; re[j] = t; t = im[i]; im[i] = im[j]; im[j] = t; } }
    for (var len = 2; len <= n; len <<= 1) {
      var ang = -2 * Math.PI / len, wr = Math.cos(ang), wi = Math.sin(ang);
      for (var s = 0; s < n; s += len) { var cr = 1, ci = 0;
        for (var k = 0; k < len / 2; k++) {
          var ar = re[s + k + len / 2] * cr - im[s + k + len / 2] * ci, ai = re[s + k + len / 2] * ci + im[s + k + len / 2] * cr;
          re[s + k + len / 2] = re[s + k] - ar; im[s + k + len / 2] = im[s + k] - ai; re[s + k] += ar; im[s + k] += ai;
          var nr = cr * wr - ci * wi; ci = cr * wi + ci * wr; cr = nr; } } }
  }
  function gauss() { var u = 1 - Math.random(), v = Math.random(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }
  function rng(seed) { var s = seed >>> 0 || 1; return function () { s ^= s << 13; s ^= s >>> 17; s ^= s << 5; return ((s >>> 0) / 4294967296); }; }
  /* sliders: <input type=range data-k="name">; map(v) converts the raw value; fmt(x) formats it */
  function bind(root, spec, onchange) {
    var st = {};
    Object.keys(spec).forEach(function (k) {
      var el = root.querySelector('[data-k="' + k + '"]'), out = root.querySelector('[data-v="' + k + '"]'), s = spec[k];
      var upd = function () { st[k] = s.map ? s.map(parseFloat(el.value)) : parseFloat(el.value); if (out) out.textContent = s.fmt ? s.fmt(st[k]) : st[k]; };
      upd(); el.addEventListener('input', function () { upd(); onchange(k); });
    });
    return st;
  }
  function seg(root, name, onchange) {      // segmented buttons with data-<name>
    var bs = root.querySelectorAll('[data-' + name + ']'), val = null;
    bs.forEach(function (b) { if (b.getAttribute('aria-pressed') === 'true') val = b.getAttribute('data-' + name);
      b.addEventListener('click', function () { bs.forEach(function (o) { o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); });
        onchange(b.getAttribute('data-' + name)); }); });
    return val;
  }
  function toggle(btn, onchange) {
    btn.addEventListener('click', function () { var on = btn.getAttribute('aria-pressed') !== 'true'; btn.setAttribute('aria-pressed', on ? 'true' : 'false'); onchange(on); });
    return btn.getAttribute('aria-pressed') === 'true';
  }
  function observe(root, draw) {
    var raf = 0, go = function () { cancelAnimationFrame(raf); raf = requestAnimationFrame(draw); };
    try { draw(); } catch (e) { if (window.console) console.error(e); }   // first draw now, not on the next frame
    if (window.ResizeObserver) new ResizeObserver(go).observe(root); else window.addEventListener('resize', go);
    return go;
  }
  window.BD = { C: C, setup: setup, frame: frame, line: line, hline: hline, vline: vline, dot: dot, logticks: logticks,
                eng: eng, fft: fft, gauss: gauss, rng: rng, bind: bind, seg: seg, toggle: toggle, observe: observe };
})();
