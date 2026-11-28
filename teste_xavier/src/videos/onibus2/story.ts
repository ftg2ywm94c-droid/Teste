// Vídeo 15 "Você decide · O último ônibus · Parte 2" (a maioria escolheu B: ficar no ônibus). Continuação do vídeo 13.
// Narração 75,96 s (projeto_videos3d/analysis/narracao/15_words.json). Mesmo ônibus, mesma rua (eixo +x, porta do lado +z);
// depois da rua escura ele entra numa garagem enorme em x ~ GX. Câmeras de dentro no referencial do ônibus (u, y, v).
export const FPS = 30;
export const TOTAL = 2279;
export const T0 = 0;
export const D0 = 0; // ground height (m)
export type V3 = [number, number, number];

export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const smooth = (x: number) => { const u = clamp01(x); return u * u * (3 - 2 * u); };
export const easeOut = (u: number) => 1 - (1 - clamp01(u)) ** 4;

/** tempos das palavras (s), de 15_words.json */
export const W = {
  porta: 0.32, fecha: 0.72, dentro: 2.26, e1: 3.08, passa: 3.6, ponto: 5.18, no: 5.96, letreiro: 6.1, noturno: 7.06, vira: 7.98, fora: 8.54,
  ele1: 10.02, rota: 10.78, rua: 11.94, poste: 13.04, as: 14.52, luzes: 14.74, apagar: 16.34, uma1: 17.14, uma2: 17.72, frente: 18.58, fundo: 19.5,
  o1: 20.26, vibra: 20.78, boa: 23.02, agora: 24.34, retrovisor: 25.5, voce1: 26.82, olha: 27.2, encarando: 29.6, ele2: 30.58, fundo2: 32.14,
  pro: 32.82, tava: 33.96, pouco: 35.22, e2: 36.06, alguem: 36.46, la: 37.36, o2: 38.08, garagem: 39.12, enorme: 39.78, dezenas: 40.72,
  parados: 41.96, todos: 42.96, aceso: 44.12, e3: 45.04, nenhum: 45.24, motorista: 45.64, a1: 46.96, abre: 47.5, pela: 48.38, fala: 50.3,
  ultima: 51.08, parada: 51.46, e4: 52.44, tocar: 54.08, numero: 54.6, voceTem: 56.72, cinco: 57.12, segundos: 57.6, opcaoA: 58.96,
  atende: 60.06, opcaoB: 61.52, corre: 63.9, garagem2: 64.56, comenta: 65.8, mais: 67.8, tres: 69.28, manda: 70.18, e5: 72.82, se: 72.94,
  decide: 75.3,
};
// nomes antigos ainda importados pelo cast.ts / world.ts (não usados aqui)
export const T_OFF = 999, T_FRIDGE = 999, T_HOURS = 999, T_SINK = 999, T_WAR = 999, T_NOT = 999;
export const BOLTS: number[] = [];
export const windAt = (_id: number, _t: number) => 0;
export const leanAt = (_id: number, _t: number) => 0;
export const lampOn = (_id: number, _t: number) => false;
export const FLOOR_H = [11, 6.8, 6.8, 6.8, 6.8, 6.8, 6.8, 6.5];

// ---------------- o ônibus ----------------
export const BZ = 2.0;          // eixo do ônibus (z do mundo); porta do lado +z (calçada em z > 4)
export const STOP_X = 8.2;      // onde ele parou no fim do Ep. 1 (o seu ponto)
export const POLE_X = 12.1;     // o poste do seu ponto
export const POLE_Z = 5.0;
export const DOOR_U: [number, number] = [3.25, 4.55];
export const FRONT_SEAT: V3 = [3.55, 0, -0.8];   // o banco da frente (atrás do motorista), onde você ficou com o celular
export const BACK_SEAT: V3 = [-5.5, 0, 0.85];    // o banco do fundo, onde você estava no Ep. 1
export const FLOOR_Y = 0.4, CUSHION_Y = 0.88;
export const GX = 1200;         // a garagem: piso x em [GX-20, GX+40], z em [-30, 14]; entrada na parede x = GX-20, z em [-3, 7]
export const GARAGE_STOP = GX + 6;
/** filas de ônibus parados na garagem: [x do centro, z] (todos de frente para +x) */
export const PARKED: [number, number][] = [];
for (const z of [-6, -10.5, -15, -19.5, -24, 9]) for (const x of [GX - 6, GX + 8, GX + 22]) PARKED.push([x, z]);
export const PHONE_LOOK: V3 = [3.57, 0.99, -0.8];
export const SCREEN_CAM: Record<number, [V3, number]> = { 7: [[3.9, 1.45, -0.35], -0.012], 16: [[3.92, 1.43, -0.38], 0.01], 18: [[3.88, 1.46, -0.33], -0.016] };
export const PHONE_NEAR: Record<number, V3> = Object.fromEntries(Object.entries(SCREEN_CAM).map(([k, [p]]) => {
  const d = PHONE_LOOK.map((v, i) => v - p[i]), n = Math.hypot(...d); return [k, p.map((v, i) => v + (0.42 * d[i]) / n) as V3];
}));

