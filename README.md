# arXiv Literature Survey System
# arXiv 文献自动综述生成系统

这是一个围绕 `arXiv` 构建的自动化文献追踪与综述生成项目。  
This project is an automated literature tracking and survey generation system built around `arXiv`.

项目默认研究主题是 `Retrieval-Augmented Generation, RAG`，但 `topic` 和 `query` 都可以配置。  
The default research topic is `Retrieval-Augmented Generation, RAG`, while both `topic` and `query` are configurable.

这个项目的重点不是“直接让 AI 代写综述”，而是把综述拆成一条可审计、可追踪、可增量更新的结构化知识流水线。  
The goal is not to let AI directly ghostwrite a survey, but to build an auditable, traceable, incrementally updated structured knowledge pipeline.

---

## 项目目标 Project Goal

系统完成以下事情：

1. 从 `arXiv` 自动抓取近 1 到 2 年的相关论文。
2. 保存原始元数据 `raw metadata`。
3. 为每篇论文生成结构化 JSON 卡片 `structured paper card`。
4. 基于卡片生成分类体系 `taxonomy`、方法对比表 `comparison table`、趋势分析 `trend analysis`。
5. 每周自动生成综述摘要 `Weekly Survey Digest`。
6. 保留历史结果，并支持本地可视化查看。

---

## 核心工作流 Core Workflow

```text
fetch papers from arXiv
  -> dats/raws/papers_raw.json
  -> generate structured cards
  -> dats/cards/paper_cards.jsonl
  -> cluster and compare
  -> outs/taxons/taxonomy.md
  -> outs/tables/comparison_table.csv
  -> outs/trends/trend_analysis.md
  -> generate weekly digest
  -> outs/digests/weekly_digest_latest.md
  -> archive dated weekly digest
  -> outs/digests/weeklies/YYYY-MM-DD.md
```

系统同时会记录工作流状态：

- `outs/stats/pipeline_status.json`
- `outs/stats/pipeline_history.json`

这两份状态文件会被本地 `dashboard` 和 `viewer` 读取，用来展示当前执行进度和历史运行记录。  
These two status files are used by the local `dashboard` and `viewer` to show live workflow progress and historical runs.

---

## 目录结构 Project Structure

```text
literature-survey-system/
  .github/        GitHub Actions workflows
  arts/           build outputs, exe files, logs, releases
  cfgs/           environment and dependency configuration
  dats/           raw paper data and structured cards
  docs/           analysis notes and usage documents
  outs/           generated reports and monitoring files
  pkgs/           Python package source code
  pmts/           prompt templates
  snps/           weekly snapshots and import drop folders
  tls/            packaging scripts and PyInstaller spec files
  tsts/           tests
  uis/            dashboard and standalone viewer frontend
  README.md
```

重点目录说明：

- `cfgs/envs/`
  - 环境变量配置，例如 `.env.example`
- `cfgs/pkgs/requirements.txt`
  - Python 依赖列表
- `dats/raws/`
  - `papers_raw.json`，保存 arXiv 原始元数据
- `dats/cards/`
  - `paper_cards.jsonl`，保存结构化论文卡片
- `outs/taxons/`
  - `taxonomy.md`
- `outs/tables/`
  - `comparison_table.csv`
- `outs/trends/`
  - `trend_analysis.md`
- `outs/digests/`
  - `weekly_digest_latest.md` 和历史周报
- `outs/stats/`
  - 流水线状态文件
- `pkgs/surveys/clis/`
  - 命令行入口 `CLI entry points`
- `pkgs/surveys/fetchers/`
  - arXiv 抓取逻辑
- `pkgs/surveys/cards/`
  - 结构化卡片生成逻辑
- `pkgs/surveys/analyses/`
  - taxonomy、comparison、trend、weekly digest 生成逻辑
- `pkgs/surveys/clients/`
  - LLM client 封装
- `pkgs/surveys/webs/`
  - 本地 Web 服务
- `uis/dashboards/`
  - 本地实时监控界面
- `uis/viewers/`
  - 独立查看器前端

---

## 主入口 Main Entry Points

### 1. 运行完整流水线 Run Full Pipeline

```powershell
python -m pkgs.surveys.clis.run
```

### 2. 启动本地 Dashboard Start Local Dashboard

```powershell
python -m pkgs.surveys.clis.serve --host 127.0.0.1 --port 8765
```

然后打开：

```text
http://127.0.0.1:8765
```

### 3. 启动 Standalone Viewer Start Standalone Viewer

```powershell
python -m pkgs.surveys.clis.viewer
```

或者直接运行已打包的 exe：

```text
arts/dists/survey_viewer_standalone_v5.exe
```

---

## 快速开始 Quick Start

### 第一步：安装依赖 Install Dependencies

