// "A torre que uma guerra salvou": our 15 s short in the flat-characters-in-a-3D-toon-world style.
// Timeline: 4 shots timed to the narration (estimates until the voice arrives; retime LINES then).
//   S1 hook, today: leaning tower, tourists posing  | "A torre mais famosa da Itália só tá de pé porque uma guerra parou a obra."
//   S2 1178: two floors, the tower sinks, masons shocked | "No segundo andar, ela começou a afundar."
//   S3 war: soldiers march past the stump, then dusk     | "A guerra parou tudo por cem anos, o barro firmou…"
//   S5 1272: the rest goes up, bent back (the curve)     | "Quando voltaram, fizeram o resto torto pro outro lado, pra disfarçar…"
//   S6 today: the finished tower stands, tourists cheer  | "…e ela não caiu."
export const FPS = 30;
// Vídeo 11 "E se faltasse luz por 3 dias?": narração inteira (72,52 s). Tempos das palavras em analysis/narracao/11_words.json.
export const TOTAL = 2176;
export const T0 = 0;
export const D0 = 0; // ground height (m)
export type V3 = [number, number, number];

export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const smooth = (x: number) => { const u = clamp01(x); return u * u * (3 - 2 * u); };
export const easeOut = (u: number) => 1 - (1 - clamp01(u)) ** 4;

/** tempos das palavras (s) */
export const W = {
  naoE: 3.94, amapa: 7.08, escuro: 7.82, quatroDias: 8.8, em2024: 10.2, temporal: 11.96, milhoes: 13.76, saoPaulo: 15.78,
  hora: 17.24, apaga: 18.56, geladeira: 19.78, horas: 22.1, depois: 23.32, carne: 24.22, risco: 25.66,
  dia1: 26.86, predios: 28.42, bomba: 30.24, semLuz: 31.48, caixa: 32.54, secando: 33.4,
  dia2: 34.86, antenas: 36.12, gerador: 38.0, bateria: 38.78, falham: 39.8, some: 41.1, maquininha: 41.82, pix: 43.42, passa: 44.12,
  ai: 44.96, celular: 46.94, lanterna: 48.12, radio: 49.04, avisar: 50.94, bem: 51.96,
  porIsso: 52.22, carga: 54.02, powerbank: 55.4, gruda: 59.12, carrega: 60.78,
  dia3: 62.72, volta: 63.86, preparou: 65.66, diferente: 67.3, inscrever: 69.46, proximo: 71.3, ese: 72.0,
};
export const T_OFF = W.apaga, T_FRIDGE = W.geladeira, T_HOURS = W.horas;
// nomes antigos ainda importados pelo cast.ts (multidões da Pisa, não usadas aqui)
export const T_SINK = 999, T_WAR = 999, T_NOT = 999;

// ---------------- sets (cada cenário num canto do mundo) ----------------
export const SET = { street: [0, 0] as const, kitchen: [200, 0] as const, building: [-200, 0] as const, antenna: [400, 0] as const, shop: [400, 120] as const, room: [600, 0] as const };

// ---------------- shots ----------------
export type Light = "day" | "golden" | "night";
export type Crowd = "tourists" | "masons" | "soldiers" | "none" | "cheer" | "family" | "fridge"
  | "hook" | "storm" | "building" | "antenna" | "shop" | "room" | "product" | "relief" | "cta";
