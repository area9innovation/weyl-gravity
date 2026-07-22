# Paper 15 publication clarifications

Date: 2026-07-22

## Scope

This revision makes the existing Paper 15 Phase-2 evidence
referee-readable. It changes no source theorem, certificate, lifecycle, or
authorship claim.

## Clarifications established from frozen evidence

- The compact pseudo-Hermitian pilot is stated as a
  24-real-dimensional structured positive-metric cone on the exact
  \(2+2+4\) spectral multiplicity frame. The imported action/Krein form
  \(G\), its unique positive fundamental symmetry
  \(C_0=-I_2\oplus I_2\oplus I_4\), and
  \(\eta_0=GC_0>0\) are separated from a genuine Mannheim \(CPT\)
  construction.
- The cylinder obstruction is quantified: each proper-conformal row has
  rank-32 commutator with the stationary \(C_0\) per chirality; the
  degree-zero-to-one BRST defect has rank 102 per chirality and 204 on the
  two-chirality direct sum. Nontrivial ghost-normalizer actions remain open.
- Schwarzschild variables are dimensionless,
  \(\widehat r=r/M\) and \(\widehat\omega=M\omega\), and the radial slice
  begins at \(2M\). The canonical pivot wall is empty. The specialized
  polynomial
  \(R_\ell(x)=Q_{21}(\ell(\ell+1),x)\) is exactly the degeneracy locus of
  the first finite polar \(p=-2\) pairing, not a second independent wall.
- The omitted differentiated axial reconstruction forcing that reversed the
  earlier fixture interpretation is promoted into the introduction.
- The conformal-graviton anomaly coefficients are identified as established
  Fradkin--Tseytlin numbers. The manuscript states the convention crosswalk
  and limits novelty to determinant-complex reconstruction, measure and
  zero-mode bookkeeping, and the map into local BV cohomology.
- The counterflow word “healthy” is restricted to the homogeneous trace
  principal block. Its exact velocity, mass, and characteristic inequalities
  are printed, while familywide Green hyperbolicity remains unclaimed.
- The dyonic preflight and detailed incomplete Hadamard carrier census have
  been moved to an appendix.

## Preserved nonpromotions

The revision does not establish a genuine Mannheim \(C\) operator, a
nontrivial ghost normalizer, BRST descent of the compact metric, a full-BV
Hadamard covariance, an asymptotically flat Bach phase space,
horizon-to-infinity matching, a wave-packet norm, a new anomaly coefficient,
counterflow PDE stability, particles, scattering, or unitarity.

## Verification

- python3 -m unittest paper.test_15_phase1_synthesis_claim_map -v
- python3 quantum-weyl/pt_cpt/synthesis/verify_cpt_feasibility_classification.py
- python3 -m black_hole_programme.phase2.generic_l_synthesis.verify
- python3 d_quotient_classical/compensator/verify_two_phase_counterflow_hamiltonian_hopf_retuning_locus.py
- python3 planning/paper-coverage/verify_phase1_paper_coverage_overlay.py planning/paper-coverage/phase1-paper-coverage-overlay-2026-07-22.json
- three stable pdflatex -interaction=nonstopmode -halt-on-error passes

All scoped verifiers passed. The final PDF has 23 pages and no undefined
references, undefined citations, overfull boxes, ignored errors, or fatal
errors.
