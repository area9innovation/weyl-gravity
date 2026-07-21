# Two-phase counterflow background component and round disposition

## Result

The selected counterflow Berger background is a genuine healthy causal point,
but it is **not** an open fixed-action phase of geometrically distinct
stationary backgrounds.  In the complete declared homogeneous Berger family,
the positive stationary locus of the certified action is the singleton

\[
(q,x,C)=\left(\frac9{40},1,\frac9{16}\right),
\qquad
q=\frac{c^2}{a^2},\quad x=a^{-2},\quad C=\mu^2\Omega^2.
\]

The 70-component causal BV parent, positive constrained Hamiltonian and
relative-charge ledger remain certified at this point.  There is no certified
causal transport away from it.

## Exact fixed-action stationary ideal

The imported action fixes

\[
\alpha_B=5,\qquad \alpha_R=0,\qquad
M_P^2=-\frac16,\qquad V_0=\frac{119}{1920},
\]

and the positive phase weights

\[
f_1^2=f_2^2=2,qquad F=4,qquad \mu^2=1.
\]

Using the exact Berger Bach and Einstein tensors, the three independent
orthonormal stationary rows have a lexicographic elimination basis

\[
1920C-12160q^2+16136q-4095,
\]

\[
160x-3200q^2+4280q-961,
\]

\[
\boxed{(q-1)(16q-5)(40q-9)}.
\]

The producer obtains this by exact Groebner reduction.  The independent rail
eliminates the two metric-row differences with resultants and obtains

\[
14622720000(q-1)^2(16q-5)(40q-9)
\]

and

\[
-39321600000x^4(x-1)(5x+2)(160x+119).
\]

Direct substitution leaves precisely three real algebraic stationary points:

| \(q\) | \(x\) | \(C\) | physical \(q,x,C>0\) | stationary Jacobian |
|---:|---:|---:|:---:|---:|
| \(9/40\) | \(1\) | \(9/16\) | yes | \(217/192\) |
| \(5/16\) | \(-2/5\) | \(1/8\) | no | \(-77/480\) |
| \(1\) | \(-119/160\) | \(119/1920\) | no | \(40579/184320\) |

All three points are simple.  Therefore the selected physical component is
zero-dimensional.  For example, the open ambient box

\[
\frac15<q<\frac14,qquad
\frac34<x<\frac54,qquad
\frac12<C<\frac58
\]

intersects the fixed-action stationary locus only at the selected point.  A
passing rational fixture was not extrapolated into an open phase.

The phase weights are not an undeclared coefficient family.  Keeping the
imported action fixes

\[
f_1^2+f_2^2=4,qquad f_1^2f_2^2=4.
\]

Their resultant is \(-(f_1^2-2)^2\), so positivity gives the unique imported
pair \(f_1^2=f_2^2=2\).

## Reduced inertia and characteristics

After the complete homogeneous lapse/Gauss reduction, the selected trace
block is

\[
L_2=\frac18\dot u^2-\frac{659}{1920}u^2.
\]

Thus the velocity Hessian is \(1/4>0\), the Hamiltonian is positive, and

\[
\lambda^2=-\frac{659}{240}.
\]

The two characteristic roots are simple and the Jordan type is \(1+1\).
This is the imported healthy reduced block, now placed inside the complete
stationary component classification.

## Charge and stabilizer strata

The compact charge matrix \((1,1)^T\) has rank one and leaves one physical
relative phase.  Diagonal charge vanishes by Gauss, while \(Q_{\rm rel}\) is
nonzero on the unrestricted stationary background.  On
\(\operatorname{span}\{D,R_{\rm rel}\}\), the moment map has rank one and
kernel

\[
K=D-\Omega R_{\rm rel}.
\]

Only on the explicitly fixed-\(Q_{\rm rel}\) leaf do \(D\) and
\(R_{\rm rel}\) become presymplectic-null.

For \(q=9/40\ne1\), the biaxial Berger spatial stabilizer is
\(SU(2)_L\times U(1)_R\), of dimension four.  Adding the helical generator
\(K\) gives a five-dimensional continuous global stabilizer.  No map to the
old fifteen-generator \(SO(4,2)\) receiver is certified.

## Why the same action does not reach the round cylinder

The selected stationary component is a singleton, so there is no continuous
stationary path toward \(q=1\).  The next algebraic stationary squashing in
that direction is \(q=5/16\), after the open gap

\[
\frac9{40}<q<\frac5{16},
\]

but it has \(x=-2/5\) and is not a positive spatial metric.  At \(q=1\), the
formal solution has \(x=-119/160\).  Equivalently, the direct round-cylinder
conditions for this action would require simultaneously

\[
C=2M_P^2=-\frac13,
\qquad
C=V_0=\frac{119}{1920},
\]

which is impossible.

This is distinct from the imported round boundary theorem.  On a separately
retuned positive-\(C\), \(\alpha_R=0\) round stationary locus, that theorem
already gives

\[
L_2=-\frac{3C}{8}\dot u^2-\frac{3C}{2}u^2,
\qquad \lambda=\pm2,
\]

so the round trace block is negative with real roots.  We import that datum
without rerunning it.  The present result says the selected action never
reaches the datum in the first place.

## Claim boundary

This is an exact `LOCAL-ALGEBRAIC` and `REDUCED-MODE` component theorem.  Its
statement that the selected point has a causal parent is a hash-pinned
`LORENTZIAN-CAUSAL` import.  It does not construct a causal parent elsewhere,
identify squashed modes with round-cylinder or \(SO(4,2)\) modes, or establish
nonlinear \(q_2\), an Einstein-source map, an observer, Hadamard data, a QME,
particles, scattering, positivity or unitarity.

## Evidence

- `d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_BACKGROUND_COMPONENT_ROUND_DISPOSITION_V1.json`
- `d_quotient_classical/compensator/TWO_PHASE_COUNTERFLOW_BACKGROUND_COMPONENT_ROUND_DISPOSITION_PAYLOAD_V1.json`
- `d_quotient_classical/compensator/verify_two_phase_counterflow_background_component_round_disposition.py`
- `residual_atlas/two-phase-counterflow-background-component-round-fragment-v1.json`

CLOSE-OUT: DONE — the complete stop condition is met
EVIDENCE: TWO_PHASE_COUNTERFLOW_BACKGROUND_COMPONENT_ROUND_DISPOSITION_V1_TIER_RECEIPT
