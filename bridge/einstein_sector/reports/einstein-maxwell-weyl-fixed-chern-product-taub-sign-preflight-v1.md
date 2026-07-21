# Fixed-Chern product Taub-sign structural preflight

Result: `EINSTEIN_MAXWELL_WEYL_FIXED_CHERN_PRODUCT_TAUB_SIGN_PREFLIGHT_V1`

## Exact result

For the pure-magnetic common Einstein--Maxwell/pure-Weyl--Maxwell product

\[
M_2(k_1)\times S^2(k_2),
\]

fix a magnetic bundle with Chern number \(N\ne0\) and minimum charge
\(q_{\min}>0\).  Flux quantization gives

\[
P=\frac{Nk_2}{2q_{\min}}.
\]

Combining this with the certified product incidence gives

\[
k_1=k_2-\beta k_2^2,
\qquad
\beta=\frac{\kappa N^2}{4q_{\min}^2},
\]

and the exact background equation

\[
\beta k_2^2-2k_2+\frac{3}{\alpha_B\kappa}=0.
\]

Its discriminant is

\[
4\left(1-\frac{\alpha_{\rm crit}}{\alpha_B}\right),
\qquad
\alpha_{\rm crit}=\frac{3N^2}{4q_{\min}^2}.
\]

Therefore:

- \(\alpha_B<\alpha_{\rm crit}\): no real fixed-Chern pure-magnetic common product;
- \(\alpha_B=\alpha_{\rm crit}\): one double root with \(k_1=0\);
- \(\alpha_B>\alpha_{\rm crit}\): two roots, a low-curvature \(k_1>0\) branch and a high-curvature \(k_1<0\) branch.

For \(N=2,q_{\min}=1,\kappa=1\), the certified compact
Plebański--Hacyan fixture is precisely the critical wall
\((\alpha_B,k_2,k_1)=(3,1,0)\).  At \(\alpha_B=4\), the two exact branches
are

\[
(k_2,k_1)=\left(\frac12,\frac14\right),
\qquad
(k_2,k_1)=\left(\frac32,-\frac34\right).
\]

## Structural consequence

The complete imported Taub-sign theorem is supported exactly on the flat
double-root wall.  The generic product preflight supplies only the principal
symbol chain map.  It explicitly lacks the curvature/flux lower-order
Hessians and a covariant presymplectic map.  Consequently neither the extra
Weyl definiteness nor the opposite Einstein sign is presently defined on the
two open chambers.  Continuity from the wall is not a proof because the
branch factorization and Lee--Wald pivots can change at the double root.

This is the first exact obstruction to the requested structural sign theorem.
The work item should close `OBSTRUCTED`, not `DONE`.

## Next scientific gate

Construct the full axial and polar lower-order Weyl--Maxwell Hessians on the
low-curvature \(dS_2\times S^2\) branch first, together with the same-background
Einstein image, q/p branch dictionary, action-derived Lee--Wald current and
lifted stabilizers.  Factor every shell, exceptional harmonic and current
pivot.  Treat the high-curvature \(AdS_2\times S^2\) branch separately because
its global boundary/Cauchy policy is not inherited from the compact flat
fixture.

The atlas fragment is fail-closed: background chambers are certified, while
off-wall dispersion, symplectic, Taub, resonance and causal maps remain
`NO_CERTIFIED_MAP` or `OPEN`.

## Evidence and verification

- Certificate: `bridge/certificates/EINSTEIN_MAXWELL_WEYL_FIXED_CHERN_PRODUCT_TAUB_SIGN_PREFLIGHT_V1.json`
- Producer: `bridge/einstein_sector/einstein_maxwell_weyl_fixed_chern_product_taub_sign_preflight.py`
- Independent verifier: `bridge/einstein_sector/verify_einstein_maxwell_weyl_fixed_chern_product_taub_sign_preflight.py`
- Atlas: `residual_atlas/einstein-fixed-chern-product-taub-sign-preflight-fragment-v1.json`
- Tests: nine exact tests, including independent algebra and forbidden-promotion mutations

The proof is `LOCAL-ALGEBRAIC`; imported fixed-wall sign statements are
`REDUCED-MODE`.  It establishes no Lorentzian-causal, observational,
scattering, particle, positivity or quantum claim.
