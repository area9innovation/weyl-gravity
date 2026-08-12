# BT six-point two-angle physical Born density

## Result

The complete leading six-external-mass BT tree density is nonnegative on an
exact physical family with two algebraically independent relative-rotation
parameters.  The result is
`REVERSE_PHYSICS_BT_SIX_POINT_TWO_ANGLE_PHYSICAL_BORN_DENSITY_V1`, tagged
`LOCAL-ALGEBRAIC` and `REDUCED-MODE`, at lifecycle state
`COEFFICIENT_COMPUTED`.

Fix the three future-null incoming momenta used by the planar and nonplanar
diagonal certificates.  Apply

\[
 R_x(u)R_z(t),\qquad
 \cos_t={1-t^2\over1+t^2},\quad \sin_t={2t\over1+t^2},\qquad
 \cos_u={1-u^2\over1+u^2},\quad \sin_u={2u\over1+u^2}
\]

to the outgoing triple, with (t,u) independent.  All six all-incoming
momenta remain exactly null and conserve four-momentum.  The complete 220-tree
amplitude, truncated only above the relevant external-mass degree three, has
no term below degree three and has all twenty middle coefficients.  Exact
reduction in \(\mathbb Q(t,u)\) gives

\[
 c_S(t,u)=c_{S^c}(t,u)
 \quad\text{for all ten unordered pairs }\{S,S^c\},\ |S|=3.
\]

In the six-variable square-free mass algebra, the full-mask coefficient of
the amplitude square is the sum over the twenty ordered complement products.
Consequently

\[
 [x_0x_1x_2x_3x_4x_5]\,\mathcal M(x)^2
   =2\sum_{S<S^c}c_S(t,u)^2\geq0
\]

at every real regular parameter pair.  At least one coefficient is a nonzero
rational function, so the density is strictly positive on a dense open
regular subset.  This is stronger than checking finitely many nonplanar
fixtures or tying (u=t/2).

## Why the claim is nonnegative rather than everywhere strictly positive

For one variable, the predecessor certificates proved that the ten numerator
polynomials have gcd one, excluding a simultaneous zero.  In two variables,
gcd one would not suffice: several bivariate polynomials can have isolated
common zeros without a common factor.  A correct strictness proof needs an
ideal, resultant, or equivalent real-algebraic certificate.

The first all-at-once resultant attempt was stopped by the 500 MB memory
ceiling.  A split exact calculation successfully formed several resultants,
but their gcd retained high-degree vertical-degeneracy factors.  Removing
univariate content made the next elimination exceed the same ceiling.  These
are failed strictness attempts, not evidence of a zero.  The certificate
therefore says exactly what follows without that elimination:

- nonnegative at every regular real ((t,u));
- strictly positive generically;
- an isolated or lower-dimensional regular common-zero set is not excluded.

## Exact backend

The earlier direct SymPy \(\mathbb Q(t,u)\) calculation spent five minutes in
multivariate fraction normalization and timed out.  The replacement backend
uses python-flint sparse `fmpq_mpoly` polynomials and standard gcd-cancelled
fraction algorithms.  It retains the full 64-slot square-free mass algebra
but discards degrees above three, since lower degrees are checked absent and
only the middle degree can contribute to the six-derivative kernel.

The producer finishes under the restored 500 MB ceiling.  The certificate
stores reduced numerator/denominator degrees and term counts for all ten
pairs.  It does not serialize multi-megabyte coefficient strings.  Exact
producer replay, content hashes of every input, and an independent explicit
220-tree verifier supply the receipts.

The independent verifier does not use the cached summed-current recursion.
At six separate rational ((t,u)) points away from the old diagonal, it
enumerates all 220 labeled trees as 105 cubic-four, 105 mixed, and 10
quartic-two topologies.  Each fixture independently reproduces the 42-term
full amplitude, all ten complement equalities, the ten-square identity, and a
strictly positive rational density.  These fixtures cross-check the producer;
the global identity itself comes from exact equality in \(\mathbb Q(t,u)\),
not from sampling.

## Physical boundary

This family changes two relative orientation angles while keeping the
incoming and outgoing energy triangle fixed.  The massless three-particle
final-state phase space at fixed total momentum is five-dimensional.  The
result is therefore not positivity over that complete phase space: the
missing data include two final-state shape variables and one orientation
angle in a generic chart.

The theorem is a local leading tree density.  It does not provide a common
prescription for internal poles, an integrated or normalized probability,
loop or KLN positivity, a Møller/LSZ/S operator, Bateman--Turok Eq. (19), a
metric BV/BRST lift, or any `LORENTZIAN-CAUSAL` result.

## Verification receipts

The scoped commands are:

```text
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_six_point_two_angle_physical_born_density.py --write --check
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_six_point_two_angle_physical_born_density.py
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest reverse_physics.tests.test_bt_six_point_two_angle_physical_born_density
```

The final producer passed 16/16 checks in 22.74 seconds with maximum RSS
385,300 KB.  The method-distinct verifier passed 14/14 checks in 0.76 seconds
with maximum RSS 73,136 KB.  Six mutation/unit tests passed in 0.79 seconds
with maximum RSS 73,344 KB.  The affected planar explicit-tree consumer passed
15/15 checks in 38.13 seconds with maximum RSS 124,572 KB.  The
nonplanar-diagonal predecessor is unchanged
and is admitted by its pinned content hash, so its certificate chain was not
rebuilt.  Two Paper V passes completed in 0.48 and 0.49 seconds with maximum
RSS 50,784 and 50,708 KB; two Paper VI passes completed in 0.50 and 0.51
seconds with maximum RSS 50,640 and 50,748 KB.  Tier 3 is unnecessary: no
freeze, release, shared core algebra,
lifecycle promotion, or claim beyond this isolated scalar certificate
changes.

The advisory Science Forge shadow rail completed its corpus census in 2.22
seconds with maximum RSS 336,852 KB, but its bridge audit failed before this
work was imported: the cached Forge 0.0.2 binary was released against a
different standard-library hash, and the current external library then raised
`E9118`.  This is recorded as an advisory toolchain failure, not a pass and not
evidence for the theorem.  The local schema, producer, explicit-tree, unit,
consumer, and TeX rails above remain the applicable gates.

## Next gate

There are two useful continuations.  A memory-bounded elimination can decide
whether the possible common-zero locus is empty.  More importantly for the
physical objective, the kinematic chart should be enlarged to the missing
orientation and final-state shape variables.  Regulated integration is only
scientifically meaningful after the sign and pole structure are controlled
on that larger chart.
