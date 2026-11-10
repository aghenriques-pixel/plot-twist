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

export default function ({ data, parentElement, setTriggerValue }) {
  const existing = parentElement.querySelector(".game");
  if (existing && existing.dataset.sceneKey === data.scene_key) {
    updateChat(existing, data.chat);
    return;
  }
  existing?.remove();

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
}

// --- Top bar: title, inventory, decisions, menu ------------------------------------------

function topBar(data, setTriggerValue) {
  const bar = el("div", "topbar");
  const titles = el("div", "titles");
  titles.append(el("div", "title", data.hud.title), el("div", "subtitle", data.hud.subtitle));
  const items = el("div", "items");
  for (const item of data.hud.inventory) {
    const chip = el("span", "chip", item.icon);
    chip.title = item.name;
    chip.setAttribute("aria-label", item.name);
    items.append(chip);
  }
  for (const decision of data.hud.decisions) items.append(el("span", "chip decision", decision));
  const menu = el("button", "menu-button", data.hud.menu_label);
  menu.onclick = () => setTriggerValue("command", { name: "menu" });
  bar.append(titles, items, menu);
  return bar;
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
    b.onclick = () => setTriggerValue("command", { name: command.name });
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
    setTimeout(() => {
      x = target;
      hero.classList.remove("walking");
      busy = false;
      if (done) done();
    }, ms);
  }

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
    stage.append(bubble);
    return bubble;
  }

  function choice(text, onClick) {
    const b = el("button", "choice", text);
    b.onclick = onClick;
    return b;
  }

  function openTalk(spot) {
    const options = spot.options.map((option) =>
      choice(option.say, () => setTriggerValue("action", { id: option.action, x: spot.stand }))
    );
    openBubble(spot.line, options, "Step away");
  }

  function openKeypad(spot) {
    const form = el("form", "keypad");
    const input = el("input");
    // Number locks open a numeric keyboard on phones; letter locks a normal one
    input.inputMode = spot.code_kind === "text" ? "text" : "numeric";
    input.autocomplete = "off";
    input.maxLength = 12;
    input.placeholder = spot.code_kind === "text" ? "······" : "····";
    const submit = choice("Try", null);
    submit.type = "submit";
    form.append(input, submit);
    form.onsubmit = (event) => {
      event.preventDefault();
      setTriggerValue("action", { id: spot.action, x: spot.stand, code: input.value });
    };
    openBubble(spot.code_prompt, [form], "Cancel");
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
      closeBubble();
      walkTo(spot.stand, onArrive);
    };
    stage.append(b);
  }

  // Looks first, so action spots are on top if they ever touch
  for (const look of looks) addSpot(look, "spot look", () => openBubble(look.text, [], "Close"));
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

  if (hero) stage.append(hero);
}
