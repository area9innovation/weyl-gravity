# Axial partial-jet transport preflight v1

This is the smallest bounded successor to the exact local partial-jet
crosswalk. It uses the existing `IvTaylor4` shared-frequency arithmetic
tensored with an explicit dual-\(\tau\) matrix layer.

The attempt covers only q00 child 0 and shell 0, panel 0. The radial interval
is placed in the outward remainder while \(\omega\) retains one shared quartic
generator. A 12-term local transition is computed in two ways:

1. transport the real \(8\times8\) base/tangent pair in the dual algebra and
   expand it into the real \(12\times12\) six-state order;
2. transport the direct real \(12\times12\) six-state connection imported
   from the exact crosswalk.

The attempt refuses before the final comparison.  It expands the unfactored
\(\omega\)-dependent Frobenius phase, whose frequency derivatives carry
powers of \(\log(r-2)\).  The shell-0 panel consequently gives
\(h\|A\|_\infty\approx 4.9161\times10^4\), outside the certified analytic-tail
regime.  The next rail must keep the moving phase symbolic and transport the
reduced Frobenius amplitude.

This is a bounded method shortfall, not a singularity or instability result.
It does not certify the microfactor, the q00 child, H4, endpoint frames,
\(T_+\), or scattering.

Run:

```bash
python3 -m black_hole_programme.phase3.axial_partial_jet_transport_preflight_v1.produce
python3 -m black_hole_programme.phase3.axial_partial_jet_transport_preflight_v1.verify
python3 -m unittest black_hole_programme.phase3.axial_partial_jet_transport_preflight_v1.test_preflight
```
