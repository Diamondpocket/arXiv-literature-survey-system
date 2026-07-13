# RAG Literature Survey Taxonomy

## Core Retrieval and Ranking Methods (Core Retrieval and Ranking Methods)
- **Evidence Count**: 28 papers
- **Representative Papers**:
  - "WorldDB: A Vector Graph-of-Worlds Memory Engine with Ontology-Aware Write-Time Reconciliation"
  - "Semantic Entanglement in Vector-Based Retrieval: A Formal Framework and Context-Conditioned Disentanglement Pipeline for Agentic RAG Systems"
  - "Latent Abstraction for Retrieval-Augmented Generation"
- **Common Innovation Types**:
  - system_or_architecture (10)
  - retrieval_method (9)
  - generation_method (6)
  - benchmark_or_evaluation (3)
- **Ambiguous Areas**:
  - Evaluation metrics are inconsistent across studies, making direct comparisons difficult
  - The distinction between retrieval methods and system architectures is sometimes unclear in the literature
  - Limited understanding of how different retrieval strategies scale with document size and complexity

## Agentic and Multi-Agent RAG (Agentic and Multi-Agent RAG)
- **Evidence Count**: 11 papers
- **Representative Papers**:
  - "MASS-RAG: Multi-Agent Synthesis Retrieval-Augmented Generation"
  - "AutoSearch: Adaptive Search Depth for Efficient Agentic RAG via Reinforcement Learning"
  - "VISOR: Agentic Visual Retrieval-Augmented Generation via Iterative Search and Over-horizon Reasoning"
- **Common Innovation Types**:
  - system_or_architecture (8)
  - retrieval_method (2)
  - benchmark_or_evaluation (1)
- **Ambiguous Areas**:
  - Defining clear boundaries between agentic and non-agentic RAG systems
  - Understanding the optimal level of agent autonomy for different tasks
  - Evaluation metrics for multi-agent collaboration effectiveness

## Domain-Specific RAG Applications (Domain-Specific RAG Applications)
- **Evidence Count**: 22 papers
- **Representative Papers**:
  - "RAVEN: Retrieval-Augmented Vulnerability Exploration Network for Memory Corruption Analysis in User Code and Binary Programs"
  - "Architecture Matters More Than Scale: A Comparative Study of Retrieval and Memory Augmentation for Financial QA Under SME Compute Constraints"
  - "PriHA: A RAG-Enhanced LLM Framework for Primary Healthcare Assistant in Hong Kong"
- **Common Innovation Types**:
  - system_or_architecture (11)
  - benchmark_or_evaluation (5)
  - retrieval_method (4)
  - generation_method (2)
- **Ambiguous Areas**:
  - Domain-specific adaptations versus general RAG improvements
  - Determining which innovations are transferable across domains
  - Evaluating domain-specific performance without ground truth benchmarks

## Multimodal and Visual RAG (Multimodal and Visual RAG)
- **Evidence Count**: 8 papers
- **Representative Papers**:
  - "AeroRAG: Structured Multimodal Retrieval-Augmented LLM for Fine-Grained Aerial Visual Reasoning"
  - "KIRA: Knowledge-Intensive Image Retrieval and Reasoning Architecture for Specialized Visual Domains"
  - "UniDoc-RL: Coarse-to-Fine Visual RAG with Hierarchical Actions and Dense Rewards"
- **Common Innovation Types**:
  - system_or_architecture (5)
  - retrieval_method (3)
- **Ambiguous Areas**:
  - Balancing different modalities (text, image, audio) in retrieval
  - Evaluating multimodal retrieval quality
  - Understanding cross-modal semantic alignment challenges

## Knowledge Graph and Structured Knowledge RAG (Knowledge Graph and Structured Knowledge RAG)
- **Evidence Count**: 4 papers
- **Representative Papers**:
  - "EHRAG: Bridging Semantic Gaps in Lightweight GraphRAG via Hybrid Hypergraph Construction and Retrieval"
  - "Building Trust in the Skies: A Knowledge-Grounded LLM-based Framework for Aviation Safety"
  - "Knowledge Is Not Static: Order-Aware Hypergraph RAG for Language Models"
- **Common Innovation Types**:
  - retrieval_method (2)
  - system_or_architecture (2)
- **Ambiguous Areas**:
  - Trade-offs between structured knowledge and flexible retrieval
  - Scalability of knowledge graph construction for large domains
  - Measuring the impact of knowledge structure on retrieval quality

## Evaluation, Benchmarks, and Diagnostics (Evaluation, Benchmarks, and Diagnostics)
- **Evidence Count**: 13 papers
- **Representative Papers**:
  - "MathNet: a Global Multimodal Benchmark for Mathematical Reasoning and Retrieval"
  - "TeleEmbedBench: A Multi-Corpus Embedding Benchmark for RAG in Telecommunications"
  - "Facet-Level Tracing of Evidence Uncertainty and Hallucination in RAG"
- **Common Innovation Types**:
  - benchmark_or_evaluation (11)
  - system_or_architecture (2)
- **Ambiguous Areas**:
  - Establishing standardized evaluation protocols across different RAG systems
  - Measuring "utility" versus "relevance" in retrieval evaluation
  - Developing benchmarks that reflect real-world query complexity

## Reliability, Safety, Privacy, and Security (Reliability, Safety, Privacy, and Security)
- **Evidence Count**: 11 papers
- **Representative Papers**:
  - "ArbGraph: Conflict-Aware Evidence Arbitration for Reliable Long-Form Retrieval-Augmented Generation"
  - "Securing Retrieval-Augmented Generation: A Taxonomy of Attacks, Defenses, and Future Directions"
  - "ADAM: A Systematic Data Extraction Attack on Agent Memory via Adaptive Querying"
- **Common Innovation Types**:
  - system_or_architecture (6)
  -

---

Generated from 685 structured paper cards. Model: glm-4.5-air. Generated at: 2026-07-13T02:42:31.053343+00:00.
