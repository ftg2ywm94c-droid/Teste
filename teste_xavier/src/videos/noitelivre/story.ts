// "A torre que uma guerra salvou": our 15 s short in the flat-characters-in-a-3D-toon-world style.
// Timeline: 4 shots timed to the narration (estimates until the voice arrives; retime LINES then).
//   S1 hook, today: leaning tower, tourists posing  | "A torre mais famosa da Itália só tá de pé porque uma guerra parou a obra."
//   S2 1178: two floors, the tower sinks, masons shocked | "No segundo andar, ela começou a afundar."
//   S3 war: soldiers march past the stump, then dusk     | "A guerra parou tudo por cem anos, o barro firmou…"
//   S5 1272: the rest goes up, bent back (the curve)     | "Quando voltaram, fizeram o resto torto pro outro lado, pra disfarçar…"
//   S6 today: the finished tower stands, tourists cheer  | "…e ela não caiu."
export const FPS = 30;
// Vídeo 19 "A Noite Livre · Ep. 1": a família trancada, o Thor na rua, 3 máscaras na esquina. Elenco de vozes.
// Tempos REAIS: narração (ElevenLabs, Ana Dias) + falas dos personagens, faixa narracao/19_narracao.mp3 (64,58 s).
// Palavras em projeto_videos3d/analysis/narracao/19_words.json; falas em narracao/19_vozes/19_linhas.json.
import { TALK } from "./talk";
export const TOTAL = 1937;
export const T0 = 0;
export const D0 = 0; // ground height (m)
export type V3 = [number, number, number];

export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const smooth = (x: number) => { const u = clamp01(x); return u * u * (3 - 2 * u); };
export const easeOut = (u: number) => 1 - (1 - clamp01(u)) ** 4;

