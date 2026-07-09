(function () {
  const form = document.getElementById("analyze-form");
  const fileInput = document.getElementById("resume-file");
  const dropzone = document.getElementById("dropzone");
  const dropzoneFilename = document.getElementById("dropzone-filename");
  const submitBtn = document.getElementById("submit-btn");

  const empty = document.getElementById("report-empty");
  const loading = document.getElementById("report-loading");
  const errorBox = document.getElementById("report-error");
  const errorMessage = document.getElementById("error-message");
  const content = document.getElementById("report-content");
  const loadingText = document.getElementById("loading-text");

  const LOADING_MESSAGES = [
    "Reading document…",
    "Extracting skills and sections…",
    "Scoring against ATS heuristics…",
    "Drafting interview questions…",
  ];

  // ---- Dropzone interactions ----
  fileInput.addEventListener("change", () => {
    if (fileInput.files.length) {
      dropzoneFilename.textContent = fileInput.files[0].name;
    }
  });

  ["dragover", "dragenter"].forEach((evt) =>
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.add("dragover");
    })
  );
  ["dragleave", "drop"].forEach((evt) =>
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.remove("dragover");
    })
  );
  dropzone.addEventListener("drop", (e) => {
    const files = e.dataTransfer.files;
    if (files.length) {
      fileInput.files = files;
      dropzoneFilename.textContent = files[0].name;
    }
  });

  // ---- Form submit ----
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    if (!fileInput.files.length) {
      showError("Please choose a resume file first.");
      return;
    }

    setState("loading");
    submitBtn.disabled = true;
    let msgIndex = 0;
    loadingText.textContent = LOADING_MESSAGES[0];
    const cycleId = setInterval(() => {
      msgIndex = (msgIndex + 1) % LOADING_MESSAGES.length;
      loadingText.textContent = LOADING_MESSAGES[msgIndex];
    }, 1800);

    const formData = new FormData();
    formData.append("resume", fileInput.files[0]);
    const jd = document.getElementById("job-description").value.trim();
    if (jd) formData.append("job_description", jd);

    try {
      const res = await fetch("/api/analyze", { method: "POST", body: formData });
      const data = await res.json();

      if (!res.ok) {
        showError(data.error || "Something went wrong. Please try again.");
        return;
      }

      renderReport(data.result);
      setState("content");
    } catch (err) {
      showError("Couldn't reach the server. Check your connection and try again.");
    } finally {
      clearInterval(cycleId);
      submitBtn.disabled = false;
    }
  });

  function setState(state) {
    empty.classList.add("hidden");
    loading.classList.add("hidden");
    errorBox.classList.add("hidden");
    content.classList.add("hidden");
    if (state === "loading") loading.classList.remove("hidden");
    if (state === "error") errorBox.classList.remove("hidden");
    if (state === "content") content.classList.remove("hidden");
    if (state === "empty") empty.classList.remove("hidden");
  }

  function showError(msg) {
    errorMessage.textContent = msg;
    setState("error");
  }

  // ---- Rendering ----
  function renderReport(r) {
    document.getElementById("candidate-name").textContent = r.candidate_name || "Candidate";
    document.getElementById("experience-level").textContent = r.estimated_experience_level || "";
    document.getElementById("score-reasoning").textContent = r.ats_score_reasoning || "";
    document.getElementById("overall-summary").textContent = r.overall_summary || "";

    setDial(clampScore(r.ats_score));

    renderTags("skills-technical", r.extracted_skills && r.extracted_skills.technical);
    renderTags("skills-tools", r.extracted_skills && r.extracted_skills.tools_and_technologies);
    renderTags("skills-soft", r.extracted_skills && r.extracted_skills.soft);
    renderTags("keyword-gaps", r.keyword_gaps, true);

    renderPlainList("sections-found", r.sections_found);
    renderPlainList("sections-missing", r.missing_sections);
    renderPlainList("strengths-list", r.strengths, "check-list");

    renderWeakSections(r.weak_sections);
    renderSuggestions(r.improvement_suggestions);
    renderQuestions(r.interview_questions);
  }

  function clampScore(score) {
    const n = Number(score);
    if (Number.isNaN(n)) return 0;
    return Math.max(0, Math.min(100, n));
  }

  function setDial(score) {
    document.getElementById("dial-score").textContent = score;

    // Arc: full path length ~ 283 (approx for this path geometry)
    const fill = document.getElementById("dial-fill");
    const circumference = 283;
    const offset = circumference - (circumference * score) / 100;
    // Slight delay so CSS transition is visible
    requestAnimationFrame(() => {
      fill.style.strokeDashoffset = offset;
    });

    let color = "var(--bad)";
    if (score >= 75) color = "var(--good)";
    else if (score >= 45) color = "var(--warn)";
    fill.style.stroke = color;

    // Needle sweeps -90deg (score 0) to +90deg (score 100)
    const angle = -90 + (180 * score) / 100;
    const needle = document.getElementById("dial-needle");
    requestAnimationFrame(() => {
      needle.style.transform = `rotate(${angle}deg)`;
    });
  }

  function renderTags(elementId, items, isGap) {
    const el = document.getElementById(elementId);
    el.innerHTML = "";
    if (!items || !items.length) {
      el.innerHTML = '<span class="empty-note">None detected</span>';
      return;
    }
    items.forEach((item) => {
      const span = document.createElement("span");
      span.className = "tag" + (isGap ? " gap" : "");
      span.textContent = item;
      el.appendChild(span);
    });
  }

  function renderPlainList(elementId, items, extraClass) {
    const el = document.getElementById(elementId);
    el.innerHTML = "";
    if (extraClass) el.classList.add(extraClass);
    if (!items || !items.length) {
      el.innerHTML = '<li class="empty-note">None</li>';
      return;
    }
    items.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      el.appendChild(li);
    });
  }

  function renderWeakSections(items) {
    const el = document.getElementById("weak-sections");
    el.innerHTML = "";
    if (!items || !items.length) {
      el.innerHTML = '<p class="empty-note">No significantly weak sections detected.</p>';
      return;
    }
    items.forEach((item) => {
      const div = document.createElement("div");
      div.className = "weak-item";
      const h4 = document.createElement("h4");
      h4.textContent = item.section || "Section";
      const issue = document.createElement("p");
      issue.className = "issue";
      issue.textContent = item.issue || "";
      const fix = document.createElement("p");
      fix.className = "fix";
      fix.textContent = item.suggestion || "";
      div.appendChild(h4);
      div.appendChild(issue);
      div.appendChild(fix);
      el.appendChild(div);
    });
  }

  function renderSuggestions(items) {
    const el = document.getElementById("suggestions-list");
    el.innerHTML = "";
    if (!items || !items.length) {
      el.innerHTML = '<li class="empty-note">No specific suggestions returned.</li>';
      return;
    }
    items.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      el.appendChild(li);
    });
  }

  function renderQuestions(questions) {
    ["technical", "behavioral", "role_specific"].forEach((key) => {
      const el = document.getElementById(`questions-${key}`);
      el.innerHTML = "";
      const list = (questions && questions[key]) || [];
      if (!list.length) {
        el.innerHTML = '<li class="empty-note">None generated</li>';
        return;
      }
      list.forEach((q) => {
        const li = document.createElement("li");
        li.textContent = q;
        el.appendChild(li);
      });
    });
  }

  // ---- Tabs ----
  document.getElementById("question-tabs").addEventListener("click", (e) => {
    const btn = e.target.closest(".tab-btn");
    if (!btn) return;
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    const tab = btn.dataset.tab;
    ["technical", "behavioral", "role_specific"].forEach((key) => {
      document.getElementById(`questions-${key}`).classList.toggle("hidden", key !== tab);
    });
  });
})();
