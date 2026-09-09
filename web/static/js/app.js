/**
 * CodingDuo - Interactive Web Application Logic
 * 6 Famous Languages Boilerplate, Inline Error Inspection (ⓘ), 1-Click 'Apply' Fix,
 * and Teacher-Style Voice Walkthrough
 */

// --- Global State ---
const state = {
  currentPass: "all_passes",
  currentTab: "editor", // "editor" or "photo"
  currentLang: "python",
  soundEnabled: true,
  isGenerating: false,
  isPlayingAudio: false,
  currentAudio: null,
  xp: 1420,
  streak: 5,
  gems: 750,
  selectedFile: null,
  activeSolutionText: "",
  activeInputCode: "",
  teacherTranscript: "",
  boilerplates: {},
  detectedErrors: [],
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

function setTeacherMessage(msg) {
  const el = document.getElementById("teacher-status-message");
  if (el) el.textContent = msg;
}

// --- Confetti Celebration ---
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

  formatted = formatted.replace(/^### (.*$)/gim, '<h3 class="text-lg font-black text-gray-900 mt-5 mb-2 pb-1 border-b border-gray-200">$1</h3>');
  formatted = formatted.replace(/^## (.*$)/gim, '<h2 class="text-xl font-black text-gray-900 mt-6 mb-3 pb-1.5 border-b-2 border-gray-200">$1</h2>');
  formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong class="font-extrabold text-gray-900">$1</strong>');
  formatted = formatted.replace(/^\s*•\s*(.+)$/gm, '<li class="ml-4 list-disc text-gray-700">$1</li>');
  formatted = formatted.replace(/^\s*-\s*(.+)$/gm, '<li class="ml-4 list-disc text-gray-700">$1</li>');
  formatted = formatted.replace(/^\s*\d+\.\s*(.+)$/gm, '<li class="ml-4 list-decimal font-medium text-gray-700">$1</li>');
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

// --- Load Language Boilerplate Code ---
function loadLanguageBoilerplate(langKey) {
  if (!state.boilerplates[langKey]) return;
  state.currentLang = langKey;
  const template = state.boilerplates[langKey];

  const codeInput = document.getElementById("ir-code-input");
  const filenameEl = document.getElementById("active-filename");

  if (codeInput) {
    codeInput.value = template.code;
  }
  if (filenameEl) {
    filenameEl.textContent = template.filename;
  }

  // Clear any active errors when changing templates
  clearInlineErrors();

  document.querySelectorAll(".lang-boilerplate-btn").forEach((btn) => {
    const isTarget = btn.getAttribute("data-lang") === langKey;
    btn.classList.toggle("active", isTarget);
    btn.classList.toggle("border-[#1CB0F6]", isTarget);
  });

  setTeacherMessage(
    `Loaded ${template.name} boilerplate! If you make any typo, click 🔍 Check Code to see the ⓘ info button and Apply fix!`
  );
}

// --- Inline Error Detection & 1-Click Fix System ---

async function checkCodeForMistakes(showCleanNotice = true) {
  const inputEl = document.getElementById("ir-code-input");
  const code = inputEl ? inputEl.value.trim() : "";

  if (!code) return false;

  duoAudio.playClick();
  setTeacherMessage("Checking code for syntax mistakes and typos...");

  try {
    const res = await fetch("/api/check-code", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        code: code,
        language: state.currentLang,
      }),
    });

    const data = await res.json();
    if (data.has_errors && data.errors && data.errors.length > 0) {
      state.detectedErrors = data.errors;
      renderInlineErrors(data.errors);
      setTeacherMessage(
        `⚠️ Found mistake on line ${data.errors[0].line_number}! Click the ⓘ button and press 'Apply' to fix the line instantly!`
      );
      return true;
    } else {
      clearInlineErrors();
      if (showCleanNotice) {
        setTeacherMessage("✅ Code looks clean! No syntax errors detected. Ready for compiler optimization passes.");
      }
      return false;
    }
  } catch (err) {
    console.warn("Check code error:", err);
    return false;
  }
}

function clearInlineErrors() {
  state.detectedErrors = [];
  const container = document.getElementById("inline-errors-container");
  if (container) {
    container.innerHTML = "";
    container.classList.add("hidden");
  }
}

