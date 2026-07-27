# Causal Laplace-to-resonance bridge

This package proves a scoped `LORENTZIAN-CAUSAL` result for the
gauge-invariant axial \(\ell=2\) spin-two sector.

The normally hyperbolic Einstein--Weyl parent family has retarded Green
operators \(G_m^{\rm ret}\).  Differentiation in the signed squared-mass
parameter gives

\[
G_{hh,{\rm W}}^{\rm ret}
=-\frac{1}{4\alpha_{\rm W}}
\left.\partial_mG_m^{\rm ret}\right|_{m=0}
=\frac{1}{4\alpha_{\rm W}}
G_0^{\rm ret}\mathcal A G_0^{\rm ret}.
\]

This sequential convolution is causal.  With the paper's
\(e^{+i\omega t}\) convention, its Laplace transform is initially defined
for \(\operatorname{Im}\omega<-c\), below the energy-growth bound, and
equals the outgoing radial resolvent.  The complete Jost and ECS theorems
uniquely continue that compactly cut-off transfer to the certified QNM
disk.  Its continuation has the nonzero rank-one double pole

\[
G_{-2}=-\frac{\omega_n'(0)}{4\alpha_{\rm W}}P_n.
\]

Thus the double pole is not merely an ECS eigenvalue: it is a resonance
pole of the meromorphic continuation of an actual retarded causal transfer
operator.

This does not justify shifting the full inverse-Laplace contour, control
the zero-frequency branch cut or high-frequency remainder, or prove a
global \(t e^{i\omega_n t}\) ringdown term.

Reproduce with:

```bash
python3 -m black_hole_programme.phase4.axial_qnm_causal_laplace_bridge_v1.produce
python3 -m black_hole_programme.phase4.axial_qnm_causal_laplace_bridge_v1.verify
python3 -m unittest -v \
  black_hole_programme.phase4.axial_qnm_causal_laplace_bridge_v1.test_causal_bridge
```
