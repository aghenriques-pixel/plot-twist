// --- 3D rooms (specs/scene-3d.md, specs/entrega-2359.md) --------------------------------------
//
// A place with a 3D room (data.world, from world3d.py) is drawn here with Three.js. The character
// is seen from behind (third person) and walks anywhere in the room. Walking up to a thing and
// pressing E (or clicking it) uses it exactly like a 2D spot: a look shows its text, a talk its
// choices, a keypad asks for the code, and the action goes to Python. Python decides everything;
// this file only draws, moves the character and sends what the player chose.
//
// This file is added after scene_view.js in the same script (app.py), so it uses el(), Sound,
// speak(), loadSettings(), rememberKeys() and interactions() from there. Three.js is a static
// file (static/), loaded once. The rooms look like Nova SBE: white walls, dark wooden floors,
// lines of LED light, and the terrace over the sea.

const THREE_URL = "app/static/three.module.min.js";
const WALK_SPEED = 3.2; // metres per second
const REACH = 1.6; // how close the character must be to use a thing
const HERO_RADIUS = 0.3;

// Loaded once per page; every room after the first starts at once
function loadThree() {
  globalThis.__forbiddenArchiveThree ??= import(new URL(THREE_URL, document.baseURI).href);
  return globalThis.__forbiddenArchiveThree;
}

function canDraw3D() {
  if (globalThis.__forbiddenArchiveWebGL === undefined) {
    try {
      const canvas = document.createElement("canvas");
      globalThis.__forbiddenArchiveWebGL = !!(canvas.getContext("webgl2") || canvas.getContext("webgl"));
    } catch {
      globalThis.__forbiddenArchiveWebGL = false;
    }
  }
  return globalThis.__forbiddenArchiveWebGL;
}

// A 3D room wherever Python sent one (endings and dangers included), if the browser can draw it
function wants3D(data) {
  return !!data.world && loadSettings().view3d && canDraw3D();
}

// Keys held down right now, for walking in 3D
const MOVE_KEYS = {
  ArrowUp: [0, -1], w: [0, -1],
  ArrowDown: [0, 1], s: [0, 1],
  ArrowLeft: [-1, 0], a: [-1, 0],
  ArrowRight: [1, 0], d: [1, 0],
};
// "W" and "w" are the same key (Shift or Caps Lock)
const moveKey = (key) => (key.length === 1 ? key.toLowerCase() : key);

// The 3D room. Returns the same keyboard handles as the 2D picture (scene_view.js gameKeys),
// plus move3d for walking in every direction. While Three.js loads, the handles do nothing; if it
// cannot load, the 2D picture is drawn instead and the handles pass on to it.
function buildRoom3D(stage, data, setTriggerValue) {
  let inner = null; // the handles of whatever is drawn: the 3D room, or the 2D picture as a fallback
  stage.classList.add("three", data.world.camera);
  if (data.world.mood) stage.classList.add(`mood-${data.world.mood}`);
  const loading = el("div", "loading3d", "…");
  stage.append(loading);
  loadThree()
    .then((THREE) => {
      if (!stage.isConnected) return;
      loading.remove();
      inner = drawRoom(THREE, stage, data, setTriggerValue);
    })
    .catch((error) => {
      console.warn("3D room unavailable, showing the 2D picture", error);
      if (!stage.isConnected) return;
      stage.className = "stage";
      stage.innerHTML = "";
      inner = buildPicture(stage, data, setTriggerValue);
    });
  return {
    startWalking: (direction, key) => inner?.startWalking(direction, key),
    stopWalking: (key) => inner?.stopWalking(key),
    useNearest: () => inner?.useNearest(),
    move3d: (key) => (inner?.move3d ? inner.move3d(key) : false),
  };
}

// --- One renderer for the whole page: made once, its canvas moved into each new room ----------

function sharedRenderer(THREE) {
  let shared = globalThis.__forbiddenArchive3D;
  if (!shared) {
    const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
    renderer.setPixelRatio(Math.min(globalThis.devicePixelRatio || 1, 1.75));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFShadowMap;
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.1;
    renderer.domElement.className = "room3d";
    shared = { renderer, active: null, last: performance.now(), slow: 0, frames: 0, level: 0 };
    // A slow computer (the demo laptop on a projector): after 2 seconds of slow frames the picture
    // is drawn with fewer pixels, then without shadows. Fast computers never notice.
    const lighter = () => {
      shared.level += 1;
      if (shared.level === 1) renderer.setPixelRatio(1);
      if (shared.level === 2) renderer.setPixelRatio(0.75);
      if (shared.level === 3) {
        renderer.shadowMap.enabled = false;
        shared.active?.scene.traverse((o) => o.material && (o.material.needsUpdate = true));
      }
      globalThis.dispatchEvent(new Event("resize"));
    };
    // One animation loop for the page: it draws whichever room is on the screen
    const frame = (now) => {
      requestAnimationFrame(frame);
      // Up to a quarter of a second per frame: a slow computer draws fewer frames, but the
      // character still walks at the same speed (update() splits long frames into short steps)
      const dt = Math.min(0.25, (now - shared.last) / 1000);
      shared.last = now;
      const room = shared.active;
      if (!room || !renderer.domElement.isConnected) return;
      room.update(dt, now / 1000);
      renderer.render(room.scene, room.camera);
      if (shared.level < 3) {
        shared.frames += 1;
        if (dt > 1 / 30) shared.slow += 1;
        if (shared.frames >= 120) {
          if (shared.slow > 60) lighter();
          shared.frames = shared.slow = 0;
        }
      }
    };
    requestAnimationFrame(frame);
    globalThis.__forbiddenArchive3D = shared;
  }
  return shared;
}

// Frees the GPU memory of a room that is no longer shown
function disposeRoom(room) {
  room.scene.traverse((object) => {
    object.geometry?.dispose();
    const materials = Array.isArray(object.material) ? object.material : object.material ? [object.material] : [];
    for (const material of materials) {
      material.map?.dispose();
      material.emissiveMap?.dispose();
      material.dispose();
    }
  });
}

// --- Textures drawn on a canvas (no image files) ------------------------------------------------

function canvasTexture(THREE, width, height, draw) {
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  draw(canvas.getContext("2d"), width, height);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = 4;
  return texture;
}

function shade(hex, amount) {
  // amount > 0 lightens, < 0 darkens (hex "#rrggbb")
  const n = parseInt(hex.slice(1), 16);
  const mix = (c) => Math.round(amount >= 0 ? c + (255 - c) * amount : c * (1 + amount));
  const r = mix(n >> 16);
  const g = mix((n >> 8) & 255);
  const b = mix(n & 255);
  return `#${((1 << 24) | (r << 16) | (g << 8) | b).toString(16).slice(1)}`;
}

// Text on a canvas: lines in a box, for boards, signs and screens
function textTexture(THREE, lines, options = {}) {
  const { width = 512, height = 256, background = "#ffffff", color = "#1a1a1a", font = "bold 44px sans-serif",
    align = "center", padding = 30, lineHeight = 1.25 } = options;
  return canvasTexture(THREE, width, height, (g, w, h) => {
    g.fillStyle = background;
    g.fillRect(0, 0, w, h);
    g.fillStyle = color;
    g.font = font;
    g.textAlign = align;
    g.textBaseline = "middle";
    const size = parseInt(font.match(/(\d+)px/)[1], 10) * lineHeight;
    const top = h / 2 - ((lines.length - 1) * size) / 2;
    lines.forEach((line, i) => g.fillText(line, align === "left" ? padding : w / 2, top + i * size));
  });
}

// Floors: dark oak planks (the library), light grey lino (the classrooms), big sandy tiles (the
// terrace). One texture covers 4 x 4 metres.
function floorTexture(THREE, kind, colour) {
  return canvasTexture(THREE, 512, 512, (g, w, h) => {
    g.fillStyle = colour;
    g.fillRect(0, 0, w, h);
    if (kind === "tiles") {
      // Damp patches and lighter stains, then the joints of 1-metre tiles
      for (let i = 0; i < 26; i++) {
        g.fillStyle = i % 3 ? `rgba(70,45,20,${0.04 + (i % 4) * 0.02})` : "rgba(255,240,210,0.07)";
        g.beginPath();
        g.ellipse((i * 157) % w, (i * 83) % h, 40 + (i % 5) * 30, 25 + (i % 3) * 20, i, 0, Math.PI * 2);
        g.fill();
      }
      g.strokeStyle = shade(colour, -0.22);
      g.lineWidth = 2;
      for (let x = 0; x <= w; x += 128) g.strokeRect(x, 0, 128, h);
      for (let y = 0; y <= h; y += 128) g.strokeRect(0, y, w, 128);
      return;
    }
    if (kind === "lino") {
      for (let i = 0; i < 6000; i++) {
        g.fillStyle = shade(colour, Math.random() * 0.08 - 0.04);
        g.fillRect(Math.random() * w, Math.random() * h, 2, 2);
      }
      return;
    }
    if (kind === "wood") {
      for (let y = 0; y < h; y += 32) {
        const offset = (y / 32) % 2 ? 0 : 160;
        for (let x = -offset; x < w; x += 320) {
          g.fillStyle = shade(colour, (Math.sin(x * 7 + y) * 0.5 + 0.5) * 0.12 - 0.05);
          g.fillRect(x + 1, y + 1, 318, 30);
          g.strokeStyle = shade(colour, -0.4);
          g.lineWidth = 1;
          g.strokeRect(x + 0.5, y + 0.5, 320, 32);
        }
      }
    } else if (kind === "carpet") {
      for (let i = 0; i < 9000; i++) {
        g.fillStyle = shade(colour, Math.random() * 0.12 - 0.06);
        g.fillRect(Math.random() * w, Math.random() * h, 2, 2);
      }
    } else {
      // concrete slabs with damp patches
      for (let i = 0; i < 40; i++) {
        g.fillStyle = `rgba(0,0,0,${Math.random() * 0.06})`;
        g.beginPath();
        g.arc(Math.random() * w, Math.random() * h, 20 + Math.random() * 90, 0, Math.PI * 2);
        g.fill();
      }
      g.strokeStyle = shade(colour, -0.25);
      g.lineWidth = 2;
      for (let x = 0; x <= w; x += 256) g.strokeRect(x, 0, 256, h);
      for (let y = 0; y <= h; y += 256) g.strokeRect(0, y, w, 256);
    }
  });
}

// --- The room ---------------------------------------------------------------------------------

// Kinds of things the character walks around (their outline on the floor is an obstacle)
// (a thing with its own outlines, like a curved row of desks, gives those instead)
// Tall things that may stand between the camera and the character: they fade while they do
const SEE_THROUGH = new Set(["column", "staircase", "bookshelf", "olive_tree", "street_lamp", "snack_machine", "lockers", "window_wall", "lectern"]);

const SOLID = new Set([
  "tiago_sleeping", "chair_coat", "lockers", "snack_machine", "staircase", "bookshelf", "beanbag", "lectern",
  "round_table", "counter", "long_table", "picnic_table", "bistro_set", "street_lamp", "socket_post",
  "sign_post", "guard", "column", "sofa", "atrium", "olive_tree", "bin",
]);

