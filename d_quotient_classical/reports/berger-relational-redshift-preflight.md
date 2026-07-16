# Berger relational observable and redshift preflight

## Outcome

All prerequisites listed for the first Berger observer-level rail are now
present: the authoritative support-local `q2`, the all-row causal Green
homotopy, and the cyclic causal Cartan contraction through arity two.  This
certificate adds the smallest exact operational pilot.  Its generality is
`G0`, with dependency tags `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, and
`LORENTZIAN-CAUSAL`.

The rotating scalar pair supplies two Weyl-invariant objects,

\[
\theta=\operatorname{atan2}(T_2,T_1),\qquad
\widehat g=\rho^2g,\qquad \rho^2=T_1^2+T_2^2.
\]

The unit clock normal `n` and the simple Berger anisotropy eigenline `s` are
therefore tensorially defined.  The latter is unique because `q != 1` on the
certified interval.  A local complete observable is

\[
\mathcal O_A(\tau)=
 \exp\!\left({\tau-\theta\over\omega}\mathcal L_D\right)A,
\qquad -\pi<\tau-\theta<\pi.
\]

Its two `D` variations cancel because `D theta=omega`.  Beyond one phase
chart an integer winding label is required; no global single-valued claim is
made here.

## Exact operational fixture

For a co-propagating characteristic signal and an observer,

\[
k=E(n+s),\qquad u(v)=\gamma(v)(n+vs),
\]

the measured frequency and endpoint ratio are

\[
\nu(v)=E\gamma(v)(1-v),\qquad
1+z={\nu_e\over\nu_r}.
\]

At the rational Berger fixture, take `E=3/4`, `v_e=0`, `v_r=3/5`, and
initial physical separation `L=1/5`.  Exact arithmetic gives

- `gamma_r=5/4`;
- `nu_e=3/4` and `nu_r=3/8`;
- `1+z=2`, hence `z=1`;
- reception at `theta=3/8`, inside the first clock chart.

Thus quotienting total `D` does not algebraically force every operational
frequency comparison to be trivial.  This example is a receding-observer
kinematic redshift on the exact Berger background; it is not yet a
gravitational or cosmological redshift.

## Fail-closed boundary

The physical redshift theorem remains open.  The next construction must
spatially dress the emitter and receiver, solve an actual signal field on the
causal complex, compute the reduced endpoint brackets and induced pairing,
control winding/multiple-null-path domains, and then test higher transferred
brackets.  No interacting, phenomenological, quantum, or QME claim follows
from this preflight.

Machine-readable result:
`d_quotient_classical/certificates/BERGER_RELATIONAL_REDSHIFT_PREFLIGHT.json`.

## Verification

The generator guards, independent rational/provenance replay, unit and
mutation tests, and AJV Draft 2020-12 strict validation pass.  Tier 2 was not
rebuilt because all five scientific prerequisites are unchanged and
content-addressed; Tier 3 is not triggered by a `G0` preflight with no
lifecycle promotion or shared-core change.
