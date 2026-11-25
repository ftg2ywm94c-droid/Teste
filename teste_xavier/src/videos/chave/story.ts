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
export const TOTAL = 1950;   // vídeo 21: 65,0 s (os 468 primeiros quadros são o piloto, iguais)
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
  // vídeo 21 (analysis/narracao/21_words.json)
  k_perdeu: 16.08, k_praca: 18.64, k_procurou: 19.9, k_banco: 20.98, k_grama: 21.96, k_meiofio: 22.86, k_homem: 26.2, k_olhando: 27.8,
  k_sol: 29.92, k_desistiu: 31.8, k_chaveiro: 33.48, k_fechadura: 34.82, k_entao: 36.22, k_seguro: 37.3, k_levanta: 40.6, k_aponta: 42.56,
  k_casa: 43.82, k_quarto: 46.7, k_acende: 47.2, k_sozinho: 50.44, k_decide: 51.68, k_se: 63.58,
  pisca: 4.94, apaga: 6.12, liga: 8.14, alguem: 11.2,
  relogio: -100, senta: -100, cel: -100, msg1: -100, foto: -100, msg2: -100, chuva: -100, bate: -100, corredor: -100,
  olho: -100, ela: -100, casaco: -100, janela: -100, celia: -100, marido: -100, rua: -100, macaneta: -100, vibra: -100,
  msg3: -100, porta2: -100, digitando: -100, decide: -100, opcaoA: -100, opcaoB: -100, comenta: -100, se: 999,
  acende: -100, knock1: -100, knock2: -100, knock3: -100, gira: -100,
  // nomes herdados (código antigo)
  tv1: -100, ancora: -100, rostos: -100, cortina: -100, tranca: -100, cade: -100, quintal: -100, portao: -100, ultimo: -100,
  esquina: -100, porta: -100, thor: -100, dois: -100, correr: -100, vira: -100, quieto: -100, abana: -100, mascaras: -100, trancado: -100, latirPara: -100,
  caiu: -100, jogador: -100, alguma: -100, param: -100,
  seis: -100, liga0: -100, n193: -100, chama: -100, duas: -100, atendem: -100, fala: -100, endereco: -100, arvore: -100, fio: -100,
  vizinha: -100, outro: -100, voz: -100, nao: -100, fica: -100, equipe: -100, ligacao: -100, celular: -100,
  la: -100, sirene: -100, e1: -100, para: -100, silencio: -100, batem: -100,
  forte: -100, e2: -100, abre: -100, filho: -100, eu: -100, entre: -100, e3: -100, fio2: -100, ainda: -100, faisca: -100,
  atravessa: -100, grita: -100,
  estrondo: -10, casa: -9, silencio0: -8, voceAbre: -100, aguentou: -100,
  apaga0: -1, estalo: 999, inclinando: 999, celular2: 999, direcao: 999, dobrar: 0, vento: -1,
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
  const k = Math.floor((t - W.pisca) * 30); return [1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0][k] ?? 0;
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
// vídeo 21: depois do piloto (5 planos), 9 planos com a câmera em caminho contínuo (sem corte aparente entre 6..13)
const CUT = [0, ...[W.poste, W.mao, W.rua2, W.chave, 15.6, 19.9, 24.0, 29.2, 36.1, 39.6, 45.8, 51.6, 63.6].map((t) => F(t)), TOTAL];
const DEF: [Light, Crowd][] = [
  ["night", "p_walk"],    // 1 duas da manhã, você volta a pé (câmera rente ao asfalto, recuando)
  ["night", "p_pole"],    // 2 o poste pisca e apaga (a câmera sobe até a lâmpada)
  ["night", "p_hand"],    // 3 você liga a lanterna (close na mão)
  ["night", "p_pov"],     // 4 a lanterna varrendo a rua: alguém parado no fim
  ["night", "p_key"],     // 5 a aproximação até a mão dele com a sua chave
  ["night", "c_rise"],    // 6 "Você perdeu essa chave hoje à tarde": a câmera sobe acima dos telhados, o céu volta para a tarde, desce na praça
  ["day", "c_search"],    // 7 "Procurou embaixo do banco, na grama, no meio-fio": a câmera segue você rente ao chão
  ["day", "c_man"],       // 8 "do outro lado da praça, tinha um homem parado": atravessa a praça até ele; por cima do ombro dele, você procurando
  ["day", "c_sunset"],    // 9 "O sol foi embora... trocou a fechadura": sobe a rua até a sua casa enquanto o sol se põe; o chaveiro na porta
  ["night", "c_back"],    // 10 "Então você está seguro... né?": da porta, desce a rua de volta até as duas da manhã
  ["night", "c_point"],   // 11 "ele levanta a chave. E aponta pra sua casa": de lado, o braço aponta; a câmera segue o braço até a casa
  ["night", "c_window"],  // 12 "A luz do seu quarto acende. Você mora sozinho."
  ["night", "c_choice"],  // 13 A ou B (cartões no mograph)
  ["night", "c_loop"],    // 14 "E se...": o começo do plano 1, emendando no quadro 0
];
/** hora do dia contínua (0 = dia, 1 = pôr do sol, 2 = noite), misturada quadro a quadro em world.ts */
export const todAt = (id: number, t: number) => {
  if (id === 6) return 2 - 2 * smooth((t - 16.3) / 2.2);
  if (id === 7 || id === 8) return 0;
  if (id === 9) return t < 32.2 ? smooth((t - 29.6) / 2.6) : 1 + smooth((t - 32.2) / 2.4);
  return 2;
};
/** a praça (z de -13,5 a -44): banco, grama, meio-fio, a árvore do homem */
export const PRACA = { bench: [1996.2, -20.0] as const, grass: [1998.6, -23.5] as const, curb: [2001.8, -14.2] as const, man: [2006.4, -34.2] as const, tree: [2008.9, -36.6] as const };
/** sua casa no fim da rua (fachada em z 44, de frente para -z): porta e a janela do quarto (andar de cima) */
export const CASA = { door: [2000.0, 44.0] as const, win: [2001.6, 4.3, 43.9] as const };
/** você na praça: onde está e se está agachado procurando */
export const youPraca = (t: number): { x: number; z: number; crouch: boolean; walk: boolean; phase: number } => {
  const B = PRACA.bench, G = PRACA.grass, C = PRACA.curb;
  const seg = (a: readonly number[], b: readonly number[], t0: number, t1: number) => { const u = smooth((t - t0) / (t1 - t0)); return { x: a[0] + (b[0] - a[0]) * u, z: a[1] + (b[1] - a[1]) * u }; };
  if (t < 18.9) { const p = seg([1999.0, -15.5], [B[0] + 1.0, B[1]], 17.6, 18.9); return { ...p, crouch: false, walk: t > 17.6, phase: t * 0.9 }; }
  if (t < 21.3) return { x: B[0] + 1.0, z: B[1], crouch: t > 19.6, walk: false, phase: 0 };
  if (t < 21.8) return { ...seg([B[0] + 1.0, B[1]], G, 21.3, 21.8), crouch: false, walk: true, phase: t * 0.9 };
  if (t < 22.6) return { x: G[0], z: G[1], crouch: true, walk: false, phase: 0 };
  if (t < 23.2) return { ...seg(G, C, 22.6, 23.2), crouch: false, walk: true, phase: t * 0.9 };
  return { x: C[0], z: C[1], crouch: t < 29.6, walk: false, phase: 0 };
};
/** o homem levantando a chave (0..1) e apontando (o 4º valor do prop "keys") */
export const raiseAt = (t: number) => (t < W.k_levanta ? 0 : 0.7 * smooth((t - W.k_levanta) / 0.6) + 0.3 * smooth((t - W.k_aponta) / 0.45));
/** a janela do quarto acende */
export const winOn = (t: number) => t >= W.k_acende;
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
/** vídeo 21: câmera que ATRAVESSA o cenário — spline Catmull-Rom por chaves de tempo (velocidade contínua nas chaves,
 *  sem o "para e anda" do path); a mesma lista vale para vários planos seguidos, então o corte entre eles não aparece */
