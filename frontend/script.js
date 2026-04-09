// ─────────────────────────────────────────
//  UNMUTE.AI — script.js
//  Word Builder + Text-to-Speech
// ─────────────────────────────────────────

const WS_URL         = "ws://unmute-ai-production.up.railway.app/ws";
const SEND_INTERVAL  = 100;    // ms — 10 fps to backend
const HOLD_DURATION  = 1500;   // ms — hold gesture this long to commit
const RECONNECT_MS   = 3000;
const MAX_TOKENS     = 50;

// ── DOM ──────────────────────────────────
const video           = document.getElementById("video");
const canvas          = document.getElementById("canvas");
const ctx             = canvas.getContext("2d");
const statusPill      = document.getElementById("statusPill");
const statusText      = document.getElementById("statusText");
const gestureDisplay  = document.getElementById("gestureDisplay");
const gestureSub      = document.getElementById("gestureSub");
const fpsBadge        = document.getElementById("fpsBadge");
const confFill        = document.getElementById("confFill");
const confValue       = document.getElementById("confValue");
const holdRingFill    = document.getElementById("holdRingFill");
const holdPercent     = document.getElementById("holdPercent");
const noHandOverlay   = document.getElementById("noHandOverlay");
const sentenceDisplay = document.getElementById("sentenceDisplay");
const tokenTrack      = document.getElementById("tokenTrack");
const wordCount       = document.getElementById("wordCount");
const charCount       = document.getElementById("charCount");
const sessionGestures = document.getElementById("sessionGestures");
const latencyVal      = document.getElementById("latencyVal");
const ttsToggle       = document.getElementById("ttsToggle");
const ttsRate         = document.getElementById("ttsRate");
const ttsPitch        = document.getElementById("ttsPitch");
const ttsRateVal      = document.getElementById("ttsRateVal");
const ttsPitchVal     = document.getElementById("ttsPitchVal");
const btnSpeak        = document.getElementById("btnSpeak");
const btnSpace        = document.getElementById("btnSpace");
const btnBackspace    = document.getElementById("btnBackspace");
const btnClear        = document.getElementById("btnClear");

// ── State ─────────────────────────────────
let socket          = null;
let isProcessing    = false;
let sendInterval    = null;
let canvasReady     = false;
let sentAt          = 0;

// Word builder
let tokens          = [];
let totalGestures   = 0;

// Hold-to-commit
let holdGesture     = null;
let holdStart       = null;
let holdCommitted   = false;
const RING_CIRCUMFERENCE = 2 * Math.PI * 26;

// Init ring
holdRingFill.style.strokeDasharray  = RING_CIRCUMFERENCE;
holdRingFill.style.strokeDashoffset = RING_CIRCUMFERENCE;

// ── WebSocket ─────────────────────────────
function connectWebSocket() {
  setStatus("connecting");
  socket = new WebSocket(WS_URL);

  socket.onopen = () => {
    setStatus("connected");
    startSending();
  };

  socket.onmessage = (event) => {
    const latency = Date.now() - sentAt;
    isProcessing  = false;
    const data    = JSON.parse(event.data);
    updateUI(data, latency);
  };

  socket.onerror  = () => setStatus("error");

  socket.onclose  = () => {
    setStatus("disconnected");
    stopSending();
    setTimeout(connectWebSocket, RECONNECT_MS);
  };
}

// ── Camera ────────────────────────────────
function startCamera() {
   video.style.transform = "scaleX(-1)";
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
      video.srcObject = stream;
      video.onloadedmetadata = () => {
        canvas.width  = video.videoWidth;
        canvas.height = video.videoHeight;
        canvasReady   = true;
      };
    })
    .catch(err => {
      console.error("Camera error:", err);
      setStatus("error");
    });
}

// ── Frame Sending ─────────────────────────
function startSending() {
  stopSending();
  sendInterval = setInterval(() => {
    if (isProcessing)  return;
    if (!canvasReady)  return;
    if (!socket || socket.readyState !== WebSocket.OPEN) return;
    if (video.readyState < 2) return;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(blob => {
      if (!blob) return;
      const reader     = new FileReader();
      reader.onloadend = () => {
        isProcessing = true;
        sentAt       = Date.now();
        socket.send(reader.result.split(",")[1]);
      };
      reader.readAsDataURL(blob);
    }, "image/jpeg", 0.7);
  }, SEND_INTERVAL);
}

function stopSending() {
  if (sendInterval) { clearInterval(sendInterval); sendInterval = null; }
}

// ── UI Update ─────────────────────────────
function updateUI(data, latency) {
  const { gesture, confidence, fps, low_conf } = data;
  const noHand = gesture === "No Hand" || gesture === "Error";

  // No-hand overlay
  noHandOverlay.classList.toggle("visible", noHand);

  // Gesture display
  gestureDisplay.textContent = noHand ? "--" : gesture;
  gestureDisplay.className   = "gesture-display" +
    (noHand ? " no-hand" : low_conf ? " low-conf" : "");
  gestureSub.textContent     = noHand ? "Waiting..." : getGestureName(gesture);

  // Confidence
  const conf = noHand ? 0 : confidence;
  confValue.textContent = `${conf}%`;
  confFill.style.width  = `${conf}%`;
  confFill.className    = "conf-fill" + getConfClass(conf, low_conf, noHand);

  // FPS + Latency
  fpsBadge.textContent   = noHand ? "-- fps" : `${fps} fps`;
  latencyVal.textContent = `${latency} ms`;

  // Hold-to-commit
  if (!noHand && !low_conf) {
    processHold(gesture);
  } else {
    resetHold();
  }

  // Session counter
  totalGestures++;
  sessionGestures.textContent = totalGestures;
}

