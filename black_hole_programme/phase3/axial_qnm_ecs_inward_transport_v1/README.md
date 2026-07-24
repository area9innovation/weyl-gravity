# Axial QNM ECS inward transport v1

This successor carries the certified reduced scalar ECS initializer sets
from \(r=45\) to the concrete matching radius \(r=4\).  It proves uniform
analytic dependence on the proposed closed frequency disk and supplies an
exact Gronwall enclosure.

The enclosure radius is of order \(10^{33}\).  It therefore proves
existence and analytic transport but is deliberately marked unusable for
Evans-boundary nonvanishing.  The exact intrinsic tangent source is regular
on the finite path, but its correlated ECS boundary datum at \(r=45\)
remains open.

Run:

```bash
python3 -m black_hole_programme.phase3.axial_qnm_ecs_inward_transport_v1.produce
python3 -m black_hole_programme.phase3.axial_qnm_ecs_inward_transport_v1.verify
python3 -m unittest -v black_hole_programme.phase3.axial_qnm_ecs_inward_transport_v1.test_ecs_inward_transport
```