// ---------------- shots ----------------
export type Light = "day" | "golden" | "night";
export type Crowd = string;
export type ShotDef = { id: number; a: number; b: number; light: Light; crowd: Crowd; inside: boolean };
const F = (t: number) => Math.round(t * FPS);
const CUT = [0, ...["e1", "no", "ele1", "as", "o1", "boa", "voce1", "ele2", "e2", "o2", "dezenas", "e3", "a1", "pela", "e4", "voceTem", "opcaoA",
  "opcaoB", "comenta", "e5"].map((k) => F(W[k as keyof typeof W]) - 1), TOTAL];
const DEF: [Crowd, boolean][] = [
  ["c_doorShut", true],  // 1 a porta fecha com você lá dentro
  ["c_leave", false],    // 2 o ônibus vai embora do seu ponto (o poste piscando fica para trás)
  ["c_sign", false],     // 3 o letreiro: NOTURNO vira FORA DE SERVIÇO
  ["c_dark", false],     // 4 sai da rota: rua sem nenhum poste aceso
  ["c_lights", true],    // 5 as luzes do teto apagam, da frente pro fundo
  ["c_vibra", true],     // 6 o celular vibra no banco da frente
  ["c_screen", true],    // 7 BOA ESCOLHA. AGORA NÃO OLHA PRO RETROVISOR.
  ["c_mirror", true],    // 8 você olha: ele não te encara, olha pro fundo
  ["c_back", true],      // 9 o banco do fundo, onde você estava
  ["c_someone", true],   // 10 tem alguém sentado lá
  ["c_enter", false],    // 11 a garagem enorme
  ["c_rows", false],     // 12 dezenas de ônibus parados, letreiros acesos
  ["c_empty", false],    // 13 nenhum motorista
  ["c_doorOpen", true],  // 14 a porta abre
  ["c_speak", true],     // 15 o motorista fala: última parada
  ["c_screen", true],    // 16 o celular toca: número desconhecido
  ["c_you5", true],      // 17 você tem cinco segundos
  ["c_screen", true],    // 18 opção A: atender
  ["c_optB", false],     // 19 opção B: descer e correr pela garagem
  ["c_choice", false],   // 20 comenta A ou B
  ["c_cta", false],      // 21 manda pra quem... você decide
];
export const SHOTS: ShotDef[] = DEF.map(([crowd, inside], i) => ({ id: i + 1, a: CUT[i], b: CUT[i + 1], light: "night", crowd, inside }));
export const XFADE: Record<number, number> = {};
export const FLASH_AT = -100;
export const FLASHES: number[] = [];
export const shotAt = (f: number) => SHOTS.find((s) => f >= s.a && f < s.b) ?? SHOTS[SHOTS.length - 1];
export const layersAt = (f: number): { id: number; alpha: number }[] => [{ id: shotAt(f).id, alpha: 1 }];
const tA = (id: number) => SHOTS[id - 1].a / FPS;
export const inGarage = (id: number) => id >= 11;

/** posição do ônibus (x do mundo) no plano id, no tempo t */
const SPEED = 8, T_GO = 2.2, ACC = 1.8, T_G = W.o2, T_STOP = 7.5;
export const busX = (id: number, t: number) => {
  if (id <= 2) return t < T_GO ? STOP_X : STOP_X + 0.5 * ACC * (t - T_GO) ** 2;
  if (id === 4) return -6 + SPEED * (t - tA(4));
  if (id >= 11) { const s = (t - T_G) / T_STOP; return s >= 1 ? GARAGE_STOP : GARAGE_STOP - 48 * (1 - s) ** 2; }
  return -26 + SPEED * (t - tA(id));
};
export const busMoving = (id: number, t: number) => busX(id, t + 0.05) - busX(id, t) > 0.004;
/** referencial do ônibus -> mundo */
export const L = (id: number, t: number, u: number, y: number, v: number): V3 => [busX(id, t) + u, y, BZ + v];

