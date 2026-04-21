# 每周文献综述 Weekly Survey Digest - Retrieval-Augmented Generation, RAG

Date / 日期: 2026-04-21
Evidence base / 证据基础: 134 structured arXiv paper cards / 134 张结构化 arXiv 论文卡片。

## 本周概览 Weekly Overview
本次周报基于已留存的 JSON 卡片生成，覆盖 134 篇论文。最新样本包括：
- MathNet: a Global Multimodal Benchmark for Mathematical Reasoning and Retrieval (2026-04-20, 多模态与视觉 RAG (Multimodal and Visual RAG))
- MASS-RAG: Multi-Agent Synthesis Retrieval-Augmented Generation (2026-04-20, 智能体与多智能体 RAG (Agentic and Multi-Agent RAG))
- WorldDB: A Vector Graph-of-Worlds Memory Engine with Ontology-Aware Write-Time Reconciliation (2026-04-20, 智能体与多智能体 RAG (Agentic and Multi-Agent RAG))
- ArbGraph: Conflict-Aware Evidence Arbitration for Reliable Long-Form Retrieval-Augmented Generation (2026-04-20, 评测、基准与诊断 (Evaluation, Benchmarks, and Diagnostics))
- DocQAC: Adaptive Trie-Guided Decoding for Effective In-Document Query Auto-Completion (2026-04-20, 评测、基准与诊断 (Evaluation, Benchmarks, and Diagnostics))

## 分类体系摘要 Taxonomy Summary
- 智能体与多智能体 RAG (Agentic and Multi-Agent RAG): 22 篇。
- 多模态与视觉 RAG (Multimodal and Visual RAG): 21 篇。
- 评测、基准与诊断 (Evaluation, Benchmarks, and Diagnostics): 21 篇。
- 可靠性、安全、隐私与防护 (Reliability, Safety, Privacy, and Security): 15 篇。
- 核心检索与排序方法 (Core Retrieval and Ranking Methods): 13 篇。
- 领域应用型 RAG (Domain-Specific RAG Applications): 12 篇。

## 方法对比摘要 Method Comparison
- Enhancing Large Language Models with Retrieval Augmented Generation for Software Testing and Inspection Automation: 方法=RAG pipeline that retrieves external knowledge to provide context to LLMs for automated test case generation and source code inspection; 复杂度=medium; 场景=software testing (automated test case generation) and software inspection (source code review); 数据驱动=yes。
- UrbanClipAtlas: A Visual Analytics Framework for Event and Scene Retrieval in Urban Videos: 方法=Segments extended recordings into short clips, generates textual descriptions with a vision-language model, indexes them for semantic retrieval, and constructs a knowledge graph mapping LLM-extracted entities and rela...; 复杂度=medium; 场景=StreetAware dataset; long urban videos at street intersections; hazardous scenarios; crossing dynamics.; 数据驱动=yes。
- UniDoc-RL: Coarse-to-Fine Visual RAG with Hierarchical Actions and Dense Rewards: 方法=Reinforcement learning framework using Group Relative Policy Optimization (GRPO) with a dense multi-reward scheme and hierarchical action space for end-to-end training of visual information acquisition.; 复杂度=high; 场景=three unspecified benchmarks; curated dataset of high-quality reasoning trajectories with fine-grained action annotations; 数据驱动=yes。
- Toward Agentic RAG for Ukrainian: 方法=Two-stage retrieval using BGE-M3 with BGE reranking, integrated with a lightweight agentic layer that performs query rephrasing and answer-retry loops, built on Qwen2.5-3B-Instruct; 复杂度=medium; 场景=UNLP 2026 Shared Task on Multi-Domain Document Understanding; 数据驱动=yes。
- LR-Robot: An Human-in-the-Loop LLM Framework for Systematic Literature Reviews with Applications in Financial Research: 方法=LR-Robot framework combining expert-defined taxonomies, LLM-based classification with retrieval-augmented generation for downstream analysis, and human-in-the-loop evaluation before full deployment.; 复杂度=medium; 场景=Corpus of 12,666 option pricing articles spanning 50 years; financial research domain.; 数据驱动=yes。
- Enhancing Mental Health Counseling Support in Bangladesh using Culturally-Grounded Knowledge: 方法=Two approaches: retrieval-augmented generation (RAG) and a knowledge graph-based method utilizing a manually constructed KG capturing causal relationships between stressors, interventions, and outcomes; 复杂度=medium; 场景=Mental health counseling support in Bangladesh for para-counselors; 数据驱动=yes。
- Don't Retrieve, Navigate: Distilling Enterprise Knowledge into Navigable Agent Skills for QA and RAG: 方法=Corpus2Skill: iterative document clustering with LLM-generated summaries compiled into a navigable tree; agents receive a bird's-eye view, drill into branches via progressively finer summaries, and retrieve documents...; 复杂度=medium; 场景=WixQA (enterprise customer-support benchmark for RAG); 数据驱动=yes。
- A Unified Model and Document Representation for On-Device Retrieval-Augmented Generation: 方法=A unified model that compresses the RAG context and utilizes the same representations for retrieval; 复杂度=medium; 场景=on-device retrieval of sensitive personal information (e.g., financial documents, contact details, medical history); specific datasets unknown; 数据驱动=yes。

## 趋势分析 Trend Analysis
当前最常见的创新类型是 **system_or_architecture**。结合结构化卡片，RAG 研究正从通用流水线转向评测、领域化、结构化知识、多模态与可靠性等更细粒度方向。

## 研究空白与未来方向 Research Gaps and Future Directions
- 仅靠摘要很难统一比较数据集、指标、成本和失败模式，后续可对代表性论文补充全文级证据。
- 未来综述应把 RAG 拆成检索、重排、生成、校验和运行治理五个环节分别评估，而不是只比较最终回答质量。
- 原创判断：更有价值的 RAG 系统不只是“检索更多”，而是能判断何时不检索、何时压缩证据、何时触发外部工具，以及何时拒答。

## 证据来源 Provenance
- This digest is generated from `paper_cards.jsonl`, `taxonomy.md`, `comparison_table.csv`, and `trend_analysis.md`.

