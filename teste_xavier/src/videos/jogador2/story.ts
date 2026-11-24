// "A torre que uma guerra salvou": our 15 s short in the flat-characters-in-a-3D-toon-world style.
// Timeline: 4 shots timed to the narration (estimates until the voice arrives; retime LINES then).
//   S1 hook, today: leaning tower, tourists posing  | "A torre mais famosa da Itália só tá de pé porque uma guerra parou a obra."
//   S2 1178: two floors, the tower sinks, masons shocked | "No segundo andar, ela começou a afundar."
//   S3 war: soldiers march past the stump, then dusk     | "A guerra parou tudo por cem anos, o barro firmou…"
//   S5 1272: the rest goes up, bent back (the curve)     | "Quando voltaram, fizeram o resto torto pro outro lado, pra disfarçar…"
//   S6 today: the finished tower stands, tourists cheer  | "…e ela não caiu."
export const FPS = 30;
// Vídeo 18 "Jogador 2 · Ep. 1": o sítio, o console, 99% e a luz cai. Narração 64,60 s.
// Tempos das palavras em projeto_videos3d/analysis/narracao/18_words.json.
export const TOTAL = 1938;
export const T0 = 0;
export const D0 = 0; // ground height (m)
export type V3 = [number, number, number];

export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const smooth = (x: number) => { const u = clamp01(x); return u * u * (3 - 2 * u); };
export const easeOut = (u: number) => 1 - (1 - clamp01(u)) ** 4;

/** tempos das palavras (s) */
export const W = {
  tres: 0.0, faltava: 2.16, e0: 6.82, caiu: 7.86, mora: 9.28, juntou: 12.96, console: 15.18, internet: 16.2, gta: 18.98, agora: 20.28, escuro: 21.48,
  so: 22.58, ai: 24.68, luzinha: 26.74, acesa: 28.34, sem: 29.54, tv: 31.46, liga: 31.84, na: 33.38, jogador: 35.38, voce: 37.68, controle: 38.56,
  os: 39.6, latiam: 40.6, param: 41.54, sofa: 43.4, alguma: 45.4, vibrar: 46.44, decide: 47.54, opcaoA: 48.94, pegar: 50.22, opcaoB: 52.56,
  sair: 53.52, gerador: 55.42, comenta: 57.28, mais: 59.0, manda: 61.6, se: 64.0,
  // nomes herdados do vídeo 16 (código antigo)
  seis: -100, liga0: -100, n193: -100, chama: -100, duas: -100, atendem: -100, fala: -100, endereco: -100, arvore: -100, fio: -100,
  vizinha: -100, outro: -100, voz: -100, nao: -100, fica: -100, equipe: -100, ligacao: -100, celular: -100, apaga: -100,
  la: -100, sirene: -100, ela: -100, chegando2: -100, e1: -100, para: -100, silencio: -100, batem: -100,
  forte: -100, e2: -100, abre: -100, filho: -100, eu: -100, entre: -100, e3: -100, fio2: -100, ainda: -100, faisca: -100,
  atravessa: -100, grita: -100,
  estrondo: -10, casa: -9, silencio0: -8, voceAbre: -100, vibra: -100, aguentou: -100,
  apaga0: -1, estalo: 999, inclinando: 999, celular2: 999, direcao: 999, pisca: 999, dobrar: 0, vento: -1,
};
export const T_OFF = -1, T_FRIDGE = 999, T_HOURS = 999, T_SINK = 999, T_WAR = 999, T_NOT = 999;

// ---------------- sets ----------------
export const SET = { street: [0, 0] as const, room: [600, 0] as const, bath: [800, 0] as const, farm: [-200, -300] as const };

// ---------------- vento, chuva e a queda da árvore ----------------
/** vento 0..1: depois da queda (vídeo 14) fica fraco, só a chuva */
export const windAt = (id: number, _t: number) => ([3, 5, 7, 10, 14, 19, 21].includes(id) ? 0.45 : 0);
/** queda da árvore: haste rígida girando na base, theta'' = (3g / 2L) sin(theta), de 0,27 rad (fim do vídeo 12) até bater na casa
 *  no "estrondo"; depois um quique pequeno e amortecido. Integração feita uma vez (60 passos por quadro). */
