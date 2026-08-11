# Krein state existence versus physical state selection in ZF

## Result

`FOUNDATIONAL_KREIN_STATE_SELECTION_ZF_V1` closes the mathematical
state-existence link for the repository's explicit reduced-mode Krein carrier.
It does not close physical state selection.

The distinction is exact.  If `v` is a named unit coordinate satisfying
`Jv = sigma v`, with `sigma` equal to `+1` or `-1`, then

```text
omega_v(A) = sigma [v, A v] = (v, A v)_0.
```

Consequently

```text
omega_v(1) = 1,
omega_v(A^dagger_0 A) = ||A v||_0^2 >= 0.
```

This is a positive normalized vector state on the operator algebra typed with
the companion Hilbert adjoint.  Its density operator is the explicitly given
rank-one projector `rho_v=|v><v|_0`, which has trace one.  No basis search,
state-existence theorem, Countable Choice, or Axiom of Choice is used: the
mode `v` is already named by energy, chirality, family, and finite coordinate.

The result carries exactly the dependency tags `LOCAL-ALGEBRAIC` and
`REDUCED-MODE`.

## Why the adjoint matters

There are two products and two adjoints in view:

```text
[x,y]       = (x,Jy)_0,
(x,y)_0     = [x,Jy],
A^sharp     = J A^dagger_0 J.
```

The state assertion uses ordinary C*-positivity
`omega(A^dagger_0 A)>=0`.  It does not replace `dagger_0` by the Krein adjoint
and then reuse the word “positive.”  Those are different typed predicates.

For the named positive mode `p=(2,+1,E,0)`, the state is `[p,Ap]`.  For the
named negative mode `n=(3,+1,A,0)`, it is `-[n,An]`.  The sign is not optional:
the raw negative-coordinate functional has value `-1` on the identity and is
not a normalized state.

## Exact finite witness

The independent checker uses

```text
J = diag(1,-1),  p=(1,0),  n=(0,1).
```

It verifies normalization and the distinguishing projection
`P_p=diag(1,0)`, for which

```text
omega_p(P_p)=1,  omega_n(P_p)=0.
```

It then enumerates all 625 two-by-two integer matrices with entries from
`-2` through `2` and checks, using integers only,

```text
omega_v(A^T A)=||Av||_2^2
```

for both signs.  The canonical witness digest is
`872d38d8c7b0fb28bbd16c3e4c3626cdba3da3482389997597491c10e3c14043`.
This finite enumeration is a regression rail for the displayed universal
identity, not a numerical approximation to positivity.

## Fock states

The imported occupation carrier `Gamma_s(H_1)=ell^2(Occ(I))` names its vacuum
coordinate.  The vacuum is `Gamma_s(J)`-positive and therefore defines the
explicit state `<0|A|0>_0`.  A named one-particle A or L occupation is
`Gamma_s(J)`-negative and gives the sign-normalized state `-[m,Am]`.

The two states disagree on the vacuum projector.  State existence is therefore
not state uniqueness.  Moreover, the vacuum is named by the occupation-number
grading—extra structure beyond the bare one-particle `J`.  This certificate
does not show that it is the interacting Weyl or Bateman–Turok state.

## Why J alone does not select a density state

There is a clean conditional no-selection theorem.  Suppose a positive
trace-class density operator `rho` of trace one were invariant under every
finite coordinate permutation preserving the positive and negative `J`
sectors.

Permutation invariance makes all positive-sector diagonal weights equal to a
constant `c_+>=0`, and all negative-sector weights equal to `c_->=0`.  Each
sector contains an explicitly enumerated infinite sequence.  Hence positivity
and trace one imply

```text
N c_+ <= 1,  N c_- <= 1
```

for every natural `N`, so both constants vanish.  The trace of a positive
trace-class operator is the sum of its coordinate diagonal entries.  It would
therefore be zero, contradicting trace one.

Thus no density-operator state is natural under the full sign-preserving
finite-permutation symmetry of the bare `J` carrier.  Finite truncations do
have uniform invariant density matrices: at equal positive and negative
sector size `N`, every coordinate has weight `1/(2N)`.  The checker records
these exact rational controls through `N=12`.  Their fixed-coordinate mass
vanishes with the cutoff; they do not produce a trace-one density on the
infinite carrier.

This theorem does not rule out singular invariant states.  Nor does it say
that all sign-preserving permutations are physical symmetries.  Energy,
dynamics, boundary conditions, detector data, KMS conditions, or BRST
reduction may legitimately break or refine that symmetry.  The result says
only that such additional input is genuinely additional.

## Three cube cells closed

Under the cube's published definition, a **Local result** means a bounded
repository result occupies the intersection; it never means the whole cell is
solved.  Three status changes now follow:

| Mathematical regime | Carrier | Obligation | Old status | New status | Reason |
|---|---|---|---|---|---|
| Classical standard | Krein/indefinite | States/probability | Pieces only | Local result | Explicit positive coordinate and Fock states plus a scoped density-selection obstruction |
| ZF with weakened Choice | Krein/indefinite | States/probability | Priority gap | Local result | The same named rank-one construction uses no Choice |
| Classical standard | Algebraic C*-system | States/probability | Pieces only | Local result | Audit correction: `FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1` already constructs states and GNS representations in ZF |

The C*-cell correction matters methodologically.  The physical obligation says
“construct states, representations, positivity, normalization, Born
probabilities, **or** physical selection rules.”  A local result need not do
all of these.  Leaving that cell at “Pieces only” contradicted both the cell
definition and the existing certificate.

## Boundary and next gate

Nothing here selects a physical Weyl state, derives a generalized Born rule,
constructs an interacting or KMS state, proves a thermodynamic trace-norm
limit, or supplies BRST/Hadamard compatibility.  It makes no
`LORENTZIAN-CAUSAL` claim.

The next gate is no longer abstract state existence.  It is to add one
physical selector—energy/KMS, asymptotic input, detector conditioning, or BRST
reduction—and test it against the repository's higher-point and thermodynamic
obstructions.
