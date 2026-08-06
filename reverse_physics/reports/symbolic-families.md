# Symbolic metric families are cheap, and that changes what is provable here

**Certificate** `REVERSE_PHYSICS_SYMBOLIC_FAMILY_V1`
**Rail** Forge, `tango/forge/examples/curvature_symbolic_family_gate.forge` — 15/15, 89.53 s
**Substrate** `tango/forge/lib/math/jetfield.forge`
**Dependency tag** `LOCAL-ALGEBRAIC`

> A capability note, not a physics result. What it establishes is that a caveat carried by
> most of this stream's certificates is **removable at low cost** — not that it has been
> removed from any of them yet. §4.

---

## 1. The caveat this attacks

Every curvature result in this stream is computed **at specific metrics** — a dozen exact
rational fixtures, ranks taken over them. That is strictly stronger than an unverified
citation and strictly weaker than a theorem, and the certificates all say so.

"Zero at twelve fixtures" is not "zero for all metrics".

## 2. The lever

A jet **is** a truncated polynomial over its coefficient type. So the moment `Jet<Rat>`
satisfies the `Field` vocabulary that `Jet<T>` demands of its coefficients, jets nest:

```
Jet<Jet<Rat>>     outer variables = the spacetime coordinates
                  inner variables = the symbolic metric parameters
```

No new polynomial type, no second arithmetic to keep in step with the first. An identity
that comes back zero is zero **as a polynomial in the parameters** — every member of the
family at once.

**Division is the catch, handled by never asking.** `Field` demands `finv`, and a polynomial
ring inverts only units. `christoffel` takes `half` as an argument and `ci_weyl` takes
`1/(D−2)`; `metric_inverse` — the one routine that divides — is replaced by building
`g = L S Lᵀ` and `g⁻¹ = (L⁻¹)ᵀ S L⁻¹` directly, both polynomial because `L` is unit
lower-triangular. `jet_inv` still traps on a non-unit, which is the correct failure.

## 3. The cost, measured rather than predicted

| parameters | max terms in a Riemann coefficient |
|---|---|
| 1 – 6 | 1 → 10 |
| 7 | 10 |
| 8 – 9 | 15 |
| **10 — the full symmetric family** | **15** |

Whole sweep, all six identities: **49.78 s, 109 MB.** With `N1` (§4) the gate is
**15/15, 89.53 s, 111 MB** — `N1` alone is nearly the whole of that increase.

**`LDLᵀ` is the general symmetric matrix.** Six strictly-lower entries of `L` plus four
diagonal entries of `S` is ten — exactly the number of independent components of a symmetric
`4×4`. Holding `S` at `diag(−1,1,1,1)` gives `det g = −1` identically, a **codimension-one
slice**; letting it vary removes that restriction entirely.

**I predicted infeasibility twice and was wrong twice.** At six parameters the worst-case
count is `C(22,6) = 74,613` monomials against an actual **10** — wrong by four orders of
magnitude. At ten it is `C(26,10) = 5,311,735` against an actual **15** — wrong by five.
Sparsity dominates worst-case counting here so completely that predicting the cost is not
worth doing. **Measure it, and make the gate demand the full family so a prediction can never
quietly become a cap.**

`s_k` has constant term `±1`, hence is a **unit**, so `1/s_k` exists in the truncated ring and
`jet_inv` returns it rather than trapping. That is the only division in the gate, and it is
division by a unit — which is exactly what the `Field` implementation is permitted to do.

### Three things that had to be right at six slots and were not at two

- **`L⁻¹ = I − N + N² − N³` exactly**, since `N⁴ = 0` for a 4×4 strictly-lower matrix. The
  earlier `L⁻¹ = I − N` is valid only when `N² = 0` — true for two non-chaining slots,
  **wrong for six**, which chain through `(2,1)`, `(3,1)`, `(3,2)`. The `inv` column verifies
  `g g⁻¹ = I` as a polynomial identity at every parameter count.
- **The inner degree is derived, not tuned.** Entries linear in the parameters give `g⁻¹`
  degree 6, `Γ` degree 8, **Riemann degree 16**. Less than that silently truncates the
  curvature itself.
- **Every row reports `unsat`.** A family that outgrows the truncation announces itself
  instead of quietly returning zeros — the failure mode that turns "the identity holds" into
  a vacuous pass.

## 4. The first claim actually upgraded

