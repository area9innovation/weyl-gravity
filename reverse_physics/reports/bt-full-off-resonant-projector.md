# BT full off-resonant projector composition

**Result:** `CLASSIFIED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

The exactly collinear Jordan calculation set the parent energy equal to the
sum of its two daughter energies before forming the carrier Gram.  This
successor retains

\[
 d=e_1+e_2-E_{\rm parent}
\]

throughout the quadratic map and restores the full daughter momentum measure
before taking a soft or collinear limit.

## Off-resonant map

For a product mode with time polynomial $P(t)$, the exact symplectic
extractor is

\[
 e^{-idt}\left[iP'(t)+(E_{\rm parent}+e_1+e_2)P(t)\right],
\]

while its d'Alembertian contains

\[
 P''-2i(e_1+e_2)P'
 +\left[E_{\rm parent}^2-(e_1+e_2)^2\right]P.
\]

After the repaired linear inverse map is applied, every explicit $t$ and
$t^2$ term cancels even for nonzero $d$.  Thus the hoped-for automatic
delta/delta-prime/delta-double-prime prescription does not arise from leftover
Jordan polynomials.

The off-resonant map is nevertheless strictly larger than its resonant slice.
For example,

\[
 (\delta b_\Omega)_{\Upsilon\Upsilon}
 =-\frac{d}{64e_1^3e_2^3},
\]

and the previously zero
$(\delta b_\Upsilon)_{\Omega\Omega}$ channel is also nonzero for $d\ne0$.
Setting $d=0$ recovers every entry of
`REVERSE_PHYSICS_BT_RT_JORDAN_KERNEL_V1` exactly.

## Full operator measure

Translation invariance makes the parent block of $K^\sharp K$ diagonal: the
two spatial momentum delta functions give
$\delta_3(P-P')$, leaving one daughter integral.  In the conventions of the
BT mode expansions,

\[
 d_3p_1=\frac{d^3p_1}{(2\pi)^3}
       =\frac{r^2dr\,d\Omega}{(2\pi)^3}.
\]

The symmetric quadratic map contributes one half of the ordered-slot Gram
after the two Bose contractions.  The two parent factors $1/(2E)$ change the
normalization but not the soft scaling.

On the exact soft blow-up chart

\[
 e_1=r,\qquad e_2=1,\qquad d=\alpha r,
\]

the off-diagonal Krein Gram has the universal leading term

\[
 G_{\Omega\Upsilon}=-\frac1{2r^3}+O(r^{-2}),
\]

independent of $\alpha$.  Physical soft rays obey
$\alpha=1-\cos\theta+O(r)$.  Restoring the radial measure therefore gives

\[
 r^2dr\,G_{\Omega\Upsilon}
 =-\frac12\frac{dr}{r}+O(dr).
\]

This is the central result.  The flat exactly-collinear slice had scaling
degree three and three endpoint jets.  On the declared full three-dimensional
soft chart, the ordinary parent composition is logarithmically non-trace-class
and has one local soft normalization.  The ambiguity is smaller, but it is
not gone.

Indeed, for a common sharp energy cutoff,

\[
 I_\epsilon=\int_\epsilon^{r_0}-\frac12\frac{dr}{r},
 \qquad
 I_{c\epsilon}-I_\epsilon=\frac12\log c.
\]

Thus changing the common resolution scale shifts the finite part.  Neither
the full off-resonant map nor the restored measure selects the desired
$1/48$.  This is not evidence against a renormalized BT construction: it is
the exact point at which a soft-collinear asymptotic Hamiltonian or equivalent
factorization/matching operator becomes necessary.

## Next gate and boundary

The next calculation must construct anti-Krein asymptotic evolution on this
off-resonant carrier and show that its cutoff response cancels the hard-factor
response independently of regulator family.  Only then can its Born-normalized
coefficient be compared with $1/48$.

This certificate does not establish that all three flat-slice constants vanish
globally, that no renormalized asymptotic dynamics exists, a complete NLO
probability, beyond-tree positivity, a gravitational lift, or anything
`LORENTZIAN-CAUSAL`.

Verification commands:

```text
ulimit -v 500000; python3 reverse_physics/bt_full_off_resonant_projector.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_full_off_resonant_projector.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_full_off_resonant_projector
```

Primary source: [Bateman--Turok](https://arxiv.org/abs/2607.00096), Eq. (16),
Eq. (19), and Appendix C.

## Verification receipt

All commands ran sequentially on 2026-08-10 under `ulimit -v 500000`.

| Tier | Command | Result | Elapsed | Max RSS |
|---|---|---:|---:|---:|
| 0 | `python3 -m py_compile reverse_physics/bt_full_off_resonant_projector.py reverse_physics/verify_bt_full_off_resonant_projector.py reverse_physics/tests/test_bt_full_off_resonant_projector.py` | PASS | 0.04 s | 16,840 KiB |
| 1 | `python3 reverse_physics/bt_full_off_resonant_projector.py --check` | PASS, 15/15 | 0.06 s | 21,332 KiB |
| 1 | `python3 reverse_physics/verify_bt_full_off_resonant_projector.py` | PASS, 6/6 | 0.18 s | 30,848 KiB |
| 1 | `python3 -m unittest -v reverse_physics.tests.test_bt_full_off_resonant_projector` | PASS, 5/5 including three decisive mutations | 1.25 s | 30,788 KiB |
| 0 | two `pdflatex -interaction=nonstopmode -halt-on-error 05-interaction-obstructions.tex` passes | PASS | 0.48 s, 0.50 s | 50,776 KiB, 50,928 KiB |
| 0 | two `pdflatex -interaction=nonstopmode -halt-on-error 06-einstein-weyl-interaction-obstructions.tex` passes | PASS | 0.53 s, 0.54 s | 50,616 KiB, 50,696 KiB |

The Paper V build retains its three pre-existing small overfull boxes; the new
text introduced no LaTeX error.  Paper VI has no overfull box.  Tier 2 was not
run because the three imported certificates are unchanged and pinned by their
SHA-256 hashes; their transitive chains therefore have no changed mathematical
input.  Tier 3 was not run because this obstruction is neither a freeze/tag nor
a theorem promotion or shared-core algebra change.  The advisory Science Forge
shadow rail was not promoted to a pass: its immediately preceding run on the
same unchanged inputs failed under the mandatory memory cap, and this scoped
package does not claim otherwise.  All three planning records pass
`python3 -m json.tool`.  A full `s-f import-program` is likewise not reported
as a pass: the launcher could not rebuild its changed source, and the cached Go
binary then failed immediately while reserving runtime page-summary memory
under the 500 MB cap.  The cap was not relaxed.  Because the package creates
new files, the documented manual explicit-path commit fallback applies; no
pre-commit `s-f work check` report is claimed.
