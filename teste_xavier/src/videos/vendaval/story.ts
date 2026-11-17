// "A torre que uma guerra salvou": our 15 s short in the flat-characters-in-a-3D-toon-world style.
// Timeline: 4 shots timed to the narration (estimates until the voice arrives; retime LINES then).
//   S1 hook, today: leaning tower, tourists posing  | "A torre mais famosa da Itália só tá de pé porque uma guerra parou a obra."
//   S2 1178: two floors, the tower sinks, masons shocked | "No segundo andar, ela começou a afundar."
//   S3 war: soldiers march past the stump, then dusk     | "A guerra parou tudo por cem anos, o barro firmou…"
//   S5 1272: the rest goes up, bent back (the curve)     | "Quando voltaram, fizeram o resto torto pro outro lado, pra disfarçar…"
//   S6 today: the finished tower stands, tourists cheer  | "…e ela não caiu."
export const FPS = 30;
// Vídeo 12 "E se um vendaval chegasse na sua casa à noite?": suspense em 2ª pessoa com escolha A/B. Narração 71,16 s.
// Tempos das palavras em projeto_videos3d/analysis/narracao/12_words.json.
export const TOTAL = 2135;
export const T0 = 0;
export const D0 = 0; // ground height (m)
export type V3 = [number, number, number];

export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const smooth = (x: number) => { const u = clamp01(x); return u * u * (3 - 2 * u); };
export const easeOut = (u: number) => 1 - (1 - clamp01(u)) ** 4;

/** tempos das palavras (s) */
export const W = {
  noite: 1.0, casa: 2.24, ninguem: 2.96, quando: 3.78, celular: 4.2, dispara: 4.5, alarme: 5.24, silencioso: 7.86,
  tela: 9.28, defesa: 10.34, alerta: 11.64, severo: 12.12, vendaval: 13.16, noventa: 15.02, voceOlha: 17.28, rua: 18.92, calma: 20.5,
  dez: 22.1, vento: 23.94, primeiro: 25.12, assobio: 26.0, fresta: 27.12, depois: 28.06, arvores: 29.58, dobrar: 30.72,
  telha: 31.62, voando: 32.42, luz: 34.16, pisca: 34.52, apaga: 35.8, escuro: 36.8, estalo: 38.54, arvoreE: 39.92, enorme: 40.56,
  inclinando: 43.28, direcao: 44.44, celular2: 46.02, oito: 46.96, dezSeg: 48.78, opcaoA: 50.34, sai: 51.68, opcaoB: 54.34,
  tranca: 56.54, banheiro: 56.92, eai: 60.06, escolhe: 61.3, comenta: 62.18, resposta: 64.04, nao: 66.74, inscrever: 67.78, ese: 70.46,
};
// nomes antigos ainda importados pelo cast.ts (não usados aqui)
export const T_OFF = W.apaga, T_FRIDGE = 999, T_HOURS = 999, T_SINK = 999, T_WAR = 999, T_NOT = 999;

// ---------------- sets ----------------
export const SET = { street: [0, 0] as const, room: [600, 0] as const, bath: [800, 0] as const };

// ---------------- vento e árvore ----------------
/** intensidade do vento 0..1 (chega em "o vento chega", árvores dobram no "dobrar") */
export const windAt = (id: number, t: number) => (id === 18 ? 0 : t < W.vento - 0.3 ? 0 : t < W.dobrar ? 0.15 + 0.55 * smooth((t - W.vento + 0.3) / (W.dobrar - W.vento + 0.3)) : 0.7 + 0.3 * smooth((t - W.dobrar) / 1.5));
/** inclinação da árvore grande (rad, para +z = na direção da casa) */
export const leanAt = (id: number, t: number) => {
  if (id === 18 || t < W.estalo - 0.05) return 0;
  const creak = 0.05 * smooth((t - W.estalo + 0.05) / 0.5);
  if (t < W.inclinando - 0.1) return creak;
  return creak + 0.24 * smooth((t - W.inclinando + 0.1) / (W.celular2 - W.inclinando + 0.1)) + (t > W.direcao ? 0.03 * smooth((t - W.direcao) / 0.2) : 0);
};
/** "a luz pisca": intervalos (s) em que a lâmpada some antes do apagão */
export const FLICKER: [number, number][] = [[W.pisca, W.pisca + 0.1], [W.pisca + 0.3, W.pisca + 0.36], [W.pisca + 0.62, W.pisca + 0.8], [W.pisca + 1.0, W.pisca + 1.07]];
export const flickOff = (t: number) => FLICKER.some(([a, b]) => t >= a && t < b);
/** abajur da sala aceso: nos planos da sala antes do apagão, menos nas piscadas */
export const lampOn = (id: number, t: number) => [2, 3, 4, 7, 10].includes(id) && t < W.apaga && !flickOff(t);
/** relâmpagos (s): clarão na tela (Vendaval.tsx) e raio no céu nos planos externos */
export const BOLTS = [29.2, 37.95, 40.35, 44.25, 52.1, 61.0, 63.6];

