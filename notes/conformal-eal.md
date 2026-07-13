# Conformal-cylinder EAL two-seed certificate

The current normalizable mode-representative enumerator leaves `EAA`, `EAL`,
and `AAL` after the Einstein-subsector selection rule.  EAL has two
parity-inequivalent tensor structures.  This note records an exact seed
certificate for each one.  Identification with complete physical BRST
cohomology remains conditional on the global conformal-charge and
linearization-stability audit.

## Correct nonmaximal product projection

For the same-chirality seed

```text
E2(2,0) + A3(3/2,1/2) -> L5(5/2,1/2),
```

the output is one step below the maximal left-`SU(2)` product.  The incoming
highest-weight state is therefore not a single product.  Exact
Clebsch--Gordan projection gives

```text
|EA;5/2,1/2>
 = (2/sqrt(7)) |E(2,0) A(1/2,1/2)>
   -sqrt(3/7)  |E(1,0) A(3/2,1/2)>.
```

The coefficients have unit square norm.  Every harmonic entering the two
terms and the outgoing `L5` harmonic is independently unit normalized.

An undifferentiated scalar cannot contract the odd vector index.  A natural
allowed derivative-Gaunt invariant is

```text
int_S3 L5*^{ij} E_i^k nabla_k A_j=-sqrt(21)/(3 pi) != 0.
```

Its exact radial scalar before the `S3` measure is

```text
-sqrt(21)/[3 pi^3(1+t^2)].
```

Thus energy, representation theory, and harmonic orthogonality all permit
the channel.  This derivative overlap is a selection certificate, not the
complete Weyl Hamiltonian coefficient.

## Four independent curvature components

`symbolic/verify_conformal_aal_vertex.py` was extended with four explicit
component modes.  They are reproduced by

```bash
python3 symbolic/verify_conformal_aal_vertex.py eal-1
python3 symbolic/verify_conformal_aal_vertex.py eal-2
python3 symbolic/verify_conformal_aal_vertex.py eal-reverse-1
python3 symbolic/verify_conformal_aal_vertex.py eal-reverse-2
```

The two forward coordinate densities before `d beta` are

```text
D1(t)= i sqrt(6) t(t^2-1)/[1920 pi^3(1+t^2)^2],
D2(t)=-i sqrt(2) t(t^2-1)/[ 640 pi^3(1+t^2)^2].
```

The independently assembled reverse densities are their exact complex
conjugates.  Every component is locally nonzero but integrates to zero.

Applying the normalized CG projection gives

```text
D_EAL(t)
 =i sqrt(42) t(t^2-1)/[2688 pi^3(1+t^2)^2].
```

The reverse projected density is `D_EAL(t)^*=-D_EAL(t)`.

## Legendre/Jacobi mechanism

Include the stereographic radial measure and set

```text
I(t)=2D(t)/(1+t^2),
u=t^2/(1+t^2).
```

Then

```text
I_EAL(t)dt
 = [i sqrt(42)/(2688 pi^3)] (2u-1)du
 = [i sqrt(42)/(2688 pi^3)] P_1^(0,0)(2u-1)du.
```

This is the `alpha=beta=0` Jacobi polynomial, equivalently the degree-one
Legendre polynomial against the constant beta weight.  Its primitive is

```text
-[i sqrt(42)/(2688 pi^3)] u(1-u),
```

which vanishes at `u=0,1`.  Hence both independently assembled directed Weyl
coefficients vanish separately.

The one-particle `L5` state has sign `-`, while the two-particle `E2 A3`
state has sign `(+) (-)=-`.  In the ordered basis
`(|E2 A3>,|L5>)`,

```text
J_EAL=-I_2,
V_EAL=0,
J_EAL V_EAL-V_EAL^dagger J_EAL=0.
```

As in EAA, this is stronger than fixed-form pseudo-Hermiticity: the metric
does not cause the cancellation because each integrated transition entry is
already zero.

## Mixed-chirality EAL tensor structure

The same-chirality seed is the only EAL parity orbit when the Einstein spin
is `J_E=1`.  For `J_E>=3/2`, EAL has a second mixed-chirality reduced channel.
Its first representative is

```text
E3(5/2,1/2) + A3(1/2,3/2) -> L6(3,1).
```

The left product is maximal while the right product is one step below
maximal.  The exact projected right-`SU(2)` coefficients are

```text
(1/2, -sqrt(3)/2).
```

All five harmonics entering this projection are independently unit
normalized.  The allowed derivative-Gaunt invariant is again nonzero:

```text
int_S3 L6*^{ij} E_i^k nabla_k A_j = 1/(3 pi).
```

Its exact radial scalar is

```text
1/[2 pi^3 (1+t^2)^2].
```

Thus the mixed channel is permitted by energy, representation theory, and
harmonic overlap.

The four exact curvature runs are

```bash
python3 symbolic/verify_conformal_aal_vertex.py mixed-eal-1
python3 symbolic/verify_conformal_aal_vertex.py mixed-eal-2
python3 symbolic/verify_conformal_aal_vertex.py mixed-eal-reverse-1
python3 symbolic/verify_conformal_aal_vertex.py mixed-eal-reverse-2
```

The two forward local densities before `d beta` are

```text
D1(t)=i sqrt(6) t(-2t^4+5t^2-1)/[1280 pi^3(1+t^2)^4],
D2(t)=i sqrt(2) t(-10t^4+t^2+3)/[1280 pi^3(1+t^2)^4].
```

The reverse calculations give their exact complex conjugates.  Applying the
normalized `(1/2,-sqrt(3)/2)` projection collapses the result to

```text
D_mixed(t)=i sqrt(6) t(2t^2-1)/[640 pi^3(1+t^2)^3].
```

After including `d beta=2dt/(1+t^2)` and setting
`u=t^2/(1+t^2)`, this becomes

```text
I_mixed(t)dt
 = [i sqrt(6)/(640 pi^3)] (1-u)(3u-1)du
 = [i sqrt(6)/(640 pi^3)]
     (1-u) P_1^(1,0)(2u-1)du.
```

The primitive

```text
-[i sqrt(6)/(640 pi^3)] u(1-u)^2
```

vanishes at both endpoints.  Both directed matrix elements therefore vanish
separately.  Since `sign(EA)=(+)(-)=-=sign(L)`, the induced form is again

```text
J_mixed=-I_2,
V_mixed=0,
J_mixed V_mixed-V_mixed^dagger J_mixed=0.
```

This closes the first normalizable representative of each EAL tensor
structure.  It does not yet prove their all-spin continuation, their descent
to physical BRST cohomology, or the all-shell conjecture
`P_Delta V3 P_Delta=0`; those require the generic harmonic recurrence,
conformal descent, and the global conformal-charge constraint audit.

## Lightweight certificate

```bash
python3 symbolic/verify_conformal_eal_vertex.py
```

Expected final line:

```text
CONFORMAL EAL SEED HARMONICS: ALL PASS
```
