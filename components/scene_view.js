// The whole game screen, fullscreen: top bar, the clickable picture, narration, endings and chat.
//
// The picture: clicking the floor makes the character walk there. Clicking a spot makes the
// character walk to it and then sends {id, x} to Python as the "action" trigger. A talk spot
// (a character or object) opens a bubble with options; a spot with a code_prompt opens a
// keypad and sends {id, x, code}; a look only shows a text.
// Buttons outside the picture send a "command" (menu, play_again, next_chapter, new_room_game)
// and the chat panel sends "chat". Python decides everything; nothing is decided here.
//
// Python sends a scene_key. When only the chat changed (co-op refresh every 2 s), the screen is
// not rebuilt, so an open bubble or a half-typed code is kept.
//
// The same component draws the main menu (data.mode === "menu"): Play, How to Play, Settings, Exit.
// Sound is generated here with the Web Audio API (no audio files) and the browser's fullscreen is
// requested when the player starts. Sound and fullscreen settings live in this browser only
// (localStorage); the language is sent to Python, because Python writes every text.

const WIDTH = 800; // picture coordinates, same as the SVG viewBox
const HEIGHT = 400;
const SPEED = 260; // picture units per second
const CHAR_W = 84; // character.svg viewBox size
const CHAR_H = 180;
const CHAR_TOP = 172; // distance from the top of character.svg to the feet

const pct = (value, total) => `${(value / total) * 100}%`;

function el(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}

// --- Settings kept in this browser --------------------------------------------------------

const SETTINGS_KEY = "forbiddenArchive.settings";
const DEFAULT_SETTINGS = { music: true, volume: 0.5, sfx: true, muted: false, fullscreen: true, showText: true, usedKeys: false, view3d: true };

function loadSettings() {
  try {
    return { ...DEFAULT_SETTINGS, ...JSON.parse(localStorage.getItem(SETTINGS_KEY) || "{}") };
  } catch {
    return { ...DEFAULT_SETTINGS };
  }
}

function saveSettings(settings) {
  try {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
  } catch {
    // private window or storage blocked: the settings just last until the page closes
  }
}

// --- Voices: the browser's own speech (no audio files, nothing sent anywhere) -------------

// Each speaker gets a different pitch, so the hero and Tomás do not sound the same
// `pick` chooses a different installed voice for each speaker when the browser has several
const VOICE_STYLE = {
  you: { pitch: 1.05, rate: 1.0, pick: 0 },
  "Tomás": { pitch: 0.8, rate: 0.94, pick: 1 },
  "Júlia": { pitch: 1.2, rate: 1.0, pick: 2 },
  Seller: { pitch: 0.9, rate: 1.1, pick: 3 },
  Clara: { pitch: 1.3, rate: 1.05, pick: 4 },
  Tiago: { pitch: 0.85, rate: 0.9, pick: 1 },
  Rita: { pitch: 1.25, rate: 1.05, pick: 2 },
};

// The game no longer speaks (the team decided against voices reading the texts aloud): speak()
// only calls onEnd, so the places that used to wait for a line still go on
const VOICES_ON = false;

function speak(text, speaker, lang, onEnd) {
  const synth = globalThis.speechSynthesis;
  if (!VOICES_ON || !text || !synth) return onEnd && setTimeout(onEnd, 0);
  synth.cancel();
  const line = new SpeechSynthesisUtterance(text);
  line.lang = lang || "en-GB";
  const style = VOICE_STYLE[speaker] || VOICE_STYLE.you;
  const all = synth.getVoices();
  let voices = all.filter((v) => v.lang === line.lang);
  if (!voices.length) voices = all.filter((v) => v.lang.startsWith(line.lang.slice(0, 2)));
  if (voices.length) line.voice = voices[style.pick % voices.length];
  line.pitch = style.pitch;
  line.rate = style.rate;
  line.volume = Math.min(1, 0.4 + loadSettings().volume);
  if (onEnd) line.onend = onEnd;
  synth.speak(line);
}

function stopSpeaking() {
  globalThis.speechSynthesis?.cancel();
}

function goFullscreen() {
  if (loadSettings().fullscreen && !document.fullscreenElement && document.documentElement.requestFullscreen) {
    enterFullscreen();
  }
}

// Full screen, keeping the Esc key for the game (Chrome and Edge: the Keyboard Lock API): the first
// Esc closes the note, the thing or the conversation, and only an Esc with nothing open leaves full
// screen. Where the browser cannot lock it, Esc leaves full screen as usual.
function enterFullscreen() {
  document.documentElement.requestFullscreen?.()
    .then(() => navigator.keyboard?.lock?.(["Escape"]))
    .catch(() => {});
}

function leaveFullscreen() {
  navigator.keyboard?.unlock?.();
  if (document.fullscreenElement && document.exitFullscreen) document.exitFullscreen().catch(() => {});
}

// --- Sound: one engine for the whole page, kept across redraws ----------------------------

const Sound = (globalThis.__forbiddenArchiveSound ??= createSound());

// Music themes, played by a small step sequencer (no audio files). Each bar has one chord
// [root as a MIDI note, quality]; patterns have 16 steps per bar ("x" plays, "o" = the fifth).
// Percussion: k kick, b heartbeat, h hi-hat, s brush, c clock tick, d water drip, m metal clank.
// Python picks the theme for each scene (logic.scene_music).
const CHORDS = { maj: [0, 4, 7], min: [0, 3, 7], dim: [0, 3, 6], sus: [0, 5, 7], min7: [0, 3, 7, 10], maj7: [0, 4, 7, 11] };
const SCALES = { minor: [0, 3, 5, 7, 10], major: [0, 2, 4, 7, 9] };
const THEMES = {
  menu: { bpm: 72, pad: "triangle", scale: "minor", lead: 0.14, chords: [[57, "min"], [53, "maj"], [48, "maj"], [55, "maj"]],
    bass: "x.......x...x...", arp: "x..x..x..x..x.x.", perc: { h: "....x.......x..." } },
  ministry: { bpm: 84, pad: "triangle", scale: "minor", lead: 0.05, chords: [[50, "min"], [46, "maj"], [43, "min"], [45, "maj"]],
    bass: "x...x...x...x...", arp: "x.x.x.x.x.x.x.x.", arpWave: "square", perc: { c: "x...x...x...x..." } },
  archive: { bpm: 60, pad: "sine", scale: "minor", lead: 0.2, chords: [[52, "min"], [48, "maj7"], [45, "min"], [47, "maj"]],
    bass: "x...............", arp: "x.......x.......", perc: { h: "..........x....." } },
  tunnels: { bpm: 66, pad: "sawtooth", scale: "minor", lead: 0.05, chords: [[48, "min"], [48, "min"], [44, "maj"], [43, "maj"]],
    bass: "x.....x.x.......", arp: "", perc: { d: "x.....x...x....." } },
  hideout: { bpm: 80, pad: "triangle", scale: "major", lead: 0.18, chords: [[53, "maj"], [48, "maj"], [50, "min"], [46, "maj"]],
    bass: "x...o...x...o...", arp: "x.x.x.x.x.x.x.x.", perc: { h: "..x...x...x...x." } },
  night_city: { bpm: 92, pad: "triangle", scale: "minor", lead: 0.12, chords: [[57, "min7"], [50, "min7"], [52, "min7"], [45, "min7"]],
    bass: "x.o.x.o.x.o.x.o.", arp: "", perc: { h: "x.x.x.x.x.x.x.x.", s: "....x.......x..." } },
  radio: { bpm: 104, pad: "sawtooth", scale: "minor", lead: 0.1, chords: [[52, "min"], [48, "maj"], [55, "maj"], [50, "maj"]],
    bass: "x..x..x.x..x..x.", arp: "xxxxxxxxxxxxxxxx", arpWave: "square", perc: { k: "x.......x.......", c: "..x...x...x...x." } },
  prison: { bpm: 70, pad: "sine", scale: "minor", lead: 0.08, chords: [[47, "min"], [48, "maj"], [47, "min"], [42, "dim"]],
    bass: "x.......x.......", arp: "x...x...x...x...", perc: { m: "x...............", k: "........x......." } },
  danger: { bpm: 150, pad: "sawtooth", scale: "minor", lead: 0, chords: [[48, "min"], [49, "maj"], [48, "min"], [47, "dim"]],
    bass: "x.x.x.x.x.x.x.x.", arp: "x.xxx.xxx.xxx.xx", arpWave: "square", perc: { b: "x.......x.......", h: "xxxxxxxxxxxxxxxx" } },
  victory: { bpm: 96, pad: "triangle", scale: "major", lead: 0.25, chords: [[48, "maj"], [55, "maj"], [57, "min"], [53, "maj"]],
    bass: "x...x...x...x...", arp: "x.x.x.x.x.x.x.x.", perc: { k: "x.......x.......", s: "....x.......x..." } },
  defeat: { bpm: 58, pad: "sine", scale: "minor", lead: 0.1, chords: [[45, "min"], [50, "min"], [52, "maj"], [45, "min"]],
    bass: "x...............", arp: "", perc: {} },
  // Carcavelos beach: slow waves of brushed noise under open chords (specs/levels-2-and-3.md)
  beach: { bpm: 64, pad: "sine", scale: "major", lead: 0.16, chords: [[50, "maj7"], [55, "maj7"], [47, "min7"], [52, "sus"]],
    bass: "x.......o.......", arp: "x...x.....x.....", perc: { s: "x.......x.......", d: "......x........." } },
  // The morning of Level 3: bright and in a hurry
  morning: { bpm: 112, pad: "triangle", scale: "major", lead: 0.2, chords: [[55, "maj"], [52, "min"], [48, "maj"], [50, "maj"]],
    bass: "x...x.o.x...x.o.", arp: "x.xxx.x.x.xxx.x.", perc: { k: "x.......x.......", h: "..x...x...x...x.", s: "....x.......x..." } },
};
const freqOf = (midi) => 440 * 2 ** ((midi - 69) / 12);

