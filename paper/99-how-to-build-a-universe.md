# Are Weyl Gravity’s Ghosts Real?

*Building model universes—and using AI—to find out*

*By GPT-5.6.sol and Asger Alstrup Palm*

Einstein’s theory says that gravity is the shape of spacetime. It has passed
an extraordinary range of tests. But it also leaves deep questions open,
including how gravity behaves as a quantum theory.

Pure Weyl gravity is a more symmetric alternative. Its equations contain
four derivatives instead of two and do not introduce a fundamental length
scale. That mathematical elegance comes with a famous danger: the equations
have additional solutions, and some appear with the “wrong” sign. They are
usually called **ghosts**.

Does that end the theory?

Perhaps. But “ghost” can refer to several different things:

- an extra solution of a differential equation;
- a classical wave remaining after gauge freedom and constraints are removed;
- a disturbance that survives nonlinear interactions;
- or a negative-probability particle in a quantum theory.

Those are not the same claim. Our project tests them separately.

It is also an experiment in how research is done. Asger Alstrup Palm is a
computer scientist, not a professional physicist. He directs AI systems that
propose calculations, write and check code, search the literature, criticize
arguments, and draft papers. The goal is not to show that AI can declare a
new law of nature. The goal is to see whether a non-expert who knows how to
work with AI can orchestrate research that becomes precise enough for experts
to verify, correct, or reject.

This article explains what the project has actually found—and what it has
not.

## A four-stage ghost test

We use four stages.

### 1. Local equations

What waves do the equations allow near a chosen background?

Fourth-order equations normally contain more local solutions than Einstein’s
second-order equations. This is the easiest level to calculate and the
easiest to overinterpret.

### 2. Classical reality

Which solutions remain after coordinate freedom, conformal gauge freedom,
global charges, boundary conditions, and zero directions of the physical
pairing are removed?

An extra formula may turn out to describe the same geometry in different
coordinates. But some additional Weyl-gravity waves survive these tests and
have nonzero action-derived pairings. They cannot all be dismissed as
duplicated algebra.

### 3. Nonlinear continuation

Can a small wave be the first term of a genuine solution once waves
themselves gravitate and interact?

On compact model universes, we found exact global balance conditions. Some
waves fail because their second-order backreaction carries an uncancelled
charge. Even after those balances vanish, resonance can force corrections
that grow with time. Formal continuation and bounded continuation are
therefore different achievements.

### 4. Quantum states

Does the final theory have a positive probability rule, consistent gauge
symmetry, and well-defined particles and interactions?

We are not there. The strict pure-Weyl theory has a nonzero local one-loop
quantum anomaly in the version tested. A compensating field can repair that
local identity at the tested order, but adding the field changes the theory.
No positive complete quantum state space or unitarity theorem has been
constructed.

## Why build several model universes?

No single spacetime makes every question manageable. We therefore use
different mathematical laboratories:

- a two-frequency oscillator for the basic fourth-order sign problem;
- a closed spherical universe for gauge symmetry and causal propagation;
- compact gravity-and-light models for nonlinear balance and clocks;
- Schwarzschild black holes for horizons, radiation, and ringing;
- Euclidean backgrounds for quantum anomalies.

A result in one laboratory is not silently transferred to another. That rule
is one of the project’s main safeguards.

## What Phase 1 found

The first phase did not produce a healthy replacement for general
relativity. It produced a classification.

Some additional fourth-order directions survive the early classical tests.
Some are removed by nonlinear balance or resonance. A modified gravity–clock
model passed a demanding causal test, but its physical reduced system
developed a robust oscillatory instability. The quantum calculation found a
strict local anomaly, while a compensator repair belonged to a changed
theory.

So the verdict is neither:

> “The ghosts were harmless.”

nor:

> “Every form of Weyl gravity has been ruled out.”

It is:

> Different candidates fail at different stages, and none tested so far has
> passed all four.

The stable technical synthesis is
[Paper 15, *What Survives the Ghost Test?*](15-four-level-ghost-classification-phase1-synthesis.pdf).

## The newest black-hole result

Black holes provide the sharpest result so far.

A disturbed Schwarzschild black hole rings at characteristic complex
frequencies called **quasinormal modes**. In ordinary general relativity, the
mode falls into the black hole at the horizon and radiates outward at
infinity.

One might hope that these natural radiation conditions automatically remove
Weyl gravity’s additional solutions and leave only Einstein’s waves. They do
not.

For axial quadrupole disturbances—the odd-parity, angular-momentum
$\ell=2$ sector—the complete Weyl system contains:

- one ordinary spin-two Regge–Wheeler layer;
- a second spin-two layer;
- and a spin-one Maxwell-like layer.

The two spin-two layers are not independent copies. They form a
**non-split extension**: one layer is attached to the other in a way that
cannot be removed by the rational local changes of variables tested in the
paper.

This matters at a particular validated Schwarzschild ringing frequency. The
ordinary Einstein mode becomes a defective resonance:

- there is one ordinary Einstein ringing pattern;
- there is a generalized partner with genuine non-Einstein curvature;
- together they form a two-step chain.

In frequency language, the local radial response has a **double pole**
instead of an ordinary simple pole. In time language, an isolated resonance
contour contains

$$
e^{i\omega_n t}\left(V_1+i t\,V_0\right).
$$

