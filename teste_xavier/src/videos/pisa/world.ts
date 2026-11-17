// The Piazza: lawn, marble paving, cathedral, baptistery, city wall, houses and hills, plus the tower built floor by
// floor as a kinematic chain (each floor sits on the top of the one below, leaning, the upper ones bent back).
// Sky, light rig, clouds and the character cards work exactly like the bridge short.
import * as THREE from "three";
import { Batch, boxGeo, V, lam, house, Kit, quad, tri } from "./build";
import { rep, ctex, stoneHD, cobbleHD, grassHD, cloudHD, roofHD, brick } from "./paint";
import { LIGHTS, LOOK, LightPreset } from "./lights";
import { TONE, CHAR, untone, twoTone } from "./shade";
import { NOINK } from "./ink";
import { Pool, Actor, Fx, stage } from "./cast";
import { FPS, D0, SHOTS, camAt, ShotDef, towerState, FLOOR_H, CURVE, V3 } from "./story";

export const loadKit = async (): Promise<Kit> => ({});

const discTex = () => ctex("sunDisc", 128, 128, (g) => {
  const gr = g.createRadialGradient(64, 64, 58, 64, 64, 64); gr.addColorStop(0, "rgba(255,255,255,1)"); gr.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = gr; g.fillRect(0, 0, 128, 128);
});
const SUN_SHOT: Record<number, { az?: number; el?: number }> = { 1: { az: 120 }, 2: { az: 110 }, 3: { az: 115 }, 5: { az: 140 }, 6: { az: 125 }, 4: { az: 125, el: 10 } };

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
  private cloudMaps: Record<"day" | "golden", THREE.Texture[]>;
  private clouds: THREE.Mesh[] = [];
  private floors: THREE.Group[] = [];
  private scaffold = new THREE.Group();
  private mudM: THREE.Mesh;
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
    this.cloudMaps = { day: [0, 1, 2, 3].map((k) => cloudHD(k, LOOK.day.cloud)), golden: [0, 1, 2, 3].map((k) => cloudHD(k, LOOK.golden.cloud)) };
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

    // ---- static piazza ----
    const b = new Batch();
    b.add(quadUp(-900, 900, -900, 900, 450, 450), M.grass);
    b.add(new THREE.CircleGeometry(12.5, 64).rotateX(-Math.PI / 2), M.pave, at(0, D0 + 0.02, 0));
    b.add(quadUp(-3.2, 3.2, -90, -12, 3, 39, D0 + 0.015), M.pave);
    b.add(quadUp(-120, 40, 30, 37, 80, 3.5, D0 + 0.015), M.pave);
    // cathedral (nave along x behind-left of the tower), transept, dome; striped marble, red roofs
    b.add(boxGeo(V(-92, D0, 12), V(-28, D0 + 20, 30), 8), M.band);
    b.add(boxGeo(V(-66, D0, 2), V(-54, D0 + 20, 40), 8), M.band);
    b.add(quad(V(-92, D0 + 20, 12), V(-28, D0 + 20, 12), V(-28, D0 + 26, 21), V(-92, D0 + 26, 21), 16, 2), M.roof);
    b.add(quad(V(-28, D0 + 20, 30), V(-92, D0 + 20, 30), V(-92, D0 + 26, 21), V(-28, D0 + 26, 21), 16, 2), M.roof);
    b.add(tri(V(-28, D0 + 20, 12), V(-28, D0 + 20, 30), V(-28, D0 + 26, 21)), M.band);
    b.add(cyl(6, 6, 8, 32), M.band, at(-60, D0 + 20, 21));
    b.add(new THREE.SphereGeometry(6.2, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2), M.dome, at(-60, D0 + 28, 21));
    for (let i = 0; i < 12; i++) b.add(cyl(0.35, 0.3, 14, 8), M.marble, at(-28.6, D0, 13 + i * 1.5)); // facade columns
    // baptistery further left
    b.add(cyl(17, 17, 22, 64), M.band, at(-140, D0, 20));
    b.add(new THREE.ConeGeometry(15, 14, 48).translate(0, 7, 0), M.dome, at(-140, D0 + 22, 20));
    // city wall behind, with crenellations, houses and hills beyond it
    b.add(boxGeo(V(-300, D0, 70), V(300, D0 + 9, 73), 3), M.wall);
    for (let x = -300; x < 300; x += 3) b.add(boxGeo(V(x, D0 + 9, 70), V(x + 1.6, D0 + 10.4, 73)), M.wall);
    let hs = 1;
    for (let x = -260; x < 260; x += 11) { const h = [9, 11, 13][hs % 3]; house(b, x, 84 + (hs % 3) * 2, Math.PI, 10, 8, h, hs); hs++; }
    for (let x = -260; x < 260; x += 13) { house(b, x + 4, 100, Math.PI, 12, 8, 12 + (hs % 2) * 3, hs); hs++; }
    // houses along the sides of the field
    for (let z = -120; z < 60; z += 11) { house(b, 70, z, -Math.PI / 2, 10, 8, 10 + (hs % 3) * 1.5, hs); hs++; house(b, -190, z, Math.PI / 2, 10, 8, 10, hs); hs++; }
    ([[-360, 300, 200, 60, 130], [160, 420, 260, 70, 150], [460, 180, 180, 50, 140], [-480, -60, 200, 46, 150], [520, -120, 170, 44, 130]] as const)
      .forEach(([x, z, sx, sy, sz], i) => b.add(new THREE.SphereGeometry(1, 28, 14, 0, Math.PI * 2, 0, Math.PI / 2), hm[i % 3], new THREE.Matrix4().compose(V(x, D0 - 2, z), new THREE.Quaternion(), V(sx, sy, sz))));
    // trees along the wall and the edges
    let ts = 0;
    for (let x = -180; x <= 60; x += 9) { tree(b, x + (ts % 3), 60 + (ts % 2) * 3, 1.0 + (ts % 3) * 0.15, M, ts); ts++; }
    for (let z = -100; z < 50; z += 10) { tree(b, 55 + (ts % 2) * 2, z, 1.1, M, ts); ts++; }
    b.build(R);

    // ---- mud where the tower sinks (shots 2-4) ----
    this.mudM = new THREE.Mesh(new THREE.CircleGeometry(9, 48).rotateX(-Math.PI / 2), new THREE.MeshLambertMaterial({ map: mud(), transparent: true, depthWrite: false }));
    twoTone(this.mudM.material as THREE.MeshLambertMaterial);
    this.mudM.position.set(5.5, D0 + 0.03, 0); this.mudM.receiveShadow = true; R.add(this.mudM);

    // ---- the tower, floor by floor ----
    for (let k = 0; k < FLOOR_H.length; k++) {
      const fb = new Batch(), g = new THREE.Group();
      floorGeo(fb, k, M); fb.build(g); g.matrixAutoUpdate = false;
      this.floors.push(g); R.add(g);
    }
    // scaffolding around the two-storey stump
    const sb = new Batch();
    for (let i = 0; i < 14; i++) { const a = (i / 14) * Math.PI * 2; sb.add(cyl(0.12, 0.12, 20, 6), M.wood, at(Math.cos(a) * 9.2, D0, Math.sin(a) * 9.2)); }
    for (const y of [5, 10, 15, 19.5]) for (let i = 0; i < 14; i++) {
      const a0 = (i / 14) * Math.PI * 2, a1 = ((i + 1) / 14) * Math.PI * 2;
      const p0 = V(Math.cos(a0) * 9.2, y, Math.sin(a0) * 9.2), p1 = V(Math.cos(a1) * 9.2, y, Math.sin(a1) * 9.2);
      const g = new THREE.BoxGeometry(0.12, 0.12, p0.distanceTo(p1));
      g.lookAt(p1.clone().sub(p0)); g.translate((p0.x + p1.x) / 2, y, (p0.z + p1.z) / 2);
      sb.add(g, M.wood);
    }
    sb.build(this.scaffold); R.add(this.scaffold);
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

  /** pose the floors: each one stands on the top centre of the one below, its axis tilted by the lean minus the curve */
  private poseTower(id: number, t: number) {
    const st = towerState(id, t);
    const p = V(0, D0 - st.sink, 0), q = new THREE.Quaternion(), one = V(1, 1, 1), up = V(0, 1, 0);
    for (let k = 0; k < this.floors.length; k++) {
      const g = this.floors[k];
      g.visible = k < st.floors;
      const deg = st.tilt - (k >= 4 ? CURVE * (k - 3) : 0);
      q.setFromAxisAngle(V(0, 0, 1), -THREE.MathUtils.degToRad(deg));
      g.matrix.compose(p, q, one); g.matrixWorldNeedsUpdate = true;
      p.add(up.set(0, FLOOR_H[k], 0).applyQuaternion(q));
    }
    this.scaffold.visible = st.scaffold;
    this.mudM.visible = id >= 2 && id <= 4;
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