function createSound() {
  let ctx = null;
  let master = null;
  let musicBus = null;
  let wanted = null; // the theme to play once sound is allowed
  let playing = null; // { name, theme, bus, step, nextTime }

  function unlock() {
    if (!ctx) {
      const AudioContext = globalThis.AudioContext || globalThis.webkitAudioContext;
      if (!AudioContext) return false;
      ctx = new AudioContext();
      master = ctx.createGain();
      master.connect(ctx.destination);
      musicBus = ctx.createGain();
      const filter = ctx.createBiquadFilter();
      filter.type = "lowpass";
      filter.frequency.value = 3200;
      musicBus.connect(filter).connect(master);
      setInterval(schedule, 40);
    }
    if (ctx.state === "suspended") ctx.resume();
    applySettings();
    if (wanted && playing?.name !== wanted) switchTo(wanted);
    return true;
  }

  function applySettings() {
    if (!ctx) return;
    const settings = loadSettings();
    master.gain.setTargetAtTime(settings.muted ? 0 : settings.volume, ctx.currentTime, 0.1);
    musicBus.gain.setTargetAtTime(settings.music ? 0.3 : 0, ctx.currentTime, 0.3);
  }

  // One note of the music: an oscillator with a short attack and a decay, into the theme's bus
  function note(bus, freq, start, length, wave, volume, attack = 0.01) {
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = wave;
    osc.frequency.value = freq;
    gain.gain.setValueAtTime(0.0001, start);
    gain.gain.linearRampToValueAtTime(volume, start + attack);
    gain.gain.exponentialRampToValueAtTime(0.0001, start + length);
    osc.connect(gain).connect(bus);
    osc.start(start);
    osc.stop(start + length + 0.05);
  }

  function sweep(bus, from, to, start, length, volume) {
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.frequency.setValueAtTime(from, start);
    osc.frequency.exponentialRampToValueAtTime(to, start + length);
    gain.gain.setValueAtTime(volume, start);
    gain.gain.exponentialRampToValueAtTime(0.0001, start + length);
    osc.connect(gain).connect(bus);
    osc.start(start);
    osc.stop(start + length + 0.05);
  }

  function hiss(bus, start, length, volume, type, frequency) {
    const buffer = ctx.createBuffer(1, Math.floor(ctx.sampleRate * length), ctx.sampleRate);
    const samples = buffer.getChannelData(0);
    for (let i = 0; i < samples.length; i++) samples[i] = (Math.random() * 2 - 1) * (1 - i / samples.length);
    const source = ctx.createBufferSource();
    const filter = ctx.createBiquadFilter();
    const gain = ctx.createGain();
    source.buffer = buffer;
    filter.type = type;
    filter.frequency.value = frequency;
    gain.gain.value = volume;
    source.connect(filter).connect(gain).connect(bus);
    source.start(start);
  }

  const DRUMS = {
    k: (bus, t) => sweep(bus, 120, 40, t, 0.18, 0.5),
    b: (bus, t) => {
      sweep(bus, 75, 35, t, 0.16, 0.7);
      sweep(bus, 70, 32, t + 0.2, 0.16, 0.5);
    },
    h: (bus, t) => hiss(bus, t, 0.04, 0.05, "highpass", 7000),
    s: (bus, t) => hiss(bus, t, 0.14, 0.08, "bandpass", 1800),
    c: (bus, t, step) => note(bus, step % 8 ? 1250 : 1550, t, 0.03, "square", 0.04, 0.002),
    d: (bus, t) => Math.random() < 0.6 && sweep(bus, 1400 + Math.random() * 500, 600, t, 0.09, 0.07),
    m: (bus, t) => [220, 341, 513, 787].forEach((f, i) => note(bus, f, t, 1.4 - i * 0.2, "sine", 0.05, 0.002)),
  };

  function playStep(play, step, t, stepLength) {
    const theme = play.theme;
    const s = step % 16;
    const [root, quality] = theme.chords[Math.floor(step / 16) % theme.chords.length];
    const tones = CHORDS[quality];
    const bar = stepLength * 16;
    if (s === 0) {
      // the chord, held for the whole bar
      tones.forEach((tone, i) => note(play.bus, freqOf(root + tone), t, bar * 1.05, theme.pad, i ? 0.05 : 0.07, bar * 0.25));
    }
    const bass = theme.bass[s];
    if (bass === "x" || bass === "o") note(play.bus, freqOf(root - 12 + (bass === "o" ? 7 : 0)), t, stepLength * 3, "triangle", 0.22);
    if (theme.arp && theme.arp[s] === "x") {
      play.arp = (play.arp + 1) % (tones.length * 2);
      const tone = tones[play.arp % tones.length] + 12 * Math.floor(play.arp / tones.length);
      note(play.bus, freqOf(root + 12 + tone), t, stepLength * 1.6, theme.arpWave || "triangle", theme.arpWave === "square" ? 0.025 : 0.05);
    }
    // a light melody, different every time: notes of the scale over the chord, on the beats
    if (theme.lead && s % 2 === 0 && Math.random() < theme.lead) {
      const scale = SCALES[theme.scale];
      const tone = scale[Math.floor(Math.random() * scale.length)];
      note(play.bus, freqOf(root + 24 + tone), t, stepLength * 6, "sine", 0.07);
    }
    for (const [drum, pattern] of Object.entries(theme.perc || {})) {
      if (pattern[s] === "x") DRUMS[drum](play.bus, t, s);
    }
  }

  // Notes are planned a little ahead of time, so the music stays steady
  function schedule() {
    if (!playing || ctx.state !== "running") return;
    const stepLength = 60 / playing.theme.bpm / 4;
    // after the tab was hidden, skip the notes that were missed instead of playing them all at once
    if (playing.nextTime < ctx.currentTime - 0.05) playing.nextTime = ctx.currentTime + 0.02;
    while (playing.nextTime < ctx.currentTime + 0.15) {
      playStep(playing, playing.step, playing.nextTime, stepLength);
      playing.nextTime += stepLength;
      playing.step += 1;
    }
  }

  // A new theme fades in while the old one fades out
  function switchTo(name) {
    const theme = THEMES[name] || THEMES.menu;
    const now = ctx.currentTime;
    if (playing) {
      const old = playing.bus;
      old.gain.setTargetAtTime(0, now, 0.5);
      setTimeout(() => old.disconnect(), 4000);
    }
    const bus = ctx.createGain();
    bus.gain.setValueAtTime(0, now);
    bus.gain.setTargetAtTime(1, now, 0.6);
    bus.connect(musicBus);
    playing = { name, theme, bus, step: 0, arp: -1, nextTime: now + 0.05 };
  }

  function music(name) {
    wanted = name;
    if (!ctx || ctx.state !== "running") return;
    if (playing?.name !== name) switchTo(name);
  }

  function tone(freq, duration, type = "sine", volume = 0.25, delay = 0) {
    if (!ctx || ctx.state !== "running" || !loadSettings().sfx || loadSettings().muted) return;
    note(master, freq, ctx.currentTime + delay, duration, type, volume, 0.005);
  }

  function noise(duration, volume = 0.18, frequency = 500) {
    if (!ctx || ctx.state !== "running" || !loadSettings().sfx || loadSettings().muted) return;
    hiss(master, ctx.currentTime, duration, volume, "bandpass", frequency);
  }

  // Browsers only allow sound after a click: the first click or key anywhere turns it on
  document.addEventListener("pointerdown", unlock, { capture: true });
  document.addEventListener("keydown", unlock, { capture: true });

  return {
    unlock,
    applySettings,
    music,
    // what is playing now (for checking in the browser's console)
    theme: () => (ctx && ctx.state === "running" && playing ? playing.name : null),
    click: () => tone(720, 0.06, "square", 0.08),
    tick: () => tone(1180, 0.04, "square", 0.05),
    step: () => noise(0.06, 0.25, 260 + Math.random() * 120),
    success: () => {
      tone(660, 0.18, "sine", 0.2);
      tone(990, 0.3, "sine", 0.18, 0.12);
    },
    refused: () => {
      tone(150, 0.28, "sawtooth", 0.12);
      tone(110, 0.3, "sawtooth", 0.1, 0.08);
    },
    ending: () => [523.3, 659.3, 784, 1046.5].forEach((f, i) => tone(f, 0.5, "triangle", 0.18, i * 0.16)),
  };
}

// --- Level clock: time spent in the current level, kept in this browser --------------------
// Python sends {level, run, finished}. A new run id (new game, restart, next level) starts the
// clock from zero; it only counts while the game screen is open and the page is visible.

const Timer = (globalThis.__forbiddenArchiveTimer ??= createTimer());

function formatTime(ms) {
  const total = Math.floor(ms / 1000);
  const h = Math.floor(total / 3600);
  const m = String(Math.floor((total % 3600) / 60)).padStart(2, "0");
  const s = String(total % 60).padStart(2, "0");
  return h ? `${h}:${m}:${s}` : `${m}:${s}`;
}

function createTimer() {
  let run = null;
  let label = null;
  let last = performance.now();
  const read = (key) => {
    try {
      return JSON.parse(localStorage.getItem(key) || "null");
    } catch {
      return null;
    }
  };
  const write = (key, value) => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch {
      // storage blocked: the clock still runs until the page closes
    }
  };
  const runKey = (level) => `forbiddenArchive.timer.${level}`;
  const bestKey = (level) => `forbiddenArchive.best.${level}`;
  const show = () => label && run && (label.textContent = `⏱ ${formatTime(run.ms)}`);

  setInterval(() => {
    const now = performance.now();
    const delta = Math.min(now - last, 2000);
    last = now;
    if (!label || !run || run.done || document.visibilityState !== "visible") return;
    run.ms += delta;
    write(runKey(run.level), run);
    show();
  }, 500);

  return {
    attach(info, element) {
      let stored = read(runKey(info.level));
      const fresh = { level: info.level, run: info.run, ms: 0, done: false };
      if (!stored || (info.run && stored.run !== info.run) || (stored.done && !info.finished)) stored = fresh;
      run = stored;
      label = element;
      if (info.finished && !run.done) {
        run.done = true;
        const best = read(bestKey(info.level));
        // only an ending that completes the level counts as a record
        if (info.completed && (!best || run.ms < best)) write(bestKey(info.level), run.ms);
      }
      write(runKey(info.level), run);
      last = performance.now();
      show();
    },
    detach() {
      label = null;
    },
    current: () => run,
    best: (level) => read(bestKey(level)),
  };
}

export default function render({ data, parentElement, setTriggerValue }) {
  const existing = parentElement.querySelector(".game");
  if (existing && existing.dataset.sceneKey === data.scene_key) {
    // A co-op refresh: the same screen, with new chat messages and the friend's new position
    updateChat(existing, data.chat);
    globalThis.__gitOutPartnerAt = data.partner?.at || null;
    globalThis.__gitOutPartnerHere = !!data.partner && data.partner.here !== false;
    return;
  }
  globalThis.__gitOutPartnerAt = data.partner?.at || null;
  globalThis.__gitOutPartnerHere = !!data.partner && data.partner.here !== false;
  existing?.remove();
  stopSpeaking();
  // Which place (and which run of it) was on the screen before this one: a 3D room uses it to
  // keep the character where it was after an action in the same room
  globalThis.__forbiddenArchiveCameFrom = globalThis.__forbiddenArchiveShowing;
  globalThis.__forbiddenArchiveShowing = data.mode === "game" ? `${data.place}:${data.timer.run}` : null;
  // The 2D/3D button draws the same screen again, here in the browser (no message to Python)
  globalThis.__forbiddenArchiveRedraw = () => {
    parentElement.querySelector(".game")?.remove();
    render({ data, parentElement, setTriggerValue });
  };
  globalThis.__forbiddenArchiveKeys = null;

  if (data.mode === "menu") {
    Timer.detach();
    Sound.music("menu");
    parentElement.appendChild(menuScreen(data, setTriggerValue));
    return;
  }

  Sound.music(data.music || "menu");
  if (data.ending) Sound.ending();
  else if (data.message) (data.message.ok ? Sound.success : Sound.refused)();

  const game = el("div", "game");
  game.dataset.sceneKey = data.scene_key;
  if (!loadSettings().showText) game.classList.add("text-hidden");
  // Around the picture, a blurred copy of it fills the screen
  const backdrop = el("div", "backdrop");
  if (data.background) backdrop.innerHTML = `<img src="${data.background}" alt="">`;
  game.append(backdrop, topBar(data, setTriggerValue));
  const stageWrap = el("div", "stage-wrap");
  const stage = el("div", "stage");
  stageWrap.append(stage);
  // Narration and (in co-op) the chat: over the bottom of the picture (under it on tall screens)
  const bottom = el("div", "bottom");
  bottom.append(narration(data));
  if (data.chat) bottom.append(chatPanel(data.chat, setTriggerValue));
  game.append(stageWrap, bottom);
  parentElement.appendChild(game);
  // On wide screens the narration is drawn over the bottom of the picture: --narr is how much of
  // the picture it covers, so the bars, choices and boxes at the bottom sit above it, not under it
  const coverNarration = () => {
    const over = getComputedStyle(bottom).position === "absolute";
    const covered = over ? stage.getBoundingClientRect().bottom - bottom.getBoundingClientRect().top : 0;
    game.style.setProperty("--narr", `${Math.max(0, Math.round(covered))}px`);
  };
  coverNarration();
  if (globalThis.ResizeObserver) {
    const watch = new ResizeObserver(coverNarration);
    watch.observe(bottom);
    watch.observe(stage);
  }

  // A level with a countdown shows the time of day; the level clock still counts, out of sight
  Timer.attach(data.timer, data.countdown ? el("span") : game.querySelector(".clock"));
  if (data.countdown) startCountdown(game, data, setTriggerValue);
  // A place with a 3D room is drawn in 3D (scene3d.js); everything else is the 2D picture
  const keys = wants3D(data) ? buildRoom3D(stage, data, setTriggerValue) : buildPicture(stage, data, setTriggerValue);
  if (data.ending) stage.append(endingCard(data, setTriggerValue));
  // A level that starts with an email over the whole screen (Level 2): "Start" closes it
  // (Level 1's briefing opens by itself, over the 3D room too)
  if (data.intro && !data.intro.again && (!wants3D(data) || data.intro.auto)) game.append(introEmail(data.intro, setTriggerValue));
  // Something just picked up appears as itself for a moment (a card with its number, a post-it...)
  const have = data.notebook.items.map((item) => item.id);
  const before = globalThis.__forbiddenArchiveItems;
  if (before && before.run === data.timer.run && data.message?.ok) {
    const fresh = data.notebook.items.filter((item) => !before.have.includes(item.id));
    if (fresh.length) showPickedUp(game, fresh);
  }
  globalThis.__forbiddenArchiveItems = { run: data.timer.run, have };
  if (data.dialogue) {
    const overlay = dialogueOverlay(data.dialogue, data);
    // The hero stays where it stood while they talk
    const hero = stage.querySelector(".hero")?.cloneNode(true);
    if (hero) overlay.insertBefore(hero, overlay.querySelector(".dialogue-box"));
    stage.append(overlay);
  }
  globalThis.__forbiddenArchiveKeys = (event, down) => gameKeys(game, data, setTriggerValue, keys, event, down);
}

