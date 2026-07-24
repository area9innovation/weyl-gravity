# Outgoing K-plus moving-phase gate

This package audits whether the rank-three outgoing reduced frame can be
promoted to one analytic endpoint \(\tau\)-frame with canonical
\(K_+=0\).

The exact phase-reduced spin-two pencil is

\[
\bar A(\omega,r)+\tau E(\omega,r).
\]

Differentiating its characteristic polynomial at the outgoing reduced
branch gives

\[
\dot q_+=-\frac34,\qquad \dot p_+=0,
\]

for the exponential rate and inverse-radius power. The spin-one block is
\(\tau\)-independent. Therefore the relative S-to-R phase normalizer at
\(r=31\) satisfies

\[
\partial_\tau\log h=\frac{93}{4}.
\]

The perturbation also has the irregular term
\((E_{\rm RW})_{12}=(3/4)r+O(1)\). The canonical polynomial eigenvector
gauge is \(B=\operatorname{diag}(3/4,0)\), satisfying
\(E_{-1}+[A_0,B]=0\). Combined with the scalar moving rate, the required
tangent correction at \(r=31\) is
\(\operatorname{diag}(0,93/4)Y\), not a scalar multiple of the whole
spin-two vector.

The rephasing is not \(\tau\)-independent. The formal recurrence still has
zero forced logarithms, unit leading amplitudes, and zero free Einstein
shear constants, but the existing fixed-phase checkpoints are not yet one
analytic moving-phase endpoint frame. Analytic \(K_+=0\) is consequently
withheld.

Run:

```bash
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_kplus_moving_phase_gate_v1.produce
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_kplus_moving_phase_gate_v1.produce --check
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_kplus_moving_phase_gate_v1.verify
python3 -m unittest black_hole_programme.phase3.axial_partial_jet_outgoing_kplus_moving_phase_gate_v1.test_moving_phase_gate
python3 -m black_hole_programme.phase3.axial_partial_jet_outgoing_kplus_moving_phase_gate_v1.audit
```