// ---------------- shots ----------------
export type Light = "day" | "golden" | "night";
export type Crowd = "tourists" | "masons" | "soldiers" | "none" | "cheer" | "family" | "fridge" | "hook" | "storm" | "building" | "antenna" | "shop" | "room" | "product" | "relief" | "cta"
  | "v_hook" | "v_alarm" | "v_phone" | "v_window" | "v_street" | "v_door" | "v_lamp" | "v_dark" | "v_tree" | "v_lean" | "v_lowbat" | "v_runA" | "v_bath" | "v_choice" | "v_cta";
export type ShotDef = { id: number; a: number; b: number; light: Light; crowd: Crowd };
const F = (t: number) => Math.round(t * FPS);
const CUT = [0, F(W.quando) - 1, F(W.tela) - 1, F(W.vendaval) - 1, F(W.voceOlha) - 1, F(W.dez) - 1, F(W.primeiro) - 1, F(W.depois) - 1, F(W.telha) - 1,
  F(W.luz) - 1, F(W.apaga) - 1, F(W.arvoreE) - 1, F(W.inclinando) - 1, F(W.celular2) - 1, F(W.opcaoA) - 1, F(W.opcaoB) - 1, F(W.eai) - 1, F(W.nao) - 1, TOTAL];
const DEF: [Light, Crowd][] = [
  ["night", "v_hook"],   // 1 São 11 da noite: sua casa acesa
  ["golden", "v_alarm"], // 2 o celular dispara
  ["golden", "v_phone"], // 3 na tela: Defesa Civil, alerta severo
  ["golden", "v_phone"], // 4 vendaval, 90 km/h
  ["night", "v_window"], // 5 você olha pela janela: calma demais
  ["night", "v_street"], // 6 dez minutos depois: o vento chega
  ["golden", "v_door"],  // 7 assobio na fresta da porta
  ["night", "v_street"], // 8 as árvores dobram
  ["night", "v_window"], // 9 uma telha voando pela janela
  ["golden", "v_lamp"],  // 10 a luz pisca...
  ["night", "v_dark"],   // 11 ...e apaga; estalo grave
  ["night", "v_tree"],   // 12 a árvore enorme da frente
  ["night", "v_lean"],   // 13 inclinando na sua direção
  ["night", "v_lowbat"], // 14 8 %, 10 segundos
  ["night", "v_runA"],   // 15 opção A: sair pra rua
  ["night", "v_bath"],   // 16 opção B: banheiro sem janela
  ["night", "v_choice"], // 17 qual você escolhe? comenta A ou B
  ["night", "v_cta"],    // 18 inscreva-se / "E se..."
];
export const SHOTS: ShotDef[] = DEF.map(([light, crowd], i) => ({ id: i + 1, a: CUT[i], b: CUT[i + 1], light, crowd }));
export const XFADE: Record<number, number> = {};
export const FLASH_AT = -100;
/** quadro inicial de cada relâmpago (sem clarão dentro do banheiro) */
export const FLASHES = BOLTS.map((t) => F(t)).filter((f) => !(f >= CUT[15] && f < CUT[16]));
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
  // gancho: grua descendo até a sua casa, janelas acesas
  1: [{ f: 0, s: () => ({ pos: [-3.0, 8.0, -9], look: [1.0, 3.6, 14], fov: 56 }) },
      { f: 2, dur: 105, s: (f) => dolly([-3.2, 2.0, -3.5], [1.2, 3.6, 13], f, 0, 0.0016, { fov: 56, roll: 0.015 }) }],
  // a sala: você no sofá, o celular dispara
  2: [{ f: 0, s: (f) => dolly([600.0, 1.35, -1.9], [600.0, 1.0, 3.2], f, S0(2), 0.0026, { fov: 48 }) }],
  // a tela do celular (perto) e mais perto no "vendaval"
  3: [{ f: 0, s: (f) => dolly([600.0, 1.26, 0.1], [600.0, 1.2, 3.0], f, S0(3), 0.0022, { fov: 40, roll: -0.012 }) }],
  4: [{ f: 0, s: (f) => dolly([600.0, 1.24, 0.5], [600.0, 1.2, 3.0], f, S0(4), 0.0022, { fov: 40, roll: 0.01 }) }],
  // pela janela: a rua do outro lado, parada (moldura da janela na frente da câmera)
  5: [{ f: 0, s: (f) => dolly([-4.0, 2.6, 10.6], [-4.0, 2.2, -20], f, S0(5), 0.0018, { fov: 50 }) }],
  // dez minutos depois: a rua, as árvores começam a balançar
  6: [{ f: 0, s: (f) => dolly([-3.4, 1.6, -3.4], [1.5, 3.6, 12], f, S0(6), 0.0024, { fov: 56, roll: -0.02 }) }],
  // a fresta da porta (bem baixo, rente ao chão)
  7: [{ f: 0, s: (f) => dolly([595.5, 0.85, 0.7], [594.1, 0.6, 4.0], f, S0(7), 0.003, { fov: 50, roll: 0.03 }) }],
  // as árvores dobram (contra-plongée)
  8: [{ f: 0, s: (f) => dolly([-6.5, 1.0, -4.5], [1.5, 4.6, 10], f, S0(8), 0.0026, { fov: 62, roll: 0.05 }) }],
  // pela janela de novo: a telha passa voando
  9: [{ f: 0, s: (f) => dolly([-4.0, 2.6, 10.6], [-4.0, 2.2, -20], f, S0(9), 0.0028, { fov: 50, roll: -0.01 }) }],
  // a luz pisca (sala acesa)
  10: [{ f: 0, s: (f) => dolly([598.5, 1.45, -4.6], [598.5, 1.05, 3.2], f, S0(10), 0.0024, { fov: 60 }) }],
  // no escuro: o estalo
  11: [{ f: 0, s: (f) => dolly([600.0, 1.3, 0.4], [600.0, 1.15, 3.2], f, S0(11), 0.003, { fov: 46 }) }],
  // a árvore enorme da frente da sua casa
  12: [{ f: 0, s: (f) => dolly([-3.0, 1.4, 1.0], [2.6, 4.6, 10], f, S0(12), 0.0022, { fov: 56, roll: 0.02 }) }],
  // da porta da casa, olhando para cima: ela inclina na sua direção
  13: [{ f: 0, s: (f) => dolly([0.2, 1.3, 11.8], [3.6, 3.9, 8.7], f, S0(13), 0.0035, { fov: 66, roll: -0.04 }) }],
  // o celular com 8 %
  14: [{ f: 0, s: (f) => dolly([600.0, 1.25, 0.6], [600.0, 1.2, 3.0], f, S0(14), 0.0026, { fov: 42, roll: 0.012 }) }],
  // opção A: você sai correndo pela porta, pra rua
  15: [{ f: 0, s: (f) => dolly([0.3, 1.7, 2.0], [0.3, 2.2, 12], f, S0(15), 0.0022, { fov: 54, roll: 0.02 }) }],
  // opção B: o banheiro sem janela
  16: [{ f: 0, s: (f) => dolly([800.0, 1.55, -1.3], [800.0, 1.2, 3.0], f, S0(16), 0.0024, { fov: 52, roll: -0.015 }) }],
  // a escolha: a casa e a árvore inclinada
  17: [{ f: 0, s: (f) => dolly([-1.5, 2.2, -1.0], [1.4, 3.6, 11], f, S0(17), 0.0016, { fov: 56 }) }],
  // CTA: tudo calmo de novo, você acenando na porta
  18: [{ f: 0, s: (f) => dolly([0.5, 1.7, 4.6], [0.3, 1.55, 12], f, S0(18), 0.0022, { fov: 46, roll: 0.012 }) }],
};
/** impact kicks: flip sign every frame, decay over 7 frames */
const KICKS = [W.dispara, W.estalo, W.direcao];
export const kickAt = (t: number) => {
  for (const k of KICKS) { const n = Math.round((t - k) * FPS); if (n >= 0 && n < 7) return (n % 2 ? -1 : 1) * (1 - n / 7); }
  return 0;
};
/** tremor de vento na câmera (planos externos com vento) */
const shake = (id: number, t: number) => (id === 6 || id === 8 || id === 12 || id === 13 || id === 15 || id === 17 ? windAt(id, t) : 0);
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
  1: [4, [1.0, 3.0, 10.5]], 2: [10, [600, 1.0, 2.6]], 3: [14, [600, 1.2, 1.9]], 4: [16, [600, 1.2, 1.9]], 5: [4, [-4, 2.5, -18]],
  6: [6, [3.5, 3.0, 9]], 7: [12, [594.1, 0.3, 3.95]], 8: [4, [1.5, 4.0, 9]], 9: [4, [-4, 2.5, -10]], 10: [8, [599.2, 1.0, 2.8]],
  11: [12, [600, 1.1, 2.6]], 12: [6, [3.5, 4, 9]], 13: [6, [3.5, 5, 8.6]], 14: [16, [600, 1.2, 1.9]], 15: [8, [0.3, 1.4, 8]],
  16: [10, [800, 1.1, 2.2]], 17: [5, [2.5, 3.5, 9.5]], 18: [9, [0.2, 1.3, 10.4]],
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