export type ShotDef = { id: number; a: number; b: number; light: Light; crowd: Crowd };
const F = (t: number) => Math.round(t * FPS);
export const SHOTS: ShotDef[] = [
  { id: 1, a: 0, b: F(W.naoE) - 1, light: "golden", crowd: "hook" },              // casa acesa, família
  { id: 2, a: F(W.naoE) - 1, b: F(W.em2024) - 1, light: "night", crowd: "none" },  // Amapá: bairro inteiro no escuro (aéreo)
  { id: 3, a: F(W.em2024) - 1, b: F(W.hora) - 1, light: "night", crowd: "storm" }, // temporal em SP
  { id: 4, a: F(W.hora) - 1, b: F(W.apaga) - 1, light: "golden", crowd: "family" },// hora zero
  { id: 5, a: F(W.apaga) - 1, b: F(W.geladeira) - 2, light: "night", crowd: "family" }, // tudo apaga
  { id: 6, a: F(W.geladeira) - 2, b: F(W.dia1) - 1, light: "night", crowd: "fridge" },  // cozinha
  { id: 7, a: F(W.dia1) - 1, b: F(W.dia2) - 1, light: "day", crowd: "building" },  // prédio e caixa d'água
  { id: 8, a: F(W.dia2) - 1, b: F(W.maquininha) - 2, light: "day", crowd: "antenna" }, // antena
  { id: 9, a: F(W.maquininha) - 2, b: F(W.ai) - 1, light: "day", crowd: "shop" },   // maquininha e Pix
  { id: 10, a: F(W.ai) - 1, b: F(W.porIsso) - 1, light: "night", crowd: "room" },   // o celular: lanterna, rádio, aviso
  { id: 11, a: F(W.porIsso) - 1, b: F(W.dia3) - 1, light: "night", crowd: "product" }, // power bank
  { id: 12, a: F(W.dia3) - 1, b: F(W.diferente) + 3, light: "golden", crowd: "relief" }, // a luz volta
  { id: 13, a: F(W.diferente) + 3, b: TOTAL, light: "golden", crowd: "cta" },        // inscreva-se
];
export const XFADE: Record<number, number> = {};
export const FLASH_AT = -100;
export const shotAt = (f: number) => SHOTS.find((s) => f >= s.a && f < s.b) ?? SHOTS[SHOTS.length - 1];
export const layersAt = (f: number): { id: number; alpha: number }[] => [{ id: shotAt(f).id, alpha: 1 }];

