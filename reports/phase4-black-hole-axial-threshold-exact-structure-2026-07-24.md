# Phase-4 axial threshold exact structure

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

The exact threshold package verifies:

- \(\phi_{0,2}=r^3/8\) and
  \(\phi_{0,1}=r^2(2r-3)/4\) solve their zero-frequency
  Regge--Wheeler equations and equal one at the horizon;
- the displayed reduction-of-order companions solve the same equations,
  decay as \(r^{-2}\), and are logarithmically singular at the horizon;
- neither scalar factor has a bounded zero-energy resonance;
- the reduced projective cocycle decomposes exactly as
  \[
  \mathcal I_{\rm red}
  =\frac{2i}{5\omega}(V_1-V_2)
   +\frac{i\omega(r-2)(2r+3)}{5r^4};
  \]
- the leading source on the spin-two zero mode has the elementary primitive
  \[
  (D^2-V_2)
  \left(-\frac{r^2}{4}-\frac r4-\frac13-\frac1{2r}\right)
  =\frac{r-2}{r}.
  \]

## Claim boundary

This result does not establish the two-region Volterra remainder needed to
turn formal low-frequency matching into a punctured positive-real
\(T_+\)-invertibility theorem. It also does not certify the proposed
\(b/a^2=O(\omega^2)\) extension-ratio bound.

## Verification

Commands:

```text
python3 -m black_hole_programme.phase4.axial_threshold_exact_structure_v1.produce
python3 -m black_hole_programme.phase4.axial_threshold_exact_structure_v1.verify
python3 -m unittest -v black_hole_programme.phase4.axial_threshold_exact_structure_v1.test_threshold
```

All seven exact residuals vanished. The independent verifier passed. Four
tests passed, including mutations of a zero mode, the cocycle decomposition,
and the fail-closed scattering ledger.

Tier 2 was not run because this package adds an exact reduced-mode result and
does not modify any shared operator or pre-existing certificate chain.
Tier 3 was not run because this is neither a freeze nor a release.

CLOSE-OUT: DONE — exact threshold identities and nonresonance certified; low-frequency scattering matching remains a separately gated successor.
EVIDENCE: black_hole_programme/phase4/axial_threshold_exact_structure_v1/receipt.json
