# Foundational dependencies of the typed biwave Green theorem

## Result

`FOUNDATIONAL_TYPED_BIWAVE_GREEN_DEPENDENCY_AUDIT_V1` audits the certified
conditional theorem for `A=P2 P1+V`.  It carries both `LOCAL-ALGEBRAIC` and
`LORENTZIAN-CAUSAL`, but those tags apply to different proof layers.

The finite checker certifies resolvent algebra.  Causal Green existence comes
from analytic hypotheses and proof artifacts; it is not computed by finite
matrices.

| Layer | Status | Foundational classification |
|---|---|---|
| compact-Cauchy global hyperbolicity and finite-rank bundle | assumed | not classified |
| normally-hyperbolic factor Green maps | imported analytic existence | not classified |
| Sobolev, time-regular and graph-domain completion | used | actual infinity/completeness; Choice open |
| finite-slab energy estimates | explicit hypothesis | not classified |
| typed companion/resolvent algebra | exact | fixed fixtures PRA-checkable |
| factorial Volterra convergence | analytic | countable series/completeness; weakest base open |
| Cauchy and Volterra uniqueness | analytic | not classified |
| finite propagation and nested-slab support | Lorentzian causal | not classified |
| formal-adjoint reversal | algebra plus distributional duality | not classified |

## Exact core

The companion construction has different operators

```text
R_sol=(I_X+G0 N)^-1,   R_src=(I_Y+N G0)^-1.
```

Associativity gives the termwise push-through

```text
sum(-G0 N)^k G0 = G0 sum(-N G0)^k.
```

The independent checker uses noncommuting rational `2 x 2` matrices.  For
truncations zero through eight it checks both Neumann remainders, the
push-through identity, and exact terms `(3/2)^n/n!`.  This establishes the
universal `LOCAL-ALGEBRAIC` layer only.

## Where existence enters

Before a Neumann series can be written, the normally-hyperbolic factors must
already have continuous advanced/retarded Green maps on the declared Sobolev
spaces.  The graph-bounded lower-order term and finite-slab energy estimate
then yield both factorial bounds.  Completeness converts the Cauchy partial
sums into operators.  Normally-hyperbolic uniqueness and Volterra uniqueness
identify nested-slab solutions, while finite propagation gives global causal
support.  Formal duality on test sections finally reverses advanced and
retarded maps and reverses the factor order in `A^sharp`.

Deleting any of those analytic joints breaks the causal theorem even though
the finite matrix identities remain true.  Conversely, the analytic theorem
is conditional on the exact physical operator having the declared normal
form and graph estimates.

## What is and is not classified

This report supplies a dependency cut, not a reverse-mathematical reversal.
The Choice strength, weakest subsystem, and constructive realization of the
normally-hyperbolic factor theorem remain `OPEN`.  Sobolev completion,
operator-valued countable series, distributional duality and causal support
must be encoded before such a classification is meaningful.

The result does not construct the full off-shell metric BV propagator, a
BRST-compatible Hadamard state, renormalized Lorentzian products, or a
Lorentzian QME.  It does not promote a finite-symbol or reduced-mode result to
`LORENTZIAN-CAUSAL` evidence.

## Follow-up atlas and next gate

The [normally-hyperbolic factor atlas](normal-hyperbolic-factor-foundations.md)
now supplies the bounded literature and dependency pass for this base case.
It finds direct classical Green and finite-propagation theorems, direct
represented-computability upper bounds for symmetric-hyperbolic evolution,
and an exact local finite-graph support certificate. It does **not** find or
prove a reverse-mathematical subsystem classification, a Bishop-style global
Green theorem, or Choice avoidance for the Sobolev/distributional construction.

That gate is now partly closed by the
[coded polygonal wave certificate](coded-polygonal-wave-rca0.md). For its
declared fast-Cauchy chiral energy representation, `RCA_0` suffices for a
unique real-time isometric Cauchy evolution. This is an upper bound, not a
necessity theorem or representation-invariant reversal, and the certificate
does not construct a spacetime distribution or causal Green map.

The next gate is L3 of the
[updated strength ladder](cylinder-wave-strength-ladder-v2.md): formalize the
weak transport/wave identity against a fixed coded localized test class. Only
after that comparison is explicit should the programme attempt finite
propagation or advanced/retarded support. The full normally-hyperbolic factor
and the biwave Volterra wrapper remain beyond this reduced flat fixture.