const hh = (i: number) => { const x = Math.sin(i * 127.1 + 31.7) * 43758.5453; return x - Math.floor(x); };
/** o poste do seu ponto continua piscando (como no fim do Ep. 1) */
export const poleOff = (t: number) => { const n = Math.floor(t * 7.5); return hh(n) < 0.32 || (hh(n + 500) < 0.2 && (t * 30) % 3 < 1); };
/** rua escura: nenhum poste nem janela acesa */
export const darkStreet = (id: number) => id === 4;
/** letreiro da frente: "N" NOTURNO, "F" FORA DE SERVIÇO, "x" apagado (pisca na troca) */
export const signAt = (id: number, t: number): "N" | "F" | "x" => {
  if (id < 3) return "N";
  if (id > 3) return "F";
  const d = t - W.vira;
  if (d < -0.12) return "N";
  if (d < 0.0) return "x";
  if (d < 0.08) return "F";
  if (d < 0.2) return "x";
  if (d < 0.3) return "F";
  if (d < 0.38) return "x";
  return "F";
};
/** lâmpadas do teto: 7 pares em u = -4.7 + 1.6 k (k = 0 é o fundo). Apagam da frente (k = 6) pro fundo a partir do "apagar";
 *  a do fundo (k = 0) fica fraca e piscando: é a única luz em cima do banco do fundo. */
const LAMP_OFF = (k: number) => W.apagar - 0.05 + (6 - k) * 0.52;
export const lampK = (u: number) => Math.round((u + 4.7) / 1.6);
export const backFlick = (t: number) => { const n = Math.floor(t * 9); return hh(n + 77) < 0.18 || (t > W.e2 + 0.24 && t < W.alguem + 0.02); };
export const lampOnAt = (id: number, t: number, k: number) => {
  if (id < 5) return true;
  if (id === 5 && t < LAMP_OFF(k)) return true;
  return k === 0 && !backFlick(t);
};
/** quanto a cabine está iluminada (1 = todas as lâmpadas acesas) */
export const intLevel = (id: number, t: number) => {
  if (id < 5) return 1;
  let on = 0; for (let k = 0; k < 7; k++) if (lampOnAt(id, t, k)) on++;
  if (id === 5) return 0.22 + 0.78 * (on / 7) ** 1.5;
  if (id === 9 || id === 10) return on ? 0.46 : 0.3;
  return 0.3;
};
export const intOff = (_t: number) => false;
/** a silhueta no banco do fundo aparece no "alguém" (na volta da piscada da lâmpada) */
export const someoneAt = (id: number, t: number) => id === 10 && t >= W.alguem + 0.02;
/** porta da frente: aberta no começo (fecha no "fecha"), abre de novo na garagem no "abre" */
export const doorOpen = (id: number, t: number) => {
  if (id === 1) return 1 - smooth((t - W.fecha + 0.15) / 0.75);
  if (id === 14) return smooth((t - W.abre + 0.1) / 0.7);
  return id >= 15 ? 1 : 0;
};
/** as lâmpadas de vapor de sódio da garagem apagam no "decide" */
export const garageOff = (id: number, t: number) => id === 21 && t >= W.decide + 0.2;

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
/** câmera no referencial do ônibus, com zoom lento */
const B = (id: number, p: V3, l: V3, rate = 0.0024, rest: Partial<Cam> = {}) => (f: number) =>
  dolly(L(id, f / FPS, ...p), L(id, f / FPS, ...l), f, S0(id), rate, rest);
