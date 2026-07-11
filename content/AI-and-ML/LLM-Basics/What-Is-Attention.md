---
title: What Is Attention
---

Attention is the mechanism that lets a model decide which other words matter when it processes each word.

The intuition: for every token, the model asks three questions using learned projections:

- Query: what am I looking for?
- Key: what do I contain?
- Value: what do I pass along if someone looks at me?

Each token's output is a weighted average of all the Values, where the weights come from how well its Query matches every other token's Key. That is the whole trick — weighted averaging with learned weights.

Why it beats RNNs: every token attends to every other token in one step, so nothing gets forgotten across long distances, and it all runs in parallel on GPUs.

Things I still want to understand: multi-head attention, why scaling by sqrt(d) matters, and KV caching.
