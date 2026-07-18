# Exceptional `ell=1,k=0` solution cofiber

The compact Plebański--Hacyan target quotient has three axial spectral fibres
at `omega^2=0,4/3,4` and two polar fibres at `omega^2=4/3,4`.  The source image
contains the axial twist and both standard `omega^2=4` modes.  The solution
cofiber is therefore exactly one extra `omega^2=4/3` mode in each parity,
tensored with the real `ell=1` SO(3) multiplicity.

The certificate prints Lagrange/CRT projectors in `x=omega^2`.  These are the
explicit solution-level inclusion/projection maps requested by bridge 1.  The
direct action current gives the extra block Gram matrix `diag(16,3)` and zero
standard--extra mixed pairing, so the cofiber is nonradical.

Lifecycle remains `ONSHELL_MAP_ONLY`: no exceptional ghost--field--equation--
identity chain map, nonzero compact-momentum classification or final residual
descent is asserted.

Evidence:

- `bridge/certificates/einstein_weyl_exceptional_ell1_solution_cofiber.json`
- `bridge/einstein_sector/einstein_weyl_exceptional_ell1_solution_cofiber.py`
- `bridge/einstein_sector/verify_einstein_weyl_exceptional_ell1_solution_cofiber.py`
