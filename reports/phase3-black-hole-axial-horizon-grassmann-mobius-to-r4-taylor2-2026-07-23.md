# Phase 3 axial horizon Grassmann/Möbius Taylor2 q0 sentinel

## Outcome

`CLASSIFIED — TAYLOR2_AMPLITUDE_RANK_SHORTFALL`

Dependency tag: `LOCAL-ALGEBRAIC`.

The q0-only degree-two shared-parameter consumer certified shells 0 and 1
through all 256 panels per shell.  It retained chart 11, real rank six on the
64-cell frequency cover, direct overlap, checked right action, 128-bit dyadic
rebase, separate amplitude transport, exact gauge covariance, and the norm
bound.  After panel 256 of shell 2 it refused at the uniform amplitude-rank
gate and returned exit 3.

The last enclosed graph state had norm `1.5016025242724733` and width
`3.003205047438802`.  The latter is slightly tighter than the frozen affine
width `3.003240069284962`, but the degree-two lift does not change the first
failed gate.  The exact amplitude center still has rank six; failure to certify
the whole 64-cell cover is therefore an enclosure/method shortfall, not a proof
of a singularity or physical rank loss.

## Provenance and boundary

The consumer imports the frozen q0 source at physics commit
`630880a6cb8d83efa286c585ffe68c52898e7f04`, SHA-256
`6978e7532e7f30944b746db91fb58d2254bd3267607947b2c3e7ea5e9ed527c3`.
It ran against `ivtaylor.forge` extracted from Tango commit
`972aa4337b73cc0f632d9599fb345098bc8ccce8`, kernel SHA-256
`fd51f0ab2a1ebce950660b58dcfc31728c032de872001f50f907f11cfa2be103`.
A superseded lifecycle checkpoint named a nonexistent `630880a6cb796…`
commit; that checkpoint is not an input.

q1–q15 were not run.  This result does not establish a horizon-to-infinity
connection, scattering, flux sign, stability, ghost, positivity, CPT,
unitarity, or any `LORENTZIAN-CAUSAL` quantum statement.

Machine receipts:

- `black_hole_programme/phase3/axial_horizon_grassmann_mobius_to_r4_taylor2/certificate.json`
- `black_hole_programme/phase3/axial_horizon_grassmann_mobius_to_r4_taylor2/receipt.json`
- `black_hole_programme/phase3/axial_horizon_grassmann_mobius_to_r4_taylor2/sentinel_q00.log`

The run elapsed 925.10 seconds, used 3656 KiB maximum resident memory, and
returned exit 3 as the typed shortfall.

## Exact carrier-subspace disposition

`CLASSIFIED — FIXED_TWO_PLANE_NOT_INVARIANT`

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

At the exact diagnostic frequency `omega=4097/8192`, the leading carrier
vectors of `XH0a` and `XH0b` have rank two.  However, the exact join
`[B,A(r)B]` has rank four at each of `r=5/2,3,4`; the three retained complex
rational determinants are nonzero.  Thus these columns define a
two-dimensional future-regular zero-indicial solution subspace inside the
four-dimensional Ricci carrier, but not a fixed closed two-dimensional
coordinate subsystem.  This does not by itself decide boundary projection
rank.

The independently reproducible machine witness is
`black_hole_programme/phase3/axial_horizon_grassmann_mobius_to_r4_taylor2/carrier_subspace_witness.json`.
Its producer imports the authoritative exact carrier matrix and endpoint
heads rather than reconstructing a second system.

## Direct horizon Gram epsilon-method shortfall

`CLASSIFIED — METHOD_SHORTFALL`

A direct evaluation of the repaired Frobenius initializer and exact radial
Lee--Wald current at `rho=2^-22` was attempted.  At `omega=1/2`, the midpoint
Hermitian eigenvalues were approximately `(-15.2141, 0.240317, 2024.476)`,
but independent entrywise Frobenius-tail boxes were amplified by the
singular current to Gram widths of order `10^5`.  Interval LDL therefore
could not isolate a pivot on any of the first eight frequency cells.  The
sweep was stopped fail-closed.  This is an enclosure-correlation failure,
not evidence for a flux-sign or rank failure.

The smallest corrective architecture is the exact `rho -> 0` Laurent
constant term of the correlated Frobenius series paired with the exact
current.  No horizon Gram or inertia claim is promoted by the failed epsilon
method.
