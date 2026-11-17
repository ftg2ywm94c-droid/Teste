// "A torre que uma guerra salvou": our 15 s short in the flat-characters-in-a-3D-toon-world style.
// Timeline: 4 shots timed to the narration (estimates until the voice arrives; retime LINES then).
//   S1 hook, today: leaning tower, tourists posing  | "A torre mais famosa da Itália só tá de pé porque uma guerra parou a obra."
//   S2 1178: two floors, the tower sinks, masons shocked | "No segundo andar, ela começou a afundar."
//   S3 war: soldiers march past the stump, then dusk     | "A guerra parou tudo por cem anos, o barro firmou…"
//   S5 1272: the rest goes up, bent back (the curve)     | "Quando voltaram, fizeram o resto torto pro outro lado, pra disfarçar…"
//   S6 today: the finished tower stands, tourists cheer  | "…e ela não caiu."
export const FPS = 30;
export const TOTAL = 378; // synced to Davi's narration (12.6 s, starts 233.40 s in the long video)
export const D0 = 0; // ground height (m)
export type V3 = [number, number, number];

export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const smooth = (x: number) => { const u = clamp01(x); return u * u * (3 - 2 * u); };
export const easeOut = (u: number) => 1 - (1 - clamp01(u)) ** 4;

/** narration word times (s) the action keys on */
export const T_SINK = 5.06;  // "afundar"
export const T_WAR = 5.5;    // "guerra"
export const T_FIRM = 7.66;  // "firmou"
export const T_NOT = 11.5;   // "não caiu"

// ---------------- shots ----------------
export type Light = "day" | "golden";
export type Crowd = "tourists" | "masons" | "soldiers" | "none" | "cheer";
export type ShotDef = { id: number; a: number; b: number; light: Light; crowd: Crowd };
export const SHOTS: ShotDef[] = [
  { id: 1, a: 0, b: 108, light: "day", crowd: "tourists" },
  { id: 2, a: 108, b: 163, light: "day", crowd: "masons" },
  { id: 3, a: 163, b: 212, light: "day", crowd: "soldiers" },
  { id: 4, a: 212, b: 242, light: "golden", crowd: "none" },
  { id: 5, a: 242, b: 330, light: "day", crowd: "none" },
  { id: 6, a: 330, b: TOTAL, light: "day", crowd: "cheer" },
];
export const XFADE: Record<number, number> = { 4: 10, 5: 8, 6: 8 };
export const FLASH_AT = 108;
export const shotAt = (f: number) => SHOTS.find((s) => f >= s.a && f < s.b) ?? SHOTS[SHOTS.length - 1];
export const layersAt = (f: number): { id: number; alpha: number }[] => {
  for (const s of SHOTS) {
    const x = XFADE[s.id];
    if (x && f >= s.a - x / 2 && f < s.a + x / 2) return [{ id: s.id - 1, alpha: 1 }, { id: s.id, alpha: (f - (s.a - x / 2) + 1) / (x + 1) }];
  }
  return [{ id: shotAt(f).id, alpha: 1 }];
};

// ---------------- the tower ----------------
// floor 0 = ground arcade (11 m), floors 1-6 = loggias (6.8 m), 7 = bell chamber. Leans toward +x (screen right from
// the south cameras). Upper floors (4+) were built taller on the low side: each bends back by CURVE (the "banana").
export const FLOOR_H = [11, 6.8, 6.8, 6.8, 6.8, 6.8, 6.8, 6.5];
export const R_OUT = 7.7;
export const CURVE = 0.55; // degrees per floor above the third
export type TowerState = { floors: number; tilt: number; sink: number; scaffold: boolean };
export const towerState = (id: number, t: number): TowerState => {
  switch (id) {
    case 2: { const k = smooth((t - T_SINK + 0.15) / 0.9); return { floors: 3, tilt: 0.3 + 4.5 * k, sink: 0.8 * k, scaffold: true }; }
    case 3: case 4: return { floors: 3, tilt: 4.8, sink: 0.8, scaffold: false };
    // 1272-1372: the rest goes up floor by floor, each upper one bent back (the curve), the lean keeps growing
    case 5: { const u = clamp01((t - 242 / FPS - 0.2) / 2.3); return { floors: 3 + Math.min(5, Math.floor(u * 5.999)), tilt: 4.8 + 2.2 * u, sink: 0.8 + 0.2 * u, scaffold: u < 0.98 }; }
    default: return { floors: 8, tilt: 7.0, sink: 1.0, scaffold: false };
  }
};