function renderInlineErrors(errors) {
  const container = document.getElementById("inline-errors-container");
  if (!container) return;

  container.innerHTML = "";
  container.classList.remove("hidden");

  errors.forEach((err, idx) => {
    const card = document.createElement("div");
    card.id = `error-card-${err.line_number}`;
    card.className = "inline-error-card p-4";

    const encodedSuggested = encodeURIComponent(err.suggested_line);

    card.innerHTML = `
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        
        <!-- Left: Line Badge & (i) Info Button & Summary -->
        <div class="flex items-start sm:items-center space-x-3">
          <!-- Line number badge -->
          <span class="px-2.5 py-1 rounded-lg bg-red-100 text-red-700 font-mono font-black text-xs border border-red-200 flex-shrink-0">
            Line ${err.line_number}
          </span>

          <!-- (i) Info Circle Button -->
          <button 
            class="info-circle-btn flex-shrink-0" 
            title="Inspect Mistake Details" 
            onclick="toggleErrorDetails(${err.line_number})"
          >
            ⓘ
          </button>

          <!-- Error Message -->
          <div class="text-xs sm:text-sm font-extrabold text-red-800">
            ${escapeHtml(err.message)}
          </div>
        </div>

        <!-- Right: 1-Click 'Apply' Button -->
        <div class="flex items-center space-x-2 self-end sm:self-center">
          <button 
            onclick="applyLineFix(${err.line_number}, '${encodedSuggested}')" 
            class="btn-apply"
            title="Apply suggested fix to this line"
          >
            <span>✓</span>
            <span>Apply</span>
          </button>
        </div>

      </div>

      <!-- Expandable Code Diff Comparison -->
      <div id="error-details-${err.line_number}" class="mt-3 pt-3 border-t border-red-200 grid grid-cols-1 md:grid-cols-2 gap-2 text-xs font-mono">
        <div class="p-2.5 rounded-xl bg-red-100/70 text-red-900 border border-red-200">
          <span class="text-[10px] uppercase font-black tracking-wider text-red-600 block mb-1">❌ Mistake on Line ${err.line_number}:</span>
          <code class="whitespace-pre-wrap">${escapeHtml(err.faulty_line)}</code>
        </div>
        <div class="p-2.5 rounded-xl bg-green-100/70 text-green-900 border border-green-200">
          <span class="text-[10px] uppercase font-black tracking-wider text-green-600 block mb-1">💡 Corrected Line (Click Apply):</span>
          <code class="whitespace-pre-wrap font-bold text-green-800">${escapeHtml(err.suggested_line)}</code>
        </div>
      </div>
    `;

    container.appendChild(card);
  });
}

function toggleErrorDetails(lineNumber) {
  duoAudio.playClick();
  const el = document.getElementById(`error-details-${lineNumber}`);
  if (el) {
    el.classList.toggle("hidden");
  }
}

// --- 1-Click Apply Line Fix Handler ---
window.applyLineFix = function(lineNumber, encodedSuggestedLine) {
  const suggestedLine = decodeURIComponent(encodedSuggestedLine);
  const inputEl = document.getElementById("ir-code-input");

  if (!inputEl) return;

  const lines = inputEl.value.split("\n");
  if (lineNumber > 0 && lineNumber <= lines.length) {
    // Replace the exact line with the suggested line
    lines[lineNumber - 1] = suggestedLine;
    inputEl.value = lines.join("\n");

    duoAudio.playSuccess();

    // Remove the error card with feedback
    const card = document.getElementById(`error-card-${lineNumber}`);
    if (card) {
      card.style.opacity = "0";
      card.style.transform = "scale(0.95)";
      setTimeout(() => {
        card.remove();
        // Check if all errors resolved
        const container = document.getElementById("inline-errors-container");
        if (container && container.children.length === 0) {
          container.classList.add("hidden");
          setTeacherMessage(`✅ Line ${lineNumber} fixed! All syntax errors resolved. Code is ready to optimize!`);
        } else {
          setTeacherMessage(`✅ Line ${lineNumber} fixed!`);
        }
      }, 200);
    }
  }
};

window.toggleErrorDetails = toggleErrorDetails;

// --- Optimize Code Action Handler ---
async function handleOptimize() {
  const inputEl = document.getElementById("ir-code-input");
  const code = inputEl ? inputEl.value.trim() : "";

  if (!code) {
    inputEl.focus();
    return;
  }

  // Pre-flight check: if there's an obvious syntax mistake, display it with (i) + Apply
  const hasErrors = await checkCodeForMistakes(false);
  if (hasErrors) {
    alert("⚠️ Please review and apply the suggested fix on the mistake highlighted above before compiling!");
    return;
  }

  state.activeInputCode = code;
  duoAudio.playClick();
  state.isGenerating = true;
  updateUIState();
  setTeacherMessage("Running compiler optimization pipeline... Computing dataflow analysis & hoisting invariant code!");

  try {
    const res = await fetch("/api/optimize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        code: code,
        pass_type: state.currentPass,
        language: state.currentLang,
      }),
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Optimization failed");

    displaySolution(data.solution, data.optimizer || "AI Optimization Engine");
    duoAudio.playSuccess();
    triggerConfetti();
    setTeacherMessage("Success! Compiler optimization passes completed. Click 'Explain Like a Teacher' to hear the voice walkthrough!");

    state.xp += 25;
    state.gems += 5;
    updateStatsDisplay();

  } catch (err) {
    console.error(err);
    setTeacherMessage(`Optimization error: ${err.message}`);
    alert(`Optimization error: ${err.message}`);
  } finally {
    state.isGenerating = false;
    updateUIState();
  }
}

