# The Krein Born trace on the obstructed shell

**Certificate** `REVERSE_PHYSICS_BT_BORN_TRACE_V1`
**Verifier** `reverse_physics/bt_born_trace.py --check` — 11 checks, all PASS (0.6 s)
**Dependency tag** `LOCAL-ALGEBRAIC`
**Lifecycle** `CLASSIFIED`
**Source read** S. Bateman and N. Turok, *Escape from Ostrogradsky via hidden
ghost parity*, [arXiv:2607.00096](https://arxiv.org/abs/2607.00096), 30 June 2026
(Higgs Centre, Edinburgh; Perimeter Institute)

> Companion to [`mannheim-cutting-rules`](mannheim-cutting-rules.md): that read
> the PT/positive-metric camp's loop paper for scope, this reads the Krein
> camp's. Both published routes stop at the same order, at the same point.

---

## 1. The blocker, and what clearing it cost

`symbolic/verify_doubled_theory.py` DQ8 ended:

> *"(The remaining BT-faithful step — transporting through their R_t and testing
> membership in the null C component — **needs their embedding and is queued**.)"*

That embedding is their Eqs. (18)–(21). Clearing the blocker cost one paper read.
This is the third recorded blocker in this repository to cost exactly that.

## 2. Their mechanism is a charge selection rule, not a norm cancellation

This is not visible from the abstract, and it changes the question:

```
R_t P^(φ) R_t†  =  P^(ΩΥ)  +  Q^(ΩΥ)
```

`P^(ΩΥ)` is charge **neutral**, t-independent, covariant, and — their emphasis —
*"most important, it is even under ghost parity."* `Q^(ΩΥ)` contains **only
negatively charged** operators. Then:

> *"Since the R_t homomorphism does not yield any positively charged operators,
> the negatively charged operators in Q cannot contribute to the trace, that is,
> Q is null and orthogonal to P."*

## 3. The fork — and it is Paper 05's, not this report's

Everything in this section is already in Paper 05. It is restated because
reading arXiv:2607.00096 independently confirms the attribution is correct;
`lem:chargenull` states **and proves** the charge-null mechanism, and
`cprop:embedding` computes the one-sidedness.

Paper 05's obstruction is ghost-parity **odd** (`cprop:krein`). Their `B` is
ghost-parity **even** by construction. So the obstruction cannot sit in `B`; it
must sit in `C`, and **`C`'s nullity carries the entire reconciliation**.

`C` is null only if the charge is one-sided — and Paper 05 has already computed
that this is a *boundary* property:

> *"one-sidedness of the regulated vacuum image — computational proposition,
> **exact iff ε = 0 in the stated charge frame**"* (`cprop:embedding`)

Their theory sits at ε = μ² = 0. Paper 05's obstruction is computed at split
mass, where both charge signs appear. **The two results do not conflict — they
sit at different points of one family**, which is exactly what Paper 05 meant by
calling the reconciliation a boundary transport question.

## 4. The computation

Their generalized Born rule, Eq. (6), on Paper 05's obstructed shell
`{|H(0)L(0)⟩, |L(3)L(−3)⟩}` at `E = 10`, with `κ = G = diag(−1,+1)`:

```
Prob(A) = tr(A† A),      A† = κ A^H κ   (Krein adjoint)
```

Two facts make this exact and decidable rather than a search:

- **The κ-even and κ-odd subspaces are Frobenius-orthogonal**, so cross terms
  drop and `Prob(A) = ‖A₊‖²_F − ‖A₋‖²_F`. Their weak-ghost-symmetry condition
  (`A = B + C`, `B` ghost symmetric, `C` null and orthogonal) is therefore
  **equivalent, on a finite shell, to the single inequality `‖A₋‖ ≤ ‖A₊‖`**.
- **The on-shell `T` is Krein self-adjoint** (`T† = T`) — DQ8b's `G T G = T^H`.
  So `Prob = tr(T²)` and no S-matrix assembly is needed.

Result, exact:

```
‖T₊‖² = 33800290689142511√5/22324055803822080000
      + 470064287210099385401/99011652301111689216000
‖T₋‖² = 482403/1554251776
Prob  = 33800290689142511√5/22324055803822080000
      + 439333411529238537401/99011652301111689216000     >  0
```

**Positive by inspection** — a positive rational multiple of `√5` plus a positive
rational. No numerical evaluation enters the conclusion anywhere. The κ-even part
exceeds the κ-odd part by a factor of about 26 in squared Frobenius norm.

### What that does *not* mean — the first version of this report got it wrong

It does **not** say the obstruction is invisible to the Krein Born rule. The
obstruction **enters** the shell trace, and by exactly

```
‖T₋‖² = 2c² = 482403/1554251776
```

