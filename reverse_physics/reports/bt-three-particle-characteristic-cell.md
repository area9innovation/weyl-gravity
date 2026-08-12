# BT three-particle characteristic cell

Certificate:
`REVERSE_PHYSICS_BT_THREE_PARTICLE_CHARACTERISTIC_CELL_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle:
`COEFFICIENT_COMPUTED`.

## Result

The missing dimension-two factor in the finite-time six-point shell can be
computed once an incoming three-particle detector cell is declared.  For the
finite-volume point cell below, the resulting local shell probability is
dimensionless and has an exact positive rate.  The rate is detector-dependent;
it is not a universal three-body cross section or flux.

## Public two-beam mechanism

Bateman--Turok use

\[
 d_np=\frac{d^np}{(2\pi)^n},\qquad
 \delta_n(p)=(2\pi)^n\delta^n(p),\qquad
 \chi(x)=\frac{\delta_1(x)}{L},
\]

where \(L=\delta_1(0)\), with the last expression understood as a
finite-volume point characteristic.  Their two-beam characteristic has
denominator

\[
 L_0L_x^2L_y^2L_z.
\]

The squared total-momentum delta contributes
\(\delta_4(0)=L_0L_xL_yL_z\).  The quotient is therefore

\[
 \frac{1}{L_xL_y}=\frac{1}{\mathrm{Area}},
\]

which reconstructs the normalization mechanism in Appendix B.  The Area is
not an additional axiom: it is the remainder of the chosen two-beam
characteristic.

## Declared three-beam cell

Introduce a positive momentum scale \(\kappa\).  The certified incoming
fixture is

\[
 \bar p_0=\kappa(6/5,6/5,0,0),
\]

\[
 \bar p_1=\kappa(1,-3/5,4/5,0),\qquad
 \bar p_2=\kappa(1,-3/5,-4/5,0).
\]

All three momenta are future null and their total spatial momentum vanishes.
Fix eight spatial components other than \(p_{0x}\) at these values, and replace
the ninth spatial constraint by

\[
 E_0+E_1+E_2=\frac{16\kappa}{5}.
\]

For one ordered cell the finite-volume denominator is

\[
 L_0L_x^2L_y^3L_z^3.
\]

On the positive mass shells, the nine-by-nine constraint Jacobian has
absolute determinant

\[
 \left|\frac{\partial(E_0+E_1+E_2,
        p_{0y},p_{0z},p_{1x},\ldots,p_{2z})}
       {\partial(p_{0x},p_{0y},p_{0z},p_{1x},\ldots,p_{2z})}
 \right|=\left|\frac{p_{0x}}{E_0}\right|=1.
\]

Because \(E_0E_1E_2=6\kappa^3/5\), the ordinary on-shell input measure of
one ordered point cell is

\[
 I_{\rm ord}=
 \frac{5}{48\kappa^3L_0L_x^2L_y^3L_z^3}.
\]

The factors of \(2\pi\) cancel exactly: nine normalized deltas cancel the
nine factors in the three spatial momentum measures.  Multiplication by the
external spacetime volume gives

\[
 N_{\rm in}=\delta_4(0)I_{\rm ord}
 =\frac{5}{48\kappa^3L_xL_y^2L_z^2}.
\]

This has mass dimension \(+2\), exactly the dimension missing from the
coupling-normalized shell coefficient.

The use of the ordinary on-shell input measure here follows from the existing
six-mass certificate.  The squared six-point amplitude starts at total
external-mass degree six, so in the six delta-prime representation every mass
derivative contributing to the leading coefficient acts on the amplitude.
Any term in which a derivative acts on the smooth phase or characteristic
weight has too few derivatives to reach degree six and vanishes at zero mass.

## The two \(3!\) factors

The generalized Born trace contains

\[
 \frac{1}{3!\,3!}.
\]

An identical-particle incoming characteristic cannot select just one labeled
ordering.  It is the sum of the six disjoint \(S_3\) images of the cell above.
Likewise, a physical local outgoing cell is the union of the six labelings of
one unordered momentum triple.  The fixture momenta are distinct, so both
orbits have six disjoint elements.  Therefore

\[
 \frac{6_{\rm in}\,6_{\rm out}}{3!\,3!}=1.
\]

This is why the labeled shell coefficient is used once.  Dividing it by an
isolated \(3!\), as in an ordinary labeled-phase-space preflight, would not be
the generalized-Born trace.

## Dimensionless detector probability

After restoring the BT tree factor, the certified labeled shell probability
per unit dimensionless tangential chart volume is

\[
 \frac{27\lambda^8T}{320\pi^4\kappa}.
\]

Multiplication by \(N_{\rm in}\) gives the local rate density

\[
 \boxed{
 \Gamma_\Xi=
 \frac{9\lambda^8}
 {1024\pi^4\kappa^4L_xL_y^2L_z^2}}
\]

and hence, for a symmetric compact tangential cell of dimensionless chart
volume \(\Delta\Xi\),

\[
 q_\Xi(T)=\Gamma_\Xi T\,\Delta\Xi+O(1).
\]

The rate has mass dimension one and \(q_\Xi\) is dimensionless.  In the
leading perturbative domain \(0\le q_\Xi\le1\), the previously certified
finite-time column supplies the complementary survival probability
\(1-q_\Xi\).

The transverse detector may be compact.  For a window \(|s|<S\), the exact
finite-time shell norm is

\[
 \int_{-S}^{S}|\alpha_{T,\kappa}(s)|^2ds
 =\frac{2T}{\kappa}\operatorname{Si}
   \!\left(\frac{ST}{2\kappa}\right)
  -\frac{8}{S}\sin^2\!\left(\frac{ST}{4\kappa}\right).
\]

Dividing by \(T\) and taking the long-time limit gives \(\pi/\kappa\), so
every fixed compact shell window containing the pole has the same leading
rate.  Smooth connected interference remains order one and is not part of the
displayed coefficient.

## Why the result is detector-dependent

The public rules do not choose this cell.  For example, keep the same box and
replace \(p_{1x}\), rather than \(p_{0x}\), by the total-energy constraint.
The absolute Jacobian becomes

\[
 |p_{1x}/E_1|=3/5,
\]

so the normalized point-cell weight changes by \(5/3\).  Both finite-volume
orbit sums are idempotent, but they describe different resolution cells.
Thus idempotence does not select a coordinate-independent three-particle
normalization.  The characteristic function, box geometry, and cell
coordinates are experimental data.

This result therefore closes the normalization for the declared detector.  It
does not define a universal \(3\to3\) cross section, glue the ten shell
channels, compute their complete order-one interference, construct a global
Møller/LSZ/S operator, prove Eq. (19), or transfer anything to gravity or a
`LORENTZIAN-CAUSAL` theory.

## Next gate

Replace the finite-volume point characteristic by a compact normalized
three-particle wave packet and prove convergence of its generalized-Born
trace to this rate.  Then construct a positive detector partition that glues
the ten finite-time shell tubes, including their intersections.  Eq. (19)
remains a separate route requiring the deferred continuum pushforward,
ghost-parity, stationarity, and trace-domain proof.

## Verification receipt

- Tier 0: the new Python and JSON files parse and the scoped diff is checked.
- Tier 1: the producer passes 27/27 exact checks, the method-distinct
  fraction-only verifier passes 26/26 checks, and seven mutation tests pass.
  Peak resident memory is below 67 MB for the producer and below 25 MB for the
  verifier and tests.
- Tier 2: the three-certificate chain from the finite-time shell through this
  detector cell passes sequentially.  Its producers report 23/23, 19/19 and
  27/27 checks; its independent verifiers report 27/27, 21/21 and 26/26
  checks.  The combined 19-test chain passes in 0.74 seconds with peak resident
  memory 75,184 KB.  Every producer and verifier remains below 75 MB.
- Tier 3 is not required because no shared core algebra, freeze, release, QME
  lifecycle, or Lorentzian claim changes.
- The Science Forge conformance rail reports `CLEAN`, including the new work
  item and append-only `DONE` event.  The Go coordinator was run separately
  with one thread and `GOMEMLIMIT=300MiB` because its virtual-address arena
  cannot start under the scientific 500 MB `ulimit`; peak resident memory was
  295,812 KB.  All scientific Python and TeX rails retained the hard cap.

Commands:

```text
ulimit -v 500000; python3 reverse_physics/bt_three_particle_characteristic_cell.py --write --check
ulimit -v 500000; python3 reverse_physics/verify_bt_three_particle_characteristic_cell.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_three_particle_characteristic_cell
```

CLOSE-OUT: DONE -- a declared symmetric three-particle finite-volume
characteristic cell turns the certified shell coefficient into a dimensionless
local detector probability rate; detector independence and global channel
gluing remain open.

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_THREE_PARTICLE_CHARACTERISTIC_CELL_V1.json`
