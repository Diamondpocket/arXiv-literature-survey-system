# 检索增强生成 (RAG) 周度调查

## 1. 本周概览 Weekly Overview

本周共收集到134篇关于检索增强生成 (RAG) 的研究论文，形成了一个全面的证据基础。这些研究涵盖了RAG的多个方面，从基础检索方法到特定领域应用，从多智能体协作到安全可靠性。研究趋势表明，RAG工作正从通用检索管道向专门化方向发展，包括评估、领域适应、知识图谱或结构化知识、多模态设置以及面向可靠性设计的方法。研究方法层日益模块化，将检索器、重排序器、生成器、评估器以及有时是智能体或工具组件视为可分离的优化目标。评估和基准测试成为一个关键压力点，因为许多摘要强调性能主张，但并不总是暴露足够的指标。

## 2. 分类体系摘要 Taxonomy Summary

基于134篇论文的证据基础，RAG研究可归类为以下几个主要方向：

- **智能体与多智能体 RAG (Agentic and Multi-Agent RAG)** (22篇)：研究多智能体协作框架，如BLUEmed临床错误检测、AffectAgent多模态情感识别和Beyond Arrow's Impossibility公平性研究。这一类别主要探索智能体间的协作机制、通信协议以及如何确保一致性。

- **领域应用型 RAG (Domain-Specific RAG Applications)** (34篇)：包括软件测试与检查自动化、心理健康咨询支持、法律推理、金融分析等特定领域的应用。这些研究关注如何将RAG适配到特定领域的知识和需求。

- **多模态与视觉 RAG (Multimodal and Visual RAG)** (17篇)：研究视觉与文本的跨模态检索增强生成，如UniDoc-RL长文档视觉问答、VRAG-DFD深度伪造检测和KIRA专业知识密集型图像检索。

- **知识图谱与结构化知识 RAG (Knowledge Graph and Structured Knowledge RAG)** (11篇)：探索如何利用知识图谱增强检索效果，如Transforming External Knowledge into Triplets和Plasma GraphRAG等。

- **核心检索与排序方法 (Core Retrieval and Ranking Methods)** (22篇)：研究检索算法、排序策略和优化方法，如CARO内容审核推理优化和Beyond Factual Grounding观点感知检索增强生成。

- **评测、基准与诊断 (Evaluation, Benchmarks, and Diagnostics)** (12篇)：关注RAG系统的评估方法和基准测试，如FRESCO语义冲突基准测试和Facet-Level Tracing证据不确定性追踪。

- **可靠性、安全、隐私与防护 (Reliability, Safety, Privacy, and Security)** (15篇)：研究RAG系统的可靠性、安全性和隐私保护，如The Cognitive Circuit Breaker和Detecting RAG Extraction Attack等。

- **效率、部署与端侧 RAG (Efficiency, Deployment, and On-Device RAG)** (5篇)：关注RAG系统的效率优化和部署问题，如A Unified Model and Document Representation for On-Device Retrieval-Augmented Generation。

- **综述、理论与治理 (Survey, Theory, and Governance)** (8篇)：包括理论分析和综述研究，如Knowledge Compounding知识复合经济分析和Large Language Models to Enhance Business Process建模研究。

## 3. 方法对比摘要 Method Comparison

| 方法名称 | 复杂度 | 应用场景 | 优势 | 局限性 | 数据驱动 |
|---------|-------|---------|------|--------|---------|
| **软件测试与检查自动化** | 中等 | 软件测试和代码审查 | 通过RAG整合补充知识源，为测试用例生成和代码检查提供额外上下文 | 未知 | 是 |
| **城市视频视觉分析框架** | 中等 | 城市街道交叉口长视频分析 | 结合RAG、分类感知实体提取和视频定位支持事件检索和解释 | 未知 | 是 |
| **分层视觉RAG与层次动作** | 高 | 多模态视觉信息获取 | LVLM智能体联合执行检索、重排序、主动视觉感知和推理，通过层次动作逐步细化证据 | 未知 | 是 |
| **乌克兰智能体RAG** | 中等 | 多领域文档理解 | 结合两阶段检索和轻量级智能体层进行查询重构和答案重试 | 受限于离线智能体管道 | 是 |
| **人类参与文献综述框架** | 中等 | 金融研究文献综述 | 专家定义多维分类，LLM执行分类，人参与评估，RAG用于下游分析 | 未知 | 是 |
| **心理健康咨询支持** | 中等 | 孟加拉国心理咨询 | 比较RAG与手动构建知识图在提供文化适应性知识方面的效果 | 未知 | 是 |
| **企业知识导航系统** | 中等 | 企业客户支持 | 将文档语料库提取为离线层次化技能目录，智能体进行导航 | 未知 | 是 |
| **端侧统一模型表示** | 中等 | 敏感个人信息检索 | 统一检索和上下文压缩，使用相同表示，最小化磁盘利用和上下文大小 | 未知 | 是 |
| **长上下文自蒸馏** | 高 | 长文档理解和多文档推理 | 通过扰动RoPE索引形成训练序列的不同视图，通过自蒸馏确保预测一致性 | 未知 | 是 |
| **分段增强检索导向** | 中等 | 新兴实体分割任务 | 引入NEST任务和ROSE框架，增强MLLM分割模型与实时网络信息 | 未知 | 是 |

## 4. 趋势分析 Trend Analysis

当前RAG研究呈现几个明显趋势：

1. **从通用到专门**：RAG研究
