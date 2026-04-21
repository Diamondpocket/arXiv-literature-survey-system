# Literature Survey System

面向课程大作业的 arXiv 文献自动综述生成系统。默认主题是 **Retrieval-Augmented Generation, RAG**，系统会持续抓取近 1-2 年的 arXiv 论文，保留原始元数据，生成结构化 JSON 卡片，再基于这些中间产物生成分类体系、方法对比表、趋势分析和 Weekly Survey Digest。

这个项目的核心不是“直接让 AI 写综述”，而是构建一条**可审计的知识流水线**：

```text
arXiv metadata
  -> deduplicated raw papers
  -> structured JSON paper cards
  -> taxonomy / comparison table / trend analysis
  -> weekly digest
```

## 项目目标

系统需要满足以下课程要求：

1. 自动抓取 arXiv 文献，保留原始元数据。
2. 建立完整分析流水线：抓取、去重、结构化抽取、分类、对比分析、汇总生成。
3. 每篇论文都生成结构化 JSON 卡片。
4. 每周自动生成 1-2 页的 Weekly Survey Digest。
5. 所有综述文本都必须基于中间结构化产物，而不是直接拼接摘要。

## 项目结构

```text
literature-survey-system/
  README.md
  PROJECT_ANALYSIS.md
  requirements.txt
  .env.example
  run_pipeline.py
  fetch_arxiv.py
  generate_cards.py
  cluster_analysis.py
  weekly_survey_generator.py
  llm_client.py
  serve_frontend.py
  workflow_metadata.py
  dashboard_app.py
  build_dashboard_exe.ps1

  prompts/
    card_extraction.txt
    taxonomy_generation.txt
    weekly_digest.txt

  frontend/
    index.html
    styles.css
    app.js
    assets/

  data/
    papers_raw.json
    paper_cards.jsonl

  outputs/
    pipeline_status.json
    pipeline_history.json
    taxonomy.md
    comparison_table.csv
    trend_analysis.md
    weekly_digest_latest.md
    weekly/

  .github/
    workflows/
      weekly.yml
```

## 核心模块说明

- `fetch_arxiv.py`
  - 从 arXiv 抓取近 1-2 年论文
  - 根据 `arxiv_id` 去重
  - 输出 `data/papers_raw.json`

- `generate_cards.py`
  - 读取原始论文元数据
  - 调用 `llm_client.py` 把摘要转成结构化卡片
  - 增量写入 `data/paper_cards.jsonl`

- `cluster_analysis.py`
  - 基于 `paper_cards.jsonl` 做分类、关键词统计与方法对比
  - 输出 `outputs/taxonomy.md`
  - 输出 `outputs/comparison_table.csv`
  - 输出 `outputs/trend_analysis.md`

- `weekly_survey_generator.py`
  - 基于卡片、分类体系、对比表和趋势分析生成周报
  - 输出 `outputs/weekly_digest_latest.md`
  - 同时按日期归档到 `outputs/weekly/YYYY-MM-DD.md`

- `run_pipeline.py`
  - 串起完整流程
  - 同时负责记录实时运行状态和运行历史

- `serve_frontend.py`
  - 提供本地 Dashboard 的 HTTP API
  - 提供可视化面板，展示工作流、增量抓取、历史运行和最终分析产物

- `workflow_metadata.py`
  - 集中管理流水线阶段定义
  - 避免阶段标签在多个模块里重复维护

## 安装

建议使用 Python 3.10+。

### 方式一：标准虚拟环境

```bash
cd literature-survey-system
python -m venv .venv
```

激活虚拟环境：

- macOS / Linux

```bash
source .venv/bin/activate
```

- Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

如果 PowerShell 因执行策略报错，可以直接绕开激活脚本，使用虚拟环境里的 Python：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

安装依赖：

```bash
pip install -r requirements.txt
```

## 配置 API Key

复制环境变量模板：

```bash
cp .env.example .env
```

在 `.env` 中填写：

```text
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0
```

如果使用兼容 OpenAI SDK 的服务，也可以设置：

```text
OPENAI_BASE_URL=https://your-compatible-endpoint/v1
OPENAI_MODEL=your-model-name
LLM_TEMPERATURE=0
```

## Mock 模式说明

如果没有 `OPENAI_API_KEY`，系统会进入 **mock mode**：

- `llm_client.py` 会返回占位结构化结果
- 流水线仍然可以完整跑通
- 适合调试工程、联调前端、验证 GitHub Actions

但是：

- mock 结果**不能**作为最终课程作业提交结果
- 正式作业必须使用真实大模型 API

## 一键运行

```bash
python run_pipeline.py
```

Windows 下推荐：

```powershell
.\.venv\Scripts\python.exe run_pipeline.py
```

## 开发期轻量运行

开发阶段不建议每次都跑满 100 篇，可以先用轻量参数联调：

```powershell
.\.venv\Scripts\python.exe run_pipeline.py --max_results 8 --card_limit 2 --batch_size 1 --no_llm_taxonomy --no_llm_weekly
```

常用参数：

- `--query`
  - 自定义 arXiv 查询语句
- `--max_results`
  - 抓取上限
