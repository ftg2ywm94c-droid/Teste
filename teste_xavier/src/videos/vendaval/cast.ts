// Our cast as lit flat sprites in the 3D world. Each frame every character asks for a drawing (a key + a draw call);
// the pool keeps one canvas per distinct drawing, so soldiers marching in step share canvases (7 head shapes x 4
// outfits). Characters are yaw-only billboards shaded by cardShade() (scene tint, bright floor, side gradient toward
// the sun, painted crescent in the drawing); standing ones get a soft multiply contact blob. Effects are unlit cards.
// Cards, effects and blobs live on the NOINK layer so the world ink pass never outlines their quads.
import * as THREE from "three";
import {
  Pen, bodyFront, bodySide, KID, fxNote, fxBurst, fxSplash, fxStars, fxCreak, fxRing, fxBlob, fxShadow, fxContact, fxPlank, fxDrum,
  Outfit, Expr, FrontOpts, SideOpts,
} from "./toon";
import { FPS, D0, SHOTS, V3, smooth, clamp01, easeOut, T_SINK, T_WAR, T_NOT, T_OFF, T_FRIDGE, T_HOURS, W, windAt, leanAt, BOLTS } from "./story";
import { LIGHTS } from "./lights";
import { NOINK } from "./ink";
import { cardShade, blobMaterial, CARD_K } from "./cardshade";

// ---------------- canvas pool ----------------
type Entry = { cv: HTMLCanvasElement; tex: THREE.CanvasTexture; w: number; h: number };
export type Req = { key: string; w: number; h: number; k: number; draw: (p: Pen) => void; tex?: THREE.CanvasTexture };
const makeEntry = (w: number, h: number): Entry => {
  const cv = document.createElement("canvas");
  cv.width = w; cv.height = h;
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  return { cv, tex, w, h };
};
export class Pool {
  private live = new Map<string, Entry>();
  private free: Entry[] = [];
  private reqs: Req[] = [];
  req(key: string, w: number, h: number, k: number, draw: (p: Pen) => void) {
    const r: Req = { key: `${w}x${h}|${key}`, w, h, k, draw };
    this.reqs.push(r);
    return r;
  }
  flush() {
    const want = new Map<string, Req[]>();
    for (const r of this.reqs) { const l = want.get(r.key); if (l) l.push(r); else want.set(r.key, [r]); }
    for (const [key, e] of this.live) if (!want.has(key)) { this.live.delete(key); this.free.push(e); }
    for (const [key, rs] of want) {
      let e = this.live.get(key);
      if (!e) {
        const r = rs[0], i = this.free.findIndex((x) => x.w === r.w && x.h === r.h);
        e = i >= 0 ? this.free.splice(i, 1)[0] : makeEntry(r.w, r.h);
        const g = e.cv.getContext("2d")!;
        g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, e.w, e.h); g.setTransform(r.k, 0, 0, r.k, 0, 0);
        r.draw(new Pen(g));
        e.tex.needsUpdate = true;
        this.live.set(key, e);
      }
      for (const r of rs) r.tex = e.tex;
    }
    this.reqs = [];
  }
}

// ---------------- sprite meshes ----------------
const blank = (() => { const c = document.createElement("canvas"); c.width = c.height = 2; return new THREE.CanvasTexture(c); })();
export const SU = 0.00216; // metres per design unit: 1000 units = 2.16 m
export const SU_SWING = 2.3 / 1830; // swing canvas: rope of 1830 units = 2.3 m
const BODY = (() => { const g = new THREE.PlaneGeometry(600 * SU, 1000 * SU); g.translate(0, (975 - 500) * SU, 0); return g; })();
const CARD = new THREE.PlaneGeometry(1, 1);
/** world roots that hold actors (to find the scene's sun when world.ts does not pass it) */
const ROOTS = new Set<THREE.Object3D>();

/** lit flat character: cardShade() material, receives shadows (dims to the bright floor only), casts its silhouette
 *  when world.ts says so (golden). Drawn after the contact blobs (renderOrder 1). */
export class Actor {
  mesh: THREE.Mesh; mat: THREE.MeshLambertMaterial; dmat: THREE.MeshDepthMaterial; r: Req | null = null;
  constructor(parent: THREE.Object3D, geo: THREE.BufferGeometry = BODY) {
    this.mat = cardShade(new THREE.MeshLambertMaterial({ map: blank, alphaTest: 0.5, side: THREE.DoubleSide }));
    this.mat.alphaToCoverage = false; // A2C + MSAA left 1 px sky-depth seams on blurred far cards (POST)
    this.dmat = new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking, map: blank, alphaTest: 0.5, side: THREE.DoubleSide });
    this.mesh = new THREE.Mesh(geo, this.mat);
    this.mesh.customDepthMaterial = this.dmat;
    // rim width is in output pixels: tell the card shader the render height (1920 = 1080 x 1920 frame)
    this.mesh.onBeforeRender = (r) => { const rt = r.getRenderTarget(); CARD_K.uPx.value = (rt ? rt.height : r.domElement.height) / 1920; };
    this.mesh.castShadow = false; this.mesh.receiveShadow = true; this.mesh.visible = false;
    this.mesh.rotation.order = "YXZ"; this.mesh.renderOrder = 1; this.mesh.layers.set(NOINK);
    parent.add(this.mesh);
    ROOTS.add(parent);
  }
  bind() { const t = this.r?.tex; if (t) { this.mat.map = t; this.dmat.map = t; } }
}
/** unlit effect card: hard cut-out (ink drawings), soft see-through (dust, mist) or a multiply ground blob */
export class Fx {
  mesh: THREE.Mesh; mat: THREE.MeshBasicMaterial; soft: THREE.MeshBasicMaterial; blob: THREE.MeshBasicMaterial; r: Req | null = null;
  constructor(parent: THREE.Object3D) {
    this.mat = new THREE.MeshBasicMaterial({ map: blank, alphaTest: 0.5, side: THREE.DoubleSide });
    this.mat.alphaToCoverage = false; // A2C + MSAA left 1 px sky-depth seams on blurred far cards (POST)
    this.soft = new THREE.MeshBasicMaterial({ map: blank, transparent: true, depthWrite: false, side: THREE.DoubleSide });
    this.blob = blobMaterial(blank);
    this.mesh = new THREE.Mesh(CARD, this.mat);
    this.mesh.visible = false; this.mesh.layers.set(NOINK);
    parent.add(this.mesh);
  }
  use(soft: boolean) { this.mesh.material = soft ? this.soft : this.mat; }
  bind() {
    const t = this.r?.tex;
    if (!t) return;
    if (this.r!.key.includes("|blob|")) {
      // no mipmaps: at grazing views the mip chain averages the blob with its white surround and it fades out
      if (t.generateMipmaps) { t.generateMipmaps = false; t.minFilter = THREE.LinearFilter; t.needsUpdate = true; }
      this.blob.map = t; this.mesh.material = this.blob; this.mesh.renderOrder = 0.5;
    }
    else { this.mat.map = t; this.soft.map = t; this.mesh.renderOrder = 0; }
  }
}

