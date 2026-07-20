# Independent freeze audit: quadratic active-clock locus

## Freeze verdict

The terminal quadratic active-clock result survives a method-distinct exact
audit:

\[
\boxed{
\mathcal L_{\mathrm{stationary}}
=\mathbb R\left(
\frac{81}{20},\frac{27}{3290},-\frac{324}{1645},
\frac{486}{1645},\frac{18}{25},1
\right),
\qquad
\mathcal L_{\mathrm{good}}=\varnothing.
}
\]

The scoped quadratic-active-clock no-go is therefore theorem-frozen. No
`Candidate C_active` is selected.

The audit reads the terminal JSON and pins its action hash, but neither imports
nor invokes its producer. It does not reuse the producer's RREF.

## Pinned terminal object

```text
result_id:
  COMPENSATOR_ACTIVE_CLOCK_PX2_LOCUS_V1
certificate_sha256:
  9ad148d6b632e215cd75636f5fd5b431fa85cf1698a63f725d8b3c9dfe61de89
action_family_sha256:
  c665462b1b98098613c3b325a1866133b32d681caec943a6c8e4a1460d0e7938
source_commit:
  c770752d132accb4e3b2bb59884d6faf10335fc8
```

## Independent action-basis reduction

The audit begins from grading signatures and the work item's replacement-only
rule.

At four metric derivatives, the parity-even scalar curvature orbit is

\[
C^2,\quad R^2,\quad E_4,\quad \Box R.
\]

\(E_4\) is topological and \(\Box R\) is horizontally exact. At two metric
derivatives, \(R\) is the single retained scalar. Shift symmetry and polynomial
degree at most two give the phase orbit

\[
1,\quad X,\quad X^2.
\]

The constant is \(p_0\). Thus the canonical coefficient basis is independently
recovered as

\[
(\alpha_B,\alpha_R,M_P^2,p_0,p_1,p_2).
\]

The work item replaces only the phase sector of the declared
\(C^2+R^2+R\) theory. Mixed operators such as \(RX\) are not silently omitted;
they belong to a larger theory class outside this theorem. The reconstructed
basis reproduces the pinned terminal action hash.

## Independent Berger geometry and variation

For the biaxial metric with \(a=1\) and \(q=c^2\), the audit evaluates the
Maurer--Cartan invariant formulas

\[
\mathrm{Ric}_{\hat a\hat b}
=\operatorname{diag}
\left(0,\frac{2-q}{2},\frac{2-q}{2},\frac q2\right),
\qquad
R=\frac{4-q}{2},
\]

\[
B_{\hat a\hat b}
=\operatorname{diag}\left(
\frac{(1-q)^2}{6},
\frac{(1-q)(1-3q)}{6},
\frac{(1-q)(1-3q)}{6},
\frac{(1-q)(5q-1)}{6}
\right).
\]

At \(q=9/40\), these reproduce the frozen Ricci, scalar and Bach entries.

Each matter column is varied monomial by monomial from

\[
-T_{ab}[X^n]
=2nX^{n-1}\partial_a\theta\partial_b\theta-X^ng_{ab}.
\]

This reconstructs the terminal cylinder and Berger matrices coefficientwise.
The clock equation passes independently: the cylinder clock is constant,
while on Berger \(X\), \(P_X\) and \(\dot\theta=3/4\) are constant.

## Integer maximal-cofactor elimination

The five rational stationary rows are cleared by row scales

\[
(1,1,19200,19200,3840).
\]

The resulting integer matrix is

\[
\begin{pmatrix}
0&36&3&1&0&0\\
0&12&-1&-1&0&0\\
1922&68403&18120&19200&10800&-18225\\
806&60249&-1080&-19200&10800&-6075\\
62&-10419&-3192&-3840&2160&-1215
\end{pmatrix}.
\]

Deleting columns \(0,\ldots,5\) gives the six maximal minors

\[
\begin{aligned}
(&-12847802688000,\ 26034048000,\ 624817152000,\\
 &937225728000,\ -2284053811200,\ 3172296960000).
\end{aligned}
\]

The alternating cofactors have gcd \(96422400\). After primitive
normalization with positive last entry, the integer kernel is

\[
(133245,270,-6480,9720,23688,32900).
\]

The last component is nonzero, so normalizing \(p_2=1\) yields exactly the
terminal rational generator. A nonzero maximal minor proves rank five
globally; there is no hidden rank-change parameter stratum.

## Singular strata and denominators

The audit does not divide by the locus parameter before separating its real
strata:

* \(t=0\): the action is zero and has no principal operator, pairing or clock
  dynamics;
