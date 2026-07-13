---
title: "The Chain Rule — How Neural Networks and LLMs Actually Learn"
description: "Part 2 of my LLM Basics series. What the chain rule is, why it is the engine behind the loss function, and how it lets an LLM with billions of weights learn."
---

> [!note] This is Part 2 of my LLM Basics series
> It builds directly on **Part 1: [[How-Neural-Networks-Work|How a Neural Network Works]]**. To follow this note, you only need these words from Part 1: **weight**, **bias**, **activation function**, and **training**. If any of those feel shaky, read Part 1 first — this note assumes nothing beyond it.

## 1. Where Part 1 left off (and the gap it left open)

In Part 1 we saw what a network *is*. Quick reminder, in one breath:

- A **neuron** (one small worker in the network) does two steps: first a straight-line step, `input × weight + bias`, then it bends the result with an **activation function**.
- Stack a few neurons, add their curves, and the network can form almost any shape to fit your data.
- We said the network finds the right **weights** (the adjustable numbers) by **training**: start with random numbers, see how wrong you are, and slowly fix the numbers.

But Part 1 quietly skipped the most important word. *How* does the network fix the numbers? When it is wrong, how does it know **which way to change each weight**, and by how much?

That "how" is this entire lecture. And the tool that makes it possible has a name: the **chain rule**. By the end you will see that the famous word **backpropagation** is nothing but the chain rule, used cleverly — and that this is exactly how a giant language model learns from text.

Let's build it from the ground up.

## 2. First idea: what a "rate of change" really is

Everything rests on one small idea, so let's make it rock solid.

A **derivative** — written $\frac{dy}{dx}$ and read *"the rate of change of y with respect to x"* — is just a **number that tells you how much the output moves when you give the input a tiny nudge.**

- If $\frac{dy}{dx} = 3$: nudge the input up a little, and the output goes up **3 times** as much.
- If $\frac{dy}{dx} = 0.5$: nudge the input up a little, and the output moves **half** as much.

So a derivative is a **sensitivity number**. It answers: *"if I wiggle the input, how big is the wiggle in the output?"* That is all. The scary `d` just means "a tiny change in."

![[chainrule-1-derivative.png]]
*The derivative at a point is the slope of the line that just touches the curve there. A steeper slope means the output reacts more strongly to a nudge in the input.*

One more thing to notice, because it matters later: the slope is **local**. On a curve, it is different at different places. Steep in some spots, gentle in others. So a derivative is always "the sensitivity *right here*, at the values you are currently at."

## 3. Second idea: steps that feed into each other

Real systems are built out of steps in a row, where each step's output becomes the next step's input:

$$X \rightarrow Y \rightarrow Z$$

Here `Y` depends on `X`, and `Z` depends on `Y`. So `Z` secretly depends on `X` too — but only **through** `Y`. `X` never touches `Z` directly; it has to go through the middle.

This "one thing feeds the next, which feeds the next" setup is called a **composite function** (a function whose input is itself the output of another function). Hold this picture — the chain rule is entirely about it.

## 4. The chain rule: multiply the rate of each link

Here is the rule, stated exactly:

$$\frac{dZ}{dX} = \frac{dZ}{dY} \times \frac{dY}{dX}$$

In plain words: **how strongly X affects Z = (how strongly Y affects Z) × (how strongly X affects Y).** You find the sensitivity of each link on its own, then **multiply them**.

**Why multiply?** Because effects *compound* as they pass down the chain. If `Y` moves twice as fast as `X`, and `Z` moves three times as fast as `Y`, then `Z` moves `2 × 3 = 6` times as fast as `X`. The push travels through the middle and gets scaled at each link.

![[chainrule-2-multiply.png]]
*You never measured "hours → score" directly. You got it by multiplying the two links you did know: 2 × 5 = 10.*

> [!tip] A quick way to picture it
> Loosely, it is like currency exchange. If 1 dollar buys 2 euros, and 1 euro buys 3 rupees, then 1 dollar buys `2 × 3 = 6` rupees — you multiply the exchange rates. Mapping it back: the "dollar → euro" rate is $\frac{dY}{dX}$, the "euro → rupee" rate is $\frac{dZ}{dY}$, and the combined "dollar → rupee" rate is $\frac{dZ}{dX}$. Where the picture breaks: exchange rates are fixed, but derivatives change from point to point — so you always use each link's rate *at your current spot*.

