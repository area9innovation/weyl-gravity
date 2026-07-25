# Paper 17 exterior pole and critical-mass bridge

Date: 2026-07-25

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Results

Paper 17 now contains two further analytical promotions.

### Exterior cut-off pole

Analytic horizon and infinity Jost solutions define exact transparent
boundary conditions at arbitrary finite cuts outside compact source and
observation supports. The finite-interval inverse therefore agrees exactly
with the cut-off exterior outgoing inverse. The certified defective Smith
type consequently gives
\[
\operatorname{Coeff}_{(\omega-\omega_n)^{-2}}
\bigl(\chi_{\rm o}R_{\rm ext}\chi_{\rm s}\bigr)
=
-\frac{\beta_n}{\alpha_n^2}
(\chi_{\rm o}u_n)\otimes(\widetilde u_n\chi_{\rm s}).
\]
The coefficient is nonzero and rank one for nontrivial smooth cutoffs,
because the selector is nonzero and a nonzero second-order ODE solution
cannot vanish on an open interval.

This is an exterior radial Green-operator theorem with compact source and
observation localization. It is not a causal spacetime resolvent theorem.

### Exact local critical-mass jet

On the transverse-traceless spin-two sector,
\[
L_m=L_2-mf
\]
gives
\[
L_2\partial_my=fy,
\qquad
[\mathcal I_{\rm mass}]=[f].
\]
Together with the exact Bach normal form,
\[
[\mathcal I_{\rm Bach}]
=\frac{i\omega}{2}[f],
\]
this proves
\[
[\mathcal I_{\rm Bach}]
=\frac{i\omega}{2}[\mathcal I_{\rm mass}],
\qquad
m=\frac{i\omega}{2}\tau
\]
in the local transverse-traceless differential module.

The equivalence gauge has the forced asymptotic slope
\[
q(r,\omega)=-\frac{i}{8\omega}r+O(1).
\]
Therefore no bounded rational triangular gauge preserves the infinity Jost
frame.

### Boundary transgression

The paper's gauge convention is
\[
Q(q)=qD-\frac12Dq,
\qquad
[L,Q(q)]|_{\ker L}=-\frac12\mathcal K_U(q).
\]
Consequently the correctly normalized commutator gauge is
\[
\widehat Q=-2Q(q),
\]
not \(Q(q)\). The exact finite-cut identity is
\[
\beta_{n,[x_-,x_+]}^{\rm Bach}
-\frac{i\omega_n}{2}\beta_{n,[x_-,x_+]}^{\rm mass}
=
\left[W(\widetilde u_n,\widehat Q u_n)\right]_{x_-}^{x_+}.
\]

The only remaining physical normalization calculation is the endpoint
limit
\[
\left[W(\widetilde u_n,\widehat Q u_n)\right]_{\mathcal H^+}^{\mathcal I^+}.
\]
It must be evaluated or regularized in matched Jost frames before claiming
\[
\left.\frac{d\omega_n}{dm}\right|_{m=0}
=\frac{2i}{\omega_n}\kappa_n^{\rm Bach}.
\]

## Claim boundary

This update does not establish:

- the uncut causal exterior spacetime resolvent;
- an inverse-Laplace contour deformation or generalized ringdown term;
- equality of globally normalized Bach and massive Jost coefficients;
- the physical massive QNM slope;
- vanishing or finiteness of the endpoint transgression before
  regularization;
- time-domain stability or any quantum statement.

## Verification

The claim map now pins the critical-parent and analytic-continuation
authorities in addition to the previous extension, QNM, and finite-interval
pole authorities.

The independent verifier checks:

- the exact Bach cocycle normal form;
- the forced gauge slope and its constant matching;
- the mass-jet parameter relation;
- the necessary \(-2\) commutator-gauge normalization;
- the exact period, root-chain, resonant-evaluation, and Green-residue
  declarations;
- all upstream flags and fail-closed boundaries.

Commands:

```text
python3 -m unittest paper/test_17_pure_weyl_extension_claim_map.py
python3 paper/generate_17_pure_weyl_extension_claim_map.py --check
python3 paper/verify_17_pure_weyl_extension_claim_map.py
python3 -m py_compile paper/generate_17_pure_weyl_extension_claim_map.py \
  paper/verify_17_pure_weyl_extension_claim_map.py \
  paper/test_17_pure_weyl_extension_claim_map.py
cd paper
pdflatex -interaction=nonstopmode -halt-on-error \
  17-pure-weyl-schwarzschild-extension-structure.tex
pdflatex -interaction=nonstopmode -halt-on-error \
  17-pure-weyl-schwarzschild-extension-structure.tex
git diff --check -- <scoped paths>
```

Outcome:

- 15 regression and mutation tests passed;
- deterministic claim-map drift check passed;
- independent symbolic, semantic, and provenance verification passed;
- PDF compiled in two passes, 17 pages;
- scoped `git diff --check` passed.

Tier 2 was not rerun because the upstream operators and content-addressed
authorities were not changed. Because this revision promotes new Paper 17
theorems, Tier 3 was run with
`python3 -m unittest discover`: all 149 discovered repository tests passed
in 0.316 seconds (2.86 seconds wall).

CLOSE-OUT: DONE — exterior cut-off pole and local critical-mass bridge
promoted with the endpoint normalization isolated exactly.
EVIDENCE: reports/PAPER17_EXTERIOR_MASS_BRIDGE_TIER_RECEIPT.json
