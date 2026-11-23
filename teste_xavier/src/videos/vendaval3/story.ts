// "A torre que uma guerra salvou": our 15 s short in the flat-characters-in-a-3D-toon-world style.
// Timeline: 4 shots timed to the narration (estimates until the voice arrives; retime LINES then).
//   S1 hook, today: leaning tower, tourists posing  | "A torre mais famosa da Itália só tá de pé porque uma guerra parou a obra."
//   S2 1178: two floors, the tower sinks, masons shocked | "No segundo andar, ela começou a afundar."
//   S3 war: soldiers march past the stump, then dusk     | "A guerra parou tudo por cem anos, o barro firmou…"
//   S5 1272: the rest goes up, bent back (the curve)     | "Quando voltaram, fizeram o resto torto pro outro lado, pra disfarçar…"
//   S6 today: the finished tower stands, tourists cheer  | "…e ela não caiu."
export const FPS = 30;
// Vídeo 16 "Vendaval · Ep. 3": continuação do vídeo 14 (a maioria escolheu B: ficar e ligar 193). Narração 76,93 s.
// Tempos das palavras em projeto_videos3d/analysis/narracao/16_words.json.
export const TOTAL = 2308;
export const T0 = 0;
export const D0 = 0; // ground height (m)
export type V3 = [number, number, number];

export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const smooth = (x: number) => { const u = clamp01(x); return u * u * (3 - 2 * u); };
export const easeOut = (u: number) => 1 - (1 - clamp01(u)) ** 4;

/** tempos das palavras (s) */
export const W = {
  seis: 0.0, liga: 1.72, n193: 4.36, chama: 5.0, duas: 6.86, atendem: 7.38, fala: 8.76, endereco: 10.06, arvore: 11.2, fio: 12.1,
  vizinha: 13.76, outro: 15.68, voz: 16.78, nao: 18.14, fica: 19.86, equipe: 21.14, tres: 22.76, ligacao: 24.08, celular: 25.02, apaga: 26.0,
  agora: 27.2, la: 30.42, sirene: 31.48, ela: 32.42, chegando2: 34.08, e1: 34.88, para: 35.74, silencio: 37.0, ai: 38.02, batem: 38.94,
  forte: 40.66, e2: 41.4, abre: 43.52, filho: 44.34, eu: 45.38, entre: 47.88, e3: 51.32, fio2: 52.9, ainda: 53.82, faisca: 54.82,
  opcaoA: 56.38, atravessa: 57.68, opcaoB: 60.92, grita: 63.76, comenta: 66.58, mais: 68.44, manda: 71.58, se: 76.04,
  // nomes do vídeo 14 ainda usados pelo código herdado
  estrondo: -10, casa: -9, silencio0: -8, voceAbre: -100, vibra: -100, aguentou: -100,
  apaga0: -1, estalo: 999, inclinando: 999, celular2: 999, direcao: 999, pisca: 999, dobrar: 0, vento: -1,
};
export const T_OFF = -1, T_FRIDGE = 999, T_HOURS = 999, T_SINK = 999, T_WAR = 999, T_NOT = 999;

// ---------------- sets ----------------
export const SET = { street: [0, 0] as const, room: [600, 0] as const, bath: [800, 0] as const };

// ---------------- vento, chuva e a queda da árvore ----------------
/** vento 0..1: depois da queda (vídeo 14) fica fraco, só a chuva */
export const windAt = (_id: number, _t: number) => 0.32;
/** queda da árvore: haste rígida girando na base, theta'' = (3g / 2L) sin(theta), de 0,27 rad (fim do vídeo 12) até bater na casa
 *  no "estrondo"; depois um quique pequeno e amortecido. Integração feita uma vez (60 passos por quadro). */
const TH0 = 0.27, TH_HIT = 0.62, LTREE = 10.5, G = 9.81;
const FALL: number[] = (() => { const out = [TH0]; let th = TH0, w = 0; const dt = 1 / 1800;
  for (let i = 0; th < TH_HIT && i < 1e6; i++) { w += (3 * G / (2 * LTREE)) * Math.sin(th) * dt; th += w * dt; if (i % 60 === 59) out.push(Math.min(th, TH_HIT)); }
  return out; })();
