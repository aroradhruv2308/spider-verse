---
title: "How a Neural Network Works"
description: A simple, friendly explanation of how a neural network fits a curve to data — and why each neuron does its math in two steps.
---

Neural networks sound scary. People draw them as a big mess of circles and arrows and say no one can really understand what happens inside. But the main idea is actually simple.

Here is the whole secret in one line: **a neural network takes a few simple curves, bends them, and adds them together until they match your data.** That's it. Everything else is just detail.

Let's build that idea slowly, in plain language.

## 1. Start with the problem

The best way to understand a tool is to first see the problem it solves. So let's take a small, everyday example.

Imagine a medicine. If you take too little, it does nothing. If you take too much, it also does nothing. Only the right amount in the middle actually works.

![[nn-statquest-1-data.png]]
*A low dose does nothing. A high dose does nothing. Only a medium dose works.*

Look at the shape those dots make. They go up in the middle and down on both sides, like a little hill.

Now try to draw **one straight line** through those dots. (A straight line just means a plain, unbent line, the kind you draw with a ruler.) You can't do it. A straight line always heads in one direction, so it can never make a hill shape. Wherever you put it, it will be wrong somewhere. The red line shows this.

So we need something that can make **curves**, not just straight lines. That single need is the reason neural networks exist.

## 2. The one tool that makes curves

To make curves, a neural network uses a helper called an **activation function**. That is a fancy name for a simple idea: it is just a ready-made curved shape. You put a number in, and it gives a number back in a way that bends.

![[nn-statquest-2-softplus.png]]
*A ready-made curved shape. It stays flat for a while, then bends upward.*

The blue line above is one common activation function. The only thing you need to notice is that it is **not straight** — it bends. That bend is the important part.

There are a few popular activation functions, with names like SoftPlus, ReLU, and sigmoid. You don't need to memorize them. Just remember one thing about all of them: **they bend.** That bending is the whole trick.

## 3. What one neuron does: two steps, in order

Now let's look closely at a single **neuron**. A neuron is just one small worker inside the network. Each neuron does its job in two steps, and the order matters a lot.

**Step 1 — the straight-line step.**
The neuron takes your input number and does simple math on it. It **multiplies** the input by a number called a **weight**, and then **adds** another number called a **bias**.

- The **weight** decides how strongly the input counts.
- The **bias** shifts the answer up or down.

You may remember `y = m·x + c` from school — the formula for a straight line. This step is exactly that. The weight is like `m`, and the bias is like `c`. So step 1 is nothing more than a straight-line calculation.

**Step 2 — the bend.**
The neuron takes the result from step 1 and passes it through the activation function. This bends the straight-line result into a curve.

So a neuron always does this, in this order:

> **output = bend( input × weight + bias )**

![[nn-statquest-4-network.png]]
*One neuron: first the straight-line step, then the bend.*

Here are the same school letters next to the words a neural network uses:

| From school (`y = m·x + c`) | In a neural network | What it does |
|---|---|---|
| `m` | weight | how strongly the input counts (and how steep the bend is) |
| `x` | input | the number coming in |
| `c` | bias | shifts the result, and slides the curve left or right |

## 4. Why do the straight-line math first, and the bend after?

This is the part that confuses most people, so let's go slowly.

The activation function is a **fixed shape**. It always bends the same way, and you cannot change its shape directly. So here is the real question: how does the network make that bend happen in the right place, and at the right steepness, for *your* data?

The answer: it uses the **weight** and the **bias** from step 1 — *before* the bend.

> [!question] The key idea
> Think of the activation function as a stamp with a curved shape carved into it. The stamp's shape never changes. But before you press it down, you can **slide the paper** left or right, and you can **stretch the paper**. That sliding and stretching is exactly what the weight and bias do. Only after you set them do you press the stamp (the bend).

![[nn-statquest-3-transform.png]]
*The same curved shape, moved and stretched by the weight and bias before the bend.*

You can see all three effects in the picture above:

- The **bias slides** the curve left or right. It decides *where* the bend happens. (green)
- The **weight** makes the curve **steeper or gentler**. It decides *how sharp* the bend is. (orange)
- A **negative weight flips** the curve like a mirror, so the bend can face the other way. (purple)

Now the order makes sense. If you did the bend *first*, on the raw input, the curve would land in one fixed spot and you could never move it to fit your data. By doing the straight-line math first, you get to **place and shape** the curve exactly where you need it.

In one line: **the straight-line step is the steering wheel, and the bend is what it steers.**

And why bend at all? Why not just use straight-line steps? Because if you only add straight lines together, you always get another straight line. Two straight lines added still make a straight line, so no matter how many you stack, you could never make the hill shape. The bend is what breaks that limit and lets the network make real curves. (The proper word for "a shape that can curve" is **nonlinear**, which simply means "not a straight line.")

## 5. Putting the pieces together

One neuron makes one simple curve. That is not enough to make a whole hill. So the network uses a few neurons together and combines their curves.

Here is how the pieces come together:

1. Each neuron makes its own curve (straight-line step, then bend).
2. Each curve is multiplied by a number, which makes it bigger or smaller (and can flip it).
3. All the curves are added together.
4. One last number shifts the whole thing up or down.

![[nn-statquest-5-squiggle.png]]
*Two simple curves, resized and added together, make the final green curve that fits the dots.*

The thick green line is the final answer. Look at where it goes: low dose → almost nothing, medium dose → high, high dose → almost nothing. It matches the dots. The network has "learned" the hill shape, just by bending and adding simple curves.

## 6. Where do all these numbers come from?

So far we used the right weights and biases as if we already knew them. We don't — not at the start. The network begins with **random** numbers. Then it checks how wrong its curve is, and slowly adjusts every weight and bias to make the curve fit a little better. It repeats this again and again until the curve matches the data.

This slow adjusting is called **training**. You will also hear the names **backpropagation** and **gradient descent** for the method, but the idea behind it is simple: guess, check the mistake, adjust, and repeat.

## 7. Quick recap

- **Neuron** — one small worker inside the network.
- **Weight** — a number that decides how strongly the input counts (and how steep the bend is).
- **Bias** — a number that shifts the result and slides the curve left or right.
- **Straight-line step** (`input × weight + bias`) — the first thing a neuron does; the same as `y = m·x + c`.
- **Activation function** — a ready-made curved shape that adds a bend.
- **Nonlinear** — just a word for "not a straight line."
- **Training** — the slow process of adjusting the numbers until the curve fits.

> [!tip] Remember this one line
> A neuron first does simple straight-line math to **place and size** the input, then **bends** it with an activation function. The network adds up many small bends to build any shape it needs. The straight-line step comes first because it is the steering wheel; the bend is what it steers.

## Related

- [[What-Is-Attention|What Is Attention]] — a good next step, once single neurons make sense.
