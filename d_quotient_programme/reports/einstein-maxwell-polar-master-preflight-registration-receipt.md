# Einstein--Maxwell polar-master-preflight registration receipt

Date: 2026-07-16

The programme imports commit
`95bdcc71e5410036abab18a86c6e841f42cc7d6b` and certificate
`bridge/certificates/einstein_maxwell_polar_master_preflight.json` with SHA-256
`bf7eefe8033e14bc13c055bc8c2210c68748f0707d1614d51ddd162a5f101705`.

The verdict `G1_POLAR_ELL_GE2_MATRIX_PREFLIGHT` certifies the generic polar
coefficient matrix, exact two-master reduction, axial--polar isospectrality,
corrected Maxwell volume-density row, reduced symmetrizer, and one exact
full-tensor `ell=2` plus-branch fixture. It does not promote the
arbitrary-`lambda` full-tensor identity, exceptional `ell=0,1` blocks,
covariant symplectic normalization, full fourth-order adjoint cokernel, or
quadratic obstruction theorem.

Verification uses
`python3 d_quotient_programme/verify_programme_status.py --check --guards`.
The command passed in `0.26 s`, including exact regeneration, evidence hashes,
and mutation guards. This is the affected Tier-2 programme chain; Tier 3
criteria are not met because the imported theorem remains an explicit
preflight.
