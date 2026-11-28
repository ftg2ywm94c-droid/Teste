// "A torre que uma guerra salvou": our 15 s short in the flat-characters-in-a-3D-toon-world style.
// Timeline: 4 shots timed to the narration (estimates until the voice arrives; retime LINES then).
//   S1 hook, today: leaning tower, tourists posing  | "A torre mais famosa da Itália só tá de pé porque uma guerra parou a obra."
//   S2 1178: two floors, the tower sinks, masons shocked | "No segundo andar, ela começou a afundar."
//   S3 war: soldiers march past the stump, then dusk     | "A guerra parou tudo por cem anos, o barro firmou…"
//   S5 1272: the rest goes up, bent back (the curve)     | "Quando voltaram, fizeram o resto torto pro outro lado, pra disfarçar…"
//   S6 today: the finished tower stands, tourists cheer  | "…e ela não caiu."
export const FPS = 30;
// Vídeo 14 "Vendaval · Ep. 2": continuação do vídeo 12 (a maioria escolheu B). Narração 67,4 s.
// Tempos das palavras em projeto_videos3d/analysis/narracao/14_words.json.
export const TOTAL = 2022;
export const T0 = 0;
export const D0 = 0; // ground height (m)
export type V3 = [number, number, number];

export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const smooth = (x: number) => { const u = clamp01(x); return u * u * (3 - 2 * u); };
export const easeOut = (u: number) => 1 - (1 - clamp01(u)) ** 4;

/** tempos das palavras (s) */
export const W = {
  maioria: 0.26, banheiro: 2.04, porta: 2.86, trancada: 3.38, celular: 4.34, oito: 5.08, lanterna: 6.66, la: 8.14, uiva: 9.7,
  ai: 10.44, estrondo: 11.48, casa: 12.3, treme: 13.18, vidro: 14.02, telha: 15.16, depois: 16.54, silencio: 17.9,
  arvore: 18.78, caiu: 19.48, sala: 21.38, voce: 21.96, inteiro: 22.38, aguentou: 23.6, mas: 24.4, pingando: 25.52,
  e1: 27.34, cheiro: 27.66, queimado: 28.12, voceAbre: 29.6, fresta: 30.8, a2: 32.22, escuro: 33.02, galhos: 34.08,
  noChao: 34.92, janela: 36.44, fio: 37.98, faisca: 39.78, ai2: 40.78, vibra: 41.66, seis: 42.62, e2: 43.76, vizinha: 44.34,
  preso: 46.4, opcaoA: 48.3, atravessa: 49.58, opcaoB: 53.22, liga: 55.86, bombeiros: 56.38, n193: 57.0, comenta: 58.3,
  mais: 60.88, se: 63.66, inscreve: 63.9, ese: 66.58,
  // nomes do vídeo 12 ainda usados pelo código herdado
  apaga: -1, estalo: 999, inclinando: 999, celular2: 999, direcao: 999, pisca: 999, dobrar: 0, vento: -1,
};
export const T_OFF = -1, T_FRIDGE = 999, T_HOURS = 999, T_SINK = 999, T_WAR = 999, T_NOT = 999;

// ---------------- sets ----------------
export const SET = { street: [0, 0] as const, room: [600, 0] as const, bath: [800, 0] as const };

// ---------------- vento, chuva e a queda da árvore ----------------
/** vento 0..1: tempestade forte até o estrondo, depois baixa até o "silêncio" e fica fraco */
export const windAt = (_id: number, t: number) => (t < W.casa ? 1.0 : t < W.silencio ? 1.0 - 0.72 * smooth((t - W.casa) / (W.silencio - W.casa)) : 0.28);
/** queda da árvore: haste rígida girando na base, theta'' = (3g / 2L) sin(theta), de 0,27 rad (fim do vídeo 12) até bater na casa
 *  no "estrondo"; depois um quique pequeno e amortecido. Integração feita uma vez (60 passos por quadro). */
const TH0 = 0.27, TH_HIT = 0.62, LTREE = 10.5, G = 9.81;
const FALL: number[] = (() => { const out = [TH0]; let th = TH0, w = 0; const dt = 1 / 1800;
  for (let i = 0; th < TH_HIT && i < 1e6; i++) { w += (3 * G / (2 * LTREE)) * Math.sin(th) * dt; th += w * dt; if (i % 60 === 59) out.push(Math.min(th, TH_HIT)); }
  return out; })();
