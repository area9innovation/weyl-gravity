# Phase 3 axial endpoint remainder enclosures

Date: 23 July 2026
Result token: `BH_PHASE3_AXIAL_ENDPOINT_REMAINDER_ENCLOSURES_V1`
Disposition: **SHORTFALL**

## Scope

This audit imports the complete axial six-state Schwarzschild reconstruction at
commit `d5d5d6de648795203604d62ce7bc4f4ce6fea510`.  It treats the axial
`ell=2` system in ingoing Eddington--Finkelstein coordinates, with `M=1`,
time dependence `exp(+i omega v)`, and real dimensionless frequency

```text
1/2 <= omega <= 3/4.
```

It asks only for rigorous finite-radius endpoint bases suitable for the later
validated connection calculation.  It does not calculate a connection matrix,
flux, scattering channel, pole, stability statement, or CPT metric.

## Future-horizon result

With `rho=r-2`, the repaired metric state is sheared to

```text
x=(P,P',Q,Q',H1,rho F),            rho x' = B(rho,omega) x.
```

The coefficient `B` is analytic for `|rho|<2`.  Its exact residue polynomial is

```text
lambda^3 (lambda+4 i omega)
         (lambda+1+4 i omega)
         (lambda+2+4 i omega).
```

Three recurrence orders were solved exactly.  Every resonant equation is
compatible, including the retained order-two resonance.  A Cauchy estimate on
the complex disk `|rho|<=1/2` gives

```text
M = 1081328809/46560,
tau = 1/262144,
epsilon = 1/4194304,
S_B(tau) = 1081328809/6102665760 < 1/4.
```

Four rational omega cells cover the pilot interval.  On each cell the Forge
`math/ivendpoint` adapter returns outward boxes for all six complex columns and
their derivatives, realified to dimension twelve, and certifies basis rank.
The public Forge interface is

```text
axial_horizon_initializer(which)
axial_horizon_epsilon()
axial_horizon_to_standard(x,rho)
```

The final function records the exact chart conversion; rows corresponding to
`F` are divided by `rho`.  Invalid cell indices fail closed.

## Infinity result

All four imported Ricci-carrier columns now have exact log-free metric lifts.
For the oscillatory `XI2` and `XI3` columns the `n=1` resonance obstruction is
exactly zero.  Together with the two Einstein-kernel columns this gives the
ordered formal basis

```text
[XI0, XI1, XI2, XI3, EI0, EI2].
```

Writing the phase-normalized formal matrix in weighted block form gives

```text
G = [[C,0],[M,K]],
det(C_weighted) = z^5 D(z,omega),
D(0,omega) = 4 omega^2,
z=1/r.
```

An exact rectangle/Neumann estimate proves

```text
|K_N,ij(r)| <= C_ij r^(-p_ij),      r >= R,
R = 2^256,
q_infinity < 1/4.
```

The exact contraction constant is about `1.1188e-104`.  Every nonzero entry has
`p_ij>1`; the decay table is

```text
6 7 6 7 99 99
5 6 5 6 99 99
6 7 6 7 99 99
5 6 5 6 99 99
3 4 3 3  5  4
4 5 3 3  6  5
```

Here `p=99,C=0` denotes an identically zero entry.  The certificate includes
exact outward boxes for `F_N(R)` and `F_N'(R)` on all four frequency cells.
Thus an omega-uniform six-column **existence enclosure** is established at the
proof radius.

## Why the work item remains a shortfall

`R=2^256` is intentionally proof-oriented.  Directly evolving the raw
six-state interval flow between that radius and the black-hole exterior is
computationally infeasible and wrapping dominated.  It is therefore not the
stable initializer consumed directly by `math/ivlinode` required by the work
item.

A bounded generic-symbolic `N=8` attempt was also audited.  The carrier source
requires coefficients to approximately depth ten, and generic rational-omega
expressions exhaust memory before that depth.  A smaller exact repair was then
made: the derivative-forced fourth `F` coefficient was restored in `XI2` and
`XI3` with canonical `H1_4=0`.  This raises the two cross-rate entries from
`p=2` to `p=3`; hence the phase-normalized `z`-flow coefficient is continuous
at `z=0`.  The remaining shortfall is quantitative: the existing primitive
constants are far too coarse for a stable validated march to `R=32`.

The clean successor has two possible implementations:

1. a cellwise interval/Krawczyk recurrence at practical `R=32,64,128`; or
2. a phase-normalized correction flow in `z=1/r` from `z=0` to a practical
   radius.

The derivative-consistency repair has already made every cross-rate entry
`p>=3`.  The successor can therefore define the `z=0` callback by its exact
same-block limits and zero cross-block limits, bounding unevaluated oscillatory
phases by the unit circle on intervals touching zero.

## Verification

The durable evidence consists of:

- exact horizon recurrence and Cauchy-majorant reproduction;
- independent structural certificate verification;
- exact branch-by-branch infinity metric-head verification;
- independent weighted-Volterra-envelope replay;
- six negative mutations, including a recurrence mutation, a remainder
  mutation, a frequency-cell gap, a false practical promotion, and a
  nonintegrable decay exponent;
- Forge C/ASan verification returning exit code 42.

## Claim boundary

Established:

- outward, rank-certified six-column horizon boxes on the complete pilot;
- exact log-free six-column formal infinity heads;
- an integrable omega-uniform Volterra existence enclosure at `R=2^256`.

Not established:

- a practical-radius infinity dispatcher;
- validated horizon-to-infinity matching;
- finite Lee--Wald flux, scattering, poles, stability, or CPT positivity;
- complex frequencies, polar parity, or frequencies outside the pilot.

CLOSE-OUT: SHORTFALL — the singular endpoint existence proofs close, but the infinity proof radius is not a stable direct `math/ivlinode` handoff.
