// "A torre que uma guerra salvou": our 15 s short in the flat-characters-in-a-3D-toon-world style.
// Timeline: 4 shots timed to the narration (estimates until the voice arrives; retime LINES then).
//   S1 hook, today: leaning tower, tourists posing  | "A torre mais famosa da Itália só tá de pé porque uma guerra parou a obra."
//   S2 1178: two floors, the tower sinks, masons shocked | "No segundo andar, ela começou a afundar."
//   S3 war: soldiers march past the stump, then dusk     | "A guerra parou tudo por cem anos, o barro firmou…"
//   S5 1272: the rest goes up, bent back (the curve)     | "Quando voltaram, fizeram o resto torto pro outro lado, pra disfarçar…"
//   S6 today: the finished tower stands, tourists cheer  | "…e ela não caiu."
export const FPS = 30;
// PILOTO de qualidade (15 s): luz real (poste e lanterna), rua com textura, câmera que acompanha a fala, celular na mão.
// Narração: narracao/piloto/piloto_narracao.mp3 (15,22 s; Spuds Oxley, eleven_v3). Palavras em analysis/narracao/piloto_words.json.
import { TALK } from "./talk";
export const TOTAL = 468;
export const T0 = 0;
export const D0 = 0; // ground height (m)
export type V3 = [number, number, number];

export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const smooth = (x: number) => { const u = clamp01(x); return u * u * (3 - 2 * u); };
export const easeOut = (u: number) => 1 - (1 - clamp01(u)) ** 4;

export type Who = "narr" | "tv" | "pai" | "mae" | "bia";
export const talkAt = (who: Who, t: number) => { const s2 = TALK[who]; if (!s2) return 0; const c = s2.charCodeAt(Math.round(t * 30)) - 48; return c > 0 ? c / 3 : 0; };
/** marcos (s), das palavras do áudio */
export const W = {
  inicio: 0, poste: 3.9, mao: 7.35, rua2: 9.95, chave: 12.45,
  pisca: 4.94, apaga: 6.12, liga: 8.14, alguem: 11.2,
  relogio: -100, senta: -100, cel: -100, msg1: -100, foto: -100, msg2: -100, chuva: -100, bate: -100, corredor: -100,
  olho: -100, ela: -100, casaco: -100, janela: -100, celia: -100, marido: -100, rua: -100, macaneta: -100, vibra: -100,
  msg3: -100, porta2: -100, digitando: -100, decide: -100, opcaoA: -100, opcaoB: -100, comenta: -100, se: 999,
  acende: -100, knock1: -100, knock2: -100, knock3: -100, gira: -100,
  // nomes herdados (código antigo)
  tv1: -100, ancora: -100, rostos: -100, cortina: -100, tranca: -100, cade: -100, quintal: -100, portao: -100, ultimo: -100,
  esquina: -100, porta: -100, thor: -100, dois: -100, correr: -100, vira: -100, quieto: -100, abana: -100, mascaras: -100, trancado: -100, latirPara: -100,
  caiu: -100, liga: -100, jogador: -100, alguma: -100, param: -100,
  seis: -100, liga0: -100, n193: -100, chama: -100, duas: -100, atendem: -100, fala: -100, endereco: -100, arvore: -100, fio: -100,
  vizinha: -100, outro: -100, voz: -100, nao: -100, fica: -100, equipe: -100, ligacao: -100, celular: -100, apaga: -100,
  la: -100, sirene: -100, e1: -100, para: -100, silencio: -100, batem: -100,
  forte: -100, e2: -100, abre: -100, filho: -100, eu: -100, entre: -100, e3: -100, fio2: -100, ainda: -100, faisca: -100,
  atravessa: -100, grita: -100,
  estrondo: -10, casa: -9, silencio0: -8, voceAbre: -100, aguentou: -100,
  apaga0: -1, estalo: 999, inclinando: 999, celular2: 999, direcao: 999, pisca: 999, dobrar: 0, vento: -1,
};
export const T_OFF = -1, T_FRIDGE = 999, T_HOURS = 999, T_SINK = 999, T_WAR = 999, T_NOT = 999;

