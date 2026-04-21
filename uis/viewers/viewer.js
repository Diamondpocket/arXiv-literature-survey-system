const viewerState = {
  rawPapers: [],
  cards: [],
  comparison: [],
  taxonomy: "",
  trend: "",
  weekly: "",
  pipelineStatus: null,
  pipelineHistory: [],
  loadedFiles: [],
};

const viewerFileHints = {
  papersRaw: ["dats/raws/papers_raw.json", "papers_raw.json"],
  cards: ["dats/cards/paper_cards.jsonl", "paper_cards.jsonl"],
  comparison: ["outs/tables/comparison_table.csv", "comparison_table.csv"],
  taxonomy: ["outs/taxons/taxonomy.md", "taxonomy.md"],
  trend: ["outs/trends/trend_analysis.md", "trend_analysis.md"],
  weekly: ["outs/digests/weekly_digest_latest.md", "weekly_digest_latest.md"],
  pipelineStatus: ["outs/stats/pipeline_status.json", "pipeline_status.json"],
  pipelineHistory: ["outs/stats/pipeline_history.json", "pipeline_history.json"],
};

const STAGE_META = {
  fetch: { zh: "抓取 arXiv", en: "Fetch arXiv" },
  cards: { zh: "结构化抽取", en: "Generate Cards" },
  analysis: { zh: "分类与对比分析", en: "Cluster Analysis" },
  weekly: { zh: "生成每周综述", en: "Weekly Digest" },
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

function shortText(value, limit = 220) {
  const text = String(value || "unknown").trim();
  return text.length <= limit ? text : `${text.slice(0, limit - 3).trim()}...`;
}

function normalizePath(file) {
  const source = file.webkitRelativePath || file.name || "";
  return source.replaceAll("\\", "/");
}

function detectKind(path) {
  const lower = path.toLowerCase();
  for (const [kind, candidates] of Object.entries(viewerFileHints)) {
    if (candidates.some((candidate) => lower.endsWith(candidate.toLowerCase()))) {
      return kind;
    }
  }
  return null;
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

function csvToRows(text) {
  const rows = [];
  let current = "";
  let row = [];
  let inQuotes = false;

  function pushCell() {
    row.push(current);
    current = "";
  }

  function pushRow() {
    if (row.length || current.length) {
      pushCell();
      rows.push(row);
    }
    row = [];
  }

  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    const next = text[index + 1];

    if (char === '"') {
      if (inQuotes && next === '"') {
        current += '"';
        index += 1;
      } else {
        inQuotes = !inQuotes;
      }
      continue;
    }

    if (char === "," && !inQuotes) {
      pushCell();
      continue;
    }

    if ((char === "\n" || char === "\r") && !inQuotes) {
      if (char === "\r" && next === "\n") index += 1;
      pushRow();
      continue;
    }

    current += char;
  }

  if (current.length || row.length) {
    pushRow();
  }

  if (!rows.length) return [];
  const [header, ...body] = rows;
  return body
    .filter((entry) => entry.some((cell) => String(cell || "").trim()))
    .map((entry) => Object.fromEntries(header.map((key, index) => [key, entry[index] ?? ""])));
}

function parseJsonl(text) {
  return String(text || "")
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      try {
        return JSON.parse(line);
      } catch (error) {
        return null;
      }
    })
    .filter((item) => item && typeof item === "object");
}

function inlineMarkdown(text) {
  return escapeHtml(text)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
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
      continue;
    }
    if (line.startsWith("## ")) {
      closeList();
      html.push(`<h2>${inlineMarkdown(line.slice(3))}</h2>`);
      continue;
    }
    if (line.startsWith("### ")) {
      closeList();
      html.push(`<h3>${inlineMarkdown(line.slice(4))}</h3>`);
      continue;
    }
    if (line.startsWith("- ")) {
      if (!inList) {
        html.push("<ul>");
        inList = true;
      }
      html.push(`<li>${inlineMarkdown(line.slice(2))}</li>`);
      continue;
    }
    closeList();
    html.push(`<p>${inlineMarkdown(line)}</p>`);
  }

  closeList();
  return html.join("");
}