* \(t>0\): the auxiliary presentation is valid, the velocity inertia is
  \((1,2,0)\), the Berger clock has standard sign, and the cylinder clock has
  the wrong sign;
* \(t<0\): the auxiliary presentation is valid, the velocity inertia is
  \((2,1,0)\), the cylinder clock has standard sign, and the Berger clock has
  the wrong sign.

All remaining denominators are nonzero integers:
\(20,25,200,1645,3290,2105600\). Row clearing uses only the positive integers
displayed above.

## Coupled principal, velocity and clock audit

On \(t\ne0\), a rational congruence takes the velocity Hessian to

\[
\operatorname{diag}\left(-6,6,-\frac{36}{25}t\right).
\]

This proves the immutable split gravity--auxiliary pair without computing
numerical eigenvalues. The six-dimensional state evolution has exact
characteristic and minimal polynomial

\[
\lambda^2(\lambda^2-2)^2.
\]

The audit verifies the annihilating polynomial and separately rejects both
proper exponent reductions.

For the Berger clock,

\[
P_X=-\frac{81}{200}t,\qquad
P_X+2XP_{XX}=-\frac{531}{200}t,\qquad
c_s^2=\frac9{59}.
\]

The longitudinal factor is retained explicitly. Standard-sign Berger
propagation requires \(t>0\), while the unit-cylinder quadratic clock requires
\(p_1<0\), hence \(t<0\). Their exact intersection is empty.

The Lee--Wald form and raw-\(D\) Hamiltonian reproduce the terminal both-sign
witnesses \(+3\) and \(-3\). The independently recomputed charge densities are

\[
Q_R=\frac{243}{400}t,\qquad
\rho_D=\frac{523827}{2105600}t,\qquad
\rho_K=-\frac{435537}{2105600}t.
\]

The total closed-background identity remains

\[
\iota_D\Omega=\frac34\,\delta Q_R,\qquad
\iota_{K_{\rm Berger}}\Omega=0.
\]

The previous \(\delta Q_R=0\) theorem for a different linear clock action is
not reused.

## Adversarial audit

Four required mutations are rejected:

| Mutation | Exact rejection |
| --- | --- |
| Berger \(p_2\) stress coefficient \(-243/256\to-242/256\) | `BERGER_ROW_MISMATCH` |
| background \(q:9/40\to1/4\) | `BERGER_ROW_MISMATCH` |
| flip the \(-T_{ab}\) sign convention | `CYLINDER_ROW_MISMATCH` |
| omit \(P_X+2XP_{XX}\) from the gate set | `OMITTED_LONGITUDINAL_GATE` |

Additional tests reject deletion of the \(t=0\) stratum, replacement of the
cofactor kernel by one sample, Candidate promotion, universalization and
Hadamard/quantum promotion.

## Claim boundary

This freeze applies only to dressed \(C^2+R^2+R\) gravity with the complete
quadratic shift-symmetric \(P(X)\) sector, no HT and no new fields on the unit
cylinder and frozen \(q=9/40\) Berger clock. It does not cover higher \(P(X)\),
higher derivatives, nearby backgrounds, fixed-charge reductions, new fields
or enlarged gauge groups. It exports no complete support-local causal parent,
Hadamard state, anomaly/QME result, particle space, scattering theorem,
positivity theorem or unitarity theorem.

## Reproduction

```bash
python3 d_quotient_classical/compensator/active_clock_px2_independent_freeze_audit.py --check
python3 d_quotient_classical/compensator/verify_active_clock_px2_independent_freeze_audit.py
python3 -m unittest \
  d_quotient_classical.compensator.tests.test_active_clock_px2_independent_freeze_audit -v
npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true \
  -s d_quotient_classical/schema/compensator-active-clock-px2-independent-freeze-audit-v1.schema.json \
  -d d_quotient_classical/certificates/COMPENSATOR_ACTIVE_CLOCK_PX2_INDEPENDENT_FREEZE_AUDIT_V1.json
python3 d_quotient_classical/atlas/generate_classical_atlas_fragment.py --check
python3 d_quotient_classical/atlas/verify_classical_atlas_fragment.py
python3 -m unittest \
  d_quotient_classical.atlas.tests.test_classical_atlas_fragment -v
```

CLOSE-OUT: DONE — the terminal no-go survives a method-distinct exact audit
and is theorem-frozen at its declared scope.

EVIDENCE: `d_quotient_classical/receipts/COMPENSATOR_ACTIVE_CLOCK_PX2_INDEPENDENT_FREEZE_AUDIT_V1_TIER_RECEIPT.json`
