---
title: "Neural Networks — Inside the Black Box"
description: A plain-English walkthrough of StatQuest's neural-networks intro, and why a neuron does (m·x + c) before the activation function.
---

A **neural network** — a system of simple math units ("neurons") wired together in layers that turn an input into a prediction — looks intimidating: a tangle of circles and arrows. But StatQuest's ["Part 1: Inside the Black Box"](https://youtu.be/CqOfi41LfDw) has one big point: the tangle is doing something simple. It **bends a few basic curves and adds them together** until the result matches your data.

That's the whole idea. By the end of this note the mysterious "black box" is just four moves: take a straight-line step, bend it, scale it, add the pieces up. Every graph below was drawn from StatQuest's *actual* fitted numbers, so the curves here are literally the ones in his video.

## 1. The problem the network is solving

![[nn-statquest-1-data.png]]
*Figure 1 — The data: dosage vs. effectiveness. It's a bump, and no straight line fits it.*

The example is a drug. Along the bottom (the **x-axis** — the horizontal line showing the input) is the **dosage**. Up the side (the **y-axis** — the vertical line showing the output) is how **effective** it was. A low dose doesn't work. A high dose doesn't work. **A medium dose works.**

Look at the shape: up in the middle, down at both ends — a bump. A **straight line** (a relationship you can draw with one unbent line, where the output changes at a steady rate) can never match a bump; wherever you put the line, it's wrong somewhere (the red line above). We need something that can **curve**. That single need is the reason all the other machinery exists.

## 2. The building block: an activation function

![[nn-statquest-2-softplus.png]]
*Figure 2 — SoftPlus (blue) is flat, then bends upward. ReLU (grey) is another common shape.*

The curve-maker is called an **activation function** — a fixed, pre-chosen shape that a neuron applies to introduce a bend. StatQuest uses one named **SoftPlus** (formula `ln(1 + eˣ)`, read "the natural log of one plus e-to-the-x" — you don't need the formula, just the shape): flat for a while, then a smooth upward bend.

SoftPlus isn't magic; it's just easy to draw. Two other very common ones are **ReLU** (**Rectified Linear Unit** — flat at zero, then a straight ramp) and **sigmoid** (an S-shaped squash of any number into the range 0 to 1). The thing they all share: none of them is straight — they **bend**. Hold onto that; it's the whole game.

## 3. One neuron does two steps, in a fixed order

![[nn-statquest-4-network.png]]
*Figure 3 — Each neuron: first the straight-line step (×w + b), then the bend (activation).*

Follow one path from input to output. Every neuron does **two separate steps, always in this order**:

1. **The straight-line step: `x·w + b`.** Take the input `x`, multiply by a **weight** `w` (a number saying how much this input matters), then add a **bias** `b` (a number that shifts the result up or down). This is *exactly* the line the video writes as **`m·x + c`** — same thing, different letters.
2. **The bend: the activation.** Feed that result into the activation function. Out comes a curve.

So a neuron is literally **line first, bend second**:  `output = activation(x·w + b)`. The letters map like this:

| Line equation (video) | Neural-network word | What it does |
|---|---|---|
| `m` (slope) | weight `w` | how much the input matters / how steep the bend is |
| `x` | input | the data value coming in |
| `c` (intercept) | bias `b` | shifts the result up or down (slides the curve) |

## 4. The question: why `m·x + c` first, then the activation?

> [!question] The thing that trips people up
> **Why compute `m·x + c` first, and only then feed it into the activation?**
> Because the `m·x + c` step is the only place where the network can *steer* the activation. The activation is a **fixed** shape with no adjustable knobs of its own — so the network puts its two knobs, the **weight** and the **bias**, *in front of* it, to slide and stretch that fixed shape to wherever the data needs a bend.

![[nn-statquest-3-transform.png]]
*Figure 4 — The same SoftPlus shape, steered by different `w` and `b` before the bend.*

Figure 4 shows one SoftPlus shape transformed **before** it's bent:

- **Add a bias (`+b`)** → the whole curve **slides** left or right. This sets *where* the bend happens. (green)
- **Multiply by a weight (`×w`)** → the curve gets **steeper or gentler**. This sets *how sharply* it bends. (orange)
- **Use a negative weight** → the curve **flips** like a mirror, so a bend can point the other way. (purple)

If you ran the activation *first*, on the raw input, that fixed bend would land in one fixed spot and nothing downstream could move it to where your data actually turns. **Doing `m·x + c` first is what gives the network the steering.** During training the computer tunes `w` and `b` precisely to park each bend in the right place.

And why bend at all — why not just stack straight-line steps? Because **adding straight lines only ever gives another straight line.** Two stacked lines, `w₂(w₁x + b₁) + b₂`, simplify right back to a single `W·x + B` — still straight, still unable to make the bump. The bend breaks that collapse. A shape that can curve is called **nonlinear** (its graph is not a straight line), and nonlinearity is the one ingredient a bump-fitting machine cannot do without.

## 5. Putting it together — building the "squiggle"

![[nn-statquest-5-squiggle.png]]
*Figure 5 — Two bent curves, each scaled by an output weight, added up (+ a final bias) = the green squiggle that fits.*

Now the payoff. This network has **two** neurons in the middle — a **hidden layer** (the neurons between input and output that do the reshaping). Each makes its own bent curve (step 1, then step 2). Then each curve is multiplied by its **output weight** (blue × −1.30, orange × 2.28 — scaling them, and flipping the blue one), the two are **added together**, and a final **bias** (−0.58) shifts the total.

The result is the thick **green squiggle** — and it passes right through the data: low dose → about 0, medium → about 1, high → about 0. The machine has "learned" the bump. (Those exact numbers — −34.4, 2.14, −2.52, 1.29, −1.30, 2.28, −0.58 — are the ones StatQuest fits in the video.)

## 6. Where do the weights and biases come from?

Not by hand — by **training**. The network starts with random weights and biases, measures how wrong its squiggle is (the **loss** — a single number for total error), then uses **backpropagation** with **gradient descent** (a method that nudges every weight and bias a little in the direction that lowers the error, over and over) until the squiggle fits. Part 1 hands you the finished numbers on purpose, so you first understand the *shape* of the machine before the training math.

This is also why SoftPlus and sigmoid are smooth instead of having sharp corners: gradient descent needs a gentle slope to follow, and smooth curves give it one.

## 7. Key terms, in one place

- **Neural network** — layers of simple units that together turn an input into a prediction.
- **Weight (`w` / `m`)** — multiplier for an input; sets its importance and how steep the bend is.
- **Bias (`b` / `c`)** — a constant added on; slides the curve left/right (or up/down).
- **`m·x + c` = `x·w + b`** — the straight-line step; where all the adjustable knobs live.
- **Activation function** — a fixed nonlinear shape (SoftPlus, ReLU, sigmoid) that adds a bend.
- **Nonlinear** — a graph that is not a straight line; the ingredient that makes curves possible.
- **Hidden layer** — the neurons between input and output that reshape the signal.
- **Squiggle** — StatQuest's word for the final fitted curve the whole network produces.
- **Training / backpropagation / gradient descent** — the automatic process that finds good weights and biases by repeatedly reducing the error (the loss).

> [!tip] One-sentence takeaway
> A neuron does a straight-line step (`m·x + c`) to **position and scale** the input, then an activation to **bend** it — and the network adds up several bends to build any shape the data needs. The line comes first because it's the steering wheel; the activation is the wheel it steers.

## Related

- [[What-Is-Attention|What Is Attention]] — the next building block, once single neurons make sense.
