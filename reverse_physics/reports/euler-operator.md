# An exact Euler operator — field equations over the jet ring

**Certificate** `REVERSE_PHYSICS_EULER_OPERATOR_V1`
**Rail** Forge, `tango/forge/examples/curvature_euler_gate.forge` — 15/15, TSan clean
**Dependency tag** `LOCAL-ALGEBRAIC`

> **A capability, not a physics result.** It establishes that the operator is right on
> Lagrangians whose field equations are already known, and nothing new about Weyl
> gravity. §5.

---

## 1. The gap it fills

The `D = 4` parity result is not *"parity-odd invariants exist"*. It is

> `RP-PARITY` is **independent on actions** and **redundant on field equations**.

[`parity-conformal-count.md`](parity-conformal-count.md) answered the first half in
`D = 6` by counting invariants. **Counting cannot touch the second half** — and every
curvature computation in this stream evaluates a scalar *at a base point*, while a
field equation is a variational object.

## 2. It is finite and algebraic

For `L = √|det g| · I(g, ∂g, ∂²g)`:

```
E^{μν} = ∂L/∂g_{μν} − ∂_α[∂L/∂(∂_α g_{μν})] + ∂_α∂_β[∂L/∂(∂_α∂_β g_{μν})]
```

A finite sum of partial derivatives of a function of finitely many jet coordinates. No
functional analysis.

**The trick that avoids deriving anything:** carry the perturbation parameter as *one
more jet variable*. Run the ordinary curvature pipeline on `g + t·h` and take the
`t`-linear slice — the first variation is then computed by **the same code** that
computes the unperturbed quantity. No linearised Christoffel symbol, no linearised
Riemann tensor, so neither can be got wrong.

With `h = φ(x)·E^{(ρσ)}`: `φ = 1` gives `A`, `φ = x^γ` gives `B`, `φ = x^γx^δ` gives
`C` — each as a **jet**, so the operator's outer derivatives are `jet_diff`.

And the operator is **linear in the Lagrangian**, so three basis field equations give
the whole quadratic sector — which turns Gauss–Bonnet from a fourth computation into a
**constraint on the three**.

### The degree budget, stated as a rule because it fails silently

The variation is read at x-degree `d`, so the Lagrangian jet must be right to **total**
degree `d + 1` — the extra one being the perturbation parameter's own exponent. That
forces `Riemann → d+1`, `Γ → d+2`, `metric → d+3`.

One short does not fail loudly: it discards the term `C` is read from, and the operator
comes back missing its last piece while still looking well-formed. It is check 12.

## 3. The controls, and why a nonzero one was required

Two `D = 4` Lagrangians are topological, so their field equations vanish identically —
**Gauss–Bonnet** and **Pontryagin**, for entirely unrelated reasons. Gauss–Bonnet is
computed as a combination of three separately computed, individually **nonzero** field
equations: a cancellation, not three zeros adding up.

But both are **vanishing** controls, and a whole class of errors survives them — an
operator missing a term that happens to vanish on topological densities, or wrong by an
overall factor, passes both.

So the anchor is **the trace law**, which this programme computed by an entirely
different route in sympy ([`weyl-trace-law.md`](weyl-trace-law.md)):

```
g^{mn} E_mn [ a Riem² + b Ric² + c R² ]  =  2(a + b + 3c) □R
```

Every check derived from it is a **ratio**, so it holds whatever normalisation either
side uses:

| | `a+b+3c` | check |
|---|---|---|
| `Riem²` | 1 | trace **nonzero** — the ratios are not about zero |
| `Ric²` | 1 | trace **equals** `Riem²`'s — two unrelated Lagrangians, same number |
| `R²` | 3 | trace **exactly 3×** — this fixes the normalisation |
| `C²` | 0 | **nonzero tensor, zero trace** — `RP-WEYL ⟺ RP-TRACELESS`, from the variation |

That last row is the one worth having: a structural fact no vanishing control can
produce, and the same statement the repository proved by another method.

## 4. Two bugs it found in its own construction

Neither showed as a wrong-looking number.

**Truncation through multiplication.** `jet_mul` caps the product at the **first**
operand's degree. `A` came from a cheaper low-degree run, so `A(x)·x^γx^δ` silently lost
its degree-2 term — exactly what `C` is read from. Every structural identity failed while
every "is it alive" check passed. After the fix, `E[E₄]` went from nonzero to **exactly
zero**: a cancellation among three numbers of order `10⁶`.

