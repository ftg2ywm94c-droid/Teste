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
import { FPS, D0, SHOTS, camAt, ShotDef, FLOOR_H, V3, W, windAt, leanAt, lampOn, fallen, doorAt, darkAt, sirenK, sirenX, sirenPulse, clamp01, tvState, tvOn, ledOn, vibAt, TvState } from "./story";

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
    { const gap = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.05, 0.02), new THREE.MeshBasicMaterial({ color: new THREE.Color(1.4, 1.7, 2.6) })); gap.position.set(594.1, D0 + 0.045, 3.975); gap.layers.set(NOINK); R.add(gap); } bx(593.62, 0.98, 3.86, 593.72, 1.04, 3.92, M.steel);
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
      bx(597.4, 0, -0.3, 598.0, 0.42, 0.15, lam("consoleBox", () => ({ color: "#e9edf3" })), 1); bx(597.38, 0.3, -0.32, 598.02, 0.34, 0.17, lam("boxBlue", () => ({ color: "#2f5fb3" })));
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
    this.drawTv(tvState(id, t), t);
    this.led.material = ledOn(id, t) ? this.ledOnM : this.glowOff;
    const v = vibAt(id, t); this.cushion.position.set(600.85 + v, D0 + 0.45 + Math.abs(v) * 0.4, 2.92); this.cushion.rotation.set(0, 0, v * 3);
    const w2 = windAt(id, t);
    for (const { g, ph } of this.corn) g.rotation.set(0, 0, w2 * (0.06 + 0.05 * Math.sin(t * 1.9 + ph) + 0.02 * Math.sin(t * 4.7 + ph * 1.7)));
    this.farmWin.visible = id === 21;
    (this.roomWin.material as THREE.MeshLambertMaterial).color.set(id === 4 ? "#bfe0ff" : "#0c1226");
  }

  /** desenha a tela da TV (só redesenha quando o estado muda; o chiado muda a cada quadro) */
  private drawTv(st: TvState, t: number) {
    const key = st === "static" ? st + Math.floor(t * 30) : st === "p2" ? st + (Math.floor(t * 2) % 2) : st;
    if (key === this.tvKey) return; this.tvKey = key;
    const g = this.tvCv.getContext("2d")!, Wd = 1024, Hd = 576;
    g.save();
    if (st === "off") { const gr = g.createLinearGradient(0, 0, Wd, Hd); gr.addColorStop(0, "#1b1d24"); gr.addColorStop(0.45, "#0b0c10"); gr.addColorStop(1, "#050507"); g.fillStyle = gr; g.fillRect(0, 0, Wd, Hd);
      g.fillStyle = "rgba(255,255,255,0.05)"; g.beginPath(); g.moveTo(80, 0); g.lineTo(300, 0); g.lineTo(120, Hd); g.lineTo(-100, Hd); g.fill(); }
    else if (st === "static") { const im = g.createImageData(Wd / 4, Hd / 4); let sd = Math.floor(t * 30) * 7919 + 1;
      for (let i = 0; i < im.data.length; i += 4) { sd = (sd * 16807) % 2147483647; const v = 40 + (sd % 200); im.data[i] = v * 0.85; im.data[i + 1] = v * 0.9; im.data[i + 2] = v; im.data[i + 3] = 255; }
      const c2 = document.createElement("canvas"); c2.width = Wd / 4; c2.height = Hd / 4; c2.getContext("2d")!.putImageData(im, 0, 0); g.imageSmoothingEnabled = false; g.drawImage(c2, 0, 0, Wd, Hd); }
    else if (st === "install") {
      // arte genérica de mundo aberto ao entardecer (nada de logo, personagem ou cidade de jogo real)
      const sky = g.createLinearGradient(0, 0, 0, Hd); sky.addColorStop(0, "#2b2f6e"); sky.addColorStop(0.45, "#c8577a"); sky.addColorStop(0.75, "#f2a35c"); sky.addColorStop(1, "#f7c873"); g.fillStyle = sky; g.fillRect(0, 0, Wd, Hd);
      g.fillStyle = "#ffe6a0"; g.beginPath(); g.arc(560, 330, 70, 0, 7); g.fill();
      g.fillStyle = "#4a2f5c"; g.beginPath(); g.moveTo(0, 400); for (let x = 0; x <= Wd; x += 64) g.lineTo(x, 380 - 50 * Math.sin(x * 0.007) - 25 * Math.sin(x * 0.019)); g.lineTo(Wd, Hd); g.lineTo(0, Hd); g.fill();
      g.fillStyle = "#2a1c38"; g.beginPath(); g.moveTo(420, Hd); g.lineTo(505, 400); g.lineTo(525, 400); g.lineTo(640, Hd); g.fill();
      g.fillStyle = "rgba(0,0,0,0.6)"; g.fillRect(0, Hd - 150, Wd, 150); g.textAlign = "center";
      g.fillStyle = "#ffffff"; g.font = "bold 36px Poppins, sans-serif"; g.fillText("INSTALANDO…", 512, Hd - 100);
      g.fillStyle = "rgba(255,255,255,0.25)"; g.fillRect(312, Hd - 82, 400, 18); g.fillStyle = "#ffd214"; g.fillRect(312, Hd - 82, 396, 18);
      g.fillStyle = "#ffd214"; g.font = "bold 44px Poppins, sans-serif"; g.fillText("99%", 512, Hd - 22);
      g.fillStyle = "rgba(0,0,0,0.5)"; g.fillRect(436, 22, 152, 58); g.fillStyle = "#ffffff"; g.font = "bold 40px Poppins, sans-serif"; g.fillText("03:12", 512, 66); }
    else { // glow / p2: tela azul-escura acesa
      const gr = g.createRadialGradient(Wd / 2, Hd / 2, 40, Wd / 2, Hd / 2, 620); gr.addColorStop(0, "#1f3f8f"); gr.addColorStop(1, "#060c24"); g.fillStyle = gr; g.fillRect(0, 0, Wd, Hd);
      if (st === "p2") { const blink = key.endsWith("1");
        g.strokeStyle = "#ffffff"; g.lineWidth = 10; g.lineJoin = "round"; // controle genérico
        g.beginPath(); g.moveTo(420, 150); g.lineTo(604, 150); g.quadraticCurveTo(660, 150, 676, 220); g.lineTo(690, 280); g.quadraticCurveTo(700, 320, 660, 316); g.quadraticCurveTo(620, 290, 590, 262);
        g.lineTo(434, 262); g.quadraticCurveTo(404, 290, 364, 316); g.quadraticCurveTo(324, 320, 334, 280); g.lineTo(348, 220); g.quadraticCurveTo(364, 150, 420, 150); g.stroke();
        g.fillStyle = "#ffffff"; g.font = "bold 46px Poppins, sans-serif"; g.textAlign = "center"; g.fillText("2", 512, 228);
        g.font = "bold 64px Poppins, sans-serif"; g.fillText("JOGADOR 2", 512, 410); g.font = "bold 40px Poppins, sans-serif"; g.fillStyle = "#9fe0ff"; g.fillText("CONECTADO", 512, 468);
        g.fillStyle = blink ? "#3cff7a" : "#1a7a3c"; g.beginPath(); g.arc(380, 454, 12, 0, 7); g.fill(); }
    }
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
      const on = false; // apagão: a rua inteira sem luz
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
