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
const DEFAULT_SETTINGS = { music: true, volume: 0.5, sfx: true, fullscreen: true, voices: true };

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
};

function speak(text, speaker, lang, onEnd) {
  const synth = globalThis.speechSynthesis;
  if (!text || !synth || !loadSettings().voices) return onEnd && setTimeout(onEnd, 0);
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
    document.documentElement.requestFullscreen().catch(() => {});
  }
}

function leaveFullscreen() {
  if (document.fullscreenElement && document.exitFullscreen) document.exitFullscreen().catch(() => {});
}

// --- Sound: one engine for the whole page, kept across redraws ----------------------------

const Sound = (globalThis.__forbiddenArchiveSound ??= createSound());

function createSound() {
  let ctx = null;
  let master = null;
  let musicBus = null;
  let mood = null;
  let voices = [];
  let chordTimer = null;
  const MOODS = {
    // Chords as frequencies (Hz); the menu is warmer, the game darker, the ending brighter
    menu: [[220, 277.2, 329.6], [196, 246.9, 293.7], [174.6, 220, 261.6], [196, 246.9, 329.6]],
    game: [[110, 130.8, 164.8], [98, 123.5, 146.8], [103.8, 130.8, 155.6], [110, 138.6, 164.8]],
    ending: [[261.6, 329.6, 392], [293.7, 349.2, 440], [329.6, 392, 493.9], [261.6, 329.6, 523.3]],
  };

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
      filter.frequency.value = 900;
      musicBus.connect(filter).connect(master);
    }
    if (ctx.state === "suspended") ctx.resume();
    applySettings();
    if (mood) startMusic(mood, true);
    return true;
  }

  function applySettings() {
    if (!ctx) return;
    const settings = loadSettings();
    master.gain.setTargetAtTime(settings.volume, ctx.currentTime, 0.1);
    musicBus.gain.setTargetAtTime(settings.music ? 0.22 : 0, ctx.currentTime, 0.3);
  }

  function playChord(chord) {
    const now = ctx.currentTime;
    for (const voice of voices) {
      voice.gain.gain.setTargetAtTime(0, now, 0.8);
      voice.osc.stop(now + 4);
    }
    voices = chord.map((freq, i) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = i === 0 ? "triangle" : "sine";
      osc.frequency.value = freq;
      osc.detune.value = (i - 1) * 6;
      gain.gain.value = 0;
      gain.gain.setTargetAtTime(i === 0 ? 0.5 : 0.3, now, 1.2);
      osc.connect(gain).connect(musicBus);
      osc.start();
      return { osc, gain };
    });
  }

  function startMusic(name, force) {
    mood = name;
    if (!ctx || ctx.state !== "running") return;
    if (chordTimer && !force && startMusic.current === name) return;
    startMusic.current = name;
    clearInterval(chordTimer);
    let step = 0;
    const chords = MOODS[name];
    playChord(chords[0]);
    chordTimer = setInterval(() => playChord(chords[++step % chords.length]), 7000);
  }

  function tone(freq, duration, type = "sine", volume = 0.25, delay = 0) {
    if (!ctx || ctx.state !== "running" || !loadSettings().sfx) return;
    const start = ctx.currentTime + delay;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = type;
    osc.frequency.value = freq;
    gain.gain.setValueAtTime(volume, start);
    gain.gain.exponentialRampToValueAtTime(0.001, start + duration);
    osc.connect(gain).connect(master);
    osc.start(start);
    osc.stop(start + duration + 0.05);
  }

  function noise(duration, volume = 0.18, frequency = 500) {
    if (!ctx || ctx.state !== "running" || !loadSettings().sfx) return;
    const buffer = ctx.createBuffer(1, Math.floor(ctx.sampleRate * duration), ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < data.length; i++) data[i] = (Math.random() * 2 - 1) * (1 - i / data.length);
    const source = ctx.createBufferSource();
    const filter = ctx.createBiquadFilter();
    const gain = ctx.createGain();
    source.buffer = buffer;
    filter.type = "bandpass";
    filter.frequency.value = frequency;
    gain.gain.value = volume;
    source.connect(filter).connect(gain).connect(master);
    source.start();
  }

  // Browsers only allow sound after a click: the first click anywhere turns it on
  document.addEventListener("pointerdown", unlock, { capture: true });
  document.addEventListener("keydown", unlock, { capture: true });

  return {
    unlock,
    applySettings,
    music: (name) => startMusic(name, false),
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

export default function ({ data, parentElement, setTriggerValue }) {
  const existing = parentElement.querySelector(".game");
  if (existing && existing.dataset.sceneKey === data.scene_key) {
    updateChat(existing, data.chat);
    return;
  }
  existing?.remove();
  stopSpeaking();

  if (data.mode === "menu") {
    Sound.music("menu");
    parentElement.appendChild(menuScreen(data, setTriggerValue));
    return;
  }

  Sound.music(data.ending ? "ending" : "game");
  if (data.ending) Sound.ending();
  else if (data.message) (data.message.ok ? Sound.success : Sound.refused)();

  const game = el("div", "game");
  game.dataset.sceneKey = data.scene_key;
  game.append(topBar(data, setTriggerValue));
  const stageWrap = el("div", "stage-wrap");
  const stage = el("div", "stage");
  stageWrap.append(stage);
  // Narration and (in co-op) the chat share the row under the picture
  const bottom = el("div", "bottom");
  bottom.append(narration(data));
  if (data.chat) bottom.append(chatPanel(data.chat, setTriggerValue));
  game.append(stageWrap, bottom);
  parentElement.appendChild(game);

  buildPicture(stage, data, setTriggerValue);
  if (data.ending) stage.append(endingCard(data.ending, setTriggerValue));
  if (data.dialogue) {
    const overlay = dialogueOverlay(data.dialogue, data);
    // The hero stays where it stood while they talk
    const hero = stage.querySelector(".hero")?.cloneNode(true);
    if (hero) overlay.insertBefore(hero, overlay.querySelector(".dialogue-box"));
    stage.append(overlay);
  }
}

// --- A conversation: shown over the picture as it was, one line at a time, spoken ---------

function dialogueOverlay(dialogue, data) {
  const overlay = el("div", "dialogue");
  overlay.onclick = (event) => event.stopPropagation();
  overlay.innerHTML = `<img class="bg" src="${dialogue.background}" alt="">`;
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
  for (const decision of data.hud.decisions) items.append(el("span", "chip decision", decision));
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
  bar.append(buttons, titles, items);
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
      return book.items.map((item) => {
        const card = el("div", "nb-item");
        card.append(el("div", "nb-icon", item.icon));
        const words = el("div", "");
        words.append(el("strong", "", item.name), el("p", "", item.text));
        card.append(words);
        return card;
      });
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
  if (data.message) box.append(el("p", data.message.ok ? "message ok" : "message refused", data.message.text));
  if (data.narration) box.append(el("p", "scene-text", data.narration));
  if (data.hint) box.append(el("p", "hint", data.hint));
  if (data.clues) {
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

// --- Ending card over the picture ----------------------------------------------------------

function endingCard(ending, setTriggerValue) {
  const card = el("div", "ending");
  const inner = el("div", "ending-inner");
  inner.append(el("div", "ending-kicker", ending.kicker), el("h2", "ending-title", ending.title));
  inner.append(el("p", "ending-text", ending.text));
  if (ending.journey.length) inner.append(el("p", "ending-journey", ending.journey.join(" · ")));
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
  stage.innerHTML = `<img class="bg" src="${background}" alt="">`;

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
      if (done) done();
    }, ms);
  }

  const closeBubble = () => stage.querySelector(".bubble")?.remove();

  // The character says something: a small bubble over the head, and the voice
  function heroSays(text) {
    if (!hero || !text) return;
    hero.querySelector(".say")?.remove();
    const bubble = el("div", "say", text);
    hero.append(bubble);
    speak(text, "you", data.voice_lang);
    setTimeout(() => bubble.remove(), Math.min(9000, 2500 + text.length * 60));
  }

  // A bubble with a text and buttons; clicks inside it never make the character walk
  function openBubble(text, buttons, leaveText) {
    closeBubble();
    const bubble = el("div", "bubble");
    bubble.onclick = (event) => event.stopPropagation();
    bubble.append(el("p", "line", text), ...buttons);
    const leave = el("button", "choice leave", leaveText);
    leave.onclick = closeBubble;
    bubble.append(leave);
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
        if (option.x === undefined || !hero) {
          setTriggerValue("action", { id: option.action, x: spot.stand });
          return;
        }
        // A place to go (a tunnel, a box): say it, walk there, then Python decides
        heroSays(option.say);
        walkTo(option.x, () =>
          setTimeout(() => setTriggerValue("action", { id: option.action, x: spot.stand, from: option.x }), 350)
        );
      })
    );
    openBubble(spot.line, options, data.ui.talk_leave);
    // A person answers aloud; objects (a shelf, a fork in the tunnel) are read by the hero
    speak(spot.line, spot.speaker || "you", data.voice_lang);
  }

  function openKeypad(spot) {
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
      setTriggerValue("action", { id: spot.action, x: spot.stand, code: input.value });
    };
    openBubble(spot.code_prompt, [form], data.ui.cancel);
    input.focus();
  }

  function addSpot(spot, className, onArrive) {
    const b = el("button", className);
    // Labels near the right edge open to the left so they are not cut off
    if (spot.x + spot.w / 2 > WIDTH * 0.75) b.classList.add("label-end");
    b.style.left = pct(spot.x, WIDTH);
    b.style.top = pct(spot.y, HEIGHT);
    b.style.width = pct(spot.w, WIDTH);
    b.style.height = pct(spot.h, HEIGHT);
    b.setAttribute("aria-label", spot.label);
    b.append(el("span", "label", spot.label));
    b.onclick = (event) => {
      event.stopPropagation();
      Sound.click();
      closeBubble();
      walkTo(spot.stand, onArrive);
    };
    stage.append(b);
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
        setTriggerValue("action", { id: timeout, x });
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
    const title = el("h1", "game-name", menu.title);
    panel.append(title);
    if (withTagline) panel.append(el("p", "tagline", menu.tagline));
    if (menu.error) panel.append(el("p", "menu-error", menu.error));
  }

  function show(screen) {
    panel.replaceChildren();
    panel.dataset.screen = screen;
    if (screen === "main") {
      heading(true);
      panel.append(
        button(L.play, () => show("map"), "menu-item primary"),
        button(L.how_to_play, () => show("how")),
        button(L.settings, () => show("settings")),
        button(L.exit, () => {
          leaveFullscreen();
          show("goodbye");
        }),
      );
    } else if (screen === "map") {
      panel.append(el("h2", "menu-heading", L.map_title));
      if (menu.error) panel.append(el("p", "menu-error", menu.error));
      panel.append(levelMap());
      if (menu.can_continue) panel.append(button(L.continue, () => startCommand("continue"), "menu-item primary"));
      const extras = el("div", "map-extras");
      extras.append(coopBox(), accountBox());
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

  // An original map of the city: a road from the Ministry (level 1) to the radio tower (level 2)
  function levelMap() {
    const map = el("div", "level-map");
    map.innerHTML = `<svg class="map-art" viewBox="0 0 600 260" aria-hidden="true">
      <defs><linearGradient id="mapSky" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#2b1d5c"/><stop offset="1" stop-color="#16324f"/></linearGradient></defs>
      <rect width="600" height="260" rx="18" fill="url(#mapSky)"/>
      <path d="M0 200 Q150 170 300 205 T600 190 V260 H0Z" fill="#1d4d4f" opacity=".8"/>
      <path d="M30 150 L60 150 L60 110 L100 110 L100 150 L130 150" fill="none" stroke="#f7c873" stroke-width="3" opacity=".5"/>
      <g fill="#3b2f6e"><rect x="40" y="120" width="40" height="70"/><rect x="95" y="100" width="30" height="90"/>
        <rect x="250" y="120" width="30" height="70"/></g>
      <g fill="#f7c873" opacity=".7"><rect x="48" y="130" width="6" height="8"/><rect x="66" y="150" width="6" height="8"/>
        <rect x="103" y="115" width="6" height="8"/><rect x="258" y="135" width="6" height="8"/></g>
      <path d="M300 170 L320 50 L340 170" fill="none" stroke="#e86a92" stroke-width="4"/>
      <circle cx="320" cy="45" r="7" fill="#ff8fab" class="map-beacon"/>
      <path d="M470 150 L530 40 L590 150 Z" fill="#4a3f7a"/><path d="M500 95 L560 95" stroke="#8fb8ff" stroke-width="3"/>
      <rect x="520" y="118" width="20" height="32" fill="#2b1d5c"/>
      <path class="map-road" d="M84 205 C160 150 220 215 288 170 S 430 95 510 120" fill="none" stroke="#ffe8a3" stroke-width="6" stroke-dasharray="4 14" stroke-linecap="round"/>
      <text x="170" y="40" text-anchor="middle" fill="#ffe8a3" font-size="15" font-family="Georgia, serif" opacity=".85">✶ ✶ ✶</text>
    </svg>`;
    const positions = [
      [14, 79],
      [48, 65],
      [85, 46],
    ];
    menu.levels.forEach((level, i) => {
      const [left, top] = positions[i] || [50, 50];
      const state = level.completed ? "done" : level.unlocked ? "open" : "locked";
      const node = el("button", `level-node ${state}`);
      node.style.left = `${left}%`;
      node.style.top = `${top}%`;
      node.disabled = !level.unlocked;
      node.append(el("span", "level-badge", level.completed ? "✓" : level.unlocked ? String(level.number) : "🔒"));
      const card = el("span", "level-card");
      card.append(el("strong", "", level.name), el("span", "", level.title));
      card.append(el("small", "", level.unlocked ? level.progress : L.level_locked));
      node.append(card);
      node.setAttribute("aria-label", `${level.name} — ${level.title}${level.unlocked ? "" : " — " + L.level_locked}`);
      node.onclick = () => {
        Sound.click();
        startCommand("open_level", { level: level.number });
      };
      map.append(node);
    });
    return map;
  }

  function coopBox() {
    const coop = el("div", "coop-box");
    coop.append(el("div", "coop-title", L.coop));
    if (!menu.online) {
      coop.append(el("p", "coop-text", L.coop_offline));
      return coop;
    }
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

  function accountBox() {
    const box = el("div", "coop-box");
    box.append(el("div", "coop-title", L.account));
    if (!menu.online) {
      box.append(el("p", "coop-text", L.account_offline));
      return box;
    }
    if (menu.account) {
      box.append(el("p", "coop-text", menu.account), button(L.log_out, () => command("log_out"), "menu-item small"));
      return box;
    }
    box.append(el("p", "coop-text", L.account_hint));
    const form = el("form", "account-form");
    const name = el("input", "join-input");
    name.placeholder = L.username;
    name.maxLength = 20;
    name.autocomplete = "username";
    name.setAttribute("aria-label", L.username);
    const pass = el("input", "join-input");
    pass.type = "password";
    pass.placeholder = L.password;
    pass.maxLength = 128;
    pass.autocomplete = "current-password";
    pass.setAttribute("aria-label", L.password);
    const send = (name_) => {
      Sound.click();
      command(name_, { username: name.value, password: pass.value });
      pass.value = "";
    };
    const create = el("button", "menu-item small", L.create_account);
    create.type = "button";
    create.onclick = () => send("create_account");
    const login = el("button", "menu-item small", L.log_in);
    login.type = "submit";
    form.onsubmit = (event) => {
      event.preventDefault();
      send("log_in");
    };
    form.append(name, pass, el("div", "account-buttons"));
    form.lastChild.append(login, create);
    box.append(form);
    return box;
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
        if (key === "voices" && settings.voices) speak(L.voices, "you", menu.language === "pt" ? "pt-PT" : "en-GB");
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

    form.append(toggle(L.music, "music"), volumeRow, toggle(L.effects, "sfx"), toggle(L.voices, "voices"), languageRow, toggle(L.fullscreen, "fullscreen"));
    return form;
  }

  show(menu.confirm ? "confirm" : menu.screen || "main");
  return root;
}