**Symbol versus tensor — invisible until you differentiate.** Summing over permutations
contracts with the Levi-Civita **symbol**, not the tensor. Pointwise, where the fixtures
have `|det g| = 1`, the two agree and nothing notices. As **jets** they differ by
`√|det g|(x)`, which is *not* constant — so multiplying the Pontryagin term by
`√|det g|` again produced a **weight-2 object that is not a Lagrangian density at all**.

> **This one reaches past this gate.** `REVERSE_PHYSICS_PARITY_CONFORMAL_COUNT_V1` uses
> the same shortcut. For counting invariants **at a point** it is sound and stays sound —
> that certificate is unaffected. For a **field-equation** question it is not, and the
> `D = 6` parity-odd density must be assembled with the weights right. It would have been
> a silent wrong answer to the actual question, caught only because the `D = 4` Pontryagin
> control exists.

### The method note

A **one-component falsifier** — 45 runs and three minutes, against 600 runs and
thirty-five — found and fixed both bugs in two short cycles. It should have existed
before the first full run; without it each bug cost half an hour to learn one bit.

## 5. The parity-odd measure rule, fixed and validated

A parity-odd scalar is built with the ε **tensor** against upper operands, while summing
over permutations contracts with the **symbol**, and `ε_tensor = √|det g| · [·]`. So

```
true scalar = √|det g| × (symbol contraction)
density     = √|det g| × scalar = |det g| × (symbol contraction)
```

**A determinant, not a square root** — and no square root at all, since `|det g|` is
polynomial in the metric.

Validated by assembling the **same** Pontryagin density both ways — the known form and the
parity-odd rule — and requiring agreement. They agree **up to a sign**, which is the
signature's, from raising four ε indices in a Lorentzian metric. Two Lagrangian
evaluations, about eight seconds; not a field-equation computation.

That is check 13, and it is what makes the `D = 6` parity-odd application safe to attempt.

## 6. It runs in parallel

The components share nothing — each is a pure function of its index pair writing one
disjoint slot, and `parallel_for` visits every index exactly once, so the writes are
race-free by construction. Closures may capture **scalars and pointers but not owned
values**, so the field identities and permutation tables are rebuilt per task rather than
shared; that sidesteps the `Send` question rather than relying on it.

**27 minutes → 9** on six workers (`user 37m` against `real 9m`). Six rather than sixteen
because the machine is shared.

Three independent confirmations, because scheduling must not be able to change an answer:

- **check 14** recomputes one component sequentially in-process and requires the same
  rational number;
- the **serial 13-check build** — a separately compiled binary with an entirely different
  execution order — returns 13/13;
- **TSan** reports no races.

And it was **probed before it was used**: a 64-task fixture doing real GMP and jet traffic,
checked componentwise against its serial computation — zero mismatches, TSan clean — before
the gate was touched.

## 7. What this does **not** establish

- **No physics result.** The operator is correct on Lagrangians whose field equations are
  known. Nothing about Weyl gravity that was not already known.
- **Not the `D = 6` parity-odd field-equation question** it was built for — a separate
  and much more expensive computation, and the symbol/tensor issue above has to be handled
  in it.
- **Only `D = 4`, only weight-4 Lagrangians.** The operator is written dimension-generally
  but validated nowhere else.
- **Nothing about actions modulo total derivatives.** Two Lagrangians differing by a total
  derivative have the same field equations, and nothing here distinguishes them.
- **Nothing Lorentzian, dynamical, or quantum.**

## 8. Substrate

- **`jet_var_slice`** — the coefficient of one variable's `k`-th power as a jet in the
  rest. This is what makes the whole thing possible with no new arithmetic.
- **`metric_det`** — the determinant as a **jet**, by the same pivoting elimination as
  `metric_inverse`; returns `none` rather than reporting a determinant it did not compute.
- **`jet_sqrt_unit`** — square root by a terminating binomial series, exact because the
  fixtures are unimodular at the base point; **traps** otherwise rather than guessing.
- **`math/curvature` no longer assumes `nv == n`.** Several routines built zero jets with
  `n` variables — correct only while the jets are coordinates-only, which was true of every
  caller until a variational calculation added a perturbation parameter. All nine gates
  that call the changed functions were re-run unchanged.

---

## Verification

```bash
cd tango/forge && export FORGE_LIB=$PWD/lib
forge verify examples/curvature_euler_gate.forge                  # 15/15, ~9 min on six workers
forge -run -sanitize-thread examples/curvature_euler_gate.forge   # the race gate
```

Exact rational arithmetic throughout. No floating point, no tolerance, no symbolic algebra
system.