const TH0 = 0.27, TH_HIT = 0.62, LTREE = 10.5, G = 9.81;
const FALL: number[] = (() => { const out = [TH0]; let th = TH0, w = 0; const dt = 1 / 1800;
  for (let i = 0; th < TH_HIT && i < 1e6; i++) { w += (3 * G / (2 * LTREE)) * Math.sin(th) * dt; th += w * dt; if (i % 60 === 59) out.push(Math.min(th, TH_HIT)); }
  return out; })();
export const FALL_DUR = (FALL.length - 1) / 30;          // segundos de queda até o impacto
export const T_FALL = W.estrondo - FALL_DUR;             // começa a cair antes, para bater exatamente no "estrondo"
export const leanAt = (_id: number, _t: number) => TH_HIT;   // a árvore já está caída em cima da casa
export const fallen = (_t: number) => false;
export const FLICKER: [number, number][] = [];
export const flickOff = (_t: number) => false;
export const lampOn = (id: number, t: number) => id === 4 || ((id === 1 || id === 2) && t < W.caiu);
/** relâmpagos (s) */
export const BOLTS: number[] = [];
/** a faísca do fio solto (true = faiscando neste quadro) */
const hh = (i: number) => { const x = Math.sin(i * 127.1 + 31.7) * 43758.5453; return x - Math.floor(x); };
/** na palavra "faísca" a faísca é forçada (rajada 2 de cada 3 quadros), para a imagem bater com a narração */
const sparkBurst = (t: number) => t >= W.faisca && t < W.faisca + 0.98;
export const sparkAt = (t: number) => { if (sparkBurst(t)) return Math.floor(t * 30 + 1e-6) % 3 < 2; const n = Math.floor(t * 15); return hh(n) < 0.42 || (hh(n + 77) < 0.25 && (t * 30) % 2 < 1); };
/** a porta do banheiro fica fechada no episódio 3 (você fica lá dentro) */
export const doorAt = (_id: number, _t: number) => 0;
/** sirene: x do carro na rua (vem de longe pela esquerda e para), 0..1 de intensidade e o pulso das luzes */
export const sirenX = (t: number) => (t < W.ela ? -95 : -95 + 72 * easeOut((t - W.ela) / (W.para - W.ela)));
export const sirenK = (_t: number) => 0;
export const sirenPulse = (t: number) => 0.55 + 0.45 * Math.sign(Math.sin(t * 2 * Math.PI * 2.2));
/** escuridão (0..1) dentro do banheiro depois que o celular apaga */
/** escuridão (0..1) na sala depois que a luz cai */
export const darkAt = (id: number, t: number) => (id === 2 ? (t < W.caiu ? 0 : 0.62) : ROOM_DARK.includes(id) ? (tvOn(id, t) ? 0.5 : 0.62) : 0);
/** a TV: instalando (99 %), desligada, chiado ao ligar sozinha, e a mensagem */
export type TvState = "install" | "off" | "static" | "p2" | "glow";
export const tvState = (id: number, t: number): TvState =>
  id === 1 || (id === 2 && t < W.caiu) ? "install" : id === 11 ? (t < W.liga ? "off" : t < W.liga + 0.7 ? "static" : "glow") : id === 12 ? (t < W.jogador - 0.15 ? "glow" : "p2") : TV_P2.includes(id) ? "p2" : "off";
export const tvOn = (id: number, t: number) => tvState(id, t) !== "off";
/** a luzinha do console (acesa mesmo sem energia) */
export const ledOn = (id: number, _t: number) => id !== 4;
/** a almofada do sofá vibrando (deslocamento em m) */
export const vibAt = (id: number, t: number) => (t < W.alguma - 0.2 || id < 15 ? 0 : 0.012 * Math.sign(Math.sin(t * 2 * Math.PI * 23)) * (0.6 + 0.4 * Math.abs(Math.sin(t * 9))));
/** os cachorros latem até o "param" */
export const barkAt = (t: number) => t < W.param - 0.05 && (Math.floor(t * 4.2) % 3 !== 2);
/** batidas na porta da frente */
export const KNOCKS: number[] = [];

// ---------------- shots ----------------
export type Light = "day" | "golden" | "night";
export type Crowd = string;
export type ShotDef = { id: number; a: number; b: number; light: Light; crowd: Crowd };
const F = (t: number) => Math.round(t * FPS);
const CUT = [0, ...[W.e0, W.mora, W.juntou, W.internet, W.agora, W.so, W.ai, W.luzinha, W.sem, W.tv, W.na, W.voce, W.os, W.sofa, W.alguma,
  W.decide, W.opcaoA, W.opcaoB, W.comenta, W.manda].map((t) => F(t) - 1), TOTAL];
