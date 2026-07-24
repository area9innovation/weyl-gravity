# Axial QNM infinity-tail gate

Status: `EXACT — CLASSIFIED — NEGATIVE TAIL GATE`.

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

This package attacks the next fail-closed infinity endpoint gate on the
closed radius-\(0.025\) QNM seed disk.  It proves that the obvious forward
interval enclosure of the formal inverse-\(r\) recurrence cannot furnish an
all-order geometric tail at the practical outer radius \(R=45\).

For scaled terms \(t_m=g_m/R^m\), the direct recurrence gain is

\[
\alpha_m=-\frac{p_m}{2i\omega(m+1)R},
\qquad
p_m=m^2+m-6-4im\omega+8\omega^2.
\]

An exact disk bound proves

\[
\lvert\alpha_m\rvert>1
\qquad(m\ge49)
\]

uniformly on the complete disk.  This is a representation-level
noncontractivity result.  It does not assert that every particular formal
coefficient orbit diverges, and it supplies no endpoint remainder.

The package specifies an exterior-complex-scaling replacement.  On

\[
r_*=x_0+e^{i\pi/4}t,\qquad t\ge0,
\]

the oscillatory Volterra factor is uniformly damped throughout the disk.
The inverse-tortoise branch and potential-integral contraction remain
explicit fail-closed gates.

## Reproduction

```bash
python3 -m black_hole_programme.phase3.axial_qnm_infinity_tail_gate_v1.produce
python3 -m black_hole_programme.phase3.axial_qnm_infinity_tail_gate_v1.verify
python3 -m unittest -v black_hole_programme.phase3.axial_qnm_infinity_tail_gate_v1.test_infinity_tail_gate
python3 -m py_compile \
  black_hole_programme/phase3/axial_qnm_infinity_tail_gate_v1/produce.py \
  black_hole_programme/phase3/axial_qnm_infinity_tail_gate_v1/verify.py \
  black_hole_programme/phase3/axial_qnm_infinity_tail_gate_v1/test_infinity_tail_gate.py
```