**Weyl tracelessness.** `C^a{}_{bad} = 0` was established by `ci_trace_sq` at a dozen exact
fixtures. It now holds as a **polynomial identity** over the full **ten-parameter symmetric family**, at
every parameter count from 1 to 10.

**No new tensor code was written.** The `ci_*` layer works on *values* of type `T` with
`Field<T>`, so taking the constant term in the **coordinates** first leaves
`ManualVec<Jet<Rat>>` — curvature at the base point, still polynomial in the parameters — and
`ci_lower_first`, `ci_ricci`, `ci_weyl`, `ci_trace_sq` all apply unchanged with
`T = Jet<Rat>`. The existing contraction layer was already generic enough; it just had never
been handed anything but rationals.

**The paired control is what makes the zero evidence.** The *same* trace operation applied to
**Riemann** gives Ricci and is required to come back **nonzero** — reported as
`riem-trace-nonzero` on every row. So the machinery demonstrably detects a nonzero trace, and
Weyl's vanishing is a fact about Weyl rather than about a routine that returns zero for
everything. Weyl is separately required to be nonzero and to depend symbolically on the
parameters, or the identity would hold for a family that is secretly one metric.

### The second: `G1`, the coordinate vectors

`REVERSE_PHYSICS_WEYL_GEOMETRY_DISCHARGE_V1` establishes `G1` **on a single metric**:

```
C² = Riem² − 2 Ric² + R²/3                        (D = 4)
C² = E₄ + 2 Ric² − (2/3) R²,   E₄ = Riem² − 4 Ric² + R²
```

These are the coordinate vectors **the entire `D = 4` classification is expressed in**, so
one metric was a thin footing. Both now hold as polynomial identities over the full
ten-parameter symmetric family.

The negative control is the same identity with `R²/4` in place of `R²/3` — it must **fail**,
and does on every row. Without it, "the identity holds" would be satisfied equally well by
three scalars that were all zero, which is why they are separately required to be nonzero.

Again no new tensor code: `ci_raise_slot`, `ci_raise2` and `ci_dot` used exactly as on
rationals. **The contraction layer keeps turning out to be generic enough already** — what
was missing was only ever a coefficient ring to hand it.

### The third: `G3`, the conformal weight

`C^a{}_{bcd}` is unchanged under `g → Ω²g`, now a **polynomial identity** over the
ten-parameter family rather than a check at fixtures. `G3` is the load-bearing input to this
stream's dimension and derivative-order arguments — *"√−g X of curvature degree k has
constant weight D − 2k"* is `G3` plus counting — so samples were a thin footing for it.

**The paired control is the point.** `R^a{}_{bcd}` under the *same* transformation must come
back **changed**, and does on every row. Weyl and Riemann differ only by trace terms, so a
comparison reporting both invariant would be comparing something to itself — which is how
earlier drafts of this gate failed twice.

`Ω² = 1 + a_c(x + x²)` carries its **own** parameter, which is why the variable count and the
live-slot count had to be separated: the conformal factor must be a variable of the inner
ring without becoming a metric component. Its constant term is 1, so it is a unit and `1/Ω²`
exists in the truncated ring — the second place a genuine division is avoided by staying
inside the units.

### The fourth: `N1`, the divergence of the Bach tensor

```
nabla^a B_ab = 0
```

This is the **gauge layer's own identity** — the Noether/diffeomorphism content of the Weyl
action, and the reason it propagates only the modes it does.
`REVERSE_PHYSICS_WEYL_GEOMETRY_DISCHARGE_V1` establishes it **against specific metrics**. It
is now a polynomial identity over the family.

**`bach_of` could not deliver it, and the reason is worth stating.** That routine returns Bach
at a *point*, because it is built on `cv_cov_val` — and a point cannot be differentiated. `N1`
needs Bach as a **function**, so the whole chain was rebuilt with the jet-level covariant
derivative: `∇` on `C^a{}_{bcd}` twice, contract to `B_{ab}`, raise, `∇` once more, contract
`ρ = e`. Three covariant derivatives, hence `XDIV = 5` outer degree, hence rank-6 jet arrays.

**The certificate predicted the wrong blocker.** `REVERSE_PHYSICS_SYMBOLIC_FAMILY_V1` recorded
`N1`, `N2` and the generator count as *"one job, not three — the Euler operator over this
ring"*. That is right for `N2` and the generator count, which are about the **variation**.
It is **wrong for `N1`**, which is about the **tensor**: `∇^a B_ab` needs only the covariant
derivative, which already existed. One of the three was not blocked at all, and grouping them
hid that for longer than it should have.

