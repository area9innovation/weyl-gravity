#!/usr/bin/env bash
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

python3 -m py_compile \
  black_hole_programme/phase4/axial_massive_jost_crosswalk_v1/verify.py \
  black_hole_programme/phase4/axial_qnm_ecs_fredholm_v1/verify.py \
  black_hole_programme/phase4/axial_qnm_causal_laplace_bridge_v1/verify.py \
  black_hole_programme/phase4/axial_qnm_null_infinity_reconstruction_v1/verify.py \
  paper/generate_17_pure_weyl_extension_claim_map.py \
  paper/verify_17_pure_weyl_extension_claim_map.py

python3 black_hole_programme/phase4/axial_massive_jost_crosswalk_v1/verify.py
python3 -m black_hole_programme.phase4.axial_qnm_ecs_fredholm_v1.verify
python3 -m black_hole_programme.phase4.axial_qnm_causal_laplace_bridge_v1.verify
python3 -m black_hole_programme.phase4.axial_qnm_null_infinity_reconstruction_v1.verify

python3 paper/generate_17_pure_weyl_extension_claim_map.py --check
python3 paper/verify_17_pure_weyl_extension_claim_map.py

python3 -m unittest -v \
  black_hole_programme.phase4.axial_massive_jost_crosswalk_v1.test_jost_crosswalk \
  black_hole_programme.phase4.axial_qnm_ecs_fredholm_v1.test_ecs_fredholm \
  black_hole_programme.phase4.axial_qnm_causal_laplace_bridge_v1.test_causal_bridge \
  black_hole_programme.phase4.axial_qnm_null_infinity_reconstruction_v1.test_reconstruction \
  paper.test_17_pure_weyl_extension_claim_map

echo "PASS: Paper 17 scoped reproduction and claim-boundary checks"
