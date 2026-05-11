# RAG Literature Survey Taxonomy

## 1. 核心检索与排序方法 (Core Retrieval and Ranking Methods)

**证据计数**: 52

**代表性论文**:
- "WorldDB: A Vector Graph-of-Worlds Memory Engine with Ontology-Aware Write-Time Reconciliation"
- "Semantic Entanglement in Vector-Based Retrieval: A Formal Framework and Context-Conditioned Disentanglement Pipeline for Agentic RAG Systems"
- "LAnR (Latent Abstraction for RAG)"
- "CHOP: Chunkwise Context-Preserving Framework for RAG on Multi Documents"
- "Skill-RAG: Failure-State-Aware Retrieval Augmentation via Hidden-State Probing and Skill Routing"

**常见创新类型**:
- 系统架构 (system_or_architecture)
- 检索方法 (retrieval_method)
- 生成方法 (generation_method)
- 基准评估 (benchmark_or_evaluation)

**模糊或低置信度区域**:
- 检索与生成的最佳整合方式尚无统一标准
- 长文档检索的效率和效果平衡仍需探索
- 检索结果的排序优化在多跳推理任务中的影响需要进一步研究

## 2. 知识图谱与结构化知识RAG (Knowledge Graph and Structured Knowledge RAG)

**证据计数**: 6

**代表性论文**:
- "EHRAG: Bridging Semantic Gaps in Lightweight GraphRAG via Hybrid Hypergraph Construction and Retrieval"
- "Knowledge Is Not Static: Order-Aware Hypergraph RAG for Language Models"
- "Building Trust in the Skies: A Knowledge-Grounded LLM-based Framework for Aviation Safety"
- "EvoRAG: Making Knowledge Graph-based RAG Automatically Evolve through Feedback-driven Backpropagation"

**常见创新类型**:
- 系统架构 (system_or_architecture)
- 检索方法 (retrieval_method)

**模糊或低置信度区域**:
- 知识图谱构建与更新的自动化程度有限
- 知识图谱与语言模型的有效融合方法仍在探索中
- 大规模知识图谱的存储与检索效率问题

## 3. 多模态与视觉RAG (Multimodal and Visual RAG)

**证据计数**: 9

**代表性论文**:
- "AeroRAG: Structured Multimodal Retrieval-Augmented LLM for Fine-Grained Aerial Visual Reasoning"
- "KIRA: Knowledge-Intensive Image Retrieval and Reasoning Architecture for Specialized Visual Domains"
- "CodeMMR: Bridging Natural Language, Code, and Image for Unified Retrieval"
- "UniDoc-RL: Coarse-to-Fine Visual RAG with Hierarchical Actions and Dense Rewards"
- "AffectAgent: Collaborative Multi-Agent Reasoning for Retrieval-Augmented Multimodal Emotion Recognition"

**常见创新类型**:
- 系统架构 (system_or_architecture)
- 检索方法 (retrieval_method)

**模糊或低置信度区域**:
- 跨模态信息融合的有效性评估标准不统一
- 视觉与文本信息的检索权重分配问题
- 多模态检索中的噪声处理机制需要进一步研究

## 4. 多智能体RAG (Agentic and Multi-Agent RAG)

**证据计数**: 10

**代表性论文**:
- "MASS-RAG: Multi-Agent Synthesis Retrieval-Augmented Generation"
- "AutoSearch: Adaptive Search Depth for Efficient Agentic RAG via Reinforcement Learning"
- "Beyond Arrow's Impossibility: Fairness as an Emergent Property of Multi-Agent Collaboration"
- "MM-Doc-R1: Training Agents for Long Document Visual Question Answering through Multi-turn Reinforcement Learning"
- "VISOR: Agentic Visual Retrieval-Augmented Generation via Iterative Search and Over-horizon Reasoning"
- "PRIME: Training Free Proactive Reasoning via Iterative Memory Evolution for User-Centric Agent"

**常见创新类型**:
- 系统架构 (system_or_architecture)
- 检索方法 (retrieval_method)

**模糊或低置信度区域**:
- 多智能体之间的协作机制与效率优化
- 智能体检索与生成的协调问题
- 多智能体系统的安全性与隐私保护措施

## 5. 领域特定RAG应用 (Domain-Specific RAG Applications)

**证据计数**: 30

**代表性论文**:
- "RAVEN: Retrieval-Augmented Vulnerability Exploration Network for Memory Corruption Analysis in User Code and Binary Programs"
- "Architecture Matters More Than Scale: A Comparative Study of Retrieval and Memory Augmentation for Financial QA Under SME Compute Constraints"
- "RoTRAG: Rule of Thumb Reasoning for Conversation Harm Detection with Retrieval-Augmented Generation"
- "LR-Robot: An Human-in-the-Loop LLM Framework for Systematic Literature Reviews with Applications in Financial Research"
- "Enhancing Mental Health Counseling Support in Bangladesh using Culturally-Grounded Knowledge"
- "LLM4C2Rust: Large Language Models for Automated Memory-Safe Code Transpilation"

**常见创新类型**:
- 系统架构 (system_or_architecture)
- 检索方法 (retrieval_method)
- 生成方法 (generation_method)
- 基准评估 (benchmark_or_evaluation)

**模糊或低置信度区域**:
- 领域特定知识库的构建与维护成本高
- 跨领域知识迁移的有效性
- 领域特定评估基准的缺乏

## 6. 效率、部署与设备端RAG (Efficiency, Deployment, and On-Device

---

Generated from 248 structured paper cards. Model: glm-4.5-air. Generated at: 2026-05-11T03:39:45.308913+00:00.