function readFileText(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result || ""));
    reader.onerror = () => reject(reader.error || new Error(`Failed to read ${file.name}`));
    reader.readAsText(file, "utf-8");
  });
}

async function loadFiles(fileList) {
  const files = Array.from(fileList || []);
  const mapped = {};
  const loadedFiles = [];

  for (const file of files) {
    const relativePath = normalizePath(file);
    const kind = detectKind(relativePath);
    loadedFiles.push({
      name: file.name,
      relativePath,
      size: file.size,
      kind: kind || "unused",
    });
    if (!kind || mapped[kind]) continue;
    mapped[kind] = file;
  }

  viewerState.loadedFiles = loadedFiles;
  viewerState.rawPapers = [];
  viewerState.cards = [];
  viewerState.comparison = [];
  viewerState.taxonomy = "";
  viewerState.trend = "";
  viewerState.weekly = "";
  viewerState.pipelineStatus = null;
  viewerState.pipelineHistory = [];

  if (mapped.papersRaw) {
    viewerState.rawPapers = JSON.parse(await readFileText(mapped.papersRaw));
  }
  if (mapped.cards) {
    viewerState.cards = parseJsonl(await readFileText(mapped.cards));
  }
  if (mapped.comparison) {
    viewerState.comparison = csvToRows(await readFileText(mapped.comparison));
  }
  if (mapped.taxonomy) {
    viewerState.taxonomy = await readFileText(mapped.taxonomy);
  }
  if (mapped.trend) {
    viewerState.trend = await readFileText(mapped.trend);
  }
  if (mapped.weekly) {
    viewerState.weekly = await readFileText(mapped.weekly);
  }
  if (mapped.pipelineStatus) {
    viewerState.pipelineStatus = JSON.parse(await readFileText(mapped.pipelineStatus));
  }
  if (mapped.pipelineHistory) {
    viewerState.pipelineHistory = JSON.parse(await readFileText(mapped.pipelineHistory));
  }
}

function currentSummary() {
  const status = viewerState.pipelineStatus || {};
  const primaryModel =
    viewerState.cards[0]?.model || viewerState.cards.find((item) => item.model)?.model || "unknown";
  return {
    rawCount: Array.isArray(viewerState.rawPapers) ? viewerState.rawPapers.length : 0,
    cardCount: viewerState.cards.length,
    comparisonCount: viewerState.comparison.length,
    model: primaryModel,
    status: status.status || "idle",
    updatedAt: status.updated_at || null,
  };
}

function renderLoadSummary() {
  const used = viewerState.loadedFiles.filter((item) => item.kind !== "unused");
  const unused = viewerState.loadedFiles.filter((item) => item.kind === "unused");
  $("viewerLoadSummary").textContent = used.length
    ? `已载入 ${used.length} 个识别文件，未使用 ${unused.length} 个文件。`
    : "尚未识别到目标文件。建议选择项目根目录，或至少包含 dats 与 outs。";
}

function renderLoadedFiles() {
  const target = $("loadedFilesPanel");
  if (!viewerState.loadedFiles.length) {
    target.innerHTML = `<p class="empty-state">还没有导入任何文件。</p>`;
    return;
  }

  target.innerHTML = viewerState.loadedFiles
    .map(
      (item) => `
        <div class="loaded-file-item ${item.kind === "unused" ? "unused" : ""}">
          <strong>${escapeHtml(item.name)}</strong>
          <span>${escapeHtml(item.relativePath || item.name)}</span>
          <span>${escapeHtml(item.kind)}</span>
        </div>
      `,
    )
    .join("");
}

