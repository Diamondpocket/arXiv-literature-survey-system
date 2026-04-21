const state = {
  summary: null,
  pipelineStatus: null,
  pipelineHistory: [],
  cards: [],
  comparison: [],
  metricCache: {},
};

const $ = (id) => document.getElementById(id);

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function short(value, limit = 260) {
  const text = String(value || "unknown").trim();
  return text.length <= limit ? text : `${text.slice(0, limit - 3).trim()}...`;
}

function compactCategoryLabel(category, count = null) {
  const text = String(category || "unknown");
  const pairs = [
    ["Reliability, Safety, Privacy, and Security", "可靠性/安全/隐私"],
    ["Domain-Specific RAG Applications", "领域应用 RAG"],
    ["Agentic and Multi-Agent RAG", "智能体 RAG"],
    ["Multimodal and Visual RAG", "多模态/视觉 RAG"],
    ["Evaluation, Benchmarks, and Diagnostics", "评测/基准/诊断"],
    ["Knowledge Graph and Structured Knowledge RAG", "知识图谱/结构化 RAG"],
    ["Survey, Theory, and Governance", "综述/理论/治理"],
    ["Efficiency, Deployment, and On-Device RAG", "效率/部署/端侧"],
    ["Core Retrieval and Ranking Methods", "核心检索/排序"],
    ["General or Unspecified RAG", "通用/未细分"],
  ];
  const matched = pairs.find(([english]) => text.includes(english));
  const base = matched ? matched[1] : text.split(" (")[0];
  return count === null ? base : `${base} (${count})`;
}

function formatDateTime(value) {
  if (!value) return "unknown";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  }).format(date);
}

function formatShortDate(value) {
  if (!value) return "unknown";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value).slice(0, 19);
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(date);
}

function statusLabel(status) {
  const labels = {
    idle: "Idle",
    pending: "Pending",
    running: "Running",
    completed: "Completed",
    skipped: "Skipped",
    failed: "Failed",
  };
  return labels[status] || String(status || "unknown");
}

function statusLabelZh(status) {
  const labels = {
    idle: "待命",
    pending: "等待中",
    running: "运行中",
    completed: "已完成",
    skipped: "已跳过",
    failed: "失败",
  };
  return labels[status] || "未知";
}

function statusChip(label, status) {
  return `<span class="status-chip ${escapeHtml(status || "idle")}">${escapeHtml(label)}</span>`;
}

function safeStageLabel(stage) {
  if (!stage) return "No active stage";
  return `${stage.label_zh || stage.id} ${stage.label_en || ""}`.trim();
}

function eventStatus(event, status) {
  if (status.status === "running" && status.current_stage === event.stage_id) {
    return "running";
  }
  return status.status === "failed" && status.current_stage === event.stage_id ? "failed" : "completed";
}

async function getJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`${url}: ${response.status}`);
  return response.json();
}

async function getText(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`${url}: ${response.status}`);
  return response.text();
}

function markdownToHtml(markdown) {
  const lines = String(markdown || "").split(/\r?\n/);
  const html = [];
  let inList = false;

  function closeList() {
    if (inList) {
      html.push("</ul>");
      inList = false;
    }
  }

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line) {
      closeList();
      continue;
    }
    if (line.startsWith("# ")) {
      closeList();
      html.push(`<h1>${inlineMarkdown(line.slice(2))}</h1>`);
    } else if (line.startsWith("## ")) {
      closeList();
      html.push(`<h2>${inlineMarkdown(line.slice(3))}</h2>`);
    } else if (line.startsWith("### ")) {
      closeList();
      html.push(`<h3>${inlineMarkdown(line.slice(4))}</h3>`);
    } else if (line.startsWith("- ")) {
      if (!inList) {
        html.push("<ul>");
        inList = true;
      }
      html.push(`<li>${inlineMarkdown(line.slice(2))}</li>`);
    } else {
      closeList();
      html.push(`<p>${inlineMarkdown(line)}</p>`);
    }
  }

  closeList();
  return html.join("");
}

function inlineMarkdown(text) {
  return escapeHtml(text)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
}

