# The BT separable C*-algebra to physical-state chain

## Result

`FOUNDATIONAL_BT_SEPARABLE_STATE_CHAIN_ZF_V1` separates five implications
that are often bundled under “choose a Hilbert-space state.”  Its tags are
`LOCAL-ALGEBRAIC` and `REDUCED-MODE`; its lifecycle is `SEPARATED`, because
the mathematical existence links close but physical state selection does not.

```text
ALGEBRA_CONSTRUCTION          ZF  proved for K(ell^2(Z))~
POSITIVE_FUNCTIONAL_EXISTENCE ZF  explicit faithful and corner states
GNS_REPRESENTATION            ZF  explicit standard representation
PHYSICAL_STATE_SELECTION       --  not implied; thermodynamic state open
DYNAMICS_AND_LOCAL_NORMALITY    --  coherent candidate not dynamically selected
```

No Countable Choice is used in the first three links.

## Four different algebras and objects

The repository source constructs a faithful normal semifinite trace on
`B(ell^2(Z))`.  That algebra is not norm-separable.  Its compact ideal
`K(ell^2(Z))`, however, is separable, as is its unitization

```text
A = K(ell^2(Z))~.
```

Finite complex-rational matrices in the canonical integer basis, together
with rational complex multiples of the identity, give an explicit countable
dense subset.  This is the correct separable algebra for the finite-detector
state audit.  It must not be conflated with either all of `B(ell^2(Z))` or the
distinct quasi-local resolution CCR algebra used by the coherent completion.

## Links 1--3: algebra, states, and GNS in ZF

Enumerate the integer basis explicitly by

```text
z(0)=0, z(2k-1)=k, z(2k)=-k
```

and assign weights `w_j=2^(-j-1)`.  Then

```text
rho(T) = sum_j w_j <e_z(j),T e_z(j)>
```

is a faithful state on `A`.  Faithfulness follows directly for positive
operators: if every diagonal entry is zero, the positive square root kills
the dense coordinate basis and hence the operator is zero.  No state is
selected from an unlabelled family.

The localized corner state

```text
omega_0(T)=<e_0,T e_0>
```

has an equally explicit GNS realization: the standard representation on
`ell^2(Z)` with cyclic vector `e_0`, since `E_n0 e_0=e_n`.  At finite radius
three the independent checker reconstructs its seven-dimensional GNS Gram as
the identity from 49 matrix units.

This concrete proof agrees with Blackadar and Farah's ZF results: separable
C*-algebras have sufficiently many states, a faithful state, and a faithful
representation on a separable Hilbert space.  Their Theorem 4.0.1 also marks
the opposite boundary: `B(H)` is norm-separable exactly when `H` is finite
dimensional.  These theorems establish mathematical existence, not physical
selection.

## The semifinite trace is not a state

The source weight is

```text
tau(T)=sum_n <e_n,T e_n>,   T>=0,
tau(E_nn)=1,                tau(1)=infinity.
```

It is faithful, normal and semifinite.  It is not a normalized functional on
the identity.  Conditioning on a finite nonzero projection `P` gives the
normal state

```text
omega_P(T)=tau(PTP)/tau(P).
```

But `P` is extra detector or incoming-state data, not a consequence of the
C*-algebra axioms.  Moreover the corner state is not tracial.  The exact
matrix-unit witness is

```text
omega_0(E_01 E_10)=1,   omega_0(E_10 E_01)=0.
```

Thus the conditional Born theorem does not contradict the earlier normalized
cyclic-trace obstruction.

## Links 4--5: physics does not follow from GNS

The repository has a mathematically valid locally normal coherent state on a
different quasi-local resolution CCR algebra.  Its one-emission rate and
rank-two physical GNS factor are constructed.  Initially, independent
increments gave the Poisson two-count coefficient `1/512`.

The committed six-point tree instead gives `5/512`: a factor five mismatch.
Consequently the coherent state remains a well-defined state but is not the
state dynamically selected by the nonlinear tree data.  State existence,
GNS representation, physical state selection, and dynamics are therefore
strictly different claims in this example.

The full-orbit normal trace-class thermodynamic limit also remains obstructed.
Abstract ZF state-existence theorems do not decide which finite projection is
incoming, choose a non-Gaussian completion from a few cumulants, construct the
nonlinear Moller operator, or prove Eq. (19).

## Boundary and next gate

This certificate does not construct a thermodynamic physical state, a finite
trace of the identity, a unique non-Gaussian count law, full nonlinear
dynamics, a gravitational lift, or a `LORENTZIAN-CAUSAL` result.

The next state question requires additional physical cumulants and positivity,
not another existence theorem.  Any candidate must remain explicitly distinct
from the separable compact-detector algebra and from the semifinite weight.

## Literature

The ZF claims are pinned to Bruce Blackadar and Ilijas Farah, *Separable
C*-algebras Without the Countable Axiom of Choice*,
[arXiv:2602.15812](https://arxiv.org/abs/2602.15812).