function renderViewerMetrics() {
  const summary = currentSummary();
  const metrics = [
    { label: "Raw papers", value: summary.rawCount },
    { label: "Paper cards", value: summary.cardCount },
    { label: "Comparison rows", value: summary.comparisonCount },
    { label: "Primary model", value: summary.model },
    { label: "Workflow status", value: summary.status },
    { label: "Updated at", value: summary.updatedAt ? formatDateTime(summary.updatedAt) : "unknown" },
  ];

  $("viewerMetrics").innerHTML = metrics
    .map(
      (metric) => `
        <div class="metric">
          <strong class="metric-value">${escapeHtml(metric.value)}</strong>
          <span>${escapeHtml(metric.label)}</span>
        </div>
      `,
    )
    .join("");
}

function renderStatusBand() {
  const status = viewerState.pipelineStatus;
  const headline = $("viewerMonitorHeadline");
  const meta = $("viewerMonitorMeta");
  const strip = $("viewerStageStrip");

  if (!status) {
    headline.textContent = "未加载 pipeline_status.json，当前展示的是静态结果文件视图。";
    meta.innerHTML = `<span class="status-chip idle">No live status</span>`;
    strip.innerHTML = `<div class="empty-state">如果导入 outs/stats/pipeline_status.json，这里会显示完整阶段状态。</div>`;
    return;
  }

  headline.textContent = status.message || "Pipeline status loaded.";
  meta.innerHTML = [
    `<span class="status-chip ${escapeHtml(status.status || "idle")}">${escapeHtml(status.status || "idle")}</span>`,
    `<span class="status-pill">Run ID: ${escapeHtml(status.run_id || "unknown")}</span>`,
    `<span class="status-pill">Updated: ${escapeHtml(formatDateTime(status.updated_at))}</span>`,
  ].join("");

  const fallbackStages = Object.keys(STAGE_META).map((stageId) => ({
    id: stageId,
    status: stageId === status.current_stage ? "running" : "pending",
    detail: "",
    progress_percent: stageId === status.current_stage ? 50 : 0,
  }));
  const stages = Array.isArray(status.stages) && status.stages.length ? status.stages : fallbackStages;

  strip.innerHTML = stages
    .map((stage) => {
      const labels = STAGE_META[stage.id] || { zh: stage.label_zh || stage.id, en: stage.label_en || stage.id };
      const percent = Number(stage.progress_percent ?? (stage.status === "completed" ? 100 : 0));
      return `
        <article class="stage-card ${escapeHtml(stage.status || "pending")}">
          <div class="stage-card-top">
            <strong>${escapeHtml(labels.zh)}</strong>
            <span>${escapeHtml(stage.status || "pending")}</span>
          </div>
          <div class="stage-card-sub">${escapeHtml(labels.en)}</div>
          <div class="stage-progress"><span style="width:${Math.max(0, Math.min(percent, 100))}%"></span></div>
          <p class="stage-card-detail">${escapeHtml(stage.detail || "No additional detail.")}</p>
        </article>
      `;
    })
    .join("");
}

function renderMarkdownPanels() {
  $("viewerWeeklyPanel").innerHTML = viewerState.weekly
    ? markdownToHtml(viewerState.weekly)
    : `<p class="empty-state">未加载 weekly_digest_latest.md。</p>`;
  $("viewerTaxonomyPanel").innerHTML = viewerState.taxonomy
    ? markdownToHtml(viewerState.taxonomy)
    : `<p class="empty-state">未加载 taxonomy.md。</p>`;
  $("viewerTrendPanel").innerHTML = viewerState.trend
    ? markdownToHtml(viewerState.trend)
    : `<p class="empty-state">未加载 trend_analysis.md。</p>`;
}

function populateCategoryOptions() {
  const select = $("viewerCategorySelect");
  const categories = new Set();
  viewerState.comparison.forEach((row) => {
    if (row.category_bilingual) categories.add(row.category_bilingual);
    else if (row.category) categories.add(row.category);
  });
  viewerState.cards.forEach((card) => {
    if (card.best_fit_category) categories.add(card.best_fit_category);
  });

  const current = select.value;
  select.innerHTML = `<option value="">All categories</option>${Array.from(categories)
    .sort((a, b) => a.localeCompare(b))
    .map((item) => `<option value="${escapeHtml(item)}">${escapeHtml(item)}</option>`)
    .join("")}`;
  select.value = current;
}