const Wd = (id: number, p: V3, l: V3, rate = 0.0018, rest: Partial<Cam> = {}) => (f: number) => dolly(p, l, f, S0(id), rate, rest);
const scr = (id: number): Key[] => [{ f: 0, s: B(id, SCREEN_CAM[id][0], PHONE_LOOK, 0.0022, { fov: 40, roll: SCREEN_CAM[id][1] }) }];
const CAMS: Record<number, Key[]> = {
  // gancho: de dentro, a porta da frente fechando na sua cara (a rua e o poste piscando lá fora)
  1: [{ f: 0, s: B(1, [3.75, 1.58, -0.25], [3.95, 1.45, 2.2], 0.003, { fov: 62, roll: 0.01 }) }],
  // de fora, no seu ponto: o ônibus vai embora, o poste fica para trás
  2: [{ f: 0, s: Wd(2, [6.2, 1.45, 7.8], [20, 1.9, 2.2], 0.0016, { fov: 52 }) }],
  // o letreiro, de perto, andando junto com o ônibus
  3: [{ f: 0, s: B(3, [11.6, 2.35, -1.7], [6.0, 2.62, 0.0], 0.0024, { fov: 44, roll: -0.01 }) }],
  // a rua sem nenhum poste aceso: o ônibus some no escuro (só as lanternas)
  4: [{ f: 0, s: Wd(4, [-16, 1.3, 3.4], [22, 1.7, 2.0], 0.002, { fov: 44 }) }],
  // do fundo, o corredor todo: as luzes apagam da frente pra cá
  5: [{ f: 0, s: B(5, [-5.0, 2.05, 0.15], [6, 1.55, -0.2], 0.0016, { fov: 58 }) }],
  // o celular acende e vibra no banco, do seu lado
  6: [{ f: 0, s: B(6, [4.2, 1.38, 0.0], [3.57, 0.99, -0.8], 0.0026, { fov: 46, roll: -0.01 }) }],
  7: scr(7),
  // o retrovisor: os olhos dele virados pro fundo
  8: [{ f: 0, s: B(8, [4.35, 2.02, -0.15], [5.85, 2.24, 0.0], 0.003, { fov: 32 }) }],
  // o banco do fundo, onde você estava, sob a única lâmpada acesa
  9: [{ f: 0, s: B(9, [-3.55, 1.6, -0.95], [-5.06, 1.3, 0.85], 0.0022, { fov: 50 }) }],
  // tem alguém sentado lá (mais perto)
  10: [{ f: 0, s: B(10, [-3.55, 1.6, -0.95], [-5.06, 1.3, 0.85], 0.0034, { fov: 46, roll: 0.012 }) }],
  // de fora: a entrada da garagem enorme, o ônibus entrando
  11: [{ f: 0, s: Wd(11, [GX - 44, 2.6, 15], [GX - 18, 3.2, 1], 0.0016, { fov: 52 }) }],
  // de cima: dezenas de ônibus parados, letreiros acesos
  12: [{ f: 0, s: () => ({ pos: [GX - 15, 8.2, 12.5], look: [GX + 16, 0.8, -13], fov: 60 }) },
       { f: S0(12) + 2, dur: 125, s: Wd(12, [GX - 12, 6.8, 11.5], [GX + 16, 0.9, -13], 0.0012, { fov: 60 }) }],
  // a cabine de um deles: banco do motorista vazio
  13: [{ f: 0, s: Wd(13, [GX + 16.6, 1.95, -3.6], [GX + 13.4, 1.55, -6.6], 0.0028, { fov: 46 }) }],
  // de dentro: a porta abre para a garagem
  14: [{ f: 0, s: B(14, [3.3, 1.6, -0.5], [4.0, 1.4, 2.6], 0.0024, { fov: 60 }) }],
  // o motorista de costas e o retrovisor: agora ele olha pra você
  15: [{ f: 0, s: B(15, [1.6, 1.95, 0.12], [5.3, 1.75, -0.4], 0.0028, { fov: 40 }) }],
  16: scr(16),
  // você no banco da frente: cinco segundos
  17: [{ f: 0, s: B(17, [4.45, 1.72, 1.0], [3.91, 1.2, -0.8], 0.0034, { fov: 54 }) }],
  18: scr(18),
  // opção B: você na porta, a garagem inteira na frente (de fora)
  19: [{ f: 0, s: Wd(19, [GARAGE_STOP + 6.6, 1.55, 6.9], [GARAGE_STOP + 3.9, 1.5, 3.3], 0.0022, { fov: 46 }) }],
  // a escolha: o ônibus parado no meio das filas, porta aberta
  20: [{ f: 0, s: () => ({ pos: [GX + 28, 6.5, 12], look: [GX + 6, 1.4, 0], fov: 54 }) },
       { f: S0(20) + 2, dur: 160, s: Wd(20, [GX + 25, 4.4, 11], [GX + 6, 1.5, 0], 0.001, { fov: 54 }) }],
  // CTA: o corredor entre as filas; as lâmpadas apagam no "decide"
  21: [{ f: 0, s: Wd(21, [GX + 36, 1.7, 4.6], [GX - 6, 1.9, -3.5], 0.0016, { fov: 42 }) }],
};
/** impact kicks: flip sign every frame, decay over 7 frames */
const KICKS = [W.porta + 0.75, W.vira, W.alguem, W.ultima, W.tocar - 0.4];
export const kickAt = (t: number) => {
  for (const k of KICKS) { const n = Math.round((t - k) * FPS); if (n >= 0 && n < 7) return (n % 2 ? -1 : 1) * (1 - n / 7); }
  return 0;
};
/** trepidação do ônibus andando (câmeras de dentro) e o tranco da freada */
const shake = (id: number, t: number) => (SHOTS[id - 1].inside && busMoving(id, t) ? 0.35 : 0);
export const camAt = (id: number, f: number): Cam => {
  const c = run(CAMS[id], f), a = kickAt(f / FPS), w = shake(id, f / FPS);
  const sx = w ? w * 0.004 * (Math.sin(f * 1.9) + 0.6 * Math.sin(f * 4.3 + 1)) : 0, sy = w ? w * 0.005 * Math.sin(f * 3.7 + 2) : 0;
  if (!a && !w) return c;
  const d: V3 = [c.look[0] - c.pos[0], c.look[1] - c.pos[1], c.look[2] - c.pos[2]];
  const Ln = Math.hypot(...d), h = Math.hypot(d[0], d[2]) || 1;
  const m = (3 / 640) * Math.tan((c.fov * Math.PI) / 360) * Ln * a * 2.5;
  return { ...c, look: [c.look[0] - (d[2] / h) * (m + sx * Ln), c.look[1] + 0.6 * m + sy * Ln, c.look[2] + (d[0] / h) * (m + sx * Ln)], roll: c.roll + a * 0.006 + sx * 0.4 };
};