export const FALL_DUR = (FALL.length - 1) / 30;          // segundos de queda até o impacto
export const T_FALL = W.estrondo - FALL_DUR;             // começa a cair antes, para bater exatamente no "estrondo"
export const leanAt = (_id: number, _t: number) => TH_HIT;   // a árvore já está caída em cima da casa
export const fallen = (_t: number) => true;
export const FLICKER: [number, number][] = [];
export const flickOff = (_t: number) => false;
export const lampOn = (_id: number, _t: number) => false;
/** relâmpagos (s) */
export const BOLTS = [11.0, 44.6, 68.2];
/** a faísca do fio solto (true = faiscando neste quadro) */
const hh = (i: number) => { const x = Math.sin(i * 127.1 + 31.7) * 43758.5453; return x - Math.floor(x); };
export const sparkAt = (t: number) => { const n = Math.floor(t * 15); return hh(n) < 0.42 || (hh(n + 77) < 0.25 && (t * 30) % 2 < 1); };
/** a porta do banheiro fica fechada no episódio 3 (você fica lá dentro) */
export const doorAt = (_id: number, _t: number) => 0;
/** sirene: x do carro na rua (vem de longe pela esquerda e para), 0..1 de intensidade e o pulso das luzes */
export const sirenX = (t: number) => (t < W.ela ? -95 : -95 + 72 * easeOut((t - W.ela) / (W.para - W.ela)));
export const sirenK = (t: number) => (t < W.sirene - 0.6 ? 0 : t < W.silencio ? clamp01((t - W.sirene + 0.6) / 0.8) : Math.max(0, 1 - (t - W.silencio) / 1.0));
export const sirenPulse = (t: number) => 0.55 + 0.45 * Math.sign(Math.sin(t * 2 * Math.PI * 2.2));
/** escuridão (0..1) dentro do banheiro depois que o celular apaga */
export const darkAt = (id: number, t: number) => (id === 10 ? smooth((t - W.apaga) / 0.25) : [11, 14, 21].includes(id) ? 1 : [18, 19, 20].includes(id) ? 0.55 : 0);
/** batidas na porta da frente */
export const KNOCKS = [W.batem, W.batem + 0.3, W.batem + 0.6, W.forte, W.forte + 0.28, W.forte + 0.56, W.abre - 0.2];

// ---------------- shots ----------------
export type Light = "day" | "golden" | "night";
export type Crowd = string;
export type ShotDef = { id: number; a: number; b: number; light: Light; crowd: Crowd };
const F = (t: number) => Math.round(t * FPS);
const CUT = [0, ...[W.n193, W.atendem, W.endereco, W.fio, W.vizinha, W.outro, W.nao, W.tres, W.ligacao, W.agora, W.la, W.ela, W.e1, W.ai, W.e2,
  W.abre, W.entre, W.e3, W.opcaoA, W.opcaoB, W.comenta, W.manda].map((t) => F(t) - 1), TOTAL];
const DEF: [Light, Crowd][] = [
  ["night", "v_dial"],    // 1 seis por cento: você liga pro 193
  ["night", "v_ear"],     // 2 chama uma vez, duas
  ["night", "v_call"],    // 3 atendem: em chamada
  ["night", "v_house"],   // 4 o endereço, a árvore
  ["night", "v_wire"],    // 5 o fio soltando faísca
  ["night", "v_neighW"],  // 6 a vizinha pedindo socorro (lanterna na janela)
  ["night", "v_call2"],   // 7 do outro lado, uma voz calma
  ["night", "v_listen"],  // 8 não chega perto do fio, fica onde você está
  ["night", "v_low3"],    // 9 três por cento
  ["night", "v_end"],     // 10 a ligação cai, o celular apaga
  ["night", "v_dark"],    // 11 escuridão e chuva
  ["night", "v_far"],     // 12 lá longe, uma sirene
  ["night", "v_near"],    // 13 ela vai chegando, chegando
  ["night", "v_gap"],     // 14 e para. silêncio.
  ["night", "v_knock"],   // 15 batem na porta da frente, forte
  ["night", "v_door"],    // 16 é a vizinha, gritando
  ["night", "v_shout"],   // 17 abre! o meu filho tá preso
  ["night", "v_room"],    // 18 entre você e a porta, a sala inteira no escuro
  ["night", "v_wire2"],   // 19 e no meio dela, o fio, ainda soltando faísca
  ["night", "v_optA"],    // 20 opção A: atravessa a sala
  ["night", "v_optB"],    // 21 opção B: fica e grita
  ["night", "v_choice"],  // 22 comenta A ou B
  ["night", "v_cta"],     // 23 manda / E se...
];
export const SHOTS: ShotDef[] = DEF.map(([light, crowd], i) => ({ id: i + 1, a: CUT[i], b: CUT[i + 1], light, crowd }));
export const XFADE: Record<number, number> = {};
export const FLASH_AT = -100;
const BATH = [1, 2, 3, 7, 8, 9, 10, 11, 14, 21];
export const inBath = (id: number) => BATH.includes(id);
/** quadro inicial de cada relâmpago (no banheiro sem janela não há clarão) */
export const FLASHES = BOLTS.map((t) => F(t)).filter((f) => { const s = SHOTS.find((x) => f >= x.a && f < x.b); return s && !inBath(s.id); });
export const shotAt = (f: number) => SHOTS.find((s) => f >= s.a && f < s.b) ?? SHOTS[SHOTS.length - 1];
export const layersAt = (f: number): { id: number; alpha: number }[] => [{ id: shotAt(f).id, alpha: 1 }];