function drawRoom(THREE, stage, data, setTriggerValue) {
  const world = data.world;
  const [W, D] = world.size;
  const H = world.height;
  const style = world.style;
  const palette = style.palette;
  const outdoor = !!style.outdoor;
  const watching = world.camera === "cctv";
  const ending = world.camera === "ending";
  // The main menu's background: the room with nobody in it, the camera circling slowly
  const menuView = world.camera === "menu";
  const shared = sharedRenderer(THREE);
  const { renderer } = shared;
  if (shared.active) disposeRoom(shared.active);
  shared.active = null;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(52, 2, 0.1, 400);

  const material = (color, options = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.75, metalness: 0.05, ...options });
  const box = (w, h, d, color, options = {}) => new THREE.Mesh(new THREE.BoxGeometry(w, h, d), material(color, options));
  const cylinder = (rTop, rBottom, h, color, options = {}, segments = 20) =>
    new THREE.Mesh(new THREE.CylinderGeometry(rTop, rBottom, h, segments), material(color, options));
  const shadowy = (object) => {
    object.traverse((child) => {
      if (child.isMesh && !child.material.transparent) {
        child.castShadow = true;
        child.receiveShadow = true;
      }
    });
    return object;
  };

  // --- Floor, walls, ceiling, sky ---
  const floorMap = floorTexture(THREE, style.floor, palette.floor);
  floorMap.wrapS = floorMap.wrapT = THREE.RepeatWrapping;
  const floorSize = outdoor ? [W + 30, D + 30] : [W, D + 8];
  floorMap.repeat.set(floorSize[0] / 4, floorSize[1] / 4);
  const floor = new THREE.Mesh(
    new THREE.PlaneGeometry(...floorSize),
    material("#ffffff", { map: floorMap, roughness: style.floor === "wood" ? 0.45 : 0.9 })
  );
  floor.rotation.x = -Math.PI / 2;
  floor.position.z = outdoor ? 0 : 4; // indoors it goes on past the open front, under the camera
  floor.receiveShadow = true;
  scene.add(floor);

  const lamps = []; // lights that can flicker
  if (outdoor) {
    buildSky(THREE, scene, W, D);
  } else {
    scene.background = new THREE.Color("#0b0a12");
    scene.fog = new THREE.Fog("#0b0a12", 16, 34);
    const wall = (width, repeat) =>
      new THREE.Mesh(new THREE.PlaneGeometry(width, H), material(palette.wall, { roughness: 0.92 }));
    const back = wall(W);
    back.position.set(0, H / 2, -D / 2);
    const left = wall(D);
    left.rotation.y = Math.PI / 2;
    left.position.set(-W / 2, H / 2, 0);
    const right = wall(D);
    right.rotation.y = -Math.PI / 2;
    right.position.set(W / 2, H / 2, 0);
    for (const w of [back, left, right]) {
      w.receiveShadow = true;
      scene.add(w);
    }
    // A dark skirting board along the walls
    const skirt = box(W, 0.12, 0.04, "#2b2b2b");
    skirt.position.set(0, 0.06, -D / 2 + 0.02);
    scene.add(skirt);
    for (const side of [-1, 1]) {
      const s = box(0.04, 0.12, D, "#2b2b2b");
      s.position.set(side * (W / 2 - 0.02), 0.06, 0);
      scene.add(s);
    }
    // The ceiling: white perforated panels (all of Nova SBE), maybe with an opening (the staircase
    // goes up through it to a lit floor above)
    const perforated = canvasTexture(THREE, 256, 256, (g, w, h) => {
      g.fillStyle = "#f1f0ec";
      g.fillRect(0, 0, w, h);
      g.fillStyle = "rgba(0,0,0,0.10)";
      for (let y = 4; y < h; y += 8) for (let x = (y % 16) / 2 + 4; x < w; x += 8) g.fillRect(x, y, 2, 2);
      g.fillStyle = "rgba(0,0,0,0.12)";
      g.fillRect(0, 0, w, 2);
      g.fillRect(0, 0, 2, h);
    });
    perforated.wrapS = perforated.wrapT = THREE.RepeatWrapping;
    const ceilingPiece = (x1, x2, z1, z2) => {
      if (x2 - x1 < 0.01 || z2 - z1 < 0.01) return;
      const map = perforated.clone();
      map.repeat.set((x2 - x1) / 1.2, (z2 - z1) / 1.2);
      map.needsUpdate = true;
      const piece = new THREE.Mesh(new THREE.PlaneGeometry(x2 - x1, z2 - z1), material("#ffffff", { map, roughness: 1 }));
      piece.rotation.x = Math.PI / 2;
      piece.position.set((x1 + x2) / 2, H, (z1 + z2) / 2);
      scene.add(piece);
    };
    const front = D / 2 + 8;
    if (style.opening) {
      const [ox1, ox2, oz1, oz2] = style.opening;
      ceilingPiece(-W / 2, ox1, -D / 2, front);
      ceilingPiece(ox2, W / 2, -D / 2, front);
      ceilingPiece(ox1, ox2, -D / 2, oz1);
      ceilingPiece(ox1, ox2, oz2, front);
      // The floor above: white walls round the opening, a bright ceiling, a glass balustrade
      const up = 3.4;
      for (const [w, d, x, z, turn] of [[ox2 - ox1, 0, (ox1 + ox2) / 2, oz1, 0], [ox2 - ox1, 0, (ox1 + ox2) / 2, oz2, Math.PI], [oz2 - oz1, 0, ox1, (oz1 + oz2) / 2, Math.PI / 2], [oz2 - oz1, 0, ox2, (oz1 + oz2) / 2, -Math.PI / 2]]) {
        const side = new THREE.Mesh(new THREE.PlaneGeometry(w, up), material("#f7f6f2", { roughness: 0.9, side: THREE.DoubleSide }));
        side.position.set(x, H + up / 2, z);
        side.rotation.y = turn;
        scene.add(side);
      }
      const top = new THREE.Mesh(new THREE.PlaneGeometry(ox2 - ox1, oz2 - oz1), new THREE.MeshBasicMaterial({ color: "#fdfbf4" }));
      top.rotation.x = Math.PI / 2;
      top.position.set((ox1 + ox2) / 2, H + up, (oz1 + oz2) / 2);
      scene.add(top);
      const upLight = new THREE.PointLight("#fff6e0", 12, 8, 1.4);
      upLight.position.set((ox1 + ox2) / 2, H + up - 0.4, (oz1 + oz2) / 2);
      scene.add(upLight);
      const rim = box(ox2 - ox1, 0.35, 0.12, "#e9e8e3");
      rim.position.set((ox1 + ox2) / 2, H - 0.17, oz2);
      scene.add(rim);
    } else {
      ceilingPiece(-W / 2, W / 2, -D / 2, front);
    }
    if (style.lights === "lines") {
      // Long lines of LED light, slightly askew, like the library
      for (let z = -D / 2 + 1.2; z < D / 2; z += 2.2) {
        for (const half of [-1, 1]) {
          const line = box(W * 0.36, 0.03, 0.05, "#ffffff", { emissive: palette.light, emissiveIntensity: 2.5 });
          line.position.set(half * W * 0.26, H - 0.02, z + half * 0.4);
          line.rotation.y = 0.14;
          scene.add(line);
        }
      }
    }
    // Light from the ceiling: a few warm point lights spread over the room
    for (let x = -W / 2 + W / 6; x < W / 2; x += W / 3) {
      for (const z of [-D / 4, D / 4]) {
        const light = new THREE.PointLight(palette.light, world.dim ? 3 : 10, 10, 1.4);
        light.position.set(x, H - 0.3, z);
        scene.add(light);
        lamps.push({ light, base: light.intensity, flicker: 3 + Math.random() * 12 });
      }
    }
    if (style.windows) buildWindows(THREE, scene, W, D, H, style.windows);
  }

  // A soft fill and a key light for the shadows
  scene.add(new THREE.HemisphereLight(outdoor ? "#7d8fc8" : "#ffffff", outdoor ? "#1c1a26" : "#3a3330", outdoor ? 0.9 : world.dim ? 0.35 : 1.0));
  const key = new THREE.DirectionalLight(outdoor ? "#b9c8ff" : "#fff6e8", outdoor ? 1.1 : world.dim ? 0.3 : 1.2);
  key.position.set(outdoor ? -6 : -4, 12, outdoor ? -10 : 8);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  Object.assign(key.shadow.camera, { left: -W / 2 - 2, right: W / 2 + 2, top: D, bottom: -D, near: 1, far: 40 });
  key.shadow.bias = -0.0008;
  key.shadow.normalBias = 0.02;
  scene.add(key);

  // --- The things in the room, from world3d.py ---
  const obstacles = []; // outlines on the floor the character walks around: [minX, maxX, minZ, maxZ]
  const usable = []; // things the character can use
  const animated = []; // little things that move every frame: (dt, time, heroPosition) => {}
  const context = { THREE, box, cylinder, material, palette, animated, data, W, D, H, world };
  const lookOf = (thing) => (thing.look !== null && thing.look !== undefined ? data.looks[thing.look] : null);
  const later = []; // things placed next to the character once it exists (the guard who caught you)
  const tall = []; // things that fade when they hide the character

  for (const thing of world.things) {
    const group = new THREE.Group();
    const [x, z] = thing.at;
    group.position.set(x, 0, z);
    if (thing.wall === "left") group.rotation.y = Math.PI / 2;
    if (thing.wall === "right") group.rotation.y = -Math.PI / 2;
    if (thing.turn !== undefined) group.rotation.y = thing.turn;
    const build = THINGS[thing.kind];
    // The words on it (a look's "face"), in the player's language; none for a clue the agent may not read
    if (build) build({ ...context, group, thing, face: lookOf(thing)?.face || null });
    // A clue the co-op agent may not read: the lights over it are out
    if (thing.dark) darken(group);
    scene.add(shadowy(group));
    if (group.userData.outlines) {
      obstacles.push(...group.userData.outlines);
    } else if (SOLID.has(thing.kind)) {
      group.updateMatrixWorld(true);
      const outline = new THREE.Box3().setFromObject(group);
      obstacles.push([outline.min.x, outline.max.x, outline.min.z, outline.max.z]);
    }
    if (thing.facing_hero) later.push(group);
    if (SEE_THROUGH.has(thing.kind)) tall.push(group);
    const spot = thing.spot !== null && thing.spot !== undefined ? data.spots[thing.spot] : null;
    const look = lookOf(thing);
    if (!spot && !look) continue;
    const stand = new THREE.Vector3(...(thing.stand ? [thing.stand[0], 0, thing.stand[1]] : [x, 0, z + 1.2]));
    // Where the label floats: over the thing
    const outline = new THREE.Box3().setFromObject(group);
    const anchor = new THREE.Vector3((outline.min.x + outline.max.x) / 2, Math.min(outline.max.y + 0.3, H - 0.3), (outline.min.z + outline.max.z) / 2);
    usable.push({ thing, group, spot, look, stand, anchor, label: (spot || look).label });
  }

  // Marks on the floor where a thing can be used: a soft golden ring, brighter for the nearest
  const ringGeometry = new THREE.RingGeometry(0.3, 0.4, 40);
  for (const item of usable) {
    const ring = new THREE.Mesh(ringGeometry, new THREE.MeshBasicMaterial({ color: "#f2c14e", transparent: true, opacity: 0.2, depthWrite: false }));
    ring.rotation.x = -Math.PI / 2;
    ring.position.set(item.stand.x, 0.015, item.stand.z);
    scene.add(ring);
    item.ring = ring;
  }

  // Dust floating in the light (indoors), or sprinklers spraying (the terrace)
  const dustCount = outdoor ? 0 : 220;
  const dustPositions = new Float32Array(dustCount * 3);
  for (let i = 0; i < dustCount; i++) {
    dustPositions[i * 3] = (Math.random() - 0.5) * W;
    dustPositions[i * 3 + 1] = Math.random() * H;
    dustPositions[i * 3 + 2] = (Math.random() - 0.5) * D;
  }
  const dustGeometry = new THREE.BufferGeometry();
  dustGeometry.setAttribute("position", new THREE.BufferAttribute(dustPositions, 3));
  const dust = new THREE.Points(dustGeometry, new THREE.PointsMaterial({ color: "#fff2c8", size: 0.025, transparent: true, opacity: 0.5, depthWrite: false }));
  scene.add(dust);
  if (world.spray) addSpray(THREE, scene, world.things.filter((t) => t.kind === "sprinkler"), animated);

  // --- The character (none for the contacto, who watches through a camera) ---
  // Where it stands is kept while the player stays in this room (an action redraws the screen);
  // a new arrival, a restart or a new game starts at the room's start
  const visit = `${data.place}:${data.timer.run}`;
  let here = globalThis.__forbiddenArchiveHere;
  if (!here || here.visit !== visit || globalThis.__forbiddenArchiveCameFrom !== visit) {
    here = { visit, x: world.start[0], z: world.start[1], turn: Math.PI };
    globalThis.__forbiddenArchiveHere = here;
  }
  const hero = watching || menuView ? null : makePerson(THREE, { coat: world.hero.coat });
  if (hero) {
    hero.group.position.set(here.x, 0, here.z);
    hero.group.rotation.y = here.turn;
    scene.add(shadowy(hero.group));
    // The guard who caught you stands in front of you, torch in hand
    for (const group of later) {
      const angle = here.turn;
      group.position.set(here.x + Math.sin(angle) * 1.4, 0, here.z + Math.cos(angle) * 1.4);
      group.rotation.y = angle + Math.PI;
    }
  }

  // Screen-space elements over the canvas: the label of the nearest thing and what the hero says
  const prompt = el("div", "prompt3d");
  const sayBox = el("div", "say3d");
  const canvas = renderer.domElement;
  stage.prepend(canvas);
  stage.append(prompt, sayBox);
  if (watching) {
    const rec = el("div", "cctv-overlay");
    rec.append(el("span", "rec", "● REC"), el("span", "cam", `CAM 0${(world.room.length % 7) + 1}`));
    stage.append(rec);
  }

  const resize = () => {
    const width = stage.clientWidth;
    const height = stage.clientHeight;
    if (!width || !height) return;
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  };
  const observer = new ResizeObserver(resize);
  observer.observe(stage);
  globalThis.addEventListener("resize", resize);
  resize();

  // --- Walking ---
  const held = new Set();
  let target = null; // { path, point, then } when walking to a clicked place or thing
  let stuck = 0;
  let stepClock = 0;
  const edge = outdoor ? 0.6 : 0.45;
  const collides = (x, z) =>
    x < -W / 2 + edge || x > W / 2 - edge || z < -D / 2 + edge + 0.1 || z > D / 2 - 0.2 ||
    obstacles.some(([x1, x2, z1, z2]) => x > x1 - HERO_RADIUS && x < x2 + HERO_RADIUS && z > z1 - HERO_RADIUS && z < z2 + HERO_RADIUS);

  function moveBy(dx, dz) {
    // Each axis on its own, so the character slides along a desk instead of stopping
    const p = hero.group.position;
    let moved = false;
    if (dx && !collides(p.x + dx, p.z)) {
      p.x += dx;
      moved = true;
    }
    if (dz && !collides(p.x, p.z + dz)) {
      p.z += dz;
      moved = true;
    }
    return moved;
  }

  function faceTowards(x, z, dt, speed = 12) {
    const wanted = Math.atan2(x, z);
    let diff = wanted - hero.group.rotation.y;
    diff = Math.atan2(Math.sin(diff), Math.cos(diff));
    hero.group.rotation.y += diff * Math.min(1, dt * speed);
  }

  // --- The nearest usable thing, and using it ---
  let nearest = null;
  const ui = interactions(stage, data, setTriggerValue, { heroSays, walkTo: null });
  const busy = () => !!stage.querySelector(".bubble, .dialogue, .ending, .notebook, .confirm, .inspect3d, .lock3d, .laptop3d");

  function findNearest() {
    if (!hero) return null;
    const p = hero.group.position;
    let best = null;
    for (const item of usable) {
      const distance = Math.hypot(item.stand.x - p.x, item.stand.z - p.z);
      if (distance <= REACH && (!best || distance < best.distance)) best = { item, distance };
    }
    return best?.item || null;
  }

  // At the laptop its screen opens (log in, the files, the Wi-Fi, the terminal)
  const laptopSteps = (spot) => world.laptop && (spot.lock === "login" || spot.lock === "wifi" || spot.talk === "pen" || spot.talk === "terminal");
  function useSpot(spot) {
    if (laptopSteps(spot)) return openLaptop(stage, data, setTriggerValue);
    if (spot.talk) return ui.openTalk(spot);
    if (spot.code_prompt) return ui.openKeypad(spot);
    setTriggerValue("action", { id: spot.action, x: spot.stand });
  }

  function use(item) {
    Sound.click();
    ui.closeBubble();
    if (hero) {
      // Turn to the thing
      const p = hero.group.position;
      const at = item.group.position;
      here.turn = Math.atan2(at.x - p.x, at.z - p.z);
    }
    if (item.look) return inspect(item);
    useSpot(item.spot);
  }

  // --- Looking at a thing close up: the camera goes to it and its words can be read on it ---
  let inspecting = null;
  const inspectLight = new THREE.PointLight("#ffffff", 0, 3, 1.5);
  scene.add(inspectLight);
  function inspect(item) {
    stopInspecting();
    item.group.updateMatrixWorld(true);
    const focus = item.group.userData.focus;
    let target;
    let normal;
    let width;
    let height;
    if (focus) {
      target = item.group.localToWorld(new THREE.Vector3(...focus.at));
      normal = new THREE.Vector3(...focus.normal).normalize().transformDirection(item.group.matrixWorld);
      ({ width, height } = focus);
    } else {
      const bounds = new THREE.Box3().setFromObject(item.group);
      target = bounds.getCenter(new THREE.Vector3());
      const size = bounds.getSize(new THREE.Vector3());
      normal = new THREE.Vector3(0, 0.35, 1).normalize();
      width = Math.max(size.x, size.z);
      height = size.y;
    }
    // Far enough for the whole face to fit the screen
    const fit = Math.max(height, width / camera.aspect) / (2 * Math.tan(THREE.MathUtils.degToRad(camera.fov / 2)));
    inspecting = { item, position: target.clone().addScaledVector(normal, fit * 1.12 + 0.03), target };
    if (hero) hero.group.visible = false;
    const panel = el("div", "inspect3d");
    panel.onclick = (event) => event.stopPropagation();
    const back = el("button", "choice inspect-back", data.ui.inspect_back);
    back.onclick = () => {
      Sound.click();
      stopInspecting();
    };
    panel.append(el("div", "inspect-name", `🔍 ${item.label}`), back);
    stage.append(panel);
    // What the character thinks about it (the snack machine, the coffee machine)
    if (item.look.remark) {
      const thought = el("div", "inspect-thought", item.look.remark);
      stage.append(thought);
      speak(item.look.remark, "you", data.voice_lang);
    }
  }
  function stopInspecting() {
    if (!inspecting) return;
    inspecting = null;
    if (hero) hero.group.visible = true;
    stage.querySelectorAll(".inspect3d, .inspect-thought").forEach((node) => node.remove());
  }

  function walkTo(point, then) {
    if (!hero) return then && then();
    ui.closeBubble();
    const path = findPath(hero.group.position, point);
    target = { path, point: path.shift(), then };
    stuck = 0;
  }

  // The way around the furniture: a grid of 25 cm squares, searched with A* (the shortest way
  // through the free squares), then straightened where nothing is in between
  const CELL = 0.25;
  const columns = Math.round(W / CELL);
  const rows = Math.round(D / CELL);
  const cellX = (i) => -W / 2 + (i + 0.5) * CELL;
  const cellZ = (j) => -D / 2 + (j + 0.5) * CELL;
  const free = [];
  for (let j = 0; j < rows; j++) for (let i = 0; i < columns; i++) free.push(!collides(cellX(i), cellZ(j)));
  const clearLine = (a, b) => {
    const n = Math.ceil(Math.hypot(b.x - a.x, b.z - a.z) / 0.1);
    for (let k = 1; k <= n; k++) if (collides(a.x + ((b.x - a.x) * k) / n, a.z + ((b.z - a.z) * k) / n)) return false;
    return true;
  };
  function findPath(from, to) {
    const goal = new THREE.Vector3(to.x, 0, to.z);
    if (clearLine(from, goal)) return [goal];
    const index = (x, z) => [
      Math.max(0, Math.min(columns - 1, Math.floor((x + W / 2) / CELL))),
      Math.max(0, Math.min(rows - 1, Math.floor((z + D / 2) / CELL))),
    ];
    const [si, sj] = index(from.x, from.z);
    const [gi, gj] = index(to.x, to.z);
    const start = sj * columns + si;
    const end = gj * columns + gi;
    const cost = new Map([[start, 0]]);
    const came = new Map();
    const open = [[0, start]];
    while (open.length) {
      open.sort((a, b) => a[0] - b[0]);
      const [, current] = open.shift();
      if (current === end) break;
      const ci = current % columns;
      const cj = Math.floor(current / columns);
      for (const [di, dj] of [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]) {
        const ni = ci + di;
        const nj = cj + dj;
        if (ni < 0 || nj < 0 || ni >= columns || nj >= rows) continue;
        const next = nj * columns + ni;
        if (!free[next] && next !== end) continue;
        const total = cost.get(current) + Math.hypot(di, dj);
        if (total < (cost.get(next) ?? Infinity)) {
          cost.set(next, total);
          came.set(next, current);
          open.push([total + Math.hypot(gi - ni, gj - nj), next]);
        }
      }
    }
    if (!came.has(end)) return [goal]; // no way round: walk straight and stop at the furniture
    const cells = [];
    for (let c = end; c !== start; c = came.get(c)) cells.unshift(new THREE.Vector3(cellX(c % columns), 0, cellZ(Math.floor(c / columns))));
    cells[cells.length - 1] = goal;
    // Keep only the corners: skip every point that can be reached in a straight line
    const path = [];
    let corner = from;
    for (let k = 0; k < cells.length; k++) {
      if (k === cells.length - 1 || !clearLine(corner, cells[k + 1])) {
        path.push(cells[k]);
        corner = cells[k];
      }
    }
    return path;
  }

  // --- Mouse: click the floor to walk there, click a thing to walk to it and use it ---
  const raycaster = new THREE.Raycaster();
  const pointer = new THREE.Vector2();
  let hovered = null;
  const pick = (event) => {
    const rect = canvas.getBoundingClientRect();
    pointer.set(((event.clientX - rect.left) / rect.width) * 2 - 1, -((event.clientY - rect.top) / rect.height) * 2 + 1);
    raycaster.setFromCamera(pointer, camera);
    for (const hit of raycaster.intersectObjects(usable.map((item) => item.group), true)) {
      const item = usable.find((u) => isInside(hit.object, u.group));
      if (item) return { item };
    }
    const floorHit = raycaster.intersectObject(floor)[0];
    return floorHit ? { point: floorHit.point } : null;
  };
  canvas.onpointermove = (event) => {
    if (ending) return;
    const hit = pick(event);
    canvas.style.cursor = hit?.item ? "pointer" : hero ? "crosshair" : "default";
    hovered = hit?.item || null;
  };
  canvas.onpointerleave = () => (hovered = null);
  stage.onclick = (event) => {
    if (event.target !== canvas || ending || menuView || data.danger) return;
    if (inspecting) return stopInspecting();
    const hit = pick(event);
    if (!hit) return;
    if (hit.item) {
      if (!hero) return hit.item.look && use(hit.item);
      Sound.click();
      walkTo(hit.item.stand, () => use(hit.item));
    } else if (hero) {
      walkTo(hit.point);
    }
  };

  // --- The contact, at the security camera: the things they can zoom in on ---
  if (watching && data.clues) {
    const panel = el("div", "cctv-list");
    panel.append(el("div", "free3d-title", data.ui.clues_zoom));
    for (const item of usable.filter((u) => u.look)) {
      const b = el("button", "choice", `🔍 ${item.label}`);
      b.onclick = (event) => {
        event.stopPropagation();
        Sound.click();
        inspect(item);
      };
      panel.append(b);
    }
    stage.append(panel);
  }

  // --- Actions with nothing in the room for them (texting Rita): buttons over the view ---
  if (world.free?.length && !ending) {
    const panel = el("div", "free3d");
    panel.append(el("div", "free3d-title", data.ui.free_actions));
    for (const index of world.free) {
      const spot = data.spots[index];
      const b = el("button", "choice", spot.label);
      b.onclick = (event) => {
        event.stopPropagation();
        Sound.click();
        ui.closeBubble();
        useSpot(spot);
      };
      panel.append(b);
    }
    stage.append(panel);
  }

  // --- The character speaks: a bubble over its head, and the voice ---
  let sayUntil = 0;
  // thinking: a thought bubble (a hint), shown for longer
  function heroSays(text, thinking = false) {
    if (!hero || !text) return;
    sayBox.textContent = text;
    sayBox.classList.add("show");
    sayBox.classList.toggle("thought", thinking);
    sayUntil = performance.now() + Math.min(thinking ? 14000 : 9000, (thinking ? 5000 : 2500) + text.length * 60);
    speak(text, "you", data.voice_lang);
  }
  if (data.speech && !world.laptop) setTimeout(() => heroSays(data.speech), 300);
  // Sitting at the laptop: its screen opens by itself
  if (world.laptop && hero && !ending) setTimeout(() => stage.isConnected && openLaptop(stage, data, setTriggerValue), 500);
  // A hint is the character thinking aloud
  if (data.message?.hint) setTimeout(() => heroSays(data.message.text.replace(/^💡\s*/, "💭 "), true), 300);

  // Puts an HTML element over a point of the room
  const projected = new THREE.Vector3();
  function placeOver(element, point) {
    projected.copy(point).project(camera);
    element.style.left = `${((projected.x + 1) / 2) * 100}%`;
    element.style.top = `${((1 - projected.y) / 2) * 100}%`;
    element.style.visibility = projected.z < 1 ? "visible" : "hidden";
  }

  // --- A danger: the choices open at once and a clock runs; at zero the timeout action is sent ---
  if (data.danger && !ending) {
    const { seconds, timeout } = data.danger;
    const spot = data.spots.find((s) => s.talk);
    const clock = el("div", "danger-clock");
    const bar = el("div", "danger-bar");
    const label = el("span", "danger-label", `⏱ ${data.ui.danger_hurry} ${seconds}`);
    clock.append(bar, label);
    stage.append(clock);
    let left = seconds;
    let done = false;
    const timer = setInterval(() => {
      if (done || !stage.isConnected) return clearInterval(timer);
      left -= 1;
      label.textContent = `⏱ ${data.ui.danger_hurry} ${Math.max(left, 0)}`;
      Sound.tick();
      if (left <= 0) {
        done = true;
        ui.closeBubble();
        setTriggerValue("action", { id: timeout, x: 0 });
      }
    }, 1000);
    stage.addEventListener("choice-sent", () => (done = true));
    requestAnimationFrame(() => {
      bar.style.transitionDuration = `${seconds}s`;
      bar.classList.add("running");
    });
    if (spot) setTimeout(() => !done && ui.openTalk(spot), 700);
  }

  // --- Cameras ---
  const look = new THREE.Vector3();
  const cctvAt = new THREE.Vector3(W / 2 - 0.8, (outdoor ? 5.5 : H - 0.25), D / 2 + 1.5);
  const cctvLook = new THREE.Vector3(-1, 0.5, -1.5);
  if (watching) {
    // A security camera high in the front corner, slowly panning
    camera.position.copy(cctvAt);
    look.copy(cctvLook);
    camera.fov = 62;
    camera.updateProjectionMatrix();
  } else {
    camera.position.set(here.x, 3.4, here.z + 6);
    look.set(here.x, 1.1, here.z - 1.5);
  }
  camera.lookAt(look);
  const offsets = { follow: new THREE.Vector3(0, 3.1, 5.2), close: new THREE.Vector3(0.9, 2.3, 3.2) };
  const followOffset = offsets[world.camera] || offsets.follow;

  // --- Every frame ---
  const wantedCamera = new THREE.Vector3();
  const wantedLook = new THREE.Vector3();
  function update(dt, time) {
    for (const lamp of lamps) {
      // A light sometimes flickers, as old tubes do
      lamp.flicker -= dt;
      const off = lamp.flicker < 0 && lamp.flicker > -0.12;
      if (lamp.flicker < -0.12) lamp.flicker = 5 + Math.random() * 14;
      lamp.light.intensity = off ? lamp.base * 0.3 : lamp.base;
    }
    for (const step of animated) step(dt, time, hero?.group.position);
    const positions = dust.geometry.attributes.position;
    for (let i = 0; i < dustCount; i++) {
      let y = positions.getY(i) + dt * 0.05;
      if (y > H) y = 0;
      positions.setY(i, y);
      positions.setX(i, positions.getX(i) + Math.sin(time * 0.3 + i) * dt * 0.02);
    }
    if (dustCount) positions.needsUpdate = true;

    if (menuView) {
      const angle = time * 0.05;
      camera.position.set(Math.sin(angle) * 9, 3.2, Math.cos(angle) * 9 + 1);
      look.set(0, 1.2, -2);
      camera.lookAt(look);
      return;
    }
    if (inspecting) {
      const ease = 1 - Math.exp(-dt * 5);
      camera.position.lerp(inspecting.position, ease);
      look.lerp(inspecting.target, ease);
      camera.lookAt(look);
      inspectLight.position.copy(camera.position);
      inspectLight.intensity += (0.9 - inspectLight.intensity) * ease;
      prompt.classList.remove("show");
      return;
    }
    inspectLight.intensity *= 0.85;
    if (watching) {
      const ease = 1 - Math.exp(-dt * 3);
      wantedCamera.set(cctvAt.x + Math.sin(time * 0.15) * 1.2, cctvAt.y, cctvAt.z);
      camera.position.lerp(wantedCamera, ease);
      look.lerp(cctvLook, ease);
      camera.lookAt(look);
      return;
    }
    const p = hero.group.position;
    if (ending) {
      // The camera slowly circles the character
      const angle = time * 0.18;
      camera.position.set(p.x + Math.sin(angle) * 4.6, 2.6, p.z + Math.cos(angle) * 4.6);
      look.set(p.x, 1.2, p.z);
      camera.lookAt(look);
      hero.animate(dt, time, false);
      return;
    }

    // Walking, in short steps, so a slow frame does not jump through a desk
    const steps = Math.ceil(dt / 0.04);
    let walking = false;
    for (let i = 0; i < steps; i++) walking = walkStep(dt / steps) || walking;
    if (walking) here.turn = hero.group.rotation.y;
    here.x = p.x;
    here.z = p.z;
    hero.animate(dt, time, walking);
    if (walking) {
      stepClock -= dt;
      if (stepClock <= 0) {
        Sound.step();
        stepClock = 0.36;
      }
    }

    // The camera follows from behind and a little above, smoothly (and stays out of the walls)
    wantedCamera.copy(p).add(followOffset);
    wantedCamera.x = Math.max(-W / 2 + 1.6, Math.min(W / 2 - 1.6, wantedCamera.x));
    wantedLook.set(p.x, 1.1, p.z - 1.6);
    const ease = 1 - Math.exp(-dt * 4);
    camera.position.lerp(wantedCamera, ease);
    look.lerp(wantedLook, ease);
    camera.lookAt(look);

    seeThrough(dt, p);

    // The nearest thing: its ring glows and its label floats over it
    nearest = findNearest();
    const shown = nearest || hovered;
    for (const item of usable) {
      const glow = item === nearest ? 0.8 + Math.sin(time * 5) * 0.2 : item === hovered ? 0.55 : 0.2;
      item.ring.material.opacity += (glow - item.ring.material.opacity) * Math.min(1, dt * 10);
    }
    // No label while a bubble (a text, choices, a keypad) is open: it would cover it
    if (shown && !busy()) {
      prompt.innerHTML = "";
      if (shown === nearest) prompt.append(el("kbd", "", "E"));
      prompt.append(el("span", "", shown.label));
      prompt.classList.add("show");
      placeOver(prompt, shown.anchor);
    } else {
      prompt.classList.remove("show");
    }
    if (sayBox.classList.contains("show")) {
      if (performance.now() > sayUntil) sayBox.classList.remove("show");
      else placeOver(sayBox, projected.set(p.x, 2.25, p.z));
    }
  }

  // A column (or the stairs, a shelf) between the camera and the character: it fades to a ghost
  const sight = new THREE.Raycaster();
  const toHero = new THREE.Vector3();
  let faded = new Set();
  let sightClock = 0;
  const setFaded = (group, on) =>
    group.traverse((child) => {
      if (!child.isMesh) return;
      for (const m of Array.isArray(child.material) ? child.material : [child.material]) {
        if (on) {
          m.userData.opacity ??= m.opacity;
          m.userData.transparent ??= m.transparent;
          m.transparent = true;
          m.opacity = Math.min(m.userData.opacity, 0.22);
          m.depthWrite = false;
        } else if (m.userData.opacity !== undefined) {
          m.opacity = m.userData.opacity;
          m.transparent = m.userData.transparent;
          m.depthWrite = true;
        }
        m.needsUpdate = true;
      }
    });
  function seeThrough(dt, p) {
    sightClock -= dt;
    if (sightClock > 0 || !tall.length) return;
    sightClock = 0.12;
    toHero.set(p.x, 1.3, p.z).sub(camera.position);
    const distance = toHero.length();
    sight.set(camera.position, toHero.normalize());
    sight.far = distance - 0.4;
    const hiding = new Set();
    for (const hit of sight.intersectObjects(tall, true)) {
      const group = tall.find((g) => isInside(hit.object, g));
      if (group) hiding.add(group);
    }
    for (const group of faded) if (!hiding.has(group)) setFaded(group, false);
    for (const group of hiding) if (!faded.has(group)) setFaded(group, true);
    faded = hiding;
  }

  // One short step: held keys first, then a clicked target
  function walkStep(dt) {
    const p = hero.group.position;
    let dx = 0;
    let dz = 0;
    for (const k of held) {
      dx += MOVE_KEYS[k][0];
      dz += MOVE_KEYS[k][1];
    }
    let walking = false;
    if (dx || dz) {
      target = null;
      const length = Math.hypot(dx, dz);
      dx = (dx / length) * WALK_SPEED * dt;
      dz = (dz / length) * WALK_SPEED * dt;
      faceTowards(dx, dz, dt);
      walking = moveBy(dx, dz);
    } else if (target) {
      const tx = target.point.x - p.x;
      const tz = target.point.z - p.z;
      const distance = Math.hypot(tx, tz);
      if (distance < 0.08) {
        if (target.path.length) {
          target.point = target.path.shift(); // the next corner
        } else {
          const then = target.then;
          target = null;
          if (then) then();
        }
      } else {
        const stepLength = Math.min(distance, WALK_SPEED * dt);
        faceTowards(tx, tz, dt);
        walking = moveBy((tx / distance) * stepLength, (tz / distance) * stepLength);
        stuck = walking ? 0 : stuck + dt;
        if (stuck > 0.3) {
          // Blocked by furniture: stop; close enough to a thing still uses it
          const then = target.then;
          target = null;
          if (then && distance < REACH) then();
        }
      }
    } else {
      faceTowards(Math.sin(here.turn), Math.cos(here.turn), dt, 6);
    }
    return walking;
  }

  shared.active = { scene, camera, update };
  // For the browser tests (Playwright): walk to a point of the room, as a click on the floor does
  if (hero) globalThis.__forbiddenArchiveWalkTo = (x, z) => walkTo(new THREE.Vector3(x, 0, z));

  // Stop drawing (and free the GPU memory) once this screen is gone
  const watcher = setInterval(() => {
    if (stage.isConnected) return;
    clearInterval(watcher);
    observer.disconnect();
    globalThis.removeEventListener("resize", resize);
    if (shared.active?.scene === scene) {
      disposeRoom(shared.active);
      shared.active = null;
    }
  }, 1000);

  const canWalk = () => hero && !ending && !data.danger;
  return {
    startWalking: () => {},
    stopWalking: (key) => {
      if (key === "blur") held.clear();
      else held.delete(moveKey(key));
    },
    useNearest: () => {
      rememberKeys();
      if (inspecting) return stopInspecting();
      if (nearest && canWalk()) use(nearest);
    },
    stopInspecting,
    move3d: (key) => {
      if (!MOVE_KEYS[moveKey(key)]) return false;
      if (!canWalk()) return true; // the keys do nothing here, but do not reach the 2D handler
      rememberKeys();
      stopInspecting();
      // WASD and the arrows walk; E, Enter and Space use the nearest thing (scene_view.js)
      ui.closeBubble();
      held.add(moveKey(key));
      return true;
    },
  };
}