**A tiny check with real numbers.** Say the two links are:

- `Y = 2X`, so $\frac{dY}{dX} = 2$ (Y always changes twice as fast as X).
- `Z = Y²`, so $\frac{dZ}{dY} = 2Y$ (this rate depends on where Y currently is).

Chain rule:

$$\frac{dZ}{dX} = \frac{dZ}{dY} \times \frac{dY}{dX} = (2Y)(2) = 4Y = 4(2X) = 8X$$

Let's verify the slow way: put it together first, `Z = (2X)² = 4X²`, whose rate of change is `8X`. ✅ Same answer. The chain rule got the right result by handling one link at a time — and that "one link at a time" is the whole point, because in a real network you *cannot* squash everything into one neat formula.

## 5. The loss function: the number we are trying to shrink

Before we connect this to learning, we need one more term made precise.

When the network makes a prediction, we compare it to the correct answer and turn "how wrong were we" into a single number. That number is the **loss** (also called the **cost** or **error**), and the formula that produces it is the **loss function**, usually written `L`.

- Big `L` → the model is very wrong.
- Small `L` → the model is close to right.
- `L = 0` → perfect (never really happens, but that is the target).

So now we can say exactly what **training** means: **training is the search for the weights that make `L` as small as possible.** Nothing more mysterious than "turn the knobs until the wrongness is smallest."

Which brings us to the real question of this whole lecture.

## 6. The significance: connecting the loss back to every weight

To make `L` smaller, the network needs to know, for **each** weight `w`:

> *"If I nudge this one weight a little, does the loss go up or down, and by how much?"*

That question is exactly a derivative: $\frac{dL}{dw}$ — the sensitivity of the loss to that weight.

Here is the problem. The loss does **not** depend on a weight directly. It depends on it through a long chain of steps:

$$w \rightarrow \text{weighted sum} \rightarrow \text{activation} \rightarrow \text{prediction} \rightarrow \text{loss}$$

The weight is buried deep at the start; the loss sits far away at the end. You cannot write `L` as one simple formula of `w` — the chain is far too tangled. **This is precisely the situation the chain rule was made for.** You compute the sensitivity of each small link, then multiply them along the path:

$$\frac{dL}{dw} = \frac{dL}{d(\text{pred})} \times \frac{d(\text{pred})}{d(\text{act})} \times \frac{d(\text{act})}{d(\text{sum})} \times \frac{d(\text{sum})}{dw}$$

![[chainrule-3-backprop.png]]
*The loss's sensitivity to a buried weight = the local sensitivities multiplied all the way back along the path.*

Doing this — starting at the loss and applying the chain rule **backwards**, link by link, until you reach every weight — is **backpropagation** (short for "backward propagation of errors"), the standard training algorithm for neural networks.

So backpropagation is not a separate piece of magic. **It is the chain rule, run backwards through the network**, so that every weight learns how much it is to blame for the final wrongness. That is the significance you were asking about: *the chain rule is the only thing that lets a deeply-buried weight find out how it affected the loss at the very end.* Take it away, and there is no way to train — the weights would be flying blind.

## 7. From the slope to the fix: gradient descent

Once we have $\frac{dL}{dw}$ for a weight, using it is simple.

$\frac{dL}{dw}$ is a slope. Picture the loss as a valley, with the weight's value along the bottom axis:

![[chainrule-4-gradient-descent.png]]
*The slope tells you which way is uphill. To lower the loss, step the other way — a little at a time. That is gradient descent.*

- If the slope is **positive** (loss rises as `w` rises), then to lower the loss you make `w` **smaller**.
- If the slope is **negative**, you make `w` **bigger**.

Either way: **step in the opposite direction of the slope.** Take a small step, recompute, step again. Rolling downhill in small steps like this is called **gradient descent**.

Two last terms, now easy to define:

- The **gradient** is just the full collection of these slopes — one $\frac{dL}{dw}$ for *every* weight at once. It is the complete "which way is uphill" map for all the knobs together.
- **Gradient descent** is the act of nudging every weight a small step downhill, using that map.