Here $V_0$ is the ordinary Einstein quasinormal mode and $V_1$ is its
generalized Weyl partner. The unusual part is the extra factor of time:

$$
t\,e^{-\gamma t}\cos(\Omega t+\phi).
$$

It is a transient enhancement, not an instability. The exponential damping
eventually wins.

This resembles the “logarithmic graviton” mechanism known from critical
gravity, where a massive and a massless spin-two mode merge. In the
asymptotically flat Schwarzschild problem, however, the endpoint tangent is
polynomial rather than a separate radial logarithm. “Jordan partner” or
“polynomial quasinormal partner” is less misleading.

The detailed result is in
[Paper 16](16-lorentzian-endpoint-nonselection-pure-weyl.pdf) and
[Paper 17](17-pure-weyl-schwarzschild-extension-structure.pdf).

## What the black-hole theorem does not say

The distinction here is essential.

The project has established:

- non-selection by the tested standard Lorentzian endpoint conditions;
- a non-split axial $\ell=2$ spin-two extension;
- one validated defective quasinormal resonance;
- a nonzero rank-one double pole of the compactly observed radial response;
- nonzero outgoing gravitational-wave content in the leading pole;
- a complexified, radially compact frequency-domain source that can excite
  the corresponding adjoint channel;
- the expected linear-in-time term for an isolated local resonance contour.

It has **not** established:

- a complete causal evolution theorem for the full Schwarzschild exterior;
- that the full late-time signal can be obtained by deforming a contour onto
  this pole;
- excitation by a specified real astrophysical source;
- the size of a signal in a detector;
- the full polar or all-multipole result;
- stability against every time-dependent disturbance;
- or a healthy quantum interpretation.

In public terms: we have found a mathematically sharp way in which the extra
Weyl layer can alter black-hole ringing. We have not shown that an
astronomical detector would see it.

## Why this is already interesting

The result goes beyond saying that a fourth-order equation contains a
repeated second-order factor. Repetition alone could mean two independent
copies. Instead, the calculation shows an inseparable extension, a
generalized non-Einstein mode, and a genuine double response pole.

That is useful even if Weyl gravity ultimately fails:

1. It identifies the precise spectral signature of the extra structure.
2. It shows that standard black-hole radiation conditions do not perform the
   same selection as some Euclidean or cosmological boundary prescriptions.
3. It separates stability from response amplification: no exponentially
   growing separated axial mode is found, yet the response is non-normal and
   defective.
4. It gives future calculations a concrete target: a globally causal
   $t e^{i\omega t}$ waveform with a real source and observable.

## The next decisive work

Scientific progress now requires fewer broad manifestos and more narrow
bridges:

1. independently reproduce the exceptional-point and double-pole
   certificates;
2. construct the complete massive spin-two axial system and match it to the
   Weyl tangent, not merely its scalar graded part;
3. build a closed global causal domain that allows the differentiated
   outgoing state;
4. justify the inverse-Laplace contour deformation;
5. calculate excitation by a real source, such as a plunging compact object;
6. reconstruct the asymptotic strain and determine the detector coefficient;
7. complete the polar and broader angular sectors;
8. determine whether any compatible quantum theory has a positive physical
   state space.

These steps could strengthen the interpretation, narrow it, or disprove it.
All three outcomes would be progress.

## The AI research experiment

AI can produce an impressive-looking derivation that is wrong. Multiple AI
systems can also repeat the same mistake. We therefore do not count polished
text or repeated calculation as independent confirmation.

The repository tries to make the process auditable:

```text
claim
  → generating calculation
  → machine-readable certificate
  → independent verifier
  → deliberately damaged test
  → paper with explicit limitations
```

Failures and corrections remain in the record. Exact algebra is kept
separate from interval-validated numerics and from exploratory computation.
A missing certificate, timeout, or unsupported parameter range is a failure
to promote the claim—not a partial success.

The experiment will not be validated by us saying that it worked. It needs
physicists and mathematicians to inspect the equations, reproduce the
computations, find errors, and decide whether anything is genuinely new and
useful.

## Public scorecard

**We have:** exact model calculations of fourth-order metrics and Jordan
limits; complete causal free gauge systems on controlled backgrounds; a
nonzero strict local one-loop anomaly; Schwarzschild endpoint non-selection;
one defective axial QNM; reproducible code and many certificate families.

**We partly have:** classical additional waves on selected backgrounds;
nonlinear continuation in finite mode spaces; a compensator repair in a
changed theory; a local isolated-contour polynomial ringdown term; and
independent verification of selected claims.

**We do not yet have:** a viable replacement for general relativity,
realistic cosmology or matter, a positive complete quantum theory, a complete
retarded waveform or detector prediction, or peer review of the whole
programme.

## Bottom line

The project’s strongest current statement is:

> Standard black-hole radiation conditions do not force pure Weyl gravity
> back into Einstein gravity. In one axial Schwarzschild channel, the extra
> layer forms a non-split extension and turns an ordinary quasinormal mode
> into a defective resonance with a double radial response pole.

That is an interesting mathematical-physics result. It is not yet evidence
that pure Weyl gravity describes nature.

For the technical claim map, see the
[physicist executive summary](98-physicist-executive-summary.md). For the
research archive, evidence graph, and authorship experiment, see the
[repository README](../README.md).
