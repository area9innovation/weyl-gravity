# Berger 84-row apparatus q2/q3 and K gate

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`.

## Result

The normalized apparatus interaction is now constructed through the declared
two-jet.  The exact action is organized by three densitized geometric maps:

```text
A_g^{mu nu} = sqrt(|g|) g^{mu nu},
V_gTheta^mu = sqrt(|g|) g^{mu nu}Theta_nu/g^{-1}(dTheta,dTheta),
W_a[A] = sqrt(|g|) f_a(Theta)rho_a(R_a)sqrt(det G_a)
         C_g(dA,dTheta wedge dR_aI(a)).
```

The lowered cubic tensor `C3=Omega84 q2` is the third derivative of the rod,
memory-transport, normalized readout, and scalar-BV actions, added to the
pinned typed 64-row `q2`.  The lowered quartic tensor `C4=Omega84 q3` is the
corresponding fourth derivative added to the pinned 59,598-term 64-row `q3`.
Raising the output with the frozen 84-row pairing generates every cotangent
partner from the same symmetric tensor; no output-only normalization is used.

The transverse normalization contributes

```text
D J[X] = J/2 tr(G^-1 DG[X]),
D2 J[X,Y] = J[1/2 tr(G^-1 D2G[X,Y])
  +1/4 tr(G^-1 DG[X])tr(G^-1 DG[Y])
  -1/2 tr(G^-1 DG[X]G^-1 DG[Y])].
```

Exact determinant fixtures and a five-factor product audit independently
verify the full first and second readout jets.  Deleting either quadratic
trace term or the pair partitions produces nonzero defects.

## Identity scope

The common BV action proves `q2,q3` cyclicity and the arity-two and
arity-three identities at `r=0`.  At the first backreacted coefficient,

```text
delta_r q2 = q3(Phi2,-,-)
```

is determined and the arity-two identity closes.  But

```text
delta_r q3 = q4(Phi2,-,-,-)
```

is not determined by a profile two-jet or the imported base `q3`.  Therefore
the backreacted arity-three identity is not promoted.

## Why ordinary K_Berger equivariance fails

The backreacted apparatus background is not fixed by the linear generator:

```text
K0 Rbar_aI = e0 Rbar_aI != 0,
K0(gHat+r Phi2) = r e0 Phi2 != 0.
```

There are exact nonzero rod witnesses inside both detector windows and 70
nonzero time-dependent `Phi2` coefficients.  The honest action is affine,
`K=K0+K1`.  Its hierarchy contains

```text
arity 1: [K1,q1]+q2(K0,-)=0,
arity 2: [K1,q2]+q3(K0,-,-)=0,
arity 3: [K1,q3]+q4(K0,-,-,-)=0.
```

The first two identities are determined by the new jets.  The third is not:
two exact `q4` completions with identical `q1,q2,q3` change its normalized
commutator coefficient by `91/6`.  The missing inputs are the base `q4`, the
third normalized profile and memory-transport jets, and the fifth rod-action
derivative.  This is a `K_Berger` affine arity-three input obstruction, not a
failure of the retarded signal.

The obvious six-row repair is also excluded exactly.  Resolving the present
six real rods in
`span{cos(nu t),sin(nu t)} tensor span{x0,x1,x2,x3}` gives rank six, while
adjoining their time derivatives gives rank eight.  Hence no constant
six-by-six internal rod rotation can absorb `e0 Rbar`.  The smallest linear
time-translation-closed replacement needs two more real rods and, with their
cotangent partners, an 88-row carrier.  That co-rotating replacement is a
separate constructive alternative: its stress, `Phi2`, unary complex, and
interactions must all be recomputed before it can support an extended-`K`
observer morphism.

## Record rank and boundary

On the maximal Maxwell-gauge/cyclic coefficientwise unary response,

```text
M(r,kappa)=M00+...,
M00=diag(C_00,C_11),
det M|_constant=C_00 C_11 != 0.
```

Hence the two records remain rank two over the formal coefficient ring.  This
does not yet define a `K_Berger`-descended observer morphism.  It also does not
establish finite-`r` Green hyperbolicity, localized emitter recoil, a
Lorentzian quantum theory, or any quantum claim.
