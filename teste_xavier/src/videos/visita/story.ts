// "A torre que uma guerra salvou": our 15 s short in the flat-characters-in-a-3D-toon-world style.
// Timeline: 4 shots timed to the narration (estimates until the voice arrives; retime LINES then).
//   S1 hook, today: leaning tower, tourists posing  | "A torre mais famosa da Itália só tá de pé porque uma guerra parou a obra."
//   S2 1178: two floors, the tower sinks, masons shocked | "No segundo andar, ela começou a afundar."
//   S3 war: soldiers march past the stump, then dusk     | "A guerra parou tudo por cem anos, o barro firmou…"
//   S5 1272: the rest goes up, bent back (the curve)     | "Quando voltaram, fizeram o resto torto pro outro lado, pra disfarçar…"
//   S6 today: the finished tower stands, tourists cheer  | "…e ela não caiu."
export const FPS = 30;
// Vídeo 20 "A Visita · Ep. 1": 3h da manhã, mensagem do número da avó que morreu, a avó na porta, os mortos voltando na rua.
// Tempos REAIS: faixa narracao/20_narracao.mp3 (76,01 s; narrador Spuds Oxley + avó Edna, ElevenLabs eleven_v3).
// Palavras em projeto_videos3d/analysis/narracao/20_words.json; falas em narracao/20_vozes/20_linhas.json.
import { TALK } from "./talk";
export const TOTAL = 2280;
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
  inicio: 0, relogio: 1.9, senta: 4.4, cel: 7.4, msg1: 9.8, foto: 13.5, msg2: 15.2, chuva: 16.8, bate: 18.8, corredor: 22.3,
  olho: 25.6, ela: 28.9, casaco: 30.8, janela: 33.3, celia: 35.1, marido: 41.5, rua: 44.4, macaneta: 49.8, vibra: 52.8,
  msg3: 54.9, porta2: 56.2, digitando: 59.6, decide: 61.7, opcaoA: 63.3, opcaoB: 65.9, comenta: 69.0, se: 74.5,
  acende: 8.1, knock1: 19.25, knock2: 19.65, knock3: 20.05, gira: 50.6,
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
export const SET = { street: [0, 0] as const, room: [600, 0] as const, bed: [1000, 0] as const, farm: [-200, -300] as const };

/** vento fraco da chuva (as árvores da rua balançam de leve) */
export const windAt = (id: number, t: number) => (OUT.includes(id) && t >= W.chuva ? 0.35 : 0);
export const leanAt = (_id: number, _t: number) => 0;
export const fallen = (_t: number) => false;
export const FLICKER: [number, number][] = [];
export const flickOff = (_t: number) => false;
/** 3h da manhã: as luzes da casa estão apagadas */
export const lampOn = (_id: number, _t: number) => false;
/** relâmpagos (s): o primeiro em "chover", os outros nos picos de medo */
export const BOLTS: number[] = [17.6, 29.0, 41.6, 47.2, 56.4, 74.2];
export const sparkAt = (_t: number) => false;
export const doorAt = (_id: number, _t: number) => 0;
export const sirenX = (_t: number) => -95;
export const sirenK = (_t: number) => 0;
export const sirenPulse = (_t: number) => 0;
/** casa no escuro (só a luz da rua e a do celular) */
export const darkAt = (id: number, _t: number) => (BED.includes(id) ? 0.5 : ROOM.includes(id) ? 0.45 : 0);
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
/** a maçaneta girando (radianos) */
export const knobAt = (t: number) => -0.55 * smooth((t - W.gira) / 1.4);

// ---------------- shots ----------------
export type Light = "day" | "golden" | "night";
export type Crowd = string;
export type ShotDef = { id: number; a: number; b: number; light: Light; crowd: Crowd };
const F = (t: number) => Math.round(t * FPS);
const CUT = [0, ...[W.relogio, W.senta, W.cel, W.msg1, W.foto, W.msg2, W.chuva, W.bate, W.corredor, W.olho, W.ela, W.casaco, W.janela,
  W.celia, W.marido, W.rua, W.macaneta, W.vibra, W.msg3, W.porta2, W.digitando, W.decide, W.opcaoA, W.opcaoB, W.comenta, W.se].map((t) => F(t)), TOTAL];
