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
export const TOTAL = 1950;   // vídeo 122 (The Key Ep. 2, inglês): 65,0 s
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
  // vídeo 122 (analysis/narracao/122_words.json)
  e_rip: 0.3, e_key: 0.76, e_grabs: 2.62, e_hard: 4.3, e_twist: 5.7, e_run: 7.38, e_behind: 8.82, e_fast: 10.8, e_shaking: 14.06,
  e_wont: 15.56, e_wrong: 17.5, e_flip: 19.18, e_click: 20.38, e_inside: 22.0, e_slam: 23.16, e_bang: 24.68, e_hits: 26.12, e_once: 27.56,
  e_twice: 28.82, e_then: 30.32, e_silence: 32.18, e_phone: 33.96, e_unknown: 35.92, e_nice: 37.94, e_keys: 40.5, e_upstairs: 42.66,
  e_off: 44.78, e_someone: 46.62, e_already: 47.84, e_decide: 49.4, e_A: 50.4, e_B: 54.22, e_comment: 57.3, e_most: 60.6, e_whatif: 64.02,
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
// vídeo 122: 14 planos guiados pela fala (rua -> porta -> dentro de casa); o 14 repete o quadro 0 (loop)
const CUT = [0, ...[2.3, 5.4, 8.6, 13.0, 17.3, 18.9, 21.6, 24.5, 30.2, 33.6, 42.2, 49.3, 63.9].map((t) => F(t)), TOTAL];
const DEF: [Light, Crowd][] = [
  ["night", "g_grab"],    // 1 "You rip the key out of his hand": de lado, frente a frente sob o poste; a chave pula da mão dele para a sua
  ["night", "g_wrist"],   // 2 "He grabs your wrist. Hard.": ele estica os braços e agarra; tranco na câmera
  ["night", "g_twist"],   // 3 "You twist free… and run.": você se solta e sai correndo para a direita (rua acima, para casa)
  ["night", "g_run"],     // 4 "Behind you, footsteps. Fast. He's chasing you.": a câmera corre na sua frente; ele atrás
  ["night", "g_lock"],    // 5 "Your hands are shaking. The key won't go in.": close da fechadura dourada, a chave tremendo e raspando
  ["night", "g_behind"],  // 6 "Wrong way.": da porta, rua abaixo: ele vindo correndo
  ["night", "g_click"],   // 7 "You flip it. Click.": a chave vira e entra
  ["night", "i_slam"],    // 8 "You get inside and slam the door.": por dentro, a porta abre, você entra, a porta bate
  ["night", "i_bang"],    // 9 "BANG. He hits the door. Once. Twice.": você encostado na porta, que treme a cada batida
  ["night", "i_silence"], // 10 "Then… silence.": a câmera chega devagar no seu rosto
  ["night", "i_phone"],   // 11 "Your phone buzzes... 'Nice try. I made two keys.'": o celular acende o seu rosto
  ["night", "i_stairs"],  // 12 "Upstairs, your bedroom light turns off. Someone is already inside.": a escada; a luz embaixo da porta apaga
  ["night", "i_choice"],  // 13 A ou B (cartões no mograph)
  ["night", "g_loop"],    // 14 "What if...": o quadro 0 parado (emenda)
];
/** hora do dia contínua (0 = dia, 1 = pôr do sol, 2 = noite), misturada quadro a quadro em world.ts */
export const todAt = (_id: number, _t: number) => 2;   // vídeo 122: sempre noite
export const todAt21 = (id: number, t: number) => {
  if (id === 6) return 2 - 2 * smooth((t - 16.3) / 2.2);
  if (id === 7 || id === 8) return 0;
  if (id === 9) return t < 32.2 ? smooth((t - 29.6) / 2.6) : 1 + smooth((t - 32.2) / 2.4);
  return 2;
};
/** a praça (z de -13,5 a -44): banco, grama, meio-fio, a árvore do homem */
export const PRACA = { bench: [1996.2, -17.2] as const, grass: [1997.5, -15.6] as const, curb: [1997.6, -14.25] as const, man: [2006.4, -34.2] as const, tree: [2008.9, -36.6] as const };
/** sua casa no fim da rua (fachada em z 44, de frente para -z): porta e a janela do quarto (andar de cima) */
export const CASA = { door: [2000.0, 44.0] as const, win: [2001.6, 4.3, 43.9] as const };
/** você na praça: onde está e se está agachado procurando */
export const youPraca = (t: number): { x: number; z: number; crouch: boolean; walk: boolean; phase: number } => {
  const B = PRACA.bench, G = PRACA.grass, C = PRACA.curb;
  const seg = (a: readonly number[], b: readonly number[], t0: number, t1: number) => { const u = smooth((t - t0) / (t1 - t0)); return { x: a[0] + (b[0] - a[0]) * u, z: a[1] + (b[1] - a[1]) * u }; };
  if (t < 18.9) { const p = seg([1999.4, -16.6], [B[0] + 1.0, B[1]], 17.6, 18.9); return { ...p, crouch: false, walk: t > 17.6, phase: t * 0.9 }; }
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
const spline = (keys: [number, V3, V3, number][]): Key[] => {
  // a MIRA é interpolada como ângulo (rumo, inclinação) + distância, não como ponto: com o ponto andando em linha, numa virada
  // de 180° ele passava rente à câmera e o giro inteiro caía em 3–4 quadros (chicote); por ângulo o giro se espalha por igual
  const A = keys.map((k) => { const d = [k[2][0] - k[1][0], k[2][1] - k[1][1], k[2][2] - k[1][2]], h = Math.hypot(d[0], d[2]);
    return [Math.atan2(d[0], d[2]), Math.atan2(d[1], h), Math.hypot(h, d[1])]; });
  for (let i = 1; i < A.length; i++) { while (A[i][0] - A[i - 1][0] > Math.PI) A[i][0] -= 2 * Math.PI; while (A[i][0] - A[i - 1][0] < -Math.PI) A[i][0] += 2 * Math.PI; }
  return [{ f: 0, s: (f) => {
    const t = f / FPS; let i = 0; while (i + 2 < keys.length && t >= keys[i + 1][0]) i++;
    const j0 = Math.max(0, i - 1), j3 = Math.min(keys.length - 1, i + 2);
    const k1 = keys[i], k2 = keys[i + 1], k0 = keys[j0], k3 = keys[j3];
    let u = clamp01((t - k1[0]) / (k2[0] - k1[0]));
    if (i === 0) u = u * u * (2 - u);                                  // sai do repouso (o último quadro do plano 5 está parado)
    if (i + 2 >= keys.length) u = u * (1 + u - u * u);                 // chega no repouso
    // v3: tangentes pelo TEMPO de cada trecho (Catmull-Rom não uniforme): com trechos de durações muito diferentes, a versão uniforme
    // passava do ponto (um giro rápido antes de um trecho longo empurrava a mira para fora de você)
    const T0 = k0[0], T1 = k1[0], T2 = k2[0], T3 = k3[0], D = T2 - T1;
    const h00 = 2 * u * u * u - 3 * u * u + 1, h10 = u * u * u - 2 * u * u + u, h01 = -2 * u * u * u + 3 * u * u, h11 = u * u * u - u * u;
    const cr = (a: number, b: number, c: number, d: number) => {
      const m1 = j0 === i ? c - b : ((c - a) / (T2 - T0)) * D, m2 = j3 === i + 1 ? c - b : ((d - b) / (T3 - T1)) * D;
      return h00 * b + h10 * m1 + h01 * c + h11 * m2; };
    const pos = [0, 1, 2].map((k) => cr(k0[1][k], k1[1][k], k2[1][k], k3[1][k])) as V3;
    const [yaw, pit, dist] = [0, 1, 2].map((k) => cr(A[j0][k], A[i][k], A[i + 1][k], A[j3][k]));
    const look: V3 = [pos[0] + dist * Math.cos(pit) * Math.sin(yaw), pos[1] + dist * Math.sin(pit), pos[2] + dist * Math.cos(pit) * Math.cos(yaw)];
    return { pos, look, fov: cr(k0[3], k1[3], k2[3], k3[3]) };
  } }];
};
const TRAVEL: [number, V3, V3, number][] = [
  [15.6, [2001.02, 0.9, -0.45], [2001.08, 0.8, -1.45], 36],
  [16.6, [2001.0, 3.0, 1.0], [2000.9, 2.4, -2.0], 44],          // recua e sobe do close da chave
  [17.7, [2000.4, 14.0, 5.0], [2000.0, 9.0, -22.0], 55],        // acima dos telhados: o céu volta para a tarde
  [18.8, [2000.0, 9.0, -8.5], [1998.0, 1.2, -18.5], 52],        // desce para a praça
  [19.8, [1999.8, 2.4, -12.4], [1997.3, 0.8, -17.2], 46],
  [20.9, [1999.3, 0.9, -14.3], [1997.2, 0.45, -17.2], 42],      // rente ao chão: você embaixo do banco
  [21.9, [1999.6, 0.8, -13.4], [1997.5, 0.35, -15.6], 44],      // na grama
  [22.9, [1999.9, 0.75, -12.9], [1997.6, 0.35, -14.25], 46],    // no meio-fio (banco, grama e meio-fio a 1,5 m um do outro)
  [23.9, [2001.6, 1.2, -13.4], [1997.9, 0.6, -14.4], 46],       // recua sem tirar o olho de você
  [25.3, [2002.6, 1.6, -17.5], [2005.6, 1.4, -30.0], 46],       // vira: "do outro lado da praça"
  [26.2, [2004.9, 1.6, -30.2], [2006.4, 1.5, -34.2], 40],       // "homem": ele, parado na sombra da árvore
  [26.9, [2005.3, 1.6, -31.7], [2006.4, 1.55, -34.2], 36],
  [27.5, [2004.0, 1.65, -33.9], [2006.4, 1.55, -34.2], 36],     // a câmera dá a volta nele (raio 2,4 m, pelo lado longe da árvore)
  [28.1, [2005.0, 1.7, -36.1], [2006.4, 1.55, -34.2], 38],
  [28.7, [2007.37, 1.75, -36.4], [2002.0, 0.7, -22.0], 38],     // por cima do ombro dele: "olhando você procurar"
  [29.3, [2007.5, 1.75, -36.9], [2002.3, 0.6, -24.0], 33],
  [29.9, [2008.3, 2.8, -32.4], [2003.5, 2.2, -12.0], 44],      // sai pelo lado dele (sem atravessar o corpo) e sobe
  [30.6, [2005.4, 4.6, -24.0], [2001.0, 3.2, -4.0], 50],        // "o sol foi embora": vira para a rua
  [31.8, [2001.0, 7.0, 0.0], [2000.0, 3.5, 28.0], 52],         // sobe a rua; o sol se pondo no fim dela
  [33.2, [2000.6, 3.0, 23.5], [2000.0, 1.6, 44.0], 46],
  [34.6, [2000.8, 1.7, 36.6], [2000.0, 1.3, 44.0], 42],         // a porta: o chaveiro trocando a fechadura
  [35.1, [2001.0, 1.7, 37.8], [2000.0, 1.3, 44.0], 39],
  [36.4, [2001.6, 12.5, 35.0], [2008.5, 8.5, 35.0], 56],         // grua: sobe acima da rua e gira olhando para baixo...
  [37.9, [2001.8, 4.5, 30.0], [2000.6, 1.4, 15.0], 48],         // ...e desce a rua de volta, duas da manhã
  [38.8, [2001.2, 1.9, 22.5], [2000.6, 1.2, 5.0], 46],
  [39.6, [2000.9, 1.75, 19.3], [2000.7, 1.1, -1.5], 40],        // atrás de você: ele na luz da lanterna
  [40.5, [1999.3, 1.6, 8.0], [2000.85, 1.3, -1.5], 40],         // vai para o lado dele
  [41.6, [1997.4, 1.5, -0.6], [2000.85, 1.3, -1.5], 36],        // de lado: "levanta a chave"
  [42.7, [1997.4, 1.5, -0.6], [2001.0, 1.55, -0.3], 34],        // o braço aponta para a tela à direita = +z = sua casa
  [43.7, [1998.0, 1.9, 1.6], [2000.5, 3.0, 30.0], 44],          // segue o braço rua acima
  [45.1, [1999.4, 2.2, 10.0], [2000.0, 3.6, 44.0], 36],
  [46.6, [1999.7, 2.4, 18.0], [2000.6, 4.1, 44.0], 30],         // a janela do quarto
  [50.8, [1999.8, 2.5, 23.6], [2000.9, 4.2, 44.0], 26],
  [52.2, [2002.0, 12.5, 24.5], [2008.9, 8.5, 24.5], 56],         // grua: sobe e gira olhando para baixo...
  [53.6, [2003.8, 5.0, 25.0], [2000.4, 0.9, 7.0], 52],          // ...escolha: você e ele, de cima
  [63.5, [2003.2, 4.4, 22.5], [2000.4, 0.9, 7.0], 46],
];
const loopCam = (): Key[] => [{ f: 0, s: (f) => { const t = f / FPS - TOTAL / FPS, z = youZ(t); return { pos: [2000.55, 0.28 + 0.05 * t, z - 3.3 + 0.25 * t], look: [2000.0, 1.0, z], fov: 58 }; } }];
// ---------------- vídeo 122: rua (você e ele sob o poste), corrida até a porta, dentro de casa (hall em x 3000) ----------------
/** v3: o hall (montado em x 3000) fica DENTRO da sua casa: (3000, z) do hall = (2000, z + 44,01) da rua; a porta do hall é a da rua */
export const HALL: [number, number] = [-1000, 44.01];
/** v3: você do quadro 0 à escolha, num só caminho (a câmera não corta mais): frente a frente com ele (z 15,1), tranco, corrida até a
 *  porta (z 42,6), entra quando a porta abre, recua e fica encostado na porta (z 44,43). face = para onde está virado (z) */
export const youSt = (t: number) => {
  if (t < W.e_twist) return { x: 2000.5, z: 15.1, run: false, walk: false, face: -1 };
  if (t < 6.8) return { x: 2000.5, z: 15.1 + 0.35 * smooth((t - W.e_twist) / 0.5), run: false, walk: false, face: 1 };
  if (t < 22.1) return { x: 2000.5 - 0.2 * smooth((t - 6.8) / 7), z: Math.min(42.6, 15.45 + 3.9 * (t - 6.8)), run: t < 13.75, walk: false, face: 1 };
  if (t < 22.9) { const k = smooth((t - 22.1) / 0.45); return { x: 2000.3 - 0.25 * k, z: 42.6 + 2.4 * k, run: false, walk: k < 1, face: 1 }; }
  if (t < 41.2) return { x: 2000.05, z: 45.0 - 0.57 * smooth((t - 22.9) / 0.4), run: false, walk: false, face: 1 };
  const k = smooth((t - 41.2) / 1.1);   // "Upstairs": sai da porta e vai até o pé da escada
  return { x: 2000.05 + 0.2 * k, z: 44.43 + 1.47 * k, run: false, walk: k > 0 && k < 1, face: 1 };
};
/** ele: parado em z 14,1; corre atrás de você; chega na porta quando ela bate (z 43,3, do lado de fora) e some depois */
export const manSt = (t: number) => {
  const k = (a: number, b: number, za: number, zb: number) => za + (zb - za) * clamp01((t - a) / (b - a));
  const x = 2000.5 - 0.1 * smooth((t - 7.6) / 1.4);
  if (t < 7.6) return { x, z: 14.1, run: false, gone: false };
  if (t < 13.0) return { x, z: k(7.6, 13.0, 14.1, 27.5), run: true, gone: false };
  if (t < 18.9) return { x, z: k(13.0, 18.9, 27.5, 35.0), run: true, gone: false };
  const z = Math.min(43.3, k(18.9, 22.8, 35.0, 43.0) + Math.max(0, t - 22.8) * 1.5);
  return { x, z, run: z < 43.3, gone: t > 23.6 };
};
/** a chave: 0 na mão dele, 1 na sua (o arranco em "key") */
export const keySwap = (t: number) => smooth((t - (W.e_key - 0.05)) / 0.18);
/** os braços dele esticando para agarrar o seu pulso (0..1) e soltando quando você se solta */
export const grabAt = (t: number) => smooth((t - W.e_grabs + 0.1) / 0.35) * (1 - smooth((t - W.e_twist) / 0.3));
/** a porta da frente por dentro (radianos; negativo = aberta para dentro) e o tremor das batidas */
export const idoorAt = (t: number) => -1.25 * smooth((t - 21.7) / 0.35) * (1 - smooth((t - (W.e_slam - 0.22)) / 0.22));
export const BANGS = [W.e_bang, W.e_hits + 0.1, W.e_once, W.e_twice];
export const bangAt = (t: number) => { for (const b of BANGS) { const d = t - b; if (d >= 0 && d < 0.35) return Math.exp(-d * 12) * Math.sin(d * 70); } return 0; };
/** a luz embaixo da porta do quarto (andar de cima): acesa até "off" */
export const stripOn = (t: number) => t < W.e_off;

const SH1: [number, V3, V3, number][] = [[0.0, [2004.7, 1.3, 14.6], [2000.5, 1.0, 14.6], 42], [2.3, [2004.45, 1.31, 14.6], [2000.5, 1.0, 14.6], 40]];
/** v3: UMA câmera do quadro 0 até a escolha (como no vídeo 21): gira nos dois, sai correndo na sua frente, chega com você na porta,
 *  vira para ele e volta para a chave, entra na casa antes de você e se vira para a porta batendo, desce até o celular, vira para a
 *  escada e termina na escolha. Só o plano 14 (loop) corta, para voltar ao quadro 0. Tempos = palavras do áudio. */
export const TRAVEL2: [number, V3, V3, number][] = [
  [0.0, [2004.7, 1.3, 14.6], [2000.5, 1.0, 14.6], 42],
  [2.3, [2004.45, 1.31, 14.6], [2000.5, 1.0, 14.6], 40],
  [4.3, [2003.7, 1.37, 14.62], [2000.5, 1.1, 14.6], 37],        // "Hard."
  [5.7, [2003.9, 1.4, 15.1], [2000.5, 1.05, 15.2], 40],         // "twist free"
  [6.8, [2004.4, 1.42, 16.4], [2000.5, 1.05, 16.1], 44],
  [7.7, [2003.3, 1.4, 21.0], [2000.4, 1.05, 18.3], 50],         // "run": passa para a sua frente
  [8.6, [2001.5, 1.32, 26.2], [2000.3, 1.05, 18.5], 54],        // "Behind you": você e ele, rua abaixo
  [9.6, [2000.9, 1.3, 29.9], [2000.25, 1.05, 20.0], 54],
  [10.8, [2000.75, 1.28, 34.6], [2000.2, 1.05, 25.0], 54],      // "Fast."
  [12.0, [2001.2, 1.32, 39.4], [2000.2, 1.05, 30.0], 52],
  [13.0, [2002.1, 1.4, 42.0], [2000.3, 1.1, 38.5], 48],         // sai da frente, você chega na porta
  [13.9, [2001.45, 1.32, 42.25], [2000.35, 1.05, 43.7], 40],    // por cima do seu ombro: a fechadura
  [15.0, [2000.85, 1.2, 42.95], [2000.36, 1.0, 43.92], 36],     // "shaking", "won't go in"
  [16.8, [2000.95, 1.18, 43.3], [2000.36, 1.0, 43.92], 32],     // de lado na fechadura
  [18.1, [2001.1, 1.75, 43.3], [2000.2, 1.1, 34.0], 44],        // "Wrong way": sobe e olha por cima de você, rua abaixo: ele vindo
  [19.3, [2000.95, 1.2, 43.25], [2000.36, 1.0, 43.92], 34],     // "flip"
  [20.5, [2000.8, 1.15, 43.35], [2000.36, 1.0, 43.92], 30],     // "Click."
  [21.4, [2000.85, 1.45, 41.9], [1999.9, 1.3, 46.0], 40],       // a porta abre (a câmera atrás de você, à direita, mirando o vão)
  [22.3, [2000.7, 1.6, 42.4], [1999.95, 1.3, 46.0], 44],        // você entra (ele logo atrás)
  [22.65, [2000.25, 1.55, 43.85], [2000.05, 1.25, 46.5], 48],   // passa pela porta (já toda aberta) atrás de você
  [23.05, [2001.2, 1.5, 44.4], [2000.05, 1.25, 44.95], 50],
  [23.25, [2001.45, 1.5, 44.95], [2000.05, 1.25, 44.75], 50],   // dá a volta em você pela direita (a 1,4 m)...
  [23.5, [2001.45, 1.5, 45.6], [2000.05, 1.25, 44.5], 50],
  [24.25, [2001.0, 1.5, 46.7], [2000.05, 1.25, 44.45], 46],     // ...e fica de frente, a porta fechada atrás de você
  [24.6, [2000.2, 1.42, 46.8], [2000.0, 1.3, 44.31], 42],       // BANG
  [30.2, [2000.15, 1.44, 46.21], [2000.0, 1.32, 44.31], 40],
  [33.6, [2000.05, 1.5, 45.31], [2000.0, 1.46, 44.36], 32],     // "silence": no seu rosto
  [34.6, [2000.3, 1.43, 45.5], [2000.0, 1.37, 44.41], 35],      // o celular
  [40.9, [2000.35, 1.44, 45.36], [2000.0, 1.38, 44.41], 33],
  [41.6, [2001.15, 1.42, 45.15], [2000.1, 1.3, 44.9], 40],      // você sai da porta e anda até a escada; a câmera dá a volta...
  [42.2, [2000.95, 1.3, 44.4], [2000.3, 1.5, 46.6], 44],        // ...e fica atrás de você
  [42.8, [2000.5, 1.15, 44.35], [2001.0, 2.6, 50.7], 47],       // "Upstairs": por cima do seu ombro, a escada
  [45.2, [2000.55, 1.12, 44.6], [2001.0, 3.3, 51.9], 42],       // a luz embaixo da porta do quarto apaga
  [48.3, [2000.6, 1.12, 44.85], [2001.0, 3.45, 52.0], 38],      // "Someone is already inside"
  [48.9, [2001.15, 1.25, 45.2], [2000.25, 1.3, 45.9], 42],         // a câmera contorna você pela direita...
  [49.6, [2001.35, 1.45, 46.15], [2000.25, 1.25, 45.95], 44],   // ..."You decide": você de perto, de lado
  [50.15, [2001.25, 2.0, 47.3], [2000.25, 1.25, 45.9], 46],      // ...sobe a escada de costas, olhando para você...
  [50.75, [2001.3, 3.3, 49.4], [2000.25, 1.2, 45.6], 50],
  [51.4, [2001.3, 3.6, 50.0], [2000.25, 1.2, 45.6], 52],        // ...e lá de cima: você embaixo, a porta atrás (A), a escada (B)
  [63.9, [2001.25, 3.5, 49.6], [2000.25, 1.15, 45.6], 46],
];
const TR = spline(TRAVEL2);
const CAMS: Record<number, Key[]> = {
  1: TR, 2: TR, 3: TR, 4: TR, 5: TR, 6: TR, 7: TR, 8: TR, 9: TR, 10: TR, 11: TR, 12: TR, 13: TR,
  // o loop: chega ao quadro 0 desacelerando; no último quadro a câmera está no ponto do quadro 0
  14: [{ f: 0, s: (f) => { const r = Math.max(0, (65.0 - f / FPS) / 1.1) ** 2;
    return { pos: [SH1[0][1][0] + 0.3 * r, SH1[0][1][1] + 0.03 * r, SH1[0][1][2]], look: SH1[0][2], fov: SH1[0][3] + 3 * r }; } }],
};
/** impact kicks: flip sign every frame, decay over 7 frames */
const KICKS: number[] = [0.82, 4.3, 5.7, 23.16, 24.68, 26.22, 27.56, 28.82];   // vídeo 122: arranco, "hard", soltar, porta batendo e as batidas
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
export const DOF: Dof[] = SHOTS.map((s) => (s.id === 14 ? { f: s.a, cInf: 4, focus: () => SH1[0][2] } : true ? { f: s.a, cInf: 4, focus: (f: number) => camAt(s.id, f).look } : { f: s.a, cInf: FOC[s.id][0], focus: () => FOC[s.id][1] }));   // vídeo 21: o foco anda junto com a mira da câmera
export const dofAt = (f: number) => {
  let i = 0; while (i + 1 < DOF.length && f >= DOF[i + 1].f) i++;
  const d = DOF[i], p = DOF[Math.max(0, i - 1)];
  const k = d.dur ? Math.min(1, (f - d.f) / d.dur) : 1;
  return { cInf: p.cInf + (d.cInf - p.cInf) * k, focus: d.focus };
};
export type Fg = { a: number; b: number; kit: string; pos: V3; s?: number; yaw?: number };
export const FOREGROUND: Fg[] = [];

