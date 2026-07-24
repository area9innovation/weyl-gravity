# Axial QNM ECS inverse-tortoise gate v1

This package advances the exact infinity-tail shortfall by constructing the
principal inverse-tortoise branch on the \(\theta=\pi/4\) exterior-complex
scaled ray from \(r=45\).  It proves that the branch stays in
\(\operatorname{Re}r\ge45\), avoids \(r=0,2\), and gives uniform contraction
bounds for the reduced spin-one and spin-two scalar Volterra equations on
the proposed radius-\(0.025\) QNM disk.

The resulting balls enclose the reduced scalar Jost value and derivative at
\(r=45\).  They are not a full Bach outgoing frame and do not certify an
Evans boundary, a root count, a QNM or an EP2.

Run:

```bash
python3 -m black_hole_programme.phase3.axial_qnm_ecs_inverse_tortoise_v1.produce
python3 -m black_hole_programme.phase3.axial_qnm_ecs_inverse_tortoise_v1.verify
python3 -m unittest -v black_hole_programme.phase3.axial_qnm_ecs_inverse_tortoise_v1.test_ecs_inverse_tortoise
```
