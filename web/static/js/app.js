/**
 * CodingDuo - Interactive Web Application Logic
 * Tactical 3D Design, Compiler Optimization Engine & Voice Narration
 */

// --- Global State ---
const state = {
  currentPass: "all_passes",
  currentTab: "editor", // "editor" or "photo"
  soundEnabled: true,
  isGenerating: false,
  isPlayingAudio: false,
  currentAudio: null,
  xp: 1420,
  streak: 5,
  gems: 750,
  selectedFile: null,
  activeSolutionText: "",
  presets: {},
};

// --- Web Audio Synthesizer (Tactile Sound Effects) ---
class CodingDuoAudio {
  constructor() {
    this.ctx = null;
  }

  init() {
    if (!this.ctx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioContext();
    }
  }

  playClick() {
    if (!state.soundEnabled) return;
    this.init();
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = "sine";
    osc.frequency.setValueAtTime(650, this.ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(320, this.ctx.currentTime + 0.05);
    gain.gain.setValueAtTime(0.15, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.05);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start();
    osc.stop(this.ctx.currentTime + 0.05);
  }

  playSuccess() {
    if (!state.soundEnabled) return;
    this.init();
    const notes = [523.25, 659.25, 783.99, 1046.5]; // C5, E5, G5, C6
    notes.forEach((freq, idx) => {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = "triangle";
      osc.frequency.setValueAtTime(freq, this.ctx.currentTime + idx * 0.08);
      gain.gain.setValueAtTime(0, this.ctx.currentTime + idx * 0.08);
      gain.gain.linearRampToValueAtTime(0.2, this.ctx.currentTime + idx * 0.08 + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + idx * 0.08 + 0.35);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(this.ctx.currentTime + idx * 0.08);
      osc.stop(this.ctx.currentTime + idx * 0.08 + 0.35);
    });
  }
}

const duoAudio = new CodingDuoAudio();

// --- Mascot Expressions & Speech Bubble ---
const MASCOT_PROMPTS = {
  welcome: "Welcome to CodingDuo! Paste your Three-Address Code or SSA form and I'll optimize it pass-by-pass!",
  thinking: "Running dataflow analysis, folding constants & hoisting invariants...",
  success: "Optimization passes complete! Check out the instruction count reduction below!",
  speaking: "Explaining the transformation passes in clear spoken English...",
  photo: "Drop a Control Flow Graph diagram or whiteboard Three-Address Code and I'll inspect it!",
  error: "Encountered an optimization issue. Check your IR syntax and try again!",
};

function setMascotMood(mood, customMessage = null) {
  const mascotEl = document.getElementById("mascot-svg");
  const speechEl = document.getElementById("mascot-speech");
  const leftEye = document.getElementById("eye-left");
  const rightEye = document.getElementById("eye-right");

  if (!mascotEl || !speechEl) return;

  mascotEl.className = "w-24 h-24 sm:w-28 sm:h-28 " + `mascot-${mood}`;
  speechEl.textContent = customMessage || MASCOT_PROMPTS[mood] || MASCOT_PROMPTS.welcome;

  if (mood === "thinking") {
    leftEye.setAttribute("cy", "42");
    rightEye.setAttribute("cy", "42");
  } else if (mood === "speaking") {
    leftEye.setAttribute("cy", "45");
    rightEye.setAttribute("cy", "45");
  } else {
    leftEye.setAttribute("cy", "46");
    rightEye.setAttribute("cy", "46");
  }
}

// --- Confetti Celebration on Optimization ---
function triggerConfetti() {
  const container = document.getElementById("confetti-container");
  if (!container) return;
  container.innerHTML = "";
  const colors = ["#58CC02", "#1CB0F6", "#FFC800", "#FF4B4B", "#CE82FF"];

  for (let i = 0; i < 30; i++) {
    const flake = document.createElement("div");
    flake.className = "absolute rounded-sm pointer-events-none";
    const size = Math.random() * 8 + 6;
    flake.style.width = `${size}px`;
    flake.style.height = `${size * 1.5}px`;
    flake.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
    flake.style.left = `${Math.random() * 100}%`;
    flake.style.top = "-10px";
    flake.style.opacity = "1";
    flake.style.transform = `rotate(${Math.random() * 360}deg)`;
    flake.style.transition = `all ${Math.random() * 1.5 + 1}s ease-out`;

    container.appendChild(flake);

    setTimeout(() => {
      flake.style.top = `${Math.random() * 80 + 20}%`;
      flake.style.opacity = "0";
      flake.style.transform = `rotate(${Math.random() * 720}deg) scale(0.5)`;
    }, 20);
  }

  setTimeout(() => { container.innerHTML = ""; }, 2500);
}

// --- Render Formatted Solution ---
function renderFormattedSolution(text) {
  // Convert Markdown code blocks with syntax highlighting & copy button
  let formatted = text.replace(/```([a-zA-Z]*)\n([\s\S]*?)```/g, (match, lang, code) => {
    const validLang = lang ? lang.trim() : "text";
    const encoded = encodeURIComponent(code.trim());
    return `
      <div class="my-4 rounded-xl border-2 border-gray-200 overflow-hidden bg-gray-900 text-white font-mono text-sm">
        <div class="flex items-center justify-between px-4 py-2 bg-gray-800 text-gray-300 text-xs uppercase tracking-wider font-bold">
          <span class="flex items-center space-x-1.5"><span class="text-green-400">●</span> <span>${validLang.toUpperCase()}</span></span>
          <button onclick="copyCode(this, '${encoded}')" class="text-xs px-2.5 py-1 rounded bg-gray-700 hover:bg-gray-600 transition font-sans">Copy Code</button>
        </div>
        <pre class="p-4 overflow-x-auto text-green-300 font-mono text-sm leading-relaxed"><code>${escapeHtml(code.trim())}</code></pre>
      </div>
    `;
  });

  // Convert Headers
  formatted = formatted.replace(/^### (.*$)/gim, '<h3 class="text-lg font-black text-gray-900 mt-5 mb-2 pb-1 border-b border-gray-200">$1</h3>');
  formatted = formatted.replace(/^## (.*$)/gim, '<h2 class="text-xl font-black text-gray-900 mt-6 mb-3 pb-1.5 border-b-2 border-gray-200">$1</h2>');

  // Bold
  formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong class="font-extrabold text-gray-900">$1</strong>');
  
  // Lists
  formatted = formatted.replace(/^\s*•\s*(.+)$/gm, '<li class="ml-4 list-disc text-gray-700">$1</li>');
  formatted = formatted.replace(/^\s*-\s*(.+)$/gm, '<li class="ml-4 list-disc text-gray-700">$1</li>');
  formatted = formatted.replace(/^\s*\d+\.\s*(.+)$/gm, '<li class="ml-4 list-decimal font-medium text-gray-700">$1</li>');

  // Paragraph breaks
  formatted = formatted.replace(/\n\n+/g, '<p class="my-3"></p>');

  return formatted;
}

function escapeHtml(str) {
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function copyCode(btn, encodedCode) {
  const code = decodeURIComponent(encodedCode);
  navigator.clipboard.writeText(code);
  const original = btn.textContent;
  btn.textContent = "Copied!";
  btn.classList.add("text-green-400");
  setTimeout(() => {
    btn.textContent = original;
    btn.classList.remove("text-green-400");
  }, 2000);
}

// --- Optimization Action Handler ---
async function handleOptimize() {
  const inputEl = document.getElementById("ir-code-input");
  const code = inputEl ? inputEl.value.trim() : "";

  if (!code) {
    inputEl.focus();
    return;
  }

  duoAudio.playClick();
  state.isGenerating = true;
  updateUIState();
  setMascotMood("thinking");

  try {
    const res = await fetch("/api/optimize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        code: code,
        pass_type: state.currentPass,
      }),
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Optimization failed");

    displaySolution(data.solution, data.optimizer || "AI Optimization Engine");
    duoAudio.playSuccess();
    triggerConfetti();
    setMascotMood("success");

    state.xp += 25;
    state.gems += 5;
    updateStatsDisplay();

  } catch (err) {
    console.error(err);
    setMascotMood("error", `Error: ${err.message}`);
    alert(`Optimization error: ${err.message}`);
  } finally {
    state.isGenerating = false;
    updateUIState();
  }
}

// --- Photo / Flowgraph Upload & Optimize ---
async function handlePhotoOptimize() {
  if (!state.selectedFile) {
    alert("Please select or drop a Control Flow Graph or IR image first!");
    return;
  }

  duoAudio.playClick();
  state.isGenerating = true;
  updateUIState();
  setMascotMood("thinking", "Scanning CFG diagram and basic blocks...");

  const formData = new FormData();
  formData.append("file", state.selectedFile);
  formData.append("pass_type", state.currentPass);

  try {
    const res = await fetch("/api/optimize-image", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Image IR optimization failed");

    displaySolution(data.solution, data.optimizer || "AI Optimization Engine");
    duoAudio.playSuccess();
    triggerConfetti();
    setMascotMood("success");

    state.xp += 30;
    updateStatsDisplay();

  } catch (err) {
    console.error(err);
    setMascotMood("error", `Error: ${err.message}`);
    alert(`Image optimizer error: ${err.message}`);
  } finally {
    state.isGenerating = false;
    updateUIState();
  }
}

// --- Voice Narration Playback ---
async function handlePlayAudio() {
  if (!state.activeSolutionText) return;

  const ttsBtn = document.getElementById("tts-btn");
  const ttsText = document.getElementById("tts-btn-text");
  const soundWave = document.getElementById("tts-wave");

  if (state.isPlayingAudio && state.currentAudio) {
    state.currentAudio.pause();
    state.isPlayingAudio = false;
    ttsText.textContent = "Explain Passes Aloud";
    soundWave.classList.add("hidden");
    setMascotMood("idle");
    return;
  }

  duoAudio.playClick();
  ttsText.textContent = "Synthesizing Voice...";
  ttsBtn.disabled = true;

  try {
    const res = await fetch("/api/tts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: state.activeSolutionText }),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Voice narration failed");
    }

    const audioBlob = await res.blob();
    const audioUrl = URL.createObjectURL(audioBlob);

    if (state.currentAudio) {
      state.currentAudio.pause();
    }

    const audio = new Audio(audioUrl);
    state.currentAudio = audio;
    state.isPlayingAudio = true;

    ttsText.textContent = "Pause Explanation";
    soundWave.classList.remove("hidden");
    ttsBtn.disabled = false;
    setMascotMood("speaking");

    audio.onended = () => {
      state.isPlayingAudio = false;
      ttsText.textContent = "Explain Passes Again";
      soundWave.classList.add("hidden");
      setMascotMood("idle");
    };

    audio.onerror = () => {
      state.isPlayingAudio = false;
      ttsText.textContent = "Explain Passes Aloud";
      soundWave.classList.add("hidden");
      setMascotMood("idle");
    };

    await audio.play();

  } catch (err) {
    console.error("TTS Error:", err);
    alert(`Voice narration error: ${err.message}`);
    ttsText.textContent = "Explain Passes Aloud";
    ttsBtn.disabled = false;
    soundWave.classList.add("hidden");
    setMascotMood("idle");
  }
}

// --- Display Solution ---
function displaySolution(solutionText, optimizer) {
  state.activeSolutionText = solutionText;
  const resultCard = document.getElementById("solution-card");
  const contentEl = document.getElementById("solution-content");
  const badgeEl = document.getElementById("solution-badge");

  if (!resultCard || !contentEl) return;

  resultCard.classList.remove("hidden");
  badgeEl.textContent = `OPTIMIZATION PASSES APPLIED (${optimizer})`;
  contentEl.innerHTML = renderFormattedSolution(solutionText);

  // Scroll smoothly to solution
  resultCard.scrollIntoView({ behavior: "smooth", block: "start" });
}

// --- UI Updates ---
function updateUIState() {
  const optBtn = document.getElementById("optimize-btn");
  const photoOptBtn = document.getElementById("photo-optimize-btn");
  const spinner = document.getElementById("loading-spinner");

  if (optBtn) {
    optBtn.disabled = state.isGenerating;
    optBtn.style.opacity = state.isGenerating ? "0.6" : "1";
  }
  if (photoOptBtn) {
    photoOptBtn.disabled = state.isGenerating;
    photoOptBtn.style.opacity = state.isGenerating ? "0.6" : "1";
  }
  if (spinner) {
    spinner.style.display = state.isGenerating ? "flex" : "none";
  }
}

function updateStatsDisplay() {
  document.getElementById("stat-xp").textContent = `${state.xp.toLocaleString()} XP`;
  document.getElementById("stat-gems").textContent = `${state.gems}`;
  document.getElementById("stat-streak").textContent = `${state.streak}`;
}

// --- Load Presets ---
async function loadPresets() {
  try {
    const res = await fetch("/api/presets");
    if (res.ok) {
      state.presets = await res.json();
    }
  } catch (e) {
    console.warn("Could not load presets:", e);
  }
}

// --- Initialize Event Listeners ---
document.addEventListener("DOMContentLoaded", async () => {
  await loadPresets();

  // Tab Switching
  document.querySelectorAll("[data-tab]").forEach((btn) => {
    btn.addEventListener("click", () => {
      duoAudio.playClick();
      const tab = btn.getAttribute("data-tab");
      state.currentTab = tab;

      document.querySelectorAll("[data-tab]").forEach((b) => b.classList.remove("border-[#58CC02]", "text-[#58CC02]"));
      document.querySelectorAll("[data-tab]").forEach((b) => b.classList.add("border-transparent", "text-gray-400"));
      
      btn.classList.remove("border-transparent", "text-gray-400");
      btn.classList.add("border-[#58CC02]", "text-[#58CC02]");

      document.getElementById("tab-editor-view").classList.toggle("hidden", tab !== "editor");
      document.getElementById("tab-photo-view").classList.toggle("hidden", tab !== "photo");

      setMascotMood(tab === "photo" ? "photo" : "welcome");
    });
  });

  // Pass Strategy Switching
  document.querySelectorAll("[data-pass]").forEach((btn) => {
    btn.addEventListener("click", () => {
      duoAudio.playClick();
      state.currentPass = btn.getAttribute("data-pass");
      document.querySelectorAll("[data-pass]").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
    });
  });

  // Preset Chips Loader
  document.querySelectorAll(".preset-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      duoAudio.playClick();
      const key = chip.getAttribute("data-preset");
      const inputEl = document.getElementById("ir-code-input");
      if (inputEl && state.presets[key]) {
        inputEl.value = state.presets[key].code;
        inputEl.focus();
        setMascotMood("welcome", `Loaded ${state.presets[key].title}! Click 'Apply Optimization Passes' to run.`);
      }
    });
  });

  // Sound Toggle
  const soundBtn = document.getElementById("sound-toggle-btn");
  if (soundBtn) {
    soundBtn.addEventListener("click", () => {
      state.soundEnabled = !state.soundEnabled;
      soundBtn.textContent = state.soundEnabled ? "🔊 Sound ON" : "🔇 Sound OFF";
      duoAudio.playClick();
    });
  }

  // File Upload Drag & Drop
  const dropZone = document.getElementById("drop-zone");
  const fileInput = document.getElementById("file-input");

  if (dropZone && fileInput) {
    dropZone.addEventListener("click", () => fileInput.click());
    fileInput.addEventListener("change", (e) => {
      if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
      }
    });

    dropZone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropZone.classList.add("border-blue-400", "bg-blue-50");
    });

    dropZone.addEventListener("dragleave", () => {
      dropZone.classList.remove("border-blue-400", "bg-blue-50");
    });

    dropZone.addEventListener("drop", (e) => {
      e.preventDefault();
      dropZone.classList.remove("border-blue-400", "bg-blue-50");
      if (e.dataTransfer.files.length > 0) {
        handleFileSelect(e.dataTransfer.files[0]);
      }
    });
  }

  function handleFileSelect(file) {
    state.selectedFile = file;
    const previewContainer = document.getElementById("photo-preview-container");
    const previewImg = document.getElementById("photo-preview");
    const fileName = document.getElementById("photo-name");

    if (previewContainer && previewImg && fileName) {
      previewContainer.classList.remove("hidden");
      fileName.textContent = file.name;
      const reader = new FileReader();
      reader.onload = (ev) => { previewImg.src = ev.target.result; };
      reader.readAsDataURL(file);
    }
  }

  // Optimize Action Buttons
  const optBtn = document.getElementById("optimize-btn");
  if (optBtn) optBtn.addEventListener("click", handleOptimize);

  const photoOptBtn = document.getElementById("photo-optimize-btn");
  if (photoOptBtn) photoOptBtn.addEventListener("click", handlePhotoOptimize);

  const ttsBtn = document.getElementById("tts-btn");
  if (ttsBtn) ttsBtn.addEventListener("click", handlePlayAudio);

  // Keyboard shortcut Cmd/Ctrl + Enter
  const irInput = document.getElementById("ir-code-input");
  if (irInput) {
    irInput.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault();
        handleOptimize();
      }
    });
  }
});