const DEF: [Light, Crowd][] = [
  ["night", "z_bed"],      // 1 três da manhã: o quarto, você sentado na cama, o despertador piscando
  ["night", "z_clock"],    // 2 seu despertador toca sozinho (close no relógio)
  ["night", "z_wake"],     // 3 você nunca colocou alarme pra essa hora (você assustado)
  ["night", "z_phone"],    // 4 aí o celular acende (no criado-mudo)
  ["night", "z_hold"],     // 5 mensagem do número da sua avó (tela do celular na camada de títulos)
  ["night", "z_photo"],    // 6 ela morreu faz dois anos (o porta-retrato)
  ["night", "z_hold"],     // 7 2ª mensagem: ela não entra sem ser convidada
  ["night", "z_rain"],     // 8 começa a chover (a casa de fora, relâmpago)
  ["night", "z_knock"],    // 9 alguém bate na porta, três vezes
  ["night", "z_hall"],     // 10 avó: abre, meu anjo, tá frio aqui fora (você olhando a porta)
  ["night", "z_peek"],     // 11 você olha pelo olho mágico
  ["night", "z_avo"],      // 12 é ela (visão do olho mágico)
  ["night", "z_avo2"],     // 13 com o mesmo casaco do enterro (mais perto)
  ["night", "z_window"],   // 14 você corre pra janela
  ["night", "z_celia"],    // 15 do outro lado da rua, a dona Célia abraçando o marido
  ["night", "z_husb"],     // 16 ele morreu faz oito anos (close nele)
  ["night", "z_street"],   // 17 cada casa da rua tem uma visita
  ["night", "z_knob"],     // 18 avó: você não vai deixar a vó entrar? (a maçaneta gira)
  ["night", "z_vib"],      // 19 o celular vibra de novo
  ["night", "z_hold2"],    // 20 3ª mensagem: essa aí na porta não sou eu
  ["night", "z_gap"],      // 21 mas se ela tá na porta... (a sombra dos pés na fresta)
  ["night", "z_hold2"],    // 22 quem tá mandando mensagem? (digitando...)
  ["night", "z_you"],      // 23 você decide
  ["night", "z_optA"],     // 24 A: abre a porta
  ["night", "z_optB"],     // 25 B: responde a mensagem
  ["night", "z_choice"],   // 26 comenta A ou B
  ["night", "z_loop"],     // 27 E se... (= quadro 0)
];
const BED = [1, 2, 3, 4, 5, 6, 7, 27];
const ROOM = [9, 10, 11, 14, 18, 19, 20, 21, 22, 23, 24, 25, 26];
const OUT = [8, 12, 13, 15, 16, 17];
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
const CAMS: Record<number, Key[]> = {
  // quarto (1000,0): cama encostada na parede do fundo (z 4), criado-mudo à direita, janela à esquerda
  1: dl(1, [999.35, 1.5, -0.9], [999.25, 0.85, 3.0], 60, 0.0012),
  2: dl(2, [1000.4, 0.78, 2.7], [1000.4, 0.68, 3.62], 36, 0.003),
  3: dl(3, [998.9, 1.15, 0.9], [998.75, 1.0, 3.0], 44, 0.0026),
  4: dl(4, [1000.0, 0.95, 2.75], [1000.3, 0.6, 3.6], 46, 0.0026),
  5: dl(5, [999.6, 1.3, 1.2], [998.9, 0.95, 3.2], 50, 0.0016),
  6: dl(6, [1000.08, 0.82, 3.05], [1000.1, 0.72, 3.85], 34, 0.0028),
  7: dl(7, [999.6, 1.3, 1.2], [998.9, 0.95, 3.2], 50, 0.0016),
  // a casa de fora na chuva (rua 0,0: a sua casa é a do meio, atrás do muro)
  8: dl(8, [1.2, 1.6, -7.0], [0.2, 3.2, 14.0], 58, 0.0016),
  // sala (600,0): a porta da frente é a da parede do fundo (x 594,1; z 3,9)
  9: dl(9, [594.6, 1.25, 0.6], [594.1, 1.1, 3.9], 50, 0.0028),
  10: dl(10, [596.6, 1.4, -0.4], [594.6, 1.2, 3.6], 48, 0.0022),
  11: dl(11, [596.5, 1.45, 2.1], [594.3, 1.35, 3.6], 50, 0.0024),
  // visão do olho mágico: de dentro da porta para a varanda (lente bem aberta; o anel preto vem na camada de títulos)
  12: dl(12, [594.1, 1.55, 4.5], [594.1, 1.25, 6.5], 96, 0.0014),
  13: dl(13, [594.1, 1.55, 4.5], [594.1, 1.38, 6.5], 70, 0.0024),
  14: dl(14, [601.9, 1.45, 1.3], [603.2, 1.4, 3.7], 52),
  // do seu portão para a casa da frente (fileira z -25): a dona Célia e o marido no portão dela
  15: dl(15, [0.6, 1.75, 6.0], [0.4, 1.1, -19.0], 20, 0.0018),
  16: dl(16, [0.6, 1.75, 6.0], [0.62, 1.5, -19.0], 12, 0.0024),
  17: dl(17, [0.6, 2.6, 6.0], [3.5, 0.9, -19.0], 40, 0.0016),
  18: dl(18, [594.2, 1.15, 3.0], [593.75, 1.02, 3.88], 44, 0.0028),
  19: dl(19, [597.0, 1.4, 0.55], [597.0, 1.3, 2.0], 44, 0.003),
  20: dl(20, [597.0, 1.4, 0.55], [597.0, 1.3, 2.0], 44, 0.0016),
  21: dl(21, [594.3, 0.35, 1.9], [594.1, 0.1, 3.9], 44, 0.0026),
  22: dl(22, [597.0, 1.4, 0.55], [597.0, 1.3, 2.0], 44, 0.0016),
  23: dl(23, [597.0, 1.4, 0.55], [597.0, 1.3, 2.0], 40, 0.003),
  24: dl(24, [595.2, 1.4, 1.2], [594.3, 1.2, 3.6], 50),
  25: dl(25, [597.0, 1.4, 0.55], [597.0, 1.3, 2.0], 46, 0.0022),
  26: dl(26, [596.4, 1.6, -1.2], [595.4, 1.1, 3.4], 54, 0.0016),
  // loop: o mesmo zoom do plano 1, chegando na lente do quadro 0 no quadro seguinte ao último
  27: [{ f: 0, s: (f) => ({ pos: [999.35, 1.5, -0.9], look: [999.25, 0.85, 3.0], fov: (360 / Math.PI) * Math.atan(Math.tan((60 * Math.PI) / 360) * Math.exp(-0.0012 * (f - TOTAL))) }) }],
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
