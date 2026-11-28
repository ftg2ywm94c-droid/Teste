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
import { FPS, D0, SHOTS, V3, smooth, clamp01, easeOut, T_SINK, T_WAR, T_NOT, T_OFF, T_FRIDGE, T_HOURS, W } from "./story";
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

/** teste 11: a família na calçada; no "apaga" todos levam um susto e olham para cima */
const family = (cam: CamInfo, t: number, out: Stage) => {
  const spots: [number, number][] = [[4.6, 7.2], [6.0, 7.6], [7.2, 7.0], [3.2, 9.6], [10.6, 9.4]];
  const after = t >= T_OFF - 2 / FPS;
  spots.forEach(([x, z], i) => {
    const kid = i === 2, o = kid ? KID : MODERN(i + 1), who: Who = { i: i + 600, o, okey: kid ? "kid" : `f${i}` };
    const expr: Expr = after ? (["shock", "nervous", "shock", "dazed", "nervous"] as Expr[])[i] : (["smile_closed", "grin", "laugh", "smile", "neutral"] as Expr[])[i];
    const hop = after && t < T_OFF + 0.25 ? 0.12 * Math.sin(((t - T_OFF) / 0.25) * Math.PI) : 0;
    const fo: FrontOpts = { mode: "stand", expr, blink: lidAt(t, i + 600, [T_OFF]), look: after ? 1 : 0 };
    out.places.push(person(cam, who, x, D0 + hop, z, { side: false, mirror: false }, fo, {}, kid ? 0.72 : 1));
    blob(out, x, D0, z, kid ? 0.72 : 1);
  });
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
/** a geladeira: uma pessoa preocupada ao lado, o relógio correndo em cima */
const fridge = (cam: CamInfo, t: number, out: Stage) => {
  const who: Who = { i: 650, o: MODERN(2), okey: "f1" };
  const fo: FrontOpts = { mode: "stand", expr: t > T_HOURS ? "pained" : "nervous", blink: lidAt(t, 650), look: -1, facing: 1 };
  out.places.push(person(cam, who, 199.8, D0, 2.4, { side: false, mirror: false }, fo, {}));
  blob(out, 199.8, D0, 2.4);
  const u = clamp01((t - T_FRIDGE - 0.2) / (T_HOURS - T_FRIDGE + 0.4));
  const qq = Math.round(u * 60) / 60;
  const pop = smooth((t - T_FRIDGE) / 0.25);
  out.fx.push({ key: `clock${qq}`, cw: 600, ch: 600, draw: (p) => fxClock(p, qq), x: 200.4, y: D0 + 2.45, z: 3.0, w: 0.85 * pop, h: 0.85 * pop });
  // "carne e leite viram risco": a carne e a caixa de leite no balcão com um aviso vermelho
  if (t >= W.carne - 0.1) {
    const k = q(easeOut((t - W.carne + 0.1) / 0.3), 20), r = t >= W.risco - 0.05;
    out.fx.push({ key: `risk${k}${r}`, cw: 700, ch: 520, draw: (p) => fxRisk(p, r), x: 201.15, y: D0 + 1.3, z: 3.2, w: 0.85 * k, h: 0.63 * k });
  }
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

const storm = (cam: CamInfo, t: number, out: Stage) => {
  const spots: [number, number][] = [[4.4, 7.4], [6.0, 8.0], [7.6, 7.2]];
  spots.forEach(([x, z], i) => {
    const who: Who = { i: i + 700, o: MODERN(i + 3), okey: `s${i}` };
    const fo: FrontOpts = { mode: "stand", expr: (["nervous", "shock", "pained"] as Expr[])[i], blink: lidAt(t, i + 700), look: 1 };
    out.places.push(person(cam, who, x, D0, z, { side: false, mirror: false }, fo, {}));
    blob(out, x, D0, z);
  });
  // chuva em três camadas diante da câmera
  const f = Math.round(t * FPS), dir = [0.427, -0.05, 0.902];
  [[1.6, 2.0, 0.6], [3.6, 4.4, 1], [8, 9.5, 1.4]].forEach(([d, w, dense], k) => {
    const s = (f * 3 + k * 2) % 8;
    out.fx.push({ key: `rain${k}_${s}`, cw: 1024, ch: 1024, draw: (p) => fxRain(p, s + k * 11, dense), soft: true,
      x: 2.5 + dir[0] * d, y: 1.8 + dir[1] * d + (k - 1) * 0.3, z: 1.6 + dir[2] * d, w, h: w * 1.8 });
  });
  // dois raios
  for (const tb of [W.temporal + 0.1, W.saoPaulo - 0.2]) if (t >= tb && t < tb + 0.2)
    out.fx.push({ key: "bolt", cw: 400, ch: 640, draw: fxBolt, x: 12, y: 16, z: 40, w: 9, h: 14 });
};

const building = (cam: CamInfo, t: number, out: Stage) => {
  const who: Who = { i: 720, o: MODERN(4), okey: "b0" };
  const dry = t >= W.secando - 0.1;
  const fo: FrontOpts = { mode: "stand", expr: dry ? "shock" : t > W.semLuz ? "nervous" : "neutral", blink: lidAt(t, 720, [W.secando]), look: -1, facing: -1 };
  out.places.push(person(cam, who, -197.55, D0, 8.0, { side: false, mirror: false }, fo, {}));
  blob(out, -197.55, D0, 8.0);
  const who2: Who = { i: 721, o: KID, okey: "kid" };
  out.places.push(person(cam, who2, -196.6, D0, 7.4, { side: false, mirror: false }, { mode: "stand", expr: dry ? "dazed" : "neutral", blink: lidAt(t, 721), look: -1 }, {}, 0.72));
  blob(out, -196.6, D0, 7.4, 0.72);
  // medidor da caixa d'água descendo
  const lvl = q(1 - 0.92 * smooth((t - W.semLuz) / (W.dia2 - W.semLuz - 0.3)), 30);
  out.fx.push({ key: `tank${lvl}`, cw: 300, ch: 600, draw: (p) => fxTank(p, lvl), x: -196.4, y: D0 + 20.0, z: 11.0, w: 1.5, h: 3.0 });
  // bomba sem energia
  if (t >= W.bomba - 0.1) { const k = q(easeOut((t - W.bomba + 0.1) / 0.25), 20);
    out.fx.push({ key: `nopow${k}`, cw: 300, ch: 300, draw: fxNoPower, x: -192.7, y: D0 + 1.7, z: 9.6, w: 0.9 * k, h: 0.9 * k }); }
  // gotas na torneira até secar
  if (t >= W.semLuz && t < W.secando + 0.2) {
    const u = ((t - W.semLuz) * 1.6) % 1;
    out.fx.push({ key: "drop", cw: 100, ch: 120, draw: fxDrop, x: -198.3, y: D0 + 0.72 - u * 0.5, z: 8.65, w: 0.06, h: 0.075 });
  }
};

const antenna = (cam: CamInfo, t: number, out: Stage) => {
  const off = t >= W.some - 0.05;
  const who: Who = { i: 740, o: MODERN(5), okey: "a0" };
  const fo: FrontOpts = { mode: "stand", expr: off ? "shock" : t > W.falham ? "nervous" : "neutral", blink: lidAt(t, 740, [W.some]), look: -1 };
  out.places.push(person(cam, who, 398.6, D0, 6.6, { side: false, mirror: false }, fo, {}));
  blob(out, 398.6, D0, 6.6);
  const sc = off ? "nosignal" : "home";
  out.fx.push({ key: `ph_${sc}`, cw: 400, ch: 760, draw: (p) => fxPhone(p, sc), x: 398.92, y: D0 + 1.12, z: 6.45, w: 0.16, h: 0.3 });
  const ph = q(((t * 0.9) % 1), 12);
  out.fx.push({ key: `sig${ph}${t > W.falham + 0.3}`, cw: 640, ch: 640, draw: (p) => fxSignal(p, ph, t > W.falham + 0.3), x: 400, y: D0 + 26.0, z: 20, w: 7, h: 7 });
  if (t >= W.gerador - 0.1) {
    const lvl = q(1 - smooth((t - W.bateria) / (W.falham - W.bateria + 0.3)), 30), k = q(easeOut((t - W.gerador + 0.1) / 0.25), 20);
    out.fx.push({ key: `bat${lvl}${k}`, cw: 500, ch: 320, draw: (p) => fxBattery(p, lvl), x: 403.5, y: D0 + 2.5, z: 16.2, w: 1.6 * k, h: 1.0 * k });
  }
};

const shop = (cam: CamInfo, t: number, out: Stage) => {
  const v: Who = { i: 760, o: MODERN(0), okey: "v0" }, c: Who = { i: 761, o: MODERN(2), okey: "c0" };
  const fail = t >= W.passa - 0.05;
  out.places.push(person(cam, v, 400.75, D0, 121.0, { side: false, mirror: false }, { mode: "stand", expr: fail ? "pained" : "nervous", blink: lidAt(t, 760, [W.passa]), look: -1 }, {}));
  out.places.push(person(cam, c, 398.95, D0, 118.9, { side: false, mirror: false }, { mode: "stand", expr: fail ? "shock" : "neutral", blink: lidAt(t, 761, [W.passa]), look: 1, facing: 1 }, {}));
  blob(out, 398.95, D0, 118.9);
  out.fx.push({ key: "cm", cw: 340, ch: 560, draw: (p) => fxCardMachine(p, true), x: 400.2, y: D0 + 1.3, z: 119.45, w: 0.24, h: 0.4 });
  if (t >= W.pix - 0.1) {
    const k = q(easeOut((t - W.pix + 0.1) / 0.25), 20), a = q((t * 6) % (Math.PI * 2), 3);
    out.fx.push({ key: `pix${a}${fail}${k}`, cw: 500, ch: 240, draw: (p) => fxPix(p, a, fail), x: 399.75, y: D0 + 1.95, z: 119.6, w: 0.8 * k, h: 0.38 * k });
  }
};

const seated = (cam: CamInfo, t: number, out: Stage, expr: Expr) => {
  const who: Who = { i: 780, o: MODERN(1), okey: "r0" };
  out.places.push(person(cam, who, 600.0, D0 + 0.33, 2.62, { side: false, mirror: false }, { mode: "sit", expr, blink: lidAt(t, 780), look: 0 }, {}));
};
const room = (cam: CamInfo, t: number, out: Stage) => {
  const sc = t >= W.avisar - 0.1 ? "msg" : t >= W.radio - 0.1 ? "radio" : t >= W.lanterna - 0.1 ? "flash" : "home";
  seated(cam, t, out, t >= W.avisar ? "relief" : t >= W.lanterna ? "smile" : "nervous");
  const pop = q(easeOut((t - W.ai) / 0.3), 20);
  out.fx.push({ key: `rph_${sc}${pop}`, cw: 400, ch: 760, draw: (p) => fxPhone(p, sc), x: 600.32, y: D0 + 1.1, z: 2.35, w: 0.2 * pop, h: 0.38 * pop });
  if (t >= W.lanterna - 0.1 && t < W.radio - 0.1)
    out.fx.push({ key: "beam", cw: 1024, ch: 1024, draw: fxBeam, soft: true, x: 601.6, y: D0 + 1.35, z: 2.3, w: 2.8, h: 2.8, rot: 0.15 });
};
const product = (cam: CamInfo, t: number, out: Stage) => {
  seated(cam, t, out, t >= W.carrega ? "relief" : "neutral");
  const back = t >= W.powerbank - 0.6;
  const flip = Math.abs(Math.cos(clamp01((t - W.powerbank + 0.6) / 0.3) * Math.PI)), w = 0.42 * (back && t < W.powerbank - 0.3 ? flip : back ? Math.max(flip, 1) : 1);
  const scr = t >= W.carrega ? "charge" : "lowbat", u = q(clamp01((t - W.carrega) / 1.6), 20);
  out.fx.push({ key: back ? "pback" : `pf${scr}${u}`, cw: 400, ch: 760, draw: (p) => (back ? fxPhoneBack(p) : fxPhone(p, scr, u)), x: 600.0, y: D0 + 1.2, z: 1.9, w, h: 0.8 });
  if (t >= W.powerbank) {
    const k = easeOut((t - W.powerbank) / 0.6), snap = smooth((t - W.gruda + 0.25) / 0.25);
    const x = 600.0 + 0.55 * (1 - k) * (1 - snap) + 0.06 * (1 - snap), y = 1.12 + 0.05 * (1 - snap), z = 1.86 - 0.04 * (1 - snap);
    const ring = t >= W.carrega ? q(0.5 + 0.5 * Math.sin((t - W.carrega) * 5), 10) : 0;
    out.fx.push({ key: `bank${ring}`, cw: 320, ch: 460, draw: (p) => fxBank(p, ring), x, y: D0 + y, z, w: 0.3, h: 0.43 });
    if (t >= W.gruda && t < W.gruda + 0.35) { const u2 = q((t - W.gruda) / 0.35, 30);
      out.fx.push({ key: `snap${u2}`, cw: 500, ch: 500, draw: (p) => fxBurst(p, u2), x: 600.0, y: D0 + 1.12, z: 1.84, w: 0.9, h: 0.9 }); }
  }
};
/** família da rua: modo "hook" (feliz), "relief" (a luz volta), "cta" (acenando) */
const street = (cam: CamInfo, t: number, out: Stage, mode: "hook" | "relief" | "cta") => {
  const spots: [number, number][] = [[4.6, 7.2], [6.0, 7.6], [7.2, 7.0], [3.2, 9.6], [10.6, 9.4]];
  spots.forEach(([x, z], i) => {
    const kid = i === 2, o = kid ? KID : MODERN(i + 1), who: Who = { i: i + 600, o, okey: kid ? "kid" : `f${i}` };
    const back = mode === "relief" && t >= W.volta + 0.1;
    const expr: Expr = mode === "relief" ? (back ? (["relief_open", "laugh", "laugh", "relief", "grin"] as Expr[])[i] : (["dazed", "nervous", "dazed", "neutral", "nervous"] as Expr[])[i])
      : mode === "cta" ? (["smile", "grin", "laugh", "smile_closed", "grin"] as Expr[])[i] : (["smile_closed", "grin", "laugh", "smile", "neutral"] as Expr[])[i];
    const hop = (mode === "relief" && back && kid) ? Math.max(0, Math.sin((t - W.volta) * 9)) * 0.15 : 0;
    const wave = mode === "cta" && i < 3 ? q(Math.sin(t * 8 + i * 1.3), 30) : undefined;
    const fo: FrontOpts = { mode: "stand", expr, wave, blink: lidAt(t, i + 600, mode === "relief" ? [W.volta] : []), look: mode === "relief" && !back ? 1 : 0 };
    out.places.push(person(cam, who, x, D0 + hop, z, { side: false, mirror: false }, fo, {}, kid ? 0.72 : 1));
    blob(out, x, D0, z, kid ? 0.72 : 1);
  });
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
  if (s.crowd === "family") family(cam, t, out);
  if (s.crowd === "fridge") fridge(cam, t, out);
  if (s.crowd === "hook" || s.crowd === "relief" || s.crowd === "cta") street(cam, t, out, s.crowd);
  if (s.crowd === "storm") storm(cam, t, out);
  if (s.crowd === "building") building(cam, t, out);
  if (s.crowd === "antenna") antenna(cam, t, out);
  if (s.crowd === "shop") shop(cam, t, out);
  if (s.crowd === "room") room(cam, t, out);
  if (s.crowd === "product") product(cam, t, out);
  return out;
};
export { FPS, T_WAR, T_NOT, smooth, clamp01 };
