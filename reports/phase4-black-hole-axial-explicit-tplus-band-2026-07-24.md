# Phase-4 explicit \(T_+\) band — active checkpoint

Dependency tags: `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

## Result

The experiment resumed the certified common-moving \(R/S\) outgoing
partial-jet checkpoint at \(r=979/32\). A bounded order-120 panel of width
\(5/32\) reached \(r=487/16\).

The accepted boundary satisfies:

- common frequency generator: `7315`;
- validated exponential pre-tail:
  `4.4421679558528834e-05`;
- joint base/tangent hull width: `5.12490045532877`;
- exact equality of retained partial-jet and direct sixteen-state Taylor
  coefficients;
- interval containment of the independent boundary comparison;
- content-addressed successor payload:
  `b1240852cb5f60848ab7d6fb6a165f394bafb803472003fada34f6816373c04a`.

This closes the specific Phase-3 runtime refusal: the order-120 fallback that
was never reached after the larger-panel timeout is admissible when executed
directly.

## Remaining gate

The frame is still at \(r=487/16\), not \(r=4\). The current serial
high-order-panel architecture is therefore not an efficient route to the
complete connection. The next implementation should retain the same
dual-number endpoint gauge but move the radial transport to a projective
line plus logarithmic-amplitude/Lohner representation, with a direct
sixteen-state comparison only at coarse checkpoints.

No \(T_+\), reflection amplitude, Stokes identity, or frequency-band theorem
is claimed by this checkpoint.

## Verification

```text
python3 -m black_hole_programme.phase4.axial_explicit_tplus_band_v1.produce --check
python3 -m black_hole_programme.phase4.axial_explicit_tplus_band_v1.verify
python3 -m unittest -v black_hole_programme.phase4.axial_explicit_tplus_band_v1.test_checkpoint
```

The independent verifier and three tests passed. Tier 2 and Tier 3 were not
run because the common frame has not reached the matching section and no
paper theorem is promoted.

CLOSE-OUT: ACTIVE CHECKPOINT — one correlated successor is certified; explicit \(T_+\) remains open at the radial transport gate.
EVIDENCE: black_hole_programme/phase4/axial_explicit_tplus_band_v1/receipt.json
