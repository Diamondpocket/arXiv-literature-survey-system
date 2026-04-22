# RAG Literature Survey Taxonomy

## 1. Evaluation, Benchmarks, and Diagnostics (Evaluation, Benchmarks, and Diagnostics)
**Evidence Count**: 14

### Representative Papers:
- MathNet: a Global Multimodal Benchmark for Mathematical Reasoning and Retrieval
- Evaluating Multi-Hop Reasoning in RAG Systems: A Comparison of LLM-Based Retriever Evaluation Strategies
- FRESCO: Benchmarking and Optimizing Re-rankers for Evolving Semantic Conflict in Retrieval-Augmented Generation
- Exploring Knowledge Conflicts for Faithful LLM Reasoning: Benchmark and Method
- A Systematic Study of Retrieval Pipeline Design for Retrieval-Augmented Medical Question Answering

### Common Innovation Types:
- benchmark_or_evaluation
- retrieval_method

### Ambiguous or Low-Confidence Areas:
- LongFact and RAGChecker benchmarks need further validation across different domains
- ConflictQA benchmark may not capture all types of knowledge conflicts in real-world scenarios
- Evaluation metrics for adaptive RAG robustness to query variations need standardization

## 2. Core Retrieval and Ranking Methods (Core Retrieval and Ranking Methods)
**Evidence Count**: 28

### Representative Papers:
- WorldDB: A Vector Graph-of-Worlds Memory Engine with Ontology-Aware Write-Time Reconciliation
- DocQAC: Adaptive Trie-Guided Decoding for Effective In-Document Query Auto-Completion
- Latent Abstraction for Retrieval-Augmented Generation
- Semantic Entanglement in Vector-Based Retrieval: A Formal Framework and Context-Conditioned Disentanglement Pipeline for Agentic RAG Systems
- NaviRAG: Towards Active Knowledge Navigation for Retrieval-Augmented Generation

### Common Innovation Types:
- system_or_architecture
- retrieval_method
- generation_method

### Ambiguous or Low-Confidence Areas:
- HyperMem's hypergraph memory needs comparative evaluation against traditional graph-based approaches
- Adaptive Query Framework's tier-based approach may require different strategies for different domains
- Query-centric vector transformation for secure cross-organizational retrieval needs validation in real-world scenarios

## 3. Agentic and Multi-Agent RAG (Agentic and Multi-Agent RAG)
**Evidence Count**: 11

### Representative Papers:
- MASS-RAG: Multi-Agent Synthesis Retrieval-Augmented Generation
- AutoSearch: Adaptive Search Depth for Efficient Agentic RAG via Reinforcement Learning
- Beyond Arrow's Impossibility: Fairness as an Emergent Property of Multi-Agent Collaboration
- Toward Agentic RAG for Ukrainian
- VISOR: Agentic Visual Retrieval-Augmented Generation via Iterative Search and Over-horizon Reasoning

### Common Innovation Types:
- system_or_architecture
- retrieval_method

### Ambiguous or Low-Confidence Areas:
- Knowledge compounding concept needs empirical validation in production environments
- Practical limitations of offline agentic pipelines in real-world deployments
- PRIME's gradient-free learning framework needs comparative studies against traditional methods

## 4. Reliability, Safety, Privacy, and Security (Reliability, Safety, Privacy, and Security)
**Evidence Count**: 13

### Representative Papers:
- ArbGraph: Conflict-Aware Evidence Arbitration for Reliable Long-Form Retrieval-Augmented Generation
- Neuro-Symbolic Resolution of Recommendation Conflicts in Multimorbidity Clinical Guidelines
- A Case Study on the Impact of Anonymization Along the RAG Pipeline
- The Cognitive Circuit Breaker: A Systems Engineering Framework for Intrinsic AI Reliability
- Securing Retrieval-Augmented Generation: A Taxonomy of Attacks, Defenses, and Future Directions

### Common Innovation Types:
- system_or_architecture
- benchmark_or_evaluation

### Ambiguous or Low-Confidence Areas:
- CanaryRAG's canary tokens approach may face detection by sophisticated attackers
- Privacy implications of runtime integrity games need further investigation
- Frameworks like ADAM require ethical guidelines for responsible vulnerability disclosure

## 5. Domain-Specific RAG Applications (Domain-Specific RAG Applications)
**Evidence Count**: 19

### Representative Papers:
- Architecture Matters More Than Scale: A Comparative Study of Retrieval and Memory Augmentation for Financial QA Under SME Compute Constraints
- RAVEN: Retrieval-Augmented Vulnerability Exploration Network for Memory Corruption Analysis in User Code and Binary Programs
- LLM4C2Rust: Large Language Models for Automated Memory-Safe Code Transpilation
- BLUEmed: Retrieval-Augmented Multi-Agent Debate for Clinical Error Detection
- Policy-Aware Edge LLM-RAG Framework for Internet of Battlefield Things Mission Orchestration

### Common Innovation Types:
- system_or_architecture
- retrieval_method
- generation_method

### Ambiguous or Low-Confidence Areas:
- Frameworks for healthcare applications need rigorous validation with actual patient data
- Financial QA approaches may not generalize to other high-stakes domains
- Safety implications of policy-aware edge LLM-RAG in military applications require thorough assessment

## 6. Multimodal and Visual RAG (Multimodal and Visual RAG)
**Evidence Count**: 7

### Representative Papers:
- AeroRAG: Structured Multimodal Retrieval-Augmented LLM for Fine-Grained Aerial Visual Reasoning
- KIRA: Knowledge-Intensive Image Retrieval and Reasoning Architecture for Specialized Visual Domains
- UniDoc-RL: Coarse-to-Fine Visual RAG with Hierarchical Actions and Dense Rewards
- AffectAgent: Collaborative Multi-Agent Reasoning for Retrieval-Augmented Multimodal Emotion Recognition
- HOG-Layout: Hierarchical 3D Scene Generation, Optimization and Editing via Vision-Language Models

### Common Innovation Types:
- system_or_architecture
- retrieval_method

### Ambiguous or Low-Confidence Areas:
- Frameworks

---

Generated from 100 structured paper cards. Model: glm-4.5-air. Generated at: 2026-04-22T00:10:39.886782+00:00.