And here is the beautiful part: backpropagation (the chain rule, backwards) computes the whole gradient — the slope for *every* weight — in **one single backward sweep** through the network. That efficiency is why training huge networks is even possible.

## 8. How this fits an LLM

An **LLM** (**Large Language Model** — the kind of model behind AI chat assistants) is, underneath, exactly the network from Part 1: neurons doing `weight × input + bias` and then a bend, stacked up. There are just two differences, and neither changes the idea:

1. It is enormous — **billions of weights** instead of a handful.
2. Its job is **next-token prediction**: a **token** is a word or word-piece, and the model's task is to read some text and predict the next token.

Now watch how everything we built clicks into place. To train it, you run this loop:

![[chainrule-5-llm-loop.png]]
*The exact same learn-by-being-wrong loop from Part 1 — just at massive scale.*

1. **Show it text**, for example `"The cat sat on the ___"`.
2. **It predicts the next token** — its best guess for the blank.
3. **Measure the loss.** Compare the guess to the real next word (`"mat"`). The loss function turns "how surprised was it by the true word" into one number `L`.
4. **Backpropagation** uses the **chain rule** to compute $\frac{dL}{dw}$ for **every one of the billions of weights** — how much each weight contributed to that wrongness — in a single backward pass.
5. **Gradient descent** nudges every weight a tiny step downhill.
6. **Repeat** over a staggering amount of text (trillions of tokens).

Do this enough times and the weights slowly settle into values that predict language astonishingly well. That "prediction machine," trained only to guess the next token, is what ends up able to answer questions and write text.

So the significance, stated plainly for LLMs: **the chain rule is the mechanism that lets an unimaginably deep, billion-weight model assign blame for a single wrong word all the way back to each individual weight — cheaply enough to do it trillions of times.** No chain rule → no backpropagation → no way to train an LLM at all. It is not a side-detail of deep learning; it is the engine.

## 9. Common misunderstandings to clear up

- **You multiply the *rates*, not the functions.** For `Z = Y²` and `Y = 2X`, you do not multiply `Y²` and `2X`. You multiply their derivatives, `2Y` and `2`.
- **The rates are local.** Each link's sensitivity depends on the actual numbers flowing through it at that moment, not a fixed value.
- **It is not limited to two links.** You can chain as many as you like: $\frac{dL}{dw} = \frac{dL}{da}\cdot\frac{da}{db}\cdot\frac{db}{dc}\cdots\frac{d(\cdot)}{dw}$. A deep network is simply a very long chain, so backpropagation multiplies many such terms.
- **Backpropagation is not a different idea from the chain rule.** It *is* the chain rule, organised to run once, backwards, so no work is repeated.

## 10. Terms recap

- **Derivative** $\big(\frac{dy}{dx}\big)$ — how much the output moves for a tiny nudge in the input; a "sensitivity."
- **Composite function** — steps feeding into each other (X → Y → Z).
- **Chain rule** — to get the far-apart sensitivity, multiply each link's sensitivity: $\frac{dZ}{dX} = \frac{dZ}{dY}\times\frac{dY}{dX}$.
- **Loss / loss function (`L`)** — one number for how wrong the model is; training tries to make it small.
- **Backpropagation** — the chain rule run backwards from the loss to every weight, giving each one its $\frac{dL}{dw}$.
- **Gradient** — the full set of those slopes, one per weight.
- **Gradient descent** — nudging every weight a small step in the downhill direction of the loss.
- **Token / next-token prediction** — a word-piece, and the LLM's core task of guessing the next one.

> [!tip] The one line to remember
> The **chain rule** lets you find how a change deep inside a chain affects the far end, by **multiplying the sensitivity of each link**. In a network, that far end is the **loss** and the deep-inside thing is a **weight** — so the chain rule (run backwards, as **backpropagation**) is exactly what tells every weight how to change to make the model less wrong. That is how everything from a tiny network to a billion-weight LLM learns.

## Related

- **Part 1:** [[How-Neural-Networks-Work|How a Neural Network Works]] — neurons, weights, and bending curves.
- **Coming next:** how these ideas scale into the pieces that make an LLM special, such as [[What-Is-Attention|attention]].