```powershell
python -m pip install -r cfgs/pkgs/requirements.txt
```

### 第二步：配置环境变量 Configure Environment Variables

复制：

```text
cfgs/envs/.env.example
```

为：

```text
cfgs/envs/.env
```

常用配置项：

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `OPENAI_MODEL`
- `LLM_TEMPERATURE`
- `LLM_REQUEST_TIMEOUT_SECONDS`
- `LLM_RETRY_ATTEMPTS`

### 第三步：先跑小规模测试 Run a Small Development Test

开发阶段不建议一上来就抓几十上百篇，先跑轻量测试更稳：

```powershell
python -m pkgs.surveys.clis.run --max_results 8 --card_limit 2 --batch_size 1 --no_llm_taxonomy --no_llm_weekly
```

### 第四步：运行完整版本 Run the Full Version

```powershell
python -m pkgs.surveys.clis.run --max_results 80 --years 2
```

---

## 论文卡片字段 Paper Card Fields

每篇论文会生成一张结构化 JSON 卡片，至少包含：

- `title`
- `problem`
- `key_idea`
- `method`
- `dataset_or_scenario`
- `metrics`
- `results_summary`
- `innovation_type`
- `limitations`
- `best_fit_category`
- `confidence_level`

同时保留审计字段：

- `arxiv_id`
- `source_url`
- `published`
- `summary`
- `evidence_source`
- `model`
- `generated_at`

约束原则：

1. 结构化抽取优先基于标题和摘要 `title + abstract`。
2. 不允许编造数据集、指标、结果。
3. 摘要没写到的信息，写 `unknown` 或 `not specified`。
4. 缺失字段时会自动补全并把 `confidence_level` 降为 `low`。

---

## 关键输出文件 Key Output Files

### 原始数据 Raw Data

- `dats/raws/papers_raw.json`
  - arXiv 原始论文元数据 `raw arXiv metadata`

### 结构化卡片 Structured Cards

- `dats/cards/paper_cards.jsonl`
  - 每篇论文一条 JSON 记录 `one JSON record per paper`

### 分析产物 Analysis Artifacts

- `outs/taxons/taxonomy.md`
  - 分类体系 `taxonomy`
- `outs/tables/comparison_table.csv`
  - 方法对比表 `comparison table`
- `outs/trends/trend_analysis.md`
  - 趋势分析与研究空白 `trend analysis and research gaps`

### 周报 Weekly Digest

- `outs/digests/weekly_digest_latest.md`
  - 最新周报 `latest digest`
- `outs/digests/weeklies/YYYY-MM-DD.md`
  - 历史周报归档 `historical weekly digests`

### 工作流监控 Workflow Monitoring

- `outs/stats/pipeline_status.json`
  - 当前运行状态 `current pipeline status`
- `outs/stats/pipeline_history.json`
  - 历史运行记录 `historical runs`

---

## 为什么这不是“直接让 AI 写综述”
## Why This Is Not Direct AI Ghostwriting

这个项目专门保留了完整的中间过程，而不是只保留最终周报。  
The project deliberately preserves the full intermediate process instead of keeping only the final digest.

系统产物包括：

1. 原始论文元数据 `raw metadata`
2. 结构化论文卡片 `structured paper cards`
3. 分类体系 `taxonomy`
4. 方法对比表 `comparison table`
5. 趋势分析 `trend analysis`
6. 每周综述 `weekly digest`

因此，最终报告是基于中间结构化产物生成的，而不是从空白直接生成整篇综述。  
The final report is generated from intermediate structured artifacts, not hallucinated from scratch.

---

## Mock Mode 是什么
## What Mock Mode Means

如果没有可用的真实 API Key，系统允许退化到 `mock mode`，以保证流程和界面还能跑通。  
If no real API key is available, the system can fall back to `mock mode` so the pipeline and UI still run.

`mock mode` 的用途：

- 本地流程调试 `local workflow debugging`
- 前端界面联调 `UI testing`
- GitHub Actions 调试 `workflow debugging`

但要注意：

> `mock mode` 只能用于演示和开发，不能作为最终课程作业结果。  
> `mock mode` is for demo and development only, not for final coursework submission.

---

## LLM 配置建议 LLM Configuration Notes

默认学术型任务通常更适合低温度 `low temperature`，例如 `0`。  
In principle, academic extraction tasks are usually better with a low temperature such as `0`.

但是部分兼容 OpenAI 的提供商模型会限制 `temperature` 取值，例如只接受 `1`。  
However, some OpenAI-compatible providers restrict the allowed `temperature`, for example accepting only `1`.

因此项目把 `LLM_TEMPERATURE` 做成了可配置项：

- 如果模型支持，优先用 `0`
- 如果服务端限制，使用提供商要求的值，例如 `1`

