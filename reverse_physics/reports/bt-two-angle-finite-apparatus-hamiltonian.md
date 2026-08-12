# Finite apparatus Hamiltonian for the two-angle BT detector

Certificate:
`REVERSE_PHYSICS_BT_TWO_ANGLE_FINITE_APPARATUS_HAMILTONIAN_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`.

Lifecycle: `COEFFICIENT_COMPUTED`.

## Result

The positive two-angle effect is no longer only an operationally declared
matrix.  It is the measured effect of an explicit bounded finite apparatus
Hamiltonian.

Let the two orthogonal equal-energy BT output modes be (|c_1angle) and
(|c_2angle).  For an apparatus phase (phi), define

\[
 |+_\phi\rangle={|c_1\rangle+e^{i\phi}|c_2\rangle\over\sqrt2},
 \qquad
 |-_\phi\rangle={|c_1\rangle-e^{i\phi}|c_2\rangle\over\sqrt2},
\]

with projections (P_\pm(\phi)).  Couple the antisymmetric mode to a
degenerate pointer qubit by

\[
 \boxed{H_{\rm int}=gP_-(\phi)\otimes\sigma_y.}
\]

This is a four-dimensional bounded self-adjoint Hamiltonian with norm
(|g|).  The equal energy of the two fixed-(s) angle modes and the
degeneracy of the pointer imply that it commutes with the reduced free
Hamiltonian.  It is therefore an energy-conserving finite interaction on the
declared carrier.

Because (P_-) is a projector,

\[
 (H_{\rm int}/g)^2=P_-(\phi)\otimes I_A,
\]

and its exponential for (	heta=g\tau) is exact:

\[
 U_\tau=P_+(\phi)\otimes I_A
 +P_-(\phi)\otimes
 [\cos\theta I_A-i\sin\theta\sigma_y].
\]

No uncomputed exponential or limiting argument remains.

## Pointer instrument

Prepare the pointer in (|0\rangle_A), evolve for time (	au), and read it
in the basis (|0\rangle_A,|1\rangle_A).  Calling pointer zero the coherent
click gives

\[
 K_{\rm click}=P_+(\phi)+\cos\theta P_-(\phi),
 \qquad
 K_{\rm no}=\sin\theta P_-(\phi).
\]

Consequently

\[
 E_{\rm click}=K_{\rm click}^\dagger K_{\rm click}
 =P_+(\phi)+\cos^2\theta P_-(\phi),
\]

\[
 E_{\rm no}=K_{\rm no}^\dagger K_{\rm no}
 =\sin^2\theta P_-(\phi),
\]

and

\[
 E_{\rm click}+E_{\rm no}=I.
\]

Thus the earlier detector parameter is selected by a physical control:

\[
 \boxed{\epsilon=\sin^2(g\tau).}
\]

At (	heta=0) every mode clicks.  At (	heta=pi/2), the antisymmetric
mode is routed completely to the no-click pointer state and the click effect
is the pure coherent projection (P_+(\phi)).

## How the apparatus selects the phase

Let

\[
 S_\phi=\operatorname{diag}(1,e^{i\phi}).
\]

Then

\[
 P_-(\phi)=S_\phi P_-(0)S_\phi^\dagger.
\]

The relative phase is therefore an ordinary interferometer setting: a phase
shifter conjugates the zero-phase antisymmetric coupling.  It is selected by
the apparatus and is not predicted by BT scattering dynamics.

Suppose the leading BT vector has relative phase (delta),

\[
 X_2=x_2(1,e^{i\delta})^T.
\]

At the calibrated setting (phi=delta), (X_2) lies entirely in the
symmetric mode and

\[
 E_{\rm click}X_2=X_2.
\]

For a mismatch (Delta=delta-phi), the exact response is instead

\[
 \boxed{
 \langle X_2,E_{\rm click}X_2\rangle
 =2|x_2|^2[1-\epsilon\sin^2(\Delta/2)].}
\]

The phase setting is therefore operationally falsifiable rather than a
basis convention hidden in the calculation.

## Transfer of the BT coefficients

At phase calibration the Hamiltonian-derived effect is exactly the effect of
the two predecessors.  Hence the complete probability through order
(lambda^6) is

\[
 q_{\rm click}=2q_4\left[1+\lambda^2
 {R_6(c_1)+R_6(c_2)\over2}\right]+O(\lambda^8).
\]

The complete relative order-eight coefficient is

\[
 q_8[\text{apparatus}]-q_8[\text{recorded}]
 =-{\epsilon\over2}
 \left\|X_4(c_1)-e^{-i\phi}X_4(c_2)\right\|^2.
\]