function comparisonCategoryLookup() {
  const lookup = new Map();
  viewerState.comparison.forEach((row) => {
    const title = String(row.title || "").trim();
    const category = row.category_bilingual || row.category || "";
    if (title && category) lookup.set(title, category);
  });
  return lookup;
}

function filterCards() {
  const text = $("viewerSearchInput").value.trim().toLowerCase();
  const category = $("viewerCategorySelect").value;
  const confidence = $("viewerConfidenceSelect").value;
  const categoryLookup = comparisonCategoryLookup();

  return viewerState.cards.filter((card) => {
    const resolvedCategory = categoryLookup.get(String(card.title || "").trim()) || card.best_fit_category || "";
    if (category && resolvedCategory !== category) return false;
    if (confidence && String(card.confidence_level || "") !== confidence) return false;
    if (!text) return true;

    const haystack = [
      card.title,
      card.problem,
      card.key_idea,
      card.method,
      card.dataset_or_scenario,
      card.metrics,
      card.results_summary,
      resolvedCategory,
    ]
      .join(" ")
      .toLowerCase();

    return haystack.includes(text);
  });
}

function renderComparisonTable() {
  $("viewerComparisonCount").textContent = `${viewerState.comparison.length} rows`;
  $("viewerComparisonBody").innerHTML = viewerState.comparison
    .slice(0, 120)
    .map(
      (row) => `
        <tr>
          <td>${escapeHtml(shortText(row.title, 120))}</td>
          <td>${escapeHtml(shortText(row.method, 120))}</td>
          <td>${escapeHtml(row.complexity || "unknown")}</td>
          <td>${escapeHtml(shortText(row.scenario, 100))}</td>
          <td>${escapeHtml(row.data_driven || "unknown")}</td>
          <td>${escapeHtml(row.category_bilingual || row.category || "unknown")}</td>
        </tr>
      `,
    )
    .join("");
}

function renderCards() {
  const filtered = filterCards();
  $("viewerPaperCount").textContent = `${filtered.length} papers`;

  if (!filtered.length) {
    $("viewerCardsList").innerHTML = `<div class="empty-state">没有符合条件的论文卡片。</div>`;
    return;
  }

  $("viewerCardsList").innerHTML = filtered
    .slice(0, 160)
    .map((card) => {
      const sourceUrl = card.source_url || `https://arxiv.org/abs/${card.arxiv_id || ""}`;
      return `
        <article class="paper-card">
          <div class="paper-card-head">
            <div>
              <h3>${escapeHtml(card.title || "unknown")}</h3>
              <div class="paper-meta-line">
                <span>${escapeHtml(card.best_fit_category || "unknown")}</span>
                <span>${escapeHtml(card.innovation_type || "unknown")}</span>
                <span>${escapeHtml(card.confidence_level || "unknown")}</span>
              </div>
            </div>
            <div class="paper-links">
              <a href="${escapeHtml(sourceUrl)}" target="_blank" rel="noreferrer">arXiv</a>
              ${card.pdf_url ? `<a href="${escapeHtml(card.pdf_url)}" target="_blank" rel="noreferrer">PDF</a>` : ""}
            </div>
          </div>

          <div class="paper-grid">
            <div><strong>Problem</strong><p>${escapeHtml(shortText(card.problem, 420))}</p></div>
            <div><strong>Key idea</strong><p>${escapeHtml(shortText(card.key_idea, 420))}</p></div>
            <div><strong>Method</strong><p>${escapeHtml(shortText(card.method, 420))}</p></div>
            <div><strong>Dataset / scenario</strong><p>${escapeHtml(shortText(card.dataset_or_scenario, 420))}</p></div>
            <div><strong>Metrics</strong><p>${escapeHtml(shortText(card.metrics, 260))}</p></div>
            <div><strong>Results</strong><p>${escapeHtml(shortText(card.results_summary, 420))}</p></div>
            <div><strong>Limitations</strong><p>${escapeHtml(shortText(card.limitations, 320))}</p></div>
            <div><strong>Audit</strong><p>${escapeHtml(card.model || "unknown")} · ${escapeHtml(formatDateTime(card.generated_at))}</p></div>
          </div>
        </article>
      `;
    })
    .join("");
}