function isInside(object, group) {
  for (let o = object; o; o = o.parent) if (o === group) return true;
  return false;
}

// A clue the co-op agent may not read: the thing stays, almost black
function darken(group) {
  const dim = (material) => {
    const dark = material.clone();
    dark.color?.multiplyScalar(0.12);
    if (dark.emissive) dark.emissiveIntensity = 0;
    dark.map = null;
    dark.needsUpdate = true;
    return dark;
  };
  group.traverse((child) => {
    if (!child.isMesh) return;
    // Some things have one material per face
    child.material = Array.isArray(child.material) ? child.material.map(dim) : dim(child.material);
  });
}

// --- Outside: the night sky, the moon and the sea of Carcavelos, beyond the railing on the right --

function buildSky(THREE, scene, W, D) {
  const sky = canvasTexture(THREE, 64, 512, (g, w, h) => {
    const gradient = g.createLinearGradient(0, 0, 0, h);
    gradient.addColorStop(0, "#05060f");
    gradient.addColorStop(0.45, "#101a3a");
    gradient.addColorStop(0.5, "#2a2f5a");
    gradient.addColorStop(0.52, "#0a1024");
    gradient.addColorStop(1, "#05070f");
    g.fillStyle = gradient;
    g.fillRect(0, 0, w, h);
  });
  const dome = new THREE.Mesh(new THREE.SphereGeometry(180, 32, 16), new THREE.MeshBasicMaterial({ map: sky, side: THREE.BackSide, fog: false }));
  scene.add(dome);
  scene.background = new THREE.Color("#05060f");
  scene.fog = new THREE.Fog("#0a1024", 40, 170);
  // Stars
  const stars = new Float32Array(900);
  for (let i = 0; i < 300; i++) {
    const a = Math.random() * Math.PI * 2;
    const h = 0.12 + Math.random() * 0.8;
    stars[i * 3] = Math.cos(a) * 170 * Math.cos(h);
    stars[i * 3 + 1] = 170 * Math.sin(h);
    stars[i * 3 + 2] = Math.sin(a) * 170 * Math.cos(h);
  }
  const starGeometry = new THREE.BufferGeometry();
  starGeometry.setAttribute("position", new THREE.BufferAttribute(stars, 3));
  scene.add(new THREE.Points(starGeometry, new THREE.PointsMaterial({ color: "#ffffff", size: 0.6, fog: false })));
  // The moon over the sea, and its path on the water
  const moon = new THREE.Mesh(new THREE.CircleGeometry(5, 32), new THREE.MeshBasicMaterial({ color: "#fff6dc", fog: false }));
  moon.position.set(150, 34, 10);
  moon.lookAt(0, 0, 0);
  scene.add(moon);
  const sea = new THREE.Mesh(
    new THREE.PlaneGeometry(160, 400),
    new THREE.MeshStandardMaterial({ color: "#0c1834", roughness: 0.25, metalness: 0.6 })
  );
  sea.rotation.x = -Math.PI / 2;
  sea.position.set(W / 2 + 82, -4, 0);
  scene.add(sea);
  const glint = new THREE.Mesh(
    new THREE.PlaneGeometry(120, 6),
    new THREE.MeshBasicMaterial({ color: "#fff2c0", transparent: true, opacity: 0.18, depthWrite: false })
  );
  glint.rotation.x = -Math.PI / 2;
  glint.position.set(W / 2 + 70, -3.95, 4);
  scene.add(glint);
  const moonlight = new THREE.DirectionalLight("#c8d4ff", 0.6);
  moonlight.position.set(60, 30, 10);
  scene.add(moonlight);
  // The railing along the edge of the terrace (back and right)
  const rail = new THREE.MeshStandardMaterial({ color: "#c9ccd2", metalness: 0.7, roughness: 0.35 });
  const railing = (length, along, x, z) => {
    const g = new THREE.Group();
    const top = new THREE.Mesh(new THREE.BoxGeometry(along === "x" ? length : 0.05, 0.05, along === "x" ? 0.05 : length), rail);
    top.position.y = 1.05;
    g.add(top);
    for (let s = -length / 2; s <= length / 2; s += 0.12) {
      const bar = new THREE.Mesh(new THREE.BoxGeometry(0.018, 1.05, 0.018), rail);
      bar.position.set(along === "x" ? s : 0, 0.525, along === "x" ? 0 : s);
      g.add(bar);
    }
    g.position.set(x, 0, z);
    scene.add(g);
  };
  railing(D, "z", W / 2, 0);
  // A low wall under the railing, the edge of the terrace
  const ledge = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.25, D + 0.4), new THREE.MeshStandardMaterial({ color: "#e9e6df" }));
  ledge.position.set(W / 2 + 0.15, 0.12, 0);
  scene.add(ledge);
}

