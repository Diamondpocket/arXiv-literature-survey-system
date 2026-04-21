# arXiv Literature Survey System

# arXiv 文献自动综述生成系统

这是一个面向 `arXiv` 的自动化文献追踪与周报生成系统。  
This project is an automated literature tracking and weekly survey generation system for `arXiv`.

项目默认研究方向是 `Retrieval-Augmented Generation, RAG`，但主题 `topic` 和检索词 `query` 都可以配置。  
The default research topic is `Retrieval-Augmented Generation, RAG`, while both `topic` and `query` are configurable.

---

## 项目目标 Project Goal

这个项目的目标，不是直接让大模型代写一篇综述，而是构建一条**结构化知识流水线** `structured knowledge pipeline`：

1. 抓取论文 `fetch papers`
2. 生成结构化卡片 `generate structured paper cards`
3. 做分类与对比分析 `taxonomy and comparison analysis`
4. 生成每周综述 `weekly survey digest`
5. 提供可视化查看界面 `dashboard and viewer`

换句话说，这个系统强调的是：

- 原始数据保留 `raw data preservation`
- 中间结构化产物保留 `structured intermediate artifacts`
- 过程可审计 `auditability`
- 结果可重复生成 `reproducibility`

---

## 核心流程 Core Workflow

主流程 `main pipeline` 如下：

```text
fetch arXiv papers
  -> dats/raws/papers_raw.json
  -> generate paper cards
  -> dats/cards/paper_cards.jsonl
  -> cluster and analyze
  -> outs/taxons/taxonomy.md
  -> outs/tables/comparison_table.csv
  -> outs/trends/trend_analysis.md
  -> generate weekly digest
  -> outs/digests/weekly_digest_latest.md
```

同时系统还会生成运行状态：

- `outs/stats/pipeline_status.json`
- `outs/stats/pipeline_history.json`

用于本地 `dashboard` 实时查看当前工作流和历史运行。

---

## 项目结构 Project Structure

```text
literature-survey-system/
  cfgs/   配置文件 Configuration files
  dats/   原始数据与结构化卡片 Data files and structured cards
  docs/   文档与源码分析 Documents and analysis notes
  outs/   分析结果与周报 Outputs and generated reports
  pkgs/   Python 包源码 Python package source code
  pmts/   提示词模板 Prompt templates
  tls/    打包与构建工具 Build and packaging tools
  uis/    本地界面 Dashboard and standalone viewer
```

更细一点的重要目录如下：

- `cfgs/envs/`
  - 环境变量配置 `environment configuration`
- `cfgs/pkgs/requirements.txt`
  - Python 依赖 `Python dependencies`
- `dats/raws/`
  - 原始论文元数据 `raw paper metadata`
- `dats/cards/`
  - 结构化论文卡片 `structured paper cards`
- `outs/taxons/`
  - 分类体系 `taxonomy`
- `outs/tables/`
  - 方法对比表 `comparison table`
- `outs/trends/`
  - 趋势分析 `trend analysis`
- `outs/digests/`
  - 周报输出 `weekly digests`
- `outs/stats/`
  - 流水线状态 `pipeline monitoring data`

---

## 主入口 Main Entry Points

### 1. 运行完整流水线 Run Full Pipeline

```powershell
.\.venv\Scripts\python.exe -m pkgs.surveys.clis.run
```

### 2. 启动本地监控面板 Start Local Dashboard

```powershell
.\.venv\Scripts\python.exe -m pkgs.surveys.clis.serve --host 127.0.0.1 --port 8765
```

### 3. 启动自动打开浏览器的面板 Start Dashboard With Auto Open

```powershell
.\.venv\Scripts\python.exe -m pkgs.surveys.clis.dashboard
```

---

## 快速开始 Quick Start

### 第一步：安装依赖 Install Dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r cfgs/pkgs/requirements.txt
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

常用配置项包括：

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `OPENAI_MODEL`
- `LLM_TEMPERATURE`

### 第三步：先跑轻量测试 Run A Lightweight Local Test

开发阶段不建议每次都抓几十上百篇论文，先小规模测试更稳：