**Two controls, and the negative one is what makes the zero mean anything.**

- `bach-jet == bach_of` — the jet-level Bach must reproduce the value-level Bach at the base
  point. Two independent constructions of one tensor. This is the shape of check that caught
  the jet-level Weyl tensor being built from the *mixed* Riemann instead of the all-lower one,
  in about ninety seconds.
- `ricci-div-nonzero` — the **negative** control. `∇^a R_ab = ½∇_b R` does **not** vanish, so
  the *same* divergence machinery applied to Ricci must come back **nonzero**. Without it,
  "the divergence vanishes" is indistinguishable from a divergence routine that returns zero
  for everything, which is the exact failure this stream has now hit three separate times.

**Only the constant term in the coordinates is read, and that is derived rather than
convenient.** Each covariant derivative costs one valid outer order: from `g` at degree 5,
Riemann and `C` are trustworthy to 3, `∇∇C` to 1, `∇B` to **0**. Reading a higher order would
be reading truncation garbage.

### The control I was told to build, built — and it doesn't work

The certificate said Bach should be checked to **vanish on Einstein metrics** *"before it can
be believed"*. That is now built: Schwarzschild (`M=1, r=4, x=cos θ=0`) as a jet in the **same
nested ring** with one unused dummy parameter, so the *identical* `bach_of` runs on it rather
than a re-derivation that could agree by sharing a mistake. Taking `x = cos θ` is what keeps
the sphere factor rational — no sine anywhere, so the fixture is exact. It passes: `g g⁻¹ = I`,
Ricci-flat, Weyl nonzero, Bach zero.

**Then I mutated `bach_of` three times, and the control passed all three.**

| mutation | Schwarzschild | what caught it |
|---|---|---|
| `½` → `⅓` on the `Ric·C` term | **passed** | conformal weight |
| `C_{acbd}` contracted as `C_{acdb}` | **passed** | conformal weight |
| the two derivative indices swapped | **passed** | **nothing** |

**The reason is structural and I should have predicted it.** On *any* Einstein metric
`R^{cd}C_{acbd} = (R/D)·g^{cd}C_{acbd} = 0` **by Weyl tracelessness** — so the `Ric·C` term is
multiplied by zero and its coefficient cannot be probed there at all. Schwarzschild is
Ricci-flat, so more strongly: `C = Riem`, and contractions of `∇∇Riem` vanish for reasons that
survive getting the formula wrong. **Bach-flatness on an Einstein metric is overdetermined** —
many wrong formulas produce it.

**Naming a known-answer control in advance is good practice; it does not make the control
discriminating.** This one was named without asking whether it *could fail*, which is the
same defect the parity retraction was about, one level up: there the *candidates* weren't
checked for well-formedness, here the *control* wasn't checked for discriminating power.

What actually constrains `bach_of` is the **conformal weight** check, which was already in the
gate. The Schwarzschild check is kept under an honest label as a **pipeline** check — the
whole chain running on a metric from outside the `LDLᵀ` family, with a genuine `1/r` series
instead of a polynomial. Narrower than advertised, still worth having.

### The mutation nothing caught, settled

`∇^c∇^d` versus `∇^d∇^c` differ by a commutator, so the third mutation was either a semantic
no-op or an **untested degree of freedom in a routine `N1` rests on**. That is not a
difference worth guessing at, so it was carried open and then settled **by computation**:

```
nabla^c nabla^d C_{acbd}  =  nabla^d nabla^c C_{acbd}
```

a **polynomial identity over the full ten-parameter family** (`np = 10`, 229 s). The mutation
was a semantic no-op. **Nothing caught it because nothing could**, and the gate has no
untested freedom there.

**How, and why that way.** The derivative order became a **parameter of the one `bach_of`
implementation** rather than a second copy that could drift — so both orderings run through
identical code and the only difference is the index pairing.

**The comparator was itself mutation-tested.** Pointing the swapped branch at a genuinely
different index gives `ORDERS-AGREE = 0`, so it demonstrably detects a difference. An
agreement test that cannot report disagreement establishes nothing — and the check separately
requires Bach to be **nonzero** and to depend **symbolically** on the parameters, so this is
not two zeros or two constants agreeing.