// Big windows on part of the back wall (from x1 to x2), with the night outside
function buildWindows(THREE, scene, W, D, H, [x1, x2]) {
  const night = canvasTexture(THREE, 1024, 256, (g, w, h) => {
    const gradient = g.createLinearGradient(0, 0, 0, h);
    gradient.addColorStop(0, "#070a1a");
    gradient.addColorStop(0.6, "#16224a");
    gradient.addColorStop(0.62, "#0a1226");
    gradient.addColorStop(1, "#05080f");
    g.fillStyle = gradient;
    g.fillRect(0, 0, w, h);
    for (let i = 0; i < 70; i++) {
      g.fillStyle = Math.random() < 0.7 ? "#ffd58a" : "#bfe0ff";
      g.fillRect(Math.random() * w, h * 0.55 + Math.random() * 12, 2, 2);
    }
  });
  const width = x2 - x1;
  const glass = new THREE.Mesh(new THREE.PlaneGeometry(width, H - 0.3), new THREE.MeshBasicMaterial({ map: night }));
  glass.position.set((x1 + x2) / 2, (H - 0.3) / 2 + 0.05, -D / 2 + 0.01);
  scene.add(glass);
  // Thin frames between the panes, every 1.4 metres
  const panes = Math.max(1, Math.round(width / 1.4));
  for (let i = 0; i <= panes; i++) {
    const frame = new THREE.Mesh(new THREE.BoxGeometry(0.05, H - 0.3, 0.06), new THREE.MeshStandardMaterial({ color: "#d8d9db" }));
    frame.position.set(x1 + (i * width) / panes, (H - 0.3) / 2 + 0.05, -D / 2 + 0.03);
    scene.add(frame);
  }
}

// The sprinklers: drops shot up in arcs, falling back down, again and again
function addSpray(THREE, scene, sprinklers, animated) {
  const perJet = 160;
  const count = perJet * sprinklers.length;
  const positions = new Float32Array(count * 3);
  const speeds = [];
  for (let i = 0; i < count; i++) speeds.push({ age: Math.random() * 1.4, angle: Math.random() * Math.PI * 2, speed: 2 + Math.random() * 2.5 });
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  const drops = new THREE.Points(geometry, new THREE.PointsMaterial({ color: "#bfe4ff", size: 0.06, transparent: true, opacity: 0.8, depthWrite: false }));
  scene.add(drops);
  animated.push((dt, time) => {
    for (let i = 0; i < count; i++) {
      const s = speeds[i];
      const [x0, z0] = sprinklers[Math.floor(i / perJet)].at;
      s.age += dt;
      if (s.age > 1.4) {
        s.age = 0;
        s.angle = time * 1.5 + (Math.random() - 0.5) * 1.2; // the jet turns round
        s.speed = 2 + Math.random() * 2.5;
      }
      const t = s.age;
      positions[i * 3] = x0 + Math.cos(s.angle) * s.speed * t;
      positions[i * 3 + 1] = Math.max(0, 0.2 + 4.2 * t - 4.9 * t * t);
      positions[i * 3 + 2] = z0 + Math.sin(s.angle) * s.speed * t;
    }
    geometry.attributes.position.needsUpdate = true;
  });
}

// --- People: the player, Tiago and the security guard, made of simple shapes --------------------
//
// options.coat: the yellow raincoat over the hoodie (the player once they take the coat)
// options.guard: a dark uniform, a cap and a torch with a beam of light
// options.sleeping: sitting, slumped over a desk (Tiago)

function makePerson(THREE, options = {}) {
  const material = (color, roughness = 0.75) => new THREE.MeshStandardMaterial({ color, roughness });
  const top = options.guard ? "#1d2333" : options.coat ? "#f2c230" : options.hoodie || "#2c4a8a";
  const topDark = options.guard ? "#141826" : options.coat ? "#c99a12" : shade(options.hoodie || "#2c4a8a", -0.3);
  const legs = options.guard ? "#151a26" : "#3b5478";
  const skin = material(options.skin || "#e9b996", 0.6);
  const hair = material(options.hair || "#2a1a10", 0.9);
  const mesh = (geometry, mat, x, y, z) => {
    const m = new THREE.Mesh(geometry, mat);
    m.position.set(x, y, z);
    return m;
  };

  const group = new THREE.Group();
  const body = new THREE.Group(); // bobs while walking
  group.add(body);

  // Legs swing from the hip (jeans and trainers)
  const legParts = [-0.11, 0.11].map((x) => {
    const hip = new THREE.Group();
    hip.position.set(x, 0.84, 0);
    hip.add(mesh(new THREE.BoxGeometry(0.17, 0.78, 0.18), material(legs), 0, -0.4, 0));
    hip.add(mesh(new THREE.BoxGeometry(0.19, 0.09, 0.3), material(options.guard ? "#0c0c0f" : "#f4f4f4", 0.5), 0, -0.82, 0.05));
    body.add(hip);
    return hip;
  });

  // The body: a hoodie, or a long raincoat, or a uniform
  const long = options.coat ? 0.95 : 0.7;
  body.add(mesh(new THREE.CylinderGeometry(0.27, options.coat ? 0.38 : 0.3, long, 16), material(top, options.coat ? 0.35 : 0.8), 0, 1.6 - long / 2, 0));
  body.add(mesh(new THREE.CylinderGeometry(0.18, 0.27, 0.14, 16), material(topDark), 0, 1.66, 0));
  if (!options.coat && !options.guard) {
    // The hoodie's hood, resting on the back, and its pocket
    body.add(mesh(new THREE.SphereGeometry(0.19, 14, 10, 0, Math.PI * 2, 0, Math.PI / 2), material(topDark), 0, 1.62, -0.14));
    body.add(mesh(new THREE.BoxGeometry(0.3, 0.14, 0.02), material(topDark), 0, 1.08, 0.29));
  }
  if (options.guard) body.add(mesh(new THREE.BoxGeometry(0.12, 0.08, 0.02), material("#d8b45a", 0.3), 0.12, 1.45, 0.27));
  body.add(mesh(new THREE.CylinderGeometry(0.07, 0.08, 0.1, 10), skin, 0, 1.76, 0));

  // Arms swing from the shoulder, opposite to the legs
  const arms = [-0.35, 0.35].map((x) => {
    const shoulder = new THREE.Group();
    shoulder.position.set(x, 1.58, 0);
    shoulder.rotation.z = x < 0 ? -0.08 : 0.08;
    shoulder.add(mesh(new THREE.BoxGeometry(0.14, 0.66, 0.16), material(top, options.coat ? 0.35 : 0.8), 0, -0.32, 0));
    shoulder.add(mesh(new THREE.SphereGeometry(0.07, 12, 10), skin, 0, -0.69, 0));
    body.add(shoulder);
    return shoulder;
  });

  // Head, hair (or the guard's cap)
  const head = new THREE.Group();
  head.position.set(0, 1.95, 0);
  head.add(mesh(new THREE.SphereGeometry(0.18, 20, 16), skin, 0, 0, 0));
  for (const x of [-0.065, 0.065]) head.add(mesh(new THREE.SphereGeometry(0.02, 8, 6), material("#1a1020", 0.3), x, 0.02, 0.165));
  if (options.guard) {
    head.add(mesh(new THREE.CylinderGeometry(0.19, 0.19, 0.12, 20), material("#141826"), 0, 0.12, 0));
    head.add(mesh(new THREE.BoxGeometry(0.26, 0.02, 0.14), material("#0b0d14"), 0, 0.07, 0.18));
  } else {
    const cap = mesh(new THREE.SphereGeometry(0.19, 20, 16, 0, Math.PI * 2, 0, Math.PI * 0.55), hair, 0, 0.02, -0.02);
    cap.rotation.x = -0.35;
    head.add(cap);
  }
  body.add(head);

  // The guard's torch, and its beam
  let beam = null;
  if (options.guard) {
    const torch = mesh(new THREE.CylinderGeometry(0.035, 0.045, 0.22, 10), material("#2a2a2a", 0.3), 0, -0.72, 0.1);
    torch.rotation.x = Math.PI / 2;
    arms[1].add(torch);
    arms[1].rotation.x = -1.1;
    beam = new THREE.SpotLight("#fff1c8", 30, 14, 0.35, 0.5, 1.2);
    beam.position.set(0.35, 1.3, 0.4);
    beam.castShadow = false;
    const aim = new THREE.Object3D();
    aim.position.set(0.2, 0, 5);
    group.add(beam, aim);
    beam.target = aim;
    const cone = new THREE.Mesh(
      new THREE.ConeGeometry(1.2, 5, 24, 1, true),
      new THREE.MeshBasicMaterial({ color: "#fff1c8", transparent: true, opacity: 0.08, depthWrite: false, side: THREE.DoubleSide })
    );
    cone.position.set(0.3, 0.9, 2.7);
    cone.rotation.x = -Math.PI / 2 + 0.25;
    group.add(cone);
  }

  // A soft dark spot under the feet
  const blob = new THREE.Mesh(new THREE.CircleGeometry(0.4, 24), new THREE.MeshBasicMaterial({ color: "#000000", transparent: true, opacity: 0.3, depthWrite: false }));
  blob.rotation.x = -Math.PI / 2;
  blob.position.y = 0.012;
  group.add(blob);

  if (options.sleeping) {
    // Sitting, slumped over the desk, arms folded under the head
    legParts.forEach((leg) => (leg.rotation.x = -1.45));
    body.position.y = -0.38;
    body.rotation.x = 0.95;
    arms.forEach((arm) => (arm.rotation.x = -1.6));
    head.rotation.x = 0.25;
  }

  group.scale.setScalar(0.9);
  let phase = 0;
  let swing = 0;
  function animate(dt, time, walking) {
    if (options.sleeping) {
      // Breathing, very slowly
      body.position.y = -0.38 + Math.sin(time * 1.4) * 0.012;
      return;
    }
    swing += ((walking ? 1 : 0) - swing) * Math.min(1, dt * 10);
    if (walking) phase += dt * 9.5;
    const s = Math.sin(phase) * 0.62 * swing;
    legParts[0].rotation.x = s;
    legParts[1].rotation.x = -s;
    arms[0].rotation.x = -s * 0.8;
    if (!options.guard) arms[1].rotation.x = s * 0.8;
    // Bob while walking, breathe while standing
    body.position.y = Math.abs(Math.sin(phase)) * 0.05 * swing + Math.sin(time * 2) * 0.008 * (1 - swing);
    head.rotation.y = Math.sin(time * 0.6) * 0.15 * (1 - swing);
  }
  return { group, animate, beam };
}

// --- What is written on the real things (story.py "face"), drawn on canvases ---------------------
// A look's face arrives with the look (already in the player's language). Without it (the co-op
// agent, the menu's background) the thing is drawn without its words.

const WHITE = "#f4f3ef";
// Handwriting (post-its, notes, the whiteboard, the chalk menu), then print (notices, signs, screens)
const HAND = "'Segoe Print', 'Ink Free', 'Bradley Hand', 'Comic Sans MS', 'Chalkboard SE', cursive";
const PRINT = "'Segoe UI', 'Helvetica Neue', Arial, sans-serif";

// Splits a text into lines no wider than maxWidth (with the canvas's current font)
function wrapText(g, text, maxWidth) {
  const lines = [];
  for (const paragraph of String(text).split("\n")) {
    let line = "";
    for (const word of paragraph.split(" ")) {
      const longer = line ? `${line} ${word}` : word;
      if (line && g.measureText(longer).width > maxWidth) {
        lines.push(line);
        line = word;
      } else {
        line = longer;
      }
    }
    lines.push(line);
  }
  return lines;
}

// Writes a wrapped text from (x, y) down; returns where the next line would start
function writeText(g, text, x, y, maxWidth, lineHeight) {
  const lines = wrapText(g, text, maxWidth);
  lines.forEach((line, i) => g.fillText(line, x, y + i * lineHeight));
  return y + lines.length * lineHeight;
}

function rounded(g, x, y, w, h, r) {
  g.beginPath();
  if (g.roundRect) g.roundRect(x, y, w, h, r);
  else g.rect(x, y, w, h);
}

// A flat sheet with a texture (paper, a screen, a sign); "glow" makes it light up on its own
function sheet(THREE, texture, width, height, options = {}) {
  const { glow = 0, side = THREE.FrontSide, transparent = false } = options;
  // A screen shows its own colours, whatever the light in the room
  if (options.screen) return new THREE.Mesh(new THREE.PlaneGeometry(width, height), new THREE.MeshBasicMaterial({ map: texture, toneMapped: false }));
  const material = new THREE.MeshStandardMaterial({ map: texture, roughness: options.roughness ?? 0.85, side, transparent });
  if (glow) {
    material.emissive = new THREE.Color("#ffffff");
    material.emissiveMap = texture;
    material.emissiveIntensity = glow;
  }
  return new THREE.Mesh(new THREE.PlaneGeometry(width, height), material);
}

// Your phone's lock screen: the time, and Rita's message as a notification
function phoneTexture(THREE, face) {
  return canvasTexture(THREE, 512, 1024, (g, w, h) => {
    const sky = g.createLinearGradient(0, 0, w, h);
    sky.addColorStop(0, "#1d1b4a");
    sky.addColorStop(0.55, "#4a2a6a");
    sky.addColorStop(1, "#c4566e");
    g.fillStyle = sky;
    g.fillRect(0, 0, w, h);
    if (!face) return;
    g.fillStyle = "rgba(255,255,255,0.9)";
    g.textAlign = "center";
    g.font = `600 30px ${PRINT}`;
    g.fillText("🔒", w / 2, 92);
    g.font = `300 130px ${PRINT}`;
    g.fillText(face._time, w / 2, 230);
    // The notification
    g.font = `500 40px ${PRINT}`;
    const lines = wrapText(g, face.message, 420);
    const cardHeight = 130 + lines.length * 50;
    rounded(g, 16, 300, w - 32, cardHeight, 34);
    g.fillStyle = "rgba(250,250,252,0.96)";
    g.fill();
    rounded(g, 40, 324, 64, 64, 16);
    g.fillStyle = "#25d366";
    g.fill();
    g.fillStyle = "#ffffff";
    g.font = `38px ${PRINT}`;
    g.fillText("💬", 72, 370);
    g.textAlign = "left";
    g.fillStyle = "#111111";
    g.font = `700 42px ${PRINT}`;
    g.fillText(face.sender, 122, 370);
    g.textAlign = "right";
    g.fillStyle = "#6b6b75";
    g.font = `30px ${PRINT}`;
    g.fillText(face.when, w - 44, 368);
    g.textAlign = "left";
    g.fillStyle = "#15151c";
    g.font = `500 40px ${PRINT}`;
    lines.forEach((line, i) => g.fillText(line, 44, 448 + i * 50));
    // The torch and the camera, at the bottom
    for (const x of [90, w - 90]) {
      g.beginPath();
      g.arc(x, h - 100, 40, 0, Math.PI * 2);
      g.fillStyle = "rgba(255,255,255,0.18)";
      g.fill();
    }
  });
}

// Your laptop's login screen, at 3%
function laptopTexture(THREE, face) {
  return canvasTexture(THREE, 1024, 640, (g, w, h) => {
    const sky = g.createLinearGradient(0, 0, w, h);
    sky.addColorStop(0, "#0f2a5c");
    sky.addColorStop(1, "#1f7a8c");
    g.fillStyle = sky;
    g.fillRect(0, 0, w, h);
    if (!face) return;
    g.textAlign = "center";
    // The user's picture and the password field
    const cx = w * 0.33;
    g.beginPath();
    g.arc(cx, 210, 70, 0, Math.PI * 2);
    g.fillStyle = "rgba(255,255,255,0.85)";
    g.fill();
    g.fillStyle = "#1f3f6e";
    g.beginPath();
    g.arc(cx, 190, 26, 0, Math.PI * 2);
    g.fill();
    g.beginPath();
    g.arc(cx, 262, 46, Math.PI, 0);
    g.fill();
    rounded(g, cx - 170, 330, 340, 64, 12);
    g.fillStyle = "rgba(255,255,255,0.92)";
    g.fill();
    g.fillStyle = "#8a8f99";
    g.font = `32px ${PRINT}`;
    g.fillText(`${face.login}  ·  ••••`, cx, 373);
    // The battery, nearly empty, and its warning
    g.textAlign = "right";
    g.fillStyle = "#ff5a5a";
    g.font = `700 38px ${PRINT}`;
    g.fillText(`▮ ${face._battery}`, w - 40, 60);
    g.textAlign = "center";
    rounded(g, cx - 210, h - 130, 420, 70, 16);
    g.fillStyle = "rgba(200,40,50,0.9)";
    g.fill();
    g.fillStyle = "#ffffff";
    g.font = `600 34px ${PRINT}`;
    g.fillText(`⚠ ${face.low}`, cx, h - 83);
  });
}