// ---------------- lens blur per beat (cInf px at 1080; 0 = sharp) ----------------
export type Dof = { f: number; dur?: number; cInf: number; focus?: (f: number) => V3 };
type FocL = [number, V3, boolean]; // [cInf, ponto, no referencial do ônibus?]
const FOC: Record<number, FocL> = {
  1: [6, [3.9, 1.6, 1.3], true], 2: [4, [STOP_X + 6, 1.7, 2.2], false], 3: [10, [6.0, 2.7, 0], true], 4: [4, [10, 1.6, 2], false],
  5: [6, [4.5, 1.4, -0.4], true], 6: [12, PHONE_LOOK, true], 7: [16, PHONE_NEAR[7], true], 8: [14, [5.78, 2.24, 0], true],
  9: [10, [-5.06, 1.3, 0.85], true], 10: [10, [-5.06, 1.32, 0.85], true], 11: [4, [GX - 22, 2, 2], false], 12: [3, [GX + 8, 1.5, -8], false],
  13: [10, [GX + 13.4, 1.55, -6.6], false], 14: [5, [3.9, 1.6, 3.0], true], 15: [8, [5.0, 1.7, -0.5], true], 16: [16, PHONE_NEAR[16], true],
  17: [10, [3.91, 1.3, -0.8], true], 18: [16, PHONE_NEAR[18], true], 19: [6, [GARAGE_STOP + 3.9, 1.5, 3.2], false], 20: [4, [GX + 8, 1.6, 1], false],
  21: [5, [GX + 14, 1.8, 0], false],
};
export const DOF: Dof[] = SHOTS.map((s) => ({ f: s.a, cInf: FOC[s.id][0], focus: (f: number) => { const [, p, loc] = FOC[s.id]; return loc ? L(s.id, f / FPS, ...p) : p; } }));
export const dofAt = (f: number) => {
  let i = 0; while (i + 1 < DOF.length && f >= DOF[i + 1].f) i++;
  const d = DOF[i], p = DOF[Math.max(0, i - 1)];
  const k = d.dur ? Math.min(1, (f - d.f) / d.dur) : 1;
  return { cInf: p.cInf + (d.cInf - p.cInf) * k, focus: d.focus };
};
export type Fg = { a: number; b: number; kit: string; pos: V3; s?: number; yaw?: number };
export const FOREGROUND: Fg[] = [];