const DEF: [Light, Crowd][] = [
  ["night", "j_tv99"],     // 1 três e doze: falta 1 % pro jogo instalar
  ["night", "j_cut"],      // 2 e a luz do sítio caiu
  ["night", "j_farm"],     // 3 você mora no sítio do seu avô
  ["golden", "j_buy"],     // 4 juntou dinheiro o ano inteiro pro console (lembrança, de dia)
  ["golden", "j_ant"],     // 5 a internet de rádio levou dois dias
  ["night", "j_dark"],     // 6 e agora, escuro
  ["night", "j_corn"],     // 7 só o vento no milharal
  ["night", "j_face"],     // 8 aí você percebe uma coisa
  ["night", "j_led"],      // 9 a luzinha do console continua acesa
  ["night", "j_noen"],     // 10 sem energia nenhuma
  ["night", "j_tvon"],     // 11 a TV liga sozinha
  ["night", "j_p2"],       // 12 na tela: jogador dois conectado
  ["night", "j_pad"],      // 13 você só tem um controle
  ["night", "j_dogs"],     // 14 os cachorros param ao mesmo tempo
  ["night", "j_side"],     // 15 e no sofá, do seu lado
  ["night", "j_vib"],      // 16 alguma coisa começa a vibrar
  ["night", "j_decide"],   // 17 você decide
  ["night", "j_optA"],     // 18 opção A: pegar o que vibra
  ["night", "j_optB"],     // 19 opção B: o gerador no galpão
  ["night", "j_choice"],   // 20 comenta A ou B
  ["night", "j_cta"],      // 21 manda / E se...
];
const ROOM_DARK = [6, 8, 9, 11, 12, 13, 15, 16, 17, 18, 20];
const TV_P2 = [13, 15, 16, 17, 18, 20];
export const SHOTS: ShotDef[] = DEF.map(([light, crowd], i) => ({ id: i + 1, a: CUT[i], b: CUT[i + 1], light, crowd }));
export const XFADE: Record<number, number> = {};
export const FLASH_AT = -100;
const BATH: number[] = [];
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
  // a TV: barra de instalação travada em 99 %
  1: [{ f: 0, s: (f) => dolly([600.3, 1.12, 1.75], [600.0, 1.02, -0.62], f, S0(1), 0.0026, { fov: 44 }) }],
  // a sala: você no sofá, a TV e o abajur acesos; no "caiu" tudo apaga
  2: [{ f: 0, s: (f) => dolly([596.4, 1.75, -2.4], [600.0, 0.9, 2.4], f, S0(2), 0.0018, { fov: 56 }) }],
  // o sítio de noite
  3: [{ f: 0, s: (f) => dolly([-206.5, 2.0, -279.5], [-198.5, 2.6, -298], f, S0(3), 0.0018, { fov: 52 }) }],
  // lembrança: você com a caixa do console, de dia
  4: [{ f: 0, s: (f) => dolly([597.9, 1.35, -0.6], [599.6, 1.15, 1.7], f, S0(4), 0.0024, { fov: 48 }) }],
  // a antena da internet de rádio no telhado
  5: [{ f: 0, s: (f) => dolly([-204.6, 3.2, -287.5], [-202.2, 7.6, -298.0], f, S0(5), 0.0022, { fov: 46 }) }],
  // escuro: você no sofá
  6: [{ f: 0, s: (f) => dolly([599.6, 1.3, 0.0], [599.4, 0.92, 2.44], f, S0(6), 0.0024, { fov: 50 }) }],
  // o milharal balançando
  7: [{ f: 0, s: (f) => dolly([-224.0, 1.25, -281.0], [-211.0, 1.5, -300.0], f, S0(7), 0.002, { fov: 56 }) }],
  // seu rosto
  8: [{ f: 0, s: (f) => dolly([599.42, 1.2, 1.3], [599.4, 1.12, 2.44], f, S0(8), 0.003, { fov: 42 }) }],
  // a luzinha do console
  9: [{ f: 0, s: (f) => dolly([601.25, 0.72, 0.35], [601.0, 0.56, -0.55], f, S0(9), 0.003, { fov: 36 }) }],
  // a casa inteira apagada
  10: [{ f: 0, s: (f) => dolly([-204.0, 1.7, -284.0], [-199.5, 2.3, -298.0], f, S0(10), 0.0024, { fov: 48 }) }],
  // a TV liga sozinha
  11: [{ f: 0, s: (f) => dolly([602.9, 1.35, 2.1], [600.0, 1.0, -0.6], f, S0(11), 0.0024, { fov: 52 }) }],
  // a mensagem na tela
  12: [{ f: 0, s: (f) => dolly([600.0, 1.12, 1.15], [600.0, 1.1, -0.62], f, S0(12), 0.0026, { fov: 42 }) }],
  // você e o único controle
  13: [{ f: 0, s: (f) => dolly([599.45, 1.08, 1.1], [599.4, 0.95, 2.44], f, S0(13), 0.0026, { fov: 46 }) }],
  // os cachorros na varanda
  14: [{ f: 0, s: (f) => dolly([-194.6, 0.85, -291.2], [-198.2, 0.75, -295.6], f, S0(14), 0.0024, { fov: 50 }) }],
  // o sofá do seu lado
  15: [{ f: 0, s: (f) => dolly([600.3, 1.25, 1.2], [600.2, 0.62, 2.9], f, S0(15), 0.0024, { fov: 50 }) }],
  // a almofada vibrando
  16: [{ f: 0, s: (f) => dolly([600.85, 0.92, 1.85], [600.75, 0.52, 2.9], f, S0(16), 0.003, { fov: 40 }) }],
  // você decide
  17: [{ f: 0, s: (f) => dolly([599.42, 1.2, 1.25], [599.4, 1.12, 2.44], f, S0(17), 0.003, { fov: 44 }) }],
  // opção A: a almofada
  18: [{ f: 0, s: (f) => dolly([601.7, 1.0, 1.95], [600.7, 0.55, 2.9], f, S0(18), 0.0024, { fov: 44 }) }],
  // opção B: o caminho escuro até o galpão
  19: [{ f: 0, s: (f) => dolly([-191.5, 1.55, -292.0], [-186.0, 1.4, -304.5], f, S0(19), 0.0022, { fov: 52 }) }],
  // comenta: a sala com a TV acesa
  20: [{ f: 0, s: (f) => dolly([596.4, 1.75, -2.4], [600.0, 0.9, 2.4], f, S0(20), 0.0016, { fov: 56 }) }],
  // a casa no escuro com a janela azul da TV
  21: [{ f: 0, s: () => ({ pos: [-202.5, 1.9, -284.0], look: [-199.5, 2.4, -298.0], fov: 50 }) }, { f: S0(21) + 2, dur: 110, s: () => ({ pos: [-207.0, 3.4, -277.0], look: [-199.5, 2.6, -298.0], fov: 52 }) }],
};
/** impact kicks: flip sign every frame, decay over 7 frames */
const KICKS = [W.caiu, W.liga, W.param, W.alguma + 0.1];
export const kickAt = (t: number) => {
  for (const k of KICKS) { const n = Math.round((t - k) * FPS); if (n >= 0 && n < 7) return (n % 2 ? -1 : 1) * (1 - n / 7); }
  return 0;
};
/** tremor de vento na câmera (planos externos com vento) */
/** tremor: vento nos planos de fora; a casa tremendo no banheiro logo depois do estrondo */
const shake = (id: number, t: number) => ([3, 5, 7, 10, 14, 19, 21].includes(id) ? windAt(id, t) * 0.5 : 0);
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
  1: [10, [600, 1.1, -0.62]], 2: [6, [599.4, 1.0, 2.44]], 3: [3, [-199, 2.5, -297]], 4: [8, [599.6, 1.15, 1.7]], 5: [4, [-202.2, 6.0, -299]],
  6: [10, [599.4, 1.0, 2.44]], 7: [5, [-213, 1.4, -297]], 8: [14, [599.4, 1.12, 2.44]], 9: [16, [601.0, 0.56, -0.55]], 10: [3, [-199.5, 2.3, -298]],
  11: [6, [600, 1.1, -0.62]], 12: [10, [600, 1.1, -0.62]], 13: [12, [599.4, 0.9, 2.3]], 14: [8, [-198.2, 0.6, -295.6]], 15: [10, [600.6, 0.55, 2.9]],
  16: [16, [600.75, 0.52, 2.9]], 17: [14, [599.4, 1.12, 2.44]], 18: [12, [600.7, 0.55, 2.9]], 19: [5, [-186, 1.4, -304]], 20: [6, [599.4, 1.0, 2.44]], 21: [3, [-199.5, 2.3, -298]],
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
