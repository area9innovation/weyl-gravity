# Exact all-\(\ell\) scalar threshold structure

Date: 2026-07-24  
Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

For each integer \(\ell\ge2\) and \(s\in\{1,2\}\), the exact
horizon-normalized static solution is

\[
\phi_{s\ell}^{(0)}
=
\frac{(2\ell)!}{2^{\ell+1}(\ell-s)!(\ell+s)!}
r^{\ell+1}\,
{}_2F_1\!\left(s-\ell,-s-\ell;-2\ell;\frac2r\right).
\]

The series terminates, has value one at \(r=2\), and grows as
\(C_{s\ell}r^{\ell+1}\) at infinity.  Its reduction-of-order partner can be
normalized to decay as \(r^{-\ell}\), but is logarithmically singular at the
horizon.  Neither scalar factor therefore has a zero-energy resonance for
any \(\ell\ge2\).

The associated low-frequency Jost and absorption coefficients are retained
as formal matched-asymptotic predictions.  They are not promoted to a
scattering theorem until a two-region Volterra remainder estimate is
certified.

## Verification

```bash
cd black_hole_programme/phase4/axial_all_ell_threshold_structure_v1
python3 produce.py
python3 verify.py
python3 -m unittest -v test_threshold.py
```

The independent verifier derives the monomial recurrence and checks separated
harmonics through \(\ell=11\).  Mutation tests reject normalization drift,
an incorrect \(\ell=2\) control, and premature Jost, outgoing-interval, or
all-\(\ell\) Bach-lift promotion.

CLOSE-OUT: DONE — exact all-\(\ell\) scalar threshold nonresonance is certified; uniform low-frequency scattering remains open.
EVIDENCE: `black_hole_programme/phase4/axial_all_ell_threshold_structure_v1/receipt.json`