// ---------------- the tower ----------------
// floor 0 = ground arcade (11 m), floors 1-6 = loggias (6.8 m), 7 = bell chamber. Leans toward +x (screen right from
// the south cameras). Upper floors (4+) were built taller on the low side: each bends back by CURVE (the "banana").
export const FLOOR_H = [11, 6.8, 6.8, 6.8, 6.8, 6.8, 6.8, 6.5];
export const R_OUT = 7.7;
export const CURVE = 0.55; // degrees per floor above the third
export type TowerState = { floors: number; tilt: number; sink: number; scaffold: boolean };
export const towerState = (_id: number, _t: number): TowerState => ({ floors: 0, tilt: 0, sink: 0, scaffold: false });
export const towerStatePisa = (id: number, t: number): TowerState => {
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

const S0 = (id: number) => SHOTS[id - 1].a;
const CAMS: Record<number, Key[]> = {
  // gancho: grua descendo até a altura dos olhos na frente da família, casas acesas
  1: [{ f: 0, s: () => ({ pos: [6.0, 6.5, -9], look: [6.0, 2.2, 14], fov: 48 }) },
      { f: 2, dur: 112, s: (f) => dolly([6.0, 1.9, 1.2], [6.0, 1.25, 10], f, 0, 0.0018, { fov: 50, roll: 0.02 }) }],
  // Amapá: o bairro inteiro apagado visto do alto, a câmera avança devagar
  2: [{ f: 0, s: (f) => dolly([-4, 24, -30], [6, 1, 22], f, S0(2), 0.0022, { fov: 46, roll: -0.02 }) }],
  // temporal em SP: rua com chuva, árvore caída, gente assustada
  3: [{ f: 0, s: (f) => dolly([2.5, 1.8, 1.6], [6.0, 1.4, 9], f, S0(3), 0.0024, { fov: 48, roll: 0.03 }) }],
  // hora zero / tudo apaga: a mesma câmera (o corte é só de luz)
  4: [{ f: 0, s: (f) => dolly([6.0, 1.9, 1.2], [6.0, 1.25, 10], f, S0(4), 0.0022, { fov: 50, roll: 0.02 }) }],
  5: [{ f: 0, s: (f) => dolly([6.0, 1.9, 1.2], [6.0, 1.25, 10], f, S0(4), 0.0022, { fov: 50, roll: 0.02 }) }],
  // cozinha: geladeira e relógio
  6: [{ f: 0, s: (f) => dolly([200.1, 1.45, -3.5], [200.3, 1.35, 4], f, S0(6), 0.0026, { fov: 50, roll: -0.02 }) }],
  // prédio: olha a caixa d'água lá em cima, depois desce até a torneira seca
  7: [{ f: 0, s: (f) => dolly([-195.5, 1.6, -9], [-200, 15.5, 9], f, S0(7), 0.0015, { fov: 52 }) },
      { f: F(W.semLuz) - 6, dur: 30, s: (f) => dolly([-196.5, 1.5, 1.5], [-198.3, 1.25, 8], f, F(W.semLuz), 0.0025, { fov: 48, roll: 0.02 }) }],
  // antena com gerador; a câmera sobe com a torre
  8: [{ f: 0, s: (f) => dolly([396.5, 1.6, -5], [400, 6.5, 20], f, S0(8), 0.0018, { fov: 52 }) },
      { f: F(W.falham) - 4, dur: 28, s: (f) => dolly([397.5, 1.55, 0.5], [398.6, 1.5, 7], f, F(W.falham), 0.003, { fov: 46, roll: -0.03 }) }],
  // a loja: maquininha sem sinal e o Pix que não passa
  9: [{ f: 0, s: (f) => dolly([400.0, 1.55, 116.3], [400.0, 1.3, 121], f, S0(9), 0.003, { fov: 46, roll: 0.02 }) }],
  // a sala no escuro: o celular vira lanterna, rádio e o jeito de avisar
  10: [{ f: 0, s: (f) => dolly([600.0, 1.35, -1.9], [600.0, 1.0, 3.2], f, S0(10), 0.0022, { fov: 48 }) }],
  // o power bank grudando atrás do celular (close)
  11: [{ f: 0, s: (f) => dolly([600.0, 1.3, -0.6], [600.0, 1.2, 3.0], f, S0(11), 0.0016, { fov: 40, roll: -0.015 }) }],
  // dia três: a luz volta em onda pela rua
  12: [{ f: 0, s: (f) => dolly([4.8, 1.9, 1.0], [6.0, 1.3, 10], f, S0(12), 0.0024, { fov: 52, roll: -0.02 }) }],
  // CTA: a família acenando para a câmera
  13: [{ f: 0, s: (f) => dolly([6.0, 1.75, 2.3], [6.0, 1.35, 10], f, S0(13), 0.0022, { fov: 46, roll: 0.015 }) }],
};
/** impact kicks: flip sign every frame, decay over 7 frames */
const KICKS = [W.apaga, W.passa, W.gruda];
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
const FOC: Record<number, [number, V3]> = {
  1: [7, [6, 1.4, 7.4]], 2: [3, [6, 1, 14]], 3: [8, [5.4, 1.4, 7.6]], 4: [8, [6, 1.4, 7.3]], 5: [8, [6, 1.4, 7.3]],
  6: [10, [200.4, 1.3, 3.0]], 7: [5, [-200, 10, 9]], 8: [5, [400, 8, 20]], 9: [12, [400, 1.3, 119.8]],
  10: [10, [600, 1.0, 2.6]], 11: [14, [600, 1.2, 1.9]], 12: [7, [6, 1.4, 7.4]], 13: [9, [6, 1.4, 6.8]],
};
export const DOF: Dof[] = SHOTS.map((s) => ({ f: s.a, cInf: FOC[s.id][0], focus: () => FOC[s.id][1] }));
DOF.splice(7, 0, { f: F(W.semLuz) + 6, cInf: 10, focus: () => [-198.2, 1.2, 7.6] });
DOF.splice(9, 0, { f: F(W.falham) + 8, cInf: 10, focus: () => [398.6, 1.4, 6.6] });
export const dofAt = (f: number) => {
  let i = 0; while (i + 1 < DOF.length && f >= DOF[i + 1].f) i++;
  const d = DOF[i], p = DOF[Math.max(0, i - 1)];
  const k = d.dur ? Math.min(1, (f - d.f) / d.dur) : 1;
  return { cInf: p.cInf + (d.cInf - p.cInf) * k, focus: d.focus };
};
export type Fg = { a: number; b: number; kit: string; pos: V3; s?: number; yaw?: number };
export const FOREGROUND: Fg[] = [];