// ---------------- placements ----------------
export type Place = {
  key: string; draw: (p: Pen) => void; x: number; y: number; z: number;
  scale?: number; mirror?: boolean; yaw?: number; geo?: "body" | "swing"; roll?: number; size?: [number, number, number];
};
export type FxPlace = { key: string; cw: number; ch: number; draw: (p: Pen) => void; x: number; y: number; z: number; w: number; h: number; flat?: boolean; rot?: number; soft?: boolean };
/** sun = world direction TOWARD the sun (optional: when absent the scene's shadow-casting light is used) */
export type CamInfo = { pos: THREE.Vector3; right: THREE.Vector3; sun?: THREE.Vector3 };

const hh = (i: number, s = 0) => { const v = Math.sin(i * 127.1 + s * 311.7) * 43758.5453; return v - Math.floor(v); };
const q = (v: number, n = 120) => Math.round(v * n) / n;
const vOf = (i: number) => (i * 7 + (i >> 2)) % 4;
/** head-shape seed: 7 shapes, so marching soldiers in step still share canvases */
const seedOf = (i: number) => ((i * 5 + 3) % 7) + 1;
/** drawing resolution by distance: [canvas w, h, scale from the 600 x 1000 design]; sized for the 1440 x 2560 final */
const tier = (d: number): [number, number, number] =>
  d < 3.2 ? [1800, 3000, 3.0] : d < 6.5 ? [1080, 1800, 1.8] : d < 16 ? [480, 800, 0.8] : [240, 400, 0.4];

// ---------------- light ----------------
const SUN = new THREE.Vector3(0.5, 0.75, -0.4).normalize();
const tmp = new THREE.Vector3();
let LNAME: "day" | "golden" | "night" = "day";
const sunOf = (root: THREE.Object3D) => {
  let s: THREE.DirectionalLight | null = null;
  root.traverse((o) => { if (!s && o instanceof THREE.DirectionalLight && o.castShadow) s = o; });
  return s as THREE.DirectionalLight | null;
};
/** the sun of the world that is calling: the attached root whose sun target sits on this camera's view axis */
const findSun = (cam: CamInfo, out: THREE.Vector3) => {
  if (cam.sun) return out.copy(cam.sun).normalize();
  let best: THREE.DirectionalLight | null = null, err = Infinity;
  for (const r of ROOTS) {
    if (!r.parent) continue;
    const s = sunOf(r);
    if (!s) continue;
    const d = tmp.copy(s.target.position).sub(cam.pos), e = Math.abs(d.dot(cam.right)) / (d.length() || 1);
    if (e < err) { err = e; best = s; }
  }
  return best ? out.copy(best.position).sub(best.target.position).normalize() : out;
};
/** canvas angle the sun comes FROM on an upright card facing the camera, in 45-degree steps (small texture cache) */
const light2D = (cam: CamInfo, mirror: boolean) => {
  const sx = SUN.dot(cam.right) * (mirror ? -1 : 1), sy = -SUN.y;
  return Math.round(Math.atan2(sy, sx) / (Math.PI / 4)) * (Math.PI / 4);
};

/** front / side view and mirroring for someone at (x, z) walking along (dx, dz); fs = foreshortening of the walk */
const viewOf = (cam: CamInfo, x: number, z: number, dx: number, dz: number) => {
  const tx = cam.pos.x - x, tz = cam.pos.z - z, tl = Math.hypot(tx, tz) || 1;
  const c = (tx * dx + tz * dz) / tl;
  return { side: c < 0.57, mirror: dx * cam.right.x + dz * cam.right.z < 0, fs: Math.round(Math.sqrt(Math.max(0, 1 - c * c)) * 20) / 20 };
};

// ---------------- life: blinks and reaction timing ----------------
/** reference expression and action changes land 0-3 f before the word onset */
const LEAD = 2 / FPS;
/** eyelid 0 open .. 1 shut. Reference: gaps 0.5-2.3 s, 4-frame blink half / shut / shut / half, plus a blink across
 *  every expression swap (the shut frames hide the swap) */
const LID = [0.5, 1, 1, 0.5];
const SWAPS: Record<number, number[]> = { 2: [T_SINK] };
const lidAt = (t: number, i: number, swaps: number[] = []) => {
  const f = Math.round(t * FPS);
  for (const ts of swaps) { const k = f - Math.round((ts - LEAD) * FPS) + 1; if (k >= 0 && k < 4) return LID[k]; }
  let s = Math.round(-60 * hh(i, 9));
  for (let n = 0; s <= f && n < 400; n++) {
    const k = f - s;
    if (k >= 0 && k < 4) return LID[k];
    s += Math.round(15 + 54 * hh(i * 31 + n, 13)); // next blink 0.5-2.3 s later
  }
  return 0;
};
const fkey = (o: object) => JSON.stringify(o, (_k, v) => (typeof v === "number" ? q(v) : v));

type Who = { i: number; o: Outfit; okey: string };
/** one character drawing in the 600 x 1000 design space, sized by distance, lit from the scene's sun */
const person = (cam: CamInfo, who: Who, x: number, y: number, z: number, view: { side: boolean; mirror: boolean }, fo: FrontOpts, so: SideOpts, scale = 1): Place & { tierKey: string } => {
  const d = cam.pos.distanceTo(tmp.set(x, y + 1.2, z)) / scale;
  const [w, h, k] = tier(d);
  const mirror = view.side && view.mirror, light = light2D(cam, mirror), seed = seedOf(who.i);
  const f2: FrontOpts = { ...fo, light, seed }, s2: SideOpts = { ...so, light, seed };
  const key = view.side ? `S|${who.okey}|${fkey(s2)}` : `F|${who.okey}|${fkey(f2)}`;
  return {
    key, x, y, z, scale, mirror, tierKey: `${w}`,
    draw: (p) => (view.side ? bodySide(p, who.o, s2) : bodyFront(p, who.o, f2)),
    size: [w, h, k],
  };
};

