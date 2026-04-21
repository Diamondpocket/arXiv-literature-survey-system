
const viewerState = {
  importBatches: [],
  rawPapers: [],
  cards: [],
  comparison: [],
  taxonomyDocs: [],
  trendDocs: [],
  weeklyDocs: [],
  pipelineStatus: null,
  pipelineStatuses: [],
  pipelineHistory: [],
  loadedFiles: [],
  dropFolderMeta: null,
  dropFolderError: "",
  autoRefreshSeconds: 20,
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

function safeSlug(value) {
  return String(value || "")
    .toLowerCase()
    .replaceAll("\\", "/")
    .replace(/[^a-z0-9/_-]+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^[-/]+|[-/]+$/g, "");
}

function inferBatchLabel(files, fallback = "Imported Batch") {
  const first = files.find((file) => normalizePath(file).includes("/"));
  if (first) {
    const root = normalizePath(first).split("/")[0];
    if (root) return root;
  }
  return `${fallback} ${viewerState.importBatches.length + 1}`;
}

function uniqueBy(items, keyBuilder) {
  const map = new Map();
  items.forEach((item, index) => {
    const key = keyBuilder(item, index);
    if (!key) return;
    if (!map.has(key)) map.set(key, item);
  });
  return Array.from(map.values());
}

function latestByTime(items, timeField) {
  return [...items].sort((left, right) => {
    const leftTime = new Date(left?.[timeField] || 0).getTime();
    const rightTime = new Date(right?.[timeField] || 0).getTime();
    return rightTime - leftTime;
  })[0] || null;
}

function rebuildDerivedState() {
  const batches = viewerState.importBatches;
  viewerState.loadedFiles = batches.flatMap((batch) =>
    (batch.loadedFiles || []).map((item) => ({
      ...item,
      batchId: batch.id,
      batchLabel: batch.label,
      source: batch.source || "manual",
    })),
  );

  viewerState.rawPapers = uniqueBy(
    batches.flatMap((batch) => batch.rawPapers || []),
    (item) => String(item.arxiv_id || item.entry_url || item.title || "").trim(),
  );

  viewerState.cards = uniqueBy(
    batches.flatMap((batch) => batch.cards || []),
    (item) => String(item.arxiv_id || item.source_url || item.title || "").trim(),
  );

  viewerState.comparison = uniqueBy(
    batches.flatMap((batch) => batch.comparison || []).map((row) => ({
      ...row,
      __batch_label: row.__batch_label || "",
    })),
    (item) => `${String(item.title || "").trim()}::${String(item.method || "").trim()}`,
  );

  viewerState.taxonomyDocs = batches
    .filter((batch) => batch.taxonomy)
    .map((batch) => ({ label: batch.label, content: batch.taxonomy, id: batch.id }));
  viewerState.trendDocs = batches
    .filter((batch) => batch.trend)
    .map((batch) => ({ label: batch.label, content: batch.trend, id: batch.id }));
  viewerState.weeklyDocs = batches
    .filter((batch) => batch.weekly)
    .map((batch) => ({ label: batch.label, content: batch.weekly, id: batch.id }));

  viewerState.pipelineStatuses = batches
    .map((batch) => batch.pipelineStatus)
    .filter((item) => item && typeof item === "object");
  viewerState.pipelineStatus = latestByTime(viewerState.pipelineStatuses, "updated_at");

  viewerState.pipelineHistory = uniqueBy(
    batches.flatMap((batch) => (Array.isArray(batch.pipelineHistory) ? batch.pipelineHistory : [])),
    (item, index) => String(item.run_id || item.updated_at || item.started_at || index),
  ).sort((left, right) => {
    const leftTime = new Date(left.updated_at || left.finished_at || left.started_at || 0).getTime();
    const rightTime = new Date(right.updated_at || right.finished_at || right.started_at || 0).getTime();
    return rightTime - leftTime;
  });
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

async function fetchJson(url) {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}
async function loadFiles(fileList) {
  const files = Array.from(fileList || []);
  const mapped = {};
  const loadedFiles = [];
  const batchLabel = inferBatchLabel(files);
  const batchId = `${safeSlug(batchLabel) || "batch"}-${Date.now()}`;

  for (const file of files) {
    const relativePath = normalizePath(file);
    const kind = detectKind(relativePath);
    loadedFiles.push({
      name: file.name,
      relativePath,
      size: file.size,
      kind: kind || "unused",
    });
    if (!kind) continue;
    mapped[kind] = file;
  }

  const batch = {
    id: batchId,
    label: batchLabel,
    source: "manual",
    sourceType: "files",
    sourcePath: "",
    loadedFiles,
    rawPapers: [],
    cards: [],
    comparison: [],
    taxonomy: "",
    trend: "",
    weekly: "",
    pipelineStatus: null,
    pipelineHistory: [],
  };

  if (mapped.papersRaw) {
    batch.rawPapers = JSON.parse(await readFileText(mapped.papersRaw));
  }
  if (mapped.cards) {
    batch.cards = parseJsonl(await readFileText(mapped.cards)).map((item) => ({
      ...item,
      __batch_label: batchLabel,
    }));
  }
  if (mapped.comparison) {
    batch.comparison = csvToRows(await readFileText(mapped.comparison)).map((row) => ({
      ...row,
      __batch_label: batchLabel,
    }));
  }
  if (mapped.taxonomy) batch.taxonomy = await readFileText(mapped.taxonomy);
  if (mapped.trend) batch.trend = await readFileText(mapped.trend);
  if (mapped.weekly) batch.weekly = await readFileText(mapped.weekly);
  if (mapped.pipelineStatus) batch.pipelineStatus = JSON.parse(await readFileText(mapped.pipelineStatus));
  if (mapped.pipelineHistory) batch.pipelineHistory = JSON.parse(await readFileText(mapped.pipelineHistory));

  viewerState.importBatches.push(batch);
  rebuildDerivedState();
}

function replaceDropFolderBatches(batches) {
  const manualBatches = viewerState.importBatches.filter((batch) => batch.source !== "dropbox");
  const normalized = (batches || []).map((batch) => ({ ...batch, source: "dropbox" }));
  viewerState.importBatches = [...normalized, ...manualBatches];
  rebuildDerivedState();
}

async function refreshDropFolder() {
  try {
    const payload = await fetchJson("/api/imports/load");
    viewerState.dropFolderMeta = payload.meta || null;
    viewerState.dropFolderError = "";
    replaceDropFolderBatches(Array.isArray(payload.batches) ? payload.batches : []);
  } catch (error) {
    viewerState.dropFolderError = String(error.message || error || "Unknown error");
  }
  renderAll();
}

function currentSummary() {
  const status = viewerState.pipelineStatus || {};
  const primaryModel =
    viewerState.cards[0]?.model || viewerState.cards.find((item) => item.model)?.model || "unknown";
  return {
    batchCount: viewerState.importBatches.length,
    rawCount: Array.isArray(viewerState.rawPapers) ? viewerState.rawPapers.length : 0,
    cardCount: viewerState.cards.length,
    comparisonCount: viewerState.comparison.length,
    model: primaryModel,
    status: status.status || "idle",
    updatedAt: status.updated_at || null,
  };
}

function renderDropFolderPanel() {
  const meta = viewerState.dropFolderMeta;
  const pathNode = $("dropFolderPath");
  const summaryNode = $("dropFolderSummary");
  if (!meta) {
    pathNode.textContent = "loading...";
    summaryNode.textContent = viewerState.dropFolderError
      ? `读取投递箱失败：${viewerState.dropFolderError}`
      : "正在读取投递箱目录...";
    return;
  }

  pathNode.textContent = meta.importsDir || "unknown";
  summaryNode.textContent = viewerState.dropFolderError
    ? `投递箱路径已创建，但最近一次读取失败：${viewerState.dropFolderError}`
    : `当前投递箱内共有 ${meta.entryCount || 0} 个条目。把 Actions 下载的目录或 zip 放进去后，点击“读取投递箱”或等待 ${viewerState.autoRefreshSeconds} 秒自动刷新。`;
}

function renderLoadSummary() {
  const used = viewerState.loadedFiles.filter((item) => item.kind !== "unused");
  const unused = viewerState.loadedFiles.filter((item) => item.kind === "unused");
  const dropFolderBatches = viewerState.importBatches.filter((item) => item.source === "dropbox").length;
  const manualBatches = viewerState.importBatches.filter((item) => item.source !== "dropbox").length;

  $("viewerLoadSummary").textContent = used.length
    ? `当前共堆叠 ${viewerState.importBatches.length} 批结果，其中投递箱 ${dropFolderBatches} 批，手动导入 ${manualBatches} 批；识别文件 ${used.length} 个，未使用 ${unused.length} 个。`
    : "还没有识别到可展示的结果文件。建议先把 Actions 下载的目录或 zip 放进投递箱，再点击“读取投递箱”。";
}

function renderLoadedFiles() {
  const target = $("loadedFilesPanel");
  if (!viewerState.importBatches.length) {
    target.innerHTML = `<p class="empty-state">还没有导入任何文件。</p>`;
    return;
  }

  target.innerHTML = viewerState.importBatches
    .map(
      (batch) => `
        <section class="loaded-batch">
          <div class="loaded-batch-head">
            <strong>${escapeHtml(batch.label)}</strong>
            <span>${escapeHtml((batch.loadedFiles || []).length)} files</span>
          </div>
          <div class="loaded-batch-sub">
            <span>${escapeHtml(batch.sourceType || batch.source || "unknown")}</span>
            <span>${escapeHtml(shortText(batch.sourcePath || "manual import", 56))}</span>
          </div>
          ${(batch.loadedFiles || [])
            .map(
              (item) => `
                <div class="loaded-file-item ${item.kind === "unused" ? "unused" : ""}">
                  <strong>${escapeHtml(item.name)}</strong>
                  <span>${escapeHtml(item.relativePath || item.name)}</span>
                  <span>${escapeHtml(item.kind)}</span>
                </div>
              `,
            )
            .join("")}
        </section>
      `,
    )
    .join("");
}

function renderViewerMetrics() {
  const summary = currentSummary();
  const metrics = [
    { label: "Imported batches", value: summary.batchCount },
    { label: "Raw papers", value: summary.rawCount },
    { label: "Paper cards", value: summary.cardCount },
    { label: "Comparison rows", value: summary.comparisonCount },
    { label: "Primary model", value: summary.model },
    { label: "Workflow status", value: summary.status },
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
    headline.textContent = "尚未读取到 pipeline_status.json，当前显示的是静态结果视图。";
    meta.innerHTML = `<span class="status-chip idle">No live status</span>`;
    strip.innerHTML = `<div class="empty-state">如果投递箱里包含 outs/stats/pipeline_status.json，这里会显示完整阶段状态。</div>`;
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
  function renderDocStack(targetId, docs, emptyMessage) {
    $(targetId).innerHTML = docs.length
      ? docs
          .map(
            (doc) => `
              <section class="viewer-doc-stack">
                <div class="viewer-doc-head">
                  <strong>${escapeHtml(doc.label)}</strong>
                </div>
                <div class="viewer-doc-body">${markdownToHtml(doc.content)}</div>
              </section>
            `,
          )
          .join("")
      : `<p class="empty-state">${emptyMessage}</p>`;
  }

  renderDocStack("viewerWeeklyPanel", viewerState.weeklyDocs, "未加载 weekly_digest_latest.md。");
  renderDocStack("viewerTaxonomyPanel", viewerState.taxonomyDocs, "未加载 taxonomy.md。");
  renderDocStack("viewerTrendPanel", viewerState.trendDocs, "未加载 trend_analysis.md。");
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
      const pdfUrl = card.pdf_url || (card.arxiv_id ? `https://arxiv.org/pdf/${card.arxiv_id}.pdf` : "");
      const preview = shortText(`${card.problem || "unknown"} ${card.key_idea || "unknown"}`, 220);
      const category = card.best_fit_category || "unknown";
      const innovation = card.innovation_type || "unknown";
      const confidence = card.confidence_level || "unknown";
      return `
        <article class="paper-card">
          <div class="paper-card-head">
            <div class="paper-card-heading">
              <div class="paper-meta-line">
                <span class="paper-chip subtle">${escapeHtml(card.__batch_label || "imported")}</span>
                <span class="paper-chip category">${escapeHtml(category)}</span>
                <span class="paper-chip">${escapeHtml(innovation)}</span>
                <span class="paper-chip confidence-${escapeHtml(confidence)}">${escapeHtml(confidence)}</span>
              </div>
              <h3>${escapeHtml(card.title || "unknown")}</h3>
              <p class="paper-preview">${escapeHtml(preview)}</p>
            </div>
            <div class="paper-links">
              <a href="${escapeHtml(sourceUrl)}" target="_blank" rel="noreferrer">arXiv</a>
              ${pdfUrl ? `<a href="${escapeHtml(pdfUrl)}" target="_blank" rel="noreferrer">PDF</a>` : ""}
            </div>
          </div>

          <div class="paper-signal-grid">
            <div class="paper-signal">
              <span>Method</span>
              <strong>${escapeHtml(shortText(card.method, 92))}</strong>
            </div>
            <div class="paper-signal">
              <span>Dataset / scenario</span>
              <strong>${escapeHtml(shortText(card.dataset_or_scenario, 92))}</strong>
            </div>
            <div class="paper-signal">
              <span>Metrics</span>
              <strong>${escapeHtml(shortText(card.metrics, 92))}</strong>
            </div>
            <div class="paper-signal">
              <span>Results</span>
              <strong>${escapeHtml(shortText(card.results_summary, 92))}</strong>
            </div>
          </div>

          <details class="paper-detail-panel">
            <summary>展开详情</summary>
            <div class="paper-grid">
              <div><strong>Problem</strong><p>${escapeHtml(shortText(card.problem, 420))}</p></div>
              <div><strong>Key idea</strong><p>${escapeHtml(shortText(card.key_idea, 420))}</p></div>
              <div><strong>Method</strong><p>${escapeHtml(shortText(card.method, 420))}</p></div>
              <div><strong>Dataset / scenario</strong><p>${escapeHtml(shortText(card.dataset_or_scenario, 420))}</p></div>
              <div><strong>Metrics</strong><p>${escapeHtml(shortText(card.metrics, 260))}</p></div>
              <div><strong>Results</strong><p>${escapeHtml(shortText(card.results_summary, 420))}</p></div>
              <div><strong>Limitations</strong><p>${escapeHtml(shortText(card.limitations, 320))}</p></div>
              <div><strong>Audit</strong><p>${escapeHtml(card.model || "unknown")} | ${escapeHtml(formatDateTime(card.generated_at))}</p></div>
            </div>
          </details>
        </article>
      `;
    })
    .join("");
}

function renderAll() {
  renderDropFolderPanel();
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
  viewerState.importBatches = [];
  viewerState.rawPapers = [];
  viewerState.cards = [];
  viewerState.comparison = [];
  viewerState.taxonomyDocs = [];
  viewerState.trendDocs = [];
  viewerState.weeklyDocs = [];
  viewerState.pipelineStatus = null;
  viewerState.pipelineStatuses = [];
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
  const batchLabel = "Bundled Sample";
  const batch = {
    id: `bundled-sample-${Date.now()}`,
    label: batchLabel,
    source: "bundled",
    sourceType: "sample",
    sourcePath: "repository sample",
    loadedFiles: loaded,
    rawPapers: [],
    cards: [],
    comparison: [],
    taxonomy: "",
    trend: "",
    weekly: "",
    pipelineStatus: null,
    pipelineHistory: [],
  };

  for (const [url, kind] of candidates) {
    try {
      const response = await fetch(url);
      if (!response.ok) continue;
      const text = await response.text();
      loaded.push({ name: url.split("/").pop(), relativePath: url, size: text.length, kind });
      if (kind === "papersRaw") batch.rawPapers = JSON.parse(text);
      if (kind === "cards") batch.cards = parseJsonl(text).map((item) => ({ ...item, __batch_label: batchLabel }));
      if (kind === "comparison") {
        batch.comparison = csvToRows(text).map((row) => ({ ...row, __batch_label: batchLabel }));
      }
      if (kind === "taxonomy") batch.taxonomy = text;
      if (kind === "trend") batch.trend = text;
      if (kind === "weekly") batch.weekly = text;
      if (kind === "pipelineStatus") batch.pipelineStatus = JSON.parse(text);
      if (kind === "pipelineHistory") batch.pipelineHistory = JSON.parse(text);
    } catch (error) {
      // Ignore missing bundled sample files.
    }
  }

  viewerState.importBatches.push(batch);
  rebuildDerivedState();
  renderAll();
}
async function copyDropFolderPath() {
  const path = viewerState.dropFolderMeta?.importsDir;
  if (!path) return;
  try {
    await navigator.clipboard.writeText(path);
    $("dropFolderSummary").textContent = "投递箱路径已复制。现在可以直接把结果目录或 zip 放进去。";
  } catch (error) {
    $("dropFolderSummary").textContent = `复制失败，请手动复制这个路径：${path}`;
  }
}

function bindEvents() {
  $("pickFolderButton").addEventListener("click", () => $("folderPicker").click());
  $("pickFilesButton").addEventListener("click", () => $("filePicker").click());
  $("clearViewerButton").addEventListener("click", resetViewer);
  $("viewerRefreshButton").addEventListener("click", renderAll);
  $("refreshDropFolderButton").addEventListener("click", refreshDropFolder);
  $("copyDropFolderButton").addEventListener("click", copyDropFolderPath);

  $("folderPicker").addEventListener("change", async (event) => {
    await loadFiles(event.target.files);
    event.target.value = "";
    renderAll();
  });

  $("filePicker").addEventListener("change", async (event) => {
    await loadFiles(event.target.files);
    event.target.value = "";
    renderAll();
  });

  $("viewerSearchInput").addEventListener("input", renderCards);
  $("viewerCategorySelect").addEventListener("change", renderCards);
  $("viewerConfidenceSelect").addEventListener("change", renderCards);
  $("loadSampleButton").addEventListener("click", tryLoadBundledSample);
}

bindEvents();
renderAll();
refreshDropFolder();
window.setInterval(refreshDropFolder, viewerState.autoRefreshSeconds * 1000);
