# Generic-spin EAL harmonic rail and open curvature recurrence

This note separates the exact all-spin harmonic result from the curvature
identity that remains open.  It concerns normalizable highest-weight
metric-mode representatives on the cylinder.  Descent to complete physical
BRST cohomology is conditional on the `SO(4,2)` descent and global conformal-
charge/linearization-stability audits.

## Exact harmonic and Clebsch--Gordan result

Put

```text
n=2 J_E,  m=2 J_A,  p=2 J_L=n+m-1.
```

There are two parity-inequivalent positive-output-chirality products:

```text
same:  E_+(n) A_+(m) -> L_+(p),  n,m >= 2,
mixed: E_+(n) A_-(m) -> L_+(p),  n >= 3, m >= 2.
```

Each chiral product is multiplicity one, but one `SU(2)` product is one step
below maximal and therefore requires two magnetic products.  With the phase
and Wigner conventions used by the cylinder constructor, their exact
normalized coefficient vectors are

```text
c_same = (
  sqrt((n+2)/(n+m+3)),
 -sqrt((m+1)/(n+m+3))
),

c_mixed = (
  sqrt((n-2)/(n+m-1)),
 -sqrt((m+1)/(n+m-1))
).
```

`symbolic/verify_conformal_eal_generic_harmonics.py` gives closed
stereographic coordinate expressions for every required highest and
once-lowered `E`, `A_+`, `A_-`, and outgoing `L` harmonic.  It verifies them
against the full Wigner-D/Clebsch--Gordan constructor at

```text
(n,m)=(2,2),(2,3),(3,2),(3,3),(4,2),
```

where each orbit is included when admissible.  It also verifies exact compact
energy and both azimuthal-weight conservation laws component by component.

The reverse convention conjugates each spatial harmonic and negates its
compact-energy and azimuthal weights.  Since both coefficient vectors are
real, reverse assembly conjugates the projected density without an extra
intrinsic phase.  The finite same- and mixed-chirality seed certificates
independently construct both directions and confirm this convention.

Run the exact lightweight rail with

```bash
python3 symbolic/verify_conformal_eal_generic_harmonics.py
```

Its expected final line is

```text
CONFORMAL GENERIC EAL HARMONICS: ALL PASS
```

## Exact finite curvature seeds

The two fully assembled curvature seeds are

```text
same (n,m)=(2,2):
D(t)=C_same t(t^2-1)/(1+t^2)^2,
C_same=i sqrt(42)/(2688 pi^3),

mixed (n,m)=(3,2):
D(t)=C_mixed t(2t^2-1)/(1+t^2)^3,
C_mixed=i sqrt(6)/(640 pi^3).
```

Both have nonzero allowed derivative-Gaunt overlaps and locally nonzero Weyl
densities.  Both forward and reverse integrated coefficients nevertheless
vanish separately by their exact endpoint primitives.  Thus neither seed is
a Gaunt-selection zero, a forward/reverse cancellation, or a metric-sign
cancellation.

## Precise open recurrence lemma

Writing `N=n+m`, the two seeds motivate the orbit-dependent identity

```text
D_orbit(t)
 = C_orbit(n,m)
   t[(N-3)t^2-1]/(1+t^2)^(N-2).
```

After including `d beta=2 dt/(1+t^2)` and using

```text
u=t^2/(1+t^2),
```

this would become

```text
I_orbit(u) du
 = C_orbit(n,m)
   (1-u)^(N-4) P_1^(N-4,0)(2u-1) du

 = d[-C_orbit(n,m) u(1-u)^(N-3)].
```

The primitive vanishes at both endpoints for every admissible same or mixed
spin.  This Jacobi consequence is proved symbolically.  What is **not** yet
proved is that the complete CG-projected Weyl curvature density has the
displayed radial factor for arbitrary symbolic `n,m`.

A direct projected attempt constructed both magnetic curvature components,
formed their CG sum before global reduction, and normalized more than 75,000
distributive radial terms in each orbit.  It remained in exact symbolic
reduction after the imposed 20-minute bound, so it was stopped and is not
retained as a certificate.  No contrary radial term or nonzero integral was
found; equally, no generic quotient was obtained.  The recurrence above must
therefore remain a lemma to prove, not a computed theorem.

## Scope still open

Even a proof of the radial recurrence on these representatives would not by
itself establish `P_Delta V_3 P_Delta=0` on physical BRST cohomology.  The
remaining inputs are:

1. descent through all `SO(4,2)` components and parity conjugates;
2. independence under BRST-representative changes and auxiliary/Stueckelberg
   completion;
3. the global conformal-charge/linearization-stability constraint audit;
4. completeness of the reduced cubic-family enumeration.

Accordingly, the exact result at this checkpoint is the all-spin
harmonic/CG construction plus two finite curvature seeds.  The all-spin Weyl
recurrence and the physical all-shell theorem remain open.
