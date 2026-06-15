# Retrieval-Augmented Generation (RAG) Literature Survey Taxonomy

## 核心检索与排序方法 (Core Retrieval and Ranking Methods)

**证据计数 (Evidence Count):** 102 papers

**代表性论文 (Representative Papers):**
- WorldDB: A Vector Graph-of-Worlds Memory Engine with Ontology-Aware Write-Time Reconciliation
- LAnR: Latent Abstraction for Retrieval-Augmented Generation
- Semantic Entanglement in Vector-Based Retrieval: A Formal Framework and Context-Conditioned Disentanglement Pipeline for Agentic RAG Systems
- STRIDE: Strategic Iterative Decision-Making for Retrieval-Augmented Multi-Hop Question Answering
- NaviRAG: Towards Active Knowledge Navigation for Retrieval-Augmented Generation
- Adaptive Query Routing: A Tier-Based Framework for Hybrid Retrieval Across Financial, Legal, and Medical Documents

**常见创新类型 (Common Innovation Types):**
- system_or_architecture: 系统或架构创新，如新的记忆引擎、推理框架
- retrieval_method: 检索方法创新，如新的检索算法、表示学习方法
- generation_method: 生成方法创新，如新的上下文整合机制

**模糊或低置信度区域 (Ambiguous/Low-Confidence Areas):**
- 长文档处理的最优策略在不同任务中的适用性
- 多源异构知识的融合方法缺乏统一评估框架
- 检索与生成的协同优化机制仍有探索空间

## 知识图谱与结构化知识RAG (Knowledge Graph and Structured Knowledge RAG)

**证据计数 (Evidence Count):** 14 papers

**代表性论文 (Representative Papers):**
- EvoRAG: Making Knowledge Graph-based RAG Automatically Evolve through Feedback-driven Backpropagation
- EHRAG: Bridging Semantic Gaps in Lightweight GraphRAG via Hybrid Hypergraph Construction and Retrieval
- Knowledge Is Not Static: Order-Aware Hypergraph RAG for Language Models
- Building Trust in the Skies: A Knowledge-Grounded LLM-based Framework for Aviation Safety

**常见创新类型 (Common Innovation Types):**
- system_or_architecture: 知识图谱构建与更新的新方法
- retrieval_method: 图结构检索的创新方法，如超边检索、时序感知检索
- benchmark_or_evaluation: 图RAG专用评估基准

**模糊或低置信度区域 (Ambiguous/Low-Confidence Areas):**
- 知识图谱的动态更新机制与下游任务效果的关联性
- 不同领域知识图谱的最佳表示方法
- 图结构检索与向量检索的混合策略优劣对比

## 多模态与视觉RAG (Multimodal and Visual RAG)

**证据计数 (Evidence Count):** 15 papers

**代表性论文 (Representative Papers):**
- AeroRAG: Structured Multimodal Retrieval-Augmented LLM for Fine-Grained Aerial Visual Reasoning
- KIRA: Knowledge-Intensive Image Retrieval and Reasoning Architecture for Specialized Visual Domains
- UniDoc-RL: Coarse-to-Fine Visual RAG with Hierarchical Actions and Dense Rewards
- AffectAgent: Collaborative Multi-Agent Reasoning for Retrieval-Augmented Multimodal Emotion Recognition
- CodeMMR: Bridging Natural Language, Code, and Image for Unified Retrieval

**常见创新类型 (Common Innovation Types):**
- system_or_architecture: 多模态RAG的系统架构创新
- retrieval_method: 视觉信息检索与推理的新方法
- benchmark_or_evaluation: 多模态RAG评估基准

**模糊或低置信度区域 (Ambiguous/Low-Confidence Areas):**
- 跨模态信息对齐的最佳策略
- 视觉RAG中的长距离依赖关系建模
- 多模态检索中的质量评估标准不统一

## 代理与多代理RAG (Agentic and Multi-Agent RAG)

**证据计数 (Evidence Count):** 21 papers

**代表性论文 (Representative Papers):**
- MASS-RAG: Multi-Agent Synthesis Retrieval-Augmented Generation
- AutoSearch: Adaptive Search Depth for Efficient Agentic RAG via Reinforcement Learning
- Beyond Arrow's Impossibility: Fairness as an Emergent Property of Multi-Agent Collaboration
- PRIME: Training Free Proactive Reasoning via Iterative Memory Evolution for User-Centric Agent
- VISOR: Agentic Visual Retrieval-Augmented Generation via Iterative Search and Over-horizon Reasoning

**常见创新类型 (Common Innovation Types):**
- system_or_architecture: 多代理协作框架的新架构
- retrieval_method: 代理主动检索策略创新
- benchmark_or_evaluation: 代理RAG行为评估基准

**模糊或低置信度区域 (Ambiguous/Low-Confidence Areas):**
- 多代理系统的最佳通信机制
- 代理自主性与人类监督的平衡策略
- 代理RAG的扩展性与资源消耗问题

## 域特定RAG应用 (Domain-Specific RAG Applications)

**证据计数 (Evidence Count):** 85 papers

**代表性论文 (Representative Papers):**
- Architecture Matters More Than Scale: A Comparative Study of Retrieval and Memory Augmentation for Financial QA Under SME Compute Constraints
- RAVEN: Retrieval-Augmented Vulnerability Exploration Network for Memory Corruption Analysis in User Code and Binary Programs
- LR-Robot: An Human-in-the-Loop LLM Framework for Systematic Literature Reviews with Applications in Financial Research
- BLUEmed: Retrieval-Augmented Multi-Agent Debate for Clinical Error Detection
- Policy-Aware Edge LLM-RAG Framework for Internet of Battlefield Things Mission Orchestration

**常见创新类型 (Common Innovation Types):**
- system_or_architecture: �

---

Generated from 540 structured paper cards. Model: glm-4.5-air. Generated at: 2026-06-15T04:16:24.853824+00:00.
