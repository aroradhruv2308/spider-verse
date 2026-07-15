---
title: AI Engineering Roadmap — 1-Month Sprint
---

*A 4-week upskilling sprint: agents, evals, RAG internals, TypeScript, voice agents, and
fine-tuning. Each week = watch/read → build a small sandbox → write a notes page here →
prove it out loud. Tick a box, resync, done.*

**Progress:** Week 0 ☐ · Week 1 ☐ · Week 2 ☐ · Week 3 ☐ · Week 4 ☐

## Week 0 — Setup (one evening)

- [ ] API keys: Anthropic / OpenAI
- [ ] Free [Langfuse](https://langfuse.com) cloud account
- [ ] Docker Desktop working, Node 22, Python 3.11+ env
- [ ] Public repo `ai-engineering-sandbox` with folders `week1-agents` … `week4-breadth`
- [ ] GitHub profile cleaned up (photo, bio)

## Week 1 — Agents & LangGraph

**Learn**
- [ ] [LangChain Academy — Intro to LangGraph](https://academy.langchain.com/courses/intro-to-langgraph), modules 1–2 (graphs, state, nodes, edges)
- [ ] Modules 3–4 (memory, checkpointing) — or [LangGraph Essentials quickstart](https://academy.langchain.com/courses/langgraph-essentials-python)
- [ ] LangGraph docs: Concepts page
- [ ] Anthropic docs: tool use + structured outputs (vocabulary pass)

**Build — Sandbox 1: three-node agent**
- [ ] Node 1 plans → node 2 calls one real tool (weather/search API) → node 3 validates JSON output, retries once
- [ ] SqliteSaver checkpointing; kill mid-run, restart, watch it resume
- [ ] Push to `week1-agents` with README

**Prove**
- [ ] Can answer: what lives in state? why checkpoint before the LLM call? short-term vs long-term memory? when is a framework overkill?
- [ ] Notes page written: *LLM orchestration in my own words*
- [ ] Friday mock interview done

## Week 2 — Evals, Guardrails, Observability

**Learn**
- [ ] Hamel Husain — *Your AI Product Needs Evals*
- [ ] [promptfoo LLM-as-judge guide](https://www.promptfoo.dev/docs/guides/llm-as-a-judge/) + [DataCamp promptfoo tutorial](https://www.datacamp.com/tutorial/promptfoo-tutorial)
- [ ] [Langfuse LLM-as-judge video](https://langfuse.com/guides/videos/llm-as-a-judge-eval-on-dataset-experiments); wire tracing into Sandbox 1, read one full trace
- [ ] OWASP LLM Top 10 — prompt injection section (2 attacks, 1 mitigation each)

**Build — Sandbox 2: eval harness**
- [ ] Toy task (email summarizer) + 10–15 case golden dataset (incl. 2 injection attempts)
- [ ] promptfoo config with judge rubric (accuracy, completeness, tone)
- [ ] Run against 2 models; understand every score difference
- [ ] Eval runs in GitHub Actions on every push (regression gate)

**Prove**
- [ ] Can answer: golden dataset vs vibes? rubric vs pairwise? judge-bias controls? why evals on every change?
- [ ] Notes page + Friday mock interview

## Week 3 — RAG Internals: pgvector, Hybrid Search, Reranking

**Learn**
- [ ] LangChain *RAG From Scratch* — chunking, retrieval, reranking episodes
- [ ] [Instaclustr pgvector hybrid search tutorial](https://www.instaclustr.com/education/vector-database/pgvector-hybrid-search-benefits-use-cases-and-quick-tutorial/)
- [ ] Read every line of the official [pgvector cross-encoder example](https://github.com/pgvector/pgvector-python/blob/master/examples/hybrid_search/cross_encoder.py)
- [ ] Memorize the production shape: BM25 top-20 + vector top-20 → RRF merge → rerank → top 5 to the LLM

**Build — Sandbox 3: three-mode retrieval**
- [ ] Docker Postgres + pgvector; ingest 40–50 docs, chunk two ways (300 vs 800 tokens)
- [ ] Mode A vector-only · Mode B hybrid + RRF · Mode C hybrid + cross-encoder rerank
- [ ] Same 5 queries through all three; record the winner per query in the README

**Prove**
- [ ] Can answer: why hybrid wins on exact tokens? what the cross-encoder sees that embeddings can't? chunk size vs recall/precision? recall@k in one sentence?
- [ ] Notes page + Friday mock interview

## Week 4 — Breadth: TypeScript/Next.js · Voice · Fine-tuning

**TypeScript + Next.js (Mon–Wed)**
- [ ] [TS Handbook](https://www.typescriptlang.org/docs/handbook/): Basics → Everyday Types → Generics
- [ ] [Next.js Learn](https://nextjs.org/learn) — first half
- [ ] Mini-build: one typed React component + 2-page Next.js app locally

**Voice agent (Sat)**
- [ ] [Pipecat quickstart](https://docs.pipecat.ai/overview/introduction) voice bot running (STT → LLM → TTS)
- [ ] Change the system prompt, talk to it, find where latency hides
- [ ] Skim LiveKit Agents docs for the vocabulary

**Fine-tuning + vLLM (Sun)**
- [ ] [Unsloth fine-tuning guide](https://unsloth.ai/docs/get-started/fine-tuning-llms-guide) — run one free-Colab LoRA notebook end to end, understand every cell
- [ ] Serve a small model with vLLM once; hit it with curl
- [ ] Know the decision rule: prompt → RAG → fine-tune, in that order

**Prove**
- [ ] Can answer: what generics buy; the voice latency budget; LoRA in one paragraph; fine-tune vs RAG decision
- [ ] Notes page + final full-month mock interview

## After the sprint
- [ ] All four sandbox folders public and pinned on [GitHub](https://github.com/aroradhruv2308)
- [ ] One garden notes page per week published
- [ ] Pick the depth track the market pulls hardest (agents / evals / RAG) and go one level deeper