// A post-it: handwriting on yellow paper
function postItTexture(THREE, text, sign, steps = []) {
  return canvasTexture(THREE, 512, 512, (g, w, h) => {
    g.fillStyle = "#ffe766";
    g.fillRect(0, 0, w, h);
    g.fillStyle = "rgba(0,0,0,0.05)";
    g.fillRect(0, 0, w, 60);
    g.fillStyle = "#2a2a6a";
    g.textAlign = "left";
    g.font = `46px ${HAND}`;
    let y = writeText(g, text, 30, 100, w - 60, 56);
    for (const step of steps) {
      g.fillText(step, 60, y + 10);
      y += 50;
    }
    if (sign) {
      g.textAlign = "right";
      g.fillText(sign, w - 34, Math.min(h - 30, y + 30));
    }
  });
}

// The whiteboard: the exercise in blue marker (or old smudges on the other board)
function whiteboardTexture(THREE, face) {
  return canvasTexture(THREE, 1280, 800, (g, w, h) => {
    g.fillStyle = "#fbfbfa";
    g.fillRect(0, 0, w, h);
    // Old, badly wiped marker
    g.strokeStyle = "rgba(120,130,150,0.12)";
    g.lineWidth = 26;
    for (let i = 0; i < 6; i++) {
      g.beginPath();
      g.moveTo(80 + i * 190, 120 + (i % 3) * 170);
      g.bezierCurveTo(200 + i * 160, 60, 300 + i * 120, 420, 500 + i * 110, 300 + (i % 2) * 260);
      g.stroke();
    }
    if (!face) return;
    g.textAlign = "left";
    g.fillStyle = "#c8343a";
    g.font = `700 64px ${HAND}`;
    g.fillText(`${face.title}:`, 90, 140);
    g.fillStyle = "#1d3c8f";
    g.font = `700 104px ${HAND}`;
    face._lines.forEach((line, i) => g.fillText(line, 140, 300 + i * 150));
  });
}

// A printed notice (A4)
function noticeTexture(THREE, face) {
  return canvasTexture(THREE, 600, 850, (g, w, h) => {
    g.fillStyle = "#fdfdfb";
    g.fillRect(0, 0, w, h);
    if (!face) return;
    g.fillStyle = "#c8343a";
    g.fillRect(0, 0, w, 130);
    g.fillStyle = "#ffffff";
    g.textAlign = "center";
    g.font = `800 66px ${PRINT}`;
    g.fillText(`⚡ ${face.title}`, w / 2, 90);
    g.fillStyle = "#1a1a1a";
    g.textAlign = "left";
    g.font = `44px ${PRINT}`;
    let y = writeText(g, face.text, 50, 230, w - 100, 58);
    g.font = `800 48px ${PRINT}`;
    y = writeText(g, face.extra, 50, y + 50, w - 100, 60);
    g.fillStyle = "#6b6b6b";
    g.font = `28px ${PRINT}`;
    g.fillText(face.from, 50, h - 50);
  });
}

// Mum's note: blue pen on a crumpled page of lined paper
function noteTexture(THREE, face) {
  return canvasTexture(THREE, 640, 480, (g, w, h) => {
    g.fillStyle = "#f7f3e6";
    g.fillRect(0, 0, w, h);
    g.strokeStyle = "rgba(80,130,200,0.35)";
    g.lineWidth = 2;
    for (let y = 70; y < h; y += 44) {
      g.beginPath();
      g.moveTo(0, y);
      g.lineTo(w, y);
      g.stroke();
    }
    g.strokeStyle = "rgba(200,60,60,0.4)";
    g.beginPath();
    g.moveTo(70, 0);
    g.lineTo(70, h);
    g.stroke();
    // Creases
    for (let i = 0; i < 14; i++) {
      g.fillStyle = `rgba(0,0,0,${0.02 + (i % 3) * 0.015})`;
      g.beginPath();
      g.moveTo((i * 97) % w, 0);
      g.lineTo(((i * 53) % w) + 60, h);
      g.lineTo(((i * 71) % w) + 20, h / 2);
      g.fill();
    }
    if (!face) return;
    g.fillStyle = "#1e2f8a";
    g.textAlign = "left";
    g.font = `36px ${HAND}`;
    const y = writeText(g, face.text, 86, 60, w - 120, 44);
    g.fillStyle = "#b1202a";
    g.font = `700 38px ${HAND}`;
    g.fillText(face.shout, 86, y + 4);
    g.fillRect(86, y + 14, Math.min(w - 120, g.measureText(face.shout).width), 4);
    g.fillStyle = "#1e2f8a";
    g.font = `36px ${HAND}`;
    g.textAlign = "right";
    g.fillText(face.sign, w - 40, y + 60);
  });
}

// The emergency plan of floor 0: the lockers, the stairs, "you are here" and the terrace door
function planTexture(THREE, face) {
  return canvasTexture(THREE, 800, 800, (g, w, h) => {
    g.fillStyle = "#ffffff";
    g.fillRect(0, 0, w, h);
    g.fillStyle = "#0f8a4a";
    g.fillRect(0, 0, w, 100);
    if (!face) return;
    g.fillStyle = "#ffffff";
    g.textAlign = "center";
    g.font = `800 50px ${PRINT}`;
    g.fillText(face.title, w / 2, 68);
    // The floor: walls, the lockers, the stairs
    g.strokeStyle = "#333333";
    g.lineWidth = 8;
    g.strokeRect(60, 150, 680, 480);
    g.fillStyle = "#d9dde2";
    g.fillRect(70, 160, 220, 50);
    g.fillStyle = "#333333";
    g.font = `28px ${PRINT}`;
    g.fillText(face.lockers, 180, 194);
    g.strokeStyle = "#555555";
    g.lineWidth = 3;
    for (let y = 240; y < 460; y += 22) {
      g.beginPath();
      g.moveTo(360, y);
      g.lineTo(460, y);
      g.stroke();
    }
    g.strokeRect(360, 240, 100, 220);
    g.fillText(face.stairs, 410, 490);
    // You are here
    g.fillStyle = "#c8343a";
    g.beginPath();
    g.arc(180, 300, 20, 0, Math.PI * 2);
    g.fill();
    g.font = `700 30px ${PRINT}`;
    g.fillText(face.here, 180, 360);
    // The way to the terrace door, in the right wall
    g.strokeStyle = "#0f8a4a";
    g.lineWidth = 10;
    g.setLineDash([22, 14]);
    g.beginPath();
    g.moveTo(205, 300);
    g.lineTo(560, 300);
    g.lineTo(560, 210);
    g.lineTo(700, 210);
    g.stroke();
    g.setLineDash([]);
    g.fillStyle = "#0f8a4a";
    g.beginPath();
    g.moveTo(740, 210);
    g.lineTo(700, 186);
    g.lineTo(700, 234);
    g.fill();
    g.fillStyle = "#ffffff";
    g.fillRect(732, 170, 16, 80);
    rounded(g, 470, 520, 250, 90, 12);
    g.fillStyle = "#0f8a4a";
    g.fill();
    g.fillStyle = "#ffffff";
    g.font = `800 46px ${PRINT}`;
    g.fillText(face.door, 595, 580);
    g.fillStyle = "#0f8a4a";
    g.font = `700 32px ${PRINT}`;
    g.fillText(`➜ ${face.exit}`, w / 2, 700);
  });
}

// The snack machine's glass: empty spirals, "sold out", and one sad bag of crisps
function snacksTexture(THREE, face) {
  return canvasTexture(THREE, 512, 900, (g, w, h) => {
    g.fillStyle = "#151a22";
    g.fillRect(0, 0, w, h);
    for (let row = 0; row < 5; row++) {
      const y = 70 + row * 165;
      g.fillStyle = "#59606b";
      g.fillRect(20, y + 110, w - 40, 8);
      for (let col = 0; col < 4; col++) {
        const x = 40 + col * 118;
        g.strokeStyle = "#9aa3ad";
        g.lineWidth = 4;
        for (let k = 0; k < 4; k++) {
          g.beginPath();
          g.ellipse(x + 40, y + 70 - k * 2, 30, 34, 0, 0, Math.PI * 2);
          g.stroke();
        }
        if (row === 3 && col === 1) {
          // The last bag of crisps
          g.fillStyle = "#ffcf2e";
          rounded(g, x + 8, y + 10, 66, 92, 10);
          g.fill();
          g.fillStyle = "#c8343a";
          g.fillRect(x + 8, y + 40, 66, 18);
        } else if (face) {
          g.save();
          g.translate(x + 40, y + 60);
          g.rotate(-0.35);
          g.fillStyle = "#c8343a";
          g.fillRect(-56, -16, 112, 32);
          g.fillStyle = "#ffffff";
          g.font = `800 20px ${PRINT}`;
          g.textAlign = "center";
          g.fillText(face.sold, 0, 7);
          g.restore();
        }
      }
    }
  });
}

// The cafeteria's chalk menu: the coffees and their prices, and the Wi-Fi rule underneath
function menuTexture(THREE, face) {
  return canvasTexture(THREE, 1024, 680, (g, w, h) => {
    g.fillStyle = "#1e2422";
    g.fillRect(0, 0, w, h);
    for (let i = 0; i < 30; i++) {
      g.fillStyle = `rgba(255,255,255,${0.015 + (i % 4) * 0.01})`;
      g.beginPath();
      g.arc((i * 137) % w, (i * 89) % h, 40 + (i % 5) * 25, 0, Math.PI * 2);
      g.fill();
    }
    if (!face) return;
    g.fillStyle = "#f6f2e4";
    g.textAlign = "center";
    g.font = `700 76px ${HAND}`;
    g.fillText(face.title, w / 2, 96);
    g.font = `52px ${HAND}`;
    face._coffees.forEach((coffee, i) => {
      const y = 196 + i * 78;
      g.textAlign = "left";
      g.fillText(coffee, 110, y);
      g.textAlign = "right";
      g.fillText(face.prices[i], w - 110, y);
      g.fillStyle = "rgba(246,242,228,0.5)";
      const from = 140 + g.measureText(coffee).width;
      for (let x = from; x < w - 280; x += 22) g.fillRect(x, y - 8, 6, 6);
      g.fillStyle = "#f6f2e4";
    });
    g.fillRect(110, 438, w - 220, 4);
    g.textAlign = "center";
    g.fillStyle = "#ffe08a";
    g.font = `700 50px ${HAND}`;
    g.fillText(`📶 ${face.wifi}`, w / 2, 510);
    g.fillStyle = "#f6f2e4";
    g.font = `40px ${HAND}`;
    writeText(g, face.rule, w / 2, 572, w - 160, 50);
  });
}

// A sticker on the coffee machine
function stickerTexture(THREE, face) {
  return canvasTexture(THREE, 512, 256, (g, w, h) => {
    g.fillStyle = "#ffffff";
    g.fillRect(0, 0, w, h);
    g.fillStyle = "#f08a24";
    g.fillRect(0, 0, w, 56);
    g.fillStyle = "#ffffff";
    g.textAlign = "center";
    g.font = `800 40px ${PRINT}`;
    g.fillText("⚠", w / 2, 44);
    if (!face) return;
    g.fillStyle = "#1a1a1a";
    g.font = `700 40px ${PRINT}`;
    writeText(g, face.text, w / 2, 120, w - 50, 50);
  });
}

// The metal sign by the terrace door
function signTexture(THREE, face) {
  return canvasTexture(THREE, 640, 480, (g, w, h) => {
    g.fillStyle = "#ffffff";
    g.fillRect(0, 0, w, h);
    g.strokeStyle = "#1d5fa8";
    g.lineWidth = 18;
    g.strokeRect(9, 9, w - 18, h - 18);
    // A sprinkler and its drops
    g.fillStyle = "#1d5fa8";
    g.fillRect(w / 2 - 14, 150, 28, 40);
    for (let i = 0; i < 9; i++) {
      const a = Math.PI + (i / 8) * Math.PI;
      g.beginPath();
      g.arc(w / 2 + Math.cos(a) * 95, 150 + Math.sin(a) * 85, 9, 0, Math.PI * 2);
      g.fill();
    }
    if (!face) return;
    g.textAlign = "center";
    g.font = `800 52px ${PRINT}`;
    g.fillText(face.title, w / 2, 280);
    g.fillStyle = "#1a1a1a";
    g.font = `600 46px ${PRINT}`;
    g.fillText(face.text, w / 2, 360);
  });
}

// --- The kinds of things, built from simple shapes. Each one gets an empty group placed in the
// room (turned to face the room when it hangs on a wall) and adds its shapes to it. ---------------

// A chair: a shell on thin legs (the library, the classrooms, the cafeteria)
function chair(THREE, box, color = "#4b4f55") {
  const g = new THREE.Group();
  const seat = box(0.46, 0.05, 0.44, color, { roughness: 0.6 });
  seat.position.y = 0.46;
  const back = box(0.46, 0.42, 0.05, color, { roughness: 0.6 });
  back.position.set(0, 0.7, -0.2);
  back.rotation.x = -0.12;
  g.add(seat, back);
  for (const [x, z] of [[-0.19, -0.17], [0.19, -0.17], [-0.19, 0.17], [0.19, 0.17]]) {
    const leg = box(0.025, 0.46, 0.025, "#b8bcc2", { metalness: 0.6, roughness: 0.3 });
    leg.position.set(x, 0.23, z);
    g.add(leg);
  }
  return g;
}

// Where the camera looks when the thing is examined close up: a point of the thing, the direction
// its face looks to, and the width and height to show (all in the thing's own coordinates)
function focusOn(group, at, normal, width, height) {
  group.userData.focus = { at, normal, width, height };
}

// An outline on the floor the character walks around, for things too big or too curved for one
// box (the rows of desks): [minX, maxX, minZ, maxZ] in the room's coordinates
function outline(group, points) {
  const xs = points.map((p) => p[0]);
  const zs = points.map((p) => p[1]);
  (group.userData.outlines ??= []).push([Math.min(...xs), Math.max(...xs), Math.min(...zs), Math.max(...zs)]);
}

// Many copies of one shape in one draw call (chairs, spotlights, railing bars)
function copies(THREE, geometry, material, placements) {
  const mesh = new THREE.InstancedMesh(geometry, material, placements.length);
  const m = new THREE.Matrix4();
  const q = new THREE.Quaternion();
  const s = new THREE.Vector3(1, 1, 1);
  placements.forEach(([x, y, z, turn = 0], i) => {
    q.setFromAxisAngle(new THREE.Vector3(0, 1, 0), turn);
    m.compose(new THREE.Vector3(x, y, z), q, s);
    mesh.setMatrixAt(i, m);
  });
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return mesh;
}