/** ground shadow under a standing / sitting card (review rounds 2-4), multiply, blue-violet: a TIGHT contact pool right under
 *  the feet (~.5 on screen at the core) so nobody floats, plus by day (cards cast no real shadow) a lighter soft tail
 *  stretched AWAY from the sun, length ~1.6 m / tan(sun elevation), capped. Golden: world.ts casts real card shadows. */
const CONTACT: Record<"day" | "golden" | "night", [number, number, number]> = { day: [0.2, 0.21, 0.33], golden: [0.24, 0.2, 0.33], night: [0.08, 0.09, 0.16] };
const TAIL: [number, number, number] = [0.42, 0.44, 0.62];
const toSrgb = (v: number) => { const c = clamp01(v); return c <= 0.0031308 ? 12.92 * c : 1.055 * c ** (1 / 2.4) - 0.055; };
const hexOf = (c: [number, number, number], k: number) => "#" + c.map((v) => Math.round(255 * toSrgb(1 - (1 - v) * k)).toString(16).padStart(2, "0")).join("");
const blob = (out: Stage, x: number, y: number, z: number, sc = 1, k = 1) => {
  const hl = Math.hypot(SUN.x, SUN.z) || 1, ox = -SUN.x / hl, oz = -SUN.z / hl, rot = Math.atan2(-ox, -oz);
  if (LNAME === "day") {
    const el = Math.asin(Math.min(0.99, Math.max(0.1, SUN.y)));
    const len = Math.min(2.4, Math.max(0.5, 1.6 / Math.tan(el))) * sc, h = len + 0.55 * sc, c = 0.3 * h; // feet at v = .2 of the card
    const tc = hexOf(TAIL, k);
    out.fx.push({ key: `blob|shadow|${tc}`, cw: 128, ch: 256, draw: (p) => fxShadow(p, tc), x: x + ox * c, y: y + 0.018, z: z + oz * c,
      w: 0.72 * sc, h, flat: true, rot });
  }
  const cc = hexOf(CONTACT[LNAME], k);
  out.fx.push({ key: `blob|contact|${cc}`, cw: 128, ch: 128, draw: (p) => fxContact(p, cc), x: x + ox * 0.03 * sc, y: y + 0.022, z: z + oz * 0.03 * sc,
    w: 0.52 * sc, h: 0.4 * sc, flat: true, rot });
};

// ---------------- crowd by shot ----------------
export type Stage = { places: Place[]; fx: FxPlace[] };


// ---------------- Pisa cast ----------------
const MODERN = (v: number): Outfit => {
  const tees = ["#e2453c", "#3f6fb5", "#f3d35a", "#2f8a4f", "#f08a2c", "#7b5ac9"], hairs = ["#5a3b2a", "#2a201a", "#c9893a", "#4a3020"];
  return { jacket: tees[v % 6], pants: ["#3b5b9a", "#3b3f52", "#d9c7a0"][v % 3], boots: "#f4f1ea", hat: "hair", hair: hairs[v % 4], skin: SKINS_[v % 4] };
};
const SKINS_ = ["#ffe2c2", "#f5c9a0", "#ecd0b6", "#c99067"];
const MASON = (v: number): Outfit => ({ jacket: ["#b5653f", "#8a6a4a", "#a8724a"][v % 3], pants: "#5b4a3a", boots: "#4a3426", hat: "cap", cap: ["#e8dcc0", "#d9c7a0"][v % 2], skin: SKINS_[(v + 1) % 4], moustache: v % 3 === 1 ? "#4a3020" : undefined });
const WARRIOR = (v: number): Outfit => ({ jacket: v % 2 ? "#b8343a" : "#9c2e33", pants: "#3d4440", boots: INK_, hat: "cap", cap: "#9aa3ad", belt: "#d9c7a0", sword: true, skin: SKINS_[v % 4], moustache: v % 4 === 1 ? "#4a3426" : undefined });
const INK_ = "#241726";

/** tourists in front of the tower doing the "holding it up" pose (S1) or cheering (S5) */
const tourists = (cam: CamInfo, t: number, out: Stage, cheer: boolean) => {
  const spots: [number, number][] = cheer
    ? [[-2.6, -86.2], [-1.2, -85.4], [0.2, -86.4], [1.5, -85.2], [2.9, -86], [-0.5, -83.2], [1.9, -82.8], [-2.1, -82.6]]
    : [[-1.9, -80.6], [-0.5, -81.3], [0.8, -80.4], [-3.2, -77.4], [2.6, -77.2]];
  spots.forEach(([x, z], i) => {
    const kid = i % 4 === 2, o = kid ? KID : MODERN(i), who: Who = { i: i + 300, o, okey: kid ? "kid" : `m${i}` };
    const hop = cheer && kid ? Math.max(0, Math.sin(t * 8 + i)) * 0.18 : 0;
    const expr: Expr = cheer ? (["laugh", "grin", "laugh", "smile"] as Expr[])[i % 4] : (["grin", "smile_closed", "laugh", "grin"] as Expr[])[i % 4];
    const wave = cheer ? q(Math.sin(t * 9 + i * 1.3), 30) : 1; // S1: arm up flat against the tower
    const fo: FrontOpts = { mode: "stand", expr, wave, blink: lidAt(t, i + 300), look: cheer ? 0 : 1 };
    out.places.push(person(cam, who, x, D0 + hop, z, { side: false, mirror: false }, fo, {}, kid ? 0.72 : 1));
    blob(out, x, D0, z, kid ? 0.72 : 1, hop > 0 ? 0.6 : 1);
  });
};

/** 1178: masons at the base hammering; on "afundar" they freeze in shock */
const masons = (cam: CamInfo, t: number, out: Stage) => {
  const spots: [number, number][] = [[11.6, -28.4], [13.1, -29.4], [14.5, -28.2], [10.2, -25.5], [15.6, -25.2], [12.8, -24.6]];
  const after = t >= T_SINK - 2 / FPS;
  spots.forEach(([x, z], i) => {
    const who: Who = { i: i + 400, o: MASON(i), okey: `mason${i % 3}` };
    const k = q((Math.sin(t * 7 + i * 1.9) + 1) / 2, 15);
    const expr: Expr = after ? (i % 2 ? "shock" : "nervous") : (i % 3 === 0 ? "whistle" : "grin");
    const fo: FrontOpts = { mode: "stand", expr, prop: after ? ["hammer", 0] : ["hammer", k], blink: lidAt(t, i + 400, SWAPS[2]), look: after ? -1 : 0, facing: -1 };
    out.places.push(person(cam, who, x, D0, z, { side: false, mirror: false }, fo, {}));
    blob(out, x, D0, z);
  });
  // the shock lands with a burst at the sinking base
  if (t >= T_SINK && t < T_SINK + 0.4) {
    const u = q((t - T_SINK) / 0.4, 30);
    out.fx.push({ key: `burst${u}`, cw: 500, ch: 500, draw: (p) => fxBurst(p, u), x: 7.8, y: D0 + 0.6, z: -3.5, w: 3.2, h: 3.2 });
  }
};

