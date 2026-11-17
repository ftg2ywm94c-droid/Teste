// Vídeo 13 "Você decide · O último ônibus · Ep. 1": suspense em 2ª pessoa, a audiência escolhe a continuação.
// Narração 70,61 s (projeto_videos3d/analysis/narracao/13_words.json). O ônibus anda de verdade pela rua noturna
// do vídeo 12 (eixo +x do mundo, porta do lado +z, a calçada); câmeras e cartões de dentro são dados no referencial
// do ônibus (u para a frente, y para cima, v para o lado da porta) e convertidos pela posição busX do plano.
export const FPS = 30;
export const TOTAL = 2118;
export const T0 = 0;
export const D0 = 0; // ground height (m)
export type V3 = [number, number, number];

export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const smooth = (x: number) => { const u = clamp01(x); return u * u * (3 - 2 * u); };
export const easeOut = (u: number) => 1 - (1 - clamp01(u)) ** 4;

/** tempos das palavras (s) */
export const W = {
  meia: 0.0, pega: 1.7, so: 3.5, motorista: 4.82, senta: 5.84, fundo: 6.62, encosta: 7.48, janela: 8.48, dorme: 9.48,
  ate: 10.42, celular: 10.92, tocar: 11.88, naoE: 12.58, banco: 14.12, frente: 14.66, sozinho: 15.54, ninguem: 16.42,
  ele1: 17.6, para: 17.88, toca: 18.9, voce2: 20.28, aproxima: 20.9, tela: 21.64, numero: 22.8, mensagem: 24.7,
  naoDesce: 25.84, ponto: 27.28, olha: 28.36, motorista2: 29.16, ele2: 30.14, encara: 30.54, retrovisor: 31.06, desvia: 32.02,
  chega: 33.32, outra: 33.64, ele3: 35.12, sabe: 35.8, viu: 36.64, onibus: 37.42, frear: 38.36, proximo: 39.22, seu: 40.24,
  porta: 40.86, abre: 41.32, rua: 42.8, vazia: 43.14, poste: 44.46, piscando: 44.78, celular3: 45.94, vibra: 46.46, fica: 48.4,
  sentado: 48.62, voceTem: 49.8, cinco: 50.38, segundos: 50.88, opcaoA: 52.04, desce: 53.34, opcaoB: 55.62, fica2: 57.42,
  descobre: 58.74, vai: 60.2, comenta: 61.0, ou: 61.82, resposta: 63.24, episodio: 65.82, se: 66.76, inscreve: 67.04, decide: 69.98,
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
export const STOP_X = 8.2;      // parado no ponto: a porta da frente (u ~ 3.9) fica a ~2 m do poste piscando (x = 14)
export const POLE_X = 12.1;   // o poste do ponto, logo na frente da porta da frente (pisca depois da parada)
export const POLE_Z = 5.0;
export const DOOR_U: [number, number] = [3.25, 4.55];
export const FRONT_SEAT: V3 = [3.55, 0, -0.8];   // o banco da frente (atrás do motorista), onde está o celular
export const BACK_SEAT: V3 = [-5.5, 0, 0.85];    // você, no fundo, do lado da janela da calçada
export const FLOOR_Y = 0.4, CUSHION_Y = 0.88;
/** celular "na mão": ponto a ~0,42 m na frente da câmera nos planos da tela (referencial do ônibus); a DOF foca nele */
export const PHONE_LOOK: V3 = [3.57, 0.99, -0.8];
export const SCREEN_CAM: Record<number, [V3, number]> = { 9: [[3.9, 1.45, -0.35], -0.012], 10: [[3.92, 1.43, -0.38], 0.01], 13: [[3.88, 1.46, -0.33], -0.016], 16: [[3.9, 1.44, -0.36], 0.014] };
export const PHONE_NEAR: Record<number, V3> = Object.fromEntries(Object.entries(SCREEN_CAM).map(([k, [p]]) => {
  const d = PHONE_LOOK.map((v, i) => v - p[i]), n = Math.hypot(...d); return [k, p.map((v, i) => v + (0.42 * d[i]) / n) as V3];
}));

// ---------------- shots ----------------
export type Light = "day" | "golden" | "night";
export type Crowd = string;
export type ShotDef = { id: number; a: number; b: number; light: Light; crowd: Crowd; inside: boolean };
const F = (t: number) => Math.round(t * FPS);
const CUT = [0, F(W.so) - 1, F(W.senta) - 1, F(W.ate) - 1, F(W.naoE) - 1, F(W.banco) - 1, F(W.ele1) - 1, F(W.voce2) - 1, F(W.numero) - 1, F(W.naoDesce) - 1,
  F(W.olha) - 1, F(W.ele2) - 1, F(W.chega) - 1, F(W.onibus) - 1, F(W.porta) - 1, F(W.celular3) - 1, F(W.voceTem) - 1, F(W.opcaoA) - 1,
  F(W.opcaoB) - 1, F(W.comenta) - 1, F(W.se) - 1, TOTAL];
const DEF: [Crowd, boolean][] = [
  ["b_ext", false],     // 1 meia-noite e dez: o último ônibus vem pela rua vazia
  ["b_wide", true],     // 2 só você e o motorista
  ["b_doze", true],     // 3 você senta no fundo, encosta na janela, quase dorme
  ["b_wake", true],     // 4 um celular começa a tocar (lá na frente)
  ["b_awake", true],    // 5 não é o seu: você acorda e olha
  ["b_ring", true],     // 6 no banco da frente, sozinho; ninguém pega
  ["b_ring2", true],    // 7 ele para... e toca de novo
  ["b_walk", true],     // 8 você se aproxima
  ["b_screen", true],   // 9 número desconhecido e uma mensagem
  ["b_screen", true],   // 10 NÃO DESCE NO PRÓXIMO PONTO
  ["b_driver", true],   // 11 você olha para o motorista
  ["b_mirror", true],   // 12 ele te encara pelo retrovisor e desvia
  ["b_screen", true],   // 13 ELE JÁ SABE QUE VOCÊ VIU
  ["b_brake", false],   // 14 o ônibus freia: o próximo ponto é o seu
  ["b_door", true],     // 15 a porta abre: rua vazia, poste piscando
  ["b_screen", true],   // 16 FICA SENTADO
  ["b_you5", true],     // 17 você tem cinco segundos
  ["b_optA", false],    // 18 opção A: descer no seu ponto
  ["b_optB", true],     // 19 opção B: ficar e descobrir pra onde ele vai
  ["b_choice", false],  // 20 comenta A ou B
  ["b_cta", false],     // 21 se inscreve / você decide
];
export const SHOTS: ShotDef[] = DEF.map(([crowd, inside], i) => ({ id: i + 1, a: CUT[i], b: CUT[i + 1], light: "night", crowd, inside }));
export const XFADE: Record<number, number> = {};
export const FLASH_AT = -100;
export const FLASHES: number[] = [];
export const shotAt = (f: number) => SHOTS.find((s) => f >= s.a && f < s.b) ?? SHOTS[SHOTS.length - 1];
export const layersAt = (f: number): { id: number; alpha: number }[] => [{ id: shotAt(f).id, alpha: 1 }];
const tA = (id: number) => SHOTS[id - 1].a / FPS;

/** posição do ônibus (x do mundo) no plano id, no tempo t */
const SPEED = 8;
export const busX = (id: number, t: number) => {
  switch (id) {
    case 1: return -24 + SPEED * t;
    case 14: { const a = SPEED / (W.seu - tA(14)); return t < W.seu ? STOP_X - 0.5 * a * (W.seu - t) ** 2 : STOP_X; }
    case 15: case 16: case 17: case 18: case 20: return STOP_X;
    case 21: return STOP_X + 0.5 * 1.6 * Math.max(0, t - tA(21) - 0.6) ** 2;
    default: return -26 + SPEED * (t - tA(id));
  }
};
export const busMoving = (id: number, t: number) => busX(id, t + 0.05) - busX(id, t) > 0.004;
/** referencial do ônibus -> mundo */
export const L = (id: number, t: number, u: number, y: number, v: number): V3 => [busX(id, t) + u, y, BZ + v];

/** o poste do ponto pisca (true = apagado) a partir da parada */
const hh = (i: number) => { const x = Math.sin(i * 127.1 + 31.7) * 43758.5453; return x - Math.floor(x); };
export const poleOff = (t: number) => {
  if (t < W.seu - 0.4) return false;
  const n = Math.floor(t * 7.5);
  return hh(n) < 0.32 || (hh(n + 500) < 0.2 && (t * 30) % 3 < 1);
};
/** luzes de dentro do ônibus piscam no "fica sentado" */
export const INT_FLICK: [number, number][] = [[W.fica - 0.05, W.fica + 0.05], [W.fica + 0.2, W.fica + 0.27], [W.fica + 0.42, W.fica + 0.47]];
export const intOff = (t: number) => INT_FLICK.some(([a, b]) => t >= a && t < b);

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
const scr = (id: number): Key[] => [{ f: 0, s: B(id, SCREEN_CAM[id][0], PHONE_LOOK, 0.0022, { fov: 40, roll: SCREEN_CAM[id][1] }) }];
const CAMS: Record<number, Key[]> = {
  // gancho: a rua vazia à meia-noite, o ônibus vem pela pista (câmera na calçada, descendo)
  1: [{ f: 0, s: () => ({ pos: [10, 5.5, 8.6], look: [-12, 1.6, 2], fov: 48 }) },
      { f: 2, dur: 100, s: (f) => dolly([9, 1.6, 7.4], [-8, 1.9, 2], f, 0, 0.0016, { fov: 48, roll: 0.012 }) }],
  // dentro: do fundo, o corredor vazio até o motorista
  2: [{ f: 0, s: B(2, [-5.0, 2.05, 0.15], [6, 1.55, -0.2], 0.002, { fov: 58 }) }],
  // você no fundo, cabeça na janela (câmera entre as barras)
  3: [{ f: 0, s: B(3, [-3.75, 1.62, -0.55], [-5.42, 1.42, 0.85], 0.0024, { fov: 50 }) }],
  // o celular acende no banco da frente (câmera no corredor, à frente do banco)
  4: [{ f: 0, s: B(4, [4.2, 1.38, 0.0], [3.57, 0.99, -0.8], 0.0026, { fov: 46, roll: -0.01 }) }],
  // você acordou: olha lá para a frente
  5: [{ f: 0, s: B(5, [-3.75, 1.6, -0.55], [-5.42, 1.42, 0.85], 0.003, { fov: 46, roll: 0.012 }) }],
  // o celular sozinho no banco, o ônibus vazio atrás
  6: [{ f: 0, s: B(6, [4.25, 1.72, 0.3], [3.4, 1.0, -0.8], 0.0022, { fov: 56 }) }],
  // ele para... e toca de novo
  7: [{ f: 0, s: B(7, [4.15, 1.3, 0.1], [3.57, 0.99, -0.8], 0.0026, { fov: 44, roll: 0.01 }) }],
  // você se aproxima (câmera subjetiva andando pelo corredor e olhando para o banco)
  8: [{ f: 0, s: (f) => ({ pos: L(8, f / FPS, -3.6, 1.66, 0.05), look: L(8, f / FPS, 5.5, 1.35, -0.4), fov: 50 }) },
      { f: S0(8) + 2, dur: 50, s: (f) => ({ pos: L(8, f / FPS, 2.9, 1.64, 0.05), look: L(8, f / FPS, 5.5, 1.3, -0.5), fov: 50 }) },
      { f: S0(8) + 46, dur: 28, s: (f) => ({ pos: L(8, f / FPS, 3.85, 1.6, 0.05), look: L(8, f / FPS, ...PHONE_LOOK), fov: 46 }) }],
  // a tela (perto)
  9: scr(9), 10: scr(10),
  // você olha para o motorista (de costas, lá na frente)
  11: [{ f: 0, s: B(11, [1.5, 1.95, 0.12], [5.3, 1.6, -0.5], 0.0028, { fov: 42 }) }],
  // o retrovisor: os olhos dele
  12: [{ f: 0, s: B(12, [4.35, 2.02, -0.15], [5.85, 2.24, 0.0], 0.003, { fov: 32 }) }],
  13: scr(13),
  // de fora: o ônibus freia no ponto (câmera na calçada, depois do poste)
  14: [{ f: 0, s: (f) => dolly([21.5, 1.45, 7.8], [6.5, 1.9, 2.4], f, S0(14), 0.0018, { fov: 50 }) }],
  // de dentro: a porta abre para a rua vazia e o poste piscando
  15: [{ f: 0, s: B(15, [2.55, 1.62, -0.9], [3.9, 1.85, 3.0], 0.0022, { fov: 54 }) }],
  16: scr(16),
  // você, em pé entre a porta e o banco: cinco segundos
  17: [{ f: 0, s: B(17, [0.2, 1.72, 0.25], [3.0, 1.45, 0.12], 0.0036, { fov: 50 }) }],
  // opção A: você na porta, olhando a rua (de fora, da calçada)
  18: [{ f: 0, s: (f) => dolly([11.0, 1.45, 6.7], [12.1, 1.6, 3.2], f, S0(18), 0.0022, { fov: 48 }) }],
  // opção B: você sentado no banco da frente, o ônibus andando
  19: [{ f: 0, s: B(19, [4.2, 1.7, 1.0], [3.55, 1.3, -0.8], 0.002, { fov: 54 }) }],
  // a escolha: o ônibus parado no ponto, porta aberta, poste piscando
  20: [{ f: 0, s: () => ({ pos: [22, 4.2, 10.5], look: [9.5, 1.6, 2.4], fov: 52 }) },
       { f: S0(20) + 2, dur: 150, s: (f) => dolly([19.5, 2.2, 9.2], [9.5, 1.7, 2.4], f, S0(20), 0.0012, { fov: 52 }) }],
  // CTA: o ônibus vai embora pela rua
  21: [{ f: 0, s: (f) => dolly([-12.0, 1.6, 2.6], [30, 1.7, 2.0], f, S0(21), 0.0016, { fov: 46 }) }],
};
/** impact kicks: flip sign every frame, decay over 7 frames */
const KICKS = [W.celular, W.naoDesce, W.fica];
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
  1: [4, [-6, 1.6, 2], false], 2: [6, [4.5, 1.4, -0.4], true], 3: [10, [-5.42, 1.3, 0.85], true], 4: [12, PHONE_LOOK, true],
  5: [10, [-5.42, 1.35, 0.85], true], 6: [8, PHONE_LOOK, true], 7: [12, PHONE_LOOK, true], 8: [6, PHONE_LOOK, true],
  9: [16, PHONE_NEAR[9], true], 10: [16, PHONE_NEAR[10], true], 11: [8, [5.0, 1.6, -0.7], true], 12: [14, [5.78, 2.24, 0], true],
  13: [16, PHONE_NEAR[13], true], 14: [4, [9, 1.6, 2.4], false], 15: [5, [3.9, 1.6, 3.0], true], 16: [16, PHONE_NEAR[16], true],
  17: [10, [3.0, 1.45, 0.12], true], 18: [6, [12.1, 1.5, 3.2], false], 19: [10, [3.55, 1.3, -0.8], true], 20: [4, [10, 1.6, 2.4], false],
  21: [4, [6, 1.6, 2], false],
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
