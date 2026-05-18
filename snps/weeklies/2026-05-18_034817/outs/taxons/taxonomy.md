# Retrieval-Augmented Generation (RAG) Taxonomy

## Core Retrieval and Ranking Methods (Core Retrieval and Ranking Methods)
**Evidence Count:** 94

**Representative Papers:**
- WorldDB: A Vector Graph-of-Worlds Memory Engine with Ontology-Aware Write-Time Reconciliation
- ArbGraph: Conflict-Aware Evidence Arbitration for Reliable Long-Form Retrieval-Augmented Generation
- LAnR (Latent Abstraction for RAG)
- QREAM: Question-Oriented Document Rewriting for Retrieval-Augmented Generation
- Skill-RAG: Failure-State-Aware Retrieval Augmentation via Hidden-State Probing and Skill Routing
- NaviRAG: Towards Active Knowledge Navigation for Retrieval-Augmented Generation

**Common Innovation Types:**
- system_or_architecture
- retrieval_method
- generation_method

**Ambiguous/Low-Confidence Areas:**
- The boundary between retrieval methods and generation methods is sometimes unclear
- Papers focusing on core retrieval methods often have overlapping approaches with knowledge graph-based methods
- Some methods blur the line between retrieval and reasoning components

## Agentic and Multi-Agent RAG (Agentic and Multi-Agent RAG)
**Evidence Count:** 22

**Representative Papers:**
- MASS-RAG: Multi-Agent Synthesis Retrieval-Augmented Generation
- AutoSearch: Adaptive Search Depth for Efficient Agentic RAG via Reinforcement Learning
- Beyond Arrow's Impossibility: Fairness as an Emergent Property of Multi-Agent Collaboration
- VISOR: Agentic Visual Retrieval-Augmented Generation via Iterative Search and Over-horizon Reasoning
- PRIME: Training Free Proactive Reasoning via Iterative Memory Evolution for User-Centric Agent

**Common Innovation Types:**
- system_or_architecture
- retrieval_method

**Ambiguous/Low-Confidence Areas:**
- The distinction between single-agent and multi-agent approaches is not always clearly defined
- Some papers describe frameworks that could be implemented with either single or multiple agents
- The level of agent autonomy varies significantly across papers

## Knowledge Graph and Structured Knowledge RAG (Knowledge Graph and Structured Knowledge RAG)
**Evidence Count:** 12

**Representative Papers:**
- EvoRAG: Making Knowledge Graph-based RAG Automatically Evolve through Feedback-driven Backpropagation
- Knowledge Is Not Static: Order-Aware Hypergraph RAG for Language Models
- Building Trust in the Skies: A Knowledge-Grounded LLM-based Framework for Aviation Safety
- EHRAG: Bridging Semantic Gaps in Lightweight GraphRAG via Hybrid Hypergraph Construction and Retrieval

**Common Innovation Types:**
- system_or_architecture
- retrieval_method

**Ambiguous/Low-Confidence Areas:**
- Some structured knowledge approaches could be considered under core retrieval methods
- The level of graph structure complexity varies significantly
- The distinction between knowledge graphs and other structured representations is sometimes unclear

## Multimodal and Visual RAG (Multimodal and Visual RAG)
**Evidence Count:** 15

**Representative Papers:**
- AeroRAG: Structured Multimodal Retrieval-Augmented LLM for Fine-Grained Aerial Visual Reasoning
- KIRA: Knowledge-Intensive Image Retrieval and Reasoning Architecture for Specialized Visual Domains
- CodeMMR: Bridging Natural Language, Code, and Image for Unified Retrieval
- UniDoc-RL: Coarse-to-Fine Visual RAG with Hierarchical Actions and Dense Rewards
- AffectAgent: Collaborative Multi-Agent Reasoning for Retrieval-Augmented Multimodal Emotion Recognition

**Common Innovation Types:**
- system_or_architecture
- retrieval_method

**Ambiguous/Low-Confidence Areas:**
- The definition of "multimodal" varies across papers (text+image, text+code, etc.)
- Some approaches focus primarily on one modality with minimal integration
- The level of cross-modal reasoning capabilities differs significantly

## Domain-Specific RAG Applications (Domain-Specific RAG Applications)
**Evidence Count:** 39

**Representative Papers:**
- Architecture Matters More Than Scale: A Comparative Study of Retrieval and Memory Augmentation for Financial QA Under SME Compute Constraints
- RAVEN: Retrieval-Augmented Vulnerability Exploration Network for Memory Corruption Analysis in User Code and Binary Programs
- LLM4C2Rust: Large Language Models for Automated Memory-Safe Code Transpilation
- LR-Robot: An Human-in-the-Loop LLM Framework for Systematic Literature Reviews with Applications in Financial Research
- BLUEmed: Retrieval-Augmented Multi-Agent Debate for Clinical Error Detection

**Common Innovation Types:**
- system_or_architecture
- generation_method
- retrieval_method

**Ambiguous/Low-Confidence Areas:**
- The boundary between domain-specific applications and core retrieval methods is sometimes unclear
- Some applications have domain-specific adaptations that could be generalized
- The level of domain expertise required varies significantly

## Evaluation, Benchmarks, and Diagnostics (Evaluation, Benchmarks, and Diagnostics)
**Evidence Count:** 19

**Representative Papers:**
- MathNet: a Global Multimodal Benchmark for Mathematical Reasoning and Retrieval
- CARE: Context-Aware Retriever Evaluation strategy for better evaluating multi-hop reasoning in RAG systems
- TeleEmbedBench: A Multi-Corpus Embedding Benchmark for RAG in Telecommunications
- FRESCO: Benchmarking and Optimizing Re-rankers for Evolving Semantic Conflict in Retrieval-Augmented Generation
- Facet-Level Tracing of Evidence Uncertainty and Hallucination in RAG

**Common Innovation Types:**
- benchmark_or_evaluation
- theoretical_analysis

**Ambiguous/Low-Confidence Areas:**
- Some evaluation frameworks are specific to certain R

---

Generated from 307 structured paper cards. Model: glm-4.5-air. Generated at: 2026-05-18T03:47:45.825772+00:00.
