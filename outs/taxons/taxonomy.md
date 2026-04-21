# Taxonomy of Retrieval-Augmented Generation Research

## 1. Core Retrieval and Ranking Methods (核心检索与排序方法)
**Evidence Count:** 2

**Representative Papers:**
- WorldDB: A Vector Graph-of-Worlds Memory Engine with Ontology-Aware Write-Time Reconciliation
- DocQAC: Adaptive Trie-Guided Decoding for Effective In-Document Query Auto-Completion

**Common Innovation Types:**
- system_or_architecture
- retrieval_method

**Ambiguous or Low-Confidence Areas:**
- The performance metrics for DocQAC are unknown, requiring human evaluation of its effectiveness compared to traditional QAC methods.
- The relationship between the graph-based approach in WorldDB and traditional vector retrieval methods needs further clarification.

## 2. Agentic and Multi-Agent RAG (智能体与多智能体RAG)
**Evidence Count:** 1

**Representative Papers:**
- MASS-RAG: Multi-Agent Synthesis Retrieval-Augmented Generation

**Common Innovation Types:**
- system_or_architecture

**Ambiguous or Low-Confidence Areas:**
- The specific metrics for evaluating MASS-RAG are unknown, making it difficult to assess its effectiveness compared to single-agent RAG systems.
- The scalability of the multi-agent approach when handling large numbers of retrieved documents needs further investigation.

## 3. Reliability, Safety, Privacy, and Security (可靠性、安全性、隐私与安全)
**Evidence Count:** 1

**Representative Papers:**
- ArbGraph: Conflict-Aware Evidence Arbitration for Reliable Long-Form Retrieval-Augmented Generation

**Common Innovation Types:**
- system_or_architecture

**Ambiguous or Low-Confidence Areas:**
- While the approach addresses conflict resolution, the limitations of ArbGraph in handling complex, multi-faceted contradictions are not specified.
- The computational overhead of the conflict arbitration process needs further evaluation for real-time applications.

## 4. Evaluation, Benchmarks, and Diagnostics (评估、基准与诊断)
**Evidence Count:** 1

**Representative Papers:**
- MathNet: a Global Multimodal Benchmark for Mathematical Reasoning and Retrieval

**Common Innovation Types:**
- benchmark_or_evaluation

**Ambiguous or Low-Confidence Areas:**
- The limitations of the MathNet benchmark are not explicitly mentioned in the abstract, requiring human review to identify potential biases or gaps.
- The benchmark's effectiveness in evaluating non-mathematical reasoning capabilities needs further assessment.

---

Generated from 5 structured paper cards. Model: glm-4.5-air. Generated at: 2026-04-21T16:16:39.378914+00:00.