// --- Keyboard ----------------------------------------------------------------------------------
// One listener for the page; it calls the handler of the screen on show. Keys never fire while
// typing (a code, the chat, a form, the text mode's fields).

if (!globalThis.__forbiddenArchiveKeyListener) {
  globalThis.__forbiddenArchiveKeyListener = true;
  const typing = (event) => {
    const target = event.composedPath?.()[0] || event.target;
    return target && (target.isContentEditable || ["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName));
  };
  document.addEventListener("keydown", (event) => {
    // Esc works even while typing a code (it closes the padlock, the keypad, the login)
    if ((!typing(event) || event.key === "Escape") && !event.ctrlKey && !event.metaKey && !event.altKey) globalThis.__forbiddenArchiveKeys?.(event, true);
  });
  document.addEventListener("keyup", (event) => globalThis.__forbiddenArchiveKeys?.(event, false));
  globalThis.addEventListener("blur", () => globalThis.__forbiddenArchiveKeys?.({ key: "blur" }, false));
}

function toggleFullscreen() {
  if (document.fullscreenElement) leaveFullscreen();
  else enterFullscreen();
}

function toggleMute(button) {
  const settings = loadSettings();
  settings.muted = !settings.muted;
  saveSettings(settings);
  Sound.applySettings();
  if (!settings.muted) Sound.click();
  button.textContent = settings.muted ? "🔇" : "🔊";
  button.setAttribute("aria-pressed", String(!settings.muted));
}

function toggleText(game) {
  const settings = loadSettings();
  settings.showText = !settings.showText;
  saveSettings(settings);
  game.classList.toggle("text-hidden", !settings.showText);
}

function gameKeys(game, data, setTriggerValue, keys, event, down) {
  const key = event.key;
  const handled = () => event.preventDefault?.();
  if (!down) {
    keys.stopWalking(key);
    return;
  }
  const click = (button) => {
    if (!button) return false;
    handled();
    button.click();
    return true;
  };
  const numbered = (container) => {
    const n = Number(key);
    if (!(n >= 1 && n <= 9)) return false;
    const marked = container.querySelector(`button[data-key="${n}"]`);
    return click(marked || [...container.querySelectorAll(".ending-buttons button")][n - 1]);
  };
  // Overlays first, from the top: a question, the notebook, a conversation, the ending, a bubble
  const confirm = game.querySelector(".confirm");
  if (confirm) {
    if (key === "Escape" || key === "n" || key === "N") return click(confirm.querySelector(".no"));
    if (key === "Enter" || key === "y" || key === "Y" || key === "s" || key === "S") return click(confirm.querySelector(".yes"));
    return;
  }
  // The level's opening email (level 2): E, Enter or Space close it, like its Start button (a held
  // key that opened it does not close it again straight away)
  const intro = game.querySelector(".intro-email");
  if (intro) {
    const start = intro.querySelector(".intro-start");
    const keys = start?.textContent === intro.dataset.close ? ["e", "E", "Enter", " ", "Escape"] : ["e", "E", "Enter", " "];
    if (keys.includes(key) && !event.repeat && start && !start.hidden && !start.disabled) {
      return click(start);
    }
    handled();
    return;
  }
  const book = game.querySelector(".notebook");
  if (book) {
    if (key === "Escape" || key === "n" || key === "N") {
      handled();
      book.remove();
    }
    return;
  }
  const dialogue = game.querySelector(".dialogue:not(.closing)");
  if (dialogue) {
    if ([" ", "Enter", "ArrowRight", "e", "E"].includes(key)) return click(dialogue.querySelector(".dialogue-next"));
    return;
  }
  const ending = game.querySelector(".ending");
  if (ending) {
    if (key === "Enter") return click(ending.querySelector(".big.primary"));
    if (numbered(ending)) return;
  }
  // Looking at a thing close up (3D): Esc goes back to the room; E, Enter or Space use it when it
  // can also be used (PC 7: log in), or go back
  const inspecting = game.querySelector(".inspect3d");
  if (inspecting && key === "Escape") return click(inspecting.querySelector(".inspect-back"));
  if (inspecting && ["e", "E", "Enter", " "].includes(key)) return click(inspecting.querySelector(".inspect-act") || inspecting.querySelector(".inspect-back"));
  // A lock or the laptop's screen (3D) takes the keys while it is open; Esc closes it
  const device = game.querySelector(".lock3d, .laptop3d");
  if (device) {
    if (key === "Escape") return click(device.querySelector(".device-close, .laptop-leave"));
    return;
  }
  const bubble = game.querySelector(".bubble");
  if (bubble) {
    if (key === "Escape") return click(bubble.querySelector(".leave"));
    if (numbered(bubble)) return;
    if (key === "ArrowUp" || key === "ArrowDown") {
      const buttons = [...bubble.querySelectorAll("button")];
      const at = buttons.indexOf(bubble.getRootNode().activeElement);
      const next = buttons[(at + (key === "ArrowDown" ? 1 : buttons.length - 1)) % buttons.length] || buttons[0];
      handled();
      next?.focus();
      return;
    }
    if (key === "Enter" && bubble.contains(bubble.getRootNode().activeElement)) return;
  }
  // In a 3D room the arrows and WASD walk in every direction
  if (keys.move3d?.(key)) return handled();
  if (event.repeat && !["ArrowLeft", "ArrowRight", "a", "A", "d", "D"].includes(key)) return;
  switch (key) {
    case "ArrowLeft":
    case "a":
    case "A":
      handled();
      return keys.startWalking(-1, key);
    case "ArrowRight":
    case "d":
    case "D":
      handled();
      return keys.startWalking(1, key);
    case "e":
    case "E":
    case "Enter":
    case "ArrowUp":
    case "w":
    case "W":
    case " ":
      handled();
      return keys.useNearest();
    case "n":
    case "N":
      handled();
      return openNotebook(game, data.notebook, "items");
    case "h":
    case "H":
      if (!data.countdown?.can_hint) return;
      handled();
      return game.querySelector(".hint-button")?.click();
    case "t":
    case "T":
      handled();
      return toggleText(game);
    case "f":
    case "F":
      handled();
      return toggleFullscreen();
    case "m":
    case "M":
      handled();
      return toggleMute(game.querySelector(".sound-button"));
    // Nothing open any more: the Esc after that leaves full screen
    case "Escape":
      if (!document.fullscreenElement) return;
      handled();
      return leaveFullscreen();
    case "r":
    case "R":
      if (!data.can_restart) return;
      handled();
      return askRestart(game, data, setTriggerValue);
  }
}

// --- Restart the level: asked first, then Python starts the same level again ----------------

function askRestart(game, data, setTriggerValue) {
  Sound.click();
  game.querySelector(".confirm")?.remove();
  const overlay = el("div", "confirm");
  const panel = el("div", "confirm-panel");
  const yes = el("button", "big primary yes", data.ui.yes);
  const no = el("button", "big no", data.ui.no);
  yes.onclick = () => {
    Sound.click();
    overlay.remove();
    setTriggerValue("command", { name: "restart_level" });
  };
  no.onclick = () => {
    Sound.click();
    overlay.remove();
  };
  const buttons = el("div", "confirm-buttons");
  buttons.append(yes, no);
  panel.append(el("p", "", data.ui.restart_confirm), buttons);
  overlay.append(panel);
  overlay.onclick = (event) => event.target === overlay && overlay.remove();
  game.append(overlay);
  yes.focus();
}

// --- A conversation: shown over the picture as it was, one line at a time, spoken ---------

function dialogueOverlay(dialogue, data) {
  if (dialogue.phone) return phoneOverlay(dialogue, data);
  const overlay = el("div", "dialogue");
  overlay.onclick = (event) => event.stopPropagation();
  if (dialogue.background) overlay.innerHTML = `<img class="bg" src="${dialogue.background}" alt="">`;
  else overlay.classList.add("over-room");
  const box = el("div", "dialogue-box");
  const who = el("div", "dialogue-who");
  const text = el("p", "dialogue-text");
  const next = el("button", "choice dialogue-next", data.ui.dialogue_continue);
  box.append(who, text, next);
  overlay.append(box);
  let index = -1;
  function nextLine() {
    index += 1;
    if (index >= dialogue.lines.length) {
      stopSpeaking();
      overlay.classList.add("closing");
      setTimeout(() => overlay.remove(), 400);
      return;
    }
    const line = dialogue.lines[index];
    who.textContent = line.who;
    box.dataset.speaker = line.speaker === "you" ? "you" : "other";
    text.textContent = line.text;
    speak(line.text, line.speaker, data.voice_lang);
  }
  next.onclick = () => {
    Sound.click();
    nextLine();
  };
  // Starts once the browser has drawn it (voices need the page to be visible)
  setTimeout(nextLine, 250);
  return overlay;
}

// Text messages: your phone, held up, the messages arriving one by one
function phoneOverlay(dialogue, data) {
  const overlay = el("div", "dialogue over-room phone-chat");
  overlay.onclick = (event) => event.stopPropagation();
  const phone = el("div", "phone");
  const head = el("div", "phone-head");
  const other = dialogue.lines.find((line) => line.speaker !== "you");
  head.append(el("span", "phone-avatar", (other?.who || "?").slice(0, 1)), el("span", "phone-title", other?.who || dialogue.phone));
  const list = el("div", "phone-messages");
  const next = el("button", "choice dialogue-next", data.ui.dialogue_continue);
  phone.append(head, list);
  overlay.append(phone, next);
  let index = -1;
  const close = () => {
    overlay.classList.add("closing");
    setTimeout(() => overlay.remove(), 400);
  };
  function nextLine() {
    index += 1;
    if (index >= dialogue.lines.length) return close();
    // The answers arrive by themselves, a moment later ("typing…"): no key to press
    // (specs/level1-laptop-and-notes.md); the button then closes the phone
    if (index + 1 < dialogue.lines.length) setTimeout(() => overlay.isConnected && index < dialogue.lines.length - 1 && nextLine(), 1300);
    const line = dialogue.lines[index];
    const mine = line.speaker === "you";
    const bubble = el("div", mine ? "phone-bubble mine" : "phone-bubble");
    bubble.textContent = line.text.replace(/^“|”$/g, "");
    if (!mine) {
      // "…" first, as if they were typing
      const typing = el("div", "phone-bubble typing", "• • •");
      list.append(typing);
      setTimeout(() => typing.replaceWith(bubble), 700);
    } else {
      list.append(bubble);
    }
    Sound.click();
  }
  next.onclick = () => (index >= dialogue.lines.length - 1 ? close() : nextLine());
  setTimeout(nextLine, 250);
  return overlay;
}

// --- Top bar: title, inventory, decisions, menu ------------------------------------------

function topBar(data, setTriggerValue) {
  const bar = el("div", "topbar");
  const titles = el("div", "titles");
  titles.append(el("div", "title", data.hud.title), el("div", "subtitle", data.hud.subtitle));
  const items = el("div", "items");
  for (const item of data.hud.inventory) {
    const chip = el("button", "chip", item.icon);
    chip.title = item.name;
    chip.setAttribute("aria-label", item.name);
    chip.onclick = () => openNotebook(bar.closest(".game"), data.notebook, "items");
    items.append(chip);
  }
  // What you decided before: one line each (the whole sentence on hover), never spilling out of the bar
  // (only the latest: all of them are in the notebook)
  for (const decision of data.hud.decisions.slice(-1)) {
    const chip = el("span", "chip decision", decision);
    chip.title = decision;
    items.append(chip);
  }
  const menu = el("button", "menu-button", data.hud.menu_label);
  menu.onclick = () => {
    Sound.click();
    setTriggerValue("command", { name: "menu" });
  };
  const book = el("button", "menu-button notebook-button", `🎒 ${data.notebook.title}`);
  const count = data.notebook.items.length + data.notebook.conversations.length;
  if (count) book.append(el("span", "badge", String(count)));
  book.onclick = () => openNotebook(bar.closest(".game"), data.notebook, "items");
  const buttons = el("div", "bar-buttons");
  buttons.append(menu, book);
  if (data.can_restart) {
    const restart = el("button", "menu-button", data.ui.restart_level);
    restart.title = `${data.ui.restart_level} (R)`;
    restart.onclick = () => askRestart(bar.closest(".game"), data, setTriggerValue);
    buttons.append(restart);
  }
  const clock = el("div", data.countdown ? "clock countdown" : "clock", data.countdown ? "🕐 --:--:--" : "⏱ 00:00");
  clock.setAttribute("aria-live", "off");
  const textButton = el("button", "menu-button icon", "💬");
  textButton.title = data.ui.toggle_text;
  textButton.setAttribute("aria-label", data.ui.toggle_text);
  textButton.onclick = () => {
    Sound.click();
    toggleText(bar.closest(".game"));
  };
  const full = el("button", "menu-button icon", "⛶");
  full.title = data.ui.toggle_fullscreen;
  full.setAttribute("aria-label", data.ui.toggle_fullscreen);
  full.onclick = () => {
    Sound.click();
    toggleFullscreen();
  };
  // 🔊 / 🔇 Sound on or off at any moment of a level (music and effects; key M)
  const sound = el("button", "menu-button icon sound-button", loadSettings().muted ? "🔇" : "🔊");
  sound.title = `${data.ui.toggle_sound} (M)`;
  sound.setAttribute("aria-label", data.ui.toggle_sound);
  sound.setAttribute("aria-pressed", String(!loadSettings().muted));
  sound.onclick = () => toggleMute(sound);
  const tools = el("div", "bar-tools");
  tools.append(clock);
  // 💡 A hint (it costs a minute on the clock): only the one who acts
  if (data.countdown?.can_hint) {
    const hint = el("button", "menu-button hint-button", data.countdown.hint_label);
    hint.title = `${data.countdown.hint_label} (H)`;
    hint.onclick = () => {
      Sound.click();
      setTriggerValue("command", { name: "hint" });
    };
    tools.append(hint);
  }
  tools.append(textButton);
  // A place with a 3D room and a 2D picture: switch between them (kept in this browser)
  if (data.world && data.background) {
    const view = el("button", "menu-button icon view-button", loadSettings().view3d ? "2D" : "3D");
    view.title = data.ui.toggle_view;
    view.setAttribute("aria-label", data.ui.toggle_view);
    view.onclick = () => {
      Sound.click();
      const settings = loadSettings();
      settings.view3d = !settings.view3d;
      saveSettings(settings);
      globalThis.__forbiddenArchiveRedraw?.();
    };
    tools.append(view);
  }
  tools.append(sound, full);
  bar.append(buttons, titles, items, tools);
  return bar;
}

// --- The notebook: items with their text, conversations, decisions, from any scene --------

function openNotebook(game, book, tab) {
  Sound.click();
  game.querySelector(".notebook")?.remove();
  const L = book.labels;
  const overlay = el("div", "notebook");
  const panel = el("div", "notebook-panel");
  const head = el("div", "notebook-head");
  head.append(el("h2", "", `🎒 ${book.title}`));
  const close = el("button", "menu-button", "✕");
  close.setAttribute("aria-label", L.close);
  close.onclick = () => overlay.remove();
  head.append(close);
  const tabs = el("div", "notebook-tabs");
  const body = el("div", "notebook-body");
  const pages = {
    items: [L.nb_items, () => {
      if (!book.items.length) return [el("p", "nb-empty", L.nb_empty)];
      // Each item as the real thing, with its name on a label under it
      const shelf = el("div", "nb-things");
      for (const item of book.items) {
        const holder = el("div", "nb-thing");
        holder.append(realThing(item.face), el("div", "nb-thing-name", `${item.icon} ${item.name}`));
        shelf.append(holder);
      }
      return [shelf];
    }],
    conversations: [L.nb_conversations, () => {
      if (!book.conversations.length) return [el("p", "nb-empty", L.nb_empty)];
      return book.conversations.map((talk) => {
        const block = el("div", "nb-talk");
        block.append(el("h3", "", talk.title));
        for (const line of talk.lines) {
          const row = el("p", line.mine ? "nb-line mine" : "nb-line");
          row.append(el("strong", "", `${line.who}: `), document.createTextNode(line.text));
          block.append(row);
        }
        return block;
      });
    }],
    decisions: [L.nb_decisions, () => {
      if (!book.decisions.length) return [el("p", "nb-empty", L.nb_empty)];
      return book.decisions.map((label) => el("p", "nb-decision", `✔ ${label}`));
    }],
  };
  function show(name) {
    for (const b of tabs.children) b.classList.toggle("on", b.dataset.tab === name);
    body.replaceChildren(...pages[name][1]());
  }
  for (const [name, [label]] of Object.entries(pages)) {
    const b = el("button", "nb-tab", label);
    b.dataset.tab = name;
    b.onclick = () => {
      Sound.click();
      show(name);
    };
    tabs.append(b);
  }
  panel.append(head, tabs, body);
  overlay.append(panel);
  overlay.onclick = (event) => {
    if (event.target === overlay) overlay.remove();
  };
  game.append(overlay);
  show(tab);
}

// --- Narration under the picture: scene text, result of the last action, clues ------------

function narration(data) {
  const box = el("div", "narration");
  const room3d = wants3D(data);
  // In 3D a hint is the character thinking (a thought bubble), not a line here
  if (data.message && !(room3d && data.message.hint)) box.append(el("p", data.message.ok ? "message ok" : "message refused", data.message.text));
  if (data.narration) box.append(el("p", "scene-text", data.narration));
  if (data.hint) box.append(el("p", "hint", data.hint));
  // Until the player has used the keyboard once, a reminder of the keys (computers only)
  if (!loadSettings().usedKeys && globalThis.matchMedia?.("(hover: hover)").matches) box.append(el("p", "key-hint", wants3D(data) ? data.ui.key_hint_3d : data.ui.key_hint));
  // In 3D the contact zooms the security camera in on the things and reads them there
  if (data.clues && !room3d) {
    const clues = el("div", "clues");
    clues.append(el("div", "clues-title", data.clues.title));
    if (!data.clues.items.length) clues.append(el("p", "clue empty", data.clues.empty));
    for (const clue of data.clues.items) {
      const line = el("p", "clue");
      line.append(el("strong", "", clue.label + " — "), document.createTextNode(clue.text));
      clues.append(line);
    }
    box.append(clues);
  }
  return box;
}

// --- The email that opens a level (Level 2) -----------------------------------------------------

function introEmail(intro, setTriggerValue) {
  const cover = el("div", "intro-email");
  const mail = el("div", "intro-mail");
  const head = el("div", "intro-head");
  head.append(el("div", "intro-from", `${intro.icon || "📧"} ${intro.sender}`), el("div", "intro-subject", intro.subject));
  const body = el("div", "intro-body");
  body.append(el("div", "intro-big", intro.big));
  intro.lines.forEach((line, i) => body.append(el("p", i === intro.warn ? "intro-line intro-warn" : "intro-line", line)));
  const goal = el("div", "intro-goal", `🎯 ${intro.goal}`);
  const start = el("button", "intro-start", intro.button);
  start.onclick = () => {
    Sound.click();
    // Read again (your laptop, later): the button only closes it, nothing is sent
    if (intro.again) return cover.remove();
    start.disabled = true;
    setTriggerValue("action", { id: intro.action, x: 0, code: null });
  };
  // Co-op: only the one who acts closes it; the other student reads it until then
  if (!intro.action && !intro.again) start.hidden = true;
  // Read again: Esc closes it too (gameKeys compares the button with this)
  if (intro.again) cover.dataset.close = intro.button;
  mail.append(head, body, goal, start);
  cover.append(mail);
  setTimeout(() => start.focus(), 50);
  return cover;
}

// --- Ending card over the picture ----------------------------------------------------------

function endingCard(data, setTriggerValue) {
  const ending = data.ending;
  const card = el("div", "ending");
  const inner = el("div", "ending-inner");
  // A won level: congratulations first, big, then how it ended
  if (ending.congrats) {
    card.classList.add("won");
    const cheer = el("div", "ending-congrats");
    cheer.append(el("div", "congrats-title", ending.congrats.title));
    if (ending.congrats.text) cheer.append(el("p", "congrats-text", ending.congrats.text));
    inner.append(cheer);
  }
  inner.append(el("div", "ending-kicker", ending.kicker), el("h2", "ending-title", ending.title));
  // A text message at the end (Tiago, Rita) arrives on the phone
  const [told, texted] = ending.text.split("📱");
  if (texted) {
    if (told.trim()) inner.append(el("p", "ending-text", told.trim()));
    // "Rita, 01:04: “…”": the sender (with the time) ends where the quoted message starts, so the
    // colons of a time do not cut the message
    const quote = texted.indexOf("“");
    const who = (quote > 0 ? texted.slice(0, quote) : texted.split(":")[0]).trim().replace(/:$/, "");
    const said = quote > 0 ? texted.slice(quote) : texted.split(":").slice(1).join(":");
    const phone = el("div", "phone small");
    const head = el("div", "phone-head");
    head.append(el("span", "phone-avatar", who.slice(0, 1)), el("span", "phone-title", who));
    const list = el("div", "phone-messages");
    list.append(el("div", "phone-bubble", said.trim().replace(/^“|”$/g, "")));
    phone.append(head, list);
    inner.append(phone);
  } else {
    inner.append(el("p", "ending-text", ending.text));
  }
  if (ending.journey.length) inner.append(el("p", "ending-journey", ending.journey.join(" · ")));
  if (ending.clock) inner.append(el("p", "ending-clock", ending.clock));
  const run = Timer.current();
  if (run && !ending.clock) {
    const best = Timer.best(data.timer.level);
    const time = el("p", "ending-time", `⏱ ${data.ui.your_time}: ${formatTime(run.ms)}`);
    if (best) time.append(el("span", "", ` · 🏆 ${data.ui.best_time}: ${formatTime(best)}`));
    inner.append(time);
  }
  const buttons = el("div", "ending-buttons");
  for (const command of ending.buttons) {
    const b = el("button", command.primary ? "big primary" : "big", command.label);
    b.onclick = () => {
      Sound.click();
      if (command.name === "next_chapter" || command.name === "new_room_game") goFullscreen();
      setTriggerValue("command", { name: command.name });
    };
    buttons.append(b);
  }
  inner.append(buttons);
  card.append(inner);
  return card;
}

// --- Chat panel (co-op) --------------------------------------------------------------------

function chatPanel(chat, setTriggerValue) {
  const panel = el("div", "chat");
  const head = el("button", "chat-head", chat.title);
  head.onclick = () => panel.classList.toggle("closed");
  const list = el("div", "chat-list");
  const form = el("form", "chat-form");
  const input = el("input", "chat-input");
  input.placeholder = chat.placeholder;
  input.maxLength = 200;
  const send = el("button", "chat-send", "➤");
  send.type = "submit";
  form.append(input, send);
  form.onsubmit = (event) => {
    event.preventDefault();
    if (!input.value.trim()) return;
    setTriggerValue("chat", input.value);
    input.value = "";
  };
  panel.append(head, list, form);
  fillChat(list, chat);
  return panel;
}

function fillChat(list, chat) {
  list.replaceChildren();
  if (!chat.messages.length) list.append(el("p", "chat-empty", chat.empty));
  for (const message of chat.messages) {
    const line = el("p", `chat-line ${message.mine ? "mine" : ""}`);
    // Plain text only: chat comes from players
    line.append(el("span", "chat-who", `${message.avatar} ${message.who}`), el("span", "chat-text", message.text));
    list.append(line);
  }
  list.scrollTop = list.scrollHeight;
}

function updateChat(game, chat) {
  const list = game.querySelector(".chat-list");
  if (list && chat) fillChat(list, chat);
}

// --- The picture: background, character, spots, bubbles -----------------------------------

function buildPicture(stage, data, setTriggerValue) {
  const { background, character, walk, x: startX, spots, looks } = data;
  // A place drawn only in 3D, shown in 2D (the browser cannot draw 3D): a plain background, labels shown
  stage.innerHTML = background ? `<img class="bg" src="${background}" alt="">` : `<div class="bg no-art"></div>`;
  if (!background) stage.classList.add("no-art");

  let x = startX;
  let busy = false;
  let hero = null;
  const clamp = (px) => (walk ? Math.min(walk.max, Math.max(walk.min, px)) : px);
  const place = (px) => (hero.style.left = pct(px - (CHAR_W / 2) * walk.scale, WIDTH));

  if (character && walk) {
    hero = el("div", "hero");
    hero.innerHTML = character;
    hero.style.width = pct(CHAR_W * walk.scale, WIDTH);
    hero.style.height = pct(CHAR_H * walk.scale, HEIGHT);
    hero.style.top = pct(walk.floor - CHAR_TOP * walk.scale, HEIGHT);
    place(x);
  }

  function walkTo(target, done) {
    if (!hero) return done && done(); // the contact watches: nobody walks
    if (busy) return;
    target = clamp(target);
    busy = true;
    const ms = Math.max(150, (Math.abs(target - x) / SPEED) * 1000);
    if (target !== x) hero.classList.toggle("left", target < x);
    hero.style.transitionDuration = `${ms}ms`;
    hero.classList.add("walking");
    place(target);
    const steps = setInterval(Sound.step, 180);
    setTimeout(() => {
      clearInterval(steps);
      x = target;
      hero.classList.remove("walking");
      busy = false;
      markNearest();
      if (done) done();
    }, ms);
  }

  // Keyboard walking: held arrows move the character a little every frame
  let walking = null;
  function startWalking(direction, key) {
    if (!hero || (busy && !walking)) return;
    rememberKeys();
    if (walking) {
      walking.direction = direction;
      walking.key = key;
      hero.classList.toggle("left", direction < 0);
      return;
    }
    closeBubble();
    busy = true;
    hero.style.transitionDuration = "0ms";
    hero.classList.add("walking");
    hero.classList.toggle("left", direction < 0);
    walking = { direction, key, last: performance.now(), steps: setInterval(Sound.step, 180) };
    const frame = (now) => {
      if (!walking) return;
      const dt = Math.min(0.05, (now - walking.last) / 1000);
      walking.last = now;
      x = clamp(x + walking.direction * SPEED * dt);
      place(x);
      markNearest();
      walking.frame = requestAnimationFrame(frame);
    };
    walking.frame = requestAnimationFrame(frame);
  }

  function stopWalking(key) {
    if (!walking || (key !== "blur" && key.toLowerCase() !== walking.key.toLowerCase())) return;
    cancelAnimationFrame(walking.frame);
    clearInterval(walking.steps);
    walking = null;
    hero.classList.remove("walking");
    busy = false;
  }

  // The spot nearest to the character (within reach) is marked; E uses it
  const NEAR = 90;
  function nearestSpot() {
    if (!hero) return null;
    let best = null;
    for (const b of stage.querySelectorAll(".spot")) {
      const distance = Math.abs(Number(b.dataset.stand) - x);
      if (distance <= NEAR && (!best || distance < best.distance)) best = { b, distance };
    }
    return best?.b || null;
  }
  function markNearest() {
    const near = nearestSpot();
    for (const b of stage.querySelectorAll(".spot.near")) if (b !== near) b.classList.remove("near");
    near?.classList.add("near");
  }
  function useNearest() {
    rememberKeys();
    const near = nearestSpot();
    if (near && !busy) near.click();
  }

  // The character says something: a small bubble over the head, and the voice
  function heroSays(text) {
    if (!hero || !text) return;
    hero.querySelector(".say")?.remove();
    const bubble = el("div", "say", text);
    hero.append(bubble);
    speak(text, "you", data.voice_lang);
    setTimeout(() => bubble.remove(), Math.min(9000, 2500 + text.length * 60));
  }

  const { closeBubble, openBubble, openTalk, openKeypad } = interactions(stage, data, setTriggerValue, {
    heroSays,
    walkTo: hero ? walkTo : null,
  });

  function addSpot(spot, className, onArrive) {
    const b = el("button", className);
    // Labels near the right edge open to the left so they are not cut off
    if (spot.x + spot.w / 2 > WIDTH * 0.75) b.classList.add("label-end");
    b.style.left = pct(spot.x, WIDTH);
    b.style.top = pct(spot.y, HEIGHT);
    b.style.width = pct(spot.w, WIDTH);
    b.style.height = pct(spot.h, HEIGHT);
    b.setAttribute("aria-label", spot.label);
    b.dataset.stand = String(spot.stand);
    b.append(el("span", "label", spot.label));
    b.onclick = (event) => {
      event.stopPropagation();
      b.blur();
      Sound.click();
      closeBubble();
      walkTo(spot.stand, onArrive);
    };
    stage.append(b);
  }

  // Co-op: the agent's picture is dark where the clues are (Python decides where, specs/design-polish.md)
  const FEATHER = 12; // picture units: the patch is a little bigger than the clue and fades out there
  for (const shadow of data.shadows || []) {
    const patch = el("div", "clue-shadow");
    patch.style.left = pct(shadow.x - FEATHER, WIDTH);
    patch.style.top = pct(shadow.y - FEATHER, HEIGHT);
    patch.style.width = pct(shadow.w + 2 * FEATHER, WIDTH);
    patch.style.height = pct(shadow.h + 2 * FEATHER, HEIGHT);
    stage.append(patch);
  }

  // Looks first, so action spots are on top if they ever touch
  for (const look of looks) addSpot(look, "spot look", () => openBubble(look.text, [], data.ui.close));
  for (const spot of spots) {
    addSpot(spot, spot.edge ? `spot edge-${spot.edge}` : "spot", () => {
      if (spot.talk) openTalk(spot);
      else if (spot.code_prompt) openKeypad(spot);
      else setTriggerValue("action", { id: spot.action, x: spot.stand });
    });
  }

  stage.onclick = (event) => {
    closeBubble();
    const box = stage.getBoundingClientRect();
    walkTo(((event.clientX - box.left) / box.width) * WIDTH);
  };

  if (data.danger) startDanger();

  // A danger scene: the choices open at once and a clock runs; at zero the timeout action is sent
  function startDanger() {
    const { seconds, timeout } = data.danger;
    const spot = spots.find((s) => s.talk);
    const clock = el("div", "danger-clock");
    const bar = el("div", "danger-bar");
    const label = el("span", "danger-label", `⏱ ${data.ui.danger_hurry} ${seconds}`);
    clock.append(bar, label);
    stage.append(clock);
    let left = seconds;
    let done = false;
    const stop = () => {
      done = true;
      clearInterval(timer);
    };
    stage.addEventListener("choice-sent", stop);
    requestAnimationFrame(() => {
      bar.style.transitionDuration = `${seconds}s`;
      bar.classList.add("running");
    });
    const timer = setInterval(() => {
      if (done) return;
      left -= 1;
      label.textContent = `⏱ ${data.ui.danger_hurry} ${Math.max(left, 0)}`;
      Sound.tick();
      if (left <= 0) {
        stop();
        closeBubble();
        // Co-op: only Player 1's browser sends it, so it is sent once
        if (data.sends_timeout !== false) setTriggerValue("action", { id: timeout, x });
      }
    }, 1000);
    if (spot) setTimeout(() => !done && openTalk(spot), 600);
  }

  if (hero) {
    stage.append(hero);
    // A refused choice: the character says why and walks back from where it went
    if (data.walk_back_from !== null && data.walk_back_from !== undefined && walk) {
      x = clamp(data.walk_back_from);
      place(x);
      setTimeout(() => walkTo(startX), 900);
    }
    if (data.speech) setTimeout(() => heroSays(data.speech), 200);
    markNearest();
  }
  return { startWalking, stopWalking, useNearest };
}

// --- Bubbles: a look's text, a talk's choices, a keypad. Shared by the 2D picture and the 3D room ---
// hooks.heroSays(text) makes the character say something; hooks.walkTo(x, done) walks in the 2D
// picture (null in 3D: there a place to go is sent to Python straight away).

function interactions(stage, data, setTriggerValue, hooks) {
  const closeBubble = () => stage.querySelector(".bubble")?.remove();

  // A bubble with a text and buttons; clicks inside it never make the character walk
  function openBubble(text, buttons, leaveText) {
    closeBubble();
    const bubble = el("div", "bubble");
    bubble.onclick = (event) => event.stopPropagation();
    bubble.append(el("p", "line", text), ...buttons);
    const leave = el("button", "choice leave", leaveText);
    leave.onclick = closeBubble;
    bubble.append(leave);
    // Choices can be picked with 1-9 on a keyboard (the number shows next to each)
    bubble.querySelectorAll(":scope > button.choice:not(.leave)").forEach((b, i) => (b.dataset.key = String(i + 1)));
    stage.append(bubble);
    return bubble;
  }

  function choice(text, onClick) {
    const b = el("button", "choice", text);
    b.onclick = (event) => {
      Sound.click();
      if (onClick) onClick(event);
    };
    return b;
  }

  function openTalk(spot) {
    const options = spot.options.map((option) =>
      choice(option.say, () => {
        closeBubble();
        stage.dispatchEvent(new Event("choice-sent"));
        if (option.x === undefined || !hooks.walkTo) {
          setTriggerValue("action", { id: option.action, x: spot.stand });
          return;
        }
        // A place to go (a tunnel, a box): say it, walk there, then Python decides
        hooks.heroSays(option.say);
        hooks.walkTo(option.x, () =>
          setTimeout(() => setTriggerValue("action", { id: option.action, x: spot.stand, from: option.x }), 350)
        );
      })
    );
    openBubble(spot.line, options, data.ui.talk_leave);
    // A person answers aloud; objects (a shelf, a fork in the tunnel) are read by the hero
    speak(spot.line, spot.speaker || "you", data.voice_lang);
  }

  function openKeypad(spot) {
    // Rita's padlock and the terrace door's keypad are drawn as themselves
    const send = (code) => setTriggerValue("action", { id: spot.action, x: spot.stand, code });
    if (spot.lock === "padlock") return openPadlock(stage, spot, data, send);
    if (spot.lock === "keypad") return openDoorKeypad(stage, spot, data, send);
    const form = el("form", "keypad");
    const input = el("input");
    // Number locks open a numeric keyboard on phones; letter locks a normal one
    input.inputMode = spot.code_kind === "text" ? "text" : "numeric";
    input.autocomplete = "off";
    input.maxLength = 12;
    input.placeholder = spot.code_kind === "text" ? "······" : "····";
    const submit = choice(data.ui.keypad_try, null);
    submit.type = "submit";
    form.append(input, submit);
    form.onsubmit = (event) => {
      event.preventDefault();
      // Nothing typed: shake instead of sending (Python also refuses an empty code)
      if (!input.value.trim()) {
        input.classList.remove("shake");
        void input.offsetWidth;
        input.classList.add("shake");
        input.focus();
        return;
      }
      setTriggerValue("action", { id: spot.action, x: spot.stand, code: input.value });
    };
    openBubble(spot.code_prompt, [form], data.ui.cancel);
    // A login (PC 7) is a box in the middle of the screen, over the screen it unlocks
    if (spot.lock === "login") stage.querySelector(".bubble")?.classList.add("bubble-center");
    input.focus();
  }

  return { closeBubble, openBubble, choice, openTalk, openKeypad };
}

// --- The real things, over the room: the locks, the laptop's screen, the items ----------------
// Rita's padlock is a padlock with 5 wheels, the terrace door has its keypad, and at the laptop
// its screen fills the view (log in, the pen drive, the Wi-Fi, the terminal). Items appear as
// themselves: a student card with its number, a post-it in handwriting...

// One open device at a time; it takes the keyboard while it is open (Esc closes it)
function openDevice(stage, className, build) {
  stage.querySelector(".lock3d, .laptop3d")?.remove();
  const overlay = el("div", className);
  let onKey = null;
  const close = () => {
    overlay.remove();
    if (onKey) document.removeEventListener("keydown", onKey, true);
  };
  overlay.onclick = (event) => {
    event.stopPropagation();
    if (event.target === overlay) close();
  };
  const closeButton = el("button", "device-close", "✕");
  closeButton.onclick = (event) => {
    event.stopPropagation();
    Sound.click();
    close();
  };
  const keys = (handler) => {
    onKey = (event) => {
      if (!overlay.isConnected) return document.removeEventListener("keydown", onKey, true);
      const target = event.composedPath?.()[0] || event.target;
      if (target?.tagName === "INPUT") return; // typing in a field of the laptop
      handler(event);
    };
    document.addEventListener("keydown", onKey, true);
  };
  build({ overlay, close, keys });
  overlay.append(closeButton);
  stage.append(overlay);
  return close;
}

// Rita's padlock: five number wheels; turn them (click, arrows or digits), then pull it open
function openPadlock(stage, spot, data, send) {
  const digits = [0, 0, 0, 0, 0];
  let at = 0;
  openDevice(stage, "lock3d", ({ overlay, close, keys }) => {
    const lock = el("div", "padlock");
    const shackle = el("div", "padlock-shackle");
    const body = el("div", "padlock-body");
    const wheels = el("div", "padlock-wheels");
    const turn = (i, by) => {
      digits[i] = (digits[i] + by + 10) % 10;
      at = i;
      Sound.tick();
      draw();
    };
    function draw() {
      wheels.replaceChildren(
        ...digits.map((digit, i) => {
          const wheel = el("div", i === at ? "wheel on" : "wheel");
          const up = el("button", "wheel-turn", "▲");
          up.onclick = () => turn(i, 1);
          const down = el("button", "wheel-turn", "▼");
          down.onclick = () => turn(i, -1);
          const window_ = el("div", "wheel-window");
          window_.append(el("span", "wheel-side", String((digit + 9) % 10)), el("span", "wheel-digit", String(digit)), el("span", "wheel-side", String((digit + 1) % 10)));
          window_.onclick = () => {
            at = i;
            draw();
          };
          wheel.append(up, window_, down);
          return wheel;
        })
      );
    }
    const pull = el("button", "choice lock-open", `🔓 ${data.ui.lock_open}`);
    pull.onclick = () => {
      shackle.classList.add("pull");
      Sound.click();
      setTimeout(() => {
        close();
        send(digits.join(""));
      }, 380);
    };
    body.append(el("div", "padlock-engraving", spot.code_prompt), wheels);
    lock.append(shackle, body);
    overlay.append(lock, pull);
    draw();
    keys((event) => {
      const key = event.key;
      if (/^[0-9]$/.test(key)) {
        digits[at] = Number(key);
        at = Math.min(4, at + 1);
        Sound.tick();
        draw();
      } else if (key === "ArrowLeft" || key === "Backspace") {
        at = Math.max(0, at - 1);
        draw();
      } else if (key === "ArrowRight") {
        at = Math.min(4, at + 1);
        draw();
      } else if (key === "ArrowUp") turn(at, 1);
      else if (key === "ArrowDown") turn(at, -1);
      else if (key === "Enter") pull.click();
      else return;
      event.preventDefault();
      event.stopPropagation();
    });
  });
}

// The terrace door's keypad: a little screen, twelve keys and a light
function openDoorKeypad(stage, spot, data, send) {
  let typed = "";
  openDevice(stage, "lock3d", ({ overlay, close, keys }) => {
    const panel = el("div", "keypad-panel");
    const screen = el("div", "keypad-screen");
    const led = el("span", "keypad-led");
    const show = () => (screen.textContent = typed || "_ _ _");
    const submit = () => {
      if (!typed) {
        panel.classList.remove("shake");
        void panel.offsetWidth;
        panel.classList.add("shake");
        return;
      }
      led.classList.add("busy");
      setTimeout(() => {
        close();
        send(typed);
      }, 300);
    };
    const press = (key) => {
      Sound.tick();
      if (key === "⌫") typed = typed.slice(0, -1);
      else if (key === "✓") return submit();
      else if (typed.length < 8) typed += key;
      show();
    };
    const pad = el("div", "keypad-keys");
    for (const key of ["1", "2", "3", "4", "5", "6", "7", "8", "9", "⌫", "0", "✓"]) {
      const b = el("button", key === "✓" ? "keypad-key ok" : "keypad-key", key);
      b.onclick = () => press(key);
      pad.append(b);
    }
    const top = el("div", "keypad-top");
    top.append(el("span", "keypad-label", spot.code_prompt), led);
    panel.append(top, screen, pad);
    overlay.append(panel);
    show();
    keys((event) => {
      const key = event.key;
      if (/^[0-9.]$/.test(key)) press(key);
      else if (key === "Backspace") press("⌫");
      else if (key === "Enter") press("✓");
      else return;
      event.preventDefault();
      event.stopPropagation();
    });
  });
}

// Your laptop on the terrace: its screen fills the view. What it shows follows what is left to do
// (Python offers one step at a time): log in, then the pen drive, then the Wi-Fi, then the terminal.
function openLaptop(stage, data, setTriggerValue) {
  const L = data.ui;
  const state = data.world.laptop;
  const spots = data.spots;
  const login = spots.find((s) => s.lock === "login");
  const plug = spots.find((s) => s.action === "inserir_pen");
  const pen = spots.find((s) => s.talk === "pen");
  const wifi = spots.find((s) => s.lock === "wifi");
  const terminal = spots.find((s) => s.talk === "terminal");
  const leave = spots.find((s) => s.action === "sair_portatil");
  const act = (id, spot, code) => setTriggerValue("action", { id, x: spot.stand, code });
  const message = data.message && !data.message.hint ? data.message : null;

  openDevice(stage, "laptop3d", ({ overlay }) => {
    const machine = el("div", "laptop-machine");
    const lid = el("div", "laptop-lid");
    const screen = el("div", "laptop-screen");
    const bar = el("div", "laptop-bar");
    const clock = el("span", "laptop-time", "");
    const copyClock = () => (clock.textContent = (document.querySelector(".clock-text")?.textContent || "").replace("🕐", "").trim().slice(0, 5));
    copyClock();
    const timer = setInterval(() => (overlay.isConnected ? copyClock() : clearInterval(timer)), 1000);
    bar.append(el("span", "", "nova OS"), el("span", "laptop-icons", `${state.wifi ? "📶" : "⚠"}  🔌 4%`), clock);
    screen.append(bar);
    const desk = el("div", "laptop-desk");
    screen.append(desk);
    const windowBox = (title, cls = "") => {
      const w = el("div", `laptop-window ${cls}`);
      const head = el("div", "laptop-window-head");
      head.append(el("span", "dots", "● ● ●"), el("span", "", title));
      w.append(head);
      desk.append(w);
      return w;
    };
    const toast = (text, ok) => {
      const t = el("div", ok ? "laptop-toast ok" : "laptop-toast bad", `${ok ? "✅" : "❌"} ${text}`);
      screen.append(t);
    };

    if (login) {
      // The login screen, with Tiago's post-it stuck on it
      desk.classList.add("login");
      const form = el("form", "laptop-login");
      const input = el("input", "laptop-input");
      input.type = "password";
      input.placeholder = login.code_prompt;
      input.autocomplete = "off";
      const go = el("button", "laptop-button", L.lap_login);
      go.type = "submit";
      form.append(el("div", "laptop-avatar", "👤"), el("div", "laptop-user", L.lap_user), input, go);
      form.onsubmit = (event) => {
        event.preventDefault();
        if (input.value.trim()) act(login.action, login, input.value);
      };
      desk.append(form);
      const tiago = data.laptop_notes?.tiago;
      if (tiago) lid.append(realThing({ kind: "postit", text: tiago.postit, sign: tiago.sign }, "screen-note"));
      if (message && !message.ok) toast(message.text, false);
      setTimeout(() => input.focus(), 50);
    } else if (plug) {
      // Logged in: the desktop is empty until Rita's pen drive goes in the USB port
      const w = windowBox(`🔌 USB`, "small");
      w.append(el("p", "laptop-help", L.lap_plug_hint));
      const go = el("button", "laptop-button", `💾 ${plug.label}`);
      go.onclick = () => {
        Sound.click();
        act(plug.action, plug);
      };
      w.append(go);
      if (message) toast(message.text, message.ok);
    } else if (pen) {
      // The pen drive: four files; clicking one runs its tests
      const w = windowBox(`📁 ${L.lap_usb}`);
      w.append(el("p", "laptop-help", L.lap_open_hint));
      for (const option of pen.options) {
        const row = el("button", "laptop-file", `📄 ${option.say}`);
        row.onclick = () => {
          Sound.click();
          w.append(el("div", "laptop-running", `⏳ ${L.lap_tests}`));
          setTimeout(() => act(option.action, pen), 700);
        };
        w.append(row);
      }
      if (message) toast(message.text, message.ok);
    } else if (wifi) {
      // The Wi-Fi networks: only the terrace's has any signal
      const w = windowBox(`📶 ${L.lap_wifi}`, "small");
      const form = el("form", "laptop-wifi");
      const input = el("input", "laptop-input");
      input.type = "password";
      input.placeholder = wifi.code_prompt;
      input.autocomplete = "off";
      const go = el("button", "laptop-button", L.lap_connect);
      go.type = "submit";
      form.append(input, go);
      form.onsubmit = (event) => {
        event.preventDefault();
        if (input.value.trim()) act(wifi.action, wifi, input.value);
      };
      const esplanada = el("button", "laptop-network on", `📶 Esplanada  🔒 ${L.lap_secured}`);
      esplanada.onclick = () => input.focus();
      // Where the password is: a note on the Wi-Fi window
      w.append(esplanada, form, el("div", "laptop-wifi-hint", `🔎 ${L.lap_wifi_hint}`));
      for (const name of ["eduroam", "NOVA-Guest"]) w.append(el("div", "laptop-network off", `▫ ${name} — ${L.lap_no_signal}`));
      if (state.file) toast(message?.ok ? message.text : "trabalho_final_v3.py ✓", true);
      if (message && !message.ok) toast(message.text, false);
      setTimeout(() => input.focus(), 50);
    } else if (terminal) {
      // The terminal: type the commands from Rita's post-it, in order
      const w = windowBox("▮ Terminal — ~/trabalho", "terminal");
      const log = el("div", "terminal-log");
      const line = (text, cls = "") => log.append(el("div", `terminal-line ${cls}`, text));
      line(`# ${L.lap_type}`, "dim");
      const done = { _git_add: 'git add .', _git_commit: 'git commit -m "final"' };
      for (const step of state.git) line(`$ ${done[step]}`);
      if (message) line(message.text, message.ok ? "ok" : "bad");
      const form = el("form", "terminal-form");
      const input = el("input", "terminal-input");
      input.autocomplete = "off";
      input.spellcheck = false;
      form.append(el("span", "terminal-prompt", "$"), input);
      const tidy = (text) => text.trim().replace(/\s+/g, " ").replace(/[“”]/g, '"');
      const commandFor = (typed) => {
        const exact = terminal.options.find((o) => tidy(o.say) === typed);
        if (exact) return exact;
        const verb = typed.match(/^git (add|commit|push)\b/)?.[1];
        return verb ? terminal.options.find((o) => o.say.startsWith(`git ${verb}`)) : null;
      };
      form.onsubmit = (event) => {
        event.preventDefault();
        const typed = tidy(input.value);
        if (!typed) return;
        input.value = "";
        line(`$ ${typed}`);
        const option = commandFor(typed);
        if (option) setTimeout(() => act(option.action, terminal), 250);
        else line(`bash: ${typed.split(" ")[0]}: ${L.lap_not_found}`, "bad");
        log.scrollTop = log.scrollHeight;
      };
      w.append(log, form);
      w.onclick = () => input.focus();
      setTimeout(() => input.focus(), 50);
    }
    lid.append(screen);
    machine.append(lid, el("div", "laptop-base"));
    overlay.append(machine);
    // Stand up: back to the terrace, the laptop keeps charging (specs/laptop-way-back.md)
    if (leave) {
      const up = el("button", "choice laptop-leave", `⏏ ${leave.label}`);
      up.onclick = (event) => {
        event.stopPropagation();
        Sound.click();
        act(leave.action, leave);
      };
      overlay.append(up);
    }
    // Rita's post-it, next to the keyboard
    const rita = data.laptop_notes?.rita;
    if (rita) overlay.append(realThing(rita, "side-note"));
  });
}

// An item as the real thing (story.py ITEM_FACES), with its words on it
function realThing(face, extra = "") {
  const thing = el("div", `real ${face.kind} ${extra}`);
  if (face.kind === "card") {
    // In the style of the Nova SBE student card: red, a big white arc with the name and the number
    // on it, "Issued" in the corner. No photo, and the names and numbers are made up (story.py).
    const nova = el("span", "card-nova");
    nova.append("N", el("span", "card-o", "O"), "VΛ");
    const logo = el("div", "card-logo");
    logo.append(nova, el("span", "card-student", "Student"));
    const words = el("div", "card-words");
    words.append(el("div", "card-name", String(face.name || face._name).toUpperCase()), el("div", "card-number", face._number));
    const issued = el("div", "card-issued");
    issued.append(el("span", "", "Issued"), el("b", "", "2025/2030"));
    thing.append(
      el("div", "card-arc"),
      el("div", "card-dot"),
      logo,
      el("div", "card-school", "NOVA SCHOOL OF BUSINESS & ECONOMICS"),
      el("div", "card-note", face.note),
      words,
      issued
    );
  } else if (face.kind === "postit") {
    thing.append(el("p", "postit-text", face.text));
    for (const step of face._steps || []) thing.append(el("p", "postit-step", step));
    if (face.sign) thing.append(el("p", "postit-sign", face.sign));
  } else if (face.kind === "coat") {
    thing.append(el("div", "coat-hood"), el("div", "coat-body"));
    const tag = el("div", "coat-tag");
    tag.append(el("b", "", "−50%"), el("span", "", face.tag));
    thing.append(tag);
  } else if (face.kind === "usb") {
    const tape = el("div", "usb-tape", face._label);
    thing.append(el("div", "usb-plug"), tape, el("div", "usb-tag", face.tag));
  } else if (face.kind === "charger") {
    thing.append(el("div", "charger-brick", face._label), el("div", "charger-cable"), el("div", "charger-note", face.tag));
  } else if (face.kind === "notebook") {
    // Rita's notebook, open on its first draft
    thing.append(el("div", "notebook-title", `${face.title} — ${face._date}`));
    for (const line of face._code) thing.append(el("code", "notebook-code", line));
    thing.append(el("div", "notebook-sign", face.sign));
  } else if (face.kind === "print") {
    // The printed browser history from PC 7
    thing.append(el("div", "print-title", face.title));
    for (const line of face._lines) thing.append(el("code", "print-line", line));
  } else if (face.kind === "key") {
    thing.append(el("div", "key-ring"), el("div", "key-blade"), el("div", "key-tag", face.tag));
  } else if (face.kind === "fish") {
    // The fisherman's sardine (Level 3)
    thing.append(el("div", "fish-body", "🐟"), el("div", "fish-tag", face.tag));
  } else if (face.kind === "laptop_item") {
    thing.append(el("div", "laptop-lid", "🐈"), el("div", "laptop-base"), el("div", "laptop-tag", face.tag));
  }
  return thing;
}

// Something you just picked up: shown as itself for a moment, then into the backpack
function showPickedUp(game, items) {
  const overlay = el("div", "picked-up");
  for (const item of items) {
    const holder = el("div", "picked-item");
    holder.append(realThing(item.face), el("div", "picked-name", item.name));
    overlay.append(holder);
  }
  overlay.onclick = () => overlay.classList.add("leaving");
  game.append(overlay);
  setTimeout(() => overlay.classList.add("leaving"), 3200);
  setTimeout(() => overlay.remove(), 4000);
}

// --- The countdown (specs/entrega-2359.md): the real time, from 23:44 to 00:00 ------------------
// Python sends how many seconds are left (penalties included) and decides what happens at 00:00;
// the browser only shows the clock and, when it reaches 00:00, asks Python to end the game.

function startCountdown(game, data, setTriggerValue) {
  const { left, starts_at: startsAt, total, lost, time_up_action: timeUp, can_hint: canAct } = data.countdown;
  const label = game.querySelector(".clock");
  // The time is written in its own span, so the "−30 s" flash next to it stays
  const text = el("span", "clock-text");
  label.textContent = "";
  label.append(text);
  const deadline = performance.now() + left * 1000;
  const two = (n) => String(n).padStart(2, "0");
  let sent = false;
  const show = () => {
    if (!label.isConnected) return clearInterval(timer);
    const remaining = Math.max(0, (deadline - performance.now()) / 1000);
    const shown = Math.floor(startsAt + total - remaining) % 86400;
    text.textContent = `🕐 ${two(Math.floor(shown / 3600))}:${two(Math.floor(shown / 60) % 60)}:${two(shown % 60)}`;
    label.classList.toggle("late", remaining <= 180);
    label.classList.toggle("last", remaining <= 60);
    if (remaining <= 0 && !sent && canAct) {
      sent = true;
      setTriggerValue("action", { id: timeUp, x: 0 });
    }
  };
  const timer = setInterval(show, 250);
  show();
  // A wrong answer or a hint: the clock jumps, and says by how much
  if (lost > 0) {
    const flash = el("span", "time-lost", `−${lost >= 60 ? `${Math.round(lost / 60)} min` : `${lost} s`}`);
    label.append(flash);
    label.classList.add("jumped");
    setTimeout(() => label.classList.remove("jumped"), 900);
  }
}

function rememberKeys() {
  const settings = loadSettings();
  if (!settings.usedKeys) {
    settings.usedKeys = true;
    saveSettings(settings);
  }
}

// --- Main menu -------------------------------------------------------------------------------
// Moving between Play / How to Play / Settings happens here; starting, continuing, joining and
// changing language are commands for Python.

function menuScreen(data, setTriggerValue) {
  const menu = data.menu;
  const L = menu.labels;
  const root = el("div", "game menu-mode");
  root.dataset.sceneKey = data.scene_key;

  const backdrop = el("div", "menu-backdrop");
  backdrop.innerHTML = `<img class="menu-art" src="${menu.background}" alt="">`;
  for (let i = 0; i < 26; i++) {
    const dot = el("span", "spark");
    dot.style.left = `${(i * 37) % 100}%`;
    dot.style.animationDelay = `${(i * 0.7) % 9}s`;
    dot.style.animationDuration = `${7 + (i % 5)}s`;
    backdrop.append(dot);
  }
  root.append(backdrop);
  // The terrace of the library at night, in 3D, behind the menu (scene3d.js)
  menuRoom3D(backdrop, menu.world);

  const panel = el("div", "menu-panel");
  root.append(panel);

  const command = (name, extra = {}) => setTriggerValue("command", { name, ...extra });
  const startCommand = (name, extra) => {
    goFullscreen();
    command(name, extra);
  };

  function button(label, onClick, className = "menu-item") {
    const b = el("button", className, label);
    b.onclick = () => {
      Sound.click();
      onClick();
    };
    return b;
  }

  function heading(withTagline) {
    // The name: a git branch with two commits, then "Git Out"
    const title = el("h1", "game-name");
    title.innerHTML = `<svg class="logo-branch" viewBox="0 0 40 48" aria-hidden="true"><path d="M12 6v36M12 30c0-10 16-6 16-16" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round"/><circle cx="12" cy="42" r="5"/><circle cx="28" cy="12" r="5"/></svg>`;
    title.append(el("span", "", menu.title));
    panel.append(title);
    panel.append(el("p", "game-subtitle", menu.subtitle));
    if (withTagline) panel.append(el("p", "tagline", menu.tagline));
    if (menu.error) panel.append(el("p", "menu-error", menu.error));
  }

  function show(screen) {
    panel.replaceChildren();
    panel.dataset.screen = screen;
    root.dataset.screen = screen;
    // The student on the terrace: framed beside the menu, or close up while dressing them
    globalThis.__gitOutShowcase?.mode(screen === "look" ? "look" : "main");
    if (screen === "main") {
      heading(true);
      if (menu.can_continue) panel.append(button(L.continue, () => startCommand("continue"), "menu-item primary"));
      panel.append(
        button(L.play, () => show("map"), menu.can_continue ? "menu-item" : "menu-item primary"),
        button(L.your_student, () => show("look")),
        button(L.how_to_play, () => show("how")),
        button(L.settings, () => show("settings")),
        button(L.exit, () => {
          leaveFullscreen();
          show("goodbye");
        }),
      );
    } else if (screen === "look") {
      panel.append(el("h2", "menu-heading", L.your_student), el("p", "coop-text", L.your_student_text), lookEditor());
    } else if (screen === "map") {
      panel.append(el("h2", "menu-heading", L.map_title));
      if (menu.error) panel.append(el("p", "menu-error", menu.error));
      panel.append(levelMap());
      if (menu.can_continue) panel.append(button(L.continue, () => startCommand("continue"), "menu-item primary"));
      const extras = el("div", "map-extras");
      // Only two ways to play: alone (the map) or with a friend (a room); no account box
      extras.append(coopBox());
      panel.append(extras, button(L.back, () => show("main"), "menu-item ghost"));
    } else if (screen === "how") {
      heading(false);
      const list = el("ul", "rules");
      for (const rule of menu.rules) list.append(el("li", "", rule));
      panel.append(el("h2", "menu-heading", L.how_to_play), list, button(L.back, () => show("main"), "menu-item ghost"));
    } else if (screen === "settings") {
      heading(false);
      panel.append(el("h2", "menu-heading", L.settings), settingsForm(), button(L.back, () => show("main"), "menu-item ghost"));
    } else if (screen === "confirm") {
      heading(false);
      panel.append(
        el("p", "confirm-text", L.confirm_restart),
        button(L.yes_restart, () => startCommand("confirm_restart"), "menu-item primary"),
        button(L.cancel, () => command("cancel_restart"), "menu-item ghost"),
      );
    } else if (screen === "goodbye") {
      panel.append(el("h1", "game-name", L.goodbye_title), el("p", "tagline", L.goodbye_text), button(L.back_to_menu, () => show("main")));
    }
  }

  // An original map of Nova SBE by the sea at night: the study room (level 1), the building locked
  // for the night (level 2) and the auditorium at sunrise (level 3), joined by a path
  function levelMap() {
    const map = el("div", "level-map");
    map.innerHTML = `<svg class="map-art" viewBox="0 0 600 260" aria-hidden="true">
      <defs>
        <linearGradient id="mapSky" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stop-color="#0d1330"/><stop offset=".62" stop-color="#1b2550"/><stop offset="1" stop-color="#e98a5c"/></linearGradient>
        <linearGradient id="mapSea" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#1d3a6b"/><stop offset="1" stop-color="#0b1730"/></linearGradient>
      </defs>
      <rect width="600" height="260" rx="18" fill="url(#mapSky)"/>
      <g fill="#fff" opacity=".7"><circle cx="40" cy="30" r="1.2"/><circle cx="120" cy="18" r="1"/><circle cx="210" cy="40" r="1.3"/>
        <circle cx="300" cy="22" r="1"/><circle cx="360" cy="48" r="1.1"/></g>
      <circle cx="80" cy="44" r="13" fill="#fff6dc"/><circle cx="86" cy="40" r="12" fill="#0d1330"/>
      <circle cx="560" cy="150" r="22" fill="#ffc87a" opacity=".9"/>
      <path d="M0 196 H600 V260 H0Z" fill="url(#mapSea)"/>
      <path d="M0 202 Q60 196 120 202 T240 202 T360 202 T480 202 T600 202" fill="none" stroke="#8fb8ff" stroke-width="1.5" opacity=".35"/>
      <path d="M0 178 Q300 160 600 176 V198 H0Z" fill="#d9c49a" opacity=".85"/>
      <g fill="#eceae4">
        <rect x="40" y="112" width="120" height="58" rx="3"/><rect x="190" y="92" width="170" height="78" rx="3"/>
        <rect x="390" y="104" width="130" height="66" rx="3"/><path d="M390 104 Q455 76 520 104Z"/>
      </g>
      <g fill="#ffd27a" opacity=".85">
        <rect x="52" y="124" width="16" height="10"/><rect x="76" y="124" width="16" height="10"/><rect x="128" y="146" width="16" height="10"/>
        <rect x="204" y="106" width="14" height="10"/><rect x="226" y="128" width="14" height="10"/><rect x="306" y="106" width="14" height="10"/>
        <rect x="408" y="120" width="94" height="8" opacity=".6"/>
      </g>
      <g font-family="Helvetica, Arial, sans-serif" font-weight="bold" font-size="17" fill="#ffffff" stroke="#c8d0dc" stroke-width=".6">
        <text x="236" y="160">N</text><text x="254" y="160">O</text><text x="274" y="160">V</text><text x="292" y="160">A</text>
      </g>
      <path class="map-road" d="M100 178 C150 205 200 150 275 176 S 400 200 455 172" fill="none" stroke="#ffe8a3" stroke-width="5" stroke-dasharray="4 13" stroke-linecap="round"/>
      <path d="M455 172 C500 150 520 110 552 86" fill="none" stroke="#ffe8a3" stroke-width="4" stroke-dasharray="3 12" stroke-linecap="round" opacity=".45"/>
      <text x="40" y="96" fill="#ffe8a3" font-size="12" font-family="Georgia, serif" opacity=".8">23:59</text>
      <text x="252" y="80" fill="#ffe8a3" font-size="12" font-family="Georgia, serif" opacity=".8">00:01 – 00:30</text>
      <text x="470" y="90" fill="#fff0d0" font-size="12" font-family="Georgia, serif" opacity=".9">09:00</text>
    </svg>`;
    const positions = [
      [17, 62],
      [46, 54],
      [76, 58],
    ];
    // Narrow screens: the cards move to a row under the map, so they never run off it
    const list = el("div", "level-list");
    menu.levels.forEach((level, i) => {
      const [left, top] = positions[i] || [50, 50];
      const state = level.completed ? "done" : level.unlocked ? "open" : "locked";
      const node = el("button", `level-node ${state}`);
      node.style.left = `${left}%`;
      node.style.top = `${top}%`;
      node.disabled = !level.unlocked;
      node.append(el("span", "level-badge", level.completed ? "✓" : level.unlocked ? String(level.number) : "🔒"));
      const card = () => {
        const c = el("span", `level-card ${state}`);
        c.append(el("strong", "", level.name), el("span", "", level.title));
        c.append(el("small", "", level.unlocked ? level.progress : level.locked));
        const best = Timer.best(level.number);
        if (best) c.append(el("small", "level-best", `🏆 ${L.best_time}: ${formatTime(best)}`));
        return c;
      };
      node.append(card());
      list.append(card());
      node.setAttribute("aria-label", `${level.name} — ${level.title}${level.unlocked ? "" : " — " + level.locked}`);
      node.onclick = () => {
        Sound.click();
        startCommand("open_level", { level: level.number });
      };
      map.append(node);
    });
    // After the last level, like other games: a bubble saying more levels are on the way
    const more = el("div", "level-node more");
    more.style.left = "92%";
    more.style.top = "36%";
    more.append(el("span", "level-badge", "✨"));
    const soon = () => {
      const c = el("span", "level-card soon");
      c.append(el("strong", "", L.more_levels), el("small", "", L.more_levels_text));
      return c;
    };
    more.append(soon());
    list.append(soon());
    map.append(more);
    const wrap = el("div", "level-map-wrap");
    wrap.append(map, list);
    return wrap;
  }

  // Your student: every part with arrows (or colour dots); the student on the terrace changes at once
  // The look being dressed, not saved yet (Back forgets it)
  let draft = { ...menu.look };
  function lookEditor() {
    const look = draft;
    const box = el("div", "look-editor");
    const rows = el("div", "look-rows");
    const note = el("p", "look-note");
    const saveButton = button(L.look_save, () => command("save_look", { look }), "menu-item primary small");
    const isPrize = (choice) => !!menu.prizes[choice];
    const locked = (choice) => isPrize(choice) && !menu.prizes[choice].won;
    const refresh = () => {
      globalThis.__gitOutShowcase?.look(look);
      const prize = Object.values(look).find(locked);
      note.textContent = prize ? `🔒 ${menu.prizes[prize].how}` : "";
      saveButton.disabled = !!prize;
    };
    for (const [part, choices] of Object.entries(menu.parts)) {
      const row = el("div", "look-row");
      row.append(el("span", "look-part", L[`look_${part}`]));
      if (choices[0].startsWith("#")) {
        const dots = el("div", "look-dots");
        for (const colour of choices) {
          const dot = el("button", "look-dot");
          dot.style.background = colour;
          dot.setAttribute("aria-label", `${L[`look_${part}`]} ${colour}`);
          dot.classList.toggle("on", look[part] === colour);
          dot.onclick = () => {
            Sound.click();
            look[part] = colour;
            dots.querySelectorAll(".look-dot").forEach((d) => d.classList.toggle("on", d === dot));
            refresh();
          };
          dots.append(dot);
        }
        row.append(dots);
      } else {
        const name = el("span", "look-choice");
        const shown = () => {
          const choice = look[part];
          name.textContent = `${locked(choice) ? "🔒 " : isPrize(choice) ? "🏆 " : ""}${L[`look_${part}_${choice}`] || choice}`;
        };
        const step = (by) => {
          Sound.click();
          const i = choices.indexOf(look[part]);
          look[part] = choices[(i + by + choices.length) % choices.length];
          shown();
          refresh();
        };
        const prev = el("button", "look-arrow", "‹");
        const next = el("button", "look-arrow", "›");
        prev.setAttribute("aria-label", `${L[`look_${part}`]} −`);
        next.setAttribute("aria-label", `${L[`look_${part}`]} +`);
        prev.onclick = () => step(-1);
        next.onclick = () => step(1);
        const picker = el("div", "look-picker");
        picker.append(prev, name, next);
        row.append(picker);
        shown();
      }
      rows.append(row);
    }
    const random = button(L.look_random, () => {
      for (const [part, choices] of Object.entries(menu.parts)) {
        const allowed = choices.filter((c) => !locked(c));
        look[part] = allowed[Math.floor(Math.random() * allowed.length)];
      }
      box.replaceWith(lookEditor());
    }, "menu-item small");
    const actions = el("div", "look-actions");
    actions.append(random, saveButton);
    box.append(rows, note, actions);
    if (menu.look_saved) box.append(el("p", "look-saved", L.look_saved));
    box.append(button(L.back, () => {
      draft = { ...menu.look };
      globalThis.__gitOutShowcase?.look(menu.look);
      show("main");
    }, "menu-item ghost"));
    refresh();
    return box;
  }

  function coopBox() {
    const coop = el("div", "coop-box");
    coop.append(el("div", "coop-title", L.coop));
    coop.append(el("p", "coop-text", L.coop_text));
    coop.append(button(L.create_room, () => startCommand("create_room"), "menu-item small"));
    const form = el("form", "join-form");
    const input = el("input", "join-input");
    input.placeholder = L.room_code_placeholder;
    input.maxLength = 6;
    input.setAttribute("aria-label", L.room_code);
    const join = el("button", "menu-item small", L.join_room);
    join.type = "submit";
    form.append(input, join);
    form.onsubmit = (event) => {
      event.preventDefault();
      Sound.click();
      startCommand("join_room", { code: input.value });
    };
    coop.append(form);
    return coop;
  }

  function settingsForm() {
    const settings = loadSettings();
    const form = el("div", "settings");
    const save = () => {
      saveSettings(settings);
      Sound.applySettings();
    };
    const toggle = (label, key) => {
      const row = el("div", "setting");
      const b = el("button", `switch ${settings[key] ? "on" : ""}`, settings[key] ? L.on : L.off);
      b.setAttribute("aria-pressed", String(settings[key]));
      b.onclick = () => {
        settings[key] = !settings[key];
        b.className = `switch ${settings[key] ? "on" : ""}`;
        b.textContent = settings[key] ? L.on : L.off;
        b.setAttribute("aria-pressed", String(settings[key]));
        save();
        Sound.click();
        if (key === "fullscreen") (settings.fullscreen ? goFullscreen : leaveFullscreen)();
      };
      row.append(el("span", "setting-name", label), b);
      return row;
    };
    const volumeRow = el("div", "setting");
    const slider = el("input", "volume");
    slider.type = "range";
    slider.min = "0";
    slider.max = "1";
    slider.step = "0.05";
    slider.value = String(settings.volume);
    slider.setAttribute("aria-label", L.volume);
    slider.oninput = () => {
      settings.volume = Number(slider.value);
      save();
    };
    slider.onchange = () => Sound.click();
    volumeRow.append(el("span", "setting-name", L.volume), slider);

    const languageRow = el("div", "setting");
    const languages = el("div", "languages");
    for (const [code, name] of [["en", "English"], ["pt", "Português"]]) {
      const b = el("button", `switch ${menu.language === code ? "on" : ""}`, name);
      b.onclick = () => {
        Sound.click();
        if (menu.language !== code) command("set_language", { lang: code });
      };
      languages.append(b);
    }
    languageRow.append(el("span", "setting-name", L.language), languages);

    form.append(toggle(L.music, "music"), volumeRow, toggle(L.effects, "sfx"), languageRow, toggle(L.fullscreen, "fullscreen"));
    return form;
  }

  show(menu.confirm ? "confirm" : menu.screen || "main");
  return root;
}
