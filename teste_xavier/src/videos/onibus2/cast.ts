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
import { FPS, D0, SHOTS, V3, smooth, clamp01, easeOut, T_SINK, T_WAR, T_NOT, T_OFF, T_FRIDGE, T_HOURS, W, windAt, leanAt, BOLTS, L, POLE_X, POLE_Z, poleOff, FRONT_SEAT, CUSHION_Y, FLOOR_Y, PHONE_NEAR, DOOR_U, busX, busMoving, intOff, BZ, GX, inGarage, garageOff, someoneAt } from "./story";
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
// ================= vídeo 13: o último ônibus =================
/** escala o desenho: projeta em 400 x 760 num canvas 800 x 1520 (nítido de perto) */
const hi = (p: Pen, k: number, fn: (g: CanvasRenderingContext2D) => void) => { const g = p.g; g.save(); g.scale(k, k); fn(g); g.restore(); };
const wrap = (g: CanvasRenderingContext2D, text: string, maxW: number) => {
  const out: string[] = []; let line = "";
  for (const w of text.split(" ")) { const tt = line ? line + " " + w : w; if (g.measureText(tt).width > maxW && line) { out.push(line); line = w; } else line = tt; }
  if (line) out.push(line); return out;
};
const MSGS = ["NÃO DESCE NO PRÓXIMO PONTO.", "ELE JÁ SABE QUE VOCÊ VIU.", "FICA SENTADO.", "BOA ESCOLHA. AGORA NÃO OLHA PRO RETROVISOR."];
const MSG_T = ["00:11", "00:12", "00:13", "00:16"];
type CallMode = "dark" | "ring" | "notif" | "chat";
/** o celular desconhecido: tocando, tela de bloqueio com notificação, ou a conversa com n mensagens (a última "pulando") */
const fxCall = (p: Pen, mode: CallMode, n: number, u: number, k = 2, hand = false) => hi(p, k, (g) => {
  rr(g, 20, 20, 360, 720, 60, "#1c1e26", "#241726", 14);
  g.save(); g.beginPath(); g.roundRect(45, 60, 310, 640, 36); g.clip();
  if (mode === "dark") { const gr = g.createLinearGradient(45, 60, 355, 700); gr.addColorStop(0, "#151a26"); gr.addColorStop(0.5, "#0a0d14"); gr.addColorStop(1, "#05070b"); g.fillStyle = gr; g.fillRect(45, 60, 310, 640);
    g.fillStyle = "rgba(255,255,255,0.06)"; g.beginPath(); g.moveTo(60, 60); g.lineTo(200, 60); g.lineTo(60, 300); g.closePath(); g.fill(); }
  else {
    const gr = g.createLinearGradient(0, 60, 0, 700); gr.addColorStop(0, "#1b2f5a"); gr.addColorStop(1, "#0b1226"); g.fillStyle = gr; g.fillRect(45, 60, 310, 640);
    g.fillStyle = "#fff";
    if (mode === "ring") {
      font(g, 22); g.fillStyle = "#9fb4e0"; g.fillText("chamada recebida", 200, 120);
      for (let i = 0; i < 3; i++) { const r = 70 + ((u + i / 3) % 1) * 90; g.strokeStyle = `rgba(160,200,255,${0.6 * (1 - ((u + i / 3) % 1))})`; g.lineWidth = 6; g.beginPath(); g.arc(200, 250, r, 0, 7); g.stroke(); }
      p.ell(200, 250, 62, 62, "#3a4f80", 0); font(g, 80); g.fillStyle = "#fff"; g.fillText("?", 200, 254);
      font(g, 40); g.fillText("Número", 200, 380); g.fillText("desconhecido", 200, 428);
      p.ell(120, 600, 44, 44, "#e2453c", 0); p.ell(280, 600, 44, 44, "#3ccf7a", 0);
      g.strokeStyle = "#fff"; g.lineWidth = 9; g.lineCap = "round";
      g.beginPath(); g.moveTo(100, 604); g.quadraticCurveTo(120, 590, 140, 604); g.stroke();
      g.beginPath(); g.moveTo(262, 596); g.quadraticCurveTo(280, 584, 298, 596); g.stroke();
    }
    if (mode === "notif") {
      font(g, 88); g.fillStyle = "#e8eeff"; g.fillText("00:16", 200, 190); font(g, 22); g.fillStyle = "#9fb4e0"; g.fillText("quarta-feira", 200, 250);
      rr(g, 60, 300, 280, 96, 22, "rgba(255,255,255,0.14)", "#000", 0); font(g, 19); g.fillStyle = "#e2453c"; g.textAlign = "left"; g.fillText("3 mensagens", 80, 330);
      g.fillStyle = "#fff"; font(g, 21); g.textAlign = "left"; g.fillText("Número desconhecido", 80, 366, 262);
      if (u > 0) { const sc = 0.85 + 0.15 * u; g.save(); g.translate(200, 470); g.scale(sc, sc); g.globalAlpha = Math.min(1, u * 1.4);
        rr(g, -140, -50, 280, 100, 22, "#f2f4f8", "#000", 0); g.textAlign = "left"; font(g, 21); g.fillStyle = "#3a4f80"; g.textAlign = "left"; g.fillText("Mensagem · agora", -118, -18);
        font(g, 23); g.fillStyle = "#10182c"; g.textAlign = "left"; g.fillText("1 nova mensagem", -118, 20); g.restore(); }
      g.textAlign = "center";
    }
    if (mode === "chat") {
      g.fillStyle = "#0e1730"; g.fillRect(45, 60, 310, 92); p.ell(95, 112, 26, 26, "#3a4f80", 0); font(g, 30); g.fillStyle = "#fff"; g.fillText("?", 95, 114);
      font(g, 20); g.textAlign = "left"; g.fillText("Número desconhecido", 132, 104, 212); font(g, 17); g.textAlign = "left"; g.fillStyle = "#3ccf7a"; g.fillText("online", 132, 130); g.textAlign = "center";
      let y = 186;
      for (let i = Math.max(0, n - 3); i < n; i++) {
        const last = i === n - 1, a = last ? Math.min(1, u * 1.6) : 1, sc = last ? 0.7 + 0.3 * easeOut(u) : 1;
        font(g, 34); const lines = wrap(g, MSGS[i], 236), h = 30 + lines.length * 42;
        g.save(); g.globalAlpha = a; g.translate(62, y); g.scale(sc, sc);
        rr(g, 0, 0, 270, h, 26, last ? "#ffffff" : "#cfd6e6", "#000", 0);
        g.fillStyle = last ? "#c22f28" : "#33405e"; g.textAlign = "left"; lines.forEach((ln, j) => g.fillText(ln, 18, 36 + j * 42));
        font(g, 16); g.fillStyle = "#7d879c"; g.textAlign = "right"; g.fillText(MSG_T[i], 258, h - 14); g.restore(); g.textAlign = "center";
        y += h * sc + 22;
      }
    }
  }
  g.restore();
  rr(g, 160, 30, 80, 16, 8, "#111", "#111", 0);
  if (hand) { // a sua mão segurando o aparelho: dedos dobrados na borda esquerda, polegar na direita, palma embaixo
    const sk = "#ecd0b6", sh = "#c9a88e", ink = "#241726"; g.lineWidth = 7; g.strokeStyle = ink; g.lineJoin = "round";
    g.fillStyle = sk; g.beginPath(); g.moveTo(-10, 760); g.quadraticCurveTo(10, 610, 70, 600); g.lineTo(330, 600); g.quadraticCurveTo(400, 620, 410, 760); g.closePath(); g.fill(); g.stroke();
    for (let i = 0; i < 4; i++) { const y = 400 + i * 52; rr(g, 4, y, 46, 44, 20, i % 2 ? sk : "#f0d6be", ink, 7); }
    g.fillStyle = sk; g.beginPath(); g.moveTo(372, 660); g.quadraticCurveTo(388, 560, 352, 500); g.quadraticCurveTo(330, 486, 318, 512); g.quadraticCurveTo(330, 580, 322, 650); g.closePath(); g.fill(); g.stroke();
    g.fillStyle = sh; g.beginPath(); g.ellipse(200, 700, 120, 26, 0, 0, 7); g.fill();
  }
});
/** brilho frio em volta do celular aceso */
const fxHalo = (p: Pen) => { const g = p.g, gr = g.createRadialGradient(128, 128, 8, 128, 128, 128); gr.addColorStop(0, "rgba(150,190,255,0.75)"); gr.addColorStop(0.4, "rgba(120,160,255,0.25)"); gr.addColorStop(1, "rgba(120,160,255,0)"); g.fillStyle = gr; g.fillRect(0, 0, 256, 256); };
/** luz amarela do poste no chão */
const fxPool = (p: Pen) => { const g = p.g, gr = g.createRadialGradient(256, 256, 10, 256, 256, 256); gr.addColorStop(0, "rgba(255,214,140,0.55)"); gr.addColorStop(0.5, "rgba(255,190,110,0.2)"); gr.addColorStop(1, "rgba(255,190,110,0)"); g.fillStyle = gr; g.fillRect(0, 0, 512, 512); };
/** o motorista de costas: quepe, nuca, orelhas, ombros da camisa */
const fxDriverBack = (p: Pen) => hi(p, 2, (g) => {
  const ink = "#241726";
  g.lineJoin = "round"; g.lineWidth = 10; g.strokeStyle = ink;
  g.fillStyle = "#7fa6d2"; g.beginPath(); g.moveTo(20, 490); g.quadraticCurveTo(30, 330, 130, 300); g.lineTo(270, 300); g.quadraticCurveTo(370, 330, 380, 490); g.closePath(); g.fill(); g.stroke();
  g.strokeStyle = "rgba(36,23,38,0.5)"; g.lineWidth = 5; g.beginPath(); g.moveTo(200, 312); g.lineTo(200, 490); g.stroke(); g.strokeStyle = ink; g.lineWidth = 10;
  g.fillStyle = "#c99067"; g.fillRect(160, 250, 80, 62); g.strokeRect(160, 250, 80, 62);
  p.ell(108, 190, 22, 34, "#c99067", 8); p.ell(292, 190, 22, 34, "#c99067", 8);
  p.ell(200, 175, 95, 108, "#2a201a", 10);
  g.fillStyle = "#23304f"; g.beginPath(); g.moveTo(100, 140); g.quadraticCurveTo(110, 40, 200, 36); g.quadraticCurveTo(290, 40, 300, 140); g.closePath(); g.fill(); g.stroke();
  g.fillStyle = "#e0b43a"; g.fillRect(150, 122, 100, 12);
});
/** o retrovisor: os olhos do motorista. look: -1 desviado .. 0 encarando; ahead = olhando a rua */
const fxMirror = (p: Pen, look: number, ahead: boolean) => hi(p, 2, (g) => {
  rr(g, 10, 10, 440, 150, 30, "#1c1e26", "#241726", 10);
  g.save(); g.beginPath(); g.roundRect(26, 24, 408, 122, 20); g.clip();
  g.fillStyle = "#1d2840"; g.fillRect(0, 0, 460, 170);
  g.fillStyle = "#c99067"; g.fillRect(60, 30, 340, 130);
  g.fillStyle = "#23304f"; g.fillRect(40, 0, 380, 44); g.fillStyle = "#151d33"; g.fillRect(40, 40, 380, 10);
  const ex = ahead ? 10 : look * 26, lid = ahead ? 0.25 : look < -0.5 ? 0.35 : 0;
  for (const cx of [160, 300]) {
    g.fillStyle = "#2a201a"; g.save(); g.translate(cx, 66); g.rotate(cx < 230 ? 0.16 : -0.16); g.fillRect(-48, -8, 96, 15); g.restore();
    p.ell(cx, 102, 42, 26, "#fbf7ef", 6); p.ell(cx + ex, 104, 15, 16, "#241726", 0); p.ell(cx + ex + 5, 98, 4, 4, "#ffffff", 0);
    if (lid > 0) { g.fillStyle = "#b07a55"; g.fillRect(cx - 44, 76, 88, 52 * lid); g.strokeStyle = "#241726"; g.lineWidth = 5; g.beginPath(); g.moveTo(cx - 42, 76 + 52 * lid); g.lineTo(cx + 42, 76 + 52 * lid); g.stroke(); }
  }
  g.fillStyle = "rgba(255,255,255,0.12)"; g.beginPath(); g.moveTo(26, 24); g.lineTo(120, 24); g.lineTo(40, 146); g.lineTo(26, 146); g.closePath(); g.fill();
  g.restore();
});

