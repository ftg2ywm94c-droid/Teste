// The Piazza: lawn, marble paving, cathedral, baptistery, city wall, houses and hills, plus the tower built floor by
// floor as a kinematic chain (each floor sits on the top of the one below, leaning, the upper ones bent back).
// Sky, light rig, clouds and the character cards work exactly like the bridge short.
import * as THREE from "three";
import { Batch, boxGeo, V, lam, house, Kit, quad, tri } from "./build";
import { rep, ctex, stoneHD, cobbleHD, grassHD, cloudHD, roofHD, brick, facadeHD } from "./paint";
import { LIGHTS, LOOK, LightPreset } from "./lights";
import { TONE, CHAR, untone, twoTone } from "./shade";
import { NOINK } from "./ink";
import { Pool, Actor, Fx, stage } from "./cast";
import { FPS, D0, SHOTS, camAt, ShotDef, FLOOR_H, V3, W, windAt, leanAt, lampOn, fallen, doorAt, darkAt, sirenK, sirenX, sirenPulse, clamp01, tvState, tvOn, ledOn, vibAt, TvState, curtainAt, talkAt, knobAt, poleAt, torchOn, torchAim, youZ } from "./story";

export const loadKit = async (): Promise<Kit> => ({});

const discTex = () => ctex("sunDisc", 128, 128, (g) => {
  const gr = g.createRadialGradient(64, 64, 58, 64, 64, 64); gr.addColorStop(0, "rgba(255,255,255,1)"); gr.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = gr; g.fillRect(0, 0, 128, 128);
});
// banheiro: a lanterna do celular vem de baixo e de perto da câmera; sala: a lua entra pelo buraco do teto, alta e de trás
// sala de noite: luz fria, baixa e de trás da câmera; lembrança de dia: sol entrando pela janela
const SUN_SHOT: Record<number, { az?: number; el?: number }> = { 4: { az: 140, el: 25 }, 5: { az: 150, el: 22 } };

/** horizontal quad facing up at height y covering x0..x1, z0..z1 */
const quadUp = (x0: number, x1: number, z0: number, z1: number, u: number, v: number, y = D0) => {
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute([x0, y, z1, x1, y, z1, x1, y, z0, x0, y, z1, x1, y, z0, x0, y, z0], 3));
  g.setAttribute("normal", new THREE.Float32BufferAttribute([0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0], 3));
  g.setAttribute("uv", new THREE.Float32BufferAttribute([0, 0, u, 0, u, v, 0, 0, u, v, 0, v], 2));
  return g;
};
const cyl = (r0: number, r1: number, h: number, n = 48, open = false) => new THREE.CylinderGeometry(r1, r0, h, n, 1, open).translate(0, h / 2, 0);
const at = (x: number, y: number, z: number) => new THREE.Matrix4().makeTranslation(x, y, z);

/** white marble with soft grey bands (the tower and the cathedral) */
const marble = () => stoneHD("marbleHD", ["#f1ebdf", "#ebe3d4", "#f5f0e6", "#e4dccb"], "#b9ae9c");
const marbleBand = () => ctex("marbleBand", 1024, 1024, (g) => {
  g.fillStyle = "#efe8da"; g.fillRect(0, 0, 1024, 1024);
  for (let y = 0; y < 1024; y += 128) { g.fillStyle = "#c9c3b8"; g.fillRect(0, y + 96, 1024, 22); }
  g.strokeStyle = "rgba(150,140,125,0.5)"; g.lineWidth = 3;
  for (let y = 0; y < 1024; y += 64) for (let x = (y / 64) % 2 ? 0 : 64; x < 1024; x += 128) g.strokeRect(x, y, 128, 64);
});
const mud = () => ctex("mud", 512, 512, (g) => {
  const gr = g.createRadialGradient(256, 256, 40, 256, 256, 256);
  gr.addColorStop(0, "rgba(108,78,52,1)"); gr.addColorStop(0.7, "rgba(125,92,62,0.9)"); gr.addColorStop(1, "rgba(125,92,62,0)");
  g.fillStyle = gr; g.fillRect(0, 0, 512, 512);
  g.fillStyle = "rgba(80,56,38,0.6)";
  for (let i = 0; i < 60; i++) { const a = i * 2.4, r = 40 + (i * 37) % 180; g.beginPath(); g.ellipse(256 + Math.cos(a) * r, 256 + Math.sin(a) * r, 14, 7, a, 0, 7); g.fill(); }
});

/** one floor of the tower in its own frame (base at y = 0) */
const floorGeo = (b: Batch, k: number, M: Record<string, THREE.Material>) => {
  const h = FLOOR_H[k];
  if (k === 0) {
    b.add(cyl(7.0, 7.0, h), M.band);
    b.add(cyl(7.9, 7.9, 0.9), M.marble);
    b.add(cyl(7.85, 7.85, 0.6), M.marble, at(0, h - 0.6, 0));
    for (let i = 0; i < 15; i++) { const a = (i / 15) * Math.PI * 2; b.add(cyl(0.38, 0.34, h - 1.4, 10), M.marble, at(Math.cos(a) * 7.25, 0.85, Math.sin(a) * 7.25)); }
    // the door on the south side (faces the cameras)
    b.add(boxGeo(V(-1.0, 0.85, -7.12), V(1.0, 4.4, -6.9)), M.door);
  } else if (k < 7) {
    b.add(cyl(6.1, 6.1, h), M.band);
    b.add(cyl(7.75, 7.75, 0.45), M.marble);
    b.add(cyl(7.85, 7.85, 0.55), M.marble, at(0, h - 0.55, 0));
    for (let i = 0; i < 26; i++) { const a = (i / 26) * Math.PI * 2; b.add(cyl(0.2, 0.18, h - 1.0, 8), M.marble, at(Math.cos(a) * 7.35, 0.45, Math.sin(a) * 7.35)); }
  } else {
    b.add(cyl(4.9, 4.9, h), M.band);
    b.add(cyl(5.6, 5.6, 0.4), M.marble);
    b.add(cyl(5.7, 5.7, 0.5), M.marble, at(0, h - 0.5, 0));
    for (let i = 0; i < 12; i++) { const a = (i / 12) * Math.PI * 2; b.add(cyl(0.2, 0.18, h - 0.9, 8), M.marble, at(Math.cos(a) * 5.25, 0.4, Math.sin(a) * 5.25)); }
  }
};

const tree = (b: Batch, x: number, z: number, s: number, M: Record<string, THREE.Material>, seed: number) => {
  b.add(cyl(0.35 * s, 0.25 * s, 3.2 * s, 8), M.bark, at(x, D0, z));
  const g = new THREE.IcosahedronGeometry(2.2 * s, 1);
  b.add(g, seed % 2 ? M.leafA : M.leafB, at(x, D0 + 4.6 * s, z));
  b.add(new THREE.IcosahedronGeometry(1.6 * s, 1), seed % 3 ? M.leafB : M.leafA, at(x + 0.9 * s, D0 + 5.8 * s, z - 0.4 * s));
};