Neither absolute (q_8) coefficient is computed.

## Exact fixture

Choose

\[
 e^{i\phi}=i,\qquad \cos\theta={3\over5},\qquad
 \sin\theta={4\over5},\qquad \epsilon={16\over25}.
\]

All entries of (H_{\rm int}/g), (U_\tau), the Kraus maps and both effects
then lie in (mathbb Q(i)).  Direct exact multiplication verifies
(U_\tau^\dagger U_\tau=I_4) and Kraus completeness.  A calibrated unit
leading amplitude has click probability (2); a quarter-turn phase mismatch
has probability (34/25).  For

\[
 X_4=(1+2i,-3+i),
\]

the relative (q_8) shift is (-8/25).

## What is physical, and what is not

Established:

- an explicit finite self-adjoint Hamiltonian coupled to the certified BT
  output modes;
- an exact unitary time evolution and normalized two-outcome pointer
  instrument;
- dynamical selection (epsilon=sin^2(g\tau)) by coupling-duration;
- interferometric selection of the relative phase (phi);
- an exact phase-mismatch response; and
- physical finite-device realization of the complete q6 and relative-q8
  detector formulas.

The device is additional physical structure.  The public closed-system BT
Hamiltonian does not contain or predict its coupling (g), duration (	au)
or phase setting.  The construction assumes coherent access to two declared
finite-box modes and permits the apparatus to absorb their momentum
difference.  It is not a translation-invariant or spacetime-local detector
model.

It establishes no continuum-angle limit, absolute q8 coefficient, forward
endpoint, real--virtual/KLN completion, all-time scattering operator,
general Eq. (19), gravity or metric BV--BRST transfer, restored QME, residual
transfer, anything `LORENTZIAN-CAUSAL`, or literature priority.

## Independent rail

The producer uses exact quotient-ring algebra for the apparatus phase and
trigonometric circle relations and contracts the full four-dimensional
unitary symbolically.  The independent verifier uses only exact `Fraction`
pairs for complex numbers.  It reconstructs the Hamiltonian, unitary, Kraus
maps and effects over four unit-circle phases, four Pythagorean interaction
settings, all phase mismatches in that grid and a separating family of
complex q8 amplitudes.  It also rechecks every input hash and claim boundary.

## Verification receipt

All scientific processes ran sequentially under `ulimit -v 500000`.

- Python parse/compile: PASS, 0.04 s, 15,440 KB peak RSS.
- Exact quotient-ring/Hamiltonian producer: PASS 34/34, 0.82 s,
  70,992 KB peak RSS.
- Independent `Fraction` complex-matrix verifier: PASS 34/34, 0.09 s,
  24,528 KB peak RSS.
- Scoped tests: PASS 31/31 in 0.193 s (0.26 s enclosing wall time),
  24,992 KB peak RSS.  These contain 30 adversarial mutations.  A pre-final
  mutation run exposed a stored phase-projector field not independently
  compared by the verifier; that comparison was added before this final
  passing receipt.
- Papers V and VI: PASS, two `pdflatex -halt-on-error` passes each under the
  same cap.  The final passes took 0.49 s and 0.50 s, both at 51,016 KB peak
  RSS.  The PDFs have 62 pages (670,214 bytes) and 57 pages (650,801 bytes),
  respectively.  No new overfull box occurs at the inserted
  theorem; the logged overfull boxes predate these locations.
- Tier 3: FAIL-CLOSED, 2,348 tests in 789.608 s, with 32 failures and 9
  skips; the enclosing timed process took 790.63 s and peaked at 391,596 KB.
  Every new apparatus test passed.  The failures are older content-addressed
  producer/verifier rails plus the capped chain-import scan; the latter
  explicitly reported that its scan did not run and is not a pass.
- The advisory Science Forge shadow rail was bounded by a 30 s timeout.  Its
  external `cbp` shim aborted two helper calls and then stalled; timeout
  exited 124 at 30.01 s with 59,924 KB peak RSS.  No bridge-audit or coverage
  result is claimed from this invocation.

Tier 3 was required because Papers V and VI promote the detector from a
declared effect to an explicit finite Hamiltonian device.  Its unrelated
older failures remain failures and do not alter the independently passing
scoped chain.

Commands:

    ulimit -v 500000; python3 reverse_physics/bt_two_angle_finite_apparatus_hamiltonian.py --check
    ulimit -v 500000; python3 reverse_physics/verify_bt_two_angle_finite_apparatus_hamiltonian.py
    ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_two_angle_finite_apparatus_hamiltonian