// ---------------- sets ----------------
export const SET = { street: [0, 0] as const, room: [600, 0] as const, bed: [1000, 0] as const, rua: [2000, 0] as const, farm: [-200, -300] as const };

/** vento fraco da chuva (as árvores da rua balançam de leve) */
export const windAt = (_id: number, _t: number) => 0;
export const leanAt = (_id: number, _t: number) => 0;
export const fallen = (_t: number) => false;
export const FLICKER: [number, number][] = [];
export const flickOff = (_t: number) => false;
/** 3h da manhã: as luzes da casa estão apagadas */
export const lampOn = (_id: number, _t: number) => false;
/** relâmpagos (s): o primeiro em "chover", os outros nos picos de medo */
export const BOLTS: number[] = [];
export const sparkAt = (_t: number) => false;
export const doorAt = (_id: number, _t: number) => 0;
export const sirenX = (_t: number) => -95;
export const sirenK = (_t: number) => 0;
export const sirenPulse = (_t: number) => 0;
/** casa no escuro (só a luz da rua e a do celular) */
export const darkAt = (_id: number, _t: number) => 0.55;   // piloto: a luz do "céu" bem baixa, para os postes e a lanterna aparecerem
export type TvState = "news57" | "news58" | "off";
export const tvState = (_id: number, _t: number): TvState => "off";
export const tvOn = (_id: number, _t: number) => false;
export const ledOn = (_id: number, _t: number) => false;
export const vibAt = (_id: number, _t: number) => 0;
export const barkAt = (_t: number) => false;
export const wagAt = (_t: number) => 0;
export const KNOCKS: number[] = [W.knock1, W.knock2, W.knock3];
/** a cortina da sala: fechada; na janela (plano 14) você abre uma fresta */
export const curtainAt = (id: number, t: number) => (id === 14 ? 1 - 0.45 * smooth((t - W.janela - 0.5) / 0.8) : 1);
/** o despertador pisca 03:00 (liga no 1º quadro, apaga no "celular acende") */
export const alarmAt = (t: number) => t < W.cel + 0.4 && Math.floor(t * 2.2) % 2 === 0;
/** a tela do celular acesa */
export const phoneOn = (t: number) => t >= W.acende;
/** o poste da esquina: 1 aceso, pisca entre "pisca" e "apaga", 0 apagado */
export const poleAt = (t: number) => {
  if (t < W.pisca) return 1; if (t >= W.apaga) return 0;
  const k = Math.floor((t - W.pisca) * 30); return [1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0][k] ?? 0;
};
/** a lanterna do celular */
export const torchOn = (t: number) => t >= W.liga;
/** você andando pela calçada até parar sob o poste (z em metros; anda para -z, de frente para a câmera do plano 1) */
export const youZ = (t: number) => 21.0 - 1.15 * Math.min(t, W.poste + 0.6);
/** para onde a lanterna aponta (ponto no mundo) */
export const torchAim = (t: number): V3 => {
  if (t < W.rua2) return [2000.1, 0.0, 9.0];
  const u = smooth((t - W.rua2) / 1.6); const sweep = Math.sin((t - W.rua2) * 1.6) * (1 - smooth((t - W.alguem + 0.3) / 0.6));
  return [2000.4 + 2.2 * sweep * (1 - u) + 0.4 * u, 0.55 + 0.6 * u, 6.0 - 7.5 * u];
};
/** a maçaneta girando (radianos) */
export const knobAt = (t: number) => -0.55 * smooth((t - W.gira) / 1.4);

