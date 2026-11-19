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

// Floors: dark oak planks (Nova SBE), a grey carpet (the classrooms), sandy concrete (the terrace)
function floorTexture(THREE, kind, colour) {
  return canvasTexture(THREE, 512, 512, (g, w, h) => {
    g.fillStyle = colour;
    g.fillRect(0, 0, w, h);
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
const SOLID = new Set([
  "desk_row", "tiago_sleeping", "chair_coat", "lockers", "snack_machine", "staircase", "bookshelf", "beanbag",
  "round_table", "counter", "cafe_table", "picnic_table", "bistro_table", "street_lamp", "socket_post",
  "sign_post", "guard",
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
    // The ceiling, white, with its lights
    const ceiling = new THREE.Mesh(new THREE.PlaneGeometry(W, D + 8), material("#f2f1ee", { roughness: 1 }));
    ceiling.rotation.x = Math.PI / 2;
    ceiling.position.set(0, H, 4);
    scene.add(ceiling);
    if (style.ceiling === "spots") {
      // Rows of round spotlights, like the classrooms
      for (let x = -W / 2 + 1.2; x < W / 2; x += 1.6) {
        for (let z = -D / 2 + 1; z < D / 2; z += 1.8) {
          const spot = new THREE.Mesh(new THREE.CircleGeometry(0.09, 16), new THREE.MeshBasicMaterial({ color: "#fffbe8" }));
          spot.rotation.x = Math.PI / 2;
          spot.position.set(x, H - 0.01, z);
          scene.add(spot);
        }
      }
    } else {
      // Long lines of LED light, like the library
      for (let z = -D / 2 + 1.2; z < D / 2; z += 2.2) {
        const line = box(W * 0.8, 0.03, 0.06, "#ffffff", { emissive: palette.light, emissiveIntensity: 2.5 });
        line.position.set(0, H - 0.02, z);
        line.rotation.y = 0.12;
        scene.add(line);
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
    if (style.windows === "back") buildWindows(THREE, scene, W, D, H);
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
  const later = []; // things placed next to the character once it exists (the guard who caught you)

  for (const thing of world.things) {
    const group = new THREE.Group();
    const [x, z] = thing.at;
    group.position.set(x, 0, z);
    if (thing.wall === "left") group.rotation.y = Math.PI / 2;
    if (thing.wall === "right") group.rotation.y = -Math.PI / 2;
    const build = THINGS[thing.kind];
    if (build) build({ ...context, group, thing });
    // A clue the co-op agent may not read: the lights over it are out
    if (thing.dark) darken(group);
    scene.add(shadowy(group));
    if (SOLID.has(thing.kind)) {
      const outline = new THREE.Box3().setFromObject(group);
      obstacles.push([outline.min.x, outline.max.x, outline.min.z, outline.max.z]);
    }
    if (thing.facing_hero) later.push(group);
    const spot = thing.spot !== null && thing.spot !== undefined ? data.spots[thing.spot] : null;
    const look = thing.look !== null && thing.look !== undefined ? data.looks[thing.look] : null;
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
  const busy = () => !!stage.querySelector(".bubble, .dialogue, .ending, .notebook, .confirm");

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

  function useSpot(spot) {
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
    if (item.look) return ui.openBubble(item.look.text, [], data.ui.close);
    useSpot(item.spot);
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
  function heroSays(text) {
    if (!hero || !text) return;
    sayBox.textContent = text;
    sayBox.classList.add("show");
    sayUntil = performance.now() + Math.min(9000, 2500 + text.length * 60);
    speak(text, "you", data.voice_lang);
  }
  if (data.speech) setTimeout(() => heroSays(data.speech), 300);

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
  if (watching) {
    // A security camera high in the front corner, slowly panning
    camera.position.copy(cctvAt);
    look.set(-1, 0.5, -1.5);
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
    if (watching) {
      camera.position.x = cctvAt.x + Math.sin(time * 0.15) * 1.2;
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
      if (nearest && canWalk()) use(nearest);
    },
    move3d: (key) => {
      if (!MOVE_KEYS[moveKey(key)]) return false;
      if (!canWalk()) return true; // the keys do nothing here, but do not reach the 2D handler
      rememberKeys();
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

// --- Outside: the night sky, the moon and the sea over Carcavelos -------------------------------

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
  moon.position.set(30, 30, -150);
  moon.lookAt(0, 0, 0);
  scene.add(moon);
  const sea = new THREE.Mesh(
    new THREE.PlaneGeometry(400, 160),
    new THREE.MeshStandardMaterial({ color: "#0c1834", roughness: 0.25, metalness: 0.6 })
  );
  sea.rotation.x = -Math.PI / 2;
  sea.position.set(0, -4, -D / 2 - 82);
  scene.add(sea);
  const glint = new THREE.Mesh(
    new THREE.PlaneGeometry(6, 120),
    new THREE.MeshBasicMaterial({ color: "#fff2c0", transparent: true, opacity: 0.18, depthWrite: false })
  );
  glint.rotation.x = -Math.PI / 2;
  glint.position.set(14, -3.95, -D / 2 - 70);
  scene.add(glint);
  const moonlight = new THREE.DirectionalLight("#c8d4ff", 0.6);
  moonlight.position.set(30, 30, -60);
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
  railing(W, "x", 0, -D / 2);
  railing(D, "z", W / 2, 0);
  // A low wall under the railing, the edge of the terrace
  const ledge = new THREE.Mesh(new THREE.BoxGeometry(W + 0.4, 0.25, 0.3), new THREE.MeshStandardMaterial({ color: "#e9e6df" }));
  ledge.position.set(0, 0.12, -D / 2 - 0.15);
  scene.add(ledge);
}

// Big windows on the back wall, with the night outside (the lights of the coast and the sea)
function buildWindows(THREE, scene, W, D, H) {
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
  const glass = new THREE.Mesh(
    new THREE.PlaneGeometry(W * 0.5, H * 0.62),
    new THREE.MeshBasicMaterial({ map: night })
  );
  glass.position.set(-W * 0.22, H * 0.45, -D / 2 + 0.01);
  scene.add(glass);
  // Thin frames between the panes
  for (let i = 0; i <= 5; i++) {
    const frame = new THREE.Mesh(new THREE.BoxGeometry(0.05, H * 0.62, 0.05), new THREE.MeshStandardMaterial({ color: "#d8d9db" }));
    frame.position.set(-W * 0.22 - W * 0.25 + (i * W * 0.5) / 5, H * 0.45, -D / 2 + 0.03);
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

// --- The kinds of things, built from simple shapes. Each one gets an empty group placed in the
// room (turned to face the room when it hangs on a wall) and adds its shapes to it. ---------------

const WHITE = "#f4f3ef";

// A chair: a grey shell on thin legs (the library and the classrooms)
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

const THINGS = {
  // --- Study Room B ---
  wood_wall({ group, box, thing, H }) {
    // Vertical wooden slats on the back wall, like the amphitheatre
    const width = thing.width;
    for (let x = -width / 2; x < width / 2; x += 0.16) {
      const slat = box(0.12, H, 0.06, x % 0.32 < 0.16 ? "#9a6740" : "#8d5d39", { roughness: 0.55 });
      slat.position.set(x + 0.06, H / 2, 0.03);
      group.add(slat);
    }
  },

  wall_clock({ THREE, group, thing, animated }) {
    const face = new THREE.Mesh(new THREE.CircleGeometry(0.32, 32), new THREE.MeshStandardMaterial({ color: "#ffffff" }));
    face.position.set(0, 3.0, 0.08);
    const rim = new THREE.Mesh(new THREE.TorusGeometry(0.32, 0.03, 8, 32), new THREE.MeshStandardMaterial({ color: "#222222" }));
    rim.position.copy(face.position);
    const [h, m] = thing.time.split(":").map(Number);
    const hand = (length, width, angle) => {
      const pivot = new THREE.Group();
      const stick = new THREE.Mesh(new THREE.BoxGeometry(width, length, 0.01), new THREE.MeshBasicMaterial({ color: "#111111" }));
      stick.position.y = length / 2;
      pivot.add(stick);
      pivot.position.set(0, 3.0, 0.09);
      pivot.rotation.z = -angle;
      return pivot;
    };
    const hours = hand(0.17, 0.03, ((h % 12) + m / 60) * (Math.PI / 6));
    const minutes = hand(0.26, 0.02, m * (Math.PI / 30));
    const seconds = hand(0.27, 0.008, 0);
    seconds.children[0].material = new THREE.MeshBasicMaterial({ color: "#c8343a" });
    group.add(face, rim, hours, minutes, seconds);
    animated.push((dt, time) => (seconds.rotation.z = -(Math.floor(time) % 60) * (Math.PI / 30)));
  },

  desk_row({ THREE, group, box, thing }) {
    // A long white desk, gently curved, with grey chairs behind it (facing the board)
    const width = thing.width;
    const pieces = 6;
    for (let i = 0; i < pieces; i++) {
      const t = (i + 0.5) / pieces - 0.5;
      const piece = box(width / pieces + 0.02, 0.06, 0.62, WHITE, { roughness: 0.4 });
      piece.position.set(t * width, 0.76, t * t * 1.6);
      piece.rotation.y = -t * 0.5;
      const front = box(width / pieces + 0.02, 0.7, 0.04, WHITE, { roughness: 0.5 });
      front.position.set(t * width, 0.38, t * t * 1.6 - 0.3);
      front.rotation.y = -t * 0.5;
      group.add(piece, front);
      for (const offset of [-0.25, 0.25]) {
        const seat = chair(THREE, box, "#25272c");
        seat.position.set(t * width + offset * (width / pieces), 0, t * t * 1.6 + 0.62);
        seat.rotation.y = Math.PI - t * 0.5;
        group.add(seat);
      }
    }
  },

  whiteboard({ THREE, group, thing }) {
    const lines = thing.writing ? thing.writing.split("\n") : [];
    const texture = textTexture(THREE, lines.length ? lines : [""], {
      width: 768, height: 384, background: "#fbfbfb", color: "#1d3c8f", font: "bold 54px 'Courier New', monospace",
      align: "left", padding: 60,
    });
    const board = new THREE.Mesh(new THREE.BoxGeometry(2.6, 1.3, 0.04), [
      ...Array(4).fill(new THREE.MeshStandardMaterial({ color: "#c9ccd2" })),
      new THREE.MeshStandardMaterial({ map: texture, roughness: 0.2 }),
      new THREE.MeshStandardMaterial({ color: "#c9ccd2" }),
    ]);
    board.position.set(0, 1.75, 0.03);
    const tray = new THREE.Mesh(new THREE.BoxGeometry(2.6, 0.04, 0.1), new THREE.MeshStandardMaterial({ color: "#b0b4ba", metalness: 0.5 }));
    tray.position.set(0, 1.08, 0.07);
    group.add(board, tray);
  },

  tiago_sleeping({ THREE, group, box, animated }) {
    // Tiago, asleep on a Finance textbook, with "Zzz" rising
    const person = makePerson(THREE, { hoodie: "#7a2f3a", hair: "#5a3a1a", sleeping: true });
    person.group.position.set(0, 0, 0.55);
    person.group.rotation.y = Math.PI;
    const book = box(0.32, 0.05, 0.24, "#1f5c8a");
    book.position.set(0, 0.81, 0.05);
    group.add(person.group, book);
    const z = textTexture(THREE, ["z Z z"], { width: 256, height: 128, background: "rgba(0,0,0,0)", color: "#ffffff", font: "bold 64px sans-serif" });
    const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: z, transparent: true, depthWrite: false }));
    sprite.scale.set(0.6, 0.3, 1);
    group.add(sprite);
    animated.push((dt, time) => {
      person.animate(dt, time, false);
      const t = (time * 0.4) % 1;
      sprite.position.set(0.2 + Math.sin(time) * 0.05, 1.3 + t * 0.6, 0.3);
      sprite.material.opacity = 1 - t;
    });
  },

  laptop({ THREE, group, box }) {
    // Your laptop on the desk, at 3%, with Tiago's post-it on the screen
    const base = box(0.36, 0.02, 0.25, "#9aa0a8", { metalness: 0.6, roughness: 0.3 });
    base.position.set(0, 0.8, 0.0);
    const screenTexture = textTexture(THREE, ["🔒  ••••", "3%"], { width: 256, height: 160, background: "#1b2b4d", color: "#ffffff", font: "bold 30px sans-serif" });
    const lid = new THREE.Mesh(new THREE.BoxGeometry(0.36, 0.24, 0.015), [
      ...Array(4).fill(new THREE.MeshStandardMaterial({ color: "#9aa0a8" })),
      new THREE.MeshStandardMaterial({ map: screenTexture, emissive: "#ffffff", emissiveMap: screenTexture, emissiveIntensity: 0.6 }),
      new THREE.MeshStandardMaterial({ color: "#9aa0a8" }),
    ]);
    lid.position.set(0, 0.92, -0.12);
    lid.rotation.x = -0.25;
    const postIt = box(0.07, 0.07, 0.004, "#ffe14d");
    postIt.position.set(0.11, 0.97, -0.1);
    postIt.rotation.x = -0.25;
    group.add(base, lid, postIt);
  },

  phone({ THREE, group, box, animated }) {
    // Your phone, lighting up with Rita's message
    const phone = box(0.08, 0.012, 0.16, "#111111", { roughness: 0.3 });
    phone.position.set(0, 0.8, 0.05);
    const glow = box(0.07, 0.002, 0.14, "#7fd0ff", { emissive: "#7fd0ff", emissiveIntensity: 1.2 });
    glow.position.set(0, 0.807, 0.05);
    group.add(phone, glow);
    animated.push((dt, time) => (glow.material.emissiveIntensity = 0.6 + Math.max(0, Math.sin(time * 3)) * 1.2));
  },

  chair_coat({ THREE, group, box }) {
    // A chair with your yellow raincoat over its back
    const seat = chair(THREE, box, "#25272c");
    seat.rotation.y = Math.PI;
    group.add(seat);
    const coat = box(0.5, 0.75, 0.1, "#f2c230", { roughness: 0.35 });
    coat.position.set(0, 0.62, 0.24);
    coat.rotation.x = 0.1;
    const sleeve = box(0.12, 0.5, 0.1, "#e0b021", { roughness: 0.35 });
    sleeve.position.set(0.3, 0.48, 0.2);
    group.add(coat, sleeve);
  },

  notice({ THREE, group }) {
    const texture = textTexture(THREE, ["⚡ 23:30", "OFF"], { width: 256, height: 256, background: "#fff7d6", color: "#a31d24", font: "bold 56px sans-serif" });
    const paper = new THREE.Mesh(new THREE.PlaneGeometry(0.5, 0.5), new THREE.MeshStandardMaterial({ map: texture }));
    paper.position.set(0, 1.6, 0.02);
    group.add(paper);
  },

  door({ THREE, group, box, thing }) {
    // A door in a wall: dark grey, with a card reader that lights up
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

  // --- The locker corridor ---
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

  floor_note({ THREE, group, thing }) {
    const texture = textTexture(THREE, thing.dark ? [""] : ["Rita, o PIN…", "— Mãe"], { width: 256, height: 192, background: "#f6f1e3", color: "#3a3a8a", font: "italic 34px Georgia, serif" });
    const note = new THREE.Mesh(new THREE.PlaneGeometry(0.3, 0.22), new THREE.MeshStandardMaterial({ map: texture, side: THREE.DoubleSide }));
    note.rotation.x = -Math.PI / 2;
    note.rotation.z = 0.5;
    note.position.y = 0.02;
    group.add(note);
  },

  emergency_plan({ THREE, group, thing }) {
    // The emergency plan, green and white, with the terrace exit marked "3.14"
    const texture = canvasTexture(THREE, 384, 384, (g, w, h) => {
      g.fillStyle = "#ffffff";
      g.fillRect(0, 0, w, h);
      g.fillStyle = "#0f8a4a";
      g.fillRect(0, 0, w, 56);
      g.fillStyle = "#ffffff";
      g.font = "bold 30px sans-serif";
      g.textAlign = "center";
      g.fillText("PLANTA DE EMERGÊNCIA", w / 2, 38);
      g.strokeStyle = "#555555";
      g.lineWidth = 4;
      g.strokeRect(40, 90, 300, 230);
      g.strokeRect(40, 90, 150, 110);
      g.strokeRect(190, 200, 150, 120);
      if (thing.writing) {
        g.fillStyle = "#c8343a";
        g.beginPath();
        g.arc(110, 260, 12, 0, Math.PI * 2);
        g.fill();
        g.fillStyle = "#0f8a4a";
        g.font = "bold 40px sans-serif";
        g.fillText(`→ ${thing.writing}`, 290, 160);
      }
    });
    const plan = new THREE.Mesh(new THREE.PlaneGeometry(0.6, 0.6), new THREE.MeshStandardMaterial({ map: texture }));
    plan.position.set(0, 1.65, 0.02);
    const frame = new THREE.Mesh(new THREE.BoxGeometry(0.66, 0.66, 0.02), new THREE.MeshStandardMaterial({ color: "#2b2b2b" }));
    frame.position.set(0, 1.65, 0.005);
    group.add(frame, plan);
  },

  snack_machine({ THREE, group, box }) {
    const body = box(0.95, 1.9, 0.8, "#c8343a", { roughness: 0.4 });
    body.position.set(0, 0.95, 0.4);
    const glass = box(0.6, 1.2, 0.02, "#a8d8ff", { emissive: "#6fb9ff", emissiveIntensity: 0.5, transparent: true, opacity: 0.6 });
    glass.position.set(-0.1, 1.15, 0.81);
    const bag = box(0.12, 0.16, 0.05, "#ffd23f");
    bag.position.set(-0.2, 0.75, 0.76);
    const slot = box(0.18, 0.5, 0.02, "#222222");
    slot.position.set(0.32, 1.2, 0.81);
    const light = new THREE.PointLight("#8fd0ff", 2, 2.5, 2);
    light.position.set(0, 1.2, 1.3);
    group.add(body, glass, bag, slot, light);
  },

  staircase({ THREE, group, thing, box }) {
    // The big staircase of the library, with "STATE YOUR MIND AND MIND YOUR STEP" on the steps,
    // going up towards the back, between glass balustrades
    const steps = 12;
    const words = thing.words || [];
    for (let i = 0; i < steps; i++) {
      const y = 0.17 + i * 0.3;
      const z = -i * 0.32;
      const tread = box(2.2, 0.05, 0.34, "#d8c09a", { roughness: 0.6 });
      tread.position.set(0, y + 0.15, z);
      const riserTexture = textTexture(THREE, [words[steps - 1 - i] || ""], { width: 512, height: 72, background: "#f6f6f4", color: "#111111", font: "900 56px Arial Black, sans-serif" });
      const riser = new THREE.Mesh(new THREE.BoxGeometry(2.2, 0.3, 0.04), [
        ...Array(4).fill(new THREE.MeshStandardMaterial({ color: "#f6f6f4" })),
        new THREE.MeshStandardMaterial({ map: riserTexture }),
        new THREE.MeshStandardMaterial({ color: "#f6f6f4" }),
      ]);
      riser.position.set(0, y, z + 0.17);
      group.add(tread, riser);
    }
    // Glass balustrades and the white side walls
    for (const side of [-1, 1]) {
      const wall = box(0.12, 3.8, 3.9, "#f4f3ef");
      wall.position.set(side * 1.16, 1.0, -1.75);
      wall.rotation.x = -0.75;
      wall.scale.y = 0.3;
      const glass = box(0.03, 1.0, 3.9, "#bcd6e6", { transparent: true, opacity: 0.25, metalness: 0.3, roughness: 0.05 });
      glass.position.set(side * 1.12, 2.4, -1.75);
      glass.rotation.x = -0.75;
      group.add(wall, glass);
    }
  },

  glass_door({ THREE, group, box }) {
    // The glass door to the terrace, the night behind it, and its keypad
    const frame = box(1.5, 2.6, 0.1, "#c9ccd2", { metalness: 0.6, roughness: 0.3 });
    frame.position.set(0, 1.3, 0.03);
    const night = canvasTexture(THREE, 128, 256, (g, w, h) => {
      const gradient = g.createLinearGradient(0, 0, 0, h);
      gradient.addColorStop(0, "#08102a");
      gradient.addColorStop(1, "#1d2f5c");
      g.fillStyle = gradient;
      g.fillRect(0, 0, w, h);
    });
    const glass = new THREE.Mesh(new THREE.PlaneGeometry(1.32, 2.42), new THREE.MeshBasicMaterial({ map: night }));
    glass.position.set(0, 1.25, 0.09);
    const bar = box(1.2, 0.05, 0.06, "#d6d9de", { metalness: 0.8 });
    bar.position.set(0, 1.05, 0.12);
    const keypadTexture = canvasTexture(THREE, 96, 160, (g, w, h) => {
      g.fillStyle = "#14163a";
      g.fillRect(0, 0, w, h);
      g.fillStyle = "#7fd0ff";
      for (let r = 0; r < 4; r++) for (let c = 0; c < 3; c++) g.fillRect(12 + c * 26, 20 + r * 34, 18, 22);
    });
    const keypad = new THREE.Mesh(
      new THREE.BoxGeometry(0.2, 0.32, 0.05),
      new THREE.MeshStandardMaterial({ map: keypadTexture, emissive: "#ffffff", emissiveMap: keypadTexture, emissiveIntensity: 0.7 })
    );
    keypad.position.set(0.98, 1.3, 0.06);
    const sign = textTexture(THREE, ["3.14 ⟶ TERRAÇO"], { width: 512, height: 96, background: "#0f8a4a", color: "#ffffff", font: "bold 40px sans-serif" });
    const plate = new THREE.Mesh(new THREE.PlaneGeometry(0.9, 0.17), new THREE.MeshStandardMaterial({ map: sign, emissive: "#ffffff", emissiveMap: sign, emissiveIntensity: 0.5 }));
    plate.position.set(0, 2.78, 0.06);
    group.add(frame, glass, bar, keypad, plate);
  },

  bookshelf({ group, box }) {
    // A white bookshelf full of coloured books, like the library's first floor
    const shelf = box(2.4, 1.8, 0.45, "#f7f7f5", { roughness: 0.5 });
    shelf.position.set(0, 0.9, 0.23);
    group.add(shelf);
    const colours = ["#2c3e66", "#7a2f3a", "#d8c49a", "#3a6b4f", "#1d1d1d", "#b8562e", "#5b6f99", "#e3d9c0"];
    for (let row = 0; row < 4; row++) {
      let x = -1.1;
      let i = row * 3;
      while (x < 1.05) {
        const w = 0.04 + ((i * 7) % 5) * 0.012;
        const h = 0.26 + ((i * 3) % 4) * 0.025;
        const book = box(w, h, 0.3, colours[i % colours.length]);
        book.position.set(x + w / 2, 0.12 + row * 0.43 + h / 2, 0.3);
        group.add(book);
        x += w + 0.005;
        i += 1;
      }
    }
  },

  beanbag({ THREE, group }) {
    // A black leather beanbag (floor 0 of the library)
    const bag = new THREE.Mesh(new THREE.SphereGeometry(0.5, 20, 14), new THREE.MeshStandardMaterial({ color: "#151517", roughness: 0.35, metalness: 0.1 }));
    bag.scale.set(1, 0.65, 1);
    bag.position.y = 0.32;
    group.add(bag);
  },

  round_table({ group, cylinder }) {
    const top = cylinder(0.45, 0.45, 0.04, "#f7f7f5", { roughness: 0.4 }, 28);
    top.position.y = 0.72;
    const leg = cylinder(0.04, 0.04, 0.7, "#c9ccd2", { metalness: 0.6 }, 10);
    leg.position.y = 0.36;
    const foot = cylinder(0.25, 0.25, 0.03, "#c9ccd2", { metalness: 0.6 }, 20);
    foot.position.y = 0.015;
    group.add(top, leg, foot);
  },

  poster({ THREE, group }) {
    // A poster from the "Dividends and Dreams" exhibition (black and white portraits)
    const texture = canvasTexture(THREE, 256, 360, (g, w, h) => {
      g.fillStyle = "#e8e6e1";
      g.fillRect(0, 0, w, h);
      g.fillStyle = "#3a3a3a";
      g.fillRect(16, 60, w - 32, h - 120);
      g.fillStyle = "#7d7d7d";
      g.beginPath();
      g.arc(w / 2, h / 2 - 10, 50, 0, Math.PI * 2);
      g.fill();
      g.fillStyle = "#111111";
      g.font = "bold 26px Georgia, serif";
      g.textAlign = "center";
      g.fillText("NOVA SBE", w / 2, 40);
    });
    const poster = new THREE.Mesh(new THREE.PlaneGeometry(0.9, 1.26), new THREE.MeshStandardMaterial({ map: texture }));
    poster.position.set(0, 1.9, 0.02);
    group.add(poster);
  },

  guard({ THREE, group, thing, animated }) {
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
        group.position.y = Math.max(0, (1 - t * 2.2)) * 1.6; // still on the stairs at first
        if (heroAt) group.rotation.y = Math.atan2(heroAt.x - group.position.x, heroAt.z - group.position.z) + Math.sin(time * 1.5) * 0.4;
      }
      person.animate(dt, time, thing.walking && t < 1);
    });
  },

  // --- The cafeteria ---
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

  coffee_machine({ THREE, group, box, animated }) {
    const body = box(0.6, 0.55, 0.45, "#1c1c1e", { metalness: 0.6, roughness: 0.25 });
    body.position.set(0, 1.32, 0);
    const panel = box(0.3, 0.12, 0.01, "#ff9a3c", { emissive: "#ff9a3c", emissiveIntensity: 1.2 });
    panel.position.set(0, 1.45, 0.23);
    const spout = box(0.08, 0.1, 0.06, "#c9ccd2", { metalness: 0.8 });
    spout.position.set(0, 1.12, 0.2);
    const light = new THREE.PointLight("#ffb366", 2.5, 3, 2);
    light.position.set(0, 1.5, 0.7);
    group.add(body, panel, spout, light);
    animated.push((dt, time) => (panel.material.emissiveIntensity = 0.9 + Math.sin(time * 2) * 0.3));
  },

  menu_board({ THREE, group, thing }) {
    // A black menu board: the coffees and their prices (and the Wi-Fi rule underneath)
    const lines = thing.writing ? [...thing.writing.split(" · "), "Wi-Fi: + € (sem vírgula)"] : ["", "", ""];
    const texture = textTexture(THREE, ["MENU", ...lines], { width: 640, height: 400, background: "#1b1d1c", color: "#f4f1e6", font: "bold 40px 'Courier New', monospace" });
    const board = new THREE.Mesh(new THREE.PlaneGeometry(1.8, 1.12), new THREE.MeshStandardMaterial({ map: texture }));
    board.position.set(0, 2.35, 0.03);
    const frame = new THREE.Mesh(new THREE.BoxGeometry(1.9, 1.22, 0.03), new THREE.MeshStandardMaterial({ color: "#9a6740" }));
    frame.position.set(0, 2.35, 0.01);
    group.add(frame, board);
  },

  cafe_table({ THREE, group, box, cylinder, thing }) {
    // A round white table; the chairs upside down on top (or still on the floor around it)
    const top = cylinder(0.55, 0.55, 0.04, "#f7f7f5", { roughness: 0.4 }, 28);
    top.position.y = 0.74;
    const leg = cylinder(0.05, 0.05, 0.72, "#c9ccd2", { metalness: 0.6 }, 10);
    leg.position.y = 0.37;
    const foot = cylinder(0.3, 0.3, 0.03, "#c9ccd2", { metalness: 0.6 }, 20);
    foot.position.y = 0.015;
    group.add(top, leg, foot);
    for (const [x, z, angle] of [[-0.25, 0, 0.3], [0.25, 0, -0.3]]) {
      const c = chair(THREE, box);
      if (thing.chairs_down) {
        c.position.set(x * 3, 0, 0.75);
        c.rotation.y = Math.PI + angle;
      } else {
        c.rotation.x = Math.PI;
        c.rotation.y = angle;
        c.position.set(x, 1.68, z);
      }
      group.add(c);
    }
  },

  rita_card({ THREE, group, box, animated }) {
    // Rita's card on the table, next to an empty cup, glinting
    const card = box(0.09, 0.004, 0.055, "#ffffff", { emissive: "#7fd0ff", emissiveIntensity: 0.4 });
    card.position.set(0.15, 0.765, 0.1);
    card.rotation.y = 0.4;
    const stripe = box(0.09, 0.005, 0.015, "#2c6db0");
    stripe.position.set(0.15, 0.766, 0.09);
    stripe.rotation.y = 0.4;
    const cup = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.035, 0.1, 16, 1, true), new THREE.MeshStandardMaterial({ color: "#f4f1e6", side: THREE.DoubleSide }));
    cup.position.set(-0.15, 0.81, 0);
    const glow = new THREE.PointLight("#bfe4ff", 1, 1.5, 2);
    glow.position.set(0.15, 1.0, 0.1);
    group.add(card, stripe, cup, glow);
    animated.push((dt, time) => (glow.intensity = 0.6 + Math.max(0, Math.sin(time * 3)) * 1.2));
  },

  // --- The terrace ---
  facade({ THREE, group, D, H }) {
    // The white library building, its tall windows lit from inside
    const wall = new THREE.Mesh(new THREE.BoxGeometry(D + 2, H * 2.2, 0.4), new THREE.MeshStandardMaterial({ color: "#eceae4", roughness: 0.85 }));
    wall.position.set(0, H * 1.1, -0.2);
    group.add(wall);
    const lit = new THREE.MeshStandardMaterial({ color: "#ffe6b0", emissive: "#ffdc9a", emissiveIntensity: 0.9 });
    const dark = new THREE.MeshStandardMaterial({ color: "#1b2236", roughness: 0.1, metalness: 0.5 });
    for (let i = 0; i < 9; i++) {
      for (const floor of [0, 1]) {
        if (floor === 0 && Math.abs(-D / 2 + 0.9 + i * 1.3 - 2.4) < 1.2) continue; // the door
        const pane = new THREE.Mesh(new THREE.PlaneGeometry(1.1, H * 0.9), (i + floor) % 3 ? lit : dark);
        pane.position.set(-D / 2 + 0.9 + i * 1.3, H * 0.5 + floor * H * 1.05, 0.01);
        group.add(pane);
      }
    }
    const glow = new THREE.PointLight("#ffdc9a", 6, 8, 1.6);
    glow.position.set(0, 2.5, 2);
    group.add(glow);
  },

  walkway({ group, box, D, H }) {
    // The walkway above the terrace, on white columns, like the photo of the library
    const slab = box(5, 0.5, D + 2, "#f4f3ef");
    slab.position.set(0, H, 0);
    group.add(slab);
    for (const z of [-D / 2 + 1.5, 0, D / 2 - 1.5]) {
      const column = box(0.3, H, 0.3, "#f7f7f5");
      column.position.set(2.2, H / 2, z);
      group.add(column);
    }
  },

  sign_post({ THREE, group, box }) {
    const pole = box(0.06, 1.4, 0.06, "#8d949c", { metalness: 0.6 });
    pole.position.y = 0.7;
    const texture = textTexture(THREE, ["💦 23:55", "REGA"], { width: 256, height: 192, background: "#ffffff", color: "#1d5fa8", font: "bold 50px sans-serif" });
    const sign = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.38, 0.02), [
      ...Array(4).fill(new THREE.MeshStandardMaterial({ color: "#ffffff" })),
      new THREE.MeshStandardMaterial({ map: texture }),
      new THREE.MeshStandardMaterial({ color: "#ffffff" }),
    ]);
    sign.position.y = 1.45;
    sign.rotation.y = Math.PI / 2;
    group.add(pole, sign);
  },

  picnic_table({ group, box }) {
    // A wooden picnic table with its benches (the terrace)
    const wood = "#7a5a3a";
    const top = box(1.9, 0.06, 0.75, wood, { roughness: 0.85 });
    top.position.y = 0.76;
    group.add(top);
    for (const z of [-0.6, 0.6]) {
      const bench = box(1.9, 0.05, 0.28, wood, { roughness: 0.85 });
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

  bistro_table({ group, cylinder }) {
    // A small metal table, like the ones under the walkway
    const top = cylinder(0.32, 0.32, 0.03, "#c9ccd2", { metalness: 0.8, roughness: 0.3 }, 20);
    top.position.y = 0.72;
    const leg = cylinder(0.03, 0.03, 0.7, "#c9ccd2", { metalness: 0.8 }, 8);
    leg.position.y = 0.36;
    group.add(top, leg);
  },

  street_lamp({ THREE, group, box }) {
    const pole = box(0.08, 3.2, 0.08, "#3b3d42", { metalness: 0.6 });
    pole.position.y = 1.6;
    const lamp = new THREE.Mesh(new THREE.SphereGeometry(0.16, 16, 12), new THREE.MeshBasicMaterial({ color: "#ffd38a" }));
    lamp.position.y = 3.25;
    const light = new THREE.PointLight("#ffc87a", 9, 10, 1.5);
    light.position.y = 3.1;
    group.add(pole, lamp, light);
  },

  laptop_open({ THREE, group, box, thing }) {
    // Your laptop open on the picnic table, plugged in: a terminal, or the submission at the end
    const lines = thing.done ? ["✅ git push", "Submission received"] : thing.screen ? ["$ ssh nova-sbe", "> _"] : ["3%"];
    const texture = textTexture(THREE, lines, { width: 384, height: 256, background: thing.done ? "#0f3d22" : "#0b1020", color: thing.done ? "#7dff9e" : "#7fd0ff", font: "bold 38px 'Courier New', monospace" });
    const base = box(0.38, 0.02, 0.27, "#9aa0a8", { metalness: 0.6, roughness: 0.3 });
    base.position.set(0, 0.8, 0.05);
    const lid = new THREE.Mesh(new THREE.BoxGeometry(0.38, 0.26, 0.015), [
      ...Array(4).fill(new THREE.MeshStandardMaterial({ color: "#9aa0a8" })),
      new THREE.MeshStandardMaterial({ map: texture, emissive: "#ffffff", emissiveMap: texture, emissiveIntensity: 0.9 }),
      new THREE.MeshStandardMaterial({ color: "#9aa0a8" }),
    ]);
    lid.position.set(0, 0.93, -0.08);
    lid.rotation.x = -0.25;
    const pen = box(0.05, 0.015, 0.02, "#c8343a");
    pen.position.set(0.22, 0.81, 0.05);
    const postIt = box(0.08, 0.002, 0.08, "#ffe14d");
    postIt.position.set(-0.3, 0.8, 0.1);
    postIt.rotation.y = 0.3;
    const glow = new THREE.PointLight("#7fd0ff", 1.5, 2, 2);
    glow.position.set(0, 1.1, 0.3);
    group.add(base, lid, pen, postIt, glow);
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