// ---------------- camera ----------------
export type Cam = { pos: V3; look: V3; fov: number; roll: number };
type Shot = Partial<Cam> & { pos: V3; look: V3 };
type Key = { f: number; dur?: number; cut?: boolean; s: (f: number) => Shot };
export const glide = (u: number) => { const x = clamp01(u); return x * x * x * (x * (6 * x - 15) + 10); };
const mix = (a: Cam, b: Cam, k: number): Cam => ({
  pos: a.pos.map((v, i) => v + (b.pos[i] - v) * k) as V3, look: a.look.map((v, i) => v + (b.look[i] - v) * k) as V3,
  fov: a.fov + (b.fov - a.fov) * k, roll: a.roll + (b.roll - a.roll) * k,
});
const full = (c: Shot): Cam => ({ fov: 40, roll: 0, ...c });
const run = (keys: Key[], f: number) => {
  let cur = full(keys[0].s(f));
  for (let i = 1; i < keys.length; i++) {
    const k = keys[i];
    if (f < k.f) break;
    cur = k.cut ? full(k.s(f)) : mix(cur, full(k.s(f)), glide((f - k.f) / (k.dur ?? 24)));
  }
  return cur;
};
/** every hold creeps in: dolly toward the look point by rate per frame since f0 */
/** every hold creeps in: a slow zoom (the lens stays put, so the foreground cast never leaves the frame) */
const dolly = (pos: V3, look: V3, f: number, f0: number, rate = 0.0025, rest: Partial<Cam> = {}): Shot => {
  const k = Math.exp(-rate * Math.max(0, f - f0)), fov = rest.fov ?? 40;
  return { pos, look, ...rest, fov: (360 / Math.PI) * Math.atan(Math.tan((fov * Math.PI) / 360) * k) };
};

const CAMS: Record<number, Key[]> = {
  // hook: low behind the tourists "holding up" the tower, then tilt up to its top
  1: [
    { f: 0, s: (f) => dolly([-1, 1.5, -86], [2, 14, 0], f, 0, 0.0015, { fov: 54, roll: 0.02 }) },
    { f: 58, dur: 40, s: (f) => dolly([-1.5, 2.0, -86], [4, 34, 0], f, 58, 0.001, { fov: 50, roll: 0.05 }) },
  ],
  // 1178: masons in front, the stump behind them sinking on "afundar"
  2: [{ f: 108, s: (f) => dolly([14, 1.7, -36], [3.5, 7.5, 0], f, 108, 0.0022, { fov: 48, roll: -0.04 }) }],
  // the war: soldiers march across the frame in front of the stump
  3: [{ f: 163, s: (f) => dolly([-2, 2.2, -44], [2, 6.5, 0], f, 163, 0.002, { fov: 48 }) }],
  // a century later, dusk: the stump alone
  4: [{ f: 204, s: (f) => dolly([12, 3, -55], [2, 12, 0], f, 204, 0.0025, { fov: 40, roll: 0.03 }) }],
  // the rest goes up: wide side view so the curve reads
  5: [{ f: 236, s: (f) => dolly([46, 3, -74], [3, 27, 0], f, 236, 0.0015, { fov: 50, roll: -0.03 }) }],
  // today: the finished tower stands, cheering tourists in front
  6: [{ f: 322, s: (f) => dolly([-1.5, 1.6, -92], [2.5, 15, 0], f, 322, 0.0014, { fov: 54, roll: 0.02 }) }],
};
/** impact kicks: flip sign every frame, decay over 7 frames */
const KICKS = [T_SINK];
export const kickAt = (t: number) => {
  for (const k of KICKS) { const n = Math.round((t - k) * FPS); if (n >= 0 && n < 7) return (n % 2 ? -1 : 1) * (1 - n / 7); }
  return 0;
};
export const camAt = (id: number, f: number): Cam => {
  const c = run(CAMS[id], f), a = kickAt(f / FPS);
  if (!a) return c;
  const d: V3 = [c.look[0] - c.pos[0], c.look[1] - c.pos[1], c.look[2] - c.pos[2]];
  const L = Math.hypot(...d), h = Math.hypot(d[0], d[2]) || 1;
  const m = (3 / 640) * Math.tan((c.fov * Math.PI) / 360) * L * a * 2.5;
  return { ...c, look: [c.look[0] - (d[2] / h) * m, c.look[1] + 0.6 * m, c.look[2] + (d[0] / h) * m], roll: c.roll + a * 0.006 };
};

// ---------------- lens blur per beat (cInf px at 1080; 0 = sharp) ----------------
export type Dof = { f: number; dur?: number; cInf: number; focus?: (f: number) => V3 };
export const DOF: Dof[] = [
  { f: 0, cInf: 9, focus: () => [0, 1.6, -80.5] },
  { f: 58, dur: 26, cInf: 0 },
  { f: 108, cInf: 10, focus: () => [12.5, 1.5, -28.5] },
  { f: 163, cInf: 8, focus: () => [-2, 1.5, -34] },
  { f: 204, cInf: 0 },
  { f: 242, cInf: 0 },
  { f: 330, cInf: 7, focus: () => [0, 1.5, -86] },
];
export const dofAt = (f: number) => {
  let i = 0; while (i + 1 < DOF.length && f >= DOF[i + 1].f) i++;
  const d = DOF[i], p = DOF[Math.max(0, i - 1)];
  const k = d.dur ? Math.min(1, (f - d.f) / d.dur) : 1;
  return { cInf: p.cInf + (d.cInf - p.cInf) * k, focus: d.focus };
};
export type Fg = { a: number; b: number; kit: string; pos: V3; s?: number; yaw?: number };
export const FOREGROUND: Fg[] = [];
