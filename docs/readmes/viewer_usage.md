# 独立查看器使用说明
# Standalone Viewer Usage Guide

这份文档说明如何使用项目里的独立查看器 `Standalone Viewer`。  
This document explains how to use the project's standalone viewer.

---

## 1. 查看器是干什么的
## What the Viewer Is For

查看器不是用来“运行 pipeline”的，而是用来“查看已经跑出来的结果”的。  
The viewer is not for running the pipeline; it is for browsing results that have already been generated.

它特别适合这两种场景：

1. 你已经在本地跑完 pipeline，想集中查看 `dats` 和 `outs`
2. 你已经从 GitHub Actions 下载回结果，想在本地堆叠查看多个周次

---

## 2. 启动方式
## How to Launch It

### Python 方式 Python Entry

```powershell
python -m pkgs.surveys.clis.viewer
```

### EXE 方式 EXE Entry

直接运行：

```text
arts/dists/survey_viewer_standalone_v5.exe
```

---

## 3. 导入目录在哪里
## Where the Import Folder Is

### Python 运行时

查看器会自动创建：

```text
snps/imports/
```

### EXE 运行时

如果是 exe 模式，导入目录通常出现在 exe 所在目录附近：

```text
arts/dists/snps/imports/
```

这个目录就是投递箱目录 `import drop folder`。  
This is the import drop folder used by the viewer.

---

## 4. 可以往里面放什么
## What You Can Put Into the Import Folder

查看器支持三类导入：

### 1. 完整结果目录 Full Result Directory

例如一个目录内部包含：

```text
dats/
outs/
```

### 2. zip 压缩包 Zip Archive

例如 GitHub Actions 打出来的周次归档 zip。

### 3. 散文件 Loose Files

比如单独放这些文件：

- `papers_raw.json`
- `paper_cards.jsonl`
- `comparison_table.csv`
- `taxonomy.md`
- `trend_analysis.md`
- `weekly_digest_latest.md`
- `pipeline_status.json`
- `pipeline_history.json`

---

## 5. 查看器会自动识别哪些文件
## Which Files the Viewer Recognizes

查看器会自动识别并解析：

| 文件 File | 用途 Purpose |
|---|---|
| `dats/raws/papers_raw.json` | 原始论文元数据 |
| `dats/cards/paper_cards.jsonl` | 结构化论文卡片 |
| `outs/tables/comparison_table.csv` | 方法对比表 |
| `outs/taxons/taxonomy.md` | 分类体系 |
| `outs/trends/trend_analysis.md` | 趋势分析 |
| `outs/digests/weekly_digest_latest.md` | 最新周报 |
| `outs/stats/pipeline_status.json` | 当前运行状态 |
| `outs/stats/pipeline_history.json` | 历史运行记录 |

在源码中，这些识别规则定义在：

```text
pkgs/surveys/clis/viewer.py
```

对应常量是：

```python
VIEWER_FILE_HINTS
```

---

## 6. 使用流程
## Typical Usage Flow

最常见的用法是：

1. 从 GitHub 仓库下载某一次 weekly 结果
2. 把下载后的目录或 zip 放进投递箱
3. 启动查看器
4. 点击“读取投递箱”
5. 在页面里查看：
   - 论文卡片
   - weekly digest
   - taxonomy
   - trend analysis
   - comparison table
   - pipeline status

如果你连续放多个周次结果，查看器会把它们作为多个 batch 堆叠展示。  
If you place multiple weekly results into the import folder, the viewer will stack them as multiple batches.

---

## 7. 页面上能看到什么
## What You Can See in the UI

查看器页面主要包括：

- 已载入文件 `Loaded Files`
- 论文卡片过滤器 `Card Filter`
- 运行状态快照 `Status Snapshot`
- 每周文献综述 `Weekly Digest`
- 分类体系 `Taxonomy`
- 趋势分析 `Trend Analysis`
- 方法对比表 `Comparison Matrix`
- 论文卡片库 `Paper Library`

其中 `Paper Library` 支持：

- 关键词搜索
- 分类过滤
- 置信度过滤
- 多批次混合查看

---

## 8. 为什么查看器和 Dashboard 要分开
## Why the Viewer and Dashboard Are Separate

两者定位不同：

### Dashboard

- 面向当前仓库运行结果
- 更像“实时看板”
- 适合本地开发调试

### Viewer

- 面向导入结果
- 更像“离线结果浏览器”
- 适合查看 GitHub Actions 下载物

所以你可以理解成：

- `dashboard` = 看当前工作区
- `viewer` = 看导入历史包

---

## 9. 常见问题
## Common Questions

### Q1. 为什么 Actions 页面里看不到这个前端？

因为 GitHub Actions 是远程执行环境，不是你本地浏览器。  
You can see logs there, but not use it as a local interactive result browser.

### Q2. 为什么我把文件放进去后没有显示？

常见原因：

1. 放错目录了
2. 文件名不匹配查看器识别规则
3. zip 内部层级过深或不包含目标文件
4. 还没点击“读取投递箱”

### Q3. 为什么要支持散文件导入？

因为有时你不是下载完整目录，而是单独保存了几个结果文件。  
Loose-file import makes the viewer more flexible for partial local inspection.

---

## 10. 建议的最佳实践
## Recommended Best Practice

最稳的做法是：

1. 让 GitHub Actions 每周自动跑一次
2. 每次保留 `snps/weeklies/` 快照
3. 下载需要的目录或 zip
4. 丢进 viewer 的投递箱
5. 在本地统一查看多个周次结果

这样既能自动生成，也能本地可视化留档。  
This gives you both automation and local inspectability.