function renderAll() {
  renderLoadSummary();
  renderLoadedFiles();
  renderViewerMetrics();
  renderStatusBand();
  renderMarkdownPanels();
  populateCategoryOptions();
  renderComparisonTable();
  renderCards();
}

function resetViewer() {
  viewerState.rawPapers = [];
  viewerState.cards = [];
  viewerState.comparison = [];
  viewerState.taxonomy = "";
  viewerState.trend = "";
  viewerState.weekly = "";
  viewerState.pipelineStatus = null;
  viewerState.pipelineHistory = [];
  viewerState.loadedFiles = [];
  $("viewerSearchInput").value = "";
  $("viewerCategorySelect").value = "";
  $("viewerConfidenceSelect").value = "";
  renderAll();
}

async function tryLoadBundledSample() {
  const candidates = [
    ["../../dats/raws/papers_raw.json", "papersRaw"],
    ["../../dats/cards/paper_cards.jsonl", "cards"],
    ["../../outs/tables/comparison_table.csv", "comparison"],
    ["../../outs/taxons/taxonomy.md", "taxonomy"],
    ["../../outs/trends/trend_analysis.md", "trend"],
    ["../../outs/digests/weekly_digest_latest.md", "weekly"],
    ["../../outs/stats/pipeline_status.json", "pipelineStatus"],
    ["../../outs/stats/pipeline_history.json", "pipelineHistory"],
  ];

  const loaded = [];

  for (const [url, kind] of candidates) {
    try {
      const response = await fetch(url);
      if (!response.ok) continue;
      const text = await response.text();
      loaded.push({ name: url.split("/").pop(), relativePath: url, size: text.length, kind });
      if (kind === "papersRaw") viewerState.rawPapers = JSON.parse(text);
      if (kind === "cards") viewerState.cards = parseJsonl(text);
      if (kind === "comparison") viewerState.comparison = csvToRows(text);
      if (kind === "taxonomy") viewerState.taxonomy = text;
      if (kind === "trend") viewerState.trend = text;
      if (kind === "weekly") viewerState.weekly = text;
      if (kind === "pipelineStatus") viewerState.pipelineStatus = JSON.parse(text);
      if (kind === "pipelineHistory") viewerState.pipelineHistory = JSON.parse(text);
    } catch (error) {
      // Ignore missing bundled sample files.
    }
  }

  viewerState.loadedFiles = loaded;
  renderAll();
}

function bindEvents() {
  $("pickFolderButton").addEventListener("click", () => $("folderPicker").click());
  $("pickFilesButton").addEventListener("click", () => $("filePicker").click());
  $("clearViewerButton").addEventListener("click", resetViewer);
  $("viewerRefreshButton").addEventListener("click", renderAll);

  $("folderPicker").addEventListener("change", async (event) => {
    await loadFiles(event.target.files);
    renderAll();
  });

  $("filePicker").addEventListener("change", async (event) => {
    await loadFiles(event.target.files);
    renderAll();
  });

  $("viewerSearchInput").addEventListener("input", renderCards);
  $("viewerCategorySelect").addEventListener("change", renderCards);
  $("viewerConfidenceSelect").addEventListener("change", renderCards);
  $("loadSampleButton").addEventListener("click", tryLoadBundledSample);
}

bindEvents();
renderAll();