which is precisely the quantity Paper 05's `lem:chargenull` sends to **zero**. A
truncated two-dimensional shell carries no boost action, so that lemma's
hypothesis — boost invariance of the trace, giving `τ(A_q) = e^{qσ}τ(A_q)` hence
`τ(A_q) = 0` for `q ≠ 0` — is simply absent, and its conclusion fails by that
amount. The trace stays positive not because the odd part is null but because the
even part outweighs it 26 to 1.

So this is a **diagnostic**, not a step: it quantifies why a fixed-shell
evaluation cannot *be* the capstone. Paper 05 says so directly —

> *"the process operator must be transported along this family rather than held
> fixed while only the embedding is varied"*

naming the family `m_L = 4s`, `m_H = 6s`, `|k_out| = 3s`, `μ² = 26s²`,
`εg = 100s⁴`, `s → 0`. Holding the operator fixed at the split-mass rational
point is the move that instruction rules out, and it is what was done here.

## 5. A defect found upstream, and why the conclusion does not rest on it

`symbolic/verify_doubled_theory.py` built `T` with `sp.nsimplify` wrapped around
an already-exact expression. On `T[1,1]` that **fabricated** a closed form:

```
fabricated:  −2^(31/449)·3^(114/449)·5^(38/449)·7^(101/449)/75
true:        −13264093√5/987148800 − 2759177557/995045990400
agreement:   ~2×10⁻¹⁹  — a float match, not an identity
```

A 449th root cannot arise from rational matrix elements and quadratic-surd
normalisations. It survived because **the DQ8 checks test only that the diagonal
is real, never its value.** The `nsimplify` call is removed at source; DQ1–DQ9
all still pass, and the verifier now runs in **16 s instead of about four
minutes**, because that call was the bottleneck. No published quantity is
affected: every DQ8 claim is an off-diagonal element or a reality statement.

**The conclusion does not depend on the entry that was repaired.** Setting
`T[1,1] = 0` outright still leaves the trace positive (`0.00675 > 0`). That
control is in the gate and re-derived independently in the tests, because a
result whose sign turns on a value one has just corrected is not a result.

## 6. Controls, all mutation-tested

- **The criterion can fail.** Scaling the κ-odd block by 10 drives `Prob`
  negative. Without this, "positive" would not be a measurement.
- **The crossover is where it should be.** The sign flips at
  `odd_scale = ‖T₊‖/‖T₋‖ = √26.204… = 5.119`, verified from both sides — so the
  test tracks the norm ratio and not an artefact.
- **Known answer.** A κ-even `T` is Hilbert-Hermitian and the Krein rule reduces
  to the ordinary positive one.
- **The Krein adjoint is not the Hilbert adjoint**, else the grading is trivial.
- **The positivity witness rejects negatives**, including mixed-sign surds like
  `−√5 + 1`.
- **Vacuity.** The κ-odd part is nonzero; otherwise the question is empty.

## 7. What this does not establish

- **Not a step toward the capstone, and not a necessary condition for it.** The
  shell does not implement the charge-nullity mechanism, so a negative value here
  would have refuted nothing and the positive value obtained supports nothing.
  The two computations answer different questions about different objects. Paper
  05's *"boundary Born-trace evaluation"* stays **open and untouched**: it
  requires the neutral component's blindness to the obstruction coefficient, in
  the limit along the named family, with the process operator transported.
- **No novelty in the mechanism.** The charge-null rule and the ε = 0
  one-sidedness are **Paper 05's** (`lem:chargenull`, proved there by boost
  invariance; `cprop:embedding`). They are restated here because reading
  arXiv:2607.00096 independently confirms the attribution is right — not claimed.
- **Nothing at loop level, on either side.** They prove positivity at tree level
  and name their own obstacle: *"like QCD, the massless theory has collinear
  infrared divergences which affect asymptotic states. These need to be carefully
  regulated and resummed."* The PT camp's cutting rules do not reach `1/k⁴` at
  all ([`mannheim-cutting-rules`](mannheim-cutting-rules.md)). **Both published
  routes stop at the same order, at the same point** — which is where pure Weyl
  gravity lives.
- **Nothing `LORENTZIAN-CAUSAL`.**

## 8. Provenance

Read from `arXiv:2607.00096v1` (18 pp.), retrieved 2026-08-08 from
`export.arxiv.org`; quotations from §"Generalized Born Rule", Eqs. (6), (18)–(21),
and §VI. The exact `T` entries are imported one-way from
`symbolic/verify_doubled_theory.py`, pinned by exact value and recomputed by
`python3 symbolic/verify_doubled_theory.py` (DQ1–DQ9, 16 s); nothing in
`symbolic/` imports this module, so no cycle is created. All arithmetic is exact
over `ℚ(√5, √6)` in sympy; the positivity conclusion is read off the exact
coefficients and uses no floating point.