**It is now demanded rather than reported.** Check 15 fails if the identity breaks. The
regression rail runs at **two** parameters — a break shows there as readily as at ten — while
the ten-parameter run is the *result*, not something worth 123 s on every run.

**`N1` holds over a smaller sub-family than the other three.** See §5.

## 4b. The Euler operator, and a blocker that was wrong twice

**Rail** `tango/forge/examples/curvature_symbolic_euler_gate.forge` — 9/9, 963.56 s, 95 MB.

This certificate said `N1`, `N2` and the generator count were *"one job — the Euler
operator"*, and that the Euler operator was *"a port of roughly four hundred lines… because
it manipulates jet indices directly rather than going through the `Field` vocabulary"*.

**Both halves were wrong.** `N1` needed only a covariant derivative (corrected earlier). And
`euler_component` is built from `jet_var_slice`, `jet_diff` and `jet_const_term` — every one
of them generic in `T`. Two blocker predictions, both wrong in the same direction, both made
**without reading the code they were about**. The cost of checking was one file read, each
time, and each time the prediction deferred real work.

**The real obstructions were different, and both dissolve rather than port.**

| obstruction | dissolved by |
|---|---|
| `metric_inverse` **divides** | `(g₀ + th)⁻¹ = g₀⁻¹ − t g₀⁻¹hg₀⁻¹ + O(t²)` — the Euler operator reads only the `t`-linear slice, so `O(t²)` is never looked at |
| `√−det g` isn't polynomial | `S = diag(−σ₀², σ₁², σ₂², σ₃²)`, so `−det g` is a perfect square and the root is `σ₀σ₁σ₂σ₃` |

The second costs **no generality**: `LDLᵀ` with a sign-definite diagonal is exactly the
general symmetric matrix *of Lorentzian signature*, which is the only signature this
programme is about. A third obstruction is purely mechanical — the perturbation parameter is
an extra **outer** jet variable.

**Validated against a textbook answer that is not assumed.** For `L = √−g`, the Euler
derivative is `½√−g g^{ab}`. The density is computed as `exp(½ log(−det g))` of the honest
Leibniz determinant — *not* from `δ√−g = ½√−g g^{ab}δg_{ab}`, which is the answer under test.
`jet_log`/`jet_exp` invert only integer constants, units in the inner ring, so this needs no
division either.

**Two guards fired on the first run and both were right — in opposite directions.**

- `answer-symbolic = 0` caught a **real degeneracy**. Every parameter entered through
  `x + x²`, which **vanishes at the base point** — so the metric there was parameter-free and
  every check in the gate was being read where the family collapses to a single metric. Fixed
  to `1 + x + x²`: the quadratic still makes the family curved, the leading `1` makes it
  symbolic *where it is read*.
- `B-and-C-zero = 0` was **my premise being wrong**, not the code. For a derivative-free
  Lagrangian `B^γ = (A(x) − A(0))x^γ` is a nonzero jet of order `x²` that contributes nothing.
  The check had to measure **contributions**, not jets. **A control can be wrong by being too
  strong** — the opposite failure to the Einstein control two sections up.

### The fifth claim: the Noether identity

```
g_ab E^ab = 0        for  L = sqrt(-g) C^2
```

`REVERSE_PHYSICS_NOETHER_IDENTITIES_V1` establishes this at **three sampled metrics**. It now
holds as a polynomial identity over a family — the thing the whole Euler exercise was for.

**A three-rung ladder, each rung a known answer the next one needs.**

| Lagrangian | known answer | what only *it* can test |
|---|---|---|
| `√−g` | `½√−g g^{ab}` | derivative families must contribute **nothing** |
| `√−g R` | `+√−g(½R g^{ab} − R^{ab})` | derivative families must be **nonzero** |
| `√−g C²` | trace vanishes | the identity itself |

Rung two is strictly stronger *in the way that matters*: a machine returning zero `B` and `C`
passes rung one completely and fails rung two. **The sign is read off, not asserted** — the
check requires a match up to an overall sign and reports which (`+1`), because the sign is a
convention of the perturbation normalisation, and asserting conventions from memory is how
two blocker predictions here went wrong.

**The trace is taken along the conformal direction** `h_ab = tφ·g_ab`, which is both cheaper
and sharper. Cheaper: **15** Lagrangian runs rather than the 150 needed to build all ten
components and trace them — the component route did **not** finish in 580 s. Sharper: *"the
action is stationary under conformal rescaling"* **is** Weyl invariance, and the trace
identity is that fact written in components.

