// Clickable scene: background picture, the character, and clickable spots.
// Clicking the floor makes the character walk there. Clicking a spot makes the
// character walk to it and then sends {id, x} to Python as the "action" trigger.
// A talk spot (a character or object) opens a bubble with options; each option sends its action.
// A spot with a code_prompt opens a keypad and sends {id, x, code}. A look only shows a text.
// Python decides whether the action is allowed (logic.apply_action), exactly like a button.

const WIDTH = 800; // picture coordinates, same as the SVG viewBox
const HEIGHT = 400;
const SPEED = 260; // picture units per second
const CHAR_W = 84; // character.svg viewBox size
const CHAR_H = 180;
const CHAR_TOP = 172; // distance from the top of character.svg to the feet

const pct = (value, total) => `${(value / total) * 100}%`;

export default function ({ data, parentElement, setTriggerValue }) {
  parentElement.querySelector(".scene")?.remove();
  const { background, character, walk, x: startX, spots, looks } = data;

  const root = document.createElement("div");
  root.className = "scene";
  root.innerHTML = `<img class="bg" src="${background}" alt="">`;

  const hero = document.createElement("div");
  hero.className = "hero";
  hero.innerHTML = character;
  hero.style.width = pct(CHAR_W * walk.scale, WIDTH);
  hero.style.height = pct(CHAR_H * walk.scale, HEIGHT);
  hero.style.top = pct(walk.floor - CHAR_TOP * walk.scale, HEIGHT);

  let x = startX;
  let busy = false;
  let timer = null;
  const place = (px) => (hero.style.left = pct(px - (CHAR_W / 2) * walk.scale, WIDTH));
  const clamp = (px) => Math.min(walk.max, Math.max(walk.min, px));
  place(x);

  function walkTo(target, done) {
    if (busy) return;
    target = clamp(target);
    busy = true;
    const ms = Math.max(150, (Math.abs(target - x) / SPEED) * 1000);
    if (target !== x) hero.classList.toggle("left", target < x);
    hero.style.transitionDuration = `${ms}ms`;
    hero.classList.add("walking");
    place(target);
    timer = setTimeout(() => {
      x = target;
      hero.classList.remove("walking");
      busy = false;
      if (done) done();
    }, ms);
  }

  function closeBubble() {
    root.querySelector(".bubble")?.remove();
  }

  // A bubble with a text and buttons; clicks inside it never make the character walk
  function openBubble(text, buttons, leaveText) {
    closeBubble();
    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.onclick = (event) => event.stopPropagation();
    const line = document.createElement("p");
    line.className = "line";
    line.textContent = text;
    bubble.appendChild(line);
    for (const element of buttons) bubble.appendChild(element);
    const leave = document.createElement("button");
    leave.className = "choice leave";
    leave.textContent = leaveText;
    leave.onclick = closeBubble;
    bubble.appendChild(leave);
    root.appendChild(bubble);
    return bubble;
  }

  function button(text, onClick) {
    const element = document.createElement("button");
    element.className = "choice";
    element.textContent = text;
    element.onclick = onClick;
    return element;
  }

  function openTalk(spot) {
    const options = spot.options.map((option) =>
      button(option.say, () => setTriggerValue("action", { id: option.action, x: spot.stand }))
    );
    openBubble(spot.line, options, "Afastar-te");
  }

  function openKeypad(spot) {
    const form = document.createElement("form");
    form.className = "keypad";
    const input = document.createElement("input");
    input.inputMode = "numeric";
    input.autocomplete = "off";
    input.maxLength = 6;
    input.placeholder = "····";
    const submit = button("Tentar", null);
    submit.type = "submit";
    form.append(input, submit);
    form.onsubmit = (event) => {
      event.preventDefault();
      setTriggerValue("action", { id: spot.action, x: spot.stand, code: input.value });
    };
    openBubble(spot.code_prompt, [form], "Desistir");
    input.focus();
  }

  function addSpot(spot, className, onArrive) {
    const el = document.createElement("button");
    el.className = className;
    // Labels near the right edge open to the left so they are not cut off
    if (spot.x + spot.w / 2 > WIDTH * 0.75) el.classList.add("label-end");
    el.style.left = pct(spot.x, WIDTH);
    el.style.top = pct(spot.y, HEIGHT);
    el.style.width = pct(spot.w, WIDTH);
    el.style.height = pct(spot.h, HEIGHT);
    el.setAttribute("aria-label", spot.label);
    el.innerHTML = `<span class="label">${spot.label}</span>`;
    el.onclick = (event) => {
      event.stopPropagation();
      closeBubble();
      walkTo(spot.stand, onArrive);
    };
    root.appendChild(el);
  }

  // Looks first, so action spots are on top if they ever touch
  for (const look of looks) {
    addSpot(look, "spot look", () => openBubble(look.text, [], "Fechar"));
  }
  for (const spot of spots) {
    addSpot(spot, spot.edge ? `spot edge-${spot.edge}` : "spot", () => {
      if (spot.talk) openTalk(spot);
      else if (spot.code_prompt) openKeypad(spot);
      else setTriggerValue("action", { id: spot.action, x: spot.stand });
    });
  }

  root.onclick = (event) => {
    closeBubble();
    const box = root.getBoundingClientRect();
    walkTo(((event.clientX - box.left) / box.width) * WIDTH);
  };

  root.appendChild(hero);
  parentElement.appendChild(root);

  return () => {
    clearTimeout(timer);
    root.remove();
  };
}
