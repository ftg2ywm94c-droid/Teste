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
import { FPS, D0, SHOTS, V3, smooth, clamp01, easeOut, T_SINK, T_WAR, T_NOT, T_OFF, T_FRIDGE, T_HOURS, W, windAt, leanAt, BOLTS, sparkAt, PHONE_NEAR, fallen, doorAt, sirenX, sirenK, sirenPulse, darkAt, KNOCKS, tvOn, ledOn, lampOn, barkAt, vibAt } from "./story";
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
  if (stage >= 1) { font(g, 40); g.fillText("DEFESA CIVIL", 200, 286); }
  if (stage >= 2) { rr(g, 58, 316, 284, 140, 22, "#fff", "#241726", 6); font(g, 60); g.fillStyle = "#c22f28"; g.fillText("ALERTA", 200, 356); g.fillText("SEVERO", 200, 418); }
  if (stage >= 3) { g.fillStyle = "#fff"; font(g, 50); g.fillText("VENDAVAL", 200, 500); font(g, 28); g.fillText("rajadas acima de", 200, 548); font(g, 56); g.fillStyle = "#f3d35a"; g.fillText("90 km/h", 200, 600); }
  if (silent) { // sino cortado = modo silencioso
    rr(g, 262, 638, 70, 52, 14, "rgba(0,0,0,0.35)", "#fff", 0);
    p.poly([[282, 678], [286, 655], [297, 646], [308, 655], [312, 678]], "#fff", 0); g.strokeStyle = "#fff"; g.lineWidth = 6; g.beginPath(); g.moveTo(272, 688); g.lineTo(322, 642); g.stroke();
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
// ================= vídeo 14: Vendaval · Ep. 2 =================
const hi = (p: Pen, k: number, fn: (g: CanvasRenderingContext2D) => void) => { const g = p.g; g.save(); g.scale(k, k); fn(g); g.restore(); };
type Scr = "low8" | "vizinha" | "193" | "call" | "low3" | "ended" | "off";
/** telas do celular: 8 % com a lanterna ligada, a vizinha ligando (6 %), chamando 193 */
const fxCel = (p: Pen, scr: Scr, u: number, sec = 0) => hi(p, 2, (g) => {
  rr(g, 20, 20, 360, 720, 60, "#2b2f3a", "#241726", 14);
  g.save(); g.beginPath(); g.roundRect(45, 60, 310, 640, 36); g.clip();
  const gr = g.createLinearGradient(0, 60, 0, 700); gr.addColorStop(0, scr === "193" ? "#5a1414" : "#1b2f5a"); gr.addColorStop(1, "#0b1226"); g.fillStyle = gr; g.fillRect(45, 60, 310, 640);
  if (scr === "off") { g.fillStyle = "#05060a"; g.fillRect(45, 60, 310, 640); const rf = g.createLinearGradient(45, 60, 355, 700); rf.addColorStop(0, "rgba(120,140,190,0.10)"); rf.addColorStop(0.45, "rgba(120,140,190,0)"); g.fillStyle = rf; g.fillRect(45, 60, 310, 640); }
  const pct = scr === "low8" ? "8%" : ["low3", "ended"].includes(scr) ? "3%" : "6%";
  if (scr !== "off") {
  font(g, 22); g.textAlign = "right"; g.fillStyle = "#ff5a4a"; g.fillText(pct, 330, 92); g.textAlign = "center";
  rr(g, 262, 82, 34, 18, 4, "rgba(0,0,0,0)", "#ff5a4a", 3); g.fillStyle = "#ff5a4a"; g.fillRect(265, 85, 4, 12);
  if (scr === "low8") {
    rr(g, 100, 150, 190, 100, 18, "rgba(0,0,0,0)", "#fff", 10); rr(g, 290, 178, 18, 44, 4, "#fff", "#fff", 0);
    g.fillStyle = "#ff5a4a"; g.fillRect(113, 163, 164 * 0.08, 74); font(g, 92); g.fillStyle = "#ff5a4a"; g.fillText("8%", 200, 320);
    rr(g, 110, 400, 180, 150, 34, "#f3d35a", "#241726", 0);   // lanterna ligada
    g.fillStyle = "#241726"; g.beginPath(); g.moveTo(178, 420); g.lineTo(222, 420); g.lineTo(212, 450); g.lineTo(212, 495); g.lineTo(188, 495); g.lineTo(188, 450); g.closePath(); g.fill();
    font(g, 22); g.fillStyle = "#241726"; g.fillText("lanterna", 200, 525);
  }
  if (scr === "vizinha") {
    font(g, 22); g.fillStyle = "#9fb4e0"; g.fillText("chamada recebida", 200, 140);
    for (let i = 0; i < 3; i++) { const r = 60 + ((u + i / 3) % 1) * 80; g.strokeStyle = `rgba(160,200,255,${0.6 * (1 - ((u + i / 3) % 1))})`; g.lineWidth = 6; g.beginPath(); g.arc(200, 270, r, 0, 7); g.stroke(); }
    p.ell(200, 270, 58, 58, "#c97b9a", 0); font(g, 60); g.fillStyle = "#fff"; g.fillText("V", 200, 274);
    font(g, 48); g.fillText("Vizinha", 200, 400); font(g, 24); g.fillStyle = "#9fb4e0"; g.fillText("casa ao lado", 200, 446);
    p.ell(120, 600, 44, 44, "#e2453c", 0); p.ell(280, 600, 44, 44, "#3ccf7a", 0);
    g.strokeStyle = "#fff"; g.lineWidth = 9; g.lineCap = "round";
    g.beginPath(); g.moveTo(100, 604); g.quadraticCurveTo(120, 590, 140, 604); g.stroke(); g.beginPath(); g.moveTo(262, 596); g.quadraticCurveTo(280, 584, 298, 596); g.stroke();
  }
  if (scr === "193") {
    font(g, 26); g.fillStyle = "#ffd0c8"; g.fillText("chamando...", 200, 150);
    font(g, 120); g.fillStyle = "#fff"; g.fillText("193", 200, 290); font(g, 30); g.fillText("Bombeiros", 200, 370);
    for (let i = 0; i < 3; i++) { const k = (u * 3 + i) % 3 < 1 ? 1 : 0.35; p.ell(160 + i * 40, 440, 9, 9, `rgba(255,255,255,${k})`, 0); }
    p.ell(200, 600, 48, 48, "#e2453c", 0); g.strokeStyle = "#fff"; g.lineWidth = 9; g.lineCap = "round"; g.beginPath(); g.moveTo(178, 604); g.quadraticCurveTo(200, 590, 222, 604); g.stroke();
  }
  if (scr === "call" || scr === "low3" || scr === "ended") {   // em chamada com o 193: cronômetro, onda da voz, botão de desligar
    const mm = String(Math.floor(sec / 60)).padStart(2, "0"), ss = String(Math.floor(sec % 60)).padStart(2, "0");
    font(g, 26); g.fillStyle = scr === "ended" ? "#c8c8d0" : "#7be0a0"; g.fillText(scr === "ended" ? "chamada encerrada" : "em chamada", 200, 150);
    font(g, 100); g.fillStyle = "#fff"; g.fillText("193", 200, 270); font(g, 30); g.fillText("Bombeiros", 200, 340);
    font(g, 40); g.fillStyle = scr === "ended" ? "#c8c8d0" : "#fff"; g.fillText(`${mm}:${ss}`, 200, 400);
    if (scr !== "ended") for (let i = 0; i < 9; i++) { const h = 10 + 46 * Math.abs(Math.sin(u * 6.28 + i * 1.3)) * (0.4 + 0.6 * Math.abs(Math.sin(i * 2.1 + u * 3))); rr(g, 104 + i * 22, 470 - h / 2, 12, h, 6, "#9fd8ff", "#9fd8ff", 0); }
    if (scr === "low3") { rr(g, 70, 515, 260, 50, 16, "#e2453c", "#241726", 0); font(g, 24); g.fillStyle = "#fff"; g.fillText("bateria fraca · 3%", 200, 541); }
    p.ell(200, 625, 44, 44, scr === "ended" ? "#6b6b74" : "#e2453c", 0); g.strokeStyle = "#fff"; g.lineWidth = 9; g.lineCap = "round"; g.beginPath(); g.moveTo(178, 629); g.quadraticCurveTo(200, 615, 222, 629); g.stroke();
  }
  }
  g.restore(); rr(g, 160, 30, 80, 16, 8, "#111", "#111", 0);
  // a sua mão segurando
  const sk = "#f5c9a0", ink = "#241726"; g.lineWidth = 7; g.strokeStyle = ink; g.lineJoin = "round";
  g.fillStyle = sk; g.beginPath(); g.moveTo(-10, 760); g.quadraticCurveTo(10, 610, 70, 600); g.lineTo(330, 600); g.quadraticCurveTo(400, 620, 410, 760); g.closePath(); g.fill(); g.stroke();
  for (let i = 0; i < 4; i++) rr(g, 4, 400 + i * 52, 46, 44, 20, i % 2 ? sk : "#f8d6b4", ink, 7);
  g.fillStyle = sk; g.beginPath(); g.moveTo(372, 660); g.quadraticCurveTo(388, 560, 352, 500); g.quadraticCurveTo(330, 486, 318, 512); g.quadraticCurveTo(330, 580, 322, 650); g.closePath(); g.fill(); g.stroke();
});
const fxGlow = (p: Pen, col: string) => { const g = p.g, gr = g.createRadialGradient(128, 128, 6, 128, 128, 128); gr.addColorStop(0, col); gr.addColorStop(1, "rgba(0,0,0,0)"); g.fillStyle = gr; g.fillRect(0, 0, 256, 256); };
const fxSpark = (p: Pen, seed: number) => { const g = p.g; g.lineCap = "round";
  for (let i = 0; i < 14; i++) { const a = hh(i, seed) * 6.28, L = 40 + 80 * hh(i, seed + 1); g.strokeStyle = i % 3 ? "#fff6c8" : "#9fd0ff"; g.lineWidth = 3 + 3 * hh(i, seed + 2);
    g.beginPath(); g.moveTo(128 + Math.cos(a) * 8, 128 + Math.sin(a) * 8); g.lineTo(128 + Math.cos(a) * L, 128 + Math.sin(a) * L); g.stroke(); }
  fxGlow(p, "rgba(220,235,255,0.95)"); };
const fxDrip = (p: Pen) => { const g = p.g; g.fillStyle = "rgba(170,205,255,0.95)"; g.beginPath(); g.moveTo(32, 2); g.quadraticCurveTo(60, 60, 32, 62); g.quadraticCurveTo(4, 60, 32, 2); g.fill(); g.strokeStyle = "#241726"; g.lineWidth = 3; g.stroke(); };
const fxRipple = (p: Pen, u: number) => { const g = p.g; g.strokeStyle = `rgba(190,215,255,${0.9 * (1 - u)})`; g.lineWidth = 5; g.beginPath(); g.ellipse(64, 64, 10 + 50 * u, 10 + 50 * u, 0, 0, 7); g.stroke(); };
/** fumaça: tufos irregulares (vários círculos esfumados sobrepostos), cinza escuro */
const fxPuff = (p: Pen) => { const g = p.g;
  for (let i = 0; i < 9; i++) { const x = 70 + 116 * hh(i, 41), y = 70 + 116 * hh(i, 42), r = 30 + 40 * hh(i, 43), gr = g.createRadialGradient(x, y, 2, x, y, r);
    gr.addColorStop(0, "rgba(70,66,74,0.55)"); gr.addColorStop(1, "rgba(70,66,74,0)"); g.fillStyle = gr; g.fillRect(0, 0, 256, 256); } };
/** fumaça clara e translúcida (aditiva) para a fresta da porta: sem contorno, em fiapos */
const fxPuffL = (p: Pen) => { const g = p.g;
  for (let i = 0; i < 12; i++) { const x = 60 + 136 * hh(i, 51), y = 60 + 136 * hh(i, 52), r = 22 + 46 * hh(i, 53), gr = g.createRadialGradient(x, y, 2, x, y, r);
    gr.addColorStop(0, "rgba(150,150,165,0.32)"); gr.addColorStop(1, "rgba(150,150,165,0)"); g.fillStyle = gr; g.fillRect(0, 0, 256, 256); } };
const fxDust = (p: Pen, seed: number) => { const g = p.g; for (let i = 0; i < 70; i++) { g.fillStyle = `rgba(220,210,190,${0.4 + 0.5 * hh(i, seed)})`; const r = 2 + 4 * hh(i, seed + 3); g.fillRect(hh(i, seed + 1) * 1024, hh(i, seed + 2) * 1024, r, r); } };
/** a fresta da porta vista de dentro do banheiro: tudo escuro menos uma faixa vertical */
const fxCrack = (p: Pen) => { const g = p.g; g.fillStyle = "#07060b"; g.fillRect(0, 0, 540, 960); g.clearRect(170, 20, 230, 920);
  g.fillStyle = "#c08a5a"; g.fillRect(400, 0, 44, 960); g.strokeStyle = "#241726"; g.lineWidth = 6; g.strokeRect(400, -10, 44, 980); g.fillStyle = "#e9e3d6"; g.fillRect(130, 0, 40, 960); g.strokeRect(130, -10, 40, 980); };
const fxShaft = (p: Pen) => { const g = p.g, gr = g.createLinearGradient(0, 0, 0, 1024); gr.addColorStop(0, "rgba(170,195,255,0.45)"); gr.addColorStop(1, "rgba(170,195,255,0)"); g.fillStyle = gr;
  g.beginPath(); g.moveTo(380, 0); g.lineTo(640, 0); g.lineTo(900, 1024); g.lineTo(220, 1024); g.closePath(); g.fill(); };

const fwdOf2 = (cam: CamInfo) => { const x = cam.right.z, z = -cam.right.x, n = Math.hypot(x, z) || 1; return [x / n, z / n]; };
const YOU: Who = { i: 900, o: MODERN(1), okey: "you" };
const ringU = (t: number) => q((t * 1.4) % 1, 12);
const phoneNear = (id: number, t: number, out: Stage, scr: Scr) => {
  const jx = scr === "vizinha" && t >= W.vibra - 0.1 ? 0.004 * Math.sign(Math.sin(t * 90)) * ((t % 0.9) < 0.55 ? 1 : 0) : 0;
  const [x, y, z] = PHONE_NEAR[id];
  out.fx.push({ key: `cel|${scr}|${ringU(t)}|${q(jx, 300)}`, cw: 800, ch: 1520, draw: (pp) => fxCel(pp, scr, ringU(t)), x: x + jx, y, z, w: 0.155, h: 0.295 });
};
/** física simples: um objeto solto em (x0,y0,z0) com velocidade (vx,vy,vz) no tempo s; para no chão */
const ball = (x0: number, y0: number, z0: number, vx: number, vy: number, vz: number, s: number, floor = D0 + 0.05): V3 => {
  const tg = (vy + Math.sqrt(vy * vy + 2 * 9.81 * (y0 - floor))) / 9.81, k = Math.min(s, tg);
  return [x0 + vx * k, Math.max(floor, y0 + vy * k - 4.905 * k * k), z0 + vz * k];
};

const ep2 = (id: number, cam: CamInfo, t: number, out: Stage) => {
  const c = SHOTS[id - 1].crowd, w = windAt(id, t);
  const stand = (expr: Expr, look = 0, swaps: number[] = []) => {
    out.places.push(person(cam, YOU, 800.0, D0, 2.4, { side: false, mirror: false }, { mode: "stand", expr, blink: lidAt(t, 900, swaps), look }, {}));
    blob(out, 800.0, D0, 2.4);
    out.fx.push({ key: "bph", cw: 400, ch: 760, draw: (pp) => fxPhone(pp, "flash"), x: 800.28, y: D0 + 1.05, z: 2.25, w: 0.16, h: 0.3 });
    out.fx.push({ key: "bglow", cw: 256, ch: 256, draw: (pp) => fxGlow(pp, "rgba(255,250,225,0.8)"), soft: true, x: 800.28, y: D0 + 1.05, z: 2.2, w: 0.9, h: 0.9 });
  };
  const storm = (k = 1) => { const [fx, fz] = fwdOf2(cam);
    rainCamFx(cam, t, out, (0.5 + 0.7 * w) * k); windCam(cam, t, out, w); boltSky(cam, t, out); void fx; void fz; };
  switch (c) {
    case "w_recap": stand("nervous", 0); break;
    case "w_latch": { // você de lado, a mão no trinco já fechado
      out.places.push(person(cam, YOU, 800.35, D0, 2.6, { side: false, mirror: false }, { mode: "stand", expr: "nervous", blink: lidAt(t, 900), look: -1 }, {}));
      blob(out, 800.35, D0, 2.6);
      out.fx.push({ key: "bph", cw: 400, ch: 760, draw: (pp) => fxPhone(pp, "flash"), x: 800.6, y: D0 + 1.05, z: 2.45, w: 0.16, h: 0.3 });
      out.fx.push({ key: "dglow", cw: 256, ch: 256, draw: (pp) => fxGlow(pp, "rgba(255,248,215,0.5)"), soft: true, x: 799.8, y: 1.15, z: 3.22, w: 1.3, h: 1.3 }); break; }
    case "w_flash": phoneNear(id, t, out, "low8"); break;
    case "w_storm": storm(); break;
    case "w_fall": case "w_debris": case "w_wide": case "w_choice": case "w_cta": case "w_neigh": {
      storm(c === "w_fall" || c === "w_debris" ? 1 : 0.7);
      if (fallen(t) && t < W.arvore + 3) { const s = t - W.estrondo;
        for (let i = 0; i < 18; i++) {   // telhas e lascas voando da fachada no impacto, em queda balística
          const vx = (hh(i, 1) - 0.5) * 4, vy = 1 + 4 * hh(i, 2), vz = -1.5 - 3 * hh(i, 3), [x, y, z] = ball(3.2 + (hh(i, 4) - 0.5) * 2, 5 + 2 * hh(i, 5), 11.8, vx, vy, vz, Math.max(0, s - 0.15 * hh(i, 6)));
          out.fx.push({ key: "tile", cw: 300, ch: 150, draw: fxTile, x, y, z, w: 0.42, h: 0.21, rot: q((s * (6 + 6 * hh(i, 7))) % 6.28, 20) });
        }
        if (s < 1.6) for (let k = 0; k < 3; k++) out.fx.push({ key: `burst${k}`, cw: 1024, ch: 1024, draw: (pp) => fxLeaves(pp, k + 40, 26), soft: true, x: 3 + k * 0.6, y: 4.5 + s * 1.2 + k * 0.5, z: 11.2 - s * 0.8, w: 3 + s * 2, h: 3 + s * 2 });
      }
      if (c === "w_neigh" || c === "w_choice" || c === "w_cta") { // a lanterna da vizinha pedindo socorro na janela de cima da casa ao lado
        const sw = Math.sin(t * 5.3) * 0.35;
        out.fx.push({ key: "nbeam", cw: 256, ch: 256, draw: (pp) => fxGlow(pp, "rgba(255,248,220,0.95)"), soft: true, x: 10.5 + sw, y: 5.0 + 0.15 * Math.sin(t * 3.1), z: 11.9, w: 0.9, h: 0.9 });
        out.fx.push({ key: "nhalo", cw: 256, ch: 256, draw: (pp) => fxGlow(pp, "rgba(255,240,200,0.35)"), soft: true, x: 10.5 + sw, y: 5.0, z: 11.85, w: 3.2, h: 3.2 });
      }
      break;
    }
    case "w_shake": { stand(t < W.casa + 1.0 ? "shock" : "pained", 0, [W.casa]);
      const s = t - W.casa;   // poeira caindo do teto (queda livre com resistência: velocidade limite baixa)
      for (let k = 0; k < 3; k++) out.fx.push({ key: `dust${k}`, cw: 1024, ch: 1024, draw: (pp) => fxDust(pp, k + 3), soft: true, x: 799.2 + k * 0.8, y: 2.6 - Math.min(2.4, 0.9 * Math.max(0, s - k * 0.2)), z: 1.0 + k * 0.4, w: 1.4, h: 1.4 });
      break; }
    case "w_ok": stand(t < W.aguentou ? "relief" : "nervous", 0, [W.aguentou]); break;
    case "w_drip": { // a gota se forma no teto, cresce, cai em queda livre e abre um anel na poça
      const per = 0.95;
      for (let k = 0; k < 2; k++) { const s = ((t + k * per / 2) % per), grow = 0.5, x = 801.6 + (k ? -0.25 : 0), z = 1.2 + (k ? 0.18 : 0);
        if (s < grow) out.fx.push({ key: "drop", cw: 64, ch: 64, draw: fxDrip, x, y: 2.79 - 0.03 - 0.035 * (s / grow), z, w: 0.045 + 0.035 * (s / grow), h: 0.045 + 0.035 * (s / grow) });
        else { const f2 = s - grow, y = 2.76 - 4.905 * f2 * f2;
          if (y > D0 + 0.04) out.fx.push({ key: "drop", cw: 64, ch: 64, draw: fxDrip, x, y, z, w: 0.07, h: 0.1 });
          else { const tg = Math.sqrt((2.76 - 0.04) / 4.905), u = q(clamp01((f2 - tg) / 0.4), 10); out.fx.push({ key: `rip${u}`, cw: 128, ch: 128, draw: (pp) => fxRipple(pp, u), flat: true, x, y: D0 + 0.05, z, w: 0.45, h: 0.45 }); }
        }
      }
      break; }
    case "w_smoke": {
      // fumaça escura passando pela fresta de baixo da porta e subindo em fiapos; as faíscas da sala piscam pela fresta
      for (let k = 0; k < 11; k++) { const s = (t * 0.32 + k / 11) % 1, x0 = 799.5 + (k % 6) * 0.2;
        out.fx.push({ key: "puff", cw: 256, ch: 256, draw: fxPuffL, soft: true, x: x0 + 0.12 * Math.sin(t * 0.9 + k) + 0.25 * s * Math.sin(k * 1.7), y: D0 + 0.05 + s * s * 0.9, z: 3.28 - s * 0.55, w: 0.14 + s * 0.42, h: 0.12 + s * 0.4 }); }
      if (sparkAt(t)) out.fx.push({ key: "sglow2", cw: 256, ch: 256, draw: (pp) => fxGlow(pp, "rgba(170,210,255,0.95)"), soft: true, x: 800.0, y: 0.06, z: 3.48, w: 1.5, h: 0.5 });
      break; }
    case "w_door": if (doorAt(id, t) > 0.02 && sparkAt(t)) out.fx.push({ key: "sglow", cw: 256, ch: 256, draw: (pp) => fxGlow(pp, "rgba(170,210,255,0.9)"), soft: true, x: 800.1, y: 0.4, z: 4.2, w: 1.6, h: 1.6 }); break;
    case "w_peek": case "w_wire": case "w_optA": {
      if (sparkAt(t)) { const sd = Math.floor(t * 15) % 6;
        out.fx.push({ key: `spark${sd}`, cw: 256, ch: 256, draw: (pp) => fxSpark(pp, sd), x: 602.3, y: D0 + 0.12, z: 2.26, w: c === "w_wire" ? 0.7 : 0.5, h: c === "w_wire" ? 0.7 : 0.5, rot: sd });
        out.fx.push({ key: "spool", cw: 256, ch: 256, draw: (pp) => fxGlow(pp, "rgba(170,210,255,0.6)"), soft: true, flat: true, x: 602.3, y: D0 + 0.05, z: 2.26, w: 2.2, h: 2.2 }); }
      out.fx.push({ key: "shaft", cw: 1024, ch: 1024, draw: fxShaft, soft: true, x: 600.4, y: 1.6, z: 2.4, w: 3.0, h: 3.2 });
      if (c === "w_peek") { const [fx, fz] = fwdOf2(cam); out.fx.push({ key: "crack", cw: 540, ch: 960, draw: fxCrack, x: cam.pos.x + fx * 0.5, y: cam.pos.y - 0.005, z: cam.pos.z + fz * 0.5, w: 0.39, h: 0.69 }); }
      if (c === "w_optA") { const u = clamp01((t - W.atravessa + 0.3) / 3.8), x = 596.8 + 3.8 * u, z = 0.5 + 0.15 * Math.sin(u * 3), ph = (t * 1.6) % 1;
        out.places.push(person(cam, YOU, x, D0, z, { side: false, mirror: false }, { mode: u > 0 && u < 1 ? "march" : "stand", phase: ph, lift: 70, expr: "nervous", blink: lidAt(t, 900), look: 1 }, {}));
        blob(out, x, D0, z);
        out.fx.push({ key: "aglow", cw: 256, ch: 256, draw: (pp) => fxGlow(pp, "rgba(255,250,225,0.6)"), soft: true, flat: true, x: x + 0.8, y: D0 + 0.05, z: z + 0.6, w: 1.6, h: 1.6 }); }
      break; }
    case "w_call": phoneNear(id, t, out, "vizinha"); break;
    case "w_optB": phoneNear(id, t, out, "193"); break;
  }
};

// ================= vídeo 16: Vendaval · Ep. 3 =================
const NEIGH: Who = { i: 902, o: { jacket: "#d9a640", pants: "#3b3f52", boots: "#3a2a22", hat: "hair", hair: "#3a2418", skin: "#c99067" }, okey: "vizinha" };
const callSec = (t: number) => Math.max(0, t - W.atendem) * (41 / (W.outro + 1.2 - W.atendem));   // o cronômetro chega a ~00:41 na "voz calma" (roteiro)
const phone3 = (id: number, t: number, out: Stage, scr: Scr) => {
  const [x, y, z] = PHONE_NEAR[id], u = ringU(t), sec = Math.floor(callSec(t));
  out.fx.push({ key: `cel3|${scr}|${u}|${sec}`, cw: 800, ch: 1520, draw: (pp) => fxCel(pp, scr, u, sec), x, y, z, w: 0.155, h: 0.295 });
};
const ep3 = (id: number, cam: CamInfo, t: number, out: Stage) => {
  const c = SHOTS[id - 1].crowd, w = windAt(id, t), dk = darkAt(id, t);
  /** você no banheiro: com o celular no ouvido (aceso) ou no escuro */
  const you = (expr: Expr, ear: boolean, swaps: number[] = []) => {
    out.places.push(person(cam, YOU, 800.0, D0, 2.4, { side: false, mirror: false }, { mode: "stand", expr, blink: lidAt(t, 900, swaps), look: 0 }, {}));
    blob(out, 800.0, D0, 2.4);
    if (ear) { out.fx.push({ key: "earph", cw: 400, ch: 760, draw: fxPhoneBack, x: 800.27, y: D0 + 1.44, z: 2.45, w: 0.09, h: 0.17, rot: -0.2 });
      out.fx.push({ key: "eglow", cw: 256, ch: 256, draw: (pp) => fxGlow(pp, "rgba(205,225,255,0.55)"), soft: true, x: 800.26, y: D0 + 1.44, z: 2.3, w: 0.8, h: 0.8 }); }
  };
  const storm = (k = 0.7) => { rainCamFx(cam, t, out, (0.5 + 0.7 * w) * k); windCam(cam, t, out, w); boltSky(cam, t, out); };
  const spark = (big: number) => { if (sparkAt(t)) { const sd = Math.floor(t * 15) % 6;
    out.fx.push({ key: `spark${sd}`, cw: 256, ch: 256, draw: (pp) => fxSpark(pp, sd), x: 602.3, y: D0 + 0.12, z: 2.26, w: big, h: big, rot: sd });
    out.fx.push({ key: "spool", cw: 256, ch: 256, draw: (pp) => fxGlow(pp, "rgba(170,210,255,0.6)"), soft: true, flat: true, x: 602.3, y: D0 + 0.05, z: 2.26, w: 2.2, h: 2.2 }); } };
  const siren = (x: number, z: number, k: number) => { if (k <= 0) return; const pu = sirenPulse(t), a = q(k * pu, 20);
    out.fx.push({ key: `sir|${a}`, cw: 256, ch: 256, draw: (pp) => fxGlow(pp, `rgba(255,40,30,${0.95 * a})`), soft: true, x, y: 1.9, z, w: 2.2, h: 2.2 });
    out.fx.push({ key: `sirH|${a}`, cw: 256, ch: 256, draw: (pp) => fxGlow(pp, `rgba(255,60,40,${0.35 * a})`), soft: true, x, y: 2.6, z, w: 12, h: 9 });
    out.fx.push({ key: `sirF|${a}`, cw: 256, ch: 256, draw: (pp) => fxGlow(pp, `rgba(255,50,40,${0.45 * a})`), soft: true, flat: true, x: x + 3, y: D0 + 0.04, z, w: 14, h: 8 }); };
  const neighbor = (expr: Expr) => {   // a vizinha na sua porta, com a lanterna, na chuva
    out.places.push(person(cam, NEIGH, -1.25, D0, 11.45, { side: false, mirror: false }, { mode: "stand", expr, blink: lidAt(t, 902), look: 0 }, {}));
    blob(out, -1.25, D0, 11.45);
    const sw = 0.05 * Math.sin(t * 4.1);
    out.fx.push({ key: "nlamp", cw: 256, ch: 256, draw: (pp) => fxGlow(pp, "rgba(255,248,220,0.95)"), soft: true, x: -0.95 + sw, y: D0 + 1.05, z: 11.3, w: 0.5, h: 0.5 });
    out.fx.push({ key: "nlampF", cw: 256, ch: 256, draw: (pp) => fxGlow(pp, "rgba(255,240,200,0.4)"), soft: true, flat: true, x: -0.6, y: D0 + 0.05, z: 10.6, w: 3.2, h: 3.2 });
  };
  const knockDust = () => { for (const k of KNOCKS) { const s2 = t - k; if (s2 >= 0 && s2 < 1.0) for (let i = 0; i < 2; i++)
    out.fx.push({ key: `kd${i}`, cw: 1024, ch: 1024, draw: (pp) => fxDust(pp, i + 9), soft: true, x: 593.7 + i * 0.8, y: 2.15 - 1.2 * s2, z: 3.75, w: 1.0, h: 1.0 }); } };
  switch (c) {
    case "v_dial": phone3(id, t, out, "193"); break;
    case "v_ear": you("nervous", true); break;
    case "v_call": case "v_call2": phone3(id, t, out, "call"); break;
    case "v_low3": phone3(id, t, out, "low3"); break;
    case "v_end": phone3(id, t, out, t < W.apaga ? "ended" : "off"); break;
    case "v_listen": you("nervous", true); break;
    case "v_dark": case "v_optB": you(c === "v_optB" && t > W.grita - 0.3 ? "shock" : "nervous", false, [W.grita]); break;
    case "v_wire": case "v_wire2": spark(0.7); out.fx.push({ key: "shaft", cw: 1024, ch: 1024, draw: fxShaft, soft: true, x: 600.4, y: 1.6, z: 2.4, w: 3.0, h: 3.2 }); break;
    case "v_room": spark(0.45); out.fx.push({ key: "shaft", cw: 1024, ch: 1024, draw: fxShaft, soft: true, x: 600.4, y: 1.6, z: 2.4, w: 3.0, h: 3.2 });
      out.fx.push({ key: "dgap", cw: 256, ch: 256, draw: (pp) => fxGlow(pp, "rgba(255,245,215,0.7)"), soft: true, flat: true, x: 594.1, y: D0 + 0.05, z: 3.6, w: 1.6, h: 0.8 }); break;
    case "v_knock": knockDust(); out.fx.push({ key: "dgap", cw: 256, ch: 256, draw: (pp) => fxGlow(pp, "rgba(255,245,215,0.75)"), soft: true, flat: true, x: 594.1 + 0.25 * Math.sin(t * 3.3), y: D0 + 0.05, z: 3.6, w: 1.6, h: 0.8 }); break;
    case "v_optA": { spark(0.5); out.fx.push({ key: "shaft", cw: 1024, ch: 1024, draw: fxShaft, soft: true, x: 600.4, y: 1.6, z: 2.4, w: 3.0, h: 3.2 });
      const u = clamp01((t - W.atravessa + 0.3) / 4.2), x = 605.8 - 5.2 * u, z = 0.2 + 1.2 * u, ph = (t * 1.6) % 1;
      out.places.push(person(cam, YOU, x, D0, z, { side: false, mirror: false }, { mode: u > 0 && u < 1 ? "march" : "stand", phase: ph, lift: 60, expr: "nervous", blink: lidAt(t, 900), look: -1 }, {}));
      blob(out, x, D0, z); break; }
    case "v_house": case "v_neighW": case "v_choice": case "v_cta": case "v_far": case "v_near": case "v_door": case "v_shout": {
      storm(c === "v_far" || c === "v_near" ? 0.8 : 0.7);
      if (c === "v_neighW") { const sw = Math.sin(t * 5.3) * 0.35;
        out.fx.push({ key: "nbeam", cw: 256, ch: 256, draw: (pp) => fxGlow(pp, "rgba(255,248,220,0.95)"), soft: true, x: 10.5 + sw, y: 5.0 + 0.15 * Math.sin(t * 3.1), z: 11.9, w: 0.9, h: 0.9 });
        out.fx.push({ key: "nhalo", cw: 256, ch: 256, draw: (pp) => fxGlow(pp, "rgba(255,240,200,0.35)"), soft: true, x: 10.5 + sw, y: 5.0, z: 11.85, w: 3.2, h: 3.2 }); }
      if (c === "v_far" || c === "v_near") siren(sirenX(t), 6.2, sirenK(t));
      if (c === "v_choice" || c === "v_cta") siren(-24, 6.2, 0.55);
      if (c === "v_door" || c === "v_shout" || c === "v_choice" || c === "v_cta") neighbor(c === "v_door" ? "nervous" : "shock");
      break; }
    case "v_gap": { const k = sirenK(t) * sirenPulse(t), a = q(k, 20);
      if (a > 0) { out.fx.push({ key: `rg|${a}`, cw: 256, ch: 256, draw: (pp) => fxGlow(pp, `rgba(255,40,30,${0.95 * a})`), soft: true, x: 800.0, y: 0.06, z: 3.48, w: 1.6, h: 0.5 });
        out.fx.push({ key: `rgF|${a}`, cw: 256, ch: 256, draw: (pp) => fxGlow(pp, `rgba(255,50,40,${0.5 * a})`), soft: true, flat: true, x: 800.0, y: D0 + 0.04, z: 3.0, w: 1.8, h: 1.2 }); }
      break; }
  }
  void dk;
};

// ================= vídeo 18: Jogador 2 · Ep. 1 =================
/** cachorro de desenho, de lado (olhando para a esquerda), latindo ou quieto de orelha em pé */
const fxDog = (p: Pen, bark: boolean, col: string) => hi(p, 1, (g) => {
  g.lineJoin = "round"; g.lineCap = "round"; g.lineWidth = 9; g.strokeStyle = "#1a1320";
  const dark = "#5a3a24";
  g.fillStyle = col; // corpo
  g.beginPath(); g.ellipse(300, 240, 130, 62, 0, 0, 7); g.fill(); g.stroke();
  for (const [x, d] of [[210, 0], [250, 1], [350, 0], [390, 1]] as const) { g.fillStyle = d ? dark : col; g.beginPath(); g.roundRect(x - 16, 270, 32, 92, 14); g.fill(); g.stroke(); }
  g.fillStyle = col; g.beginPath(); g.moveTo(420, 220); g.quadraticCurveTo(480, 150, 470, 120); g.lineWidth = 16; g.strokeStyle = "#1a1320"; g.stroke(); g.lineWidth = 9;
  g.beginPath(); g.ellipse(160, 165, 68, 58, 0, 0, 7); g.fill(); g.stroke();            // cabeça
  g.beginPath(); g.ellipse(100, bark ? 172 : 182, 50, 30, 0, 0, 7); g.fill(); g.stroke(); // focinho
  if (bark) { g.fillStyle = "#7a1f2b"; g.beginPath(); g.moveTo(58, 192); g.lineTo(130, 196); g.lineTo(70, 232); g.closePath(); g.fill(); g.stroke(); }
  g.fillStyle = "#1a1320"; g.beginPath(); g.ellipse(56, bark ? 160 : 170, 13, 10, 0, 0, 7); g.fill();       // nariz
  g.fillStyle = dark; g.beginPath(); // orelha: caída latindo, em pé quieto (alerta)
  if (bark) { g.ellipse(196, 150, 26, 50, 0.5, 0, 7); } else { g.moveTo(178, 120); g.lineTo(210, 50); g.lineTo(226, 128); g.closePath(); }
  g.fill(); g.stroke();
  g.fillStyle = "#ffffff"; g.beginPath(); g.arc(140, 150, bark ? 13 : 17, 0, 7); g.fill(); g.stroke();
  g.fillStyle = "#1a1320"; g.beginPath(); g.arc(bark ? 136 : 146, 150, bark ? 6 : 6, 0, 7); g.fill();
});
/** o controle (genérico, sem marca) nas suas mãos */
const fxPad = (p: Pen) => hi(p, 1, (g) => {
  g.lineJoin = "round"; g.lineWidth = 10; g.strokeStyle = "#141018"; g.fillStyle = "#24262e";
  g.beginPath(); g.moveTo(150, 60); g.lineTo(362, 60); g.quadraticCurveTo(430, 60, 448, 140); g.lineTo(470, 220); g.quadraticCurveTo(480, 270, 430, 266);
  g.quadraticCurveTo(388, 240, 356, 200); g.lineTo(156, 200); g.quadraticCurveTo(124, 240, 82, 266); g.quadraticCurveTo(32, 270, 42, 220); g.lineTo(64, 140); g.quadraticCurveTo(82, 60, 150, 60); g.fill(); g.stroke();
  g.fillStyle = "#3a3d48"; g.beginPath(); g.arc(196, 170, 30, 0, 7); g.arc(316, 170, 30, 0, 7); g.fill();
  g.fillStyle = "#e6e8ee"; for (const [x, y] of [[396, 100], [418, 124], [374, 124], [396, 148]]) { g.beginPath(); g.arc(x, y, 11, 0, 7); g.fill(); }
  g.fillRect(104, 112, 44, 14); g.fillRect(119, 97, 14, 44);
  g.fillStyle = "#4aa8ff"; g.fillRect(226, 74, 60, 10); // luz do controle: jogador 1
  // as mãos segurando (pele)
  g.fillStyle = "#e0ac7e"; g.strokeStyle = "#141018"; g.lineWidth = 8;
  for (const sx of [1, -1]) { g.beginPath(); g.ellipse(256 + sx * 205, 236, 52, 40, sx * 0.5, 0, 7); g.fill(); g.stroke(); }
});
/** a caixa do console (genérica: só um desenho do aparelho, sem nome nem marca) */
const fxBox = (p: Pen) => hi(p, 1, (g) => {
  g.lineJoin = "round"; g.lineWidth = 10; g.strokeStyle = "#141018";
  g.fillStyle = "#eef1f6"; g.beginPath(); g.roundRect(40, 40, 320, 400, 14); g.fill(); g.stroke();
  g.fillStyle = "#2f5fb3"; g.fillRect(45, 340, 310, 95);
  g.fillStyle = "#ffffff"; g.beginPath(); g.roundRect(150, 100, 100, 220, 30); g.fill(); g.stroke(); g.fillStyle = "#17171c"; g.fillRect(190, 104, 20, 212);
  g.fillStyle = "#e0ac7e"; g.lineWidth = 8; for (const x of [40, 360]) { g.beginPath(); g.ellipse(x, 300, 38, 52, 0, 0, 7); g.fill(); g.stroke(); }
});
const SEAT_H = 0.45 / SU;
const ep4 = (id: number, cam: CamInfo, t: number, out: Stage) => {
  const c = SHOTS[id - 1].crowd;
  /** você no sofá, de frente para a TV */
  const sit = (expr: Expr, look = 0, swaps: number[] = []) => {
    out.places.push(person(cam, YOU, 599.35, D0, 2.44, { side: false, mirror: false }, { mode: "sit", seatH: SEAT_H, expr, blink: lidAt(t, 900, swaps), look }, {}));
  };
  const tvGlow = () => { if (!tvOn(id, t)) return;
    out.fx.push({ key: "tvwash", cw: 256, ch: 256, draw: (pp) => fxGlow(pp, "rgba(120,170,255,0.5)"), soft: true, x: 600.0, y: 1.1, z: -0.2, w: 3.4, h: 2.2 });
    out.fx.push({ key: "tvfloor", cw: 256, ch: 256, draw: (pp) => fxGlow(pp, "rgba(110,160,255,0.35)"), soft: true, flat: true, x: 600.0, y: D0 + 0.05, z: 0.8, w: 4.0, h: 3.2 }); };
  const ledGlow = (k = 1) => { if (ledOn(id, t)) out.fx.push({ key: `led${k}`, cw: 256, ch: 256, draw: (pp) => fxGlow(pp, "rgba(90,170,255,0.95)"), soft: true, x: 601.015, y: D0 + 0.62, z: -0.53, w: 0.12 * k, h: 0.2 * k }); };
  const lampGlow = () => { if (lampOn(id, t)) out.fx.push({ key: "lampG", cw: 256, ch: 256, draw: (pp) => fxGlow(pp, "rgba(255,210,140,0.6)"), soft: true, x: 596.8, y: D0 + 1.45, z: 3.3, w: 2.2, h: 2.2 }); };
  const dogs = () => { const b = barkAt(t), b2 = barkAt(t + 0.11);
    out.fx.push({ key: `dogA|${b}`, cw: 512, ch: 384, draw: (pp) => fxDog(pp, b, "#b07a48"), x: -198.4, y: D0 + 0.25 + 0.36, z: -295.6, w: 0.95, h: 0.71 });
    out.fx.push({ key: `dogB|${b2}`, cw: 512, ch: 384, draw: (pp) => fxDog(pp, b2, "#d8c2a0"), x: -197.0, y: D0 + 0.25 + 0.3, z: -295.2, w: 0.8, h: 0.6 }); };
  switch (c) {
    case "j_tv99": case "j_tvon": case "j_p2": tvGlow(); ledGlow(); if (c === "j_tvon") sit(t > W.liga ? "shock" : "nervous", 1, [W.liga]); break;
    case "j_cut": case "j_choice": sit(c === "j_cut" ? (t < W.caiu ? "grin" : "shock") : "nervous", 0, [W.caiu]); lampGlow(); tvGlow(); ledGlow(); break;
    case "j_dark": case "j_face": case "j_decide": sit(c === "j_decide" ? "shock" : "nervous", c === "j_face" ? 1 : 0); tvGlow(); ledGlow(0.8); break;
    case "j_led": ledGlow(1.6); break;
    case "j_pad": sit("nervous", -1); tvGlow(); out.fx.push({ key: "pad", cw: 512, ch: 300, draw: fxPad, x: 599.35, y: D0 + 0.74, z: 2.2, w: 0.36, h: 0.21 }); break;
    case "j_side": case "j_vib": case "j_optA": sit(c === "j_side" ? "nervous" : "shock", 1); tvGlow(); break;
    case "j_buy": out.places.push(person(cam, YOU, 599.6, D0, 1.7, { side: false, mirror: false }, { mode: "stand", expr: "grin", blink: lidAt(t, 900), look: 0 }, {}));
      blob(out, 599.6, D0, 1.7); out.fx.push({ key: "cbox", cw: 400, ch: 480, draw: fxBox, x: 599.6, y: D0 + 0.95, z: 1.45, w: 0.42, h: 0.5 }); lampGlow(); break;
    case "j_dogs": dogs(); break;
    case "j_noen": out.fx.push({ key: "winLed", cw: 256, ch: 256, draw: (pp) => fxGlow(pp, "rgba(90,170,255,0.9)"), soft: true, x: -198.875, y: D0 + 1.4, z: -296.3, w: 0.18, h: 0.18 }); dogs(); break;
    case "j_farm": case "j_cta": dogs();
      if (c === "j_cta") out.fx.push({ key: "winHalo", cw: 256, ch: 256, draw: (pp) => fxGlow(pp, "rgba(110,170,255,0.55)"), soft: true, x: -198.875, y: D0 + 1.65, z: -296.2, w: 2.6, h: 2.4 }); break;
  }
};
/** chuva diante da câmera (mesma do vídeo 12) com densidade dada */
const rainCamFx = (cam: CamInfo, t: number, out: Stage, dense: number) => rainCam(cam, t, out, dense);

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
  if (s.crowd.startsWith("w_")) ep2(id, cam, t, out);
  if (s.crowd.startsWith("v_")) ep3(id, cam, t, out);
  if (s.crowd.startsWith("j_")) ep4(id, cam, t, out);
  return out;
};
export { FPS, T_WAR, T_NOT, smooth, clamp01 };
