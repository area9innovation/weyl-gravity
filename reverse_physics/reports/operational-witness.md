# One witness with operational content

**Certificate** `REVERSE_PHYSICS_OPERATIONAL_WITNESS_V1`
**Rail** `reverse_physics/operational_witness.py` — 9/9 checks
**Dependency tag** `LOCAL-ALGEBRAIC`

---

## 1. The criticism this answers

The sharpest thing the Assumptions of Physics programme would say about this
stream is that **our carriers have no operational content**. Their framework is
rooted in *experimental verifiability* — a statement is physical only if a finite
procedure confirms it in finite time — and the topology and σ-algebras are built
from that.

Our witnesses are Lagrangian densities. `√−g (g⁰⁰)²` is a perfectly good local
functional and a perfectly bad physical system: no states, no evolution, nothing
to measure. Their version of our `T4` would ask **what experiment distinguishes
the witness**, and we had no answer.

This builds the bridge **once**, at the smallest scale, to find out whether it is
buildable at all.

## 2. Which witness, and why not a Lagrangian

Not a Lagrangian density — those are precisely the ones with no operational
content, and dressing them up would be pretending. The Krein family from
[`ghost-harmless.md`](ghost-harmless.md) already *is* a system:

| | |
|---|---|
| **states** | rays in ℂ² carrying `η = diag(1,−1)` — one positive-norm and one negative-norm direction, the minimal ghost |
| **evolution** | `U(t) = exp(−iHt)`, `H(a,d,b) = [[a,b],[−b,d]]` |
| **observable** | `\|U(t)e₁\|²` |

## 3. The measurement separates the three regimes

Computed exactly:

| `Δ` | `\|U(t)e₁\|²` | behaviour |
|---|---|---|
| `9` | `25/9 − (16/9)cos 3t` | **bounded**, oscillatory |
| `0` | `2t² + 1` | **secular**, polynomial |
| `−3` | `(4/3)cosh(√3 t) − 1/3` | **exponential** |

**The two failure modes differ from each other.** Diagonalizability and real
spectrum are independent conditions in the algebra, and the independence is
visible in the laboratory: losing diagonalizability gives *polynomial* growth,
losing reality gives *exponential*. The exponential **rate** does not separate
bounded from secular — both are zero — so boundedness has to be asked separately.
That is the operational shadow of the same independence.

## 4. The finding, in their currency

A verifiable statement is one a finite procedure confirms in finite time;
verifiable statements are the **open** sets. Two modalities are available.

**Watching the trajectory.** *"The amplitude exceeds X by time T"* is finitely
verifiable. So `Δ < 0` and `Δ = 0` are verifiable — both grow without bound. But
`Δ > 0` is **not**: *"stays bounded forever"* cannot be confirmed by any finite
observation. Refutable, not verifiable.

**Measuring the parameters.** `Δ > 0` and `Δ < 0` are **open** conditions, so
finite precision suffices. `Δ = 0` is **closed with empty interior** — no
finite-precision measurement can ever confirm it.

| | by parameters | by trajectory |
|---|---|---|
| `Δ > 0` harmless | ✅ open | ❌ needs forever |
| `Δ = 0` exceptional | ❌ measure zero | ✅ grows |
| `Δ < 0` unstable | ✅ open | ✅ grows |

> **Every regime is verifiable by at least one modality, no modality verifies all
> three, and the two that matter most need different ones.**

## 5. Why the missed mode gets missed

That middle row deserves its own statement. `Δ = 0` is exactly the **Jordan
failure mode** that this repository's own `scattering_c_factorisation` recorded
as having been *missed* — spectrum in the right place, operator not
diagonalizable.

Operationally it is **the one configuration that cannot be confirmed by measuring
the theory's parameters, only by watching it misbehave.** A criterion checked by
parameter measurement misses it **by construction** — which is a reason it gets
missed, rather than an accident.

## 6. What this does not establish

- **It does not generalise.** Built once, at the smallest scale. The
  Lagrangian-density witnesses remain without operational content.
- **It does not use their formal machinery** — only the informal criterion, not
  the topologies of verifiable statements or the σ-algebras.
- **Nothing about Weyl gravity.** Two-dimensional linear algebra.
  `C-GHOST-DYNAMICS` stays `OPEN`.
- **The verifiability verdicts are judgements**, recorded so they can be
  disputed. The amplitudes and the openness are computed.

---

```bash
PYTHONPATH=. python3 -m reverse_physics.operational_witness --check
```
