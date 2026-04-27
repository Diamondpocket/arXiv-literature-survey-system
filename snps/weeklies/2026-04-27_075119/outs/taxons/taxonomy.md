# Retrieval-Augmented Generation (RAG) Research Taxonomy

## 1. Core Retrieval and Ranking Methods (核心检索与排序方法)
**Evidence Count:** 34

### Representative Papers:
- **WorldDB: A Vector Graph-of-Worlds Memory Engine with Ontology-Aware Write-Time Reconciliation**
- **ArbGraph: Conflict-Aware Evidence Arbitration for Reliable Long-Form Retrieval-Augmented Generation**
- **DocQAC: Adaptive Trie-Guided Decoding for Effective In-Document Query Auto-Completion**
- **LAnR (Latent Abstraction for RAG)**: Latent Abstraction for Retrieval-Augmented Generation
- **CHOP: Chunkwise Context-Preserving Framework for RAG on Multi Documents**

### Common Innovation Types:
- **system_or_architecture**: Novel architectures for retrieval, memory management, and evidence integration
- **retrieval_method**: Improvements in retrieval techniques, including chunking, ranking, and context preservation
- **generation_method**: Methods for improving evidence utilization and reducing hallucinations

### Ambiguous Areas:
- **Optimal chunking strategies**: Various approaches to document segmentation (CHOP, DTCRS, ChunQiuTR) with no clear consensus on best practices
- **Retrieval-generation integration**: Tension between separate vs. integrated approaches (LAnR vs. GuarantRAG)
- **Semantic entanglement**: Formal definitions and quantification still evolving (Semantic Disentanglement Pipeline)

## 2. Knowledge Graph and Structured Knowledge RAG (知识图谱与结构化知识RAG)
**Evidence Count:** 6

### Representative Papers:
- **EHRAG: Bridging Semantic Gaps in Lightweight GraphRAG via Hybrid Hypergraph Construction and Retrieval**
- **EvoRAG: Making Knowledge Graph-based RAG Automatically Evolve through Feedback-driven Backpropagation**
- **Building Trust in the Skies: A Knowledge-Grounded LLM-based Framework for Aviation Safety**
- **Knowledge Is Not Static: Order-Aware Hypergraph RAG for Language Models**

### Common Innovation Types:
- **retrieval_method**: Hypergraph construction, temporal knowledge representation
- **system_or_architecture**: Self-evolving knowledge structures, dual-phase pipelines
- **generation_method**: Knowledge integration techniques for structured domains

### Ambiguous Areas:
- **Dynamic vs. static knowledge**: Trade-offs between pre-constructed and evolving knowledge graphs
- **Knowledge granularity**: Optimal level of knowledge structuring for different domains
- **Multi-modal knowledge integration**: Combining structured knowledge with unstructured text and visual data

## 3. Multimodal and Visual RAG (多模态与视觉RAG)
**Evidence Count:** 8

### Representative Papers:
- **AeroRAG: Structured Multimodal Retrieval-Augmented LLM for Fine-Grained Aerial Visual Reasoning**
- **CodeMMR: Bridging Natural Language, Code, and Image for Unified Retrieval**
- **KIRA: Knowledge-Intensive Image Retrieval and Reasoning Architecture for Specialized Visual Domains**
- **UniDoc-RL: Coarse-to-Fine Visual RAG with Hierarchical Actions and Dense Rewards**
- **AffectAgent: Collaborative Multi-Agent Reasoning for Retrieval-Augmented Multimodal Emotion Recognition**

### Common Innovation Types:
- **system_or_architecture**: Unified frameworks for cross-modal reasoning
- **retrieval_method**: Visual knowledge extraction, hierarchical scene understanding
- **benchmark_or_evaluation**: New benchmarks for visual RAG evaluation

### Ambiguous Areas:
- **Visual-text alignment**: Methods for bridging modality gaps remain inconsistent
- **Cross-modal retrieval**: Optimal strategies for query types across modalities
- **Evaluation metrics**: Limited standardized metrics for multimodal RAG performance

## 4. Agentic and Multi-Agent RAG (智能体与多智能体RAG)
**Evidence Count:** 9

### Representative Papers:
- **MASS-RAG: Multi-Agent Synthesis Retrieval-Augmented Generation**
- **AutoSearch: Adaptive Search Depth for Efficient Agentic RAG via Reinforcement Learning**
- **Toward Agentic RAG for Ukrainian**
- **VISOR: Agentic Visual Retrieval-Augmented Generation via Iterative Search and Over-horizon Reasoning**
- **PRIME: Training Free Proactive Reasoning via Iterative Memory Evolution for User-Centric Agent**

### Common Innovation Types:
- **system_or_architecture**: Multi-agent frameworks, collaborative reasoning
- **retrieval_method**: Agent-based retrieval strategies, active knowledge navigation
- **generation_method**: Agent-based generation, coordination mechanisms

### Ambiguous Areas:
- **Agent specialization**: Optimal division of labor among specialized agents
- **Coordination mechanisms**: Methods for agent communication and collaboration
- **Scalability**: Challenges in scaling multi-agent systems to complex tasks

## 5. Domain-Specific RAG Applications (领域特定RAG应用)
**Evidence Count:** 27

### Representative Papers:
- **Architecture Matters More Than Scale: A Comparative Study of Retrieval and Memory Augmentation for Financial QA Under SME Compute Constraints**
- **RAVEN: Retrieval-Augmented Vulnerability Exploration Network for Memory Corruption Analysis in User Code and Binary Programs**
- **LLM4C2Rust: Large Language Models for Automated Memory-Safe Code Transpilation**
- **Enhancing Mental Health Counseling Support in Bangladesh using Culturally-Grounded Knowledge**
- **LR-Robot: An Human-in-the-Loop LLM Framework for Systematic Literature Reviews with Applications in Financial Research**

### Common Innovation Types:
- **system_or_architecture**: Domain-specific architectures, knowledge integration
- **retrieval_method**: Specialized retrieval techniques for domain requirements
- **generation_method**: Domain-constrained generation methods

### Ambiguous Areas:

---

Generated from 127 structured paper cards. Model: glm-4.5-air. Generated at: 2026-04-27T07:50:42.636888+00:00.