/** the war: a column of soldiers marching left to right in front of the stump (side views) */
const soldiers = (cam: CamInfo, t: number, out: Stage) => {
  const t0 = SHOTS[2].a / FPS;
  for (let i = 0; i < 16; i++) {
    const row = i >> 1, lane = i & 1;
    const x = 0.5 + (t - t0) * 1.6 - row * 1.5 + (hh(i) - 0.5) * 0.1, z = -33.5 - lane * 1.3;
    const ph = (((t - t0) * 1.0) % 1 + 1) % 1;
    const view = viewOf(cam, x, z, 1, 0);
    const who: Who = { i: i + 500, o: WARRIOR(i % 4), okey: `war${i % 4}` };
    const expr: Expr = i % 3 === 0 ? "stern" : "neutral";
    const fo: FrontOpts = { phase: ph, expr, mode: "march", blink: lidAt(t, i + 500) };
    const so: SideOpts = { phase: ph, expr, mode: "march", blink: lidAt(t, i + 500), stomp: 1, stride: view.fs };
    out.places.push(person(cam, who, x, D0, z, view, fo, so));
    blob(out, x, D0, z);
  }
};

/** relógio desenhado: mostrador branco, contorno ameixa, ponteiro que gira (o tempo passando) */
const fxClock = (p: Pen, u: number) => {
  const g = p.g;
  p.ell(300, 300, 250, 250, "#fbf7ef", 14);
  for (let k = 0; k < 12; k++) { const a = (k / 12) * Math.PI * 2; g.beginPath(); g.moveTo(300 + Math.sin(a) * 200, 300 - Math.cos(a) * 200); g.lineTo(300 + Math.sin(a) * 228, 300 - Math.cos(a) * 228); g.strokeStyle = "#241726"; g.lineWidth = k % 3 ? 7 : 14; g.stroke(); }
  // arco "4 horas" preenchendo
  g.beginPath(); g.moveTo(300, 300); g.arc(300, 300, 185, -Math.PI / 2, -Math.PI / 2 + (Math.PI * 2 * 4 / 12) * u); g.closePath(); g.fillStyle = "rgba(240,120,60,0.55)"; g.fill();
  const ah = -Math.PI / 2 + (Math.PI * 2 * 4 / 12) * u, am = -Math.PI / 2 + Math.PI * 2 * 4 * u;
  for (const [a, L, w] of [[ah, 120, 20], [am, 175, 12]] as const) { g.beginPath(); g.moveTo(300, 300); g.lineTo(300 + Math.cos(a) * L, 300 + Math.sin(a) * L); g.strokeStyle = "#241726"; g.lineWidth = w; g.lineCap = "round"; g.stroke(); }
  p.ell(300, 300, 18, 18, "#241726");
};
// ---------------- vídeo 11: efeitos desenhados ----------------
const SANS = "bold %dpx 'DejaVu Sans', 'Liberation Sans', Arial, sans-serif";
const font = (g: CanvasRenderingContext2D, px: number) => { g.font = SANS.replace("%d", String(px)); g.textAlign = "center"; g.textBaseline = "middle"; };
const rr = (g: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number, fill: string, stroke = "#241726", lw = 12) => {
  g.beginPath(); g.roundRect(x, y, w, h, r); g.fillStyle = fill; g.fill(); if (lw) { g.lineWidth = lw; g.strokeStyle = stroke; g.stroke(); }
};
/** chuva: riscos diagonais finos (cartão translúcido) */
const fxRain = (p: Pen, seed: number, dense: number) => {
  const g = p.g; g.strokeStyle = "rgba(210,225,255,0.55)"; g.lineCap = "round";
  for (let i = 0; i < 160 * dense; i++) {
    const x = (hh(i, 1) * 1100 + seed * 37) % 1024, y = (hh(i, 2) * 1024 + seed * 173) % 1024, L = 40 + 50 * hh(i, 3);
    g.lineWidth = 1.5 + 2 * hh(i, 4); g.beginPath(); g.moveTo(x, y); g.lineTo(x - L * 0.18, y + L); g.stroke();
  }
};
/** raio: clarão em zigue-zague */
const fxBolt = (p: Pen) => {
  const pts: [number, number][] = [[260, 0], [220, 160], [290, 170], [200, 360], [270, 370], [150, 620]];
  p.line(pts, "#fffbe0", 26);
};
/** carne e leite com aviso */
const fxRisk = (p: Pen, warn: boolean) => {
  const g = p.g;
  // bandeja com bife
  rr(g, 40, 300, 280, 150, 30, "#f4f1ea");
  p.ell(180, 365, 110, 62, "#c9443c", 10); p.ell(150, 350, 30, 16, "#f2d0c0", 0); p.ell(210, 385, 22, 12, "#f2d0c0", 0);
  // caixa de leite
  const pts: [number, number][] = [[380, 470], [380, 200], [430, 140], [520, 140], [570, 200], [570, 470]];
  p.poly(pts, "#fbfbfb", 12); g.fillStyle = "#3f6fb5"; g.fillRect(392, 300, 166, 70); font(g, 46); g.fillStyle = "#fff"; g.fillText("LEITE", 475, 336);
  if (warn) { // triângulo de aviso
    p.poly([[600, 40], [690, 200], [510, 200]], "#f3d35a", 12); font(g, 110); g.fillStyle = "#241726"; g.fillText("!", 600, 140);
    g.strokeStyle = "rgba(226,69,60,0.9)"; g.lineWidth = 16; g.beginPath(); g.ellipse(310, 330, 300, 190, 0, 0, Math.PI * 2); g.stroke();
  }
};
/** medidor da caixa d'água: barra vertical azul que esvazia */
const fxTank = (p: Pen, lvl: number) => {
  const g = p.g;
  rr(g, 20, 20, 260, 560, 40, "#f4f1ea");
  g.fillStyle = lvl < 0.25 ? "#e2453c" : "#3e9fe0"; const h = 480 * lvl; g.fillRect(50, 560 - 30 - h, 200, h);
  g.lineWidth = 6; g.strokeStyle = "#241726"; for (let k = 1; k < 4; k++) { g.beginPath(); g.moveTo(50, 50 + k * 120); g.lineTo(110, 50 + k * 120); g.stroke(); }
  rr(g, 50, 50, 200, 480, 20, "rgba(0,0,0,0)", "#241726", 10);
};
/** gota d'água */
const fxDrop = (p: Pen) => { p.poly([[50, 0], [85, 70], [80, 100], [50, 120], [20, 100], [15, 70]], "#7cc7f2", 8); };
/** raio riscado (bomba sem energia) */
const fxNoPower = (p: Pen) => {
  const g = p.g; p.ell(150, 150, 130, 130, "#f4f1ea", 12);
  p.poly([[170, 40], [90, 170], [145, 170], [120, 260], [210, 120], [155, 120]], "#f3d35a", 9);
  g.strokeStyle = "#e2453c"; g.lineWidth = 26; g.lineCap = "round"; g.beginPath(); g.moveTo(60, 60); g.lineTo(240, 240); g.stroke();
};
/** bateria que esvazia */
const fxBattery = (p: Pen, lvl: number) => {
  const g = p.g; rr(g, 30, 60, 400, 200, 30, "#f4f1ea"); rr(g, 430, 120, 40, 80, 10, "#241726", "#241726", 0);
  g.fillStyle = lvl > 0.5 ? "#2f8a4f" : lvl > 0.2 ? "#f08a2c" : "#e2453c"; g.fillRect(55, 85, 350 * lvl, 150);
};
/** ondas de sinal saindo da antena */
const fxSignal = (p: Pen, ph: number, off: boolean) => {
  const g = p.g; g.lineCap = "round";
  for (let k = 0; k < 3; k++) {
    const r = 70 + k * 70 + ph * 70; if (r > 300) continue;
    g.strokeStyle = off ? "rgba(140,140,150,0.5)" : `rgba(255,243,176,${1 - r / 300})`; g.lineWidth = 18;
    for (const s of [-1, 1]) { g.beginPath(); g.arc(320, 320, r, s > 0 ? -0.6 : Math.PI - 0.6, s > 0 ? 0.6 : Math.PI + 0.6); g.stroke(); }
  }
  if (off) { g.strokeStyle = "#e2453c"; g.lineWidth = 30; g.beginPath(); g.moveTo(140, 140); g.lineTo(500, 500); g.stroke(); }
};
/** celular (frente): tela com conteúdo */
const fxPhone = (p: Pen, screen: "nosignal" | "lowbat" | "flash" | "msg" | "radio" | "charge" | "home", u = 0) => {
  const g = p.g;
  rr(g, 20, 20, 360, 720, 60, "#2b2f3a", "#241726", 14);
  const sc = screen === "flash" ? "#fffbe8" : "#10223f"; rr(g, 45, 60, 310, 640, 36, sc, sc, 0);
  font(g, 40); g.fillStyle = "#fff";
  if (screen === "nosignal") { g.fillStyle = "#f3d35a"; g.fillText("SEM", 200, 330); g.fillText("SINAL", 200, 380);
    g.strokeStyle = "#e2453c"; g.lineWidth = 12; for (let k = 0; k < 4; k++) { g.beginPath(); g.moveTo(130 + k * 40, 280); g.lineTo(130 + k * 40, 280 - 20 - k * 22); g.stroke(); } }
  if (screen === "lowbat" || screen === "charge") {
    rr(g, 110, 300, 170, 90, 16, "rgba(0,0,0,0)", "#fff", 10); rr(g, 280, 325, 16, 40, 4, "#fff", "#fff", 0);
    const lv = screen === "lowbat" ? 0.08 : 0.08 + 0.6 * u; g.fillStyle = lv < 0.2 ? "#e2453c" : "#3ccf7a"; g.fillRect(122, 312, 146 * lv, 66);
    g.fillStyle = "#fff"; g.fillText(screen === "lowbat" ? "5%" : "⚡", 200, 450);
  }
  if (screen === "msg") { rr(g, 70, 380, 260, 110, 30, "#3ccf7a", "#241726", 0); g.fillStyle = "#10223f"; font(g, 46); g.fillText("Tô bem!", 200, 435); }
  if (screen === "radio") { g.strokeStyle = "#f3d35a"; g.lineWidth = 10; for (let k = 0; k < 3; k++) { g.beginPath(); g.arc(200, 400, 40 + k * 40, -2.4, -0.7); g.stroke(); } font(g, 40); g.fillStyle = "#fff"; g.fillText("RÁDIO", 200, 480); }
  rr(g, 160, 30, 80, 16, 8, "#111", "#111", 0);
};
/** celular (costas): câmera no canto, sem logo; power bank opcional encaixado */
const fxPhoneBack = (p: Pen) => {
  const g = p.g;
  rr(g, 20, 20, 360, 720, 60, "#d9dde4", "#241726", 14);
  rr(g, 50, 50, 140, 140, 34, "#bfc5ce", "#241726", 8); p.ell(95, 95, 26, 26, "#241726", 6); p.ell(150, 145, 26, 26, "#241726", 6);
};
/** power bank magnético: retângulo branco arredondado, anel magnético, LEDs */
const fxBank = (p: Pen, ring: number) => {
  const g = p.g;
  rr(g, 20, 20, 280, 420, 50, "#f7f7f5", "#241726", 14);
  g.strokeStyle = ring > 0 ? `rgba(60,207,122,${0.4 + 0.6 * ring})` : "#c9ccd2"; g.lineWidth = 14; g.beginPath(); g.arc(160, 210, 95, 0, Math.PI * 2); g.stroke();
  for (let k = 0; k < 4; k++) p.ell(115 + k * 30, 390, 9, 9, ring > 0 && k < 1 + Math.floor(ring * 3.99) ? "#3ccf7a" : "#9aa3ad", 0);
};
/** onda de lanterna (cone de luz) */
const fxBeam = (p: Pen) => {
  const g = p.g, gr = g.createLinearGradient(0, 512, 1024, 512);
  gr.addColorStop(0, "rgba(255,250,220,0.85)"); gr.addColorStop(1, "rgba(255,250,220,0)");
  g.fillStyle = gr; g.beginPath(); g.moveTo(0, 470); g.lineTo(1024, 150); g.lineTo(1024, 874); g.lineTo(0, 554); g.closePath(); g.fill();
};
/** maquininha de cartão */
const fxCardMachine = (p: Pen, nosig: boolean) => {
  const g = p.g;
  rr(g, 20, 20, 300, 520, 50, "#3b3f52", "#241726", 14);
  rr(g, 50, 60, 240, 170, 20, nosig ? "#2a1a1a" : "#cfe8d6", "#241726", 6);
  font(g, 32); g.fillStyle = nosig ? "#ff6a5a" : "#10223f"; g.fillText(nosig ? "SEM" : "VALOR", 170, 120); g.fillText(nosig ? "SINAL" : "R$ 23,90", 170, 170);
  for (let r = 0; r < 4; r++) for (let c = 0; c < 3; c++) rr(g, 60 + c * 78, 260 + r * 62, 62, 46, 10, r === 3 && c === 2 ? "#2f8a4f" : r === 3 && c === 0 ? "#e2453c" : "#e9e6df", "#241726", 4);
};
/** "Pix" girando sem completar, depois X vermelho */
const fxPix = (p: Pen, ang: number, fail: boolean) => {
  const g = p.g; rr(g, 20, 20, 460, 200, 40, "#f4f1ea");
  font(g, 70); g.fillStyle = "#241726"; g.fillText("Pix", 150, 122);
  if (!fail) { g.strokeStyle = "#3aa89a"; g.lineWidth = 16; g.lineCap = "round"; g.beginPath(); g.arc(340, 120, 55, ang, ang + 4.2); g.stroke(); }
  else { g.strokeStyle = "#e2453c"; g.lineWidth = 22; g.lineCap = "round"; g.beginPath(); g.moveTo(295, 75); g.lineTo(385, 165); g.moveTo(385, 75); g.lineTo(295, 165); g.stroke(); }
};

