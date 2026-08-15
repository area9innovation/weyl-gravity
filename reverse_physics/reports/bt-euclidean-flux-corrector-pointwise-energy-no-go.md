# BT flux-corrector pointwise-energy no-go

**Certificate:** `REVERSE_PHYSICS_BT_EUCLIDEAN_FLUX_CORRECTOR_POINTWISE_ENERGY_NO_GO_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

The weighted-current V2 reduction left two statistical subgates.  This result
decides one tempting route to the corrector subgate: no volume-independent
pointwise comparison with the action or the weighted Dirichlet energy can
supply the missing lowest-momentum factor.  The failure persists even if the
right-hand side is generously multiplied by the full volume $N$.

For every multiple of four $L$, place the V2 $4\times4$ exponent cell in
the four time rows $0,1,2,3$, repeat it along one spatial direction, and set
the exponent to zero in every other time row.  The field is constant in the
remaining two directions.  The first and last cell rows have $\Omega=1$, so
the exponent has exact zero seams and the action remains the replicated cell
action.  The residual potential is nonzero at the seam; the calculation
retains the resulting two boundary-current rows explicitly.  More importantly,
every time row sums to zero across a spatial period.  Thus the field has zero mean and is exactly
orthogonal to both phases of the lowest axial momentum: it lies in the actual
$E_p^\perp$ background slice.

Exact rational enumeration and replication give

\[
 A_L=\frac{837}{128}L^3,
 \qquad
 E_{\mathrm{dir},L}=\frac{290423}{1024}L^3.
\]

Writing $z=e^{2\pi i/L}$, the current and weighted-potential coefficients are

\[
 \widehat J_0(p_L)=\frac{L^3}{32}(-69+15z+42z^2+4z^3-4z^{-1}),
\]

\[
 \widehat u(p_L)=\frac{L^3}{64}(8+335z+216z^2+8z^3).
\]

The two seam terms are essential.  Combining the $z$ and $z^{-1}$ real parts
still bounds the real part of the first polynomial by $-12$, while the
triangle bound on the second polynomial is $567$.  Since

\[
 \widehat K_0=\widehat J_0-(1-e^{-2\pi i/L})\widehat u,
\]

the elementary bounds $\pi<22/7$ and $\sin x<x$ imply

\[
 |\widehat K_0(p_L)|
 \geq \frac38L^3-\frac{891}{16}L^2
 \geq \frac3{16}L^3
\]

for every multiple of four $L\geq300$.  With $N=L^4$ and
$\omega_p<1936/(49L^2)$, this yields the exact lower bounds

\[
 \frac{|\widehat K_0|^2}{N\omega_pA_L}
 \geq\frac{49}{360096}L,
 \qquad
 \frac{|\widehat K_0|^2}{N\omega_pE_{\mathrm{dir},L}}
 \geq\frac{9}{2868668}L.
\]

Both ratios diverge.  The same is true with $A_L+E_{\mathrm{dir},L}$ in the
denominator.

## Meaning of the obstruction

This is a method obstruction, not a Gibbs counterexample.  These slabs may be
rare under the exact background marginal, and their correlations may cancel
after averaging.  The desired estimate

\[
 \mathbb E_{\nu_p}|\widehat K_0(p_L)|^2
 \leq C_Kg^2N\omega_p
\]

therefore remains open.  What is now ruled out is proving it by forgetting the
Gibbs weight and bounding every background separately by the action or the
weighted flux energy.  A successful proof must retain probability,
correlation, or a cancellation that is invisible to pointwise energy control.

No current-susceptibility theorem, interacting $H^{-1}$ estimate, continuum
measure, Born rule, Krein reconstruction, or `LORENTZIAN-CAUSAL` result is
claimed.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_flux_corrector_pointwise_energy_no_go.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_flux_corrector_pointwise_energy_no_go.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_flux_corrector_pointwise_energy_no_go
```

## Verification receipt

- Tier 0 passed: the three Python files compile, the schema, certificate and
  planning event parse as JSON, and the scoped staged diff check is clean.
  Python ran under a 500 MB virtual-memory cap.
- The deterministic producer drift check passed in 0.04 s.
- The non-importing independent verifier passed in 0.09 s.  It separately
  enumerates the two active coordinates at $L=8$ and $L=12$, multiplies the
  inert sites, detects both seam-current rows, and checks the action and
  Dirichlet scaling exactly.
- Ten direct and adversarial mutation tests passed in 0.17 s.
- The planning import read 1632 nodes with zero invalid items and zero
  malformed events in 7.8 s.
- The 3.2 s advisory Science Forge shadow rail failed closed on the pre-existing
  Forge binary/stdlib mismatch (`E9118`) and reported corpus baseline drift
  (1741 certificates versus 976).  Its advisory wrapper exited zero; the bridge
  audit itself is recorded as failed, not passed.
- Tier 2 was not run because the V2 content-addressed input and its shared
  operators are unchanged; its hash is checked by both certificate rails.
- Tier 3 was not run because this is a method obstruction and working checkpoint,
  not a freeze, release, lifecycle promotion, or shared-core algebra change.
- Paper 21 integration was deferred from this commit because substantial
  concurrent foundations edits overlap every Paper 21 source and generated
  artifact.  Those edits were preserved and not taken over; the paper update
  remains the next integration step after their scoped commit.