// ── Hold-to-Commit ────────────────────────
function processHold(gesture) {
  const now = Date.now();

  if (gesture !== holdGesture) {
    holdGesture   = gesture;
    holdStart     = now;
    holdCommitted = false;
  }

  const elapsed  = now - holdStart;
  const progress = Math.min(elapsed / HOLD_DURATION, 1);
  updateHoldRing(progress);

  if (progress >= 1 && !holdCommitted) {
    holdCommitted = true;
    commitGesture(gesture);
  }
}

function resetHold() {
  holdGesture   = null;
  holdStart     = null;
  holdCommitted = false;
  updateHoldRing(0);
}

function updateHoldRing(progress) {
  holdRingFill.style.strokeDashoffset = RING_CIRCUMFERENCE * (1 - progress);
  holdPercent.textContent = `${Math.round(progress * 100)}%`;
  holdRingFill.style.stroke =
    progress >= 1   ? "#22c55e" :
    progress > 0.5  ? "#f59e0b" : "#7c5cbf";
}

// ── Commit Gesture ────────────────────────
function commitGesture(gesture) {
  if (tokens.length >= MAX_TOKENS) return;
  tokens.push(gesture);
  renderBuilder();
  if (ttsToggle.checked) speak(gesture);
  setTimeout(() => updateHoldRing(0), 600);
}

// ── Word Builder Render ───────────────────
function renderBuilder() {
  // Sentence
  if (tokens.length === 0) {
    sentenceDisplay.innerHTML =
      `<span class="sentence-placeholder">Your sentence will appear here...</span>`;
  } else {
    sentenceDisplay.textContent = tokens.join(" ");
  }

  // Token chips — use event delegation, NOT inline onclick
  tokenTrack.innerHTML = tokens
    .map((t, i) => `
      <span class="token-chip" data-index="${i}" title="Click to remove">
        ${t} <span class="token-chip__x">×</span>
      </span>`)
    .join("");

  // Stats
  wordCount.textContent = tokens.length;
  charCount.textContent = tokens.join(" ").length;
}

// Event delegation for token removal — works reliably
tokenTrack.addEventListener("click", (e) => {
  const chip = e.target.closest(".token-chip");
  if (!chip) return;
  const index = parseInt(chip.dataset.index, 10);
  if (!isNaN(index)) {
    tokens.splice(index, 1);
    renderBuilder();
  }
});

// ── Button Actions ────────────────────────
btnSpeak.addEventListener("click", () => {
  if (tokens.length === 0) return;
  speak(tokens.join(" "));
});

btnSpace.addEventListener("click", () => {
  tokens.push("_");   // visible space token
  renderBuilder();
});

btnBackspace.addEventListener("click", () => {
  if (tokens.length === 0) return;
  tokens.pop();
  renderBuilder();
});

btnClear.addEventListener("click", () => {
  tokens = [];
  renderBuilder();
  resetHold();
});

// ── Text-to-Speech ────────────────────────
function speak(text) {
  if (!("speechSynthesis" in window)) return;
  if (!ttsToggle.checked) return;
  // Replace underscore space tokens with real spaces
  const cleaned = text.replace(/_/g, " ").trim();
  if (!cleaned) return;
  window.speechSynthesis.cancel();
  const utt   = new SpeechSynthesisUtterance(cleaned);
  utt.rate    = parseFloat(ttsRate.value);
  utt.pitch   = parseFloat(ttsPitch.value);
  utt.lang    = "en-US";
  window.speechSynthesis.speak(utt);
}

ttsRate.addEventListener("input", () => {
  ttsRateVal.textContent = `${parseFloat(ttsRate.value).toFixed(1)}×`;
});
ttsPitch.addEventListener("input", () => {
  ttsPitchVal.textContent = parseFloat(ttsPitch.value).toFixed(1);
});

// ── Helpers ───────────────────────────────
function getGestureName(gesture) {
  if (/^[A-Z]$/.test(gesture)) return `Letter ${gesture}`;
  if (/^[0-9]$/.test(gesture)) return `Number ${gesture}`;
  const words = { "CONGRATULATIONS": "Word: Congratulations" };
  return words[gesture] || `Gesture: ${gesture}`;
}

function getConfClass(conf, low_conf, noHand) {
  if (noHand || conf === 0) return "";
  if (low_conf || conf < 50) return " low";
  if (conf >= 75)            return " high";
  return                            " mid";
}

function setStatus(state) {
  statusPill.className = `status-pill status-pill--${state}`;
  const labels = {
    connecting:   "Connecting",
    connected:    "Connected",
    disconnected: "Disconnected",
    error:        "Error",
  };
  statusText.textContent = labels[state] || state;
}

// ── Init ──────────────────────────────────
startCamera();
connectWebSocket();
renderBuilder();