// ---------------- shots ----------------
export type Light = "day" | "golden" | "night";
export type Crowd = string;
export type ShotDef = { id: number; a: number; b: number; light: Light; crowd: Crowd };
const F = (t: number) => Math.round(t * FPS);
const CUT = [0, ...[W.poste, W.mao, W.rua2, W.chave].map((t) => F(t)), TOTAL];
const DEF: [Light, Crowd][] = [
  ["night", "p_walk"],    // 1 duas da manhã, você volta a pé (câmera rente ao asfalto, recuando)
  ["night", "p_pole"],    // 2 o poste pisca e apaga (a câmera sobe até a lâmpada)
  ["night", "p_hand"],    // 3 você liga a lanterna (close na mão)
  ["night", "p_pov"],     // 4 a lanterna varrendo a rua: alguém parado no fim
  ["night", "p_key"],     // 5 a aproximação até a mão dele com a sua chave
];
const BED: number[] = [];
const ROOM: number[] = [];

export const SHOTS: ShotDef[] = DEF.map(([light, crowd], i) => ({ id: i + 1, a: CUT[i], b: CUT[i + 1], light, crowd }));
export const XFADE: Record<number, number> = {};
export const FLASH_AT = -100;
const BATH: number[] = [];
export const inBath = (id: number) => BATH.includes(id);
/** quadro inicial de cada relâmpago */
export const FLASHES = BOLTS.map((t) => F(t)).filter((f) => { const s = SHOTS.find((x) => f >= x.a && f < x.b); return s && !inBath(s.id); });
export const shotAt = (f: number) => SHOTS.find((s) => f >= s.a && f < s.b) ?? SHOTS[SHOTS.length - 1];
export const layersAt = (f: number): { id: number; alpha: number }[] => [{ id: shotAt(f).id, alpha: 1 }];

export const PH_CAM: Record<number, [V3, V3, number]> = {};
export const PHONE_NEAR: Record<number, V3> = {};

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
/** câmera que ANDA (posição e mira interpoladas com suavidade entre chaves de tempo) */
const path = (keys: [number, V3, V3, number][]): Key[] => [{ f: 0, s: (f) => {
  const t = f / FPS; let i = 0; while (i + 1 < keys.length && t >= keys[i + 1][0]) i++;
  const A = keys[i], B = keys[Math.min(i + 1, keys.length - 1)]; const u = B === A ? 0 : glide((t - A[0]) / (B[0] - A[0]));
  const L = (p: V3, q: V3) => p.map((v, k) => v + (q[k] - v) * u) as V3;
  return { pos: L(A[1], B[1]), look: L(A[2], B[2]), fov: A[3] + (B[3] - A[3]) * u };
} }];
const walkCam = (): Key[] => [{ f: 0, s: (f) => { const t = f / FPS, z = youZ(t); return { pos: [2000.55, 0.28 + 0.05 * t, z - 3.3 + 0.25 * t], look: [2000.0, 1.0, z], fov: 58 }; } }];
const CAMS: Record<number, Key[]> = {
  1: walkCam(),
  2: path([[3.9, [2001.4, 1.5, 12.6], [2002.6, 2.2, 15.5], 54], [5.0, [2001.6, 1.6, 12.8], [2002.75, 5.1, 15.3], 40], [7.4, [2001.6, 1.6, 12.9], [2002.75, 5.05, 15.3], 38]]),
  3: path([[7.35, [2000.75, 1.35, 14.4], [2000.12, 1.25, 15.8], 38], [9.95, [2000.6, 1.3, 14.65], [2000.12, 1.2, 15.8], 34]]),
  4: path([[9.95, [2000.0, 1.62, 15.6], [2000.6, 0.6, 9.0], 60], [11.3, [2000.0, 1.62, 15.5], [2000.6, 0.9, 1.0], 54], [12.45, [2000.0, 1.62, 15.4], [2000.7, 1.1, -1.5], 50]]),
  5: path([[12.45, [2000.3, 1.5, 9.0], [2000.85, 1.2, -1.5], 44], [14.3, [2000.95, 1.1, 1.2], [2001.05, 0.95, -1.5], 38], [15.6, [2001.02, 0.9, -0.45], [2001.08, 0.8, -1.45], 36]]),
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