const THINGS = {
  // --- Study Room B, the amphitheatre (photo 4) ---
  oak_wall({ THREE, group, thing, H }) {
    // Smooth oak panels, in long horizontal boards
    const texture = canvasTexture(THREE, 1024, 512, (g, w, h) => {
      g.fillStyle = "#a8723f";
      g.fillRect(0, 0, w, h);
      for (let y = 0; y < h; y += 64) {
        g.fillStyle = y % 128 ? "rgba(255,220,170,0.06)" : "rgba(60,30,10,0.06)";
        g.fillRect(0, y, w, 64);
        g.fillStyle = "rgba(50,25,8,0.45)";
        g.fillRect(0, y, w, 2);
        for (let i = 0; i < 18; i++) {
          g.fillStyle = `rgba(80,40,15,${0.05 + (i % 3) * 0.03})`;
          g.fillRect(((i * 211 + y * 7) % w), y + 6 + (i % 5) * 11, 120 + (i % 4) * 90, 2);
        }
      }
    });
    const wall = sheet(THREE, texture, thing.width, H, { roughness: 0.5 });
    wall.position.set(0, H / 2, 0.02);
    group.add(wall);
  },

  dark_panel({ group, box }) {
    // The big dark panel in the oak wall
    const panel = box(2.5, 2.7, 0.06, "#252427", { roughness: 0.8 });
    panel.position.set(0, 1.35, 0.04);
    const trim = box(2.62, 2.8, 0.03, "#141415");
    trim.position.set(0, 1.4, 0.02);
    group.add(trim, panel);
  },

  wall_clock({ THREE, group, thing, animated }) {
    const face = new THREE.Mesh(new THREE.CircleGeometry(0.3, 32), new THREE.MeshStandardMaterial({ color: "#ffffff" }));
    face.position.set(0, 3.15, 0.08);
    const rim = new THREE.Mesh(new THREE.TorusGeometry(0.3, 0.03, 8, 32), new THREE.MeshStandardMaterial({ color: "#222222" }));
    rim.position.copy(face.position);
    const [h, m] = thing.time.split(":").map(Number);
    const hand = (length, width, angle) => {
      const pivot = new THREE.Group();
      const stick = new THREE.Mesh(new THREE.BoxGeometry(width, length, 0.01), new THREE.MeshBasicMaterial({ color: "#111111" }));
      stick.position.y = length / 2;
      pivot.add(stick);
      pivot.position.set(0, 3.15, 0.09);
      pivot.rotation.z = -angle;
      return pivot;
    };
    const hours = hand(0.16, 0.03, ((h % 12) + m / 60) * (Math.PI / 6));
    const minutes = hand(0.24, 0.02, m * (Math.PI / 30));
    const seconds = hand(0.25, 0.008, 0);
    seconds.children[0].material = new THREE.MeshBasicMaterial({ color: "#c8343a" });
    group.add(face, rim, hours, minutes, seconds);
    animated.push((dt, time) => (seconds.rotation.z = -(Math.floor(time) % 60) * (Math.PI / 30)));
  },

  spot_arcs({ THREE, group, thing, W, D, H }) {
    // Spotlights in the ceiling, in curves that follow the rows of desks
    const [cx, cz] = thing.at;
    const places = [];
    for (const r of thing.radii) {
      for (let a = -Math.PI; a < Math.PI; a += 0.75 / r) {
        const x = r * Math.sin(a);
        const z = r * Math.cos(a);
        if (Math.abs(cx + x) < W / 2 - 0.4 && Math.abs(cz + z) < D / 2 - 0.4) places.push([x, H - 0.01, z]);
      }
    }
    const disc = new THREE.CircleGeometry(0.06, 14);
    disc.rotateX(Math.PI / 2);
    group.add(copies(THREE, disc, new THREE.MeshBasicMaterial({ color: "#fffbe8" }), places));
  },

  desk_arc({ THREE, group, box, thing }) {
    // A row of white desks along an arc, with black chairs behind, all facing the whiteboards.
    // The group stands at the arc's centre; local +z is the front of the room.
    const r = thing.radius;
    const pieces = Math.max(2, Math.round(((thing.to - thing.from) * r) / 0.92));
    const step = (thing.to - thing.from) / pieces;
    const chord = 2 * r * Math.sin(step / 2) + 0.02;
    const [cx, cz] = thing.at;
    const seats = [];
    const backs = [];
    const posts = [];
    for (let i = 0; i < pieces; i++) {
      const a = thing.from + (i + 0.5) * step;
      const top = box(chord, 0.05, 0.62, WHITE, { roughness: 0.35 });
      top.position.set(r * Math.sin(a), 0.76, r * Math.cos(a));
      top.rotation.y = a;
      const front = box(chord, 0.72, 0.04, WHITE, { roughness: 0.5 });
      front.position.set((r - 0.29) * Math.sin(a), 0.38, (r - 0.29) * Math.cos(a));
      front.rotation.y = a;
      group.add(top, front);
      for (const da of [-step / 4, step / 4]) {
        const b = a + da;
        if ((thing.skip || []).some((s) => Math.abs(s - b) < 0.05)) continue;
        const cr = r + 0.6;
        seats.push([cr * Math.sin(b), 0.47, cr * Math.cos(b), b + Math.PI]);
        backs.push([(cr + 0.22) * Math.sin(b), 0.74, (cr + 0.22) * Math.cos(b), b + Math.PI]);
        posts.push([cr * Math.sin(b), 0.23, cr * Math.cos(b), b]);
      }
      // What the character walks around: the desk, then the chairs behind it, in short pieces so
      // the boxes hug the curve (the aisles between the rows stay free)
      const cuts = Math.max(1, Math.ceil(chord / 0.4));
      for (let k = 0; k < cuts; k++) {
        const a1 = a - step / 2 + (k * step) / cuts;
        const a2 = a1 + step / cuts;
        for (const [r1, r2] of [[r - 0.34, r + 0.32], [r + 0.32, r + 0.88]]) {
          const corners = [];
          for (const rr of [r1, r2]) for (const aa of [a1, a2]) corners.push([cx + rr * Math.sin(aa), cz + rr * Math.cos(aa)]);
          outline(group, corners);
        }
      }
    }
    const black = new THREE.MeshStandardMaterial({ color: "#1b1c20", roughness: 0.55 });
    const chrome = new THREE.MeshStandardMaterial({ color: "#c2c6cc", metalness: 0.7, roughness: 0.3 });
    group.add(copies(THREE, new THREE.BoxGeometry(0.46, 0.05, 0.44), black, seats));
    const backShape = new THREE.BoxGeometry(0.46, 0.5, 0.05);
    backShape.rotateX(0.12);
    group.add(copies(THREE, backShape, black, backs));
    group.add(copies(THREE, new THREE.CylinderGeometry(0.025, 0.025, 0.46, 8), chrome, posts));
  },

  whiteboard({ THREE, group, thing, face }) {
    // A whiteboard in an aluminium frame, with its tray of markers
    const texture = whiteboardTexture(THREE, thing.plain ? null : face);
    const board = sheet(THREE, texture, 2.0, 1.25, { roughness: 0.75 });
    board.position.set(0, 1.7, 0.035);
    const frame = new THREE.Mesh(new THREE.BoxGeometry(2.08, 1.33, 0.03), new THREE.MeshStandardMaterial({ color: "#c9ccd2", metalness: 0.5, roughness: 0.3 }));
    frame.position.set(0, 1.7, 0.015);
    const tray = new THREE.Mesh(new THREE.BoxGeometry(2.0, 0.04, 0.1), new THREE.MeshStandardMaterial({ color: "#b0b4ba", metalness: 0.5 }));
    tray.position.set(0, 1.05, 0.07);
    group.add(frame, board, tray);
    for (const [x, colour] of [[-0.5, "#1d3c8f"], [-0.38, "#c8343a"]]) {
      const marker = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.13, 8), new THREE.MeshStandardMaterial({ color: colour }));
      marker.rotation.z = Math.PI / 2;
      marker.position.set(x, 1.08, 0.08);
      group.add(marker);
    }
    focusOn(group, [0, 1.7, 0.04], [0, 0, 1], 2.2, 1.4);
  },

  lectern({ group, box }) {
    const body = box(0.9, 1.05, 0.6, WHITE, { roughness: 0.4 });
    body.position.y = 0.525;
    const top = box(0.95, 0.04, 0.66, "#e5e4df");
    top.position.y = 1.07;
    group.add(body, top);
  },

  tiago_sleeping({ THREE, group, box, animated }) {
    // Tiago, asleep on a Finance textbook, with "Zzz" rising
    const person = makePerson(THREE, { hoodie: "#7a2f3a", hair: "#5a3a1a", sleeping: true });
    person.group.position.set(0, 0, 0.6);
    person.group.rotation.y = Math.PI;
    const book = box(0.32, 0.05, 0.24, "#1f5c8a");
    book.position.set(0, 0.81, 0.1);
    group.add(person.group, book);
    const z = textTexture(THREE, ["z Z z"], { width: 256, height: 128, background: "rgba(0,0,0,0)", color: "#ffffff", font: "bold 64px sans-serif" });
    const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: z, transparent: true, depthWrite: false }));
    sprite.scale.set(0.6, 0.3, 1);
    group.add(sprite);
    animated.push((dt, time) => {
      person.animate(dt, time, false);
      const t = (time * 0.4) % 1;
      sprite.position.set(0.2 + Math.sin(time) * 0.05, 1.3 + t * 0.6, 0.35);
      sprite.material.opacity = 1 - t;
    });
  },

  laptop({ THREE, group, box, face }) {
    // Your laptop on the desk, at 3%, with Tiago's post-it stuck on the screen
    const base = box(0.36, 0.02, 0.25, "#9aa0a8", { metalness: 0.6, roughness: 0.3 });
    base.position.set(0, 0.8, 0.0);
    const lid = new THREE.Group();
    lid.position.set(0, 0.81, -0.125);
    lid.rotation.x = -0.25;
    const back = box(0.36, 0.24, 0.012, "#9aa0a8", { metalness: 0.6, roughness: 0.3 });
    back.position.set(0, 0.12, -0.007);
    const screen = sheet(THREE, laptopTexture(THREE, face), 0.33, 0.206, { screen: true });
    screen.position.set(0, 0.125, 0.0);
    lid.add(back, screen);
    if (face) {
      const note = sheet(THREE, postItTexture(THREE, face.postit, face.sign), 0.12, 0.12);
      note.position.set(0.095, 0.115, 0.003);
      note.rotation.z = -0.06;
      lid.add(note);
    }
    group.add(base, lid);
    const n = new THREE.Vector3(0, Math.sin(0.25), Math.cos(0.25));
    focusOn(group, [0, 0.81 + 0.125 * Math.cos(0.25), -0.125 - 0.125 * Math.sin(0.25)], [n.x, n.y, n.z], 0.42, 0.3);
  },

  phone({ THREE, group, box, face, animated }) {
    // Your phone, face up, lighting up with Rita's message
    const phone = box(0.078, 0.009, 0.158, "#111111", { roughness: 0.3 });
    phone.position.set(0, 0.795, 0.05);
    const screen = sheet(THREE, phoneTexture(THREE, face), 0.07, 0.148, { screen: true });
    screen.rotation.x = -Math.PI / 2;
    screen.position.set(0, 0.8005, 0.05);
    group.add(phone, screen);
    // It lights up now and then: a new message
    const glow = new THREE.PointLight("#bcd6ff", 0, 0.8, 2);
    glow.position.set(0, 0.9, 0.05);
    group.add(glow);
    animated.push((dt, time) => (glow.intensity = Math.max(0, Math.sin(time * 3)) * 0.8));
    focusOn(group, [0, 0.8, 0.05], [0, 1, 0.12], 0.1, 0.16);
  },

  chair_coat({ THREE, group, box }) {
    // Your chair, pulled out, with your yellow raincoat over its back
    const seat = chair(THREE, box, "#1b1c20");
    seat.rotation.y = Math.PI;
    group.add(seat);
    const coat = box(0.5, 0.75, 0.1, "#f2c230", { roughness: 0.35 });
    coat.position.set(0, 0.62, 0.24);
    coat.rotation.x = 0.1;
    const sleeve = box(0.12, 0.5, 0.1, "#e0b021", { roughness: 0.35 });
    sleeve.position.set(0.3, 0.48, 0.2);
    group.add(coat, sleeve);
  },

  notice({ THREE, group, face }) {
    // A sheet of A4 taped to the wall
    const paper = sheet(THREE, noticeTexture(THREE, face), 0.42, 0.595);
    paper.position.set(0, 1.55, 0.02);
    group.add(paper);
    for (const [x, y] of [[-0.19, 1.83], [0.19, 1.83]]) {
      const tape = new THREE.Mesh(new THREE.PlaneGeometry(0.08, 0.03), new THREE.MeshStandardMaterial({ color: "#efe7c8", transparent: true, opacity: 0.8 }));
      tape.position.set(x, y, 0.025);
      tape.rotation.z = x < 0 ? 0.5 : -0.5;
      group.add(tape);
    }
    focusOn(group, [0, 1.55, 0.02], [0, 0, 1], 0.5, 0.68);
  },

  door({ THREE, group, box, thing }) {
    // A door in a wall: dark grey (or glass), with a card reader that lights up
    const frame = box(1.3, 2.4, 0.12, "#3b3d42");
    frame.position.set(0, 1.2, 0.04);
    const leaf = box(1.1, 2.25, 0.06, thing.glass ? "#9fb8c8" : "#5d6168", thing.glass ? { transparent: true, opacity: 0.45, metalness: 0.4, roughness: 0.1 } : { roughness: 0.5 });
    leaf.position.set(0, 1.13, 0.09);
    const handle = box(0.04, 0.3, 0.05, "#d0d3d8", { metalness: 0.8, roughness: 0.2 });
    handle.position.set(0.42, 1.05, 0.14);
    const reader = box(0.1, 0.16, 0.04, "#1c1c22");
    reader.position.set(0.75, 1.2, 0.08);
    const led = new THREE.Mesh(new THREE.SphereGeometry(0.015, 8, 6), new THREE.MeshBasicMaterial({ color: "#3bff6a" }));
    led.position.set(0.75, 1.26, 0.1);
    group.add(frame, leaf, handle, reader, led);
  },

  exit_sign({ THREE, group }) {
    // The green emergency exit sign over a door
    const texture = canvasTexture(THREE, 256, 96, (g, w, h) => {
      g.fillStyle = "#11934f";
      g.fillRect(0, 0, w, h);
      g.fillStyle = "#ffffff";
      g.font = "64px sans-serif";
      g.textAlign = "center";
      g.fillText("🏃 ➜ ▯", w / 2, 70);
    });
    const sign = sheet(THREE, texture, 0.42, 0.16, { glow: 1.1 });
    sign.position.set(0, 2.62, 0.06);
    group.add(sign);
  },

  // --- The locker corridor, floor 0 of the library (photo 2) ---
  lockers({ group, box, thing }) {
    const width = thing.width;
    const count = Math.round(width / 0.5);
    for (let i = 0; i < count; i++) {
      const x = -width / 2 + (i + 0.5) * (width / count);
      for (const [y, h] of [[0.55, 1.0], [1.6, 1.0]]) {
        const door = box(width / count - 0.02, h - 0.02, 0.5, "#8d949c", { metalness: 0.45, roughness: 0.45 });
        door.position.set(x, y, 0.25);
        const vent = box(0.25, 0.08, 0.01, "#5d636a");
        vent.position.set(x, y + 0.32, 0.505);
        const handle = box(0.04, 0.14, 0.02, "#d6d9de", { metalness: 0.8 });
        handle.position.set(x + 0.15, y, 0.51);
        group.add(door, vent, handle);
      }
    }
  },

  rita_locker({ THREE, group, box, thing, animated }) {
    // Rita's locker: a sticker, and a 5-digit padlock (or the door hanging open)
    const body = box(0.5, 1.0, 0.52, "#2c6db0", { metalness: 0.4, roughness: 0.45 });
    body.position.set(0, 1.6, 0.26);
    group.add(body);
    const sticker = textTexture(THREE, ["RITA ✿"], { width: 256, height: 96, background: "#ffe14d", color: "#2a1a05", font: "bold 44px sans-serif" });
    const label = new THREE.Mesh(new THREE.PlaneGeometry(0.3, 0.11), new THREE.MeshStandardMaterial({ map: sticker }));
    if (thing.open) {
      body.scale.z = 0.98;
      const door = box(0.48, 0.98, 0.03, "#2c6db0", { metalness: 0.4 });
      door.position.set(-0.45, 1.6, 0.62);
      door.rotation.y = -1.2;
      label.position.set(-0.47, 1.85, 0.66);
      label.rotation.y = -1.2;
      const inside = box(0.44, 0.9, 0.02, "#1a1d22");
      inside.position.set(0, 1.6, 0.53);
      group.add(door, inside, label);
    } else {
      label.position.set(0, 1.85, 0.525);
      const lock = box(0.12, 0.14, 0.05, "#c9a227", { metalness: 0.8, roughness: 0.25 });
      lock.position.set(0.15, 1.5, 0.56);
      const shackle = new THREE.Mesh(new THREE.TorusGeometry(0.04, 0.01, 6, 16, Math.PI), new THREE.MeshStandardMaterial({ color: "#c9ccd2", metalness: 0.9 }));
      shackle.position.set(0.15, 1.57, 0.56);
      group.add(label, lock, shackle);
      animated.push((dt, time) => (lock.rotation.z = Math.sin(time * 2) * 0.05));
    }
  },

  floor_note({ THREE, group, face }) {
    // Mum's note, crumpled, on the floor
    const note = sheet(THREE, noteTexture(THREE, face), 0.3, 0.225, { side: THREE.DoubleSide });
    note.rotation.x = -Math.PI / 2;
    note.rotation.z = 0.12;
    note.position.y = 0.012;
    group.add(note);
    focusOn(group, [0, 0.012, 0], [0, 1, 0.1], 0.36, 0.3);
  },

  emergency_plan({ THREE, group, face }) {
    // The emergency plan, green and white, behind glass
    const plan = sheet(THREE, planTexture(THREE, face), 0.6, 0.6, { roughness: 0.7 });
    plan.position.set(0, 1.65, 0.02);
    const frame = new THREE.Mesh(new THREE.BoxGeometry(0.66, 0.66, 0.02), new THREE.MeshStandardMaterial({ color: "#2b2b2b" }));
    frame.position.set(0, 1.65, 0.005);
    group.add(frame, plan);
    focusOn(group, [0, 1.65, 0.02], [0, 0, 1], 0.7, 0.72);
  },

  snack_machine({ THREE, group, box, face }) {
    const body = box(0.95, 1.9, 0.8, "#c8343a", { roughness: 0.4 });
    body.position.set(0, 0.95, 0.4);
    const glass = sheet(THREE, snacksTexture(THREE, face), 0.62, 1.1, { glow: 0.35, roughness: 0.7 });
    glass.position.set(-0.1, 1.2, 0.805);
    const slot = box(0.18, 0.5, 0.02, "#222222");
    slot.position.set(0.32, 1.2, 0.81);
    const tray = box(0.6, 0.18, 0.02, "#111111");
    tray.position.set(-0.1, 0.38, 0.81);
    const light = new THREE.PointLight("#8fd0ff", 2, 2.5, 2);
    light.position.set(0, 1.2, 1.3);
    group.add(body, glass, slot, tray, light);
    focusOn(group, [-0.05, 1.2, 0.81], [0, 0, 1], 0.95, 1.3);
  },

  staircase({ THREE, group, thing, box, H }) {
    // The big staircase of the library, "STATE YOUR MIND AND MIND YOUR STEP" in black on the white
    // risers, going up towards the back and through the ceiling; glass on its right, a white wall
    // on its left
    const rise = 0.3;
    const run = 0.3;
    const steps = Math.round(H / rise);
    const width = 2.6;
    const words = thing.words || [];
    const white = new THREE.MeshStandardMaterial({ color: "#f6f6f4", roughness: 0.7 });
    for (let i = 0; i < steps; i++) {
      const y = i * rise;
      const z = -i * run;
      const tread = box(width, 0.05, run + 0.03, "#d9c29c", { roughness: 0.55 });
      tread.position.set(0, y + rise, z - run / 2);
      // The bottom riser says STEP, the one above YOUR, ... STATE on the seventh
      const word = words[words.length - 1 - i] || "";
      const riserMaterial = word
        ? new THREE.MeshStandardMaterial({
            map: textTexture(THREE, [word], { width: 1024, height: 118, background: "#f6f6f4", color: "#111111", font: "900 104px 'Arial Black', Arial, sans-serif" }),
            roughness: 0.7,
          })
        : white;
      const riser = new THREE.Mesh(new THREE.BoxGeometry(width, rise, 0.03), [white, white, white, white, riserMaterial, white]);
      riser.position.set(0, y + rise / 2, z);
      group.add(tread, riser);
    }
    const length = steps * run;
    const slope = Math.atan2(steps * rise, length);
    const diagonal = Math.hypot(steps * rise, length);
    // The white wall on the left, and the glass with its handrail on the right
    const wall = box(0.12, 1.1, diagonal, "#f4f3ef");
    wall.position.set(-width / 2 - 0.06, (steps * rise) / 2 + 0.55, -length / 2);
    wall.rotation.x = slope;
    const under = box(width, 0.2, diagonal, "#efeeea");
    under.position.set(0, (steps * rise) / 2 - 0.1, -length / 2 - 0.05);
    under.rotation.x = slope;
    const glass = box(0.025, 1.0, diagonal, "#bcd6e6", { transparent: true, opacity: 0.22, metalness: 0.3, roughness: 0.05 });
    glass.position.set(width / 2 + 0.03, (steps * rise) / 2 + 0.6, -length / 2);
    glass.rotation.x = slope;
    const rail = box(0.05, 0.05, diagonal, "#d0d3d8", { metalness: 0.8, roughness: 0.25 });
    rail.position.set(width / 2 + 0.03, (steps * rise) / 2 + 1.1, -length / 2);
    rail.rotation.x = slope;
    group.add(wall, under, glass, rail);
  },

  column({ group, box, cylinder, thing, H }) {
    // A white column (round ones under the walkway outside), or the black one by the stairs
    const height = thing.height || H;
    const colour = thing.colour || "#f6f6f3";
    const shaft = thing.round ? cylinder(0.17, 0.17, height, colour, { roughness: 0.5 }, 18) : box(0.45, height, 0.45, colour, { roughness: 0.6 });
    shaft.position.y = height / 2;
    group.add(shaft);
    if (thing.round) {
      const foot = cylinder(0.27, 0.3, 0.12, colour, {}, 18);
      foot.position.y = 0.06;
      group.add(foot);
    }
  },

  window_wall({ THREE, group, box, thing, H }) {
    // Tall windows to the night, with the exhibition's black and white posters hanging in front
    const width = thing.width;
    const night = canvasTexture(THREE, 1024, 512, (g, w, h) => {
      const sky = g.createLinearGradient(0, 0, 0, h);
      sky.addColorStop(0, "#060a1a");
      sky.addColorStop(0.7, "#152048");
      sky.addColorStop(1, "#1d2338");
      g.fillStyle = sky;
      g.fillRect(0, 0, w, h);
      // The terrace outside: a railing and the lamps
      g.fillStyle = "#2a3048";
      g.fillRect(0, h * 0.82, w, h * 0.18);
      g.strokeStyle = "rgba(200,205,220,0.35)";
      g.lineWidth = 2;
      for (let x = 0; x < w; x += 14) {
        g.beginPath();
        g.moveTo(x, h * 0.66);
        g.lineTo(x, h * 0.82);
        g.stroke();
      }
      for (let i = 0; i < 40; i++) {
        g.fillStyle = i % 4 ? "#ffd58a" : "#bfe0ff";
        g.fillRect((i * 97) % w, h * 0.6 + ((i * 13) % 20), 3, 3);
      }
    });
    const glass = sheet(THREE, night, width, H - 0.5, { glow: 0.6, roughness: 0.1 });
    glass.position.set(0, (H - 0.5) / 2 + 0.1, 0.02);
    group.add(glass);
    for (let x = -width / 2; x <= width / 2 + 0.01; x += width / 7) {
      const mullion = box(0.06, H - 0.4, 0.08, "#d8d9db", { metalness: 0.5 });
      mullion.position.set(x, (H - 0.4) / 2 + 0.1, 0.05);
      group.add(mullion);
    }
    const sill = box(width, 0.1, 0.12, "#d8d9db");
    sill.position.set(0, 1.2, 0.06);
    group.add(sill);
    const titles = ["Dividends and Dreams", "Nova SBE · 1978", "Carcavelos"];
    for (let i = 0; i < (thing.posters || 0); i++) {
      const x = -width / 2 + ((i + 0.5) * width) / thing.posters;
      const poster = canvasTexture(THREE, 360, 520, (g, w, h) => {
        g.fillStyle = "#f1efe9";
        g.fillRect(0, 0, w, h);
        g.fillStyle = "#1a1a1a";
        g.font = `700 30px Georgia, serif`;
        g.fillText(titles[i % titles.length], 20, 50);
        const photo = g.createLinearGradient(0, 80, 0, 440);
        photo.addColorStop(0, "#5a5a5a");
        photo.addColorStop(1, "#1e1e1e");
        g.fillStyle = photo;
        g.fillRect(20, 80, w - 40, 360);
        g.fillStyle = "#9a9a9a";
        for (let k = 0; k < 4; k++) {
          g.beginPath();
          g.arc(70 + k * 75, 300 - (k % 2) * 40, 26, 0, Math.PI * 2);
          g.fill();
          g.fillRect(48 + k * 75, 326 - (k % 2) * 40, 44, 110);
        }
        g.fillStyle = "#555555";
        g.font = `20px Georgia, serif`;
        g.fillText("Exhibition · Library", 20, 480);
      });
      const sheetMesh = sheet(THREE, poster, 1.0, 1.44);
      sheetMesh.position.set(x, 2.4, 0.45);
      group.add(sheetMesh);
      for (const dx of [-0.45, 0.45]) {
        const wire = box(0.006, H - 3.1, 0.006, "#bfc3c8");
        wire.position.set(x + dx, 3.12 + (H - 3.1) / 2, 0.45);
        group.add(wire);
      }
    }
  },

  sofa({ group, box }) {
    // A low dark grey sofa, its back to the window
    const colour = "#2c2d31";
    const seat = box(2.3, 0.42, 0.85, colour, { roughness: 0.9 });
    seat.position.set(0, 0.21, 0.42);
    const back = box(2.3, 0.75, 0.22, colour, { roughness: 0.9 });
    back.position.set(0, 0.38, 0.0);
    group.add(seat, back);
    for (const x of [-1.1, 1.1]) {
      const arm = box(0.16, 0.6, 0.85, shade(colour, -0.15), { roughness: 0.9 });
      arm.position.set(x, 0.3, 0.42);
      group.add(arm);
    }
  },

  round_table({ THREE, group, box, cylinder, thing }) {
    // A round white table on one leg, with grey shell chairs round it (or a small side table)
    const radius = thing.small ? 0.32 : 0.5;
    const top = cylinder(radius, radius, 0.04, "#f7f7f5", { roughness: 0.4 }, 28);
    top.position.y = thing.small ? 0.5 : 0.74;
    const leg = cylinder(0.04, 0.04, top.position.y, "#e6e6e3", {}, 10);
    leg.position.y = top.position.y / 2;
    const foot = cylinder(0.25, 0.25, 0.03, "#e6e6e3", {}, 20);
    foot.position.y = 0.015;
    group.add(top, leg, foot);
    for (let i = 0; i < (thing.chairs || 0); i++) {
      const a = (i / thing.chairs) * Math.PI * 2 + 0.4;
      const c = chair(THREE, box, "#8e9196");
      c.position.set(Math.sin(a) * 0.85, 0, Math.cos(a) * 0.85);
      c.rotation.y = a + Math.PI;
      group.add(c);
    }
  },

  beanbag({ THREE, group, thing }) {
    // A black leather beanbag, slumped (floor 0 of the library)
    const leather = new THREE.MeshStandardMaterial({ color: "#121214", roughness: 0.32, metalness: 0.08 });
    const seat = new THREE.Mesh(new THREE.SphereGeometry(0.5, 20, 14), leather);
    seat.scale.set(1.05, 0.55, 1);
    seat.position.y = 0.28;
    const back = new THREE.Mesh(new THREE.SphereGeometry(0.4, 18, 12), leather);
    back.scale.set(1.1, 1.0, 0.6);
    back.position.set(0, 0.55, -0.32);
    group.add(seat, back);
    group.rotation.y = ((thing.at[0] * 7 + thing.at[1] * 3) % 6) - 3;
  },

  guard({ THREE, group, thing, animated, H }) {
    // The security guard, torch in hand. In the round he comes down the stairs towards you.
    const person = makePerson(THREE, { guard: true, skin: "#c99572" });
    group.add(person.group);
    const start = group.position.clone();
    const end = thing.stand ? new THREE.Vector3(thing.stand[0] + 0.6, 0, thing.stand[1] - 1.4) : start;
    let t = 0;
    animated.push((dt, time, heroAt) => {
      if (thing.walking) {
        t = Math.min(1, t + dt / 8);
        group.position.lerpVectors(start, end, t);
        // On the stairs, one step up for every step back (the first step is at stairs_from)
        if (thing.stairs_from !== undefined) group.position.y = Math.max(0, Math.min(H, thing.stairs_from - group.position.z));
        if (heroAt) group.rotation.y = Math.atan2(heroAt.x - group.position.x, heroAt.z - group.position.z) + Math.sin(time * 1.5) * 0.4;
      }
      person.animate(dt, time, thing.walking && t < 1);
    });
  },

  // --- The cafeteria, floor 1 of the library (photo 1) ---
  bookshelf({ THREE, group, box, thing }) {
    // A white bookshelf full of books, like the library's first floor (books on both sides if it
    // stands in the room). All its books are one shape drawn many times (one draw call).
    const shelf = box(2.4, 1.9, thing.double ? 0.6 : 0.42, "#f7f7f5", { roughness: 0.5 });
    shelf.position.set(0, 0.95, thing.double ? 0 : 0.21);
    group.add(shelf);
    const colours = ["#2c3e66", "#7a2f3a", "#d8c49a", "#3a6b4f", "#1d1d1d", "#b8562e", "#5b6f99", "#e3d9c0"];
    const books = [];
    for (const side of thing.double ? [1, -1] : [1]) {
      for (let row = 0; row < 4; row++) {
        let x = -1.1;
        let i = row * 3 + (side < 0 ? 5 : 0);
        while (x < 1.05) {
          const w = 0.04 + ((i * 7) % 5) * 0.012;
          const h = 0.26 + ((i * 3) % 4) * 0.025;
          books.push({ x: x + w / 2, y: 0.14 + row * 0.44 + h / 2, z: thing.double ? side * 0.305 : 0.425, w, h, colour: colours[i % colours.length] });
          x += w + 0.006;
          i += 1;
        }
      }
    }
    const mesh = new THREE.InstancedMesh(new THREE.BoxGeometry(1, 1, 1), new THREE.MeshStandardMaterial({ roughness: 0.8 }), books.length);
    const m = new THREE.Matrix4();
    books.forEach((b, k) => {
      mesh.setMatrixAt(k, m.makeScale(b.w, b.h, 0.02).setPosition(b.x, b.y, b.z));
      mesh.setColorAt(k, new THREE.Color(b.colour));
    });
    group.add(mesh);
  },

  long_table({ THREE, group, box, thing }) {
    // A long white study table; the grey chairs upside down on top (closed), or round it
    const top = box(3.2, 0.05, 0.95, "#f7f7f5", { roughness: 0.35 });
    top.position.y = 0.75;
    group.add(top);
    for (const x of [-1.45, 1.45]) {
      const leg = box(0.05, 0.72, 0.85, "#f0efec");
      leg.position.set(x, 0.37, 0);
      group.add(leg);
    }
    for (const x of [-1.0, 0, 1.0]) {
      for (const side of [-1, 1]) {
        const c = chair(THREE, box, "#6b6f75");
        if (thing.chairs_down) {
          c.position.set(x, 0, side * 0.75);
          c.rotation.y = side > 0 ? Math.PI : 0;
        } else {
          c.rotation.x = Math.PI;
          c.rotation.y = side > 0 ? Math.PI : 0;
          c.position.set(x, 1.7, side * 0.2);
        }
        group.add(c);
      }
    }
  },

  atrium({ THREE, group, box, thing }) {
    // The atrium: a white parapet round the opening to the floor below, grey chairs along it
    const { width, depth } = thing;
    const white = "#f4f3ef";
    for (const [w, d, x, z] of [[width, 0.3, 0, -depth / 2], [width, 0.3, 0, depth / 2], [0.3, depth, -width / 2, 0], [0.3, depth, width / 2, 0]]) {
      const wall = box(w, 1.0, d, white, { roughness: 0.45 });
      wall.position.set(x, 0.5, z);
      const top = box(w + 0.2, 0.05, d + 0.2, "#fbfbf9", { roughness: 0.3 });
      top.position.set(x, 1.02, z);
      group.add(wall, top);
    }
    // The opening: dark, with a glow from the floor below (its inner sides are in shadow too)
    const shadowSide = new THREE.MeshBasicMaterial({ color: "#1a1c24" });
    for (const [w, x, z, turn] of [[width - 0.32, 0, -depth / 2 + 0.16, 0], [width - 0.32, 0, depth / 2 - 0.16, Math.PI], [depth - 0.32, -width / 2 + 0.16, 0, Math.PI / 2], [depth - 0.32, width / 2 - 0.16, 0, -Math.PI / 2]]) {
      const side = new THREE.Mesh(new THREE.PlaneGeometry(w, 0.99), shadowSide);
      side.position.set(x, 0.5, z);
      side.rotation.y = turn;
      group.add(side);
    }
    const hole = new THREE.Mesh(new THREE.PlaneGeometry(width - 0.3, depth - 0.3), new THREE.MeshBasicMaterial({ color: "#0b0b10" }));
    hole.rotation.x = -Math.PI / 2;
    hole.position.y = 0.02;
    const glow = new THREE.PointLight("#9fc4ff", 2, 3, 2);
    glow.position.set(0, 0.6, 0);
    group.add(hole, glow);
    for (let x = -width / 2 + 0.5; x < width / 2; x += 0.75) {
      const c = chair(THREE, box, "#5a5e64");
      c.position.set(x, 0, -depth / 2 - 0.55);
      group.add(c);
    }
  },

  counter({ group, box, thing }) {
    const width = thing.width;
    const body = box(width, 1.0, 0.7, "#f4f3ef", { roughness: 0.45 });
    body.position.set(0, 0.5, 0);
    const top = box(width + 0.1, 0.05, 0.8, "#3a3a3d", { roughness: 0.3 });
    top.position.set(0, 1.02, 0);
    const wood = box(width, 0.25, 0.02, "#9a6740");
    wood.position.set(0, 0.3, 0.36);
    group.add(body, top, wood);
  },

  coffee_machine({ THREE, group, box, face, animated }) {
    const body = box(0.6, 0.55, 0.45, "#1c1c1e", { metalness: 0.6, roughness: 0.25 });
    body.position.set(0, 1.32, 0);
    const panel = box(0.3, 0.08, 0.01, "#ff9a3c", { emissive: "#ff9a3c", emissiveIntensity: 1.2 });
    panel.position.set(0, 1.52, 0.23);
    const spout = box(0.08, 0.1, 0.06, "#c9ccd2", { metalness: 0.8 });
    spout.position.set(0, 1.12, 0.2);
    const sticker = sheet(THREE, stickerTexture(THREE, face), 0.3, 0.15);
    sticker.position.set(0, 1.36, 0.228);
    sticker.rotation.z = 0.04;
    const light = new THREE.PointLight("#ffb366", 2.5, 3, 2);
    light.position.set(0, 1.5, 0.7);
    group.add(body, panel, spout, sticker, light);
    animated.push((dt, time) => (panel.material.emissiveIntensity = 0.9 + Math.sin(time * 2) * 0.3));
    focusOn(group, [0, 1.3, 0.23], [0, 0.15, 1], 0.8, 0.7);
  },

  menu_board({ THREE, group, face }) {
    // The black menu board, in chalk: the coffees and their prices (and the Wi-Fi rule)
    const board = sheet(THREE, menuTexture(THREE, face), 1.8, 1.2, { roughness: 0.9 });
    board.position.set(0, 2.3, 0.035);
    const frame = new THREE.Mesh(new THREE.BoxGeometry(1.92, 1.32, 0.04), new THREE.MeshStandardMaterial({ color: "#8a5a33" }));
    frame.position.set(0, 2.3, 0.01);
    const lamp = new THREE.PointLight("#fff1d0", 2.5, 3.5, 2);
    lamp.position.set(0, 3.2, 0.8);
    group.add(frame, board, lamp);
    focusOn(group, [0, 2.3, 0.04], [0, -0.1, 1], 2.0, 1.32);
  },

  rita_card({ THREE, group, box, animated }) {
    // Rita's card on the table, next to an empty cup, glinting
    const card = box(0.09, 0.004, 0.055, "#ffffff", { emissive: "#7fd0ff", emissiveIntensity: 0.4 });
    card.position.set(0.15, 0.78, 0.1);
    card.rotation.y = 0.4;
    const stripe = box(0.09, 0.005, 0.015, "#2c6db0");
    stripe.position.set(0.15, 0.781, 0.09);
    stripe.rotation.y = 0.4;
    const cup = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.035, 0.1, 16, 1, true), new THREE.MeshStandardMaterial({ color: "#f4f1e6", side: THREE.DoubleSide }));
    cup.position.set(-0.15, 0.825, 0);
    const glow = new THREE.PointLight("#bfe4ff", 1, 1.5, 2);
    glow.position.set(0.15, 1.0, 0.1);
    group.add(card, stripe, cup, glow);
    animated.push((dt, time) => (glow.intensity = 0.6 + Math.max(0, Math.sin(time * 3)) * 1.2));
  },

  // --- The terrace, outside the library (photo 3) ---
  facade({ THREE, group, box, thing }) {
    // The white library: a long volume with two floors of glass on the left, a taller white cube
    // with one big window on the right, lit from inside at night
    const white = "#eeede8";
    // The inside, seen through the glass: lit shelves, lamps, and posters on the ground floor
    const inside = (metres, posters) =>
      canvasTexture(THREE, 2048, 512, (g, w, h) => {
        const perMetre = w / metres;
        g.fillStyle = "#f2d6a0";
        g.fillRect(0, 0, w, h);
        g.fillStyle = "rgba(255,250,235,0.9)";
        g.fillRect(0, 0, w, 26);
        g.fillStyle = "rgba(110,80,45,0.35)";
        g.fillRect(0, h * 0.8, w, h * 0.2);
        for (let x = perMetre * 0.4; x < w; x += perMetre * 2.6) {
          g.fillStyle = "rgba(245,245,240,0.95)";
          g.fillRect(x, h * 0.36, perMetre * 1.6, h * 0.44);
          const colours = ["#3a4a6a", "#7a3a3a", "#c9b58a", "#3a5a48"];
          for (let row = 0; row < 3; row++) {
            for (let k = 0; k < 14; k++) {
              g.fillStyle = colours[(k + row) % 4];
              g.fillRect(x + 8 + k * (perMetre * 1.6 - 16) / 14, h * 0.4 + row * h * 0.13, (perMetre * 1.6 - 16) / 16, h * 0.1);
            }
          }
        }
        if (posters) {
          for (let x = perMetre * 1.9; x < w; x += perMetre * 2.6) {
            g.fillStyle = "#2a2a2a";
            g.fillRect(x, h * 0.18, perMetre * 0.45, h * 0.5);
            g.fillStyle = "#f2f0ea";
            g.fillRect(x + 6, h * 0.18 + 6, perMetre * 0.45 - 12, h * 0.14);
          }
        }
      });
    const lit = (texture) => new THREE.MeshStandardMaterial({ map: texture, emissive: "#ffffff", emissiveMap: texture, emissiveIntensity: 0.7, roughness: 0.15 });
    // Left volume: x from -10 to 2, two floors of glass with thin mullions every 1.2 m
    const left = box(12, 8.4, 6, white, { roughness: 0.85 });
    left.position.set(-4, 4.2, -3);
    group.add(left);
    for (const [y, h, posters] of [[2.05, 3.5, true], [6.05, 3.3, false]]) {
      const pane = new THREE.Mesh(new THREE.PlaneGeometry(11.6, h), lit(inside(11.6, posters)));
      pane.position.set(-4, y, 0.02);
      group.add(pane);
    }
    for (let i = 0; i <= 10; i++) {
      const mullion = box(0.06, 7.6, 0.08, "#d9dadc", { metalness: 0.4 });
      mullion.position.set(-9.8 + i * 1.16, 4.0, 0.06);
      group.add(mullion);
    }
    const slab = box(12, 0.5, 0.15, white);
    slab.position.set(-4, 4.05, 0.08);
    group.add(slab);
    // Right volume: x from 2 to 10, taller, with its big window upstairs and a covered ground floor
    const right = box(8, 6.6, 9, white, { roughness: 0.85 });
    right.position.set(6, 7.9, -1.5);
    const behind = box(8, 4.6, 5, shade(white, -0.05), { roughness: 0.9 });
    behind.position.set(6, 2.3, -3.5);
    group.add(right, behind);
    const big = new THREE.Mesh(new THREE.PlaneGeometry(5.6, 3.4), lit(inside(5.6, false)));
    big.position.set(5.6, 8.0, 3.01);
    group.add(big);
    for (let x = 2.8; x <= 8.4; x += 1.4) {
      const mullion = box(0.06, 3.4, 0.08, "#d9dadc");
      mullion.position.set(x, 8.0, 3.05);
      group.add(mullion);
    }
    const lowGlass = new THREE.Mesh(new THREE.PlaneGeometry(7.6, 3.6), lit(inside(7.6, true)));
    lowGlass.position.set(6, 2.0, -0.99);
    group.add(lowGlass);
    // Warm light spilling out onto the terrace
    for (const x of [-7, -2, 5]) {
      const light = new THREE.PointLight("#ffd9a0", 5, 9, 1.6);
      light.position.set(x, 2.6, 1.6);
      group.add(light);
    }
  },

  walkway({ THREE, group, box, thing }) {
    // The walkway: a white bridge over the terrace, with a railing of thin metal bars
    const { width, length } = thing;
    const deck = box(width, 0.5, length, "#f4f3ef", { roughness: 0.6 });
    deck.position.set(0, 4.45, 0);
    group.add(deck);
    const steel = new THREE.MeshStandardMaterial({ color: "#c9ccd2", metalness: 0.7, roughness: 0.35 });
    const bars = [];
    for (const x of [-width / 2 + 0.05, width / 2 - 0.05]) {
      for (let z = -length / 2; z <= length / 2; z += 0.13) bars.push([x, 5.2, z]);
      const rail = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.05, length), steel);
      rail.position.set(x, 5.72, 0);
      group.add(rail);
    }
    for (let x = -width / 2; x <= width / 2; x += 0.13) bars.push([x, 5.2, length / 2 - 0.05]);
    group.add(copies(THREE, new THREE.BoxGeometry(0.018, 1.0, 0.018), steel, bars));
  },

  sign_post({ THREE, group, box, face }) {
    // A metal sign on a pole, by the door: the sprinklers' time
    const pole = box(0.06, 1.4, 0.06, "#8d949c", { metalness: 0.6 });
    pole.position.y = 0.7;
    const sign = sheet(THREE, signTexture(THREE, face), 0.56, 0.42, { roughness: 0.7 });
    sign.position.set(0, 1.45, 0.04);
    const plate = box(0.58, 0.44, 0.02, "#d0d3d8", { metalness: 0.6 });
    plate.position.set(0, 1.45, 0.02);
    const lamp = new THREE.PointLight("#ffe7b8", 1.2, 2.2, 2);
    lamp.position.set(0, 2.0, 0.6);
    group.add(pole, plate, sign, lamp);
    focusOn(group, [0, 1.45, 0.05], [0, 0, 1], 0.66, 0.52);
  },

  picnic_table({ group, box }) {
    // A weathered wooden picnic table with its benches (the terrace)
    const wood = "#857463";
    for (const dz of [-0.25, 0, 0.25]) {
      const plank = box(1.9, 0.05, 0.23, shade(wood, dz * 0.3), { roughness: 0.9 });
      plank.position.set(0, 0.76, dz);
      group.add(plank);
    }
    for (const z of [-0.62, 0.62]) {
      const bench = box(1.9, 0.05, 0.26, wood, { roughness: 0.9 });
      bench.position.set(0, 0.45, z);
      group.add(bench);
    }
    for (const x of [-0.75, 0.75]) {
      for (const side of [-1, 1]) {
        const leg = box(0.07, 0.95, 0.07, shade(wood, -0.2));
        leg.position.set(x, 0.42, side * 0.35);
        leg.rotation.x = side * 0.5;
        group.add(leg);
      }
    }
  },

  socket_post({ THREE, group, box, animated }) {
    // The only socket that works: a little post by the tables, its light blinking
    const post = box(0.16, 0.9, 0.16, "#8d949c", { metalness: 0.5 });
    post.position.y = 0.45;
    const socket = box(0.12, 0.12, 0.02, "#f4f3ef");
    socket.position.set(0, 0.75, 0.09);
    const led = new THREE.Mesh(new THREE.SphereGeometry(0.02, 8, 6), new THREE.MeshBasicMaterial({ color: "#3bff6a" }));
    led.position.set(0, 0.86, 0.09);
    const glow = new THREE.PointLight("#3bff6a", 1, 1.6, 2);
    glow.position.set(0, 0.9, 0.3);
    group.add(post, socket, led, glow);
    animated.push((dt, time) => (glow.intensity = Math.sin(time * 4) > 0 ? 1.2 : 0.2));
  },

  sprinkler({ group, cylinder }) {
    const head = cylinder(0.05, 0.07, 0.08, "#2b2b2b", { metalness: 0.5 }, 10);
    head.position.y = 0.04;
    group.add(head);
  },

  bistro_set({ THREE, group, cylinder, box }) {
    // A small aluminium table with two aluminium chairs, like the ones under the walkway
    const alu = { metalness: 0.85, roughness: 0.3 };
    const top = box(0.62, 0.03, 0.62, "#c9ccd2", alu);
    top.position.y = 0.72;
    const leg = cylinder(0.03, 0.03, 0.7, "#c9ccd2", alu, 8);
    leg.position.y = 0.36;
    const foot = box(0.5, 0.02, 0.06, "#c9ccd2", alu);
    foot.position.y = 0.01;
    const foot2 = foot.clone();
    foot2.rotation.y = Math.PI / 2;
    group.add(top, leg, foot, foot2);
    for (const side of [-1, 1]) {
      const c = new THREE.Group();
      const seat = box(0.42, 0.03, 0.42, "#cfd2d7", alu);
      seat.position.y = 0.46;
      c.add(seat);
      for (let k = -2; k <= 2; k++) {
        const slat = box(0.04, 0.36, 0.02, "#cfd2d7", alu);
        slat.position.set(k * 0.09, 0.68, -0.2);
        c.add(slat);
      }
      const rail = box(0.44, 0.03, 0.03, "#cfd2d7", alu);
      rail.position.set(0, 0.87, -0.2);
      c.add(rail);
      for (const [x, z] of [[-0.18, -0.18], [0.18, -0.18], [-0.18, 0.18], [0.18, 0.18]]) {
        const l = cylinder(0.012, 0.012, 0.46, "#cfd2d7", alu, 6);
        l.position.set(x, 0.23, z);
        c.add(l);
      }
      c.position.set(side * 0.6, 0, side * 0.15);
      c.rotation.y = side > 0 ? -Math.PI / 2 : Math.PI / 2;
      group.add(c);
    }
  },

  olive_tree({ THREE, group, cylinder }) {
    // An olive tree in a big black pot
    const pot = cylinder(0.55, 0.45, 0.9, "#1c1c1f", { roughness: 0.5 }, 24);
    pot.position.y = 0.45;
    const earth = cylinder(0.5, 0.5, 0.02, "#3a2a1c", {}, 20);
    earth.position.y = 0.88;
    group.add(pot, earth);
    const bark = new THREE.MeshStandardMaterial({ color: "#5d5246", roughness: 0.9 });
    for (const [lean, turn, length] of [[0.25, 0, 1.6], [0.45, 2.2, 1.4], [0.35, 4.1, 1.5]]) {
      const branch = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.07, length, 8), bark);
      branch.position.set(Math.sin(turn) * Math.sin(lean) * length * 0.5, 0.9 + Math.cos(lean) * length * 0.5, Math.cos(turn) * Math.sin(lean) * length * 0.5);
      branch.rotation.set(Math.cos(turn) * lean, 0, -Math.sin(turn) * lean);
      group.add(branch);
    }
    const leaves = new THREE.MeshStandardMaterial({ color: "#6b7a5a", roughness: 0.95 });
    for (let i = 0; i < 9; i++) {
      const a = i * 2.4;
      const ball = new THREE.Mesh(new THREE.IcosahedronGeometry(0.32 + (i % 3) * 0.08, 0), leaves);
      ball.position.set(Math.sin(a) * (0.4 + (i % 2) * 0.3), 2.3 + (i % 4) * 0.22, Math.cos(a) * (0.4 + (i % 2) * 0.3));
      group.add(ball);
    }
  },

  bin({ group, cylinder }) {
    const can = cylinder(0.2, 0.2, 0.85, "#b7bbc1", { metalness: 0.8, roughness: 0.3 }, 18);
    can.position.y = 0.425;
    const lid = cylinder(0.21, 0.21, 0.04, "#8d939a", { metalness: 0.8 }, 18);
    lid.position.y = 0.87;
    group.add(can, lid);
  },

  street_lamp({ THREE, group, box }) {
    const pole = box(0.08, 3.4, 0.08, "#3b3d42", { metalness: 0.6 });
    pole.position.y = 1.7;
    const head = box(0.5, 0.08, 0.2, "#3b3d42", { metalness: 0.6 });
    head.position.set(0.2, 3.42, 0);
    const lamp = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.02, 0.14), new THREE.MeshBasicMaterial({ color: "#ffe2a8" }));
    lamp.position.set(0.22, 3.37, 0);
    const light = new THREE.PointLight("#ffc87a", 9, 11, 1.5);
    light.position.set(0.22, 3.2, 0);
    group.add(pole, head, lamp, light);
  },

  laptop_open({ THREE, group, box, thing }) {
    // Your laptop open on the picnic table, plugged in, Rita's post-it by the keyboard
    const lines = thing.done ? ["✅ git push", "100%"] : thing.screen ? ["", ""] : ["3%"];
    const texture = textTexture(THREE, lines, { width: 384, height: 256, background: thing.done ? "#0f3d22" : "#0f2a5c", color: thing.done ? "#7dff9e" : "#ff6b6b", font: "bold 38px 'Courier New', monospace" });
    const base = box(0.38, 0.02, 0.27, "#9aa0a8", { metalness: 0.6, roughness: 0.3 });
    base.position.set(0, 0.8, 0.05);
    const lid = new THREE.Mesh(new THREE.BoxGeometry(0.38, 0.26, 0.015), [
      ...Array(4).fill(new THREE.MeshStandardMaterial({ color: "#9aa0a8" })),
      new THREE.MeshStandardMaterial({ map: texture, emissive: "#ffffff", emissiveMap: texture, emissiveIntensity: 0.9 }),
      new THREE.MeshStandardMaterial({ color: "#9aa0a8" }),
    ]);
    lid.position.set(0, 0.93, -0.08);
    lid.rotation.x = -0.25;
    const postIt = box(0.08, 0.002, 0.08, "#ffe14d");
    postIt.position.set(-0.3, 0.8, 0.1);
    postIt.rotation.y = 0.3;
    const cable = box(0.6, 0.01, 0.01, "#1a1a1a");
    cable.position.set(0.45, 0.79, -0.05);
    const glow = new THREE.PointLight("#7fd0ff", 1.5, 2, 2);
    glow.position.set(0, 1.1, 0.3);
    group.add(base, lid, postIt, cable, glow);
  },
};

// --- The main menu's background: a 3D room behind the menu (the 2D picture stays if 3D fails) ---

function menuRoom3D(backdrop, world) {
  if (!world || !loadSettings().view3d || !canDraw3D()) return;
  const stage = el("div", "stage three menu menu-3d");
  backdrop.append(stage);
  const data = { world, spots: [], looks: [], ui: {}, place: "menu", timer: { run: "menu" }, voice_lang: "en-GB" };
  loadThree()
    .then((THREE) => {
      if (!stage.isConnected) return;
      drawRoom(THREE, stage, data, () => {});
      backdrop.classList.add("has-3d");
    })
    .catch(() => stage.remove());
}