- `--years`
  - 时间窗口
- `--skip_fetch`
  - 跳过抓取，复用已有 `papers_raw.json`
- `--card_limit`
  - 只处理部分新论文
- `--batch_size`
  - 控制每次 LLM 抽取的批量大小
- `--no_llm_taxonomy`
  - 用确定性规则生成 taxonomy
- `--no_llm_weekly`
  - 用确定性模板生成 digest

## Dashboard 可视化面板

启动本地前端：

```powershell
.\.venv\Scripts\python.exe serve_frontend.py --host 127.0.0.1 --port 8765
```

打开浏览器：

```text
http://127.0.0.1:8765
```

Dashboard 会展示：

- 流水线当前状态 `pipeline_status.json`
- 最近运行历史 `pipeline_history.json`
- 本轮新增论文
- 当前 Raw Papers / Paper Cards / Comparison Rows / Weekly Archives
- 最新 `taxonomy.md`、`trend_analysis.md`、`weekly_digest_latest.md`

## 生成桌面版 EXE

```powershell
powershell -ExecutionPolicy Bypass -File .\build_dashboard_exe.ps1
```

输出文件：

- `dist/survey_dashboard.exe`

如果这个文件正在运行、无法覆盖，可以重新打一个新名字的版本，或者先关闭旧进程。

## 输出文件说明

- `data/papers_raw.json`
  - 原始 arXiv 元数据
  - 保留 `arxiv_id`、标题、作者、摘要、分类、链接等信息

- `data/paper_cards.jsonl`
  - 每篇论文一条 JSON 结构化卡片
  - 包含课程要求字段和审计字段

- `outputs/taxonomy.md`
  - 基于卡片生成的分类体系

- `outputs/comparison_table.csv`
  - 方法对比表
  - 包含方法、复杂度、场景、优缺点、是否数据驱动等字段

- `outputs/trend_analysis.md`
  - 研究趋势分析
  - 包含研究空白与未来方向

- `outputs/weekly_digest_latest.md`
  - 最新周报

- `outputs/weekly/YYYY-MM-DD.md`
  - 历史周报归档

- `outputs/pipeline_status.json`
  - 当前运行状态
  - 给前端监控面板实时读取

- `outputs/pipeline_history.json`
  - 历史运行记录
  - 展示每次运行新增了多少论文、多少卡片、何时生成周报

## 为什么这不是“AI 直接代写综述”

这个项目明确保留了完整中间链路：

1. 原始数据：`papers_raw.json`
2. 中间结构化卡片：`paper_cards.jsonl`
3. 分类体系：`taxonomy.md`
4. 方法对比表：`comparison_table.csv`
5. 趋势分析：`trend_analysis.md`
6. 周报：`weekly_digest_latest.md`

因此最终周报是由**结构化知识流水线**生成的，而不是直接给大模型一句“帮我写综述”。

## 如何降低大模型不确定性

项目通过以下方式降低 LLM 输出波动：

- 固定 Prompt 模板
- `temperature=0`
- 保留中间结果
- 新论文才增量生成卡片
- 对输出 JSON 做字段校验
- 缺失字段自动填 `unknown`
- 保存 `model` 和 `generated_at`
- 明确要求只能基于 title 和 abstract，不允许虚构

## GitHub Actions 每周自动更新

工作流文件：

- `.github/workflows/weekly.yml`

支持：

- `schedule`
  - 每周自动运行
- `workflow_dispatch`
  - 手动触发

典型流程：

1. 拉取仓库
2. 安装 Python 和依赖
3. 注入 `OPENAI_API_KEY`
4. 执行 `python run_pipeline.py`
5. 提交 `data/` 和 `outputs/` 的更新

> 注意：只有在 GitHub 仓库真正创建并推送后，GitHub Actions 才会在网页端可见并开始工作。

## 交作业时建议展示的文件

- `README.md`
- `PROJECT_ANALYSIS.md`
- `run_pipeline.py`
- `fetch_arxiv.py`
- `generate_cards.py`
- `cluster_analysis.py`
- `weekly_survey_generator.py`
- `llm_client.py`
- `data/papers_raw.json`
- `data/paper_cards.jsonl`
- `outputs/taxonomy.md`
- `outputs/comparison_table.csv`
- `outputs/trend_analysis.md`
- `outputs/weekly_digest_latest.md`
- `.github/workflows/weekly.yml`

## 推荐答辩说法

你可以这样解释：

> 本系统不是直接调用大模型生成整篇综述，而是把大模型放在结构化知识流水线中的“分析模块”位置。  
> 它先抓取 arXiv 数据，保存原始元数据；再把论文摘要抽取为结构化 JSON 卡片；然后基于这些卡片做分类、方法对比和趋势分析；最后才生成周报。  
> 因此系统的重点是结构化分析、趋势判断和知识组织，而不是把写作完全交给模型。

## 相关文档

- [PROJECT_ANALYSIS.md](/C:/Users/86515/Documents/Codex/literature-survey-system/PROJECT_ANALYSIS.md)
#   a r X i v - l i t e r a t u r e - s u r v e y - s y s t e m  
 