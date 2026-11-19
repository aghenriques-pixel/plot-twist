// --- 3D rooms (specs/scene-3d.md) ------------------------------------------------------------
//
// A place with a 3D room (data.world, from world3d.py) is drawn here with Three.js instead of the
// 2D picture. The character is seen from behind (third person) and walks anywhere in the room.
// Walking up to a thing and pressing E (or clicking it) uses it exactly like a 2D spot: a look
// shows its text, a talk its choices, a keypad asks for the code, and the action goes to Python.
// Python decides everything; this file only draws and moves the character.
//
// This file is added after scene_view.js in the same script (app.py), so it uses el(), Sound,
// loadSettings() and interactions() from there. Three.js is a static file (static/), loaded once.

const THREE_URL = "app/static/three.module.min.js";
const WALK_SPEED = 3.2; // metres per second
const REACH = 1.6; // how close the character must be to use a thing
const HERO_RADIUS = 0.32;

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

// A 3D room only where Python sent one, the player wants 3D and the browser can draw it.
// A danger scene (a clock and choices at once) keeps the 2D picture.
function wants3D(data) {
  return !!data.world && !data.danger && !data.ending && loadSettings().view3d && canDraw3D();
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
  stage.classList.add("three", data.world.camera === "cctv" ? "cctv" : "follow");
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
      stage.classList.remove("three", "cctv", "follow");
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
    renderer.toneMappingExposure = 1.15;
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

// --- The room ---------------------------------------------------------------------------------

function drawRoom(THREE, stage, data, setTriggerValue) {
  const world = data.world;
  const [W, D] = world.size;
  const H = world.height;
  const palette = world.palette;
  const watching = world.camera === "cctv";
  const shared = sharedRenderer(THREE);
  const { renderer } = shared;
  if (shared.active) disposeRoom(shared.active);
  shared.active = null;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color("#0c0b1f");
  scene.fog = new THREE.Fog("#0c0b1f", 14, 30);
  const camera = new THREE.PerspectiveCamera(50, 2, 0.1, 60);

  const box = (w, h, d, color, options = {}) =>
    new THREE.Mesh(
      new THREE.BoxGeometry(w, h, d),
      new THREE.MeshStandardMaterial({ color, roughness: 0.75, metalness: 0.05, ...options })
    );
  const cylinder = (rTop, rBottom, h, color, options = {}) =>
    new THREE.Mesh(
      new THREE.CylinderGeometry(rTop, rBottom, h, 20),
      new THREE.MeshStandardMaterial({ color, roughness: 0.7, ...options })
    );
  const shadowy = (object) => {
    object.traverse((child) => {
      if (child.isMesh) {
        child.castShadow = true;
        child.receiveShadow = true;
      }
    });
    return object;
  };

  // Floor: large tiles
  const floorTexture = canvasTexture(THREE, 256, 256, (g, w, h) => {
    g.fillStyle = palette.floor;
    g.fillRect(0, 0, w, h);
    g.fillStyle = shade(palette.floor, 0.06);
    g.fillRect(0, 0, w / 2, h / 2);
    g.fillRect(w / 2, h / 2, w / 2, h / 2);
    g.strokeStyle = shade(palette.floor, -0.35);
    g.lineWidth = 3;
    g.strokeRect(0, 0, w, h);
    g.beginPath();
    g.moveTo(w / 2, 0);
    g.lineTo(w / 2, h);
    g.moveTo(0, h / 2);
    g.lineTo(w, h / 2);
    g.stroke();
  });
  floorTexture.wrapS = floorTexture.wrapT = THREE.RepeatWrapping;
  floorTexture.repeat.set(W / 2.4, (D + 6) / 2.4);
  const floor = new THREE.Mesh(
    new THREE.PlaneGeometry(W, D + 6),
    new THREE.MeshStandardMaterial({ map: floorTexture, roughness: 0.55, metalness: 0.1 })
  );
  floor.rotation.x = -Math.PI / 2;
  floor.position.z = 3; // goes on past the open front, under the camera
  floor.receiveShadow = true;
  scene.add(floor);

  // Walls: back, left and right (the front is open, like a stage)
  const wallTexture = canvasTexture(THREE, 256, 256, (g, w, h) => {
    g.fillStyle = palette.wall;
    g.fillRect(0, 0, w, h);
    // Wide panels with a thin dark seam between them
    for (let x = 0; x < w; x += 128) {
      g.fillStyle = shade(palette.wall, x % 256 ? -0.03 : 0.02);
      g.fillRect(x, 0, 128, h);
      g.fillStyle = shade(palette.wall, -0.25);
      g.fillRect(x, 0, 3, h);
    }
  });
  wallTexture.wrapS = wallTexture.wrapT = THREE.RepeatWrapping;
  const wallMaterial = (repeat) => {
    const texture = wallTexture.clone();
    texture.needsUpdate = true;
    texture.repeat.set(repeat, 1);
    return new THREE.MeshStandardMaterial({ map: texture, roughness: 0.9 });
  };
  const back = new THREE.Mesh(new THREE.PlaneGeometry(W, H), wallMaterial(W / 4));
  back.position.set(0, H / 2, -D / 2);
  const left = new THREE.Mesh(new THREE.PlaneGeometry(D, H), wallMaterial(D / 4));
  left.rotation.y = Math.PI / 2;
  left.position.set(-W / 2, H / 2, 0);
  const right = left.clone();
  right.material = wallMaterial(D / 4);
  right.rotation.y = -Math.PI / 2;
  right.position.x = W / 2;
  for (const wall of [back, left, right]) {
    wall.receiveShadow = true;
    scene.add(wall);
  }
  // A low dark ceiling, so the room feels closed in
  const ceiling = new THREE.Mesh(
    new THREE.PlaneGeometry(W, D),
    new THREE.MeshStandardMaterial({ color: shade(palette.wall, -0.7), roughness: 1 })
  );
  ceiling.rotation.x = Math.PI / 2;
  ceiling.position.y = H;
  scene.add(ceiling);

  // Dark skirting board along the walls
  const skirt = box(W, 0.35, 0.08, shade(palette.wall, -0.55));
  skirt.position.set(0, 0.175, -D / 2 + 0.04);
  scene.add(skirt);
  for (const side of [-1, 1]) {
    const s = box(0.08, 0.35, D, shade(palette.wall, -0.55));
    s.position.set(side * (W / 2 - 0.04), 0.175, 0);
    scene.add(s);
  }

  // The red banner with the place's name, high on the back wall
  const bannerTexture = canvasTexture(THREE, 2048, 128, (g, w, h) => {
    const gradient = g.createLinearGradient(0, 0, w, 0);
    gradient.addColorStop(0, shade(palette.trim, -0.25));
    gradient.addColorStop(0.5, palette.trim);
    gradient.addColorStop(1, shade(palette.trim, -0.25));
    g.fillStyle = gradient;
    g.fillRect(0, 0, w, h);
    g.fillStyle = "#f4e6ec";
    g.font = "64px Georgia, serif";
    g.textAlign = "center";
    g.textBaseline = "middle";
    g.letterSpacing = "28px";
    g.fillText(data.hud.title.toUpperCase(), w / 2, h / 2 + 4);
  });
  const banner = new THREE.Mesh(
    new THREE.BoxGeometry(W, 0.85, 0.06),
    new THREE.MeshStandardMaterial({ map: bannerTexture, roughness: 0.6, emissive: "#3a0a14", emissiveIntensity: 0.6 })
  );
  banner.position.set(0, H - 0.6, -D / 2 + 0.05);
  scene.add(banner);

  // Pillars on the back wall
  for (const x of world.pillars) {
    const pillar = box(0.38, H - 1.05, 0.22, shade(palette.wall, 0.1));
    pillar.position.set(x, (H - 1.05) / 2, -D / 2 + 0.11);
    scene.add(shadowy(pillar));
  }

  // Light: a cold fill, a key light for the shadows, and the ceiling lamps
  scene.add(new THREE.HemisphereLight("#9fb0ff", "#1a1430", 1.1));
  const key = new THREE.DirectionalLight("#dfe6ff", 1.6);
  key.position.set(-4, 9, 7);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  Object.assign(key.shadow.camera, { left: -W / 2 - 1, right: W / 2 + 1, top: D, bottom: -D, near: 1, far: 30 });
  key.shadow.bias = -0.0008;
  key.shadow.normalBias = 0.02;
  scene.add(key);
  const lamps = [];
  for (const [x, z] of world.lamps) {
    const tube = box(1.5, 0.06, 0.28, "#ffffff", { emissive: palette.light, emissiveIntensity: 2.2 });
    tube.position.set(x, H - 0.05, z);
    scene.add(tube);
    const light = new THREE.PointLight(palette.light, 9, 9, 1.6);
    light.position.set(x, H - 0.4, z);
    scene.add(light);
    lamps.push({ tube, light, base: 9, flicker: Math.random() * 10 });
  }

  // --- The things in the room, from world3d.py ---
  const obstacles = []; // boxes the character walks around: [minX, maxX, minZ, maxZ]
  const usable = []; // things the character can use
  const animated = []; // little things that move every frame
  const block = (x, z, w, d) => obstacles.push([x - w / 2, x + w / 2, z - d / 2, z + d / 2]);

  for (const thing of world.things) {
    const group = new THREE.Group();
    group.position.set(thing.at[0], 0, thing.at[1]);
    if (thing.wall === "left") group.rotation.y = Math.PI / 2;
    if (thing.wall === "right") group.rotation.y = -Math.PI / 2;
    const build = THINGS[thing.kind];
    const made = build ? build({ THREE, group, thing, box, cylinder, palette, block, animated, data }) : null;
    // A clue the co-op agent may not read: the lights over it are out
    if (thing.dark) darken(group);
    scene.add(shadowy(group));
    const spot = thing.spot !== null && thing.spot !== undefined ? data.spots[thing.spot] : null;
    const look = thing.look !== null && thing.look !== undefined ? data.looks[thing.look] : null;
    if (!spot && !look) continue;
    const stand = new THREE.Vector3(...(thing.stand ? [thing.stand[0], 0, thing.stand[1]] : [thing.at[0], 0, thing.at[1] + 1.2]));
    // Where the label floats: over the thing
    const top = new THREE.Box3().setFromObject(group);
    const anchor = new THREE.Vector3((top.min.x + top.max.x) / 2, top.max.y + 0.25, (top.min.z + top.max.z) / 2);
    usable.push({ thing, group, spot, look, stand, anchor, label: (spot || look).label, made });
  }

  // Marks on the floor where a thing can be used: a soft golden ring, brighter for the nearest
  const ringGeometry = new THREE.RingGeometry(0.32, 0.42, 40);
  for (const item of usable) {
    const ring = new THREE.Mesh(
      ringGeometry,
      new THREE.MeshBasicMaterial({ color: "#f2c14e", transparent: true, opacity: 0.18, depthWrite: false })
    );
    ring.rotation.x = -Math.PI / 2;
    ring.position.set(item.stand.x, 0.012, item.stand.z);
    scene.add(ring);
    item.ring = ring;
  }

  // Dust floating in the light
  const dustCount = 260;
  const dustPositions = new Float32Array(dustCount * 3);
  for (let i = 0; i < dustCount; i++) {
    dustPositions[i * 3] = (Math.random() - 0.5) * W;
    dustPositions[i * 3 + 1] = Math.random() * H;
    dustPositions[i * 3 + 2] = (Math.random() - 0.5) * D;
  }
  const dustGeometry = new THREE.BufferGeometry();
  dustGeometry.setAttribute("position", new THREE.BufferAttribute(dustPositions, 3));
  const dust = new THREE.Points(
    dustGeometry,
    new THREE.PointsMaterial({ color: "#fff2c8", size: 0.03, transparent: true, opacity: 0.55, depthWrite: false })
  );
  scene.add(dust);

  // --- The character (none for the contacto, who watches through a camera) ---
  // Where the character stands is kept while the player stays in this room (an action redraws
  // the screen); a new arrival, a restart or a new game starts at the room's start
  const visit = `${data.place}:${data.timer.run}`;
  let here = globalThis.__forbiddenArchiveHere;
  if (!here || here.visit !== visit || globalThis.__forbiddenArchiveCameFrom !== visit) {
    here = { visit, x: world.start[0], z: world.start[1], turn: Math.PI };
    globalThis.__forbiddenArchiveHere = here;
  }
  const hero = watching ? null : makeHero(THREE);
  if (hero) {
    hero.group.position.set(here.x, 0, here.z);
    hero.group.rotation.y = here.turn;
    scene.add(shadowy(hero.group));
  }

  // Screen-space elements over the canvas: the label of the nearest thing and what the hero says
  const prompt = el("div", "prompt3d");
  const sayBox = el("div", "say3d");
  const canvas = renderer.domElement;
  stage.prepend(canvas);
  stage.append(prompt, sayBox);
  if (watching) {
    const rec = el("div", "cctv-overlay");
    rec.append(el("span", "rec", "● REC"), el("span", "cam", "CAM 03"));
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
  let target = null; // { point, then } when walking to a clicked place or thing
  let stuck = 0;
  let stepClock = 0;
  const collides = (x, z) =>
    x < -W / 2 + 0.45 || x > W / 2 - 0.45 || z < -D / 2 + 0.55 || z > D / 2 - 0.2 ||
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

  function use(item) {
    Sound.click();
    ui.closeBubble();
    if (hero) {
      // Turn to the thing
      const p = hero.group.position;
      here.turn = Math.atan2(item.group.position.x - p.x, item.group.position.z - p.z);
    }
    if (item.look) return ui.openBubble(item.look.text, [], data.ui.close);
    const spot = item.spot;
    if (spot.talk) return ui.openTalk(spot);
    if (spot.code_prompt) return ui.openKeypad(spot);
    setTriggerValue("action", { id: spot.action, x: spot.stand });
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
    let from_ = from;
    for (let k = 0; k < cells.length; k++) {
      if (k === cells.length - 1 || !clearLine(from_, cells[k + 1])) {
        path.push(cells[k]);
        from_ = cells[k];
      }
    }
    return path;
  }

  // --- Mouse: click the floor to walk there, click a thing to walk to it and use it ---
  const raycaster = new THREE.Raycaster();
  const pointer = new THREE.Vector2();
  const pick = (event) => {
    const rect = canvas.getBoundingClientRect();
    pointer.set(((event.clientX - rect.left) / rect.width) * 2 - 1, -((event.clientY - rect.top) / rect.height) * 2 + 1);
    raycaster.setFromCamera(pointer, camera);
    for (const hit of raycaster.intersectObjects(usable.map((item) => item.group), true)) {
      const item = usable.find((u) => u.group === hit.object || isInside(hit.object, u.group));
      if (item) return { item };
    }
    const floorHit = raycaster.intersectObject(floor)[0];
    return floorHit ? { point: floorHit.point } : null;
  };
  canvas.onpointermove = (event) => {
    const hit = pick(event);
    canvas.style.cursor = hit?.item && hero ? "pointer" : hero ? "crosshair" : "default";
    hovered = hit?.item || null;
  };
  canvas.onpointerleave = () => (hovered = null);
  let hovered = null;
  stage.onclick = (event) => {
    if (event.target !== canvas) return;
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
    const visible = projected.z < 1;
    element.style.left = `${((projected.x + 1) / 2) * 100}%`;
    element.style.top = `${((1 - projected.y) / 2) * 100}%`;
    element.style.visibility = visible ? "visible" : "hidden";
  }

  // --- Cameras ---
  const look = new THREE.Vector3();
  if (watching) {
    // A security camera high in the front corner, slowly panning
    camera.position.set(W / 2 - 0.8, H + 0.6, D / 2 + 3.2);
    look.set(-1, 0.6, -1);
    camera.fov = 58;
    camera.updateProjectionMatrix();
  } else {
    camera.position.set(here.x, 3.6, here.z + 6);
    look.set(here.x, 1.1, here.z - 1.5);
  }
  camera.lookAt(look);

  // --- Every frame ---
  const followOffset = new THREE.Vector3(0, 3.3, 5.6);
  const wantedCamera = new THREE.Vector3();
  const wantedLook = new THREE.Vector3();
  function update(dt, time) {
    for (const lamp of lamps) {
      // A lamp sometimes flickers, as old tubes do
      lamp.flicker -= dt;
      const off = lamp.flicker < 0 && lamp.flicker > -0.12;
      if (lamp.flicker < -0.12) lamp.flicker = 4 + Math.random() * 12;
      lamp.light.intensity = off ? lamp.base * 0.25 : lamp.base;
      lamp.tube.material.emissiveIntensity = off ? 0.4 : 2.2;
    }
    for (const step of animated) step(dt, time, hero?.group.position);
    const positions = dust.geometry.attributes.position;
    for (let i = 0; i < dustCount; i++) {
      let y = positions.getY(i) + dt * 0.05;
      if (y > H) y = 0;
      positions.setY(i, y);
      positions.setX(i, positions.getX(i) + Math.sin(time * 0.3 + i) * dt * 0.02);
    }
    positions.needsUpdate = true;

    if (watching) {
      camera.position.x = W / 2 - 0.8 + Math.sin(time * 0.15) * 1.2;
      camera.lookAt(look);
      for (const item of usable) item.ring.material.opacity = 0.18;
      return;
    }

    // Walking, in short steps, so a slow frame does not jump through a desk
    const p = hero.group.position;
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
    followAndLabel(dt, time);
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

  function followAndLabel(dt, time) {
    const p = hero.group.position;
    // The camera follows from behind and a little above, smoothly
    wantedCamera.copy(p).add(followOffset);
    wantedCamera.x = Math.max(-W / 2 + 2.2, Math.min(W / 2 - 2.2, wantedCamera.x));
    wantedLook.set(p.x, 1.1, p.z - 1.6);
    const ease = 1 - Math.exp(-dt * 4);
    camera.position.lerp(wantedCamera, ease);
    look.lerp(wantedLook, ease);
    camera.lookAt(look);

    // The nearest thing: its ring glows and its label floats over it
    nearest = findNearest();
    const shown = nearest || hovered;
    for (const item of usable) {
      const glow = item === nearest ? 0.75 + Math.sin(time * 5) * 0.2 : item === hovered ? 0.5 : 0.18;
      item.ring.material.opacity += (glow - item.ring.material.opacity) * Math.min(1, dt * 10);
    }
    // No label while a bubble (a text, choices, a keypad) is open: it would cover it
    if (shown && !stage.querySelector(".bubble")) {
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
      else placeOver(sayBox, projected.set(p.x, 2.35, p.z));
    }
  }

  shared.active = { scene, camera, update };

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

  return {
    startWalking: () => {},
    stopWalking: (key) => {
      if (key === "blur") held.clear();
      else held.delete(moveKey(key));
    },
    useNearest: () => {
      rememberKeys();
      if (nearest) use(nearest);
    },
    move3d: (key) => {
      if (!hero || !MOVE_KEYS[moveKey(key)]) return false;
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
    // Some things (the calendar) have one material per face
    child.material = Array.isArray(child.material) ? child.material.map(dim) : dim(child.material);
  });
}

// --- The character: a detective in a trench coat and a hat, made of simple shapes ----------

function makeHero(THREE) {
  const material = (color, roughness = 0.75) => new THREE.MeshStandardMaterial({ color, roughness });
  const coat = material("#a85f2c");
  const coatDark = material("#7d431c");
  const trousers = material("#2b2346");
  const skin = material("#f0c39b", 0.6);
  const hatColour = material("#1f2245", 0.5);
  const band = material("#c8343a", 0.5);
  const mesh = (geometry, mat, x, y, z) => {
    const m = new THREE.Mesh(geometry, mat);
    m.position.set(x, y, z);
    return m;
  };

  const group = new THREE.Group();
  const body = new THREE.Group(); // bobs while walking
  group.add(body);

  // Legs swing from the hip
  const legs = [-0.12, 0.12].map((x) => {
    const hip = new THREE.Group();
    hip.position.set(x, 0.86, 0);
    hip.add(mesh(new THREE.BoxGeometry(0.17, 0.78, 0.19), trousers, 0, -0.4, 0));
    hip.add(mesh(new THREE.BoxGeometry(0.19, 0.1, 0.32), material("#151018", 0.4), 0, -0.82, 0.05));
    body.add(hip);
    return hip;
  });

  // The trench coat: wider at the bottom, with a belt and a collar
  body.add(mesh(new THREE.CylinderGeometry(0.3, 0.42, 1.0, 16), coat, 0, 1.18, 0));
  body.add(mesh(new THREE.CylinderGeometry(0.335, 0.335, 0.07, 16), coatDark, 0, 1.22, 0));
  body.add(mesh(new THREE.BoxGeometry(0.08, 0.06, 0.03), material("#d8b45a", 0.3), 0, 1.22, 0.335));
  body.add(mesh(new THREE.CylinderGeometry(0.2, 0.3, 0.14, 16), coatDark, 0, 1.72, 0));
  body.add(mesh(new THREE.CylinderGeometry(0.07, 0.08, 0.1, 10), skin, 0, 1.8, 0));

  // Arms swing from the shoulder, opposite to the legs
  const arms = [-0.38, 0.38].map((x) => {
    const shoulder = new THREE.Group();
    shoulder.position.set(x, 1.62, 0);
    shoulder.rotation.z = x < 0 ? -0.08 : 0.08;
    shoulder.add(mesh(new THREE.BoxGeometry(0.15, 0.68, 0.17), coat, 0, -0.33, 0));
    shoulder.add(mesh(new THREE.SphereGeometry(0.075, 12, 10), skin, 0, -0.71, 0));
    body.add(shoulder);
    return shoulder;
  });

  // Head and hat
  const head = new THREE.Group();
  head.position.set(0, 1.98, 0);
  head.add(mesh(new THREE.SphereGeometry(0.19, 20, 16), skin, 0, 0, 0));
  // Hair at the back of the head, under the hat
  const hair = mesh(new THREE.SphereGeometry(0.2, 20, 16, 0, Math.PI * 2, 0, Math.PI * 0.62), material("#3a2516", 0.9), 0, 0.01, -0.025);
  hair.rotation.x = -0.5;
  head.add(hair);
  for (const x of [-0.07, 0.07]) head.add(mesh(new THREE.SphereGeometry(0.022, 8, 6), material("#1a1020", 0.3), x, 0.02, 0.17));
  head.add(mesh(new THREE.CylinderGeometry(0.34, 0.34, 0.035, 24), hatColour, 0, 0.14, 0));
  head.add(mesh(new THREE.CylinderGeometry(0.19, 0.22, 0.24, 20), hatColour, 0, 0.27, 0));
  head.add(mesh(new THREE.CylinderGeometry(0.222, 0.222, 0.06, 20), band, 0, 0.19, 0));
  body.add(head);

  // A soft dark spot under the feet
  const blob = new THREE.Mesh(
    new THREE.CircleGeometry(0.42, 24),
    new THREE.MeshBasicMaterial({ color: "#000000", transparent: true, opacity: 0.35, depthWrite: false })
  );
  blob.rotation.x = -Math.PI / 2;
  blob.position.y = 0.01;
  group.add(blob);
  group.scale.setScalar(0.88);

  let phase = 0;
  let swing = 0;
  function animate(dt, time, walking) {
    swing += ((walking ? 1 : 0) - swing) * Math.min(1, dt * 10);
    if (walking) phase += dt * 9.5;
    const s = Math.sin(phase) * 0.62 * swing;
    legs[0].rotation.x = s;
    legs[1].rotation.x = -s;
    arms[0].rotation.x = -s * 0.8;
    arms[1].rotation.x = s * 0.8;
    // Bob while walking, breathe while standing
    body.position.y = Math.abs(Math.sin(phase)) * 0.05 * swing + Math.sin(time * 2) * 0.008 * (1 - swing);
    head.rotation.y = Math.sin(time * 0.6) * 0.15 * (1 - swing);
  }
  return { group, animate };
}

// --- The kinds of things, built from simple shapes. Each one gets an empty group placed in the
// room; it adds its shapes and, for furniture, the box the character walks around. -------------

const THINGS = {
  desk({ THREE, group, thing, box, cylinder, block, animated }) {
    const top = box(2.0, 0.07, 0.95, "#6f7cc9", { roughness: 0.5 });
    top.position.y = 0.78;
    group.add(top);
    for (const [x, z] of [[-0.92, -0.4], [0.92, -0.4], [-0.92, 0.4], [0.92, 0.4]]) {
      const leg = box(0.07, 0.78, 0.07, "#22264a");
      leg.position.set(x, 0.39, z);
      group.add(leg);
    }
    // The monitor, its screen softly lit
    const monitor = box(0.78, 0.52, 0.08, "#1c1f3a");
    monitor.position.set(-0.2, 1.17, -0.22);
    const screen = box(0.68, 0.42, 0.01, "#2bb4c9", { emissive: "#2bb4c9", emissiveIntensity: 0.9 });
    screen.position.set(-0.2, 1.17, -0.175);
    const neck = box(0.08, 0.2, 0.08, "#1c1f3a");
    neck.position.set(-0.2, 0.9, -0.24);
    group.add(monitor, screen, neck);
    // A paper or two
    const paper = box(0.3, 0.01, 0.4, "#ece6d4");
    paper.position.set(0.45, 0.82, 0.12);
    paper.rotation.y = 0.3;
    group.add(paper);
    // The chair in front of it
    const seat = box(0.5, 0.07, 0.48, "#2e2a55");
    seat.position.set(0, 0.48, 0.78);
    const backrest = box(0.5, 0.55, 0.06, "#2e2a55");
    backrest.position.set(0, 0.8, 1.0);
    const pole = cylinder(0.04, 0.04, 0.44, "#14142a");
    pole.position.set(0, 0.24, 0.78);
    group.add(seat, backrest, pole);
    if (thing.mug) {
      // Tomás's mug, with the number he stares at (only sent when the player may read it)
      const mugTexture = canvasTexture(THREE, 256, 128, (g, w, h) => {
        g.fillStyle = "#f3ead6";
        g.fillRect(0, 0, w, h);
        if (thing.writing) {
          // Painted on both sides, so it can be read from wherever the player stands
          g.fillStyle = "#c8343a";
          g.font = "bold 64px Georgia, serif";
          g.textAlign = "center";
          g.textBaseline = "middle";
          g.fillText(thing.writing, w * 0.25, h / 2);
          g.fillText(thing.writing, w * 0.75, h / 2);
        }
      });
      const mug = new THREE.Mesh(
        new THREE.CylinderGeometry(0.075, 0.07, 0.16, 24),
        new THREE.MeshStandardMaterial({ map: mugTexture, roughness: 0.35 })
      );
      mug.position.set(0.7, 0.895, -0.05);
      mug.rotation.y = -0.4;
      const handle = new THREE.Mesh(
        new THREE.TorusGeometry(0.045, 0.012, 8, 16),
        new THREE.MeshStandardMaterial({ color: "#f3ead6", roughness: 0.35 })
      );
      handle.position.set(0.79, 0.895, -0.05);
      group.add(mug, handle);
      // Steam from the coffee
      const steam = [];
      for (let i = 0; i < 3; i++) {
        const puff = new THREE.Mesh(
          new THREE.SphereGeometry(0.03, 8, 6),
          new THREE.MeshBasicMaterial({ color: "#ffffff", transparent: true, opacity: 0.25, depthWrite: false })
        );
        puff.position.set(0.7, 1.0, -0.05);
        group.add(puff);
        steam.push(puff);
      }
      animated.push((dt, time) => {
        steam.forEach((puff, i) => {
          const t = (time * 0.4 + i / 3) % 1;
          puff.position.y = 0.98 + t * 0.35;
          puff.position.x = 0.7 + Math.sin(time * 2 + i) * 0.03;
          puff.material.opacity = 0.22 * (1 - t);
          puff.scale.setScalar(1 + t * 1.5);
        });
      });
    }
    block(thing.at[0], thing.at[1], 2.1, 1.0);
    block(thing.at[0], thing.at[1] + 0.85, 0.55, 0.45);
  },

  boss_desk({ THREE, group, thing, box, block }) {
    const wood = "#8a5530";
    const top = box(2.5, 0.09, 1.2, wood, { roughness: 0.45 });
    top.position.y = 0.8;
    const front = box(2.5, 0.72, 0.06, shade(wood, -0.25));
    front.position.set(0, 0.4, 0.55);
    const sideL = box(0.06, 0.76, 1.15, shade(wood, -0.2));
    sideL.position.set(-1.2, 0.38, 0);
    const sideR = sideL.clone();
    sideR.position.x = 1.2;
    group.add(top, front, sideL, sideR);
    // A green banker's lamp with a warm light
    const base = box(0.2, 0.04, 0.14, "#2a2a2a");
    base.position.set(0.85, 0.87, -0.3);
    const stem = box(0.03, 0.3, 0.03, "#b89a4a", { metalness: 0.6 });
    stem.position.set(0.85, 1.02, -0.3);
    const shadeMesh = new THREE.Mesh(
      new THREE.CylinderGeometry(0.06, 0.16, 0.12, 16, 1, true),
      new THREE.MeshStandardMaterial({ color: "#1f6b3a", emissive: "#1f6b3a", emissiveIntensity: 0.4, side: THREE.DoubleSide })
    );
    shadeMesh.position.set(0.85, 1.2, -0.3);
    const bulb = new THREE.PointLight("#ffcf7a", 3.5, 3.5, 2);
    bulb.position.set(0.85, 1.1, -0.3);
    group.add(base, stem, shadeMesh, bulb);
    // A pile of folders
    for (let i = 0; i < 3; i++) {
      const folder = box(0.42, 0.03, 0.3, i % 2 ? "#d8c49a" : "#c9b07a");
      folder.position.set(0.15, 0.86 + i * 0.03, -0.15);
      folder.rotation.y = i * 0.12;
      group.add(folder);
    }
    block(thing.at[0], thing.at[1], 2.6, 1.3);
  },

  access_card({ THREE, group, box, animated }) {
    // The card, half under a folder, glinting
    const card = box(0.3, 0.012, 0.19, "#f2c14e", { emissive: "#f2c14e", emissiveIntensity: 0.7, metalness: 0.4, roughness: 0.3 });
    card.position.set(0, 0.86, 0.15);
    card.rotation.y = -0.35;
    const stripe = box(0.3, 0.013, 0.04, "#3a2a10");
    stripe.position.set(0, 0.861, 0.12);
    stripe.rotation.y = -0.35;
    const glowTexture = canvasTexture(THREE, 64, 64, (g, w, h) => {
      const gradient = g.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, w / 2);
      gradient.addColorStop(0, "rgba(255,220,120,0.9)");
      gradient.addColorStop(1, "rgba(255,220,120,0)");
      g.fillStyle = gradient;
      g.fillRect(0, 0, w, h);
    });
    const glow = new THREE.Sprite(
      new THREE.SpriteMaterial({ map: glowTexture, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending })
    );
    glow.position.set(0, 0.95, 0.15);
    const light = new THREE.PointLight("#ffcc66", 1.5, 2.2, 2);
    light.position.set(0, 1.1, 0.15);
    group.add(card, stripe, glow, light);
    animated.push((dt, time) => {
      const pulse = 0.5 + Math.sin(time * 3) * 0.5;
      glow.scale.setScalar(0.55 + pulse * 0.35);
      light.intensity = 0.8 + pulse * 1.4;
    });
  },

  telescreen({ THREE, group, box, animated, thing }) {
    // The Party's eye: it follows the character around the room
    const y = 2.75;
    const frame = box(1.75, 1.12, 0.14, "#8b97d6", { roughness: 0.4, metalness: 0.3 });
    frame.position.set(0, y, 0.07);
    const screenTexture = canvasTexture(THREE, 256, 160, (g, w, h) => {
      const gradient = g.createRadialGradient(w / 2, h / 2, 10, w / 2, h / 2, w / 1.6);
      gradient.addColorStop(0, "#5fb6e6");
      gradient.addColorStop(1, "#1a3a7a");
      g.fillStyle = gradient;
      g.fillRect(0, 0, w, h);
    });
    const screen = new THREE.Mesh(
      new THREE.PlaneGeometry(1.55, 0.94),
      new THREE.MeshStandardMaterial({ map: screenTexture, emissive: "#ffffff", emissiveMap: screenTexture, emissiveIntensity: 0.9 })
    );
    screen.position.set(0, y, 0.145);
    const white = new THREE.Mesh(
      new THREE.CircleGeometry(0.42, 32),
      new THREE.MeshBasicMaterial({ color: "#eef3ff" })
    );
    white.scale.y = 0.55;
    white.position.set(0, y, 0.15);
    const iris = new THREE.Mesh(new THREE.CircleGeometry(0.15, 32), new THREE.MeshBasicMaterial({ color: "#d8345a" }));
    const pupil = new THREE.Mesh(new THREE.CircleGeometry(0.06, 24), new THREE.MeshBasicMaterial({ color: "#2a0a1a" }));
    iris.position.set(0, y, 0.155);
    pupil.position.set(0, y, 0.16);
    group.add(frame, screen, white, iris, pupil);
    const light = new THREE.PointLight("#5fb6e6", 2.5, 4, 2);
    light.position.set(0, y, 0.8);
    group.add(light);
    let blink = 3 + Math.random() * 4;
    animated.push((dt, time, heroAt) => {
      // Look towards the character (or wander when there is none)
      const dx = heroAt ? Math.max(-1, Math.min(1, (heroAt.x - thing.at[0]) / 5)) : Math.sin(time * 0.4);
      iris.position.x = dx * 0.18;
      pupil.position.x = dx * 0.2;
      blink -= dt;
      const closed = blink < 0 && blink > -0.15;
      if (blink < -0.15) blink = 3 + Math.random() * 5;
      white.scale.y = closed ? 0.05 : 0.55;
      iris.visible = pupil.visible = !closed;
    });
  },

  calendar({ THREE, group, thing }) {
    // The Party's calendar; the circled day is only drawn when the player may read it
    const texture = canvasTexture(THREE, 256, 320, (g, w, h) => {
      g.fillStyle = "#f3ead6";
      g.fillRect(0, 0, w, h);
      g.fillStyle = "#c8343a";
      g.fillRect(0, 0, w, 70);
      g.fillStyle = "#f3ead6";
      g.font = "bold 40px Georgia, serif";
      g.textAlign = "center";
      g.textBaseline = "middle";
      g.fillText("1984", w / 2, 38);
      g.font = "22px Georgia, serif";
      for (let day = 1; day <= 30; day++) {
        const col = (day - 1) % 6;
        const row = Math.floor((day - 1) / 6);
        const x = 26 + col * 41;
        const y = 102 + row * 46;
        g.fillStyle = "#4a4f8f";
        g.fillText(String(day), x, y);
        if (thing.writing && String(day) === thing.writing) {
          g.strokeStyle = "#c8343a";
          g.lineWidth = 4;
          g.beginPath();
          g.arc(x, y, 18, 0, Math.PI * 2);
          g.stroke();
        }
      }
    });
    const page = new THREE.Mesh(
      new THREE.BoxGeometry(0.85, 1.06, 0.03),
      [null, null, null, null, new THREE.MeshStandardMaterial({ map: texture, roughness: 0.8 }), null].map(
        (m) => m || new THREE.MeshStandardMaterial({ color: "#d9cfb5" })
      )
    );
    page.position.set(0, 2.55, 0.03);
    group.add(page);
  },

  notice_board({ THREE, group, box }) {
    const board = box(1.45, 1.05, 0.06, "#8a6338", { roughness: 0.95 });
    board.position.set(0, 2.75, 0.04);
    const frame = box(1.55, 1.15, 0.04, "#5a3b1c");
    frame.position.set(0, 2.75, 0.01);
    group.add(frame, board);
    const notes = [
      [-0.4, 2.95, "#f3ead6", 0.05],
      [0.3, 2.85, "#f6e7a8", -0.04],
      [-0.25, 2.45, "#f3ead6", 0.08],
    ];
    for (const [x, y, color, tilt] of notes) {
      const texture = canvasTexture(THREE, 128, 160, (g, w, h) => {
        g.fillStyle = color;
        g.fillRect(0, 0, w, h);
        g.fillStyle = "#7a7468";
        for (let line = 0; line < 6; line++) g.fillRect(14, 30 + line * 20, w - 28 - (line % 2) * 22, 5);
      });
      const note = new THREE.Mesh(new THREE.PlaneGeometry(0.42, 0.52), new THREE.MeshStandardMaterial({ map: texture, roughness: 0.9 }));
      note.position.set(x, y, 0.075);
      note.rotation.z = tilt;
      const pin = new THREE.Mesh(new THREE.SphereGeometry(0.025, 8, 6), new THREE.MeshStandardMaterial({ color: "#c8343a" }));
      pin.position.set(x, y + 0.22, 0.09);
      group.add(note, pin);
    }
  },

  cabinet({ group, box, thing, block }) {
    const body = box(0.9, 1.6, 0.65, "#4a5180", { roughness: 0.5, metalness: 0.3 });
    body.position.y = 0.8;
    group.add(body);
    for (let i = 0; i < 4; i++) {
      const handle = box(0.25, 0.03, 0.03, "#c9cbe0", { metalness: 0.7 });
      handle.position.set(0, 0.35 + i * 0.38, 0.34);
      group.add(handle);
    }
    block(thing.at[0], thing.at[1], 1.0, 0.75);
  },

  archive_door({ THREE, group, box, animated }) {
    // On the right wall (the group is turned): the door, its frame, a card reader and a keypad
    const frame = box(1.55, 2.75, 0.18, "#14163a");
    frame.position.set(0, 1.375, 0.05);
    const door = box(1.3, 2.55, 0.08, "#2c3172", { roughness: 0.5, metalness: 0.2 });
    door.position.set(0, 1.275, 0.13);
    const knob = new THREE.Mesh(new THREE.SphereGeometry(0.05, 12, 10), new THREE.MeshStandardMaterial({ color: "#d8b45a", metalness: 0.8, roughness: 0.3 }));
    knob.position.set(-0.48, 1.2, 0.2);
    const lamp = new THREE.Mesh(new THREE.SphereGeometry(0.07, 12, 10), new THREE.MeshBasicMaterial({ color: "#f2c14e" }));
    lamp.position.set(0, 2.9, 0.1);
    const lampLight = new THREE.PointLight("#f2c14e", 2, 3, 2);
    lampLight.position.set(0, 2.8, 0.5);
    const keypadTexture = canvasTexture(THREE, 96, 160, (g, w, h) => {
      g.fillStyle = "#14163a";
      g.fillRect(0, 0, w, h);
      g.fillStyle = "#7fd0ff";
      for (let r = 0; r < 4; r++) for (let c = 0; c < 3; c++) g.fillRect(12 + c * 26, 20 + r * 34, 18, 22);
    });
    const keypad = new THREE.Mesh(
      new THREE.BoxGeometry(0.2, 0.33, 0.05),
      new THREE.MeshStandardMaterial({ map: keypadTexture, emissive: "#ffffff", emissiveMap: keypadTexture, emissiveIntensity: 0.7 })
    );
    keypad.position.set(1.0, 1.3, 0.1);
    const reader = box(0.16, 0.22, 0.05, "#1c1c22");
    reader.position.set(1.0, 1.65, 0.1);
    const led = new THREE.Mesh(new THREE.SphereGeometry(0.02, 8, 6), new THREE.MeshBasicMaterial({ color: "#ff3b3b" }));
    led.position.set(1.0, 1.73, 0.13);
    // A sign: no name, only a number
    const sign = canvasTexture(THREE, 256, 64, (g, w, h) => {
      g.fillStyle = "#0e0f24";
      g.fillRect(0, 0, w, h);
      g.fillStyle = "#c8343a";
      g.font = "bold 34px Georgia, serif";
      g.textAlign = "center";
      g.textBaseline = "middle";
      g.fillText("101-A", w / 2, h / 2 + 2);
    });
    const plate = new THREE.Mesh(new THREE.PlaneGeometry(0.6, 0.15), new THREE.MeshStandardMaterial({ map: sign }));
    plate.position.set(0, 2.3, 0.175);
    group.add(frame, door, knob, lamp, lampLight, keypad, reader, led, plate);
    animated.push((dt, time) => {
      led.material.color.set(Math.sin(time * 4) > 0 ? "#ff3b3b" : "#5a1010");
    });
  },

  exit({ THREE, group, box }) {
    // On the left wall: the way home, a dark doorway with warm light behind it
    const frame = box(1.4, 2.6, 0.16, "#14163a");
    frame.position.set(0, 1.3, 0.05);
    const opening = new THREE.Mesh(
      new THREE.PlaneGeometry(1.15, 2.4),
      new THREE.MeshStandardMaterial({ color: "#3a2410", emissive: "#ff9a3c", emissiveIntensity: 0.35 })
    );
    opening.position.set(0, 1.2, 0.14);
    const warm = new THREE.PointLight("#ffab55", 2.5, 4, 2);
    warm.position.set(0, 1.4, 0.8);
    const arrow = canvasTexture(THREE, 128, 64, (g, w, h) => {
      g.fillStyle = "#0e0f24";
      g.fillRect(0, 0, w, h);
      g.fillStyle = "#f2c14e";
      g.font = "bold 40px sans-serif";
      g.textAlign = "center";
      g.textBaseline = "middle";
      g.fillText("⌂", w / 2, h / 2 + 2);
    });
    const sign = new THREE.Mesh(new THREE.PlaneGeometry(0.4, 0.2), new THREE.MeshStandardMaterial({ map: arrow, emissive: "#ffffff", emissiveMap: arrow, emissiveIntensity: 0.5 }));
    sign.position.set(0, 2.8, 0.15);
    group.add(frame, opening, warm, sign);
  },
};