export const FALL_DUR = (FALL.length - 1) / 30;          // segundos de queda até o impacto
export const T_FALL = W.estrondo - FALL_DUR;             // começa a cair antes, para bater exatamente no "estrondo"
export const leanAt = (_id: number, t: number) => {
  if (t < T_FALL) return TH0 + 0.012 * Math.sin(t * 2.3);                       // ainda inclinada, balançando no vento
  if (t < W.estrondo) { const k = (t - T_FALL) * 30, i = Math.floor(k); return FALL[i] + (FALL[Math.min(i + 1, FALL.length - 1)] - FALL[i]) * (k - i); }
  const s = t - W.estrondo; return TH_HIT - 0.035 * Math.exp(-s * 5) * Math.abs(Math.sin(s * 14));   // quica e assenta na casa
};
export const fallen = (t: number) => t >= W.estrondo;
export const FLICKER: [number, number][] = [];
export const flickOff = (_t: number) => false;
export const lampOn = (_id: number, _t: number) => false;
/** relâmpagos (s) */
export const BOLTS = [9.0, 35.6, 45.2, 59.6];   // sem clarão no estrondo (a queda tem que aparecer)
/** a faísca do fio solto (true = faiscando neste quadro) */
const hh = (i: number) => { const x = Math.sin(i * 127.1 + 31.7) * 43758.5453; return x - Math.floor(x); };
export const sparkAt = (t: number) => { const n = Math.floor(t * 15); return hh(n) < 0.42 || (hh(n + 77) < 0.25 && (t * 30) % 2 < 1); };
/** abertura da porta do banheiro (rad): uma fresta no "abre uma fresta"; atravessa a sala na opção A */
export const doorAt = (id: number, t: number) => (id === 12 ? 0.45 * smooth((t - W.voceAbre - 0.4) / 1.2) : id >= 13 && id !== 15 && id !== 16 && id !== 18 ? 0.42 : 0);

// ---------------- shots ----------------
export type Light = "day" | "golden" | "night";
export type Crowd = string;
export type ShotDef = { id: number; a: number; b: number; light: Light; crowd: Crowd };
const F = (t: number) => Math.round(t * FPS);
const CUT = [0, F(W.porta) - 1, F(W.celular) - 1, F(W.la) - 1, F(W.ai) - 1, F(W.casa) - 1, F(W.vidro) - 1, F(W.arvore) - 1, F(W.voce) - 1,
  F(W.mas) - 1, F(W.e1) - 1, F(W.voceAbre) - 1, F(W.a2) - 1, F(W.noChao) - 1, F(W.ai2) - 1, F(W.e2) - 1, F(W.opcaoA) - 1, F(W.opcaoB) - 1,
  F(W.comenta) - 1, F(W.se) - 1, TOTAL];
const DEF: [Light, Crowd][] = [
  ["night", "w_recap"],   // 1 a maioria escolheu B: o banheiro
  ["night", "w_latch"],   // 2 a porta tá trancada
  ["night", "w_flash"],   // 3 celular com 8 %, lanterna acesa
  ["night", "w_storm"],   // 4 lá fora, o vento uiva
  ["night", "w_fall"],    // 5 aí vem o estrondo: a árvore cai
  ["night", "w_shake"],   // 6 a casa inteira treme
  ["night", "w_debris"],  // 7 vidro quebrando, telha caindo... silêncio
  ["night", "w_wide"],    // 8 a árvore caiu em cima da sua sala
  ["night", "w_ok"],      // 9 você tá inteiro, o banheiro aguentou
  ["night", "w_drip"],    // 10 água pingando do teto
  ["night", "w_smoke"],   // 11 cheiro de queimado vindo da sala
  ["night", "w_door"],    // 12 você abre uma fresta da porta
  ["night", "w_peek"],    // 13 a sala no escuro, cheia de galhos
  ["night", "w_wire"],    // 14 o fio solto soltando faísca
  ["night", "w_call"],    // 15 o celular vibra: 6 %
  ["night", "w_neigh"],   // 16 a vizinha: tem alguém preso aqui do lado
  ["night", "w_optA"],    // 17 opção A: atravessar a sala
  ["night", "w_optB"],    // 18 opção B: ligar 193
  ["night", "w_choice"],  // 19 comenta A ou B
  ["night", "w_cta"],     // 20 inscreve / E se...
];
export const SHOTS: ShotDef[] = DEF.map(([light, crowd], i) => ({ id: i + 1, a: CUT[i], b: CUT[i + 1], light, crowd }));
export const XFADE: Record<number, number> = {};
export const FLASH_AT = -100;
const BATH = [1, 2, 3, 6, 9, 10, 11, 12, 15, 18];
export const inBath = (id: number) => BATH.includes(id);
/** quadro inicial de cada relâmpago (no banheiro sem janela não há clarão) */
export const FLASHES = BOLTS.map((t) => F(t)).filter((f) => { const s = SHOTS.find((x) => f >= x.a && f < x.b); return s && !inBath(s.id); });
export const shotAt = (f: number) => SHOTS.find((s) => f >= s.a && f < s.b) ?? SHOTS[SHOTS.length - 1];
export const layersAt = (f: number): { id: number; alpha: number }[] => [{ id: shotAt(f).id, alpha: 1 }];