**`C²` is computed from the definition, not from the certified `G1` identity.** Using
`C² = Riem² − 2Ric² + R²/3` would be legitimate — it holds over the full ten — but it would
couple this result to that one. Computing directly makes this an **independent confirmation**
of `G1` rather than a consumer of it.

**Mutation tested, and unlike the Einstein control it discriminates.** Changing `1/(D−2)` to
`1/(D−1)` in the Weyl construction gives `WEYL-TRACE-VANISHES = 0`. That matters precisely
because the last known-answer control built here survived three separate defects and turned
out to be nearly vacuous. This one can fail. The negative control is the same conformal trace
on `√−g R`, which comes back **nonzero**.

### The sixth claim: the generator count

**The inherited seven-candidate list turned out to be incomplete**, and the omission was the
dangerous one — §4d. Over the *complete* degree-≤2 list of **ten**, exactly **five** lie in
the kernel of `T_ab E^ab`:

| in the kernel | **not** identities |
|---|---|
| `g`, `R g`, `R² g`, `\|Ric\|² g`, `\|Riem\|² g` | `Ric`, `Ric²`, `R Ric`, `Ric^{cd}R_{acbd}`, `R_{acde}R_b{}^{cde}` |

**All five kernel elements are `f·g`.** Gauge symmetries form a **module over functions**, not
a vector space, so `R g_ab` is the Weyl generator multiplied by a function rather than a
second symmetry — a naive kernel dimension overcounts four to one. **One generator**, now over
a family rather than at three fixtures.

What makes that meaningful is not the four that vanish but the three that **don't**. `Ric`,
`Ric²` and `R·Ric` are the candidates that are *not* multiples of `g`, and all three come back
nonzero. They are the discriminating half; without them "everything vanishes" would fit
equally well.

### 4d. The inherited list was incomplete, and the gap was the dangerous one

Every one of the inherited seven — `g`, `Ric`, `R g`, `Ric²`, `R² g`, `|Ric|² g`, `R Ric` — is
built from `g` and **Ricci**. Nothing in the list uses Riemann beyond its Ricci trace.

At curvature degree ≤ 2 the complete list is **ten**: `g` at degree 0; `Ric`, `R g` at degree
1; and **seven** at degree 2 — three scalars times `g` (`R²`, `|Ric|²`, `|Riem|²`), one scalar
times `Ric`, and three carrying both free indices on curvature (`Ric²`, `Ric^{cd}R_{acbd}`,
`R_{acde}R_b{}^{cde}`).

**The three omitted are exactly the ones that could have broken the count.** `E^{ab}` for the
Weyl action *is* the Bach tensor, which involves the full Weyl tensor rather than only its
traces — so a candidate contracting against **Riemann** is precisely the kind that might
produce a second generator, and a Ricci-only list structurally could not have seen it.
`|Riem|² g` is another `f·g` and joins the kernel for free; the other two are **not** multiples
of `g` and were genuine candidate generators.

**The count survives.** Both Riemann-built candidates come back **nonzero**. The previous
answer was right for an incomplete reason and is now right for a complete one.

**Over-complete is the safe direction.** If the ten carry linear dependences — plausible in
`D = 4`, where Gauss–Bonnet relates the scalars — then ten *over*-counts the dimension. That
is harmless: completeness needs a **spanning** set, and a spanning set that isn't a basis
still cannot hide an identity. The risk was *under*-completeness, which is what the inherited
list had.

**And it was nearly free.** The component route's cost is the 150 Lagrangian runs producing
`E^{rs}`, shared across every candidate — three more candidates is three more contractions
against curvature already in hand. Seven to ten took the gate from 716.92 s to 876.76 s.

### The route that failed, and the control that caught it

The obvious approach was directional — perturb along `h_ab = tφ T_ab`, 15 Lagrangian runs per
candidate instead of 150. It reported **`FUNCTION-LINEAR = 0`**.

**The control was right.** A directional perturbation folds `T` into the test function, so the
extraction `A − ∂B + ∂∂C` picks up derivatives of `T` by Leibniz. That's fine in principle —
the integration by parts still lands on `T_ab E^ab` — but it changes the **degree budget**.
`gdeg = ldeg + 2` is derived for a **constant** direction. `Ric` costs two derivatives of the
metric, so a curvature-valued direction needs `gdeg = ldeg + 4`, and building it at `ldeg + 2`
silently truncates exactly the terms Leibniz produces.