export type Who = "narr" | "tv" | "pai" | "mae" | "bia";
/** boca 0..1 de cada personagem, tirada do envelope do áudio dele (talk.ts) */
export const talkAt = (who: Who, t: number) => { const s2 = TALK[who]; if (!s2) return 0; const c = s2.charCodeAt(Math.round(t * 30)) - 48; return c > 0 ? c / 3 : 0; };
/** marcos (s) */
export const W = {
  inicio: 0, tv1: 3.55, ancora: 8.36, rostos: 12.25, cortina: 16.24, tranca: 18.76, cade: 21.12, quintal: 22.39, portao: 24.59, ultimo: 25.85,
  rua: 28.5, esquina: 32.2, porta: 35.93, thor: 37.32, dois: 38.86, correr: 40.53, vira: 43.62, quieto: 45.37, abana: 47.76, mascaras: 48.55,
  decide: 50.53, opcaoA: 52.1, opcaoB: 54.6, comenta: 58.2, se: 62.55, trancado: 19.02, latirPara: 46.78,
  // nomes herdados (código antigo)
  caiu: -100, liga: -100, jogador: -100, alguma: -100, param: -100,
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
/** vento 0..1: noite parada */
export const windAt = (_id: number, _t: number) => 0;
export const leanAt = (_id: number, _t: number) => 0;
export const fallen = (_t: number) => false;
export const FLICKER: [number, number][] = [];
export const flickOff = (_t: number) => false;
/** o abajur da sala fica aceso (a casa tem luz; o perigo é lá fora) */
export const lampOn = (id: number, _t: number) => ROOM.includes(id);
export const BOLTS: number[] = [];
export const sparkAt = (_t: number) => false;
export const doorAt = (_id: number, _t: number) => 0;
export const sirenX = (_t: number) => -95;
export const sirenK = (_t: number) => 0;
export const sirenPulse = (_t: number) => 0;
/** sala com luz baixa (abajur + TV) */
export const darkAt = (id: number, _t: number) => (ROOM.includes(id) ? 0.3 : 0);
/** a TV: telejornal com o relógio (21:57 / 21:58) */
export type TvState = "news57" | "news58" | "off";
export const tvState = (id: number, t: number): TvState => (id === 24 ? "news57" : ROOM.includes(id) ? (t >= W.dois ? "news58" : "news57") : "off");
export const tvOn = (id: number, t: number) => tvState(id, t) !== "off";
export const ledOn = (_id: number, _t: number) => false;
export const vibAt = (_id: number, _t: number) => 0;
/** o Thor late sem parar na rua */
/** o Thor late sem parar até "para de latir" (depois fica quieto e abana o rabo) */
export const barkAt = (t: number) => t < W.latirPara && Math.floor(t * 4.6) % 3 !== 2;
/** rabo abanando (radianos) depois que para de latir */
export const wagAt = (t: number) => (t < W.latirPara ? 0 : 0.5 * Math.sin(t * 2 * Math.PI * 3.2));
export const KNOCKS: number[] = [];
/** a cortina: 0 aberta .. 1 fechada (a mãe fecha no plano 5; no plano 20 você abre uma fresta) */
export const curtainAt = (id: number, t: number) => (id < 5 || id === 24 ? 0 : id === 5 ? smooth((t - W.cortina - 0.6) / 1.4) : id === 22 ? 0.55 : 1);

// ---------------- shots ----------------
export type Light = "day" | "golden" | "night";
export type Crowd = string;
export type ShotDef = { id: number; a: number; b: number; light: Light; crowd: Crowd };
const F = (t: number) => Math.round(t * FPS);
const CUT = [0, ...[W.tv1, W.ancora, W.rostos, W.cortina, W.tranca, W.cade, W.quintal, W.portao, W.ultimo, W.rua, W.esquina, W.porta, W.thor,
  W.dois, W.correr, W.vira, W.quieto, W.mascaras, W.decide, W.opcaoA, W.opcaoB, W.comenta, W.se].map((t) => F(t)), TOTAL];
const DEF: [Light, Crowd][] = [
  ["night", "n_sofa"],     // 1 imagina: a família no sofá olhando a TV
  ["night", "n_tv"],       // 2 a TV: NOITE LIVRE 22H, 21:57
  ["night", "n_anchor"],   // 3 o apresentador: atenção, faltam três minutos
  ["night", "n_faces"],    // 4 os rostos ouvindo (a polícia não vai atender)
  ["night", "n_curtain"],  // 5 mãe: fecha essa cortina
  ["night", "n_lock"],     // 6 pai: tudo trancado
  ["night", "n_bed"],      // 7 Bia: cadê o Thor? (caminha vazia)
  ["night", "n_peek"],     // 8 pai: tava no quintal
  ["night", "n_gate"],     // 9 o portão tá aberto (lá fora)
  ["night", "n_look"],     // 10 quem foi o último? todos olham pra você / foi você
  ["night", "n_thor"],     // 11 o Thor latindo no meio da rua
  ["night", "n_masks"],    // 12 três máscaras na esquina
  ["night", "n_door"],     // 13 mãe: ninguém abre essa porta
  ["night", "n_bia"],      // 14 Bia: mãe, é o Thor!
  ["night", "n_tv2"],      // 15 TV: faltam dois minutos (21:58)
  ["night", "n_pai"],      // 16 pai: se correr...
  ["night", "n_turn"],     // 17 e se eles chegarem primeiro? (uma máscara vira pra casa)
  ["night", "n_wag"],      // 18 aí o Thor para de latir e abana o rabo
  ["night", "n_wagmask"],  // 19 pra uma das máscaras
  ["night", "n_you"],      // 20 você decide
  ["night", "n_optA"],     // 21 opção A: a porta
  ["night", "n_optB"],     // 22 opção B: a janela
  ["night", "n_choice"],   // 23 comenta A ou B
  ["night", "n_loop"],     // 24 E se... (= quadro 0: o vídeo emenda no começo)
];
const ROOM = [1, 2, 3, 4, 5, 6, 7, 8, 10, 13, 14, 15, 16, 20, 21, 22, 23, 24];
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
const dl = (id: number, pos: V3, look: V3, fov: number, rate = 0.0022): Key[] => [{ f: 0, s: (f) => dolly(pos, look, f, S0(id), rate, { fov }) }];
const CAMS: Record<number, Key[]> = {
  1: dl(1, [600.0, 1.85, -0.9], [600.0, 0.95, 2.5], 66, 0.0012),
  2: dl(2, [600.0, 1.12, 2.0], [600.0, 1.1, -0.62], 44, 0.0016),
  3: dl(3, [600.0, 1.12, 1.15], [600.0, 1.12, -0.62], 46, 0.0018),
  4: dl(4, [600.0, 1.2, 0.3], [600.0, 1.0, 2.44], 60, 0.0022),
  5: dl(5, [601.9, 1.45, 1.3], [603.2, 1.35, 3.7], 52),
  6: dl(6, [595.5, 1.45, 1.6], [594.2, 1.2, 3.7], 50),
  7: dl(7, [597.15, 1.65, -0.35], [597.3, 0.65, 1.8], 56),
  8: dl(8, [601.2, 1.45, 1.5], [602.5, 1.4, 3.7], 50),
  9: dl(9, [3.1, 1.5, 1.2], [2.2, 1.0, 10.0], 56, 0.0018),
  10: dl(10, [597.0, 1.55, -1.9], [597.0, 1.1, 2.0], 56, 0.0022),
  11: dl(11, [0.7, 0.5, -6.2], [1.5, 0.55, -3.0], 46, 0.0024),
  12: dl(12, [-7.0, 1.4, -10.0], [-12.0, 1.2, -4.6], 46, 0.0022),
  13: dl(13, [594.6, 1.4, 1.6], [594.3, 1.25, 3.4], 48, 0.0026),
  14: dl(14, [597.75, 1.4, 0.35], [597.8, 1.25, 1.9], 46, 0.003),
  15: dl(15, [600.0, 1.12, 1.9], [600.0, 1.1, -0.62], 44, 0.0016),
  16: dl(16, [597.4, 1.4, 0.6], [596.0, 1.3, 2.2], 44, 0.0026),
  17: dl(17, [-2.0, 1.5, 6.4], [-12.0, 1.35, -4.6], 26, 0.0026),
  18: dl(18, [2.5, 0.5, -0.85], [1.6, 0.5, -3.0], 50, 0.0022),
  19: dl(19, [4.6, 1.0, -1.7], [-0.6, 0.75, -3.4], 42, 0.0016),
  20: dl(20, [597.0, 1.4, 0.55], [597.0, 1.3, 2.0], 44, 0.003),
  21: dl(21, [594.6, 1.4, 1.6], [594.3, 1.2, 3.4], 50),
  22: dl(22, [601.9, 1.45, 1.3], [603.2, 1.4, 3.7], 52),
  23: dl(23, [597.0, 1.75, -2.4], [597.0, 1.0, 2.0], 58, 0.0016),
  // o fecho em loop: a mesma câmera do quadro 0 do plano 1, parada
  // loop: the same slow zoom as shot 1, arriving at shot 1's frame-0 lens exactly on the frame after the last one (no freeze before the seam)
  24: [{ f: 0, s: (f) => ({ pos: [600.0, 1.85, -0.9], look: [600.0, 0.95, 2.5], fov: (360 / Math.PI) * Math.atan(Math.tan((66 * Math.PI) / 360) * Math.exp(-0.0012 * (f - TOTAL))) }) }],
};
/** impact kicks: flip sign every frame, decay over 7 frames */
const KICKS: number[] = [];
export const kickAt = (t: number) => {
  for (const k of KICKS) { const n = Math.round((t - k) * FPS); if (n >= 0 && n < 7) return (n % 2 ? -1 : 1) * (1 - n / 7); }
  return 0;
};
/** tremor de vento na câmera (planos externos com vento) */
/** tremor: vento nos planos de fora; a casa tremendo no banheiro logo depois do estrondo */
const shake = (_id: number, _t: number) => 0;
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
const FOC: Record<number, [number, V3]> = Object.fromEntries(Object.entries(CAMS).map(([k, keys]) => { const c = keys[0].s(0); return [Number(k), [6, c.look]]; }));
export const DOF: Dof[] = SHOTS.map((s) => ({ f: s.a, cInf: FOC[s.id][0], focus: () => FOC[s.id][1] }));
export const dofAt = (f: number) => {
  let i = 0; while (i + 1 < DOF.length && f >= DOF[i + 1].f) i++;
  const d = DOF[i], p = DOF[Math.max(0, i - 1)];
  const k = d.dur ? Math.min(1, (f - d.f) / d.dur) : 1;
  return { cInf: p.cInf + (d.cInf - p.cInf) * k, focus: d.focus };
};
export type Fg = { a: number; b: number; kit: string; pos: V3; s?: number; yaw?: number };
export const FOREGROUND: Fg[] = [];
