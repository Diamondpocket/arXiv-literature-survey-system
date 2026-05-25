# Retrieval-Augmented Generation (RAG) Literature Survey Taxonomy

## 1. Core Retrieval and Ranking Methods (核心检索和排序方法)
**Evidence Count:** 93

### Representative Papers:
- "Latent Abstraction for Retrieval-Augmented Generation"
- "Semantic Entanglement in Vector-Based Retrieval: A Formal Framework and Context-Conditioned Disentanglement Pipeline for Agentic RAG Systems"
- "LAnR (Latent Abstraction for RAG), a unified framework where a single LLM jointly performs encoding, retrieval, and generation entirely within its own latent space"
- "Skill-RAG: Failure-State-Aware Retrieval Augmentation via Hidden-State Probing and Skill Routing"

### Common Innovation Types:
- System or architecture improvements
- Novel retrieval methods
- Generation methods
- Query transformation and optimization

### Ambiguous or Low-Confidence Areas:
- The boundary between retrieval and generation methods is sometimes unclear
- Confidence levels are generally high, but some approaches lack comprehensive evaluation
- The relationship between semantic entanglement and other retrieval challenges needs further investigation

## 2. Knowledge Graph and Structured Knowledge RAG (知识图谱和结构化知识RAG)
**Evidence Count:** 11

### Representative Papers:
- "EvoRAG: Making Knowledge Graph-based RAG Automatically Evolve through Feedback-driven Backpropagation"
- "Order-Aware Hypergraph RAG for Language Models"
- "Building Trust in the Skies: A Knowledge-Grounded LLM-based Framework for Aviation Safety"
- "Knowledge Is Not Static: Order-Aware Hypergraph RAG for Language Models"

### Common Innovation Types:
- Knowledge graph construction and evolution
- Structured knowledge representation
- Hypergraph-based approaches
- Knowledge compounding and updating mechanisms

### Ambiguous or Low-Confidence Areas:
- The scalability of knowledge graph approaches to very large corpora
- Optimal knowledge granularity and structure for different tasks
- Dynamic knowledge update mechanisms and their effectiveness

## 3. Multimodal and Visual RAG (多模态和视觉RAG)
**Evidence Count:** 14

### Representative Papers:
- "AeroRAG: Structured Multimodal Retrieval-Augmented LLM for Fine-Grained Aerial Visual Reasoning"
- "KIRA: Knowledge-Intensive Image Retrieval and Reasoning Architecture for Specialized Visual Domains"
- "UniDoc-RL: Coarse-to-Fine Visual RAG with Hierarchical Actions and Dense Rewards"
- "CodeMMR: Bridging Natural Language, Code, and Image for Unified Retrieval"

### Common Innovation Types:
- Cross-modal retrieval and alignment
- Visual-structured knowledge representation
- Hierarchical visual reasoning
- Multimodal context integration

### Ambiguous or Low-Confidence Areas:
- Handling complex visual relationships and spatial reasoning
- Evaluation metrics for multimodal RAG systems
- Integration of different modalities with varying levels of semantic richness

## 4. Domain-Specific RAG Applications (领域特定RAG应用)
**Evidence Count:** 49

### Representative Papers:
- "RAVEN: Retrieval-Augmented Vulnerability Exploration Network for Memory Corruption Analysis in User Code and Binary Programs"
- "Architecture Matters More Than Scale: A Comparative Study of Retrieval and Memory Augmentation for Financial QA Under SME Compute Constraints"
- "LLM4C2Rust: Large Language Models for Automated Memory-Safe Code Transpilation"
- "BLUEmed: Retrieval-Augmented Multi-Agent Debate for Clinical Error Detection"

### Common Innovation Types:
- Specialized knowledge integration for specific domains
- Domain-specific retrieval strategies
- Compliance and safety considerations in critical domains
- Multi-agent approaches for domain-specific tasks

### Ambiguous or Low-Confidence Areas:
- Domain adaptation strategies and their generalizability
- Balancing domain expertise with general reasoning capabilities
- Handling domain-specific knowledge evolution and updates

## 5. Evaluation, Benchmarks, and Diagnostics (评估、基准和诊断)
**Evidence Count:** 24

### Representative Papers:
- "MathNet: a Global Multimodal Benchmark for Mathematical Reasoning and Retrieval"
- "TeleEmbedBench: A Multi-Corpus Embedding Benchmark for RAG in Telecommunications"
- "Evaluating Multi-Hop Reasoning in RAG Systems: A Comparison of LLM-Based Retriever Evaluation Strategies"
- "Beyond Relevance: Utility-Centric Retrieval in the LLM Era"

### Common Innovation Types:
- New benchmark creation
- Evaluation methodologies for retrieval components
- Diagnostic frameworks for RAG systems
- Benchmarking under evolving conditions

### Ambiguous or Low-Confidence Areas:
- Developing standardized evaluation metrics across different RAG applications
- Benchmarking under adversarial conditions
- Evaluation of long-context and multi-hop reasoning scenarios

## 6. Reliability, Safety, Privacy, and Security (可靠性、安全、隐私和安全)
**Evidence Count:** 20

### Representative Papers:
- "ArbGraph: Conflict-Aware Evidence Arbitration for Reliable Long-Form Retrieval-Augmented Generation"
- "A Case Study on the Impact of Anonymization Along the RAG Pipeline"
- "The Cognitive Circuit Breaker: A Systems Engineering Framework for Intrinsic AI Reliability"
- "Detecting RAG Extraction Attack via Dual-Path Runtime Integrity Game"

### Common Innovation Types:
- Evidence conflict resolution
- Privacy-preserving retrieval mechanisms
- Security against extraction attacks
- Trustworthiness frameworks

### Ambiguous or Low-Confidence Areas:
- Balancing privacy with retrieval effectiveness
- Security in cross-organizational RAG systems
- Robustness against adversarial attacks

## 7. Agentic and Multi-Agent RAG (智能体和多智能体RAG)
**Evidence Count:** 17

### Representative Papers:
- "MASS

---

Generated from 358 structured paper cards. Model: glm-4.5-air. Generated at: 2026-05-25T03:49:35.898308+00:00.