这不是“随机性更大更好”，而是“先保证接口可用，再结合 prompt 和审计机制控制稳定性”。  
This is not about preferring higher randomness, but about staying compatible first and controlling variance through prompts and auditing.

---

## GitHub Actions 自动运行
## GitHub Actions Automation

仓库包含工作流文件：

```text
.github/workflows/weekly.yml
```

它支持：

- 每周自动运行 `scheduled weekly run`
- 手动触发 `workflow_dispatch`
- 自动生成 `dats`、`outs`、`snps`
- 自动把结果提交回仓库

通常需要在 GitHub 仓库中配置以下 Secrets：

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`

常见 Variables：

- `OPENAI_MODEL`

如果你需要在网页端手动测试：

1. 打开 GitHub 仓库
2. 进入 `Actions`
3. 选择 `weekly.yml`
4. 点击 `Run workflow`

---

## 周次快照与下载
## Weekly Snapshots and Download

为了便于每次自动运行后留档，项目会把结果按时间归档到：

```text
snps/weeklies/
```

典型结构如下：

```text
snps/weeklies/YYYY-MM-DD_HHMMSS/
  dats/
  outs/
```

同时可以生成同名 zip，方便直接下载和本地查看。  
The workflow can also produce a matching zip so each weekly run can be downloaded and inspected locally.

这套设计的好处是：

- 每次运行都有独立快照
- 便于按时间回看历史版本
- 便于把多个周次结果导入同一个查看器

---

## Standalone Viewer 独立查看器

项目内置一个本地结果查看器，用于把 GitHub Actions 下载回来的结果堆叠展示。  
The project includes a local standalone viewer for stacking and browsing downloaded workflow results.

入口方式：

- Python 运行：
  - `python -m pkgs.surveys.clis.viewer`
- EXE 运行：
  - `arts/dists/survey_viewer_standalone_v5.exe`

查看器会自动创建投递目录：

```text
snps/imports/
```

如果你运行的是 exe，则投递目录会出现在 exe 所在目录旁边，例如：

```text
arts/dists/snps/imports/
```

你只需要把以下任意一种东西丢进去：

1. 一整个结果目录，内部包含 `dats/` 和 `outs/`
2. 由 Actions 导出的 zip 文件
3. 单独的 `papers_raw.json`、`paper_cards.jsonl`、`taxonomy.md` 等文件

查看器会自动识别并加载：

- `papers_raw.json`
- `paper_cards.jsonl`
- `comparison_table.csv`
- `taxonomy.md`
- `trend_analysis.md`
- `weekly_digest_latest.md`
- `pipeline_status.json`
- `pipeline_history.json`

更详细的使用方法见：

- [docs/analyses/workflow_guide.md](C:\Users\86515\Documents\Codex\literature-survey-system\docs\analyses\workflow_guide.md)
- [docs/readmes/viewer_usage.md](C:\Users\86515\Documents\Codex\literature-survey-system\docs\readmes\viewer_usage.md)

---

## 适合交作业时展示的文件
## Suggested Files for Submission Demo

建议至少展示这些文件：

1. `README.md`
2. `docs/analyses/project_analysis.md`
3. `dats/cards/paper_cards.jsonl`
4. `outs/taxons/taxonomy.md`
5. `outs/tables/comparison_table.csv`
6. `outs/trends/trend_analysis.md`
7. `outs/digests/weekly_digest_latest.md`
8. `outs/stats/pipeline_status.json`
9. `outs/stats/pipeline_history.json`

---

## 答辩时可以怎么解释
## How To Explain This In a Defense

你可以这样说：

> 本项目不是让大模型直接代写综述，而是把综述工作拆解为“抓取、结构化抽取、分类、对比、趋势分析、周报生成”几个阶段。  
> 大模型在其中承担的是结构化分析模块 `analysis module` 的角色，而不是终端写手。  
> 原始数据、中间 JSON 卡片、分类体系、对比表和最终周报全部留档，因此整个系统是可审计、可追踪、可复现的。

---

## 进一步阅读 Further Reading

- [docs/analyses/project_analysis.md](C:\Users\86515\Documents\Codex\literature-survey-system\docs\analyses\project_analysis.md)
- [docs/analyses/workflow_guide.md](C:\Users\86515\Documents\Codex\literature-survey-system\docs\analyses\workflow_guide.md)
- [docs/readmes/viewer_usage.md](C:\Users\86515\Documents\Codex\literature-survey-system\docs\readmes\viewer_usage.md)

---

## 一句话总结 One-Sentence Summary

这不是“让 AI 直接写综述”，而是“让 AI 参与一个可审计、可追踪、可持续更新的文献知识流水线”。  
This is not about asking AI to directly write a survey, but about using AI inside an auditable, traceable, continuously updated literature knowledge pipeline.
