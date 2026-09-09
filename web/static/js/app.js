/**
 * DuoSolve - Interactive Web Application Logic
 * Duolingo Feather Design System, Web Audio Synthesizer & ElevenLabs Voice Narration
 */

// --- Global State ---
const state = {
  currentPersona: "solver",
  currentTab: "solve", // "solve" or "photo"
  soundEnabled: true,
  isGenerating: false,
  isPlayingAudio: false,
  currentAudio: null,
  xp: 1420,
  streak: 5,
  gems: 750,
  hearts: 5,
  selectedFile: null,
  activeSolutionText: "",
};

// --- Web Audio Synthesizer (Duolingo-style Sound Effects) ---
class DuoAudioSynthesizer {
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
    osc.frequency.setValueAtTime(600, this.ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(300, this.ctx.currentTime + 0.05);
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

const duoAudio = new DuoAudioSynthesizer();

// --- Mascot Expressions & Speech Bubble ---
const MASCOT_PROMPTS = {
  welcome: "Hi! I am Duo, your problem-solving buddy! What are we conquering today?",
  thinking: "Calculating with Azure OpenAI Brain... hold tight!",
  success: "Fantastic work! Here is the complete step-by-step solution!",
  speaking: "Listen up! Reading the solution in ElevenLabs natural voice...",
  photo: "Drop a photo of your homework or error and I'll examine it!",
  error: "Oops, something went wrong. Let's give it another shot!",
};

function setMascotMood(mood, customMessage = null) {
  const mascotEl = document.getElementById("mascot-svg");
  const speechEl = document.getElementById("mascot-speech");
  const leftEye = document.getElementById("eye-left");
  const rightEye = document.getElementById("eye-right");
  const beak = document.getElementById("mascot-beak");

  if (!mascotEl || !speechEl) return;

  mascotEl.className = "w-28 h-28 " + `mascot-${mood}`;
  speechEl.textContent = customMessage || MASCOT_PROMPTS[mood] || MASCOT_PROMPTS.welcome;

  if (mood === "thinking") {
    leftEye.setAttribute("cy", "42");
    rightEye.setAttribute("cy", "42");
  } else if (mood === "speaking") {
    leftEye.setAttribute("cy", "46");
    rightEye.setAttribute("cy", "46");
  } else {
    leftEye.setAttribute("cy", "48");
    rightEye.setAttribute("cy", "48");
  }
}

// --- Confetti Animation on Success ---
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

// --- Markdown, Math & Code Formatter ---
function renderFormattedSolution(text) {
  // Convert Markdown code blocks with syntax highlighting & copy button
  let formatted = text.replace(/```([a-zA-Z]*)\n([\s\S]*?)```/g, (match, lang, code) => {
    const validLang = lang ? lang.trim() : "plaintext";
    const encoded = encodeURIComponent(code.trim());
    return `
      <div class="my-4 rounded-xl border-2 border-gray-200 overflow-hidden bg-gray-900 text-white font-mono text-sm">
        <div class="flex items-center justify-between px-4 py-2 bg-gray-800 text-gray-300 text-xs uppercase tracking-wider font-bold">
          <span>${validLang}</span>
          <button onclick="copyCode(this, '${encoded}')" class="text-xs px-2.5 py-1 rounded bg-gray-700 hover:bg-gray-600 transition">Copy</button>
        </div>
        <pre class="p-4 overflow-x-auto"><code>${escapeHtml(code.trim())}</code></pre>
      </div>
    `;
  });

  // Convert Bold **text**
  formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong class="font-extrabold text-gray-900">$1</strong>');
  
  // Convert bullet lists
  formatted = formatted.replace(/^\s*•\s*(.+)$/gm, '<li class="ml-4 list-disc">$1</li>');
  formatted = formatted.replace(/^\s*\d+\.\s*(.+)$/gm, '<li class="ml-4 list-decimal font-medium">$1</li>');

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

// --- Problem Solving Action ---
async function handleSolve() {
  const inputEl = document.getElementById("problem-input");
  const prompt = inputEl ? inputEl.value.trim() : "";

  if (!prompt) {
    inputEl.focus();
    return;
  }

  duoAudio.playClick();
  state.isGenerating = true;
  updateUIState();
  setMascotMood("thinking");

  try {
    const res = await fetch("/api/solve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt: prompt,
        persona: state.currentPersona,
      }),
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Solving failed");

    displaySolution(data.solution, data.provider, data.model);
    duoAudio.playSuccess();
    triggerConfetti();
    setMascotMood("success");

    // Update stats
    state.xp += 20;
    state.gems += 5;
    updateStatsDisplay();

  } catch (err) {
    console.error(err);
    setMascotMood("error", `Error: ${err.message}`);
    alert(`Could not solve: ${err.message}`);
  } finally {
    state.isGenerating = false;
    updateUIState();
  }
}

// --- Photo Upload & Solve ---
async function handlePhotoSolve() {
  if (!state.selectedFile) {
    alert("Please select or drop an image file first!");
    return;
  }

  duoAudio.playClick();
  state.isGenerating = true;
  updateUIState();
  setMascotMood("thinking", "Analyzing photo with vision AI...");

  const captionEl = document.getElementById("photo-caption");
  const caption = captionEl ? captionEl.value.trim() : "";

  const formData = new FormData();
  formData.append("file", state.selectedFile);
  if (caption) formData.append("caption", caption);
  formData.append("persona", state.currentPersona);

  try {
    const res = await fetch("/api/solve-image", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Image solving failed");

    displaySolution(data.solution, data.provider, data.model);
    duoAudio.playSuccess();
    triggerConfetti();
    setMascotMood("success");

    state.xp += 30;
    updateStatsDisplay();

  } catch (err) {
    console.error(err);
    setMascotMood("error", `Error: ${err.message}`);
    alert(`Image solver error: ${err.message}`);
  } finally {
    state.isGenerating = false;
    updateUIState();
  }
}

// --- ElevenLabs Text-to-Speech Playback ---
async function handlePlayAudio() {
  if (!state.activeSolutionText) return;

  const ttsBtn = document.getElementById("tts-btn");
  const ttsText = document.getElementById("tts-btn-text");
  const soundWave = document.getElementById("tts-wave");

  if (state.isPlayingAudio && state.currentAudio) {
    state.currentAudio.pause();
    state.isPlayingAudio = false;
    ttsText.textContent = "Listen Solution";
    soundWave.classList.add("hidden");
    setMascotMood("idle");
    return;
  }

  duoAudio.playClick();
  ttsText.textContent = "Loading Voice...";
  ttsBtn.disabled = true;

  try {
    const res = await fetch("/api/tts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: state.activeSolutionText }),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "TTS generation failed");
    }

    const audioBlob = await res.blob();
    const audioUrl = URL.createObjectURL(audioBlob);

    if (state.currentAudio) {
      state.currentAudio.pause();
    }

    const audio = new Audio(audioUrl);
    state.currentAudio = audio;
    state.isPlayingAudio = true;

    ttsText.textContent = "Pause Voice";
    soundWave.classList.remove("hidden");
    ttsBtn.disabled = false;
    setMascotMood("speaking");

    audio.onended = () => {
      state.isPlayingAudio = false;
      ttsText.textContent = "Listen Again";
      soundWave.classList.add("hidden");
      setMascotMood("idle");
    };

    audio.onerror = () => {
      state.isPlayingAudio = false;
      ttsText.textContent = "Listen Solution";
      soundWave.classList.add("hidden");
      setMascotMood("idle");
    };

    await audio.play();

  } catch (err) {
    console.error("TTS Error:", err);
    alert(`Voice narration error: ${err.message}`);
    ttsText.textContent = "Listen Solution";
    ttsBtn.disabled = false;
    soundWave.classList.add("hidden");
    setMascotMood("idle");
  }
}

// --- Display Solution ---
function displaySolution(solutionText, provider, model) {
  state.activeSolutionText = solutionText;
  const resultCard = document.getElementById("solution-card");
  const contentEl = document.getElementById("solution-content");
  const badgeEl = document.getElementById("solution-badge");

  if (!resultCard || !contentEl) return;

  resultCard.classList.remove("hidden");
  badgeEl.textContent = `SOLVED BY ${provider.toUpperCase()} (${model})`;
  contentEl.innerHTML = renderFormattedSolution(solutionText);

  // Trigger KaTeX math rendering if KaTeX is loaded
  if (window.renderMathInElement) {
    try {
      window.renderMathInElement(contentEl, {
        delimiters: [
          { left: "$$", right: "$$", display: true },
          { left: "\\[", right: "\\]", display: true },
          { left: "$", right: "$", display: false },
          { left: "\\(", right: "\\)", display: false },
        ],
        throwOnError: false,
      });
    } catch (e) {
      console.warn("KaTeX rendering warning:", e);
    }
  }

  // Scroll smoothly to solution
  resultCard.scrollIntoView({ behavior: "smooth", block: "start" });
}

// --- UI Updates & Event Handlers ---
function updateUIState() {
  const solveBtn = document.getElementById("solve-btn");
  const photoSolveBtn = document.getElementById("photo-solve-btn");
  const spinner = document.getElementById("loading-spinner");

  if (solveBtn) {
    solveBtn.disabled = state.isGenerating;
    solveBtn.style.opacity = state.isGenerating ? "0.6" : "1";
  }
  if (photoSolveBtn) {
    photoSolveBtn.disabled = state.isGenerating;
    photoSolveBtn.style.opacity = state.isGenerating ? "0.6" : "1";
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

// --- Initialize Event Listeners ---
document.addEventListener("DOMContentLoaded", () => {
  // Tab Switching
  document.querySelectorAll("[data-tab]").forEach((btn) => {
    btn.addEventListener("click", () => {
      duoAudio.playClick();
      const tab = btn.getAttribute("data-tab");
      state.currentTab = tab;

      document.querySelectorAll("[data-tab]").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");

      document.getElementById("tab-solve-view").classList.toggle("hidden", tab !== "solve");
      document.getElementById("tab-photo-view").classList.toggle("hidden", tab !== "photo");

      setMascotMood(tab === "photo" ? "photo" : "welcome");
    });
  });

  // Persona Switching
  document.querySelectorAll("[data-persona]").forEach((btn) => {
    btn.addEventListener("click", () => {
      duoAudio.playClick();
      state.currentPersona = btn.getAttribute("data-persona");
      document.querySelectorAll("[data-persona]").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
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

  // Quick Chips
  document.querySelectorAll(".quick-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      duoAudio.playClick();
      const inputEl = document.getElementById("problem-input");
      if (inputEl) {
        inputEl.value = chip.getAttribute("data-query");
        inputEl.focus();
      }
    });
  });

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

  // Solve Action Buttons
  const solveBtn = document.getElementById("solve-btn");
  if (solveBtn) solveBtn.addEventListener("click", handleSolve);

  const photoSolveBtn = document.getElementById("photo-solve-btn");
  if (photoSolveBtn) photoSolveBtn.addEventListener("click", handlePhotoSolve);

  const ttsBtn = document.getElementById("tts-btn");
  if (ttsBtn) ttsBtn.addEventListener("click", handlePlayAudio);

  // Keyboard shortcut Ctrl/Cmd + Enter to solve
  const problemInput = document.getElementById("problem-input");
  if (problemInput) {
    problemInput.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault();
        handleSolve();
      }
    });
  }
});
