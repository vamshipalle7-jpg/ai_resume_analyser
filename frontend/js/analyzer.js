/**
 * Analyzer Module
 * Handles file drag & drop, analysis execution, and rendering of all ATS & AI insights.
 */
const Analyzer = {
  currentFile: null,
  currentAnalysis: null,
  samplePresets: [],

  init() {
    this.setupDropzone();
    this.loadSamplePresets();
  },

  setupDropzone() {
    const dropzone = document.getElementById("dropzone");
    const fileInput = document.getElementById("resume-file-input");

    if (!dropzone || !fileInput) return;

    ["dragenter", "dragover"].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.add("dropzone-active");
      });
    });

    ["dragleave", "drop"].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove("dropzone-active");
      });
    });

    dropzone.addEventListener("drop", (e) => {
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        this.selectFile(files[0]);
      }
    });

    dropzone.addEventListener("click", () => {
      fileInput.click();
    });

    fileInput.addEventListener("change", (e) => {
      if (e.target.files.length > 0) {
        this.selectFile(e.target.files[0]);
      }
    });
  },

  selectFile(file) {
    const validExtensions = [".pdf", ".docx", ".doc"];
    const fileExt = file.name.substring(file.name.lastIndexOf(".")).toLowerCase();
    
    if (!validExtensions.includes(fileExt)) {
      App.showToast("Unsupported file format. Please upload a PDF or DOCX resume.", "error");
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      App.showToast("File size exceeds 10MB limit.", "error");
      return;
    }

    this.currentFile = file;
    this.updateFilePreview(file);
    App.showToast(`Selected file: ${file.name}`, "info");
  },

  updateFilePreview(file) {
    const previewContainer = document.getElementById("file-preview-card");
    const defaultDropzoneContent = document.getElementById("dropzone-default");
    const fileNameEl = document.getElementById("preview-file-name");
    const fileSizeEl = document.getElementById("preview-file-size");
    const fileTypeBadge = document.getElementById("preview-file-type");

    if (file) {
      if (defaultDropzoneContent) defaultDropzoneContent.classList.add("hidden");
      if (previewContainer) previewContainer.classList.remove("hidden");
      if (fileNameEl) fileNameEl.textContent = file.name;
      if (fileSizeEl) fileSizeEl.textContent = `${(file.size / 1024).toFixed(1)} KB`;
      if (fileTypeBadge) {
        const isPdf = file.name.toLowerCase().endsWith(".pdf");
        fileTypeBadge.textContent = isPdf ? "PDF" : "DOCX";
        fileTypeBadge.className = isPdf
          ? "px-2 py-0.5 text-xs font-bold bg-red-100 text-red-700 rounded"
          : "px-2 py-0.5 text-xs font-bold bg-blue-100 text-blue-700 rounded";
      }
    } else {
      if (defaultDropzoneContent) defaultDropzoneContent.classList.remove("hidden");
      if (previewContainer) previewContainer.classList.add("hidden");
    }
  },

  clearSelectedFile(e) {
    if (e) e.stopPropagation();
    this.currentFile = null;
    const fileInput = document.getElementById("resume-file-input");
    if (fileInput) fileInput.value = "";
    this.updateFilePreview(null);
  },

  async loadSamplePresets() {
    try {
      const data = await API.get(CONFIG.ENDPOINTS.SAMPLES);
      this.samplePresets = data.job_descriptions || [];
      this.renderSampleSelect();
    } catch (e) {
      console.warn("Could not load sample presets:", e);
    }
  },

  renderSampleSelect() {
    const select = document.getElementById("sample-jd-select");
    if (!select || !this.samplePresets.length) return;

    select.innerHTML = '<option value="">-- Or choose a sample Job Description --</option>' +
      this.samplePresets.map(p => `<option value="${p.id}">${p.title} (${p.industry})</option>`).join("");

    select.addEventListener("change", (e) => {
      const selected = this.samplePresets.find(p => p.id === e.target.value);
      if (selected) {
        document.getElementById("job-title-input").value = selected.title;
        document.getElementById("industry-input").value = selected.industry;
        document.getElementById("job-desc-input").value = selected.description;
        App.showToast(`Loaded sample: ${selected.title}`, "info");
      }
    });
  },

  async loadSampleResume(type) {
    const filename = type === "pdf" ? "sample_backend_developer.pdf" : "sample_frontend_developer.docx";
    const path = `assets/sample_resumes/${filename}`;
    
    try {
      const response = await fetch(path);
      if (!response.ok) throw new Error("Sample file not accessible via static assets");
      const blob = await response.blob();
      const file = new File([blob], filename, { type: blob.type });
      this.selectFile(file);

      // Also set matching job description if empty
      const titleInput = document.getElementById("job-title-input");
      if (!titleInput.value) {
        const jdSelect = document.getElementById("sample-jd-select");
        if (type === "pdf" && jdSelect) {
          jdSelect.value = "backend_engineer";
          jdSelect.dispatchEvent(new Event("change"));
        } else if (jdSelect) {
          jdSelect.value = "fullstack_engineer";
          jdSelect.dispatchEvent(new Event("change"));
        }
      }
    } catch (e) {
      App.showToast("Could not load sample resume asset. Please upload a file manually.", "error");
    }
  },

  async runAnalysis() {
    const jobTitle = document.getElementById("job-title-input").value.trim();
    const industry = document.getElementById("industry-input").value.trim() || "Technology";
    const jobDescription = document.getElementById("job-desc-input").value.trim();

    if (!jobTitle) {
      App.showToast("Please enter a Target Job Title.", "warning");
      return;
    }
    if (!jobDescription || jobDescription.length < 20) {
      App.showToast("Please provide a Job Description (at least 20 characters).", "warning");
      return;
    }
    if (!this.currentFile) {
      App.showToast("Please upload a resume file (PDF or DOCX).", "warning");
      return;
    }

    this.setLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", this.currentFile);
      formData.append("job_title", jobTitle);
      formData.append("target_industry", industry);
      formData.append("job_description", jobDescription);

      const result = await API.postForm(CONFIG.ENDPOINTS.ANALYZE_UPLOAD, formData);
      this.currentAnalysis = result;
      this.renderResults(result);
      App.showToast("Resume analysis completed successfully!", "success");

      // Scroll smoothly to results
      document.getElementById("results-section").scrollIntoView({ behavior: "smooth" });
    } catch (err) {
      App.showToast(err.message || "Failed to analyze resume.", "error");
    } finally {
      this.setLoading(false);
    }
  },

  setLoading(isLoading) {
    const btn = document.getElementById("analyze-btn");
    const loader = document.getElementById("analysis-progress");
    
    if (isLoading) {
      if (btn) {
        btn.disabled = true;
        btn.classList.add("opacity-60", "cursor-not-allowed");
      }
      if (loader) loader.classList.remove("hidden");
    } else {
      if (btn) {
        btn.disabled = false;
        btn.classList.remove("opacity-60", "cursor-not-allowed");
      }
      if (loader) loader.classList.add("hidden");
    }
  },

  renderResults(data) {
    const resultsSection = document.getElementById("results-section");
    if (!resultsSection) return;
    resultsSection.classList.remove("hidden");

    // 1. Header info
    document.getElementById("res-job-title").textContent = data.job_title;
    document.getElementById("res-filename").textContent = `${data.filename} (${data.file_type.toUpperCase()})`;
    document.getElementById("res-date").textContent = new Date(data.created_at).toLocaleDateString(undefined, {
      year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
    });

    // 2. Score Gauge & Match Level
    const score = data.ats_score;
    document.getElementById("ats-score-text").textContent = score;

    const badge = document.getElementById("match-level-badge");
    badge.textContent = data.match_level.toUpperCase();
    if (score >= 85) {
      badge.className = "px-3 py-1 text-sm font-bold bg-emerald-100 text-emerald-800 rounded-full border border-emerald-300";
    } else if (score >= 70) {
      badge.className = "px-3 py-1 text-sm font-bold bg-indigo-100 text-indigo-800 rounded-full border border-indigo-300";
    } else if (score >= 50) {
      badge.className = "px-3 py-1 text-sm font-bold bg-amber-100 text-amber-800 rounded-full border border-amber-300";
    } else {
      badge.className = "px-3 py-1 text-sm font-bold bg-rose-100 text-rose-800 rounded-full border border-rose-300";
    }

    // Animate SVG Gauge
    const circle = document.getElementById("gauge-circle");
    if (circle) {
      const radius = 64;
      const circumference = 2 * Math.PI * radius;
      const offset = circumference - (score / 100) * circumference;
      circle.style.strokeDasharray = `${circumference} ${circumference}`;
      circle.style.strokeDashoffset = offset;

      if (score >= 85) circle.setAttribute("stroke", "#10b981");
      else if (score >= 70) circle.setAttribute("stroke", "#4f46e5");
      else if (score >= 50) circle.setAttribute("stroke", "#f59e0b");
      else circle.setAttribute("stroke", "#ef4444");
    }

    // 3. Breakdown Bars
    const b = data.score_breakdown;
    this.setBar("bar-skills", "val-skills", b.skills);
    this.setBar("bar-exp", "val-exp", b.experience);
    this.setBar("bar-kw", "val-kw", b.keywords);
    this.setBar("bar-edu", "val-edu", b.education);
    this.setBar("bar-fmt", "val-fmt", b.formatting);

    // 4. Skills Matrix
    this.renderSkillsMatrix(data.matched_skills, data.missing_skills, data.bonus_skills);

    // 5. Experience & Education
    this.renderExperience(data.experience_analysis);
    this.renderEducation(data.education_analysis);

    // 6. Keywords
    this.renderKeywords(data.keyword_analysis);

    // 7. AI Recommendations
    this.renderAIRecommendations(data.ai_recommendations);

    // 8. Interview Questions
    this.renderInterviewQuestions(data.interview_questions);
  },

  setBar(barId, valId, val) {
    const bar = document.getElementById(barId);
    const valEl = document.getElementById(valId);
    if (bar) bar.style.width = `${val}%`;
    if (valEl) valEl.textContent = `${val}%`;
  },

  renderSkillsMatrix(matched, missing, bonus) {
    const matchedContainer = document.getElementById("matched-skills-container");
    const missingContainer = document.getElementById("missing-skills-container");
    const bonusContainer = document.getElementById("bonus-skills-container");

    if (matchedContainer) {
      if (matched.length) {
        matchedContainer.innerHTML = matched.map(s => `
          <span class="inline-flex items-center gap-1.5 px-3 py-1 text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-lg shadow-sm">
            <svg class="w-3.5 h-3.5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
            ${s}
          </span>
        `).join("");
      } else {
        matchedContainer.innerHTML = '<span class="text-xs text-slate-400 italic">No direct skill matches detected.</span>';
      }
    }

    if (missingContainer) {
      if (missing.length) {
        missingContainer.innerHTML = missing.map(m => {
          const isCritical = m.priority === "Critical";
          const badgeClass = isCritical 
            ? "bg-rose-50 text-rose-700 border-rose-200" 
            : "bg-amber-50 text-amber-700 border-amber-200";
          const priorityBadge = isCritical
            ? `<span class="px-1.5 py-0.2 text-[10px] uppercase font-bold bg-rose-200 text-rose-800 rounded">Required</span>`
            : `<span class="px-1.5 py-0.2 text-[10px] uppercase font-bold bg-amber-200 text-amber-800 rounded">Recommended</span>`;

          return `
            <div class="p-2.5 rounded-lg border ${badgeClass} text-xs flex flex-col gap-1 shadow-sm">
              <div class="flex items-center justify-between font-semibold">
                <span class="text-sm font-bold text-slate-800">${m.skill}</span>
                ${priorityBadge}
              </div>
              <p class="text-slate-600 text-[11px] leading-relaxed mt-0.5">${m.tip}</p>
            </div>
          `;
        }).join("");
      } else {
        missingContainer.innerHTML = '<span class="text-xs text-emerald-600 font-medium">✓ Zero missing skills! Perfect match.</span>';
      }
    }

    if (bonusContainer) {
      if (bonus.length) {
        bonusContainer.innerHTML = bonus.map(s => `
          <span class="inline-flex items-center px-2.5 py-1 text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200 rounded-md">
            + ${s}
          </span>
        `).join("");
      } else {
        bonusContainer.innerHTML = '<span class="text-xs text-slate-400 italic">No additional peripheral skills found.</span>';
      }
    }
  },

  renderExperience(exp) {
    document.getElementById("exp-years").textContent = `${exp.estimated_years} Years`;
    document.getElementById("exp-seniority").textContent = exp.detected_seniority;
    document.getElementById("exp-verbs-score").textContent = `${exp.action_verb_score}%`;
    document.getElementById("exp-metrics-count").textContent = `${exp.quantifiable_metrics_count} Metrics`;
    document.getElementById("exp-verdict").textContent = exp.summary_verdict;

    const highlightsList = document.getElementById("exp-highlights");
    if (highlightsList && exp.highlights) {
      highlightsList.innerHTML = exp.highlights.map(h => `
        <li class="flex items-start gap-2 text-xs text-slate-700">
          <span class="text-indigo-600 font-bold">•</span>
          <span>${h}</span>
        </li>
      `).join("");
    }
  },

  renderEducation(edu) {
    document.getElementById("edu-highest").textContent = edu.highest_degree || "Technical Background";
    document.getElementById("edu-verdict").textContent = edu.verdict;

    const certsContainer = document.getElementById("edu-certs-container");
    if (certsContainer) {
      if (edu.certifications_found && edu.certifications_found.length) {
        certsContainer.innerHTML = edu.certifications_found.map(c => `
          <span class="px-2 py-0.5 text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200 rounded">
            🏅 ${c}
          </span>
        `).join("");
      } else {
        certsContainer.innerHTML = '<span class="text-xs text-slate-400 italic">No industry certifications detected.</span>';
      }
    }
  },

  renderKeywords(kw) {
    document.getElementById("kw-density-score").textContent = `${kw.density_score}%`;
    document.getElementById("kw-recommendation").textContent = kw.recommendation;

    const matchedKwEl = document.getElementById("kw-matched-chips");
    if (matchedKwEl && kw.matched_keywords) {
      matchedKwEl.innerHTML = kw.matched_keywords.map(k => `
        <span class="inline-flex items-center gap-1 px-2 py-0.5 text-xs rounded ${k.matched ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-slate-50 text-slate-500 border border-slate-200'}">
          ${k.matched ? '✓' : '×'} ${k.keyword} (${k.resume_count}/${k.jd_count})
        </span>
      `).join("");
    }

    const missingKwEl = document.getElementById("kw-missing-chips");
    if (missingKwEl && kw.missing_critical_keywords) {
      missingKwEl.innerHTML = kw.missing_critical_keywords.map(k => `
        <span class="px-2 py-0.5 text-xs font-medium bg-rose-50 text-rose-700 border border-rose-200 rounded">
          ${k}
        </span>
      `).join("");
    }
  },

  renderAIRecommendations(recs) {
    document.getElementById("ai-verdict").textContent = recs.overall_verdict;
    document.getElementById("ai-fit-badge").textContent = recs.fit_assessment;

    const rewritesContainer = document.getElementById("ai-bullet-rewrites");
    if (rewritesContainer && recs.bullet_point_rewrites) {
      rewritesContainer.innerHTML = recs.bullet_point_rewrites.map((r, i) => `
        <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs flex flex-col gap-3">
          <div class="flex items-center justify-between">
            <span class="font-bold text-slate-800 uppercase tracking-wide">Rewrite Example #${i + 1} (${r.framework})</span>
            <span class="text-[11px] text-indigo-600 font-semibold">ATS Optimized</span>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div class="p-3 bg-red-50/60 border border-red-200 rounded-lg">
              <span class="text-[10px] font-bold uppercase text-red-600 block mb-1">Original Bullet</span>
              <p class="text-slate-700 leading-relaxed italic">"${r.original}"</p>
            </div>
            <div class="p-3 bg-emerald-50/70 border border-emerald-200 rounded-lg">
              <span class="text-[10px] font-bold uppercase text-emerald-700 block mb-1">STAR High-Impact Rewrite</span>
              <p class="text-emerald-950 font-medium leading-relaxed">"${r.improved}"</p>
            </div>
          </div>
          <p class="text-slate-500 text-[11px] leading-relaxed"><strong class="text-slate-700">Rationale:</strong> ${r.rationale}</p>
        </div>
      `).join("");
    }

    const actionPlanList = document.getElementById("ai-action-plan");
    if (actionPlanList && recs.action_plan) {
      actionPlanList.innerHTML = recs.action_plan.map(step => `
        <li class="flex items-start gap-2 text-xs text-slate-700">
          <span class="text-emerald-600 font-bold">✓</span>
          <span>${step}</span>
        </li>
      `).join("");
    }
  },

  renderInterviewQuestions(questions) {
    const container = document.getElementById("interview-questions-container");
    if (!container) return;

    if (!questions || !questions.length) {
      container.innerHTML = '<p class="text-xs text-slate-400 italic">No interview questions generated.</p>';
      return;
    }

    container.innerHTML = questions.map((q, idx) => {
      const typeBadge = {
        "Technical": "bg-blue-100 text-blue-700 border-blue-200",
        "Gap-Probe": "bg-rose-100 text-rose-700 border-rose-200",
        "System Design": "bg-purple-100 text-purple-700 border-purple-200",
        "Behavioral": "bg-amber-100 text-amber-700 border-amber-200",
        "Situational": "bg-teal-100 text-teal-700 border-teal-200"
      }[q.type] || "bg-slate-100 text-slate-700 border-slate-200";

      return `
        <div class="p-4 bg-white border border-slate-200 rounded-xl shadow-sm hover:border-indigo-300 transition-all">
          <div class="flex items-center justify-between mb-2">
            <span class="px-2.5 py-0.5 text-xs font-bold rounded-full border ${typeBadge}">${q.type} Question</span>
            <span class="text-[11px] text-slate-400 font-mono">Q${idx + 1}</span>
          </div>
          <h4 class="text-sm font-bold text-slate-900 leading-snug mb-2">${q.question}</h4>
          <p class="text-xs text-slate-500 mb-3 leading-relaxed"><strong class="text-slate-700">Why Interviewers Ask:</strong> ${q.rationale}</p>
          <div class="p-3 bg-indigo-50/50 rounded-lg border border-indigo-100 text-xs">
            <span class="font-bold text-indigo-900 block mb-1">💡 Recommended Answer Strategy:</span>
            <p class="text-indigo-950 leading-relaxed">${q.answer_strategy}</p>
          </div>
        </div>
      `;
    }).join("");
  }
};