const YOU: Who = { i: 900, o: MODERN(2), okey: "you2" };
const fwdOf = (cam: CamInfo) => { const x = cam.right.z, z = -cam.right.x, n = Math.hypot(x, z) || 1; return [x / n, z / n]; };
const buzz = (t: number, a: number, b: number) => (t >= a && t < b ? 0.006 * Math.sign(Math.sin(t * 90)) * ((t - a) % 0.9 < 0.55 ? 1 : 0) : 0);
/** estado da tela do celular em cada plano */
const callState = (id: number, t: number): [CallMode, number, number] => {
  const ringU = q((t * 1.4) % 1, 12);
  switch (id) {
    case 6: return t >= W.vibra - 0.05 ? ["notif", 0, q(clamp01((t - W.vibra + 0.05) / 0.35), 12)] : ["dark", 0, 0];
    case 7: return ["chat", 4, q(clamp01((t - W.boa + 0.1) / 0.35), 12)];
    case 16: return t >= W.tocar - 0.45 ? ["ring", 0, ringU] : ["dark", 0, 0];
    case 17: case 18: return ["ring", 0, ringU];
    default: return ["dark", 0, 0];
  }
};
const ringing = (id: number, t: number) => { const [m] = callState(id, t); return m === "ring"; };
/** o celular deitado no assento do banco da frente (tamanho real, tela para cima, topo para o encosto). Tocando, ele vibra e
 *  "anda" alguns milímetros e gira um pouco; com o ônibus andando, treme junto com o banco */