export class World {
  root = new THREE.Group();
  private pool = new Pool();
  private actors: Actor[] = [];
  private fxs: Fx[] = [];
  private hemi: THREE.HemisphereLight; private sun: THREE.DirectionalLight;
  private sky: THREE.Mesh; private skyMat: THREE.ShaderMaterial;
  private fog = new THREE.Fog("#bccbec", 25, 420);
  private sunDisc: THREE.Sprite;
  private sunCache = new Map<number, THREE.Vector3>();
  private cloudMaps: Record<"day" | "golden" | "night", THREE.Texture[]>;
  private clouds: THREE.Mesh[] = [];
  private floors: THREE.Group[] = [];
  private glows: THREE.Mesh[] = [];   // janelas e lâmpadas: acesas até o apagão
  private glowOn = new THREE.MeshBasicMaterial({ color: new THREE.Color(2.6, 1.75, 0.85), fog: true });
  private glowOff = new THREE.MeshBasicMaterial({ color: new THREE.Color(0.03, 0.035, 0.06), fog: true });
  private bulbOn = new THREE.MeshBasicMaterial({ color: new THREE.Color(4.0, 3.0, 1.6), fog: true });
  private storm = new THREE.Group();
  private wtrees: { g: THREE.Group; ph: number }[] = [];   // árvores que balançam com o vento
  private big = new THREE.Group();                          // a árvore enorme da frente da sua casa
  private lamp!: THREE.Mesh;
  private smash = new THREE.Group();                        // depois da queda: copa amassada na fachada, buraco, telhas no chão
  private bathDoor = new THREE.Group();
  // vídeo 18: a TV (tela com textura desenhada por quadro), a luzinha do console, a almofada, o milharal, a janela da casa
  private tvCv = document.createElement("canvas"); private tvTex!: THREE.CanvasTexture; private tvKey = "";
  private tvMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(1.35, 1.35, 1.35), fog: false });
  private led!: THREE.Mesh; private ledOnM = new THREE.MeshBasicMaterial({ color: new THREE.Color(0.6, 1.6, 4.5), fog: false });
  private cushion = new THREE.Group();
  private corn: { g: THREE.Group; ph: number }[] = [];
  private farmWin!: THREE.Mesh; private winBlue = new THREE.MeshBasicMaterial({ color: new THREE.Color(0.55, 1.0, 2.6), fog: true });
  private roomWin!: THREE.Mesh;
  private curtL = new THREE.Group(); private curtR = new THREE.Group();   // vídeo 19: a cortina da sala
  private knob = new THREE.Group();
  // PILOTO: luzes reais (o poste da esquina e a lanterna do celular) e a lâmpada que acende/apaga
  private poleLight = new THREE.SpotLight("#ffb766", 0, 22, 0.95, 0.55, 1.4);
  private farLight = new THREE.SpotLight("#ffc98a", 0, 24, 0.9, 0.6, 1.4);
  private torch = new THREE.SpotLight("#eef4ff", 0, 30, 0.33, 0.45, 1.1);
  private poleBulb!: THREE.Mesh; private bulbWarm = new THREE.MeshBasicMaterial({ color: new THREE.Color(5.0, 3.4, 1.6), fog: true });                                         // vídeo 20: a maçaneta da porta da frente (gira)
  private frustum = new THREE.Frustum();
  private m4 = new THREE.Matrix4(); private v = new THREE.Vector3(); private sph = new THREE.Sphere();

  constructor(_kit: Kit) {
    const R = this.root, M: Record<string, THREE.Material> = {};
    // ---- sky + light (same as the bridge short) ----
    this.skyMat = new THREE.ShaderMaterial({
      uniforms: { c0: { value: new THREE.Color() }, c1: { value: new THREE.Color() }, c2: { value: new THREE.Color() },
        c3: { value: new THREE.Color() }, c4: { value: new THREE.Color() }, e: { value: new THREE.Vector4() } },
      vertexShader: "varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }",
      fragmentShader: `uniform vec3 c0, c1, c2, c3, c4; uniform vec4 e; varying vec3 vP;
        void main(){ float el = asin(clamp(normalize(vP).y, -1.0, 1.0));
          vec3 c = mix(c0, c1, smoothstep(0.0, e.x, el));
          c = mix(c, c2, smoothstep(e.x, e.y, el));
          c = mix(c, c3, smoothstep(e.y, e.z, el));
          c = mix(c, c4, smoothstep(e.z, e.w, el));
          gl_FragColor = vec4(c, 1.0); }`,
      side: THREE.BackSide, depthWrite: false, fog: false,
    });
    this.sky = new THREE.Mesh(new THREE.SphereGeometry(1100, 48, 24), this.skyMat);
    this.sky.renderOrder = -1; this.sky.frustumCulled = false; this.sky.layers.set(NOINK);
    R.add(this.sky);
    this.sunDisc = new THREE.Sprite(new THREE.SpriteMaterial({ map: discTex(), color: new THREE.Color(6.0, 4.4, 2.4), fog: false, depthWrite: false }));
    this.sunDisc.frustumCulled = false; this.sunDisc.layers.set(NOINK); R.add(this.sunDisc);
    this.hemi = new THREE.HemisphereLight("#cfe6ff", "#6c5c8c", 1.1);
    this.sun = new THREE.DirectionalLight("#fff0d6", 2.6);
    this.sun.castShadow = true;
    this.sun.shadow.mapSize.set(4096, 4096);
    R.add(this.hemi, this.sun, this.sun.target);
    this.cloudMaps = { day: [0, 1, 2, 3].map((k) => cloudHD(k, LOOK.day.cloud)), golden: [0, 1, 2, 3].map((k) => cloudHD(k, LOOK.golden.cloud)), night: [0, 1, 2, 3].map((k) => cloudHD(k, LOOK.night.cloud)) };
    for (let i = 0; i < 10; i++) {
      const a = (i / 10) * Math.PI * 2 + 0.3, d = 620 + (i % 3) * 60;
      const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: this.cloudMaps.day[i % 4], color: new THREE.Color(1.1, 1.1, 1.1), transparent: true, depthWrite: false, fog: false }));
      const w = 140 + (i % 4) * 30;
      m.position.set(Math.cos(a) * d, 110 + (i % 4) * 40, Math.sin(a) * d); m.scale.set(w, w / 2, 1);
      m.layers.set(NOINK);
      this.clouds.push(m); R.add(m);
    }

    // ---- materials ----
    M.grass = lam("grassHD", () => ({ map: grassHD() }));
    M.cobble = lam("cobbleHD", () => ({ map: cobbleHD() }));
    M.marble = lam("marbleHD", () => ({ map: marble() }));
    M.band = lam("marbleBand", () => ({ map: rep(marbleBand(), 3, 1) }));
    M.pave = lam("paveHD", () => ({ map: stoneHD("paveHD", ["#e6dccd", "#ddd3c3", "#ece4d6", "#d6cbba"], "#aea293") }));
    M.door = lam("door", () => ({ color: "#3a2a22" }));
    M.roof = lam("roofRed", () => ({ map: roofHD("#b5543c") }));
    M.wall = lam("cityWall", () => ({ map: rep(brick(), 6, 1) }));
    M.bark = lam("bark", () => ({ color: "#8a5a3c" }));
    M.leafA = lam("leafA", () => ({ color: "#62ae4c" }));
    M.leafB = lam("leafB", () => ({ color: "#4f9a43" }));
    M.wood = lam("scaffoldWood", () => ({ color: "#a8724a" }));
    M.dome = lam("domeRed", () => ({ color: "#c0603f" }));
    const hm = [lam("hillA", () => ({ color: "#78b257" })), lam("hillB", () => ({ color: "#6aa24e" })), lam("hillC", () => ({ color: "#8bbf63" }))];

    // ---- vídeo 11: cenários ----
    const b = new Batch();
    b.add(quadUp(-900, 900, -900, 900, 450, 450), M.grass);
    ([[-360, 300, 200, 60, 130], [160, 420, 260, 70, 150], [460, 180, 180, 50, 140], [-480, -60, 200, 46, 150], [520, -120, 170, 44, 130], [760, 260, 220, 60, 150]] as const)
      .forEach(([x, z, sx, sy, sz], i) => b.add(new THREE.SphereGeometry(1, 28, 14, 0, Math.PI * 2, 0, Math.PI / 2), hm[i % 3], new THREE.Matrix4().compose(V(x, D0 - 2, z), new THREE.Quaternion(), V(sx, sy, sz))));
    M.asphalt = lam("asphalt", () => ({ color: "#4a4c55" }));
    M.walk = lam("walkHD", () => ({ map: stoneHD("walkHD", ["#cfc6b8", "#c6bdae", "#d6cec1", "#bfb5a6"], "#9e9484") }));
    M.white = lam("fridge", () => ({ color: "#eef1f4" }));
    M.handle = lam("fridgeHandle", () => ({ color: "#8d96a3" }));
    M.pole = lam("pole", () => ({ color: "#3d4250" }));
    M.tileWall = lam("tileWall", () => ({ color: "#dfe7e4" }));
    M.tileFloor = lam("tileFloorHD", () => ({ map: stoneHD("tileFloorHD", ["#d9cdb8", "#d1c4ad", "#e0d5c2", "#cbbda5"], "#a89880") }));
    M.woodLight = lam("woodLight", () => ({ color: "#c08a5a" }));
    M.woodDark = lam("woodDark", () => ({ color: "#7a5236" }));
    M.counterTop = lam("counterTop", () => ({ color: "#efe9df" }));
    M.glassNight = lam("glassNight", () => ({ color: "#1d2a52" }));
    M.steel = lam("steel", () => ({ color: "#aab3bf" }));
    M.tank = lam("tankBlue", () => ({ color: "#3e7fc1" }));
    M.gen = lam("genYellow", () => ({ color: "#d9b53c" }));
    M.concrete = lam("concreteHD", () => ({ map: stoneHD("concreteHD", ["#c9c6bf", "#c2bfb7", "#d0cdc6", "#bbb7ae"], "#9d9990") }));
    M.sofa = lam("sofa", () => ({ color: "#c0563e" }));
    M.rug = lam("rug", () => ({ color: "#3f6fb5" }));
    M.shelf = lam("shelfBoxes", () => ({ color: "#f08a2c" }));
    M.shelf2 = lam("shelfBoxes2", () => ({ color: "#2f8a4f" }));
    M.shelf3 = lam("shelfBoxes3", () => ({ color: "#f3d35a" }));
    const bx = (x0: number, y0: number, z0: number, x1: number, y1: number, z1: number, m: THREE.Material, r = 0) => b.add(boxGeo(V(x0, D0 + y0, z0), V(x1, D0 + y1, z1), r), m);
    /** barra cilíndrica de p0 a p1 */
    const bar = (bb: Batch, p0: THREE.Vector3, p1: THREE.Vector3, r: number, m: THREE.Material) => {
      const g = new THREE.CylinderGeometry(r, r, p0.distanceTo(p1), 8);
      g.applyMatrix4(new THREE.Matrix4().makeRotationFromQuaternion(new THREE.Quaternion().setFromUnitVectors(V(0, 1, 0), p1.clone().sub(p0).normalize())));
      g.translate((p0.x + p1.x) / 2, (p0.y + p1.y) / 2, (p0.z + p1.z) / 2);
      bb.add(g, m);
    };

    // STREET (0,0): rua, calçada, fileira de casas acesas, outras fileiras para o plano aéreo
    b.add(quadUp(-80, 80, -16, 4, 80, 10, D0 + 0.03), M.asphalt);
    b.add(quadUp(-80, 80, 4, 12.2, 50, 4, D0 + 0.05), M.walk);
    b.add(quadUp(-80, 80, -20.2, -16, 50, 2, D0 + 0.05), M.walk);
    const HX = [-10, 0, 10.5, 21], HW = [9.5, 10, 10.5, 9], HH = [8.4, 9.8, 7, 8.4];
    HX.forEach((x, i) => house(b, x, 16, Math.PI, HW[i], 8, HH[i], i + 2));
    for (const x of [-32, -21]) house(b, x, 16, Math.PI, 10, 8, 7 + (x & 3), 9 + (x & 1));
    for (const x of [32, 43, 54]) house(b, x, 16, Math.PI, 10, 8, 7.5 + (x % 3), 11 + (x & 1));
    let hsd = 20;
    for (let x = -40; x <= 60; x += 11) { house(b, x, -25, 0, 10, 8, 7 + (hsd % 3), hsd); hsd++; }
    for (let x = -46; x <= 66; x += 12) { house(b, x + 3, 32, Math.PI, 11, 8, 7 + (hsd % 3) * 1.5, hsd); hsd++; }
    for (let x = -52; x <= 72; x += 13) { house(b, x, 48, Math.PI, 12, 8, 9 + (hsd % 2) * 3, hsd); hsd++; }
    let ts = 0;
    for (let x = -60; x <= 80; x += 14) { tree(b, x + (ts % 3), 62 + (ts % 2) * 3, 1.1 + (ts % 3) * 0.15, M, ts); ts++; }
    // árvores da calçada (dos dois lados) num grupo próprio cada uma, para o vento balançar
    ([[-15.5, 10.4, 0.8], [-8.5, 10.6, 0.7], [26.5, 10.8, 0.75], [-22, -18, 0.85], [-12, -18.2, 0.75], [-1.5, -17.8, 0.9], [9, -18.1, 0.8], [19, -17.9, 0.85]] as const)
      .forEach(([x, z, sc], i) => { const g = new THREE.Group(); g.position.set(x, 0, z); const tb2 = new Batch(); tree(tb2, 0, 0, sc, M, i + 3); tb2.build(g); R.add(g); this.wtrees.push({ g, ph: i * 1.7 }); });
    { // a árvore enorme: tronco grosso, galhos e copa larga, pivô na base
      const bb = new Batch();
      bb.add(cyl(0.55, 0.3, 6.2, 12), M.bark);
      bar(bb, V(0, 4.2, 0), V(1.6, 6.0, -0.3), 0.14, M.bark); bar(bb, V(0, 4.6, 0), V(-1.5, 6.3, 0.4), 0.13, M.bark);
      ([[0, 7.4, 0, 2.9, "leafB"], [1.6, 8.3, -0.5, 2.2, "leafA"], [-1.5, 8.0, 0.6, 2.1, "leafA"], [0.3, 9.4, 0.2, 1.8, "leafB"], [-0.4, 6.6, -1.1, 1.7, "leafA"]] as const)
        .forEach(([x, y, z, r, m]) => bb.add(new THREE.IcosahedronGeometry(r, 1), M[m], at(x, y, z)));
      bb.build(this.big); this.big.position.set(3.5, D0, 9.0); R.add(this.big);
    }
    // janelas acesas na fachada (mesma grade do facadeHD)
    const winG = new THREE.PlaneGeometry(1.0, 1.25).rotateY(Math.PI);
    HX.forEach((x, i) => {
      const w = HW[i], n = Math.max(1, Math.floor(w / 2.2)), floors = Math.max(1, Math.floor(HH[i] / 2.8));
      for (let fl = 0; fl < floors; fl++) for (let k = 0; k < n; k++) {
        if (fl === 0 && k === Math.floor(n / 2)) continue; // porta
        if ((i * 7 + fl * 3 + k) % 5 === 4) continue;      // nem toda janela acesa
        const px = -w / 2 + ((k + 0.5) / n) * w, yb = fl * 2.8 + 0.9;
        const m = new THREE.Mesh(winG, this.glowOn); m.position.set(x - px, D0 + yb + 0.64, 16 - 4 - 0.03); m.layers.set(NOINK);
        this.glows.push(m); R.add(m);
      }
    });
    for (const x of [1.5, 14]) {
      b.add(cyl(0.09, 0.07, 4.4, 10), M.pole, at(x, D0, 4.6));
      b.add(boxGeo(V(x - 0.05, D0 + 4.3, 4.55), V(x + 0.75, D0 + 4.4, 4.65)), M.pole);
      const bulb = new THREE.Mesh(new THREE.SphereGeometry(0.2, 16, 10), this.bulbOn); bulb.position.set(x + 0.7, D0 + 4.18, 4.6); bulb.layers.set(NOINK);
      this.glows.push(bulb); R.add(bulb);
    }
    // o temporal: árvore caída na calçada e um poste torto (só no plano 3)
    const tb = new Batch();
    { const trunk = cyl(0.32, 0.22, 7.5, 10); trunk.rotateZ(Math.PI / 2 - 0.12).rotateY(0.35).translate(0.6, 0.45, 10.6); tb.add(trunk, M.bark);
      tb.add(new THREE.IcosahedronGeometry(2.0, 1), M.leafA, at(-2.9, 1.4, 9.4)); tb.add(new THREE.IcosahedronGeometry(1.5, 1), M.leafB, at(-1.6, 1.0, 8.4));
      tb.add(new THREE.IcosahedronGeometry(1.2, 1), M.leafA, at(-3.8, 0.9, 11.2));
      const p = cyl(0.09, 0.07, 4.4, 10); p.rotateZ(0.32).translate(-6.0, 0, 4.6); tb.add(p, M.pole); }
    tb.build(this.storm); R.add(this.storm);

    // KITCHEN (200,0): chão de lajota, parede de azulejo, geladeira, balcão, janela escura
    b.add(quadUp(190, 212, -8, 4.5, 12, 7, D0 + 0.02), M.tileFloor);
    bx(190, 0, 4.0, 212, 3.4, 4.4, M.tileWall);
    bx(194.6, 0, -8, 195.0, 3.4, 4.4, M.tileWall);
    bx(199.9, 0, 3.12, 200.9, 1.85, 4.0, M.white, 2);
    bx(199.92, 1.28, 3.08, 200.88, 1.3, 3.12, M.handle);
    bx(200.74, 0.55, 3.0, 200.8, 1.15, 3.08, M.handle);
    bx(200.74, 1.4, 3.0, 200.8, 1.75, 3.08, M.handle);
    bx(201.1, 0, 3.35, 204.6, 0.88, 4.0, M.woodLight); bx(201.05, 0.88, 3.3, 204.65, 0.94, 4.0, M.counterTop);
    bx(201.1, 1.6, 3.65, 204.6, 2.3, 4.0, M.woodLight);
    bx(196.2, 0, 3.35, 199.6, 0.88, 4.0, M.woodLight); bx(196.15, 0.88, 3.3, 199.65, 0.94, 4.0, M.counterTop);
    bx(197.2, 1.25, 3.98, 198.8, 2.35, 4.02, M.glassNight); bx(197.1, 1.2, 3.96, 198.9, 1.26, 4.04, M.white); bx(197.1, 2.32, 3.96, 198.9, 2.4, 4.04, M.white);
    bx(197.95, 1.25, 3.95, 198.05, 2.35, 3.97, M.white);
    for (let i = 0; i < 3; i++) bx(201.4 + i * 0.5, 0.94, 3.6, 201.7 + i * 0.5, 1.15 + i * 0.05, 3.85, [M.shelf, M.shelf2, M.shelf3][i]);

    // BUILDING (-200,0): prédio de 6 andares, caixa d'água no telhado, bomba e cano, torneira
    b.add(quadUp(-230, -170, -12, 9, 30, 10, D0 + 0.03), M.asphalt);
    b.add(quadUp(-230, -170, 0, 9, 30, 4, D0 + 0.05), M.walk);
    const predio = lam("predioF", () => ({ map: facadeHD("predioF", 12, 18, { wall: "#e6d2a8", shutter: "#4f7fb0" }) }));
    b.add(quad(V(-194, D0, 9), V(-206, D0, 9), V(-206, D0 + 18, 9), V(-194, D0 + 18, 9)), predio);
    bx(-206, 0, 9.02, -194, 18, 19, lam("predioWall", () => ({ color: "#d9c39a" })));
    bx(-206.3, 18, 8.7, -193.7, 18.4, 19.3, M.concrete);
    b.add(cyl(1.4, 1.4, 2.2, 32), M.tank, at(-199, D0 + 18.4, 12.5)); b.add(cyl(1.5, 1.5, 0.15, 32), M.tank, at(-199, D0 + 20.6, 12.5));
    bx(-199.2, 18.4, 9.8, -198.8, 19.3, 11.2, M.steel);
    bx(-193.4, 0, 9.4, -192.0, 0.95, 10.8, M.steel, 2); b.add(cyl(0.08, 0.08, 17.6, 8), M.steel, at(-193.7, D0 + 0.9, 9.25));
    bx(-198.45, 0.85, 8.86, -198.15, 1.05, 9.0, M.steel); bx(-198.35, 0.75, 8.7, -198.25, 0.95, 8.9, M.steel);
    for (const [x, h, si] of [[-218, 14, 31], [-182, 12, 32]] as const) {
      const fm = lam("predio" + si, () => ({ map: facadeHD("predio" + si, 11, h, { wall: si % 2 ? "#cfd8e0" : "#e9c7b0", shutter: "#6b5a8a" }) }));
      b.add(quad(V(x + 5.5, D0, 10), V(x - 5.5, D0, 10), V(x - 5.5, D0 + h, 10), V(x + 5.5, D0 + h, 10)), fm);
      bx(x - 5.5, 0, 10.02, x + 5.5, h, 19, lam("pw" + si, () => ({ color: si % 2 ? "#bcc6cf" : "#d8b39c" })));
      bx(x - 5.7, h, 9.8, x + 5.7, h + 0.35, 19.2, M.concrete);
    }

    // ANTENNA (400,0): torre treliçada, painéis, gerador, abrigo
    const ab = new Batch();
    const T = V(400, D0, 20), H = 26, legs = [[-1, -1], [1, -1], [1, 1], [-1, 1]];
    const lp = (k: number, y: number) => { const s = 1.7 - 1.3 * (y / H); return V(T.x + legs[k][0] * s, y, T.z + legs[k][1] * s); };
    for (let k = 0; k < 4; k++) bar(ab, lp(k, 0), lp(k, H), 0.09, M.steel);
    for (let y = 0; y < H - 1; y += 2.6) for (let k = 0; k < 4; k++) { bar(ab, lp(k, y), lp((k + 1) % 4, y + 2.6), 0.04, M.steel); bar(ab, lp(k, y + 2.6), lp((k + 1) % 4, y + 2.6), 0.045, M.steel); }
    for (let k = 0; k < 3; k++) { const a = (k / 3) * Math.PI * 2 + 0.6; ab.add(boxGeo(V(-0.25, -0.9, -0.08), V(0.25, 0.9, 0.08), 1), M.white, new THREE.Matrix4().makeRotationY(-a).setPosition(T.x + Math.cos(a) * 0.75, H - 1.5, T.z + Math.sin(a) * 0.75)); }
    bar(ab, V(T.x, H, T.z), V(T.x, H + 2.5, T.z), 0.05, M.steel);
    ab.build(R);
    bx(402.4, 0, 15.6, 404.6, 1.3, 17.0, M.gen, 3); bx(403.0, 1.3, 16.0, 403.2, 1.9, 16.2, M.pole);
    bx(395.0, 0, 16.5, 398.0, 2.6, 19.5, M.concrete); bx(394.8, 2.6, 16.3, 398.2, 2.8, 19.7, M.pole);
    b.add(quadUp(390, 410, -8, 10, 10, 9, D0 + 0.04), M.walk);
    for (let i = 0; i < 6; i++) tree(b, 386 + i * 6 + (i % 2) * 2, 34 + (i % 3) * 3, 1.0 + (i % 2) * 0.2, M, i);

    // SHOP (400,120): lojinha com balcão e prateleiras
    b.add(quadUp(394, 406, 112, 123, 6, 6, D0 + 0.02), M.tileFloor);
    bx(394, 0, 122.8, 406, 3.2, 123.2, lam("shopWall", () => ({ color: "#f3e3c2" })));
    bx(398.4, 0, 119.6, 401.6, 1.0, 120.4, M.woodDark, 2); bx(398.3, 1.0, 119.5, 401.7, 1.06, 120.5, M.counterTop);
    for (let r = 0; r < 3; r++) { bx(396.5, 1.0 + r * 0.6, 122.4, 403.5, 1.05 + r * 0.6, 122.8, M.woodLight);
      for (let i = 0; i < 9; i++) bx(396.7 + i * 0.75, 1.05 + r * 0.6, 122.45, 397.15 + i * 0.75, 1.4 + r * 0.6 - (i % 3) * 0.05, 122.75, [M.shelf, M.shelf2, M.shelf3, M.sofa, M.rug][(i + r) % 5]); }

    // ROOM (600,0): sala no escuro: sofá, tapete, janela, quadro
    b.add(quadUp(592, 608, -6, 4.2, 8, 5, D0 + 0.02), lam("floorWoodHD", () => ({ map: stoneHD("floorWoodHD", ["#a4744c", "#9a6c46", "#ad7c52", "#93663f"], "#7d5536") })));
    bx(592, 0, 4.0, 608, 6.0, 4.4, lam("roomWall", () => ({ color: "#d9cbb4" })));
    bx(598.4, 0, 2.5, 601.6, 0.45, 3.6, M.sofa, 3); bx(598.4, 0.45, 3.3, 601.6, 1.05, 3.65, M.sofa, 3);
    bx(598.2, 0, 2.5, 598.5, 0.7, 3.65, M.sofa, 2); bx(601.5, 0, 2.5, 601.8, 0.7, 3.65, M.sofa, 2);
    b.add(quadUp(598.0, 602.0, 0.6, 2.9, 1, 1, D0 + 0.04), M.rug);
    bx(602.6, 1.2, 4.02, 604.4, 2.5, 4.06, lam("nightOut", () => ({ color: "#0c1226" }))); bx(602.5, 1.15, 3.95, 604.5, 1.22, 4.05, M.white); bx(603.45, 1.2, 3.95, 603.55, 2.5, 3.97, M.white);
    bx(598.9, 1.6, 3.97, 600.2, 2.4, 4.0, M.woodDark); bx(598.98, 1.68, 3.96, 600.12, 2.32, 3.97, M.shelf2);
    bx(596.4, 0, 3.0, 597.2, 0.55, 3.8, M.woodLight); b.add(cyl(0.03, 0.03, 0.9, 8), M.pole, at(596.8, D0 + 0.55, 3.4)); b.add(new THREE.ConeGeometry(0.28, 0.35, 16, 1, true).translate(0, 0.17, 0), M.white, at(596.8, D0 + 1.4, 3.4));
    this.lamp = new THREE.Mesh(new THREE.SphereGeometry(0.11, 16, 10), this.bulbOn); this.lamp.position.set(596.8, D0 + 1.5, 3.4); this.lamp.layers.set(NOINK); R.add(this.lamp);
    { const rw = lam("roomWall", () => ({ color: "#d9cbb4" }));   // vídeo 16: paredes laterais e do fundo da sala (os planos novos olham de lado)
      bx(591.7, 0, -6.3, 592.0, 3.1, 4.2, rw); bx(608.6, 0, -6.3, 608.9, 3.1, 4.2, rw); bx(592.0, 0, -6.6, 608.6, 3.1, -6.3, rw); }
    // a porta da sala (com fresta embaixo)
    bx(593.35, 0, 3.9, 593.5, 2.2, 3.99, M.white); bx(594.7, 0, 3.9, 594.85, 2.2, 3.99, M.white); bx(593.35, 2.1, 3.9, 594.85, 2.22, 3.99, M.white);
    bx(593.5, 0.07, 3.92, 594.7, 2.1, 3.97, M.woodLight);
    { const gap = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.05, 0.02), new THREE.MeshBasicMaterial({ color: new THREE.Color(1.4, 1.7, 2.6) })); gap.position.set(594.1, D0 + 0.045, 3.975); gap.layers.set(NOINK); R.add(gap); }
    for (const yy of [0.35, 1.2]) bx(593.6, yy, 3.905, 594.6, yy + 0.55, 3.92, lam("doorPanel", () => ({ color: "#a8724a" })));

    // BATH (800,0): banheiro sem janela: azulejo, vaso, pia, espelho, porta trancada
    b.add(quadUp(797.6, 802.4, -4, 3.5, 6, 9, D0 + 0.02), M.tileFloor);
    const az = lam("bathTile", () => ({ map: stoneHD("bathTileHD", ["#d8e8ea", "#d0e2e5", "#e0eeef", "#c8dcdf"], "#9fb8bc") }));
    bx(797.3, 0, 3.4, 799.3, 2.8, 3.7, az); bx(800.7, 0, 3.4, 802.7, 2.8, 3.7, az); bx(799.3, 2.12, 3.4, 800.7, 2.8, 3.7, az); bx(797.3, 0, -4, 797.6, 2.8, 3.7, az);
    // atrás da porta: o corredor escuro que dá na sala (só aparece pela fresta)
    { const hd = lam("hallDark", () => ({ color: "#14121e" })); bx(798.6, 0, 6.2, 801.4, 2.7, 6.3, hd); bx(798.5, 0, 3.7, 798.6, 2.7, 6.3, hd); bx(801.4, 0, 3.7, 801.5, 2.7, 6.3, hd);
      bx(798.6, 2.7, 3.7, 801.4, 2.8, 6.3, hd); b.add(quadUp(798.6, 801.4, 3.7, 6.2, 1, 1, D0 + 0.05), lam("hallFloor", () => ({ color: "#1d1a24" }))); } bx(802.4, 0, -4, 802.7, 2.8, 3.7, az);
    bx(799.3, 0, 3.3, 799.4, 2.12, 3.4, M.white); bx(800.6, 0, 3.3, 800.7, 2.12, 3.4, M.white); bx(799.3, 2.05, 3.3, 800.7, 2.12, 3.4, M.white);
    bx(801.0, 0, 2.4, 801.6, 0.42, 3.1, M.white, 3); bx(800.98, 0.42, 2.38, 801.62, 0.47, 3.12, M.white, 2); bx(801.0, 0.47, 2.95, 801.6, 0.95, 3.3, M.white, 2);
    b.add(cyl(0.12, 0.1, 0.78, 12), M.white, at(798.5, D0, 3.0)); bx(798.1, 0.78, 2.7, 798.9, 0.9, 3.35, M.white, 2);
    bx(798.15, 1.25, 3.36, 798.85, 1.95, 3.4, M.glassNight); bx(798.1, 1.2, 3.37, 798.9, 1.25, 3.41, M.steel);
    bx(797.62, 0.9, 1.6, 797.7, 1.5, 2.3, M.rug);

    // ===== vídeo 14: depois da queda =====
    { // fachada da sua casa (x = 0, frente em z = 12): copa amassada contra a parede, buraco, janelas quebradas, telhas e vidro na calçada
      const sb = new Batch(), dark = lam("holeDark", () => ({ color: "#14101c" }));
      ([[3.0, 5.6, 11.6, 2.2, "leafB"], [4.6, 6.4, 11.7, 1.8, "leafA"], [1.9, 6.6, 11.8, 1.6, "leafA"], [3.8, 7.6, 11.9, 1.7, "leafB"], [2.6, 4.6, 11.4, 1.3, "leafA"]] as const)
        .forEach(([x, y, z, r, m]) => sb.add(new THREE.IcosahedronGeometry(r, 1), M[m], at(x, y, z)));
      sb.add(quad(V(5.0, 3.6, 11.97), V(1.6, 3.4, 11.97), V(1.4, 7.4, 11.97), V(5.2, 7.8, 11.97)), dark);
      for (const [x0, y0] of [[-3.2, 1.0], [-3.2, 3.8], [3.6, 1.0]] as const) sb.add(quad(V(x0 + 0.6, y0, 11.96), V(x0 - 0.6, y0 + 0.1, 11.96), V(x0 - 0.4, y0 + 1.1, 11.96), V(x0 + 0.5, y0 + 0.9, 11.96)), dark);
      const tile = lam("tileRed", () => ({ color: "#b5543c" }));
      for (let i = 0; i < 22; i++) { const a = i * 2.39, r = 1.0 + (i % 5) * 0.6;
        sb.add(boxGeo(V(-0.22, 0, -0.12), V(0.22, 0.04, 0.12)), tile, new THREE.Matrix4().makeRotationY(a).setPosition(3.0 + Math.cos(a) * r, D0 + 0.06, 10.4 + Math.sin(a) * r * 0.6)); }
      for (let i = 0; i < 8; i++) { const a = i * 1.7; bar(sb, V(3.2 + Math.cos(a) * 1.5, D0 + 0.08, 10.2 + Math.sin(a)), V(3.2 + Math.cos(a) * 1.5 + 0.9, D0 + 0.3, 10.2 + Math.sin(a) + 0.4), 0.05, M.bark); }
      sb.build(this.smash); R.add(this.smash);
    }
    { // vídeo 18 — a sala do sítio: teto inteiro, rack, TV, console genérico (sem marca), almofada
      const ceil = lam("roomCeil", () => ({ color: "#cfc3ad" }));
      b.add(boxGeo(V(592, D0 + 3.0, -6.3), V(608, D0 + 3.15, 4.0), 0, true), ceil);
      const black = lam("tvBlack", () => ({ color: "#17171c" })), consW = lam("consoleWhite", () => ({ color: "#f2f3f5" }));
      bx(598.7, 0, -0.95, 601.3, 0.5, -0.45, M.woodDark, 2); bx(598.68, 0.5, -0.97, 601.32, 0.54, -0.43, M.woodLight);
      bx(599.85, 0.54, -0.72, 600.15, 0.6, -0.6, black); bx(599.96, 0.6, -0.68, 600.04, 0.66, -0.64, black);
      bx(599.12, 0.62, -0.68, 600.88, 1.6, -0.6, black, 1);
      bx(600.95, 0.54, -0.86, 601.08, 0.95, -0.56, consW, 2); bx(600.995, 0.55, -0.87, 601.035, 0.94, -0.55, black);
      // a caixa do console vazia no chão e o controle no rack
      bx(599.3, 0.54, -0.62, 599.5, 0.58, -0.5, black);
      // a tela: textura desenhada a cada quadro
      this.tvCv.width = 1024; this.tvCv.height = 576; this.tvTex = new THREE.CanvasTexture(this.tvCv); this.tvTex.colorSpace = THREE.SRGBColorSpace;
      this.tvMat.map = this.tvTex;
      const scr = new THREE.Mesh(new THREE.PlaneGeometry(1.68, 0.945), this.tvMat); scr.position.set(600.0, D0 + 1.11, -0.595); scr.layers.set(NOINK); R.add(scr);
      this.led = new THREE.Mesh(new THREE.BoxGeometry(0.012, 0.09, 0.004), this.ledOnM); this.led.position.set(601.015, D0 + 0.62, -0.548); this.led.layers.set(NOINK); R.add(this.led);
      const cb = new Batch(); cb.add(new THREE.SphereGeometry(1, 28, 14).scale(0.32, 0.1, 0.27).translate(0, 0.1, 0), lam("cushion", () => ({ color: "#f6e2a8", emissive: new THREE.Color("#3d3018") }))); cb.build(this.cushion);
      this.cushion.position.set(600.85, D0 + 0.45, 2.92); R.add(this.cushion);
      this.roomWin = new THREE.Mesh(new THREE.PlaneGeometry(1.8, 1.3), lam("nightOut", () => ({ color: "#0c1226" }))); this.roomWin.position.set(603.5, D0 + 1.85, 4.0); this.roomWin.rotation.y = Math.PI; R.add(this.roomWin);
    }
    { // vídeo 18 — o SÍTIO (-200, -300): casa do avô com varanda, terreiro, milharal, galpão com gerador, antena de rádio, cerca
      const dirt = lam("dirtYard", () => ({ map: ctex("dirtPlain", 512, 512, (g) => { g.fillStyle = "#7a5c3e"; g.fillRect(0, 0, 512, 512); let sd = 7; for (let i = 0; i < 900; i++) { sd = (sd * 16807) % 2147483647; const x = sd % 512; sd = (sd * 16807) % 2147483647; const y = sd % 512; g.fillStyle = i % 3 ? "rgba(60,42,26,0.35)" : "rgba(150,120,85,0.3)"; g.beginPath(); g.ellipse(x, y, 3 + (i % 5), 2 + (i % 3), i, 0, 7); g.fill(); } }) }));
      b.add(quadUp(-238, -176, -322, -268, 12, 10, D0 + 0.03), dirt);
      house(b, -200, -300, 0, 9, 7, 5.2, 3);
      const porch = lam("porchWood", () => ({ color: "#9c6b44" }));
      bx(-204.6, 0, -296.6, -195.4, 0.25, -294.4, M.concrete); bx(-204.6, 2.55, -296.6, -195.4, 2.7, -294.2, porch);
      for (const x of [-204.4, -200, -195.6]) bx(x - 0.08, 0.25, -294.6, x + 0.08, 2.55, -294.44, porch);
      // galpão de madeira com a porta escura e o gerador
      const plank = lam("plankHD", () => ({ map: stoneHD("plankHD", ["#8a6440", "#7e5a38", "#94704a", "#735232"], "#5c4128") })), inside = lam("shedDark", () => ({ color: "#15121a" }));
      bx(-190, 0, -310, -182, 3.6, -309.7, plank); bx(-190, 0, -310, -189.7, 3.6, -302, plank); bx(-182.3, 0, -310, -182, 3.6, -302, plank);
      bx(-190, 0, -302.3, -187.6, 3.6, -302, plank); bx(-184.4, 0, -302.3, -182, 3.6, -302, plank); bx(-187.6, 2.8, -302.3, -184.4, 3.6, -302, plank);
      bx(-189.7, 0, -309.7, -182.3, 3.55, -309.6, inside); b.add(quadUp(-189.7, -182.3, -309.6, -302.3, 1, 1, D0 + 0.04), inside);
      const tin = lam("tinRoof", () => ({ color: "#8d97a3" }));
      b.add(quad(V(-190.4, D0 + 3.6, -301.6), V(-181.6, D0 + 3.6, -301.6), V(-181.6, D0 + 4.8, -306), V(-190.4, D0 + 4.8, -306)), tin);
      b.add(quad(V(-181.6, D0 + 3.6, -310.4), V(-190.4, D0 + 3.6, -310.4), V(-190.4, D0 + 4.8, -306), V(-181.6, D0 + 4.8, -306)), tin);
      b.add(tri(V(-190, D0 + 3.6, -302), V(-190, D0 + 4.8, -306), V(-190, D0 + 3.6, -310)), plank); b.add(tri(V(-182, D0 + 3.6, -310), V(-182, D0 + 4.8, -306), V(-182, D0 + 3.6, -302)), plank);
      bx(-187.3, 0, -303.9, -185.9, 0.75, -302.9, M.gen, 3); bx(-187.35, 0.75, -303.95, -185.85, 0.8, -302.85, M.pole);
      // antena da internet de rádio no telhado
      bar(b, V(-202.2, D0 + 4.0, -298.2), V(-202.2, D0 + 9.2, -298.2), 0.07, M.steel);
      bar(b, V(-202.2, D0 + 8.0, -298.2), V(-201.2, D0 + 6.0, -298.2), 0.03, M.steel); bar(b, V(-202.2, D0 + 8.0, -298.2), V(-203.2, D0 + 6.0, -298.2), 0.03, M.steel);
      { const grid = lam("dishGrid", () => ({ map: ctex("dishGrid", 256, 192, (g) => { g.fillStyle = "#c9ced6"; g.fillRect(0, 0, 256, 192); g.strokeStyle = "#5c6370"; g.lineWidth = 6;
          for (let x = 0; x <= 256; x += 32) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, 192); g.stroke(); } for (let y = 0; y <= 192; y += 32) { g.beginPath(); g.moveTo(0, y); g.lineTo(256, y); g.stroke(); } }) }));
        b.add(boxGeo(V(-202.9, D0 + 8.2, -298.05), V(-201.5, D0 + 9.25, -297.97)), grid); bx(-202.3, 8.6, -297.97, -202.1, 8.8, -297.6, M.pole); }
      // cerca de madeira
      for (let x = -216; x <= -180; x += 2.4) bx(x - 0.06, 0, -287.06, x + 0.06, 1.15, -286.94, porch);
      bx(-216, 0.55, -287.03, -180, 0.62, -286.97, porch); bx(-216, 0.95, -287.03, -180, 1.02, -286.97, porch);
      for (let i = 0; i < 7; i++) tree(b, -178 + (i % 3) * 3 - i * 2, -318 - (i % 2) * 6, 1.0 + (i % 3) * 0.15, M, i);
      // o milharal: fileiras ao longo de z, cada uma num grupo que o vento inclina
      const stalk = lam("cornStalk", () => ({ color: "#8fae4a" })), leafC = lam("cornLeaf", () => ({ color: "#78a23e" })), tassel = lam("cornTassel", () => ({ color: "#d8c46a" }));
      let seed = 1; const rnd = () => { seed = (seed * 16807) % 2147483647; return seed / 2147483647; };
      for (let xr = -233; xr <= -210; xr += 0.9) {
        const rb2 = new Batch(), g = new THREE.Group();
        for (let z = -318; z <= -289; z += 0.45) {
          const h = 1.9 + rnd() * 0.5, dx = (rnd() - 0.5) * 0.2, dz = z + 300 + (rnd() - 0.5) * 0.15;
          rb2.add(new THREE.CylinderGeometry(0.018, 0.03, h, 5).translate(dx, h / 2, dz), stalk);
          for (let k = 0; k < 4; k++) { const y = 0.5 + k * 0.38, a = rnd() * 6.28, L = 0.55 + rnd() * 0.2;
            rb2.add(tri(V(dx, y, dz), V(dx + Math.cos(a) * L, y + 0.18, dz + Math.sin(a) * L), V(dx + Math.cos(a) * L * 0.5, y + 0.12, dz + Math.sin(a) * L * 0.5 + 0.05)), leafC); }
          rb2.add(new THREE.ConeGeometry(0.05, 0.25, 5).translate(dx, h + 0.1, dz), tassel);
        }
        rb2.build(g); g.position.set(xr, D0, -300); R.add(g); this.corn.push({ g, ph: xr * 0.37 });
      }
      // a janela da sala da casa: azul quando a TV liga sozinha
      this.farmWin = new THREE.Mesh(new THREE.PlaneGeometry(0.95, 1.05), this.winBlue); this.farmWin.position.set(-198.875, D0 + 1.65, -296.44); this.farmWin.layers.set(NOINK); this.farmWin.visible = false; R.add(this.farmWin);
    }
    { // vídeo 19 — A NOITE LIVRE
      // a cortina da janela da sala (dois panos que fecham do lado para o meio)
      const cloth = lam("curtain", () => ({ map: ctex("curtainHD", 256, 256, (g) => { g.fillStyle = "#b8873f"; g.fillRect(0, 0, 256, 256);
        for (let x = 0; x < 256; x += 32) { const gr = g.createLinearGradient(x, 0, x + 32, 0); gr.addColorStop(0, "rgba(60,30,10,0.35)"); gr.addColorStop(0.5, "rgba(255,230,180,0.18)"); gr.addColorStop(1, "rgba(60,30,10,0.35)"); g.fillStyle = gr; g.fillRect(x, 0, 32, 256); } }) }));
      for (const [grp, x0, dir] of [[this.curtL, 602.45, 1], [this.curtR, 604.55, -1]] as const) {
        const cb2 = new Batch(); cb2.add(boxGeo(V(dir > 0 ? 0 : -1, 0, -0.02), V(dir > 0 ? 1 : 0, 1.55, 0.02)), cloth); cb2.build(grp);
        grp.position.set(x0, D0 + 1.05, 3.9); R.add(grp);
      }
      bx(602.3, 2.62, 3.88, 604.7, 2.66, 3.95, M.pole);
      // a caminha do Thor (vazia), perto do sofá
      b.add(new THREE.TorusGeometry(0.34, 0.1, 10, 28).rotateX(Math.PI / 2).translate(597.0, D0 + 0.1, 1.3), lam("dogBed", () => ({ color: "#3f7fc2" })));
      b.add(cyl(0.3, 0.3, 0.05, 24), lam("dogBedIn", () => ({ color: "#e8d6b0" })), at(597.0, D0 + 0.02, 1.3));
      bx(597.55, 0, 1.05, 597.75, 0.06, 1.2, lam("dogBowl", () => ({ color: "#d94c3a" })));
      // o muro da frente da casa (x = 0) com o portão de correr aberto e o trilho
      const muro = lam("muroHD", () => ({ map: stoneHD("muroHD", ["#d8cbb2", "#d1c3a8", "#ddd1ba", "#cbbd9f"], "#a89a7f") }));
      bx(-5.2, 0, 7.8, 1.0, 1.9, 8.1, muro); bx(3.6, 0, 7.8, 5.2, 1.9, 8.1, muro); bx(-5.2, 0, 8.1, -4.9, 1.9, 12.0, muro); bx(4.9, 0, 8.1, 5.2, 1.9, 12.0, muro);
      bx(0.85, 0, 7.75, 1.05, 2.1, 8.15, M.pole); bx(3.55, 0, 7.75, 3.75, 2.1, 8.15, M.pole);
      bx(1.0, 0.0, 7.98, 6.4, 0.04, 8.02, M.steel); // trilho
      const grade = lam("gateBars", () => ({ color: "#2c2f38" })), gb = new Batch();
      gb.add(boxGeo(V(0, 0.05, -0.02), V(2.6, 0.12, 0.02)), grade); gb.add(boxGeo(V(0, 1.75, -0.02), V(2.6, 1.82, 0.02)), grade);
      for (let i = 0; i <= 13; i++) gb.add(boxGeo(V(i * 0.2 - 0.02, 0.05, -0.02), V(i * 0.2 + 0.02, 1.82, 0.02)), grade);
      const gate = new THREE.Group(); gb.build(gate); gate.position.set(2.6, D0, 7.66); R.add(gate);   // meio aberto: o vão de 1,6 m fica livre
      b.add(quadUp(-4.9, 4.9, 8.1, 12.0, 4, 2, D0 + 0.06), M.concrete);
    }
    { // o banheiro: teto com mancha de água; porta num grupo com dobradiça (abre uma fresta)
      b.add(boxGeo(V(797.3, D0 + 2.8, -4), V(802.7, D0 + 2.95, 3.7), 0, true), lam("bathCeil", () => ({ color: "#e4ece9" })));
      b.add(quad(V(801.0, 2.795, 0.6), V(802.2, 2.795, 0.6), V(802.2, 2.795, 1.8), V(801.0, 2.795, 1.8)), lam("stainHD", () => ({ map: ctex("stain", 256, 256, (g) => {
        g.fillStyle = "#e4ece9"; g.fillRect(0, 0, 256, 256); const gr = g.createRadialGradient(128, 128, 10, 128, 128, 120); gr.addColorStop(0, "rgba(120,100,70,0.75)"); gr.addColorStop(0.7, "rgba(150,130,95,0.45)"); gr.addColorStop(1, "rgba(150,130,95,0)");
        g.fillStyle = gr; g.beginPath(); for (let i = 0; i < 24; i++) { const a = (i / 24) * Math.PI * 2, r = 90 + 26 * Math.sin(i * 2.7); g.lineTo(128 + Math.cos(a) * r, 128 + Math.sin(a) * r); } g.closePath(); g.fill(); }) })));
      b.add(quadUp(801.2, 802.0, 0.8, 1.6, 1, 1, D0 + 0.03), lam("puddle", () => ({ color: "#2a3a5c" })));
      const db = new Batch();
      db.add(boxGeo(V(0, 0.05, -0.05), V(1.2, 2.05, 0.05)), M.woodLight);
      db.add(boxGeo(V(0.12, 0.98, -0.11), V(0.22, 1.04, -0.05)), M.steel); db.add(boxGeo(V(0.1, 1.18, -0.09), V(0.3, 1.24, -0.05)), M.steel);
      db.build(this.bathDoor); this.bathDoor.position.set(799.4, D0, 3.35); R.add(this.bathDoor);
    }

    { // ===== PILOTO — RUA (2000,0): asfalto com rachaduras, pedrinhas e poças; calçadas de lajota; meio-fio; bueiro;
      // muros com reboco e portões; postes com braço, luminária, parafusos e fios; tudo com textura desenhada aqui =====
      let sd = 11; const rnd = () => { sd = (sd * 16807) % 2147483647; return sd / 2147483647; };
      const asph = ctex("asphaltHD", 1024, 1024, (g) => {
        g.fillStyle = "#3b3d44"; g.fillRect(0, 0, 1024, 1024);
        for (let i = 0; i < 9000; i++) { const x = rnd() * 1024, y = rnd() * 1024, r = 0.6 + rnd() * 2.2, c = 40 + rnd() * 50;
          g.fillStyle = `rgba(${c},${c + 2},${c + 8},${0.35 + rnd() * 0.5})`; g.beginPath(); g.arc(x, y, r, 0, 7); g.fill(); }
        for (let i = 0; i < 260; i++) { const x = rnd() * 1024, y = rnd() * 1024, c = 120 + rnd() * 60; g.fillStyle = `rgba(${c},${c},${c - 6},0.8)`; g.beginPath(); g.ellipse(x, y, 1.5 + rnd() * 3, 1 + rnd() * 2, rnd() * 3, 0, 7); g.fill(); }
        g.strokeStyle = "rgba(18,18,22,0.85)"; g.lineCap = "round";
        for (let k = 0; k < 14; k++) { let x = rnd() * 1024, y = rnd() * 1024; g.lineWidth = 1.5 + rnd() * 2.5; g.beginPath(); g.moveTo(x, y);
          for (let j = 0; j < 9; j++) { x += (rnd() - 0.5) * 90; y += (rnd() - 0.3) * 70; g.lineTo(x, y); if (rnd() < 0.3) { g.moveTo(x, y); } } g.stroke(); }
        for (let k = 0; k < 5; k++) { const x = rnd() * 1024, y = rnd() * 1024, gr = g.createRadialGradient(x, y, 4, x, y, 60 + rnd() * 60); gr.addColorStop(0, "rgba(20,20,24,0.45)"); gr.addColorStop(1, "rgba(20,20,24,0)"); g.fillStyle = gr; g.fillRect(x - 130, y - 130, 260, 260); }
      });
      M.asphHD = lam("asphHD", () => ({ map: rep(asph, 2, 8) }));
      b.add(quadUp(1996.4, 2003.6, -12, 40, 1, 1, D0 + 0.03), M.asphHD);
      // faixa central apagada (tracejada, gasta)
      for (let z = -12; z < 40; z += 4) b.add(quadUp(1999.93, 2000.07, z, z + 2.0, 1, 1, D0 + 0.035), lam("laneWorn", () => ({ color: "#b9b29a" })));
      // poças que brilham com as luzes (Phong com brilho)
      const puddle = twoTone(new THREE.MeshPhongMaterial({ color: "#30343f", shininess: 120, specular: new THREE.Color(1.6, 1.5, 1.4) }));
      for (const [x, z, rx, rz] of [[2001.6, 13.8, 0.9, 0.5], [1999.2, 8.5, 0.7, 0.4], [1998.6, 4.0, 1.1, 0.6], [1998.9, 18.5, 0.6, 0.35]] as const)
        b.add(new THREE.CircleGeometry(1, 28).rotateX(-Math.PI / 2).scale(rx, 1, rz).translate(x, D0 + 0.04, z), puddle);
      const tile = ctex("walkTileHD", 512, 512, (g) => { g.fillStyle = "#a9a49a"; g.fillRect(0, 0, 512, 512);
        for (let y = 0; y < 512; y += 128) for (let x = 0; x < 512; x += 128) { const c = 150 + rnd() * 30; g.fillStyle = `rgb(${c},${c - 4},${c - 12})`; g.fillRect(x + 4, y + 4, 120, 120);
          for (let i = 0; i < 90; i++) { g.fillStyle = `rgba(70,66,60,${rnd() * 0.3})`; g.fillRect(x + 4 + rnd() * 120, y + 4 + rnd() * 120, 2, 2); } }
        g.strokeStyle = "rgba(40,36,32,0.6)"; g.lineWidth = 2; g.beginPath(); g.moveTo(140, 260); g.lineTo(200, 300); g.lineTo(230, 380); g.stroke(); });
      const walkM = lam("walkPilot", () => ({ map: rep(tile, 3, 26) }));
      b.add(quadUp(2003.85, 2006.6, -12, 40, 1, 1, D0 + 0.16), walkM); b.add(quadUp(1993.4, 1996.15, -12, 40, 1, 1, D0 + 0.16), walkM);
      const curb = lam("curbHD", () => ({ map: rep(stoneHD("curbHD", ["#b8b3a8", "#aea99e", "#c2bdb2", "#a39e93"], "#8a857b"), 1, 20) }));
      bx(2003.6, 0, -12, 2003.85, 0.16, 40, curb); bx(1996.15, 0, -12, 1996.4, 0.16, 40, curb);
      // bueiro na sarjeta
      const grate = lam("grate", () => ({ map: ctex("grateHD", 128, 256, (g) => { g.fillStyle = "#1b1c20"; g.fillRect(0, 0, 128, 256); g.fillStyle = "#4a4d55"; for (let y = 10; y < 256; y += 22) g.fillRect(10, y, 108, 9); g.strokeStyle = "#2a2b30"; g.lineWidth = 8; g.strokeRect(4, 4, 120, 248); }) }));
      b.add(quadUp(2003.1, 2003.55, 11.2, 12.2, 1, 1, D0 + 0.045), grate);
      // muros de reboco com portões, dos dois lados; casas atrás (fachadas)
      const plaster = (key: string, base: string) => lam(key, () => ({ map: rep(ctex(key + "T", 512, 512, (g) => { g.fillStyle = base; g.fillRect(0, 0, 512, 512);
        for (let i = 0; i < 2600; i++) { const a = rnd() * 0.12; g.fillStyle = rnd() < 0.5 ? `rgba(0,0,0,${a})` : `rgba(255,255,255,${a * 0.7})`; g.beginPath(); g.arc(rnd() * 512, rnd() * 512, 1 + rnd() * 5, 0, 7); g.fill(); }
        const gr = g.createLinearGradient(0, 380, 0, 512); gr.addColorStop(0, "rgba(40,50,40,0)"); gr.addColorStop(1, "rgba(40,50,40,0.45)"); g.fillStyle = gr; g.fillRect(0, 380, 512, 132);
        g.strokeStyle = "rgba(60,50,40,0.5)"; g.lineWidth = 1.5; g.beginPath(); g.moveTo(300, 120); g.lineTo(330, 200); g.lineTo(318, 260); g.stroke(); }), 3, 1) }));
      const murA = plaster("murA", "#cdbfa6"), murB = plaster("murB", "#b9c2b4"), murC = plaster("murC", "#d6b3a0");
      const gateM = lam("gatePilot", () => ({ color: "#2a2d35" }));
      for (const [side, x0, x1] of [[1, 2006.6, 2006.9], [-1, 1993.1, 1993.4]] as const)
        for (let z = -12, k = 0; z < 40; z += 8, k++) {
          const m = [murA, murB, murC][(k + (side > 0 ? 0 : 1)) % 3];
          bx(x0, 0, z, x1, 1.9, z + 5.4, m); // muro
          for (let i = 0; i <= 12; i++) bx(x0 + 0.05, 0.1, z + 5.4 + i * 0.2, x1 - 0.05, 1.85, z + 5.43 + i * 0.2, gateM); // portão de grade
          bx(x0 - 0.04, 1.9, z, x1 + 0.04, 2.0, z + 8, M.concrete);
          house(b, side > 0 ? 2011.5 : 1988.5, z + 4, side > 0 ? -Math.PI / 2 : Math.PI / 2, 7.6, 7, 6 + (k % 3) * 1.4, 30 + k + (side > 0 ? 0 : 10));
        }
      // postes de concreto com braço, luminária e fios (o da esquina z 15,3; o do fim da rua z -4, sem luz)
      const conc = lam("poleConc", () => ({ map: rep(stoneHD("poleConcHD", ["#9a978f", "#918e86", "#a39f97", "#8a877f"], "#77746d"), 1, 4) }));
      const lampM = lam("lampHead", () => ({ color: "#3d4048" })), bolt = lam("bolt", () => ({ color: "#6c6f76" }));
      for (const z of [15.3, -4.0, 34.0]) {
        b.add(cyl(0.16, 0.11, 7.4, 14), conc, at(2004.1, D0 + 0.16, z));
        bar(b, V(2004.1, D0 + 6.9, z), V(2002.8, D0 + 7.15, z), 0.05, M.pole);
        bx(2002.55, 6.95, z - 0.18, 2003.05, 7.15, z + 0.18, lampM, 2);
        for (const yy of [1.2, 3.0, 5.6]) for (const s2 of [-1, 1]) b.add(new THREE.SphereGeometry(0.025, 6, 4), bolt, at(2004.1 + s2 * 0.13, D0 + yy, z - 0.1));
        bx(2003.95, 2.3, z - 0.22, 2004.25, 2.75, z - 0.12, lam("poleBox", () => ({ color: "#5c6a5a" })));
      }
      for (const dy of [6.3, 6.55]) bar(b, V(2004.1, D0 + dy, -4.0), V(2004.1, D0 + dy - 0.35, 15.3), 0.012, M.pole), bar(b, V(2004.1, D0 + dy, 15.3), V(2004.1, D0 + dy - 0.3, 34.0), 0.012, M.pole);
      this.poleBulb = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.04, 0.28), this.bulbWarm); this.poleBulb.position.set(2002.8, D0 + 6.93, 15.3); this.poleBulb.layers.set(NOINK); R.add(this.poleBulb);
      const far = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.04, 0.28), this.bulbWarm); far.position.set(2002.8, D0 + 6.93, 34.0); far.layers.set(NOINK); R.add(far);
      // luzes reais
      for (const L of [this.poleLight, this.farLight, this.torch]) { L.castShadow = true; L.shadow.mapSize.set(1024, 1024); L.shadow.bias = -0.0004; L.shadow.camera.near = 0.2; R.add(L, L.target); }
      this.poleLight.position.set(2002.8, D0 + 6.85, 15.3); this.poleLight.target.position.set(2001.8, D0, 15.6);
      this.farLight.position.set(2002.8, D0 + 6.85, 34.0); this.farLight.target.position.set(2001.5, D0, 33.5);
    }
    { // ===== vídeo 20 — A VISITA =====
      // a maçaneta (alavanca) da porta da frente, com pivô no espelho
      const kb = new Batch(); kb.add(boxGeo(V(-0.015, -0.045, -0.02), V(0.015, 0.045, 0.0)), M.steel); kb.add(boxGeo(V(-0.01, -0.012, -0.075), V(0.11, 0.012, -0.045)), M.steel);
      kb.add(boxGeo(V(-0.008, -0.008, -0.045), V(0.008, 0.008, -0.02)), M.steel); kb.build(this.knob); this.knob.position.set(593.62, D0 + 1.01, 3.9); R.add(this.knob);
      bx(593.55, 1.48, 3.895, 593.65, 1.58, 3.91, M.steel);   // o olho mágico
      // a varanda do lado de fora da porta: piso, colunas, muretinha, luz amarela acesa em cima da porta, escuro atrás
      b.add(quadUp(591.5, 597.0, 4.4, 8.5, 4, 3, D0 + 0.03), M.concrete);
      const porch2 = lam("porchWall", () => ({ color: "#5d5866" }));
      bx(591.4, 0, 8.4, 597.1, 0.75, 8.6, porch2); bx(591.4, 0, 4.4, 591.6, 2.8, 8.6, porch2); bx(596.9, 0, 4.4, 597.1, 2.8, 8.6, porch2);
      bx(591.4, 2.8, 4.4, 597.1, 2.95, 8.6, lam("porchRoof", () => ({ color: "#3a3644" })));
      for (const x of [592.2, 596.0]) bx(x - 0.09, 0.75, 8.42, x + 0.09, 2.8, 8.58, M.white);
      b.add(quad(V(597.1, D0 + 0.75, 8.62), V(591.4, D0 + 0.75, 8.62), V(591.4, D0 + 2.8, 8.62), V(597.1, D0 + 2.8, 8.62)), lam("porchNight", () => ({ color: "#0b1024" })));
      // a noite atrás da varanda: quintal escuro e árvores em silhueta (sem céu aberto no olho mágico)
      b.add(quad(V(606, D0 - 0.5, 14), V(582, D0 - 0.5, 14), V(582, D0 + 9, 14), V(606, D0 + 9, 14)), lam("yardNight", () => ({ color: "#0a0f22" })));
      b.add(quadUp(582, 606, 8.6, 14, 6, 3, D0 + 0.02), lam("yardGrass", () => ({ color: "#1c2a26" })));
      for (const [x, z, r] of [[589, 12.5, 1.6], [599, 12.8, 1.9], [603.5, 12.2, 1.4]] as const) b.add(new THREE.IcosahedronGeometry(r, 1), lam("treeNight", () => ({ color: "#14201c" })), at(x, D0 + 2.6, z));
      bx(593.8, 2.4, 4.4, 594.4, 2.46, 4.55, M.pole);
      const pb = new THREE.Mesh(new THREE.SphereGeometry(0.09, 14, 10), this.bulbOn); pb.position.set(594.1, D0 + 2.36, 4.5); pb.layers.set(NOINK); R.add(pb);
      bx(593.1, 0, 5.0, 595.1, 0.02, 6.1, lam("doormat", () => ({ color: "#6a4a32" })));
      // O QUARTO (1000,0): chão de madeira, paredes azul-escuras, cama de solteiro, criado-mudo, janela com a rua na chuva, pôster
      b.add(quadUp(994, 1006, -4, 4.2, 6, 4, D0 + 0.02), lam("floorWoodHD", () => ({ map: stoneHD("floorWoodHD", ["#a4744c", "#9a6c46", "#ad7c52", "#93663f"], "#7d5536") })));
      const bw = lam("bedWall", () => ({ color: "#5f7fa8" }));
      bx(994, 0, 4.0, 1006, 3.0, 4.3, bw); bx(993.7, 0, -4, 994.0, 3.0, 4.3, bw); bx(1006, 0, -4, 1006.3, 3.0, 4.3, bw);
      b.add(boxGeo(V(994, D0 + 3.0, -4), V(1006, D0 + 3.15, 4.3), 0, true), lam("roomCeil", () => ({ color: "#cfc3ad" })));
      const sheet = lam("bedSheet", () => ({ color: "#e9eef5" })), blanket = lam("blanket", () => ({ map: ctex("blanketHD", 256, 256, (g) => { g.fillStyle = "#c4473b"; g.fillRect(0, 0, 256, 256); g.fillStyle = "#e8d6b0";
        for (let y = 0; y < 256; y += 64) g.fillRect(0, y + 26, 256, 12); for (let x = 0; x < 256; x += 64) g.fillRect(x + 26, 0, 12, 256); }) }));
      bx(997.6, 0, 1.9, 999.6, 0.32, 3.95, M.woodDark, 2); bx(997.65, 0.32, 1.95, 999.55, 0.5, 3.9, sheet, 3);
      bx(997.6, 0.5, 1.9, 999.6, 0.56, 3.15, blanket, 2); bx(997.6, 0.0, 1.88, 999.6, 0.5, 1.92, blanket);
      bx(997.85, 0.5, 3.35, 999.35, 0.66, 3.85, sheet, 6); bx(997.6, 0, 3.92, 999.6, 1.15, 4.0, M.woodDark, 2);
      bx(999.95, 0, 3.3, 1000.6, 0.55, 3.95, M.woodLight, 2); bx(999.93, 0.55, 3.28, 1000.62, 0.59, 3.97, M.woodDark);
      bx(996.0, 1.15, 4.0, 997.2, 2.25, 4.02, lam("bedWin", () => ({ color: "#0d1430" })));
      bx(995.95, 1.1, 3.98, 997.25, 1.16, 4.04, M.white); bx(995.95, 2.24, 3.98, 997.25, 2.3, 4.04, M.white); bx(996.57, 1.15, 3.98, 996.63, 2.25, 4.03, M.white);
      bx(995.95, 1.1, 3.98, 996.0, 2.3, 4.04, M.white); bx(997.2, 1.1, 3.98, 997.25, 2.3, 4.04, M.white);
      bx(1001.4, 1.3, 3.98, 1002.3, 2.5, 4.0, lam("poster", () => ({ map: ctex("posterHD", 256, 340, (g) => { g.fillStyle = "#24324f"; g.fillRect(0, 0, 256, 340); g.fillStyle = "#f3d35a"; g.beginPath(); g.arc(128, 140, 70, 0, 7); g.fill();
        g.fillStyle = "#e8eef8"; g.fillRect(40, 250, 176, 18); g.fillRect(70, 280, 116, 12); }) })));
      bx(1002.8, 0, 3.1, 1004.0, 0.75, 3.95, M.woodLight, 2); bx(1003.0, 0.75, 3.6, 1003.8, 0.78, 3.9, M.steel);
      b.add(quadUp(998.2, 1001.6, 0.4, 1.8, 1, 1, D0 + 0.03), lam("bedRug", () => ({ color: "#3f6f5a" })));
    }
    b.build(R);
  }

  private shotSun(id: number, s: ShotDef, L: LightPreset) {
    let v = this.sunCache.get(id);
    if (v) return v;
    let fx = 0, fz = 0;
    for (let f = s.a; f < s.b; f += 3) {
      const c = camAt(id, f), x = c.look[0] - c.pos[0], z = c.look[2] - c.pos[2], n = Math.hypot(x, z) || 1;
      fx += x / n; fz += z / n;
    }
    const n = Math.hypot(fx, fz) || 1; fx /= n; fz /= n;
    const az = THREE.MathUtils.degToRad(SUN_SHOT[id]?.az ?? L.az), el = THREE.MathUtils.degToRad(SUN_SHOT[id]?.el ?? L.el);
    const hx = fx * Math.cos(az) - fz * Math.sin(az), hz = fz * Math.cos(az) + fx * Math.sin(az);
    v = new THREE.Vector3(hx * Math.cos(el), Math.sin(el), hz * Math.cos(el)).normalize();
    this.sunCache.set(id, v);
    return v;
  }
  private actor(i: number) { while (this.actors.length <= i) this.actors.push(new Actor(this.root)); return this.actors[i]; }
  private fx(i: number) { while (this.fxs.length <= i) this.fxs.push(new Fx(this.root)); return this.fxs[i]; }

  private poseTower(id: number, t: number) {
    this.storm.visible = false;
    this.smash.visible = fallen(t);
    this.bathDoor.rotation.set(0, doorAt(id, t), 0);
    const w = windAt(id, t);
    for (const { g, ph } of this.wtrees) g.rotation.set(0, 0, -(w * 0.09 + w * 0.05 * Math.sin(t * 2.7 + ph) + w * 0.02 * Math.sin(t * 6.3 + ph * 2)));
    this.big.rotation.set(leanAt(id, t), 0, -(w * 0.035 + w * 0.025 * Math.sin(t * 2.2 + 0.4)) * (1 - 0.6 * Math.min(1, leanAt(id, t) / 0.2)));
    this.lamp.material = lampOn(id, t) ? this.bulbOn : this.glowOff;
    // vídeo 18
    this.drawTv(tvState(id, t), t, talkAt("tv", t));
    this.led.material = ledOn(id, t) ? this.ledOnM : this.glowOff;
    const v = vibAt(id, t); this.cushion.position.set(600.85 + v, D0 + 0.45 + Math.abs(v) * 0.4, 2.92); this.cushion.rotation.set(0, 0, v * 3);
    const w2 = windAt(id, t);
    for (const { g, ph } of this.corn) g.rotation.set(0, 0, w2 * (0.06 + 0.05 * Math.sin(t * 1.9 + ph) + 0.02 * Math.sin(t * 4.7 + ph * 1.7)));
    this.farmWin.visible = false;
    this.big.visible = false; this.cushion.visible = false;
    const ck = curtainAt(id, t); this.curtL.scale.set(0.25 + 0.8 * ck, 1, 1); this.curtR.scale.set(0.25 + 0.8 * ck, 1, 1);
    (this.roomWin.material as THREE.MeshLambertMaterial).color.set("#0c1226");
    this.knob.rotation.set(0, 0, id === 18 ? knobAt(t) : 0);
    // PILOTO: o poste que pisca e apaga, o do fundo aceso, a lanterna presa ao celular na sua mão
    const pk = poleAt(t); this.poleLight.intensity = 900 * pk; this.poleBulb.material = pk ? this.bulbWarm : this.glowOff;
    this.farLight.intensity = 700;
    const z = youZ(t); this.torch.intensity = torchOn(t) ? 1400 : 0; this.torch.position.set(1999.98, D0 + 1.2, z - 0.2); this.torch.target.position.set(...torchAim(t));
  }

  /** desenha a tela da TV: telejornal genérico com o apresentador falando e o relógio */
  private drawTv(st: TvState, t: number, talk: number) {
    const key = st + "|" + talk + "|" + (Math.floor(t * 1.5) % 2);
    if (key === this.tvKey) return; this.tvKey = key;
    const g = this.tvCv.getContext("2d")!, Wd = 1024, Hd = 576;
    g.save();
    if (st === "off") { g.fillStyle = "#0b0c10"; g.fillRect(0, 0, Wd, Hd); g.restore(); this.tvTex.needsUpdate = true; return; }
    const bg = g.createLinearGradient(0, 0, Wd, Hd); bg.addColorStop(0, "#14306e"); bg.addColorStop(1, "#0a1636"); g.fillStyle = bg; g.fillRect(0, 0, Wd, Hd);
    g.strokeStyle = "rgba(120,170,255,0.18)"; g.lineWidth = 3; for (let x = 560; x < Wd; x += 48) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x - 160, Hd); g.stroke(); }
    // tudo dentro da faixa central (x 270..754), que é o que aparece no 9:16
    // o apresentador (desenho simples, terno, gravata vermelha)
    const ax = 512, ay = 250;
    g.fillStyle = "#2b2f3a"; g.beginPath(); g.moveTo(ax - 150, Hd); g.quadraticCurveTo(ax - 140, ay + 110, ax, ay + 100); g.quadraticCurveTo(ax + 140, ay + 110, ax + 150, Hd); g.fill();
    g.fillStyle = "#f2f2f2"; g.beginPath(); g.moveTo(ax - 34, ay + 100); g.lineTo(ax, ay + 170); g.lineTo(ax + 34, ay + 100); g.fill();
    g.fillStyle = "#c8323a"; g.beginPath(); g.moveTo(ax - 10, ay + 108); g.lineTo(ax + 10, ay + 108); g.lineTo(ax + 14, ay + 190); g.lineTo(ax, ay + 205); g.lineTo(ax - 14, ay + 190); g.fill();
    g.fillStyle = "#e7b48e"; g.strokeStyle = "#241726"; g.lineWidth = 7; g.beginPath(); g.ellipse(ax, ay, 82, 92, 0, 0, 7); g.fill(); g.stroke();
    g.fillStyle = "#3a2a22"; g.beginPath(); g.ellipse(ax, ay - 58, 86, 44, 0, Math.PI, 2 * Math.PI); g.fill(); g.stroke();
    g.fillStyle = "#241726"; for (const sx of [-26, 26]) { g.beginPath(); g.ellipse(ax + sx, ay - 6, 8, 11, 0, 0, 7); g.fill(); }
    g.lineWidth = 6; for (const sx of [-26, 26]) { g.beginPath(); g.moveTo(ax + sx - 14, ay - 32); g.lineTo(ax + sx + 14, ay - 30); g.stroke(); }
    if (talk > 0.05) { g.fillStyle = "#5a1e28"; g.beginPath(); g.ellipse(ax, ay + 44, 16 + 5 * talk, 4 + 15 * talk, 0, 0, 7); g.fill(); g.stroke(); }
    else { g.beginPath(); g.moveTo(ax - 18, ay + 44); g.lineTo(ax + 18, ay + 42); g.stroke(); }
    // AO VIVO (esquerda) e relógio (direita), no alto da faixa central
    const blink = key.endsWith("1");
    g.fillStyle = "#d8272f"; g.fillRect(282, 26, 168, 52); g.fillStyle = "#ffffff"; g.font = "bold 34px Poppins, sans-serif"; g.textAlign = "left"; g.fillText("AO VIVO", 306, 64);
    if (blink) { g.beginPath(); g.arc(294, 52, 6, 0, 7); g.fill(); }
    const clock = st === "news58" ? "21:58" : "21:57";
    g.fillStyle = "rgba(0,0,0,0.7)"; g.fillRect(580, 22, 162, 62); g.fillStyle = "#ffd214"; g.font = "bold 48px Poppins, sans-serif"; g.textAlign = "center"; g.fillText(clock, 661, 70);
    // faixa de baixo em duas linhas curtas
    g.fillStyle = "#d8272f"; g.fillRect(0, Hd - 128, Wd, 128); g.fillStyle = "#ffffff"; g.font = "bold 44px Poppins, sans-serif";
    if (st === "news58") { g.fillText("FALTAM 2 MINUTOS", Wd / 2, Hd - 76); g.font = "bold 34px Poppins, sans-serif"; g.fillText("FIQUEM EM CASA", Wd / 2, Hd - 30); }
    else { g.fillText("NOITE LIVRE", Wd / 2, Hd - 76); g.font = "bold 34px Poppins, sans-serif"; g.fillText("DAS 22H ÀS 6H", Wd / 2, Hd - 30); }
    g.restore(); this.tvTex.needsUpdate = true;
  }

  update(id: number, f: number, cam: THREE.PerspectiveCamera, scene: THREE.Scene) {
    const t = f / FPS, s = SHOTS[id - 1], L = LIGHTS[s.light];
    const c = camAt(id, f);
    cam.position.set(...c.pos); cam.up.set(0, 1, 0); cam.lookAt(...c.look); cam.rotateZ(c.roll);
    cam.fov = c.fov; cam.near = 0.2; cam.far = 1500; cam.updateProjectionMatrix(); cam.updateMatrixWorld();
    const focus = V(...c.look), dist = cam.position.distanceTo(focus);
    cam.layers.enable(NOINK);
    const K = LOOK[s.light], sunDir = this.shotSun(id, s, L);
    this.hemi.color.set(L.sky); this.hemi.groundColor.set(L.ground); this.hemi.intensity = L.hemiI;
    this.sun.color.set(L.sunCol); this.sun.intensity = L.sunI;
    let Rr = THREE.MathUtils.clamp(dist * 1.15 + 7, 14, 110);
    if (s.light === "golden") Rr = Math.max(Rr, 40);
    this.sun.position.copy(focus).addScaledVector(sunDir, 260); this.sun.target.position.copy(focus);
    const sc = this.sun.shadow.camera;
    sc.left = -Rr; sc.right = Rr; sc.top = Rr; sc.bottom = -Rr; sc.near = 20; sc.far = 560; sc.updateProjectionMatrix();
    this.sun.shadow.bias = L.bias; this.sun.shadow.normalBias = L.normalBias * (Rr / 12);
    TONE.uLitCol.value.set(...L.lit); TONE.uShadeCol.value.set(...L.shade); TONE.uShadeLift.value.set(...L.lift);
    TONE.uLambert.value = L.lambert; TONE.uSideK.value = L.sideK; TONE.uTerm.value = L.term; TONE.uBounce.value.set(...LOOK[s.light].bounce); TONE.uSat.value = LOOK[s.light].sat;
    { // vídeo 16: o banheiro escurece quando o celular apaga; a sirene tinge a rua de vermelho
      const dk = darkAt(id, t);
      if (dk > 0) { const m = 1 - 0.74 * dk; TONE.uLitCol.value.multiplyScalar(m); TONE.uShadeCol.value.multiplyScalar(m); TONE.uShadeLift.value.multiplyScalar(1 - 0.75 * dk);
        if (tvOn(id, t)) { TONE.uLitCol.value.x *= 0.82; TONE.uLitCol.value.z += 0.1; TONE.uShadeLift.value.z += 0.03; } }
      const near = id === 13 ? 0.25 + 0.55 * clamp01((sirenX(t) + 95) / 72) : id === 12 ? 0.22 : id >= 22 ? 0.3 : 0;
      const sk = near * (id >= 22 ? 1 : sirenK(t)) * sirenPulse(t);
      if (sk > 0) { TONE.uLitCol.value.x += 0.3 * sk; TONE.uShadeLift.value.x += 0.06 * sk; TONE.uLitCol.value.z *= 1 - 0.15 * sk; }
    }
    CHAR.uCharTint.value.set(...L.charTint); CHAR.uCharShade.value = L.charShade; CHAR.uGrad.value = L.charGrad;
    CHAR.uBodyGrad.value = L.bodyGrad; CHAR.uSideTint.value.set(...L.sideTint);
    const su = this.skyMat.uniforms;
    K.sky.c.forEach((h, i) => untone(h, su["c" + i].value));
    const e = K.sky.e.map((deg) => THREE.MathUtils.degToRad(deg));
    su.e.value.set(e[1], e[2], e[3], e[4]);
    this.sky.position.copy(cam.position);
    untone(L.fog, this.fog.color); this.fog.near = L.fogNear; this.fog.far = L.fogFar * 1.4;
    scene.fog = this.fog; scene.background = null;
    this.sunDisc.visible = s.light === "golden";
    if (this.sunDisc.visible) {
      this.sunDisc.position.copy(cam.position).addScaledVector(sunDir, 900);
      this.sunDisc.scale.setScalar(2 * 900 * Math.tan(THREE.MathUtils.degToRad(1.7)));
    }
    for (let i = 0; i < this.clouds.length; i++) {
      const m = this.clouds[i];
      m.lookAt(cam.position.x, m.position.y, cam.position.z);
      (m.material as THREE.MeshBasicMaterial).map = this.cloudMaps[s.light][i % 4];
    }
    this.poseTower(id, t);
    // janelas: acesas no golden; no dia três voltam em onda da esquerda para a direita
    for (const g of this.glows) {
      const on = true; // vídeo 19: a rua com luz (o perigo é a noite, não o escuro)
      g.material = on ? ((g.geometry as THREE.BufferGeometry).type === "SphereGeometry" ? this.bulbOn : this.glowOn) : this.glowOff;
    }
    // ---- cast + effects ----
    const right = V(0, 0, 0).setFromMatrixColumn(cam.matrixWorld, 0);
    const st = stage(id, t, { pos: cam.position, right });
    this.frustum.setFromProjectionMatrix(this.m4.multiplyMatrices(cam.projectionMatrix, cam.matrixWorldInverse));
    const tint = s.light === "golden" ? "#ffcf9e" : "#ffffff";
    let ai = 0;
    const used: Actor[] = [];
    for (const p of st.places) {
      const sc2 = p.scale ?? 1;
      if (!this.frustum.intersectsSphere(this.sph.set(this.v.set(p.x, p.y + 1.1 * sc2, p.z), 3.5))) continue;
      const a = this.actor(ai++);
      const [w, h, k] = p.size ?? [300, 500, 0.5];
      a.r = this.pool.req(p.key, w, h, k, p.draw);
      a.mesh.visible = true;
      a.mesh.position.set(p.x, p.y, p.z);
      a.mesh.rotation.set(0, p.yaw ?? Math.atan2(cam.position.x - p.x, cam.position.z - p.z), p.roll ?? 0);
      a.mesh.scale.set(p.mirror ? -sc2 : sc2, sc2, sc2);
      if (a.mat.emissiveMap) a.mat.emissive.set(tint);
      a.mesh.castShadow = L.actorShadow;
      used.push(a);
    }
    for (let i = ai; i < this.actors.length; i++) this.actors[i].mesh.visible = false;
    let fi = 0;
    const fused: Fx[] = [];
    for (const p of st.fx) {
      if (!this.frustum.intersectsSphere(this.sph.set(this.v.set(p.x, p.y, p.z), Math.max(p.w, p.h)))) continue;
      const e2 = this.fx(fi++);
      e2.r = this.pool.req(p.key, p.cw, p.ch, 1, p.draw);
      e2.use(!!p.soft);
      e2.mesh.visible = true;
      e2.mesh.position.set(p.x, p.y, p.z);
      if (p.flat) e2.mesh.rotation.set(-Math.PI / 2, 0, p.rot ?? 0);
      else { e2.mesh.quaternion.copy(cam.quaternion); e2.mesh.rotateZ(p.rot ?? 0); }
      e2.mesh.scale.set(p.w, p.h, 1);
      fused.push(e2);
    }
    for (let i = fi; i < this.fxs.length; i++) this.fxs[i].mesh.visible = false;
    this.pool.flush();
    for (const a of used) a.bind();
    for (const e3 of fused) e3.bind();
    return focus;
  }
}
export type { V3 };
