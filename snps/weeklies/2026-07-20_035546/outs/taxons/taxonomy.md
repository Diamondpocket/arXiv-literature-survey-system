# Retrieval-Augmented Generation (RAG) Taxonomy

## 1. Core Retrieval and Ranking Methods (Core Retrieval and Ranking Methods)
- **Evidence Count**: 30 papers
- **Representative Papers**:
  - "WorldDB: A Vector Graph-of-Worlds Memory Engine with Ontology-Aware Write-Time Reconciliation"
  - "Semantic Entanglement in Vector-Based Retrieval: A Formal Framework and Context-Conditioned Disentanglement Pipeline for Agentic RAG Systems"
  - "Latent Abstraction for Retrieval-Augmented Generation"
  - "LAnR (Latent Abstraction for RAG), a unified framework where a single LLM jointly performs encoding, retrieval, and generation entirely within its own latent space."
- **Common Innovation Types**:
  - System or architecture (e.g., WorldDB, LAnR)
  - Retrieval method (e.g., ChunQiuTR for temporal retrieval)
  - Generation method (e.g., QREAM for document rewriting)
- **Ambiguous/Low-Confidence Areas**:
  - Effectiveness of latent space retrieval versus traditional retrieval methods
  - Optimal chunking strategies for different document types
  - Balance between retrieval and parametric knowledge utilization

## 2. Evaluation, Benchmarks, and Diagnostics (Evaluation, Benchmarks, and Diagnostics)
- **Evidence Count**: 10 papers
- **Representative Papers**:
  - "MathNet: a Global Multimodal Benchmark for Mathematical Reasoning and Retrieval"
  - "TeleEmbedBench: A Multi-Corpus Embedding Benchmark for RAG in Telecommunications"
  - "FRESCO: Benchmarking and Optimizing Re-rankers for Evolving Semantic Conflict in Retrieval-Augmented Generation"
- **Common Innovation Types**:
  - Benchmark or evaluation (most common)
  - System or architecture for evaluation
- **Ambiguous/Low-Confidence Areas**:
  - Generalizability of domain-specific benchmarks
  - Metrics that capture utility rather than just relevance
  - Evaluation of multi-hop reasoning across different domains

## 3. Agentic and Multi-Agent RAG (Agentic and Multi-Agent RAG)
- **Evidence Count**: 9 papers
- **Representative Papers**:
  - "MASS-RAG: Multi-Agent Synthesis Retrieval-Augmented Generation"
  - "AutoSearch: Adaptive Search Depth for Efficient Agentic RAG via Reinforcement Learning"
  - "Beyond Arrow's Impossibility: Fairness as an Emergent Property of Multi-Agent Collaboration"
- **Common Innovation Types**:
  - System or architecture (dominant)
  - Retrieval method
- **Ambiguous/Low-Confidence Areas**:
  - Optimal number of agents for specific tasks
  - Coordination mechanisms between agents
  - Scalability of multi-agent systems

## 4. Knowledge Graph and Structured Knowledge RAG (Knowledge Graph and Structured Knowledge RAG)
- **Evidence Count**: 5 papers
- **Representative Papers**:
  - "EHRAG: Bridging Semantic Gaps in Lightweight GraphRAG via Hybrid Hypergraph Construction and Retrieval"
  - "Knowledge Is Not Static: Order-Aware Hypergraph RAG for Language Models"
  - "Building Trust in the Skies: A Knowledge-Grounded LLM-based Framework for Aviation Safety"
- **Common Innovation Types**:
  - Retrieval method
  - System or architecture
- **Ambiguous/Low-Confidence Areas**:
  - Dynamic knowledge graph maintenance
  - Balancing structure with flexibility in knowledge representation
  - Knowledge fusion from multiple sources

## 5. Domain-Specific RAG Applications (Domain-Specific RAG Applications)
- **Evidence Count**: 25 papers
- **Representative Papers**:
  - "RAVEN: Retrieval-Augmented Vulnerability Exploration Network for Memory Corruption Analysis in User Code and Binary Programs"
  - "Architecture Matters More Than Scale: A Comparative Study of Retrieval and Memory Augmentation for Financial QA Under SME Compute Constraints"
  - "LR-Robot: An Human-in-the-Loop LLM Framework for Systematic Literature Reviews with Applications in Financial Research"
  - "BLUEmed: Retrieval-Augmented Multi-Agent Debate for Clinical Error Detection"
- **Common Innovation Types**:
  - System or architecture
  - Retrieval method
  - Generation method
- **Ambiguous/Low-Confidence Areas**:
  - Domain-specific versus general-purpose RAG effectiveness
  - Integration of domain-specific knowledge with general reasoning
  - Handling of domain-specific terminology and jargon

## 6. Multimodal and Visual RAG (Multimodal and Visual RAG)
- **Evidence Count**: 6 papers
- **Representative Papers**:
  - "AeroRAG: Structured Multimodal Retrieval-Augmented LLM for Fine-Grained Aerial Visual Reasoning"
  - "KIRA: Knowledge-Intensive Image Retrieval and Reasoning Architecture for Specialized Visual Domains"
  - "UniDoc-RL: Coarse-to-Fine Visual RAG with Hierarchical Actions and Dense Rewards"
- **Common Innovation Types**:
  - System or architecture
  - Retrieval method
- **Ambiguous/Low-Confidence Areas**:
  - Modality-specific retrieval strategies
  - Cross-modal knowledge integration
  - Evaluation metrics for multimodal reasoning

## 7. Reliability, Safety, Privacy, and Security (Reliability, Safety, Privacy, and Security)
- **Evidence Count**: 11 papers
- **Representative Papers**:
  - "ArbGraph: Conflict-Aware Evidence Arbitration for Reliable Long-Form Retrieval-Augmented Generation"
  - "Detecting RAG Extraction Attack via Dual

---

Generated from 766 structured paper cards. Model: glm-4.5-air. Generated at: 2026-07-20T03:54:46.776462+00:00.