That control was deliberately run on a **nonzero** case. The same test on `R g` would have
been `0 = R × 0` and proved nothing — the vacuous-control failure this programme keeps
finding, here anticipated instead of discovered.

**And check 6's conformal direction is *not* excused by argument.** `g` costs no derivatives,
so it should be exact at `gdeg` — but that is an argument of *exactly the same form* as the
one that just proved wrong for `Ric`. So the component route recomputes `g_ab E^ab`
independently and is required to **agree** with check 6's directional value. It does. An
argument that has already failed once in the same session is not evidence the second time.

The component route was taken rather than raising the degree because `gdeg = ldeg + 4` puts
the `C` family at outer degree 7, and cost climbs steeply in degree. It costs 150 runs against
15 per candidate, has **no** degree subtlety, and yields **all seven** contractions from one
computation.

**The parameter counts differ in kind, not just in size.** `ROOTNP = 8` is a **premise**:
parameters 0–5 are the `L` slots and only 6–9 are the diagonal σ, so `det g` depends on
nothing below 7 and check 3's symbolic premise is *unsatisfiable* there rather than false.
`FULLNP`, `EULNP` and `NOETHNP` are **budgets**, measured — 3.2 s at 2, 14.3 s at 4, 175 s at
6, and 7 does not finish in 500 s, because the leading `1` also makes every entry dense at
every coordinate order. `NOETHNP = 2` is much the smallest sub-family of any claim here:
`√−g C²` rebuilds the Weyl tensor and raises all four of its slots on *every* Lagrangian run.

## 4e. The total-derivative quotient — the step two certificates say was never taken

Both the cubic and derivative conformal-count certificates say, verbatim:

> *"the quotient by total derivatives. It is not needed for a pointwise count and **it was not
> performed**, so nothing here is a statement about **LAGRANGIANS**, about actions, or about
> the trace anomaly's coefficients."*

Every conformal count in this repository is a **pointwise rank**. Two Lagrangians differing by
a total derivative give the same *action*, so a count of invariants is not a count of actions
until the quotient is taken.

**The Euler operator is that quotient.** `E[L] = 0` exactly when `L` is a total divergence, so
the space of actions is the **image** of `L ↦ E[L]` and the total derivatives are its
**kernel**. Built for the Noether work, it turns out to be the instrument for a blocker
recorded elsewhere as untouched.

**And the known answer here is one the repository currently imports.**
`REVERSE_PHYSICS_WEYL_GEOMETRY_DISCHARGE_V1` lists `G4` — *"∫√−g E₄ is topological in D = 4"* —
under **still_imported**, as *"a global statement, not reachable pointwise."* Its **local**
content is reachable pointwise, and is now computed:

```
E[√−g E₄] = 0   identically,    E₄ = Riem² − 4 Ric² + R²
```

as a polynomial identity in the metric parameters, not at a sampled metric. That matters in
this programme's own currency: `REVERSE_PHYSICS_WEYL_ACTION_V1` states its novelty as *"the
machine-checked zero-axiom derivation with the geometric inputs **isolated**"*, so converting a
cited geometry input into a computed one is exactly the kind of contribution it accumulates.

**The rank is pinned from both sides.** `≤ 2` because `(1, −4, 1)` is in the kernel
*identically*; `≥ 2` from an explicit exact metric, a rank at a point being a lower bound on
the generic rank. So the three-dimensional parity-even quadratic carrier modulo total
derivatives is exactly **two**-dimensional — and the D = 4 uniqueness theorem's final step,
*"the quotient by topological terms leaves exactly the one-dimensional span of the Weyl
action"*, stops being asserted.

**The first rank was wrong, and the gate said so.** It reported `RANK = 0` beside
`each-nonzero = 1` — a flat contradiction. The rank was read at the inner **constant term**,
which is all-parameters-zero, and there the family degenerates to the **flat** metric where
every curvature scalar vanishes. The rows were nonzero as polynomials and zero at the point
they were being read at: the same shape as the base-point degeneracy §4b caught, one level
down. Now evaluated at distinct small rationals `1/2, 1/3, …`, which is sound because a rank
at a point can only *understate* a lower bound.

## 5. What this does **not** establish

- **The quotient is taken for the QUADRATIC sector only.** The "was not performed" sentence
  sits in the *cubic* and *weight-6* certificates, and those are not quotiented here. The
  method is demonstrated on the one sector whose answer is independently known.