function animateNumber(node, start, end) {
  const from = Number(start) || 0;
  const to = Number(end) || 0;
  if (from === to) {
    node.textContent = String(to);
    return;
  }

  const duration = 650;
  const startTime = performance.now();

  function frame(now) {
    const progress = Math.min((now - startTime) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const value = Math.round(from + (to - from) * eased);
    node.textContent = String(value);
    if (progress < 1) {
      requestAnimationFrame(frame);
    }
  }

  requestAnimationFrame(frame);
}

function renderMetrics() {
  const summary = state.summary || {};
  const model = (summary.model_counts || [])[0]?.[0] || "unknown";
  const weeklyFiles = (summary.weekly_files || []).length;
  const latestRun = state.pipelineHistory?.[0];
  const newCount = Number(latestRun?.fetch_stats?.new_count || 0);
  const metrics = [
    { id: "raw", label: "Raw papers", value: summary.papers_count || 0, numeric: true },
    { id: "cards", label: "Paper cards", value: summary.cards_count || 0, numeric: true },
    { id: "comparison", label: "Comparison rows", value: summary.comparison_rows || 0, numeric: true },
    { id: "new_fetch", label: "New in latest run", value: newCount, numeric: true },
    { id: "model", label: "Primary model", value: model, numeric: false },
    { id: "archives", label: "Weekly archives", value: weeklyFiles, numeric: true },
  ];

  $("metrics").innerHTML = metrics.map((metric) => `
    <div class="metric">
      <strong class="metric-value" data-id="${escapeHtml(metric.id)}" data-numeric="${metric.numeric ? "1" : "0"}">${escapeHtml(metric.numeric ? "0" : String(metric.value))}</strong>
      <span>${escapeHtml(metric.label)}</span>
    </div>
  `).join("");

  $("metrics").querySelectorAll(".metric-value").forEach((node) => {
    const id = node.dataset.id;
    const metric = metrics.find((item) => item.id === id);
    if (!metric) return;
    if (metric.numeric) {
      const previous = state.metricCache[id] ?? 0;
      animateNumber(node, previous, metric.value);
      state.metricCache[id] = metric.value;
    } else {
      node.textContent = String(metric.value);
      state.metricCache[id] = metric.value;
    }
  });
}

function renderHeroStatus() {
  const summary = state.summary || {};
  const status = state.pipelineStatus || {};
  const latestRun = state.pipelineHistory?.[0] || {};
  const currentStage = (status.stages || []).find((stage) => stage.id === status.current_stage);
  const weeklyDate = summary.weekly_files?.[0]?.date || "not generated";
  const cardsGenerated = latestRun.cards_stats?.generated_count ?? status.stats?.cards?.generated_count ?? 0;
  const papersFetched = latestRun.fetch_stats?.new_count ?? status.stats?.fetch?.new_count ?? 0;

  $("heroStatusGrid").innerHTML = [
    {
      label: "Run status",
      value: `${statusLabelZh(status.status || "idle")} / ${statusLabel(status.status || "idle")}`,
      note: `Last update ${formatShortDate(status.updated_at)}`,
    },
    {
      label: "Active stage",
      value: currentStage ? currentStage.label_zh : "当前无活动阶段",
      note: currentStage ? currentStage.label_en : "No active stage",
    },
    {
      label: "Latest delta",
      value: `${papersFetched} papers · ${cardsGenerated} cards`,
      note: "Latest run changes",
    },
    {
      label: "Latest digest",
      value: weeklyDate,
      note: `${summary.cards_count || 0} structured cards available`,
    },
  ].map((item) => `
    <article class="hero-stat-card">
      <span class="hero-stat-label">${escapeHtml(item.label)}</span>
      <strong class="hero-stat-value">${escapeHtml(item.value)}</strong>
      <span class="hero-stat-note">${escapeHtml(item.note)}</span>
    </article>
  `).join("");
}

function renderFilters() {
  const select = $("categorySelect");
  const current = select.value;
  const categoryRows = state.summary?.category_counts || [];
  const categories = categoryRows.map(([name]) => name).filter(Boolean);
  select.innerHTML = `<option value="">All categories</option>` + categoryRows
    .filter(([category]) => category)
    .map(([category, count]) => {
      const label = compactCategoryLabel(category, count);
      return `<option value="${escapeHtml(category)}" title="${escapeHtml(category)}">${escapeHtml(label)}</option>`;
    })
    .join("");
  select.value = categories.includes(current) ? current : "";
}

function stageProgressText(stage) {
  const current = Number(stage.progress_current || 0);
  const total = Number(stage.progress_total || 0);
  if (total > 0) return `${current} / ${total}`;
  if (stage.status === "completed") return "done";
  if (stage.status === "skipped") return "skipped";
  return "waiting";
}

function renderStageStrip(stages, updatedAt) {
  $("stageStrip").innerHTML = (stages || []).map((stage) => `
    <article class="stage-card ${escapeHtml(stage.status || "pending")}">
      <div class="stage-header">
        <h3 class="stage-title">${escapeHtml(stage.label_zh)}<span>${escapeHtml(stage.label_en)}</span></h3>
        <span class="stage-dot" aria-hidden="true"></span>
      </div>
      <p class="stage-detail">${escapeHtml(stage.detail || "Waiting for stage execution.")}</p>
      <div class="progress-track"><div class="progress-bar" style="width:${escapeHtml(String(stage.progress_percent || 0))}%"></div></div>
      <p class="stage-count">Progress / 进度: ${escapeHtml(stageProgressText(stage))} · ${escapeHtml(String(stage.progress_percent || 0))}%</p>
      <p class="stage-time">${escapeHtml(stage.status === "running" ? "Started" : "Updated")} / ${escapeHtml(formatShortDate(stage.finished_at || stage.started_at || updatedAt))}</p>
    </article>
  `).join("");
}

function renderActivityFeed(status) {
  const events = status.recent_events || [];
  if (!events.length) {
    $("activityFeed").innerHTML = `<div class="empty-state">还没有事件流记录。运行一次 pipeline 后，这里会按时间显示抓取、卡片生成和综述产物更新。</div>`;
    return;
  }

  $("activityFeed").innerHTML = events.map((event) => {
    const tone = eventStatus(event, status);
    const payloadTitle = event.payload?.title || event.payload?.arxiv_id || "";
    return `
      <div class="log-item ${escapeHtml(tone)}">
        <div class="log-head">
          <p class="log-title">${escapeHtml(event.stage_label_zh || event.stage_id)} <span>${escapeHtml(event.stage_label_en || "")}</span></p>
          ${statusChip(`${statusLabelZh(tone)} ${statusLabel(tone)}`, tone)}
        </div>
        <p class="log-message">${escapeHtml(event.message || "No message")}</p>
        ${payloadTitle ? `<p class="log-meta">${escapeHtml(payloadTitle)}</p>` : ""}
        <p class="log-meta">${escapeHtml(formatDateTime(event.time))}</p>
      </div>
    `;
  }).join("");
}

function renderRuntimeSnapshot(status, summary) {
  const latestRun = state.pipelineHistory?.[0] || {};
  const fetchStats = status.stats?.fetch || latestRun.fetch_stats || {};
  const cardStats = status.stats?.cards || latestRun.cards_stats || {};

  $("activitySummary").innerHTML = `
    <div class="summary-grid">
      <div class="summary-tile">
        <strong>${escapeHtml(String(summary.papers_count || 0))}</strong>
        <span>Raw papers</span>
      </div>
      <div class="summary-tile">
        <strong>${escapeHtml(String(summary.cards_count || 0))}</strong>
        <span>Structured cards</span>
      </div>
      <div class="summary-tile">
        <strong>${escapeHtml(String(fetchStats.new_count || 0))}</strong>
        <span>New papers this run</span>
      </div>
      <div class="summary-tile">
        <strong>${escapeHtml(String(cardStats.generated_count || 0))}</strong>
        <span>New cards this run</span>
      </div>
      <div class="summary-tile">
        <strong>${escapeHtml(formatShortDate(status.started_at || status.updated_at))}</strong>
        <span>Run start</span>
      </div>
      <div class="summary-tile">
        <strong>${escapeHtml(formatShortDate(status.finished_at || status.updated_at))}</strong>
        <span>Latest transition</span>
      </div>
    </div>
  `;
}

function renderNewPapers(status, summary) {
  const papers = status.recent_new_papers || [];
  const fallback = summary.latest_papers || [];
  const source = papers.length ? papers : fallback;
  const title = papers.length ? "本轮新增论文" : "本轮无新增，展示最近样本";

  if (!source.length) {
    $("newPapersPanel").innerHTML = `<div class="empty-state">当前还没有可展示的抓取结果。等 fetch 阶段执行后，这里会列出新增论文。</div>`;
    return;
  }

  $("newPapersPanel").innerHTML = `
    <div class="panel-note">${escapeHtml(title)}</div>
    ${source.slice(0, 10).map((paper) => `
      <article class="new-paper-item">
        <p class="paper-title">${escapeHtml(paper.title || "unknown")}</p>
        <p class="paper-meta">${escapeHtml((paper.published || "").slice(0, 10) || "unknown")} · ${escapeHtml(paper.arxiv_id || "unknown")}</p>
        <p class="paper-desc">${escapeHtml((paper.categories || []).join(", ") || "No categories")}</p>
        <p class="paper-meta"><a class="paper-link" href="${escapeHtml(paper.entry_url || "#")}" target="_blank" rel="noreferrer">Open arXiv</a></p>
      </article>
    `).join("")}
  `;
}

function renderHistory(history) {
  if (!history.length) {
    $("historyPanel").innerHTML = `<div class="empty-state">还没有运行历史。等 pipeline 完整跑过一次，这里会按时间记录每天或每周的执行情况。</div>`;
    return;
  }

  $("historyPanel").innerHTML = history.slice(0, 10).map((run) => {
    const fetchStats = run.fetch_stats || {};
    const cardsStats = run.cards_stats || {};
    const weeklyStats = run.weekly_stats || {};
    const digestName = String(weeklyStats.archive_path || "").split(/[\\/]/).pop() || "not generated";
    return `
      <article class="run-item">
        <div class="run-head">
          <p class="run-title">${escapeHtml(formatDateTime(run.started_at || run.updated_at))}</p>
          ${statusChip(`${statusLabelZh(run.status)} ${statusLabel(run.status)}`, run.status)}
        </div>
        <p class="run-desc">新增论文 ${escapeHtml(String(fetchStats.new_count || 0))} 篇，新增卡片 ${escapeHtml(String(cardsStats.generated_count || 0))} 张。</p>
        <p class="run-meta">Query: ${escapeHtml(short(run.query || "unknown", 88))}</p>
        <p class="run-meta">Digest: ${escapeHtml(digestName)}</p>
      </article>
    `;
  }).join("");
}

function renderMonitor() {
  const status = state.pipelineStatus || {
    status: "idle",
    message: "Waiting for pipeline status.",
    stages: [],
    updated_at: "",
    current_stage: null,
    stats: {},
  };
  const summary = state.summary || {};
  const currentStage = (status.stages || []).find((stage) => stage.id === status.current_stage);

  $("monitorHeadline").textContent = status.message || "Pipeline status unavailable.";
  $("visualCaption").innerHTML = `
    ${statusChip(`${statusLabelZh(status.status)} ${statusLabel(status.status)}`, status.status)}
    <strong style="display:block;margin-top:6px;">${escapeHtml(status.topic || "Literature Survey Pipeline")}</strong>
    <span style="display:block;color:#61666b;margin-top:4px;">最后更新 / Last update: ${escapeHtml(formatDateTime(status.updated_at))}</span>
  `;

  $("monitorMeta").innerHTML = [
    statusChip(`${statusLabelZh(status.status)} ${statusLabel(status.status)}`, status.status),
    statusChip(safeStageLabel(currentStage), currentStage?.status || "idle"),
    statusChip(`Last update ${formatShortDate(status.updated_at)}`, "idle"),
  ].join("");

  renderHeroStatus();
  renderStageStrip(status.stages || [], status.updated_at);
  renderActivityFeed(status);
  renderRuntimeSnapshot(status, summary);
  renderNewPapers(status, summary);
  renderHistory(state.pipelineHistory || []);
}

function renderCards() {
  const total = state.summary?.cards_count || state.cards.length;
  $("paperCount").textContent = `${state.cards.length} / ${total} papers`;
  if (!state.cards.length) {
    $("cardsList").innerHTML = `<div class="paper-card"><h3>No cards yet</h3><p>Run the pipeline to generate structured paper cards.</p></div>`;
    return;
  }

  $("cardsList").innerHTML = state.cards
    .map((card) => {
      const confidence = String(card.confidence_level || "unknown").toLowerCase();
      const macroCategory = card.macro_category || card.best_fit_category || "unknown";
      const sourceCategory = card.best_fit_category || "unknown";
      const compactMacro = compactCategoryLabel(macroCategory);
      const sourcePill = sourceCategory !== macroCategory
        ? `<span class="pill" title="${escapeHtml(sourceCategory)}">fine: ${escapeHtml(short(sourceCategory, 34))}</span>`
        : "";
      return `
        <article class="paper-card">
          <h3>${escapeHtml(card.title)}</h3>
          <div class="meta">
            <span class="pill category" title="${escapeHtml(macroCategory)}">${escapeHtml(compactMacro)}</span>
            ${sourcePill}
            <span class="pill confidence-${escapeHtml(confidence)}">${escapeHtml(confidence)}</span>
            <span class="pill">${escapeHtml((card.published || "").slice(0, 10) || "unknown")}</span>
            <span class="pill">${escapeHtml(card.model || "unknown")}</span>
          </div>
          <div class="paper-grid">
            ${field("Problem", card.problem)}
            ${field("Key idea", card.key_idea)}
            ${field("Method", card.method)}
            ${field("Dataset / scenario", card.dataset_or_scenario)}
            ${field("Metrics", card.metrics)}
            ${field("Results", card.results_summary)}
          </div>
          <div class="links">
            <a href="${escapeHtml(card.source_url || "#")}" target="_blank" rel="noreferrer">arXiv</a>
            <a href="${escapeHtml(card.pdf_url || "#")}" target="_blank" rel="noreferrer">PDF</a>
          </div>
        </article>
      `;
    })
    .join("");
}

function field(label, value) {
  return `<div class="field"><strong>${escapeHtml(label)}</strong><p>${escapeHtml(short(value))}</p></div>`;
}

function renderComparison() {
  $("comparisonCount").textContent = `${state.comparison.length} rows`;
  $("comparisonBody").innerHTML = state.comparison
    .slice(0, 80)
    .map((row) => `
      <tr>
        <td>${escapeHtml(row.title)}</td>
        <td>${escapeHtml(short(row.method, 180))}</td>
        <td>${escapeHtml(row.complexity)}</td>
        <td>${escapeHtml(short(row.scenario, 160))}</td>
        <td>${escapeHtml(row.data_driven)}</td>
        <td>${escapeHtml(row.category_bilingual || row.category)}</td>
      </tr>
    `)
    .join("");
}

async function loadCards() {
  const params = new URLSearchParams();
  const q = $("searchInput").value.trim();
  const category = $("categorySelect").value;
  const confidence = $("confidenceSelect").value;
  if (q) params.set("q", q);
  if (category) params.set("category", category);
  if (confidence) params.set("confidence", confidence);
  params.set("limit", "120");
  state.cards = await getJson(`/api/cards?${params.toString()}`);
  renderCards();
}

async function refreshReportsAndCards() {
  const [comparison, weekly, taxonomy, trend] = await Promise.all([
    getJson("/api/comparison"),
    getText("/api/weekly"),
    getText("/api/taxonomy"),
    getText("/api/trend"),
  ]);
  state.comparison = comparison;
  renderComparison();
  $("weeklyPanel").innerHTML = markdownToHtml(weekly);
  $("taxonomyPanel").innerHTML = markdownToHtml(taxonomy);
  $("trendPanel").innerHTML = markdownToHtml(trend);
  await loadCards();
}

async function loadAll() {
  const [summary, pipelineStatus, pipelineHistory] = await Promise.all([
    getJson("/api/summary"),
    getJson("/api/pipeline_status"),
    getJson("/api/pipeline_history"),
  ]);
  state.summary = summary;
  state.pipelineStatus = pipelineStatus;
  state.pipelineHistory = pipelineHistory;
  renderMetrics();
  renderFilters();
  renderMonitor();
  await refreshReportsAndCards();
}

async function pollLive() {
  try {
    const [summary, pipelineStatus, pipelineHistory] = await Promise.all([
      getJson("/api/summary"),
      getJson("/api/pipeline_status"),
      getJson("/api/pipeline_history"),
    ]);

    const previousSummary = state.summary;
    const previousStatus = state.pipelineStatus;
    const previousHistoryHead = state.pipelineHistory?.[0]?.run_id;
    const currentHistoryHead = pipelineHistory?.[0]?.run_id;
    const shouldReload =
      !previousSummary ||
      summary.cards_count !== previousSummary.cards_count ||
      summary.comparison_rows !== previousSummary.comparison_rows ||
      summary.latest_generated !== previousSummary.latest_generated ||
      previousStatus?.updated_at !== pipelineStatus.updated_at ||
      previousHistoryHead !== currentHistoryHead;

    state.summary = summary;
    state.pipelineStatus = pipelineStatus;
    state.pipelineHistory = pipelineHistory;
    renderMetrics();
    renderFilters();
    renderMonitor();

    if (shouldReload) {
      await refreshReportsAndCards();
    }
  } catch (error) {
    console.warn("Polling failed:", error);
  }
}

function debounce(fn, delay = 220) {
  let timer = null;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

$("refreshButton").addEventListener("click", loadAll);
$("searchInput").addEventListener("input", debounce(loadCards));
$("categorySelect").addEventListener("change", loadCards);
$("confidenceSelect").addEventListener("change", loadCards);

loadAll()
  .then(() => {
    setInterval(pollLive, 4000);
  })
  .catch((error) => {
    console.error(error);
    $("monitorHeadline").textContent = `Dashboard failed to load: ${error.message}`;
    $("cardsList").innerHTML = `<div class="paper-card"><h3>Dashboard failed to load</h3><p>${escapeHtml(error.message)}</p></div>`;
  });