/** celular "na mão" nos planos de tela (ponto ~0,42 m à frente da câmera) */
export const PH_CAM: Record<number, [V3, V3, number]> = { 1: [[800.55, 1.5, 1.0], [800.15, 1.12, 2.6], -0.01], 3: [[800.5, 1.52, 1.05], [800.1, 1.1, 2.6], 0.012], 7: [[800.48, 1.5, 1.08], [800.12, 1.12, 2.6], -0.008], 9: [[800.45, 1.5, 1.0], [800.12, 1.12, 2.6], -0.014], 10: [[800.52, 1.51, 1.02], [800.14, 1.11, 2.6], 0.01] };
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
  1: ph(1),
  // você com o celular no ouvido, no banheiro
  2: [{ f: 0, s: (f) => dolly([800.55, 1.5, 0.45], [800.0, 1.42, 2.4], f, S0(2), 0.0026, { fov: 48, roll: 0.012 }) }],
  3: ph(3),
  // a casa com a árvore caída (o endereço, a árvore)
  4: [{ f: 0, s: (f) => dolly([10.5, 2.6, 2.6], [2.4, 4.8, 12], f, S0(4), 0.002, { fov: 58 }) }],
  // o fio soltando faísca
  5: [{ f: 0, s: (f) => dolly([601.0, 0.75, 0.9], [602.9, 0.35, 3.0], f, S0(5), 0.003, { fov: 50, roll: 0.02 }) }],
  // a lanterna da vizinha na janela da casa ao lado
  6: [{ f: 0, s: (f) => dolly([16.5, 1.5, 4.5], [10.5, 4.0, 12], f, S0(6), 0.0024, { fov: 54 }) }],
  7: ph(7),
  // ouvindo a voz calma, de perto
  8: [{ f: 0, s: (f) => dolly([799.72, 1.52, 1.25], [800.0, 1.45, 2.4], f, S0(8), 0.0022, { fov: 46, roll: -0.01 }) }],
  9: ph(9),
  10: ph(10),
  // escuridão: o banheiro quase sem luz
  11: [{ f: 0, s: (f) => dolly([800.0, 1.55, -1.3], [800.0, 1.2, 3.0], f, S0(11), 0.0026, { fov: 52, roll: -0.015 }) }],
  // a rua: lá longe, uma sirene
  12: [{ f: 0, s: (f) => dolly([9.0, 1.5, 6.8], [-40, 2.2, 7.0], f, S0(12), 0.0022, { fov: 48 }) }],
  // ela vai chegando
  13: [{ f: 0, s: (f) => dolly([2.0, 1.3, 7.2], [-30, 1.8, 6.0], f, S0(13), 0.003, { fov: 54, roll: 0.02 }) }],
  // a fresta de baixo da porta do banheiro: a luz vermelha pisca e para
  14: [{ f: 0, s: (f) => dolly([800.3, 0.85, 1.25], [800.0, 0.3, 3.35], f, S0(14), 0.0025, { fov: 58 }) }],
  // batem na porta da frente (de dentro da sala)
  15: [{ f: 0, s: (f) => dolly([597.6, 1.35, -1.2], [594.1, 1.15, 3.9], f, S0(15), 0.003, { fov: 50 }) }],
  // é a vizinha, na sua porta, na chuva
  16: [{ f: 0, s: (f) => dolly([3.4, 1.6, 6.8], [-1.2, 1.4, 11.6], f, S0(16), 0.0024, { fov: 52 }) }],
  17: [{ f: 0, s: (f) => dolly([0.5, 1.5, 9.3], [-1.2, 1.35, 11.5], f, S0(17), 0.003, { fov: 44, roll: 0.02 }) }],
  // do lado do banheiro: a sala inteira no escuro até a porta
  18: [{ f: 0, s: (f) => dolly([606.5, 1.6, -4.5], [594.1, 1.1, 3.9], f, S0(18), 0.0022, { fov: 58 }) }],
  // e no meio dela, o fio
  19: [{ f: 0, s: () => ({ pos: [606.5, 1.6, -4.5], look: [594.1, 1.1, 3.9], fov: 58 }) },
       { f: S0(19) + 2, dur: 100, s: (f) => dolly([604.4, 0.75, 1.55], [602.3, 0.15, 2.26], f, S0(19), 0.002, { fov: 50 }) }],
  // opção A: você atravessando a sala
  20: [{ f: 0, s: (f) => dolly([607.4, 1.7, -3.4], [601.8, 0.9, 1.8], f, S0(20), 0.002, { fov: 60 }) }],
  // opção B: você fica no banheiro e grita
  21: [{ f: 0, s: (f) => dolly([800.4, 1.5, 0.6], [800.0, 1.4, 2.4], f, S0(21), 0.0026, { fov: 50 }) }],
  22: [{ f: 0, s: (f) => dolly([11.5, 2.8, 2.0], [2.4, 4.8, 12], f, S0(22), 0.0014, { fov: 58 }) }],
  23: [{ f: 0, s: () => ({ pos: [9.5, 2.4, 3.2], look: [2.4, 4.8, 12], fov: 56 }) }, { f: S0(23) + 2, dur: 100, s: () => ({ pos: [13, 3.6, 0.4], look: [2.4, 5.2, 12], fov: 56 }) }],
};
/** impact kicks: flip sign every frame, decay over 7 frames */
const KICKS = [W.n193 + 0.6, W.atendem, W.apaga, W.para, ...KNOCKS, W.e3 + 1.6];
export const kickAt = (t: number) => {
  for (const k of KICKS) { const n = Math.round((t - k) * FPS); if (n >= 0 && n < 7) return (n % 2 ? -1 : 1) * (1 - n / 7); }
  return 0;
};
/** tremor de vento na câmera (planos externos com vento) */
/** tremor: vento nos planos de fora; a casa tremendo no banheiro logo depois do estrondo */
const shake = (id: number, t: number) => ([4, 6, 12, 13, 16, 17, 22, 23].includes(id) ? windAt(id, t) * 0.8 : 0);
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
  1: [16, PHONE_NEAR[1]], 2: [10, [800, 1.4, 2.4]], 3: [16, PHONE_NEAR[3]], 4: [4, [2.4, 4.5, 11.5]], 5: [12, [602.8, 0.2, 2.8]], 6: [4, [10.5, 4.0, 12]],
  7: [16, PHONE_NEAR[7]], 8: [12, [800, 1.45, 2.4]], 9: [16, PHONE_NEAR[9]], 10: [16, PHONE_NEAR[10]], 11: [10, [800, 1.1, 2.4]], 12: [3, [-30, 2.0, 7]],
  13: [4, [-20, 1.8, 6.5]], 14: [12, [800.0, 0.1, 3.3]], 15: [8, [594.1, 1.1, 3.9]], 16: [6, [-1.2, 1.3, 11.5]], 17: [10, [-1.2, 1.35, 11.5]],
  18: [6, [600.5, 0.8, 2.4]], 19: [12, [602.3, 0.15, 2.26]], 20: [8, [603, 1.0, 1.6]], 21: [10, [800, 1.4, 2.4]], 22: [4, [2.4, 4.6, 11.8]], 23: [4, [2.4, 4.6, 11.8]],
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