- **`G4`'s global content is still imported.** What is computed is that the Euler derivative
  of `√−g E₄` vanishes *pointwise*. That `∫√−g E₄` is a topological invariant — Gauss–Bonnet
  itself — is a global statement and remains cited.
- **Six claims are upgraded, not the ledger.** Weyl tracelessness, `G1`, `G3`, `N1`, the
  Noether identity and the generator **count** are done.
- **The identity and the count both hold at TWO parameters**, far short of the ten that
  tracelessness, `G1` and `G3` enjoy. `√−g C²` through 150 Lagrangian runs is expensive enough
  that this is a real restriction. The count was first run at one and **not left there** — a
  claim that could have been made over a wider family and wasn't is a cap, not a boundary.
- **Completeness holds at curvature degree ≤ 2 and for ALGEBRAIC candidates only.** The ten
  span symmetric rank-2 tensors built from `g`, `g⁻¹` and Riemann at degree ≤ 2. Degree 3 and
  above, and anything involving **derivatives** of curvature (`∇∇R` and the like), are not
  swept. "One generator" is one generator *in that class*.
- **The general trace law `N2` is not computed.** What is verified is the Weyl case — the
  vanishing instance. `g^{mn}E_mn = 2(a + b + 3c)□R` over the whole quadratic family is not.
- **The Noether identity holds over only two parameters**, smaller than `N1`'s three and far
  smaller than the ten the other three enjoy. `√−g C²` is expensive enough that this is a real
  restriction, not a formality.
- This report has now **twice** recorded a predicted blocker that turned out not to be the
  real one.
- **that `bach_of`'s coefficients are verified by an Einstein metric.** The control was built
  and mutation-tested and does **not** discriminate — three separate defects survived it. The
  conformal-weight check is what constrains them.
- **`N1` holds over a smaller sub-family, and the gate says which.** Three covariant
  derivatives mean rank-6 jet arrays at outer degree 5, and the cost climbs in the parameter
  count far faster than the undifferentiated identities do: twelve checks at the **full ten**
  cost about 26 s, `N1` alone at **three** costs about 60 s. So `N1` is verified over
  `N1NP = 3` parameters, not ten — a **strictly smaller** family than tracelessness, `G1` and
  `G3`. `np = 4` passes in 359 s and is on the record; `np = 5` was **not determined**.
- **That number is a budget, not a wall,** and the distinction is load-bearing. Every other
  check here demands the full family precisely because a *predicted* cost nearly became a
  silent cap. What makes `N1 = 3` different is that it is measured, the higher passing value
  is recorded, and the undetermined one is named as undetermined rather than implied to be a
  limit.
- **The printed label is derived from that one constant.** A hardcoded `np=1` reported the
  wrong number for a run at `np=2` before it was caught. A receipt whose number is typed
  rather than computed is fiction.
- **The family is now general in the metric, not in the coordinate dependence.** The
  unimodularity restriction is gone — ten parameters span every component of a symmetric
  `4×4`. What remains is that each slot carries a **fixed quadratic pattern** in `x` rather
  than a general function, so this is a generic metric *family* near flat, not every metric.
- **Six identities are verified so far** — last-pair antisymmetry, the first Bianchi
  identity, Weyl tracelessness, the two `G1` forms, and `G3`. The first two exercise the
  pipeline rather than settling anything in doubt; tracelessness, `G1` and `G3` were standing
  ledger claims.
- **The Euler operator is not yet available over this ring**, so the Noether-identity result
  is still at sampled fixtures.

## 6. What it opens

The next targets all need the same missing piece — **the Euler operator over this ring** —
because each is about the *variation* rather than the curvature: `N1` (`∇^a B_ab = 0`, which
needs the Bach tensor), the trace law `N2`, and the Noether identity generator count — which
would turn *"one generator at three fixtures"* into *"one generator for every metric in the
family"*, the actual reverse-physics statement about the gauge algebra.

---

## Verification

```bash
cd tango/forge && export FORGE_LIB=$PWD/lib
forge -run examples/curvature_symbolic_family_gate.forge   # 15/15, 89.53 s, 111 MB
forge -run examples/curvature_symbolic_euler_gate.forge    # 9/9,   963.56 s,  95 MB
```

Exact rational arithmetic throughout. No floating point, no tolerance.
