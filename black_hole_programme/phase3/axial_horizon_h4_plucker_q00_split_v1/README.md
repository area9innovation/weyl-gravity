# Exact q00 dyadic split

This bounded remedy experiment splits the original q00 cell exactly:

\[
[1/2,2049/4096]
=
[1/2,4097/8192]\cup[4097/8192,2049/4096].
\]

Each child independently rebuilds the exact horizon initializer and
degree-four shared-generator Taylor transport. Both stop at shell 4,
segment 3—the boundary where the unsplit cell lost its componentwise
projective pivot witness.

The cover counts only if the independent verifier confirms:

- exact dyadic abutment with no gap or overlap;
- both frozen parent-certificate hashes;
- the generated exterior-action and relation inventories;
- all 20 ordered segment checkpoints in each child;
- a nonzero pivot and all 45 relation checks at the target.

From `physics/symplectic-reconstruction`:

```bash
PYTHONPATH=. python3 -m \
  black_hole_programme.phase3.\
axial_horizon_h4_plucker_q00_split_v1.run_children

PYTHONPATH=. python3 -m unittest -v \
  black_hole_programme.phase3.\
axial_horizon_h4_plucker_q00_split_v1.test_split

PYTHONPATH=. python3 -m \
  black_hole_programme.phase3.\
axial_horizon_h4_plucker_q00_split_v1.verify
```

No child proceeds beyond shell 4, segment 3.