// ---------------- vídeo 12: o vendaval ----------------
/** tela do celular para o alerta: 0 só o aviso piscando, 1 + "DEFESA CIVIL", 2 + "ALERTA SEVERO", 3 + vendaval/90 km/h */
const fxAlert = (p: Pen, stage: number, hot: boolean, silent: boolean) => {
  const g = p.g;
  rr(g, 20, 20, 360, 720, 60, "#2b2f3a", "#241726", 14);
  const gr = g.createLinearGradient(0, 60, 0, 700); gr.addColorStop(0, hot ? "#e2453c" : "#9c2420"); gr.addColorStop(1, hot ? "#9c2420" : "#5a1414");
  g.save(); g.beginPath(); g.roundRect(45, 60, 310, 640, 36); g.clip(); g.fillStyle = gr; g.fillRect(45, 60, 310, 640); g.restore();
  p.poly([[200, 110], [270, 235], [130, 235]], "#f3d35a", 10); font(g, 86); g.fillStyle = "#241726"; g.fillText("!", 200, 192);
  g.fillStyle = "#fff";
  if (stage >= 1) { font(g, 36); g.fillText("DEFESA CIVIL", 200, 290); }
  if (stage >= 2) { rr(g, 58, 320, 284, 70, 18, "#fff", "#fff", 0); font(g, 29); g.fillStyle = "#c22f28"; g.fillText("ALERTA SEVERO", 200, 356); }
  if (stage >= 3) { g.fillStyle = "#fff"; font(g, 46); g.fillText("VENDAVAL", 200, 440); font(g, 27); g.fillText("rajadas acima de", 200, 500); font(g, 54); g.fillStyle = "#f3d35a"; g.fillText("90 km/h", 200, 560); }
  if (silent) { // sino cortado = modo silencioso
    rr(g, 255, 620, 80, 60, 16, "rgba(0,0,0,0.35)", "#fff", 0);
    p.poly([[278, 666], [282, 640], [295, 630], [308, 640], [312, 666]], "#fff", 0); g.strokeStyle = "#fff"; g.lineWidth = 6; g.beginPath(); g.moveTo(268, 680); g.lineTo(322, 626); g.stroke();
  }
  rr(g, 160, 30, 80, 16, 8, "#111", "#111", 0);
};
/** celular com bateria em 8 % */
const fxLow8 = (p: Pen, hot: boolean) => {
  const g = p.g;
  rr(g, 20, 20, 360, 720, 60, "#2b2f3a", "#241726", 14); rr(g, 45, 60, 310, 640, 36, "#10223f", "#10223f", 0);
  rr(g, 100, 290, 190, 100, 18, "rgba(0,0,0,0)", "#fff", 10); rr(g, 290, 318, 18, 44, 4, "#fff", "#fff", 0);
  g.fillStyle = hot ? "#ff5a4a" : "#e2453c"; g.fillRect(113, 303, 164 * 0.08, 74);
  font(g, 92); g.fillStyle = hot ? "#ff5a4a" : "#ffffff"; g.fillText("8%", 200, 480);
  rr(g, 160, 30, 80, 16, 8, "#111", "#111", 0);
};
/** moldura da janela vista de dentro (parede escura, vidro vazado, cortinas): cartão colado na frente da câmera */
const fxWindow = (p: Pen) => {
  const g = p.g, W0 = 540, H0 = 960;
  g.fillStyle = "#2a2238"; g.fillRect(0, 0, W0, H0);
  g.clearRect(70, 170, 400, 560);
  g.fillStyle = "#efe6d6"; for (const [x, y, w, h] of [[56, 156, 428, 18], [56, 726, 428, 22], [56, 156, 18, 592], [466, 156, 18, 592], [262, 170, 16, 560], [70, 440, 400, 14]]) g.fillRect(x, y, w, h);
  g.strokeStyle = "#241726"; g.lineWidth = 6; g.strokeRect(56, 156, 428, 592);
  g.fillStyle = "#d9cdb8"; g.fillRect(30, 748, 480, 40); g.strokeRect(30, 748, 480, 40); // peitoril
  g.fillStyle = "#7a2e3a"; // cortinas
  g.beginPath(); g.moveTo(0, 120); g.lineTo(120, 120); g.quadraticCurveTo(70, 450, 110, 820); g.lineTo(0, 820); g.closePath(); g.fill(); g.stroke();
  g.beginPath(); g.moveTo(540, 120); g.lineTo(420, 120); g.quadraticCurveTo(470, 450, 430, 820); g.lineTo(540, 820); g.closePath(); g.fill(); g.stroke();
  g.fillStyle = "#3a2c22"; g.fillRect(0, 104, 540, 18);
};
/** folhas soltas (cartão translúcido) */
const fxLeaves = (p: Pen, seed: number, n: number) => {
  const g = p.g;
  for (let i = 0; i < n; i++) {
    const x = (hh(i + seed * 13, 1) * 1024), y = (hh(i + seed * 7, 2) * 1024), a = hh(i, 3) * 6.28, r = 10 + 14 * hh(i, 4);
    g.save(); g.translate(x, y); g.rotate(a + seed * 0.7);
    g.fillStyle = ["#4f9a43", "#62ae4c", "#8a6a3a", "#3e7e38"][i % 4]; g.beginPath(); g.ellipse(0, 0, r, r * 0.45, 0, 0, 7); g.fill();
    g.strokeStyle = "rgba(36,23,38,0.8)"; g.lineWidth = 2; g.stroke(); g.restore();
  }
};
/** rajadas de vento: riscos brancos curvos */
const fxGust = (p: Pen, seed: number) => {
  const g = p.g; g.lineCap = "round";
  for (let i = 0; i < 9; i++) {
    const y = 80 + hh(i, seed) * 860, x = hh(i, seed + 1) * 300, L = 300 + 400 * hh(i, seed + 2), c = (hh(i, seed + 3) - 0.5) * 120;
    g.strokeStyle = `rgba(235,242,255,${0.25 + 0.35 * hh(i, 5)})`; g.lineWidth = 3 + 5 * hh(i, 6);
    g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + L / 2, y + c, x + L, y + c * 0.3); g.stroke();
  }
};
/** telha de barro voando */
const fxTile = (p: Pen) => { p.poly([[20, 60], [60, 20], [240, 30], [280, 80], [250, 130], [70, 120]], "#c4643c", 10); p.stroke([[80, 50], [230, 60]], 6, "#8e4026"); p.stroke([[75, 90], [240, 98]], 6, "#8e4026"); };