const phoneOnSeat = (id: number, t: number, out: Stage, _cam: CamInfo) => {
  const [m, n, u] = callState(id, t), r = ringing(id, t), mov = busMoving(id, t);
  const walk = r ? 0.004 * Math.sin(t * 2.1) : 0, jx = (r ? buzz(t, 0, 999) * 0.5 : 0) + (mov ? 0.0015 * Math.sin(t * 37) : 0);
  const [x, y, z] = L(id, t, FRONT_SEAT[0] + 0.03 + jx, CUSHION_Y + 0.007, FRONT_SEAT[2] + walk);
  const rot = Math.PI / 2 + 0.12 + (r ? 0.05 * Math.sin(t * 1.3) + (buzz(t, 0, 999) ? 0.015 : 0) : 0);
  if (m !== "dark") { const s2 = m === "ring" ? q(0.42 + 0.06 * Math.sin(t * 18), 40) : 0.32;   // luz da tela no tecido do banco
    out.fx.push({ key: "halo", cw: 256, ch: 256, draw: fxHalo, soft: true, flat: true, x, y: y - 0.003, z, w: s2, h: s2 }); }
  out.fx.push({ key: `phF|${m}|${n}|${u}`, cw: 800, ch: 1520, draw: (pp) => fxCall(pp, m, n, u, 2), x, y, z, w: 0.078, h: 0.158, flat: true, rot: q(rot, 200) });
};
/** o celular "na mão", enchendo a tela */
const phoneNear = (id: number, t: number, out: Stage) => {
  const [m, n, u] = callState(id, t), jx = m === "ring" ? buzz(t, 0, 999) * 0.35 : 0;
  const [x, y, z] = L(id, t, PHONE_NEAR[id][0], PHONE_NEAR[id][1], PHONE_NEAR[id][2] + jx);
  out.fx.push({ key: `phN|${m}|${n}|${u}`, cw: 800, ch: 1520, draw: (pp) => fxCall(pp, m, n, u, 2, true), x, y, z, w: 0.155, h: 0.295 });
};
const driver = (id: number, t: number, out: Stage) => {
  const [x, y, z] = L(id, t, 5.0, 1.36, -0.73);
  out.fx.push({ key: "drvBack", cw: 800, ch: 1000, draw: fxDriverBack, x, y, z, w: 0.62, h: 0.78 });
};
const mirror = (id: number, t: number, out: Stage, look: number, ahead: boolean) => {
  const [x, y, z] = L(id, t, 5.78, 2.24, 0);
  out.fx.push({ key: `mir|${q(look, 10)}|${ahead}`, cw: 920, ch: 340, draw: (pp) => fxMirror(pp, look, ahead), x, y, z, w: 0.5, h: 0.185 });
};
/** luz do ônibus no chão (planos de fora): faróis na pista à frente, janelas acesas dos dois lados, porta aberta na calçada */
const fxHead = (p: Pen) => { const g = p.g, gr = g.createRadialGradient(80, 128, 4, 80, 128, 420); gr.addColorStop(0, "rgba(255,244,214,0.55)"); gr.addColorStop(0.45, "rgba(255,240,205,0.2)"); gr.addColorStop(1, "rgba(255,240,205,0)"); g.fillStyle = gr; g.fillRect(0, 0, 512, 256); };
const fxSpill = (p: Pen) => { const g = p.g, gr = g.createLinearGradient(0, 0, 0, 128); gr.addColorStop(0, "rgba(190,215,255,0.32)"); gr.addColorStop(1, "rgba(190,215,255,0)"); g.fillStyle = gr; g.fillRect(0, 0, 512, 128);
  g.globalCompositeOperation = "destination-out"; for (let x = 0; x < 512; x += 64) g.fillRect(x, 0, 6, 128); };