// --- Photo / Flowgraph Upload & Optimize ---
async function handlePhotoOptimize() {
  if (!state.selectedFile) {
    alert("Please select or drop a Control Flow Graph or diagram first!");
    return;
  }

  duoAudio.playClick();
  state.isGenerating = true;
  updateUIState();
  setTeacherMessage("Scanning flowgraph image and extracting basic blocks...");

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

    state.activeInputCode = "Image Flowgraph Input";
    displaySolution(data.solution, data.optimizer || "AI Optimization Engine");
    duoAudio.playSuccess();
    triggerConfetti();
    setTeacherMessage("Image Flowgraph optimization complete! Listen to the teacher explanation below.");

    state.xp += 30;
    updateStatsDisplay();

  } catch (err) {
    console.error(err);
    setTeacherMessage(`Image optimizer error: ${err.message}`);
    alert(`Image optimizer error: ${err.message}`);
  } finally {
    state.isGenerating = false;
    updateUIState();
  }
}

// --- Teacher-Style Voice Walkthrough Playback ---
async function handlePlayAudio() {
  if (!state.activeSolutionText) return;

  const ttsBtn = document.getElementById("tts-btn");
  const ttsText = document.getElementById("tts-btn-text");
  const soundWave = document.getElementById("tts-wave");
  const transcriptCard = document.getElementById("teacher-transcript-card");
  const transcriptText = document.getElementById("teacher-transcript-text");

  if (state.isPlayingAudio && state.currentAudio) {
    state.currentAudio.pause();
    state.isPlayingAudio = false;
    ttsText.textContent = "Explain Like a Teacher (Voice)";
    soundWave.classList.add("hidden");
    return;
  }

  duoAudio.playClick();
  ttsText.textContent = "Professor is Preparing Walkthrough...";
  ttsBtn.disabled = true;

  try {
    // 1. Fetch teacher script
    const teacherScriptRes = await fetch("/api/teacher-explanation", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        code: state.activeInputCode || "Intermediate Code",
        solution: state.activeSolutionText,
      }),
    });

    let teacherScript = "";
    if (teacherScriptRes.ok) {
      const data = await teacherScriptRes.json();
      teacherScript = data.teacher_script;
      state.teacherTranscript = teacherScript;
      
      if (transcriptCard && transcriptText) {
        transcriptText.textContent = `"${teacherScript}"`;
        transcriptCard.classList.remove("hidden");
      }
    }

    // 2. Stream audio
    const res = await fetch("/api/tts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: teacherScript || state.activeSolutionText,
        teacher_mode: true,
      }),
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

    ttsText.textContent = "Pause Teacher Explanation";
    soundWave.classList.remove("hidden");
    ttsBtn.disabled = false;
    setTeacherMessage("Speaking: Professor is walking you through the optimization passes!");

    audio.onended = () => {
      state.isPlayingAudio = false;
      ttsText.textContent = "Explain Like a Teacher Again";
      soundWave.classList.add("hidden");
      setTeacherMessage("Finished walkthrough! You can edit the code and optimize again!");
    };

    audio.onerror = () => {
      state.isPlayingAudio = false;
      ttsText.textContent = "Explain Like a Teacher (Voice)";
      soundWave.classList.add("hidden");
    };

    await audio.play();

  } catch (err) {
    console.error("TTS Error:", err);
    alert(`Teacher voice error: ${err.message}`);
    ttsText.textContent = "Explain Like a Teacher (Voice)";
    ttsBtn.disabled = false;
    soundWave.classList.add("hidden");
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

// --- Fetch Boilerplates from API ---
async function fetchBoilerplates() {
  try {
    const res = await fetch("/api/boilerplates");
    if (res.ok) {
      state.boilerplates = await res.json();
      loadLanguageBoilerplate("python");
    }
  } catch (e) {
    console.warn("Could not load boilerplates:", e);
  }
}

// --- Initialize Event Listeners ---
document.addEventListener("DOMContentLoaded", async () => {
  await fetchBoilerplates();

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

      setTeacherMessage(tab === "photo" ? "Upload a Control Flow Graph (CFG) diagram or whiteboard code!" : "Select a language boilerplate or edit code directly!");
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

  // 6 Language Boilerplate Buttons
  document.querySelectorAll(".lang-boilerplate-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      duoAudio.playClick();
      const lang = btn.getAttribute("data-lang");
      loadLanguageBoilerplate(lang);
    });
  });

  // Check Code Button
  const checkCodeBtn = document.getElementById("check-code-btn");
  if (checkCodeBtn) {
    checkCodeBtn.addEventListener("click", () => checkCodeForMistakes(true));
  }

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

  // Action Buttons
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
