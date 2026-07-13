# Conformal cylinder Born--deformation bridge

Status: exact finite-block algebra, implemented by
`symbolic/verify_conformal_deformation_bridge.py`.  This note fixes the
logical interface between the P4 contact-plus-exchange calculation and the
metric-deformation complex.  It is not a quartic Weyl coefficient.

## Fixed-form expansion

Let the compact-cylinder Hamiltonian and candidate Hermitian form be

```text
H(g)=H0+g V1+g^2 V2+O(g^3),
G(g)=J +g G1+g^2 G2+O(g^3),
```

where `H0^dagger J=J H0`.  Expanding `H^dagger G=G H` gives

```text
H0^dagger G1-G1 H0 = J V1-V1^dagger J,

H0^dagger G2-G2 H0
 = J V2-V2^dagger J+G1 V1-V1^dagger G1.
```

Write the second right-hand side as `S2`.  On a compact-energy eigenspace
`P=P_E`, the left side vanishes because cylinder `D` is semisimple.  Thus
every nonzero component of `P S2 P` is a genuine cokernel coordinate.

For the reduced-resolvent formula below one uses the stronger properties of
the normalizable cylinder basis, not semisimplicity alone:

```text
H0=H0^dagger,  [H0,J]=0,  H0 P=E P,
```

with `P` the **full** energy-`E` eigenspace and hence `Q H0 Q-E` invertible.
These hypotheses make the reduced resolvent self-adjoint and make the shell
deformation map vanish.  A merely diagonalizable `J`-pseudo-Hermitian
operator would require its biorthogonal spectral projectors instead; the
formula written here should not be applied to such a block without that
replacement.

## Canonical off-shell solution

Set `Q=1-P` and use the self-adjoint reduced resolvent

```text
R_E=Q(E-H0)^(-1)Q.
```

If the first-order shell source vanishes, choose the canonical off-shell
solution with zero homogeneous shell block.  With

```text
D1=J V1-V1^dagger J,
```

its relevant components are

```text
P G1 Q= P D1 R_E,
Q G1 P=-R_E D1 P.
```

The projected cross term is then

```text
P(G1 V1-V1^dagger G1)P
 =P[J V1 R_E V1-(V1 R_E V1)^dagger J]P.
```

Therefore the complete second-order source satisfies the exact identity

```text
P S2 P = J_P B2(E)-B2(E)^dagger J_P,

B2(E)=P[V2+V1 Q(E-H0)^(-1)Q V1]P.
```

Equivalently, with the P4 convention,

```text
B2(E)=P[V2-V1 Q(H0-E)^(-1)Q V1]P.
```

This fixes the relative contact/exchange sign.  It proves that the
`J`-anti-Hermitian part of the correctly normalized stationary Born block is
the metric-deformation cocycle; a raw contact or stripped covariant amplitude
is not enough.

This algebra does **not** by itself prove that coefficients extracted from a
covariant four-wave action and bordered Fourier-space Hessian already use
that stationary normalization.  The P4 archive must separately derive the
overall `i` convention, the derivative-interaction contact map, both old-
fashioned time orderings, compact-state/LSZ factors and the energy
denominators.  That covariant-to-stationary certificate is an input to this
identity, not a consequence of the finite-block matrix check.
The fail-closed P4 schema stores this derivation in
`stationary_born_mapping.json`, cross-links its exact operator inputs to the
combined archive, and independently recomputes the effective block, source
and cokernel coordinates.

The product above is **operator composition**.  If an archive stores
lower-index Krein amplitudes rather than mixed-index operator matrices, every
intermediate contraction must explicitly raise the internal index with the
inverse Gram matrix `J_Q^(-1)`.  Omitting that factor changes ghost signs and
does not represent `V1 R_E V1`.  The P4 archive must state which convention
its left/right currents use and verify their equivalence after index raising.

## Operator scope

The identity applies to a consistently defined perturbative operator.  For
the current P4 target this is the normal-ordered **connected tree** block:

* the quartic canonical contact, including instantaneous/constraint pieces;
* every connected one-internal-line cubic exchange and time ordering;
* the same finite-volume or compact-cylinder state normalization in both
  terms;
* cancellation of disconnected vacuum factors;
* subtraction/LSZ normalization of reducible external-state corrections;
* an independently assembled reverse block defining the physical adjoint.

The unqualified quantum Feshbach operator also contains the infinite
self-energy/loop tails classified in
`notes/conformal-quartic-intermediates.md`.  The same algebra applies only
after those sums are regulated and the corresponding counterterms and state
renormalization are included.  A finite one-line archive must not be called
that full operator.

## First-order ambiguity

A homogeneous first-order correction `X` commutes with `H0`.  Its change of
the second-order shell source is

```text
P(X V1-V1^dagger X)P.
```

The stronger all-shell cubic statement

```text
P V1 P=0
```

makes this vanish for every `X`, exactly as in the Paper-VI bridge.  Merely
knowing the first-order pseudo-Hermiticity source

```text
P(J V1-V1^dagger J)P=0
```

is not sufficient: a nonzero `J_P`-self-adjoint `P V1 P` can still make the
second-order source depend on the homogeneous choice.  The executable
certificate includes an exact counterexample.

This is why the unresolved mixed-chirality EAL orbit is logically important.
Until the complete cubic shell block is either proved zero or incorporated
jointly with its first-order metric freedom, the P4 calculation yields a
canonical-source certificate, not yet an ambiguity-independent no-go
theorem.

## Reproduction

```bash
python3 symbolic/verify_conformal_deformation_bridge.py
```

Expected final line:

```text
CONFORMAL DEFORMATION BRIDGE: ALL PASS
```