const busLight = (id: number, t: number, out: Stage) => {
  const bx = busX(id, t), off = intOff(t);
  out.fx.push({ key: "beam", cw: 512, ch: 256, draw: fxHead, soft: true, flat: true, x: bx + 6 + 4.2, y: D0 + 0.05, z: BZ, w: 9, h: 3.6 });
  if (!off) for (const sv of [-1, 1])
    out.fx.push({ key: "spill", cw: 512, ch: 128, draw: fxSpill, soft: true, flat: true, x: bx - 0.3, y: D0 + (sv > 0 ? 0.075 : 0.045), z: BZ + sv * 2.0, w: 11.2, h: 1.5, rot: sv > 0 ? Math.PI : 0 });
};
const pool = (t: number, out: Stage) => { if (!poleOff(t)) out.fx.push({ key: "pool", cw: 512, ch: 512, draw: fxPool, soft: true, flat: true, x: POLE_X + 0.6, y: D0 + 0.08, z: POLE_Z + 0.4, w: 5.5, h: 4.2 }); };

/** alguém sentado no fundo: só a silhueta (cabeça, ombros, tronco), sem rosto; borda fria da lâmpada de cima */
const fxShadowMan = (p: Pen) => hi(p, 2, (g) => {
  g.fillStyle = "#07080d"; g.strokeStyle = "rgba(150,175,220,0.55)"; g.lineWidth = 6; g.lineJoin = "round";
  g.beginPath(); g.moveTo(30, 500); g.quadraticCurveTo(36, 300, 120, 268); g.lineTo(150, 250); g.quadraticCurveTo(200, 236, 250, 250);
  g.lineTo(280, 268); g.quadraticCurveTo(364, 300, 370, 500); g.closePath(); g.fill(); g.stroke();
  g.beginPath(); g.ellipse(200, 160, 74, 92, 0, 0, 7); g.fill(); g.stroke();
  g.fillStyle = "#07080d"; g.fillRect(168, 236, 64, 40);
});
/** poça de luz laranja das lâmpadas de sódio no piso da garagem */
const fxSodium = (p: Pen) => { const g = p.g, gr = g.createRadialGradient(256, 256, 10, 256, 256, 256); gr.addColorStop(0, "rgba(255,170,80,0.42)"); gr.addColorStop(0.5, "rgba(255,150,60,0.14)"); gr.addColorStop(1, "rgba(255,150,60,0)"); g.fillStyle = gr; g.fillRect(0, 0, 512, 512); };
const sodiumPools = (id: number, t: number, cam: CamInfo, out: Stage) => {
  if (garageOff(id, t)) return;
  for (let x = GX - 17; x < GX + 40; x += 6) for (const z of [-26, -17.25, -8.25, 2.0, 10.5]) {
    if (Math.hypot(x - cam.pos.x, z - cam.pos.z) > 60) continue;
    out.fx.push({ key: "sod", cw: 512, ch: 512, draw: fxSodium, soft: true, flat: true, x, y: D0 + 0.06, z, w: 7, h: 7 });
  }
};