const spline = (keys: [number, V3, V3, number][]): Key[] => [{ f: 0, s: (f) => {
  const t = f / FPS; let i = 0; while (i + 2 < keys.length && t >= keys[i + 1][0]) i++;
  const k1 = keys[i], k2 = keys[i + 1], k0 = keys[Math.max(0, i - 1)], k3 = keys[Math.min(keys.length - 1, i + 2)];
  let u = clamp01((t - k1[0]) / (k2[0] - k1[0]));
  if (i === 0) u = u * u * (2 - u);                                  // sai do repouso (o último quadro do plano 5 está parado)
  if (i + 2 >= keys.length) u = u * (1 + u - u * u);                 // chega no repouso
  const cr = (a: number, b: number, c: number, d: number) => 0.5 * (2 * b + (-a + c) * u + (2 * a - 5 * b + 4 * c - d) * u * u + (-a + 3 * b - 3 * c + d) * u * u * u);
  const P = (j: 1 | 2) => [0, 1, 2].map((k) => cr(k0[j][k], k1[j][k], k2[j][k], k3[j][k])) as V3;
  return { pos: P(1), look: P(2), fov: cr(k0[3], k1[3], k2[3], k3[3]) };
} }];
const TRAVEL: [number, V3, V3, number][] = [
  [15.6, [2001.02, 0.9, -0.45], [2001.08, 0.8, -1.45], 36],
  [16.6, [2001.0, 3.0, 1.0], [2000.9, 2.4, -2.0], 44],          // recua e sobe do close da chave
  [17.7, [2000.4, 14.0, 5.0], [2000.0, 9.0, -22.0], 55],        // acima dos telhados: o céu volta para a tarde
  [18.8, [2000.0, 10.0, -9.0], [1998.0, 1.5, -22.0], 52],       // desce para a praça
  [19.8, [1999.4, 3.0, -14.8], [1997.2, 0.7, -20.0], 44],
  [20.9, [1998.8, 1.0, -16.9], [1997.1, 0.5, -20.3], 42],       // rente ao chão: você embaixo do banco
  [21.9, [1999.9, 0.6, -19.6], [1998.6, 0.3, -23.5], 44],       // na grama
  [22.9, [2000.6, 0.65, -17.4], [2001.8, 0.3, -14.2], 46],      // vira para o meio-fio
  [23.9, [2003.4, 1.1, -17.4], [2002.0, 0.5, -14.2], 46],
  [24.8, [2004.4, 1.6, -22.0], [2005.8, 1.4, -30.0], 46],       // atravessa a praça
  [25.9, [2005.1, 1.6, -27.8], [2006.4, 1.5, -34.2], 42],
  [26.7, [2005.6, 1.6, -30.4], [2006.4, 1.6, -34.2], 36],       // "homem": ele, parado na sombra da árvore
  [27.8, [2007.6, 1.75, -37.6], [2003.0, 0.8, -16.0], 40],       // por cima do ombro dele
  [29.1, [2007.5, 1.7, -37.3], [2002.3, 0.6, -14.4], 33],       // "olhando você procurar"
  [30.2, [2004.0, 4.2, -25.0], [2001.0, 3.2, -4.0], 50],        // "o sol foi embora": sobe e vira para a rua
  [31.8, [2001.0, 5.5, -4.0], [2000.0, 3.0, 26.0], 52],         // sobe a rua; o sol se pondo no fim dela
  [33.2, [2000.6, 3.0, 23.5], [2000.0, 1.6, 44.0], 46],
  [34.6, [2000.8, 1.7, 36.6], [2000.0, 1.3, 44.0], 42],         // a porta: o chaveiro trocando a fechadura
  [36.0, [2001.0, 1.7, 38.0], [2000.0, 1.3, 44.0], 38],
  [37.0, [2001.6, 2.2, 37.0], [2000.0, 1.4, 20.0], 50],         // de volta, rua abaixo, duas da manhã
  [38.5, [2001.2, 1.9, 22.5], [2000.6, 1.2, 5.0], 46],
  [39.6, [2000.9, 1.75, 19.3], [2000.7, 1.1, -1.5], 40],        // atrás de você: ele na luz da lanterna
  [40.5, [1999.3, 1.6, 8.0], [2000.85, 1.3, -1.5], 40],         // vai para o lado dele
  [41.6, [1997.4, 1.5, -0.6], [2000.85, 1.3, -1.5], 36],        // de lado: "levanta a chave"
  [42.7, [1997.4, 1.5, -0.6], [2001.0, 1.55, -0.3], 34],        // o braço aponta para a tela à direita = +z = sua casa
  [43.7, [1998.0, 1.9, 1.6], [2000.5, 3.0, 30.0], 44],          // segue o braço rua acima
  [45.1, [1999.4, 2.2, 10.0], [2000.0, 3.6, 44.0], 36],
  [46.6, [1999.7, 2.4, 18.0], [2000.6, 4.1, 44.0], 30],         // a janela do quarto
  [51.4, [1999.8, 2.5, 24.0], [2000.9, 4.2, 44.0], 26],
  [53.0, [2003.8, 5.0, 25.0], [2000.4, 0.9, 7.0], 52],          // escolha: você e ele, de cima
  [63.5, [2003.2, 4.4, 22.5], [2000.4, 0.9, 7.0], 46],
];
const loopCam = (): Key[] => [{ f: 0, s: (f) => { const t = f / FPS - TOTAL / FPS, z = youZ(t); return { pos: [2000.55, 0.28 + 0.05 * t, z - 3.3 + 0.25 * t], look: [2000.0, 1.0, z], fov: 58 }; } }];
const CAMS: Record<number, Key[]> = {
  6: spline(TRAVEL), 7: spline(TRAVEL), 8: spline(TRAVEL), 9: spline(TRAVEL), 10: spline(TRAVEL), 11: spline(TRAVEL), 12: spline(TRAVEL), 13: spline(TRAVEL),
  14: loopCam(),
  1: walkCam(),
  2: path([[3.9, [2001.4, 1.5, 12.6], [2002.6, 2.2, 15.5], 54], [5.0, [2001.6, 1.6, 12.8], [2002.75, 5.1, 15.3], 40], [7.4, [2001.7, 1.55, 13.25], [2002.75, 5.0, 15.3], 33]]),   // aproximação lenta até o corte: no escuro depois do "apaga" a imagem não fica parada
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
export const DOF: Dof[] = SHOTS.map((s) => (s.id >= 6 ? { f: s.a, cInf: 4, focus: (f: number) => camAt(s.id, f).look } : { f: s.a, cInf: FOC[s.id][0], focus: () => FOC[s.id][1] }));   // vídeo 21: o foco anda junto com a mira da câmera
export const dofAt = (f: number) => {
  let i = 0; while (i + 1 < DOF.length && f >= DOF[i + 1].f) i++;
  const d = DOF[i], p = DOF[Math.max(0, i - 1)];
  const k = d.dur ? Math.min(1, (f - d.f) / d.dur) : 1;
  return { cInf: p.cInf + (d.cInf - p.cInf) * k, focus: d.focus };
};
export type Fg = { a: number; b: number; kit: string; pos: V3; s?: number; yaw?: number };
export const FOREGROUND: Fg[] = [];
