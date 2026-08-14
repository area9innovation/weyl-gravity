# BT interacting finite-volume OS kernel obstruction

**Certificate:** `REVERSE_PHYSICS_BT_EUCLIDEAN_LAMBDA04_OS_KERNEL_OBSTRUCTION_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

**Lifecycle:** `OBSTRUCTION_PROVED`

## Result

The positive Bateman--Turok Euclidean Gibbs measure fails ordinary
Osterwalder--Schrader reflection positivity at the simulated coupling
`lambda=0.4` on the periodic `6^4` lattice.  The proof is exact.  It does not
use the Monte Carlo estimate of the earlier reflected observable.

The obstruction uses a negative determinant of the Gibbs-density kernel on
two positive-time half-configurations.  Put `psi=lambda*phi` and let every
listed integer `k` denote `psi=k*log(2)`.  On the three positive time slices
take

```text
p=(-7,0,7),       q=(-6,3,3).
```

Both half-field sums vanish.  After reflection, the full time profile for a
pair of half-configurations is

```text
profile(p,q)=(p0,q0,q1,q2,p2,p1).
```

The fields are spatially constant.  Six spatial neighbors therefore cancel
six of the eight terms in the lattice Laplacian, and the exact curvature at
time `t` is

```text
r_t=2^(k_(t-1)-k_t)+2^(k_(t+1)-k_t)-2.
```

All weights and actions are rational even though the field values contain
`log(2)`.  At `lambda=2/5`, the action per spatial site is

```text
s(p,p) =       6555228825 / 32768
s(q,q) =    1711289113625 / 1048576
s(p,q) =    1920872864825 / 2097152.
```

Consequently

```text
s(p,p)+s(q,q)-2*s(p,q) = 717075/4096 > 0.
```

There are `6^3=216` identical spatial sites, so the full-lattice gap is

```text
S(p,p)+S(q,q)-2*S(p,q) = 19361025/512 > 0.
```

For the two-by-two density kernel

```text
K_ij=exp(-S(i,j)),       i,j in {p,q},
```

reflection symmetry gives a symmetric matrix and

```text
det(K)
 = exp(-S_pp-S_qq) * (1-exp(S_pp+S_qq-2*S_pq))
 < 0.
```

Thus `K` has one negative direction.

## Why a point-kernel determinant is an OS obstruction

Zero-mode fixing means that the two half-fields `x,y` are integrated on

```text
ell(x)+ell(y)=0,
```

where `ell` is the sum of the field over one half.  The centers `p,q` lie in
`ker(ell)`, so all four pairs `(p,p)`, `(p,q)`, `(q,p)`, and `(q,q)` lie on
this integration hyperplane.

Choose equal-shape smooth compact bumps of width `epsilon` around `p` and
`q` in the positive-half field space, and combine them with a negative vector
of `K`.  Their reflected OS form is an integral of the continuous positive
Gibbs density over the zero-mode hyperplane.  After translating to the four
centers and scaling the bump variables,

```text
epsilon^(-(2*n-1)) Q_OS(F_epsilon)
```

converges to a common strictly positive bump factor times the negative
quadratic form of `K`; the exponent `2*n-1` is the dimension left after the
single global sum constraint.  Therefore `Q_OS(F_epsilon)<0` for every
sufficiently small `epsilon`.  These compactly supported functions depend
only on the finite positive-time half and are admissible OS cylinder
functions.

This step is important: four low-density point configurations do not carry
probability mass by themselves.  The bump argument turns the exact pointwise
kernel sign into a genuine negative integral over open neighborhoods.

## Meaning

The previous numerical preflight correctly indicated the sign, but it is now
supporting evidence only.  Ordinary positive-Hilbert OS reconstruction is
rigorously obstructed both at the free endpoint and at `lambda=0.4` on the
declared finite lattice.

This does not make the positive Euclidean measure ill-defined.  It says that
positivity of its Boltzmann density is insufficient to produce a positive
Lorentzian Hilbert space through the ordinary OS theorem.  A specifically
indefinite or Krein reconstruction would require different axioms and a new
certificate.

## Verification

```text
python3 reverse_physics/bt_euclidean_lambda04_os_kernel_obstruction.py --check
python3 reverse_physics/verify_bt_euclidean_lambda04_os_kernel_obstruction.py
python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_lambda04_os_kernel_obstruction
```

The producer uses the spatial reduction.  The independent verifier instead
constructs all `6^4` sites, enumerates all eight neighbors of every site, and
recomputes the three actions using exact fractions.

## Boundaries

- This does not establish failure at every nonzero coupling.
- This does not obstruct a Krein or other indefinite-metric reconstruction.
- This does not provide an interacting volume-uniform estimate.
- This does not construct a continuum or infinite-volume BT measure.
- This does not establish a Born rule, scattering probability, or event rate.
- This does not establish anything tagged `LORENTZIAN-CAUSAL`.

## Next gate

The finite-volume ordinary-OS question at `lambda=0.4` is closed.  The active
continuum gate is now an interacting, volume-uniform negative-Sobolev moment
estimate.  Tightness and identification of a limit remain later gates.

CLOSE-OUT: SHORTFALL -- exact ordinary OS positivity is obstructed at lambda=0.4; the interacting volume-uniform estimate remains open.

EVIDENCE: `reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_LAMBDA04_OS_KERNEL_OBSTRUCTION_V1.json`