const onibus = (id: number, cam: CamInfo, t: number, out: Stage) => {
  const c = SHOTS[id - 1].crowd;
  const SEAT_H = (CUSHION_Y - FLOOR_Y) / SU;
  const seated = (u: number, v: number, fo: FrontOpts, yaw?: number) => {
    const [x, , z] = L(id, t, u + 0.36, 0, v), sway = busMoving(id, t) ? q(0.012 * Math.sin(t * 2.3) + 0.005 * Math.sin(t * 7.1), 300) : 0;
    const pl = person(cam, YOU, x, FLOOR_Y, z, { side: false, mirror: false }, { ...fo, mode: "sit", seatH: SEAT_H }, {}); pl.roll = sway; if (yaw !== undefined) pl.yaw = yaw;
    out.places.push(pl); blob(out, x, FLOOR_Y, z);
  };
  if (["c_leave"].includes(c)) pool(t, out);
  if (["c_leave", "c_sign", "c_dark", "c_enter", "c_rows", "c_choice", "c_cta", "c_optB"].includes(c)) busLight(id, t, out);
  if (inGarage(id) && !SHOTS[id - 1].inside) sodiumPools(id, t, cam, out);
  switch (c) {
    case "c_vibra": phoneOnSeat(id, t, out, cam); break;
    case "c_screen": phoneNear(id, t, out); break;
    case "c_mirror": mirror(id, t, out, 1.15, false); break;
    case "c_someone": if (someoneAt(id, t)) { const [x, y, z] = L(id, t, -5.38, 1.36, 0.85); out.fx.push({ key: "shadowMan", cw: 800, ch: 1000, draw: fxShadowMan, x, y, z, w: 0.62, h: 0.78 }); } break;
    case "c_speak": driver(id, t, out); mirror(id, t, out, t < W.fala ? 1.15 : 0, false); break;
    case "c_you5": seated(FRONT_SEAT[0], FRONT_SEAT[2], { expr: t >= W.cinco ? "shock" : "nervous", blink: lidAt(t, 900, [W.cinco]), look: q(Math.sin(t * 2.2) * 0.6, 4) }); phoneOnSeat(id, t, out, cam); break;
    case "c_optB": { const [x, , z] = L(id, t, (DOOR_U[0] + DOOR_U[1]) / 2, 0, 1.2);
      out.places.push(person(cam, YOU, x, D0 + 0.4, z, { side: false, mirror: false }, { mode: "stand", expr: "nervous", blink: lidAt(t, 900), look: q(Math.sin(t * 1.3) * 0.8, 4) }, {}));
      blob(out, x, D0 + 0.4, z); break; }
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
  if (s.crowd.startsWith("c_")) onibus(id, cam, t, out);
  return out;
};
export { FPS, T_WAR, T_NOT, smooth, clamp01 };
