# Berger clock Einstein-incidence theorem

The certified positive Berger clock is an exact Weyl--matter background, but
it is not an Einstein background, a conformally Einstein background, or an
Einstein solution with the same clock stress tensor.

In the orthonormal frame, with (q=c^2/a^2), the (00) Ricci component
vanishes while the spatial Ricci components do not.  Thus

\[
\operatorname{Ric}=\Lambda g
\]

would force \(\Lambda=0\) and then fail spatially.  The stronger
conformally-Einstein possibility is ruled out because every four-dimensional
conformally Einstein metric is Bach-flat, whereas

\[
B_{00}=\frac{(1-q)^2}{6a^4}>0
\]

throughout the certified interval.

For the same clock stress, (T_{ab}=\alpha_B B_{ab}), the trace of

\[
G_{ab}+\Lambda g_{ab}=\kappa T_{ab}
\]

fixes \(\Lambda=R/4\).  The remaining equation requires the trace-free Ricci
tensor \(S\) to be proportional to \(B\).  The exact component minor is

\[
S_{00}B_{11}-S_{11}B_{00}
=-\frac{q(1-q)}{8a^6}\neq0,
\]

so no constants \(\kappa,\Lambda\) solve the Einstein--clock equation on the
open interval.

Consequently, the complete retained Berger \(q_1\) is a Weyl--matter minimal
complex on a genuine non-Einstein branch.  A same-base-point linearized
Einstein--clock inclusion is not a meaningful next construction: the two
solution loci do not meet at this background.  One may still split
\(\alpha_B\delta B-\delta T\) to study an affine Einstein defect, or select a
different common background before comparing tangent complexes.

This is a `LOCAL-ALGEBRAIC`, `REDUCED-MODE` classification.  It establishes no
nonminimal, causal, nonlinear, scattering, or quantum result.

Machine certificate:
`bridge/certificates/berger_einstein_incidence.json`.

Verification:

```text
python3 -m bridge.einstein_sector.berger_einstein_incidence --verify bridge/certificates/berger_einstein_incidence.json
python3 bridge/einstein_sector/verify_berger_einstein_incidence.py
python3 -m unittest bridge.einstein_sector.tests.test_berger_einstein_incidence
```

## Receipt

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0 | Python compile and JSON parse | under 0.1 s | PASS |
| 1 | incidence generator/verifier | 1.14 s | PASS |
| 1 | independent exact consumer | 0.83 s | PASS |
| 1 | scoped unit tests | 1.44 s | PASS (5 tests) |

The complete retained Berger operator was not rebuilt: its unchanged
content-addressed certificate was consumed by hash.  The full classical and
quantum suites were not run because this result neither changes shared
classical algebra nor promotes a causal, nonlinear, quantum, freeze, or
release lifecycle state.

| Artifact | SHA-256 |
|---|---|
| generator | `3c16abc73b3371edd32151a467c4045d638e39433c7ddfeb467190b0a4ce7cf4` |
| schema | `54d6ea3ff2ba1c68689d77ccce1dc972161dc0faaa6d0d45acaf348399dbe9f5` |
| certificate | `6ab941dbf3312bcc991dc0de59be30853f876e4599414196a3ae21c967c863b4` |
| independent verifier | `fc2fd259564d137556f7912c72c89ed7a8bca7a14f19e9ee9d687f62f3ecd95e` |
| tests | `eb873e827f938d4390e58d729479e88cadf48d59b497e4da239f71f4da32bcba` |
| imported retained operator | `296bd46e4d94320a6a5b227167d722da1793d1f81891dcf2e494f9b631dcdd77` |