const YOU: Who = { i: 900, o: MODERN(1), okey: "you" };
const fwdOf = (cam: CamInfo) => { const x = cam.right.z, z = -cam.right.x, n = Math.hypot(x, z) || 1; return [x / n, z / n]; };
/** chuva em três camadas diante da câmera (dense 0..1.4) */
const rainCam = (cam: CamInfo, t: number, out: Stage, dense = 1) => {
  const f = Math.round(t * FPS), [fx, fz] = fwdOf(cam);
  [[1.4, 1.9, 0.6], [3.4, 4.2, 1], [8, 9.5, 1.4]].forEach(([d, w, dn], k) => {
    const sd = (f * 3 + k * 2) % 8;
    out.fx.push({ key: `rain${k}_${sd}_${dense}`, cw: 1024, ch: 1024, draw: (p) => fxRain(p, sd + k * 11, dn * dense), soft: true,
      x: cam.pos.x + fx * d, y: cam.pos.y + (k - 1) * 0.3, z: cam.pos.z + fz * d, w, h: w * 1.8, rot: -0.25 });
  });
};
/** folhas e rajadas atravessando a tela (vento para +x do mundo) */
const windCam = (cam: CamInfo, t: number, out: Stage, w: number) => {
  if (w < 0.05) return;
  const f = Math.round(t * FPS), [fx, fz] = fwdOf(cam);
  for (let k = 0; k < 3; k++) {
    const d = 2.2 + k * 2.4, u = ((t * (0.9 + 0.5 * w) + k * 0.37) % 1), side = (u - 0.5) * (2.5 + k * 1.6);
    out.fx.push({ key: `lv${k}_${f % 6}`, cw: 1024, ch: 1024, draw: (p) => fxLeaves(p, (f % 6) + k * 5, Math.round(10 + 22 * w)), soft: true,
      x: cam.pos.x + fx * d + side * cam.right.x, y: cam.pos.y + 0.3 - k * 0.2 + 0.4 * Math.sin(u * 6), z: cam.pos.z + fz * d + side * cam.right.z, w: 1.6 + k, h: 1.6 + k });
  }
  if (w > 0.3) { const sd = Math.floor(t * 10) % 5;
    out.fx.push({ key: `gust${sd}`, cw: 1024, ch: 1024, draw: (p) => fxGust(p, sd * 3 + 1), soft: true, x: cam.pos.x + fx * 3, y: cam.pos.y, z: cam.pos.z + fz * 3, w: 4.2, h: 4.2, rot: -0.08 }); }
};
/** raio no céu nos relâmpagos */
const boltSky = (cam: CamInfo, t: number, out: Stage) => {
  const [fx, fz] = fwdOf(cam);
  for (const b of BOLTS) if (t >= b && t < b + 0.17)
    out.fx.push({ key: "bolt", cw: 400, ch: 640, draw: fxBolt, x: cam.pos.x + fx * 60 + cam.right.x * 12, y: 26, z: cam.pos.z + fz * 60 + cam.right.z * 12, w: 9, h: 14 });
};
const phoneSmall = (out: Stage, key: string, draw: (p: Pen) => void, pop: number, jx = 0) =>
  out.fx.push({ key: `${key}${pop}`, cw: 400, ch: 760, draw, x: 600.32 + jx, y: D0 + 1.1, z: 2.35, w: 0.2 * pop, h: 0.38 * pop });