```powershell
.\.venv\Scripts\python.exe -m pkgs.surveys.clis.run --max_results 8 --card_limit 2 --batch_size 1 --no_llm_taxonomy --no_llm_weekly
```

### 第四步：启动本地查看界面 Open Local UI

```powershell
.\.venv\Scripts\python.exe -m pkgs.surveys.clis.serve --host 127.0.0.1 --port 8765
```

然后打开：

```text
http://127.0.0.1:8765
```

---

## 关键输出文件 Key Output Files

### 原始数据 Raw Data

- `dats/raws/papers_raw.json`  
  arXiv 原始论文元数据 `raw arXiv metadata`

### 结构化卡片 Structured Cards

- `dats/cards/paper_cards.jsonl`  
  每篇论文对应一张 JSON 卡片 `one JSON card per paper`

### 分析结果 Analysis Artifacts

- `outs/taxons/taxonomy.md`  
  分类体系 `taxonomy`
  
- `outs/tables/comparison_table.csv`  
  方法对比表 `comparison table`
  
- `outs/trends/trend_analysis.md`  
  趋势分析与研究空白 `trend analysis and research gaps`
  

### 周报 Weekly Digest

- `outs/digests/weekly_digest_latest.md`  
  最新周报 `latest digest`
  
- `outs/digests/weeklies/YYYY-MM-DD.md`  
  历史周报归档 `historical weekly archives`
  

### 工作流状态 Workflow Monitoring

- `outs/stats/pipeline_status.json`  
  当前运行状态 `current run status`
  
- `outs/stats/pipeline_history.json`  
  历史运行记录 `historical run records`
  

---

## 为什么这不是“直接让 AI 写综述” Why This Is Not Direct AI Ghostwriting

这个项目专门保留了完整的中间过程，而不是只保留最终周报。

系统输出包括：

1. 原始论文元数据 `raw metadata`
2. 结构化论文卡片 `structured paper cards`
3. 分类体系 `taxonomy`
4. 方法对比表 `comparison table`
5. 趋势分析 `trend analysis`
6. 每周综述 `weekly digest`

因此，最终报告是**基于结构化中间产物生成的**，而不是从空白直接生成整篇综述。

---

## Mock 模式说明 Mock Mode

如果没有可用的真实 API Key，系统允许进入 `mock mode`，从而保证整条流水线仍然可以跑通，用于：

- 本地流程测试 `local workflow testing`
- 前端界面测试 `UI testing`
- GitHub Actions 调试 `workflow debugging`

但必须注意：

> `mock mode` 只能用于演示和测试，不能作为最终课程作业结果。

正式提交时，应使用真实 LLM API 重新生成结果。

---

## GitHub Actions 自动运行 GitHub Actions Automation

仓库包含工作流文件：

```text
.github/workflows/weekly.yml
```

它支持：

- 每周自动运行 `scheduled weekly run`
- 手动触发 `workflow_dispatch`
- 自动提交更新后的 `dats` 和 `outs`

如果要启用，需要在 GitHub 仓库中配置：

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`

可选变量：

- `OPENAI_MODEL`

---

## 文档入口 Documentation

- `docs/readmes/usage.txt`  
  本地使用说明 `practical usage notes`
  
- `docs/analyses/project_analysis.md`  
  源码级项目分析 `source-level project analysis`
  

---

## 适合老师快速查看的内容 Suggested Files For Course Review

如果老师只看几个关键文件，建议重点看：

1. `README.md`
2. `docs/analyses/project_analysis.md`
3. `dats/cards/paper_cards.jsonl`
4. `outs/taxons/taxonomy.md`
5. `outs/tables/comparison_table.csv`
6. `outs/trends/trend_analysis.md`
7. `outs/digests/weekly_digest_latest.md`

---

## 一句话总结 One-Sentence Summary

这个项目不是“让 AI 直接写综述”，而是“让 AI 参与一个可审计、可追踪、可增量更新的文献知识流水线”。  
This project is not about asking AI to directly write a survey, but about using AI inside an auditable, traceable, incrementally updated literature knowledge pipeline.
