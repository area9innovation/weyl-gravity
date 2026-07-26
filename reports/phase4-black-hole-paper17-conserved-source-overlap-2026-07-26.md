# Paper 17 conserved-source overlap close-out

Date: 2026-07-26  
Work item: `sf:program/work/phase4-black-hole-paper17-conserved-source-overlap`  
Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

The odd stress-energy source map is exactly onto the smooth compact radial
Regge--Wheeler forcings at every nonzero frequency.

For

\[
\mu=(\ell-1)(\ell+2),\qquad
(\partial_{r_*}^2+\omega^2-fV_{\rm odd})\Psi=F,
\]

the Martel--Poisson odd projections

\[
P_t=0,\qquad
P_r=\frac{\mu F}{2i\omega rf},\qquad
P=\frac{\partial_r(rF)}{2i\omega}
\]

satisfy

\[
\nabla_aP^a+\frac2r r_aP^a-\frac{\mu}{r^2}P=0
\]

and produce

\[
fS_{\rm odd}=F.
\]

Using the exact odd-harmonic norms, the inverse projections are

\[
T^{aB}=\frac{P^a}{16\pi r^2}X^B,\qquad
T^{AB}=\frac{P}{8\pi r^4}X^{AB}.
\]

This stress tensor is conserved. It is also traceless because its
two-dimensional tensor block vanishes and \(X^{AB}\) is trace-free.
Accordingly, it is compatible with the divergence-free and trace-free Bach
equation as a complexified external source.

For the nonzero adjoint QNM state, choose

\[
F=\eta\,\overline{\widetilde u_n},
\]

where \(\eta\) is a nonnegative nonzero compact bump supported where
\(\widetilde u_n\ne0\). Compact support removes all endpoint terms and gives

\[
\langle\widetilde u_n,F\rangle_{\rm aug}
=\int\eta|\widetilde u_n|^2\,dr_*>0.
\]

The source-side overlap and the previously certified Bondi observation
overlap are therefore simultaneously nonzero. The isolated transfer
operator has a visible double pole and a nonzero
\(u e^{i\omega_nu}/r\) coefficient for this source.

## Scientific correction

A standard massive point-particle stress tensor has nonzero trace. It cannot
be inserted directly on the right-hand side of the pure-Weyl Bach equation,
whose left-hand side is trace-free. A future plunging-source calculation must
first specify a conformal matter completion, an improved stress tensor, or a
compensator. The present theorem is an exact source-existence result, not a
nonzero-overlap theorem for a geodesic massive particle.

## Evidence

Primary source formulas:

- K. Martel and E. Poisson, *Gravitational perturbations of the
  Schwarzschild spacetime: A practical covariant and gauge-invariant
  formalism*, Phys. Rev. D 71, 104003 (2005), arXiv:gr-qc/0502028,
  Eqs. (3.4), (3.9), and (5.10)--(5.16).

Certificate package:

- `black_hole_programme/phase4/axial_qnm_conserved_source_overlap_v1/`

The producer checks the projection, master-source, conservation, and
trace identities. The independent verifier re-derives the reduced source
and conservation law. Five tests include decisive source-sign,
conservation-sign, point-particle-promotion, and plunge-promotion mutations.

## Claim boundary

Established:

- arbitrary smooth compact reduced odd forcing is realized;
- the realizing external stress tensor is conserved and traceless;
- a source with nonzero certified-QNM adjoint overlap exists;
- the already certified observation overlap then makes the isolated
  double-pole transfer coefficient nonzero.

Not established:

- nonzero overlap for a specified geodesic plunge;
- a positive-energy or energy-condition-satisfying matter realization;
- a global retarded inverse-Laplace deformation;
- detector sensitivity or parameter-estimation bounds;
- admissibility of the weakened constant generalized component in a
  standard asymptotically flat phase space.

## Verification commands

```text
python3 black_hole_programme/phase4/axial_qnm_conserved_source_overlap_v1/produce.py
python3 black_hole_programme/phase4/axial_qnm_conserved_source_overlap_v1/verify.py
python3 -m unittest black_hole_programme.phase4.axial_qnm_conserved_source_overlap_v1.test_source_overlap
python3 paper/generate_17_pure_weyl_extension_claim_map.py
python3 paper/verify_17_pure_weyl_extension_claim_map.py
python3 -m unittest paper.test_17_pure_weyl_extension_claim_map
cd paper && pdflatex -interaction=nonstopmode -halt-on-error 17-pure-weyl-schwarzschild-extension-structure.tex
cd paper && pdflatex -interaction=nonstopmode -halt-on-error 17-pure-weyl-schwarzschild-extension-structure.tex
```

Tier 3 was not run because no shared core operator, release, or freeze was
changed. The exact affected Paper 17 chain and its imported hashes were
replayed.

EVIDENCE: `black_hole_programme/phase4/axial_qnm_conserved_source_overlap_v1/receipt.json`

CLOSE-OUT: DONE — exact conserved-traceless source realization, nonzero adjoint overlap, Paper 17 revision, certificate, independent verifier, mutation tests, PDF, and receipts are complete; specified conformal-matter trajectories and global causal promotion remain explicit successor gates.
