# E-D1a: the cylinder generator at null infinity

## Result

The first asymptotically flat step is a generator dictionary, not a charge
calculation.  It separates three objects that the earlier discussion called
`D`:

```text
H_ESU = real time translation d_T on the Einstein static universe,
D_M   = real Lorentzian Minkowski dilation t d_t+r d_r,
D_rad = compact grading used by radial quantization/residual modules.
```

`bridge/certificates/d_quotient_asymptotic_seed.json` proves the real
coordinate identities below with tags `LOCAL-ALGEBRAIC` and `REDUCED-MODE`.
It carries no `LORENTZIAN-CAUSAL` claim.

## Real Penrose map

Use

```text
u=tan U, v=tan V,
U=(T-R)/2, V=(T+R)/2,
Omega_P=cos T+cos R=2 cos U cos V.
```

The real cylinder time translation pushes into the Minkowski patch as

```text
H_ESU = (1+u^2)/2 d_u+r(u+r)d_r.
```

For the inverse-radius defining function `Omega=1/r`,

```text
H_ESU(Omega)=-(1+u Omega).
```

It therefore approaches `-1` at future null infinity.  Real cylinder time
crosses the boundary of a fixed Minkowski patch; it is not an asymptotic
symmetry of that one patch.  In conformal-algebra notation it is the real
combination `(P_0+K_0)/2` in the convention displayed by the certificate,
not `P_0` and not the real dilation.

Conversely,

```text
D_M=u d_u+r d_r
```

obeys

```text
L_(D_M) g=2g,
D_M(Omega)=-Omega,
D_M restricted to I_plus=u d_u.
```

It is tangent to `I_plus`.  Its pullback to the real cylinder is

```text
D_M=sin(T)cos(R)d_T+cos(T)sin(R)d_R,
```

which is not `d_T`.  It nevertheless preserves `T+R=pi` because its action
on that defining equation vanishes there.

The standard statement “the cylinder Hamiltonian is `D`” belongs to radial
quantization: it uses a Cayley/Wick continuation and the radial adjoint.  It
must not be substituted silently for the real Lorentzian Penrose
push-forward.  The residual module may continue to call its compact grading
`D`; the asymptotic programme must attach a real form and boundary lift before
assigning that generator a surface charge.

## Why Bondi energy does not answer this question

In Bondi coordinates,

```text
P_0=d_u,
[D_M,P_0]=-P_0.
```

Thus the three candidate Hamiltonians are distinct.  A nonzero ADM/Bondi
charge for `P_0` proves that time translation is not proper gauge, but it
does not compute the charge of `D_M` or `H_ESU`.  The earlier phrase
“time-translation/`D` charge” must therefore be split into separate tests.

## Reduced flat-dilation boundary test

The combination

```text
T_s(g)=exp(-2s) Phi_s^*g,
Phi_s(u,r)=(exp(s)u,exp(s)r)
```

fixes the Minkowski background.  The Weyl parameter is `sigma=-1`
infinitesimally.  On

```text
g_AB=r^2 q_AB+r C_AB+...,
N_AB=d_u C_AB,
```

the exact reduced action is

```text
C_s(u,x)=exp(-s) C(exp(s)u,x),
N_s(u,x)=N(exp(s)u,x),

delta_D C=u d_u C-C,
delta_D N=u d_u N.
```

Consequently the candidate strong core

```text
N in L1_u Hs(S2) intersect L2_u Hs(S2),
C with finite Hs endpoint limits
```

is mapped into itself for finite `s`.  Its news norms and memory rescale as

```text
||N_s||_L1=exp(-s)||N||_L1,
||N_s||_L2^2=exp(-s)||N||_L2^2,
Delta C_s=exp(-s)Delta C.
```

This is only reduced kinematics.  The second Bach radiative pair, Coulombic
aspects, soft completion, `i0` matching, ghosts, antifields, counterterms,
and presymplectic flux have not been shown to transform within a common
phase space.  In particular, the physical Weyl compensator is not declared
proper gauge at the boundary.

The appropriate comparison is the enlarged BMSW phase-space programme,
which explicitly treats local Weyl rescalings as boundary transformations
with renormalized charges in Einstein gravity
([Freidel et al.](https://arxiv.org/abs/2104.05793)).  Its nonlinear action
on Bondi data has also been derived
([Flanagan and Nichols](https://arxiv.org/abs/2311.03130)).  Neither result is
a pure-Weyl null-infinity charge certificate.  Existing conformal-gravity
charge results likewise depend on their declared, non-null-infinity boundary
conditions ([Irakleidou, Lovrekovic, and Preis](https://arxiv.org/abs/1412.7508)).

## Triangular Einstein-defect seed

For the reduced field order `(h,chi)`, with `chi=Box h`, write

```text
P = [[Box,-1],
     [0, Box]].
```

If a common invariant domain already carries a two-sided retarded or advanced
wave Green operator `G`, exact matrix multiplication gives

```text
G_P = [[G,G G],
       [0,  G]].
```

Both inverse remainders are

```text
[[Box G-1, G(Box G-1)],
 [0,       Box G-1]].
```

Composition retains retarded/advanced support by causal transitivity.  This
is the correct operator-algebra seed for E-D2, and `chi=0` is the formal
Einstein invariant subspace when its source and Cauchy data vanish.  It is
not yet a Green-complex theorem: no weighted/polyhomogeneous tensor domain,
constraint-compatible gauge complex, or corner map has been supplied.

## Verdict and next closure condition

The required fail-closed verdicts are

```text
asymptotically flat D: PHASE_SPACE_NOT_CLOSED,
Einstein sector:       EINSTEIN_OPEN.
```

`PHASE_SPACE_NOT_CLOSED` does not mean `D_GAUGE` or `D_CHARGED`.  It records
two precise obstructions:

1. real cylinder time does not preserve a fixed Minkowski null boundary;
2. flat dilation preserves the reduced radiative core, but the full Bach
   phase space and charge have not been constructed.

The next theorem must choose one real boundary generator, complete all Bondi
and defect data under its action, and compute the renormalized charge and
flux.  Only then is either a quotient or a charged asymptotic symmetry a
well-posed conclusion.

## Verification

```bash
python3 -m bridge.einstein_sector.d_quotient_asymptotic_seed --verify bridge/certificates/d_quotient_asymptotic_seed.json
python3 -m unittest bridge.einstein_sector.tests.test_d_quotient_asymptotic_seed
```