/** celular "na mão" nos planos de tela (ponto ~0,42 m à frente da câmera) */
export const PH_CAM: Record<number, [V3, V3, number]> = { 3: [[800.55, 1.5, 1.0], [800.15, 1.12, 2.6], -0.01], 15: [[800.5, 1.52, 1.05], [800.1, 1.1, 2.6], 0.012], 18: [[800.45, 1.5, 1.0], [800.12, 1.12, 2.6], -0.014] };
export const PHONE_NEAR: Record<number, V3> = Object.fromEntries(Object.entries(PH_CAM).map(([k, [p, l]]) => {
  const d = l.map((v, i) => v - p[i]), n = Math.hypot(...d); return [k, p.map((v, i) => v + (0.42 * d[i]) / n) as V3];
}));

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
const ph = (id: number): Key[] => [{ f: 0, s: (f) => dolly(PH_CAM[id][0], PH_CAM[id][1], f, S0(id), 0.0022, { fov: 40, roll: PH_CAM[id][2] }) }];
const CAMS: Record<number, Key[]> = {
  // banheiro: você em pé, a lanterna acesa (mesmo enquadramento do fim do vídeo 12)
  1: [{ f: 0, s: (f) => dolly([800.0, 1.55, -1.3], [800.0, 1.2, 3.0], f, S0(1), 0.0024, { fov: 52, roll: -0.015 }) }],
  // o trinco da porta, de perto
  2: [{ f: 0, s: (f) => dolly([799.55, 1.5, 0.55], [800.0, 1.2, 3.3], f, S0(2), 0.003, { fov: 44, roll: 0.02 }) }],
  3: ph(3),
  // lá fora: o vento uiva (contra-plongée nas árvores)
  4: [{ f: 0, s: (f) => dolly([-6.5, 1.0, -4.5], [1.5, 4.6, 10], f, S0(4), 0.0026, { fov: 62, roll: 0.05 }) }],
  // a árvore cai sobre a casa (de lado, da calçada)
  5: [{ f: 0, s: (f) => dolly([-9.0, 2.2, 6.0], [3.0, 4.4, 11.5], f, S0(5), 0.0012, { fov: 62 }) }],
  // a casa inteira treme (banheiro)
  6: [{ f: 0, s: (f) => dolly([800.0, 1.6, -1.0], [800.0, 1.45, 3.0], f, S0(6), 0.002, { fov: 56 }) }],
  // vidro e telhas caindo da fachada, depois silêncio
  7: [{ f: 0, s: (f) => dolly([8.5, 1.4, 6.2], [2.6, 4.6, 12], f, S0(7), 0.002, { fov: 60, roll: -0.02 }) }],
  // a árvore caída em cima da casa (grua descendo)
  8: [{ f: 0, s: () => ({ pos: [12, 7.5, 1.5], look: [2, 4.5, 12], fov: 58 }) },
      { f: S0(8) + 2, dur: 90, s: (f) => dolly([10.5, 2.6, 2.6], [2.4, 4.8, 12], f, S0(8), 0.0015, { fov: 58 }) }],
  9: [{ f: 0, s: (f) => dolly([800.0, 1.55, -0.9], [800.0, 1.25, 3.0], f, S0(9), 0.0026, { fov: 50 }) }],
  // a goteira: de baixo, olhando a mancha no teto e as gotas
  10: [{ f: 0, s: (f) => dolly([800.9, 0.55, -0.4], [801.6, 1.7, 1.2], f, S0(10), 0.0022, { fov: 62 }) }],
  // fumaça entrando pela fresta de baixo da porta
  11: [{ f: 0, s: (f) => dolly([800.3, 0.85, 1.25], [800.0, 0.3, 3.35], f, S0(11), 0.003, { fov: 58 }) }],
  // a porta abre uma fresta
  12: [{ f: 0, s: (f) => dolly([800.95, 1.55, 0.55], [800.4, 1.1, 3.5], f, S0(12), 0.0026, { fov: 56 }) }],
  // pela fresta: a sala no escuro, cheia de galhos
  13: [{ f: 0, s: (f) => dolly([597.8, 1.55, -4.2], [600.6, 1.6, 3.4], f, S0(13), 0.002, { fov: 54 }) }],
  // o fio solto perto da janela quebrada
  14: [{ f: 0, s: (f) => dolly([601.0, 0.75, 0.9], [602.9, 0.35, 3.0], f, S0(14), 0.0026, { fov: 50, roll: 0.02 }) }],
  15: ph(15),
  // a casa da vizinha, ao lado: uma lanterna pedindo socorro na janela
  16: [{ f: 0, s: (f) => dolly([16.5, 1.5, 4.5], [10.5, 4.0, 12], f, S0(16), 0.0022, { fov: 54 }) }],
  // opção A: você atravessando a sala no escuro
  17: [{ f: 0, s: (f) => dolly([597.6, 1.5, -2.8], [599.6, 1.0, 1.4], f, S0(17), 0.002, { fov: 58 }) }],
  18: ph(18),
  // a escolha: a casa com a árvore caída
  19: [{ f: 0, s: (f) => dolly([11.5, 2.8, 2.0], [2.4, 4.8, 12], f, S0(19), 0.0014, { fov: 58 }) }],
  // CTA: afastando devagar
  20: [{ f: 0, s: (f) => ({ pos: [9.5, 2.4, 3.2], look: [2.4, 4.8, 12], fov: 56 }) }, { f: S0(20) + 2, dur: 100, s: () => ({ pos: [13, 3.6, 0.4], look: [2.4, 5.2, 12], fov: 56 }) }],
};
/** impact kicks: flip sign every frame, decay over 7 frames */
const KICKS = [W.estrondo, W.casa, W.faisca, W.vibra];
export const kickAt = (t: number) => {
  for (const k of KICKS) { const n = Math.round((t - k) * FPS); if (n >= 0 && n < 7) return (n % 2 ? -1 : 1) * (1 - n / 7); }
  return 0;
};
/** tremor de vento na câmera (planos externos com vento) */
/** tremor: vento nos planos de fora; a casa tremendo no banheiro logo depois do estrondo */
const shake = (id: number, t: number) => (id === 6 ? 1.6 * Math.exp(-(t - W.casa) * 1.2) : [4, 5, 7, 8, 16, 19, 20].includes(id) ? windAt(id, t) * 0.8 : 0);
export const camAt = (id: number, f: number): Cam => {
  const c = run(CAMS[id], f), a = kickAt(f / FPS), w = shake(id, f / FPS);
  const sx = w ? w * 0.012 * (Math.sin(f * 0.9) + 0.6 * Math.sin(f * 2.3 + 1)) : 0, sy = w ? w * 0.008 * Math.sin(f * 1.7 + 2) : 0;
  if (!a && !w) return c;
  const d: V3 = [c.look[0] - c.pos[0], c.look[1] - c.pos[1], c.look[2] - c.pos[2]];
  const L = Math.hypot(...d), h = Math.hypot(d[0], d[2]) || 1;
  const m = (3 / 640) * Math.tan((c.fov * Math.PI) / 360) * L * a * 2.5;
  return { ...c, look: [c.look[0] - (d[2] / h) * (m + sx * L), c.look[1] + 0.6 * m + sy * L, c.look[2] + (d[0] / h) * (m + sx * L)], roll: c.roll + a * 0.006 + sx * 0.4 };
};

