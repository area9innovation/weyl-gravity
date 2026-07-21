# Cylinder derived BFV/Koszul time-slice carrier

Result: `CYLINDER_DERIVED_BFV_KOSZUL_TIME_SLICE_CARRIER_V1`

## Result

The predecessor correctly ruled out replacing the common Taub-zero fibre by
a unary subspace deletion.  Its stronger “carrier missing” diagnosis can now
be sharpened using already frozen residual data.

On the selected D-finite Einstein-cylinder model, the intrinsic derived
carrier exists.  It is

\[
\left[
\mathcal P_{\rm lin}\mathop{\times}^{\mathbf R}_{\mathfrak{so}(4,2)^*}
\{0\}\,/^{\mathbf R}SO(4,2)
\right],
\]

represented by 15 residual ghosts \(c^A\), 15 ghost momenta \(b_A\), and the
selected E/A/L matter phase space.  The ghost momenta are precisely the
Koszul generators:

\[
\eta_A=b_A,
\qquad
d_K\eta_A=\mu_A
\]

on the ghost-free slice.  The full BFV charge is

\[
\Omega_{\rm res}
=c^A\mu_A-\frac12 f^A{}_{BC}c^Bc^C b_A.
\]

The imported exact cubic master-equation check has zero Jacobi,
representation, and moment-map-equivariance defects.  The endpoint map is
suspended into the BFV ghost momenta with the unique normalization
\(\lambda=1\) for all 15 generators.  Raw \(D\) preserves the intrinsic
derived carrier and is gauge there, while remaining charged on the unreduced
linear phase space.

## Exact remaining obstruction

This does not yet define a chain map from arbitrary-support local BV anomaly
cocycles to the time slice.  The strongest local lift currently certifies
only two mode-specialized metric seeds and explicitly records:

- full support-local \(q_2\): `NOT_COMPUTED`;
- local \(q_1q_2\) chain identity: `NOT_COMPUTED`;
- Diff/Weyl ghost completion: `NOT_COMPUTED`;
- antifield completion: `NOT_COMPUTED`;
- portable local \(q_1,\pi_{\rm cl},\iota_{\rm cl},s_{\rm cl}\): absent.

Therefore the intrinsic residual carrier and algebraic endpoint suspension
are certified, but support compatibility and representative independence for
the full local-to-time-slice map are not.  No anomaly image or raw-\(D\)
Cartan defect can be assigned.

## First perturbative orders

Counting metric fluctuations while retaining the Weyl ghost:

| representative | first metric order | reason |
|---|---:|---|
| \(\omega C^2\) | 2 | \(C(\bar g)=0\) |
| \(\omega E_4\) | 1 | \(\delta E_4=d\Theta_E\), with the certified \(d\omega\wedge\Theta_E\) residual |
| \(\omega C\widetilde C\) | 2 | both background Weyl factors vanish |

These are local Taylor orders, not receiver maps or cohomology verdicts.

## Quantum receiver contract

Quantum may import the intrinsic 15-generator BFV charge, the identification
\(\eta_A=b_A\), the normalized endpoint suspension, finite-window
nilpotency, raw-\(D\) preservation, and the three Taylor orders.  It must not
rerun anomaly restriction until a support-local arbitrary-input \(q_2\), its
ghost/antifield completion, portable local contraction, and the arity-two
chain square are supplied.

This is `LOCAL-ALGEBRAIC` / `REDUCED-MODE`.  It establishes no QME,
Lorentzian-causal, Hadamard, observable, particle, positivity, scattering or
unitarity statement.