const buzz = (t: number, a: number, b: number) => (t >= a && t < b ? 0.012 * Math.sign(Math.sin(t * 90)) * ((t - a) % 0.9 < 0.55 ? 1 : 0) : 0);
const alertStage = (t: number) => (t >= W.vendaval - 0.05 ? 3 : t >= W.alerta - 0.05 ? 2 : t >= W.defesa - 0.05 ? 1 : 0);

const vendaval = (id: number, cam: CamInfo, t: number, out: Stage) => {
  const c = SHOTS[id - 1].crowd, w = windAt(id, t), hot = Math.floor(t * 2.5) % 2 === 0;
  const seat = (expr: Expr, look = 0) => out.places.push(person(cam, YOU, 600.0, D0 + 0.33, 2.62, { side: false, mirror: false }, { mode: "sit", expr, blink: lidAt(t, 900, [W.dispara, W.estalo]), look }, {}));
  switch (c) {
    case "v_alarm": {
      seat(t >= W.dispara + 1.2 ? "nervous" : t >= W.dispara - 0.07 ? "shock" : "smile_closed", t >= W.dispara ? 1 : 0);
      if (t >= W.celular - 0.1) { const pop = q(easeOut((t - W.celular + 0.1) / 0.3), 20), sil = t >= W.silencioso - 0.05;
        phoneSmall(out, `al${hot}${sil}${q(buzz(t, W.dispara, 99), 200)}`, (pp) => fxAlert(pp, 0, hot, sil), pop, buzz(t, W.dispara, 99)); }
      break;
    }
    case "v_phone": {
      seat("nervous", 0);
      const st = alertStage(t), jx = buzz(t, 0, 99) * 1.5;
      out.fx.push({ key: `alertBig${st}${hot}${q(jx, 200)}`, cw: 400, ch: 760, draw: (pp) => fxAlert(pp, st, hot, true), x: 600.0 + jx, y: D0 + 1.2, z: 1.9, w: 0.42, h: 0.8 });
      break;
    }
    case "v_window": {
      const [fx, fz] = fwdOf(cam);
      if (id === 9) { rainCam(cam, t, out, 1.2); windCam(cam, t, out, w); boltSky(cam, t, out);
        if (t >= W.telha + 0.15 && t < W.voando + 0.9) { const u = (t - W.telha - 0.15) / (W.voando + 0.75 - W.telha);
          out.fx.push({ key: "tile", cw: 300, ch: 150, draw: fxTile, x: -9.5 + 12 * u, y: 4.6 - 2.2 * u + 0.5 * Math.sin(u * 9), z: 3.5, w: 0.9, h: 0.45, rot: u * 9 }); } }
      out.fx.push({ key: "win", cw: 540, ch: 960, draw: fxWindow, x: cam.pos.x + fx * 0.55, y: cam.pos.y - 0.008, z: cam.pos.z + fz * 0.55, w: 0.42, h: 0.75 });
      break;
    }
    case "v_street": { windCam(cam, t, out, w); if (w > 0.55) { rainCam(cam, t, out, (w - 0.4) * 1.6); boltSky(cam, t, out); } break; }
    case "v_door": {
      for (let k = 0; k < 4; k++) { const u = ((t * 1.6 + k / 4) % 1);
        out.fx.push({ key: `dg${k % 2}`, cw: 1024, ch: 1024, draw: (pp) => fxGust(pp, 7 + k % 2), soft: true, flat: true, x: 594.1 + (k - 1.5) * 0.14, y: D0 + 0.05 + 0.01 * k, z: 3.5 - u * 1.2, w: 1.1, h: 0.7, rot: Math.PI / 2 });
        out.fx.push({ key: `dl${k}`, cw: 1024, ch: 1024, draw: (pp) => fxLeaves(pp, k + 20, 3), soft: true, x: 594.1 + (k - 1.5) * 0.18, y: D0 + 0.05 + 0.25 * u, z: 3.86 - u * 1.4, w: 0.5, h: 0.5 }); }
      break;
    }
    case "v_lamp": seat(t >= W.pisca ? "nervous" : "neutral", -1); break;
    case "v_dark": {
      seat(t >= W.estalo - 0.07 ? "shock" : "nervous", t >= W.estalo ? 1 : 0);
      phoneSmall(out, "dk", (pp) => fxPhone(pp, "home"), 1);
      break;
    }
    case "v_tree": case "v_lean": case "v_choice": {
      rainCam(cam, t, out, 1.1); windCam(cam, t, out, w); boltSky(cam, t, out);
      const L = leanAt(id, t);
      if (L > 0.01 && (id === 12 || id === 13)) { const u = q((t * 3) % 1, 10);
        out.fx.push({ key: `creak${u}`, cw: 300, ch: 300, draw: (pp) => fxCreak(pp, u), x: 3.5 + 0.9, y: D0 + 1.4, z: 9.0 + 0.2, w: 1.6, h: 1.6 }); }
      break;
    }
    case "v_lowbat": {
      seat("pained", 0);
      out.fx.push({ key: `low8${hot}`, cw: 400, ch: 760, draw: (pp) => fxLow8(pp, hot), x: 600.0, y: D0 + 1.2, z: 1.9, w: 0.42, h: 0.8 });
      break;
    }
    case "v_runA": {
      rainCam(cam, t, out, 1.1); windCam(cam, t, out, w); boltSky(cam, t, out);
      const u = clamp01((t - W.sai + 0.2) / 2.6), z = 11.6 - 5.4 * u, ph = (t * 2.6) % 1;
      out.places.push(person(cam, YOU, 0.3, D0, z, { side: false, mirror: false }, { mode: u > 0 && u < 1 ? "march" : "stand", phase: ph, lift: 90, expr: "shock", blink: lidAt(t, 900), look: 0 }, {}));
      blob(out, 0.3, D0, z);
      break;
    }
    case "v_bath": {
      out.places.push(person(cam, YOU, 800.0, D0, 2.4, { side: false, mirror: false }, { mode: "stand", expr: t >= W.tranca ? "stern" : "nervous", blink: lidAt(t, 900, [W.tranca]), look: 0 }, {}));
      blob(out, 800.0, D0, 2.4);
      out.fx.push({ key: "bph", cw: 400, ch: 760, draw: (pp) => fxPhone(pp, "flash"), x: 800.28, y: D0 + 1.05, z: 2.25, w: 0.16, h: 0.3 });
      break;
    }
    case "v_cta": {
      out.places.push(person(cam, YOU, 0.2, D0, 10.4, { side: false, mirror: false }, { mode: "stand", expr: "grin", wave: q(Math.sin(t * 8), 30), blink: lidAt(t, 900), look: 0 }, {}));
      blob(out, 0.2, D0, 10.4);
      break;
    }
  }
};

/** everything with a face in shot `id` at time t */
export const stage = (id: number, t: number, cam: CamInfo): Stage => {
  const out: Stage = { places: [], fx: [] };
  const s = SHOTS[id - 1];
  LNAME = s.light;
  findSun(cam, SUN);
  if (s.crowd === "tourists") tourists(cam, t, out, false);
  if (s.crowd === "cheer") tourists(cam, t, out, true);
  if (s.crowd === "masons") masons(cam, t, out);
  if (s.crowd === "soldiers") soldiers(cam, t, out);
  if (s.crowd.startsWith("v_")) vendaval(id, cam, t, out);
  return out;
};
export { FPS, T_WAR, T_NOT, smooth, clamp01 };