// ---------------- lens blur per beat (cInf px at 1080; 0 = sharp) ----------------
export type Dof = { f: number; dur?: number; cInf: number; focus?: (f: number) => V3 };
const FOC: Record<number, [number, V3]> = {
  1: [10, [800, 1.1, 2.4]], 2: [8, [800.3, 1.2, 2.4]], 3: [16, PHONE_NEAR[3]], 4: [4, [1.5, 4.0, 9]], 5: [4, [3.0, 4.4, 11]], 6: [8, [800, 1.2, 2.4]],
  7: [6, [2.8, 4.5, 11.8]], 8: [4, [2.4, 4.5, 11.5]], 9: [10, [800, 1.2, 2.4]], 10: [10, [801.6, 1.6, 1.2]], 11: [12, [800.0, 0.1, 3.3]],
  12: [8, [800.5, 1.1, 3.3]], 13: [6, [600.4, 1.4, 3.0]], 14: [12, [602.8, 0.2, 2.8]], 15: [16, PHONE_NEAR[15]], 16: [4, [10.5, 4.0, 12]],
  17: [8, [599.2, 1.0, 0.5]], 18: [16, PHONE_NEAR[18]], 19: [4, [2.4, 4.6, 11.8]], 20: [4, [2.4, 4.6, 11.8]],
};
export const DOF: Dof[] = SHOTS.map((s) => ({ f: s.a, cInf: FOC[s.id][0], focus: () => FOC[s.id][1] }));
export const dofAt = (f: number) => {
  let i = 0; while (i + 1 < DOF.length && f >= DOF[i + 1].f) i++;
  const d = DOF[i], p = DOF[Math.max(0, i - 1)];
  const k = d.dur ? Math.min(1, (f - d.f) / d.dur) : 1;
  return { cInf: p.cInf + (d.cInf - p.cInf) * k, focus: d.focus };
};
export type Fg = { a: number; b: number; kit: string; pos: V3; s?: number; yaw?: number };
export const FOREGROUND: Fg[] = [];
