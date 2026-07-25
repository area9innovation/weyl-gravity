"""Amplitude-preserving continuation of the certified infinity trace frames.

Phase 3 transported the incoming and outgoing infinity *planes* from ``r=32``
to ``r=4`` in Grassmann charts.  Its state already has the exact
factorization

    Y = G_chart(Z) A,

but deliberately reset ``A`` to the identity after every propagation and
chart change because only the planes were needed there.  This module renders
the same certified factor rail while retaining the cocycle ``A``.  No ODE
factor is recomputed.

The implementation patches four narrowly identified normalization points in
the reviewed Phase-3 Forge renderer.  Every replacement is fail-closed: a
source drift raises before a Forge program is compiled.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any

from ...phase3.axial_global_connection_matrix_v5.chunks import (
    infinity_plane_taylor_transport as base,
)


SCHEMA = "phase4-axial-amplitude-taylor-stage-v1"
TARGET_INTERVAL = ("1/2", "10001/20000")
TARGET_SHIFT = Fraction(-497, 625)
TARGET_SCALE = Fraction(128, 625)


class AmplitudeTransportError(RuntimeError):
    """Fail-closed amplitude-cocycle producer refusal."""


def _replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise AmplitudeTransportError(
            f"{label}: expected one normalization site, found {count}"
        )
    return source.replace(old, new, 1)


def _retain_amplitude_source(source: str) -> str:
    source = _replace_once(
        source,
        """  // Plane-classifier normalization: discard the endpoint-coordinate
  // amplitude and retain only the graph.  This preserves the subspace but
  // does not preserve the original scattering amplitude normalization.
  return new PtState(true,chart,ivtm_clone(z.value),pt_identity6(),
    pm_from_iv(bounds.forward),pm_from_iv(bounds.inverse));""",
        """  let ar:IvTaylorResult=ivtm_rebase_dyadic(u,160);
  if(!ar.ok){return pt_fail();}
  return new PtState(true,chart,ivtm_clone(z.value),ivtm_clone(ar.value),
    pm_from_iv(bounds.forward),pm_from_iv(bounds.inverse));""",
        "initial endpoint amplitude",
    )
    source = _replace_once(
        source,
        """  // The plane-only rail keeps amplitude exactly I6, so reconstruction is
  // literally G_chart(Z).  Avoid multiplying by an interval identity, which
  // would add outward-rounding fuzz to structurally zero pivot remainders.
  return new IvTaylorResult(true,0,pt_graph_basis(s.z,s.chart));""",
        """  let raw:IvTaylorResult=ivtm_mul_checked(
    pt_graph_basis(s.z,s.chart),s.amplitude);
  if(!raw.ok){return raw;}
  return ivtm_rebase_dyadic(raw.value,160);""",
        "frame reconstruction",
    )
    source = _replace_once(
        source,
        """  let bounds:PtBasisBounds=pt_basis_bounds(u);
  if(!zr.ok || !bounds.ok){return pt_fail();}
  return new PtState(true,new_chart,ivtm_clone(zr.value),pt_identity6(),
    pm_mul_iv(s.forward_bound,bounds.forward),
    pm_mul_iv(s.inverse_bound,bounds.inverse));""",
        """  let bounds:PtBasisBounds=pt_basis_bounds(u);
  let ar0:IvTaylorResult=ivtm_mul_checked(u,s.amplitude);
  if(!ar0.ok){return pt_fail();}
  let ar:IvTaylorResult=ivtm_rebase_dyadic(ar0.value,160);
  if(!zr.ok || !bounds.ok || !ar.ok){return pt_fail();}
  return new PtState(true,new_chart,ivtm_clone(zr.value),
    ivtm_clone(ar.value),
    pm_mul_iv(s.forward_bound,bounds.forward),
    pm_mul_iv(s.inverse_bound,bounds.inverse));""",
        "chart-change amplitude",
    )
    source = _replace_once(
        source,
        """  let bounds:PtBasisBounds=pt_basis_bounds(m.value);
  if(!zr.ok || !bounds.ok){return pt_fail();}
  return new PtState(true,s.chart,ivtm_clone(zr.value),pt_identity6(),
    pm_mul_iv(s.forward_bound,bounds.forward),
    pm_mul_iv(s.inverse_bound,bounds.inverse));""",
        """  let bounds:PtBasisBounds=pt_basis_bounds(m.value);
  let ar0:IvTaylorResult=ivtm_mul_checked(m.value,s.amplitude);
  if(!ar0.ok){return pt_fail();}
  let ar:IvTaylorResult=ivtm_rebase_dyadic(ar0.value,160);
  if(!zr.ok || !bounds.ok || !ar.ok){return pt_fail();}
  return new PtState(true,s.chart,ivtm_clone(zr.value),
    ivtm_clone(ar.value),
    pm_mul_iv(s.forward_bound,bounds.forward),
    pm_mul_iv(s.inverse_bound,bounds.inverse));""",
        "radial-step amplitude",
    )
    source = _replace_once(
        source,
        """fn pt_best_chart(s:borrow PtState)->PtState{
  let best:PtState=pt_fail();let c:i64=0;
  while(c<20){
    let cand:PtState=pt_rechart(s,c);
    if(cand.ok && (!best.ok || pt_norm(cand.z)<pt_norm(best.z))){
      best=new PtState(true,cand.chart,ivtm_clone(cand.z),
        ivtm_clone(cand.amplitude),cand.forward_bound,cand.inverse_bound);
    }
    drop(cand);c=c+1;
  }
  return best;
}""",
        """fn pt_best_chart(s:borrow PtState)->PtState{
  // Retaining a certified chart is preferable to probing singular candidate
  // pivots.  pt_step_any still changes chart if the current propagation
  // genuinely refuses.
  if(!s.ok){return pt_fail();}
  return new PtState(true,s.chart,ivtm_clone(s.z),
    ivtm_clone(s.amplitude),s.forward_bound,s.inverse_bound);
}""",
        "scheduled chart selection",
    )
    marker = "fn pt_step_any(phi:borrow IvTaylorMat,s:borrow PtState)->PtState{"
    if source.count(marker) != 1:
        raise AmplitudeTransportError("fixed-chart step insertion drift")
    fixed_step = """fn pt_step_chart(phi:borrow IvTaylorMat,s:borrow PtState,
  new_chart:i64)->PtState{
  if(!s.ok){return pt_fail();}
  let g:IvTaylorMat=pt_graph_basis(s.z,s.chart);
  let yg0:IvTaylorResult=ivtm_mul_checked(phi,g);
  if(!yg0.ok){return pt_fail();}
  let yg:IvTaylorResult=ivtm_rebase_dyadic(yg0.value,160);
  if(!yg.ok){return pt_fail();}
  let u:IvTaylorMat=pt_rows(yg.value,new_chart,true);
  let v:IvTaylorMat=pt_rows(yg.value,new_chart,false);
  let rank:IvTaylorRank=ivtm_full_column_rank_cells(u,512);
  if(!rank.certified || rank.rank!=6){return pt_fail();}
  let zr0:IvTaylorResult=ivtm_solve_right(v,u);
  if(!zr0.ok){return pt_fail();}
  let zr:IvTaylorResult=ivtm_rebase_dyadic(zr0.value,160);
  let ar0:IvTaylorResult=ivtm_mul_checked(u,s.amplitude);
  if(!ar0.ok){return pt_fail();}
  let ar:IvTaylorResult=ivtm_rebase_dyadic(ar0.value,160);
  let bounds:PtBasisBounds=pt_basis_bounds(u);
  if(!zr.ok || !ar.ok || !bounds.ok){return pt_fail();}
  return new PtState(true,new_chart,ivtm_clone(zr.value),
    ivtm_clone(ar.value),
    pm_mul_iv(s.forward_bound,bounds.forward),
    pm_mul_iv(s.inverse_bound,bounds.inverse));
}

"""
    source = source.replace(marker, fixed_step + marker, 1)
    return source


def _import_previous_amplitudes(
    source: str, previous: dict[str, Any] | None
) -> str:
    if previous is None:
        return source
    minus = previous["chart_states"]["Iminus"]["amplitude"]
    plus = previous["chart_states"]["Iplus"]["amplitude"]
    builders = "\n".join(
        base._serialized_builder("pt_previous_minus_a", minus)
        + base._serialized_builder("pt_previous_plus_a", plus)
    )
    marker = "fn pt_seed_minus()->PtState{"
    if source.count(marker) != 1:
        raise AmplitudeTransportError("continuation amplitude insertion drift")
    source = source.replace(marker, builders + "\n" + marker, 1)
    source = _replace_once(
        source,
        "    pt_previous_minus_z(),pt_identity6(),",
        "    pt_previous_minus_z(),pt_previous_minus_a(),",
        "minus continuation amplitude",
    )
    source = _replace_once(
        source,
        "    pt_previous_plus_z(),pt_identity6(),",
        "    pt_previous_plus_z(),pt_previous_plus_a(),",
        "plus continuation amplitude",
    )
    return source


def _emit_amplitudes(source: str) -> str:
    source = _replace_once(
        source,
        """  let mz:String=ivtm_serialize(minus.z,0);
  let pz:String=ivtm_serialize(plus.z,0);""",
        """  let mz:String=ivtm_serialize(minus.z,0);
  let pz:String=ivtm_serialize(plus.z,0);
  let ma:String=ivtm_serialize(minus.amplitude,0);
  let pa:String=ivtm_serialize(plus.amplitude,0);""",
        "amplitude serialization",
    )
    source = _replace_once(
        source,
        """  println(strfmt(system_allocator(),"MINUS_Z {}",[str_view(mz)]));
  println(strfmt(system_allocator(),"PLUS_Z {}",[str_view(pz)]));""",
        """  println(strfmt(system_allocator(),"MINUS_Z {}",[str_view(mz)]));
  println(strfmt(system_allocator(),"PLUS_Z {}",[str_view(pz)]));
  println(strfmt(system_allocator(),"MINUS_A {}",[str_view(ma)]));
  println(strfmt(system_allocator(),"PLUS_A {}",[str_view(pa)]));""",
        "amplitude output",
    )
    source = _replace_once(
        source,
        "  drop(ms);drop(ps);drop(mz);drop(pz);",
        "  drop(ms);drop(ps);drop(mz);drop(pz);drop(ma);drop(pa);",
        "amplitude output cleanup",
    )
    return source


def _raw_terminal(
    *,
    child: int,
    stage: int,
    ordinals: list[int],
    start_local: int,
    initial_minus: str,
    initial_plus: str,
    require_rank: bool,
) -> str:
    lines = [
        f"  let mraw:IvTaylorMat=ivtm_clone({initial_minus});",
        f"  let praw:IvTaylorMat=ivtm_clone({initial_plus});",
    ]
    for local in range(start_local, len(ordinals)):
        ordinal = ordinals[local]
        lines += [
            f"  let phi_{local}:IvTaylorMat=pt_factor_{local:03d}();",
            f"  let mr0_{local}:IvTaylorResult=ivtm_mul_checked(phi_{local},mraw);",
            f"  let pr0_{local}:IvTaylorResult=ivtm_mul_checked(phi_{local},praw);",
            f"  if(!mr0_{local}.ok || !pr0_{local}.ok){{",
            f'    println("REFUSE raw-step ordinal={ordinal}");return 3;}}',
            f"  let mr_{local}:IvTaylorResult=ivtm_rebase_dyadic(mr0_{local}.value,160);",
            f"  let pr_{local}:IvTaylorResult=ivtm_rebase_dyadic(pr0_{local}.value,160);",
            f"  if(!mr_{local}.ok || !pr_{local}.ok){{",
            f'    println("REFUSE raw-rebase ordinal={ordinal}");return 3;}}',
            f"  mraw=ivtm_clone(mr_{local}.value);",
            f"  praw=ivtm_clone(pr_{local}.value);",
        ]
    lines += [
        "  let mstd:IvTaylorMat=pt_block_to_standard(mraw);",
        "  let pstd:IvTaylorMat=pt_block_to_standard(praw);",
    ]
    if require_rank:
        lines += [
            "  let combined:IvTaylorMat=pt_hcat(mstd,pstd);",
            "  let rm:IvTaylorRank=ivtm_full_column_rank_cells(mstd,64);",
            "  let rp:IvTaylorRank=ivtm_full_column_rank_cells(pstd,64);",
            "  let rc:IvTaylorRank=ivtm_full_column_rank_cells(combined,64);",
            '  println(strfmt(system_allocator(),"RANKS {} {} {}",',
            "    [rm.rank,rp.rank,rc.rank]));",
            "  let combined_ok:bool=rc.certified && rc.rank==12;",
            "  let minus_ok:bool=(rm.certified && rm.rank==6) || combined_ok;",
            "  let plus_ok:bool=(rp.certified && rp.rank==6) || combined_ok;",
            '  if(!minus_ok || !plus_ok || !combined_ok){',
            '    println("REFUSE terminal-raw-rank");return 3;}',
        ]
    else:
        lines += ['  println("RANKS 0 0 0");']
    lines += [
        "  let ms:String=ivtm_serialize(mstd,0);",
        "  let ps:String=ivtm_serialize(pstd,0);",
        '  println(strfmt(system_allocator(),"MINUS_RAW {}",[str_view(ms)]));',
        '  println(strfmt(system_allocator(),"PLUS_RAW {}",[str_view(ps)]));',
        "  drop(ms);drop(ps);",
        f'  println("PASS child={child} stage={stage} raw-tail");return 42;',
        "}",
        "",
    ]
    return "\n".join(lines)


def _switch_to_raw_tail(
    source: str,
    metadata: dict[str, Any],
    previous: dict[str, Any] | None,
) -> str:
    stage = metadata["stage"]
    ordinals = metadata["factor_ordinals"]
    if stage == 5:
        local = ordinals.index(212)
        marker = f"  let phi_{local}:IvTaylorMat=pt_factor_{local:03d}();"
        if source.count(marker) != 1:
            raise AmplitudeTransportError("raw crosswalk switch drift")
        prefix = source.split(marker, 1)[0]
        crosswalk = [
            f"  let phi_{local}:IvTaylorMat=pt_factor_{local:03d}();",
            "  let mbefore:IvTaylorResult=pt_reconstruct(minus);",
            "  let pbefore:IvTaylorResult=pt_reconstruct(plus);",
            "  if(!mbefore.ok || !pbefore.ok){",
            '    println("REFUSE pre-crosswalk-reconstruction");return 3;}',
            f"  let mcross0:IvTaylorResult=ivtm_mul_checked(phi_{local},mbefore.value);",
            f"  let pcross0:IvTaylorResult=ivtm_mul_checked(phi_{local},pbefore.value);",
            "  if(!mcross0.ok || !pcross0.ok){",
            '    println("REFUSE raw-crosswalk");return 3;}',
            "  let mcross:IvTaylorResult=ivtm_rebase_dyadic(mcross0.value,160);",
            "  let pcross:IvTaylorResult=ivtm_rebase_dyadic(pcross0.value,160);",
            "  if(!mcross.ok || !pcross.ok){",
            '    println("REFUSE raw-crosswalk-rebase");return 3;}',
        ]
        return prefix + "\n".join(crosswalk) + "\n" + _raw_terminal(
            child=metadata["child"],
            stage=stage,
            ordinals=ordinals,
            start_local=local + 1,
            initial_minus="mcross.value",
            initial_plus="pcross.value",
            require_rank=False,
        )
    if stage == 6:
        if previous is None or "raw_frames" not in previous:
            raise AmplitudeTransportError("raw tail continuation missing")
        builders = "\n".join(
            base._serialized_builder(
                "pt_previous_minus_raw", previous["raw_frames"]["Iminus"]
            )
            + base._serialized_builder(
                "pt_previous_plus_raw", previous["raw_frames"]["Iplus"]
            )
        )
        marker = "pub fn main()->i64{"
        if source.count(marker) != 1:
            raise AmplitudeTransportError("raw tail main replacement drift")
        prefix = source.split(marker, 1)[0] + builders + "\n" + marker + "\n"
        return prefix + _raw_terminal(
            child=metadata["child"],
            stage=stage,
            ordinals=ordinals,
            start_local=0,
            initial_minus="pt_previous_minus_raw()",
            initial_plus="pt_previous_plus_raw()",
            require_rank=False,
        )
    return source


def _q(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _restrict_linear_matrix(matrix: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(matrix)
    for row in range(len(matrix["center"])):
        for col in range(len(matrix["center"][row])):
            c0 = Fraction(matrix["center"][row][col])
            c1 = Fraction(matrix["linear"][row][col])
            out["center"][row][col] = _q(c0 + TARGET_SHIFT * c1)
            out["linear"][row][col] = _q(TARGET_SCALE * c1)
    return out


def _restrict_ivtm(model: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(model)
    c0, c1, c2 = model["coefficients"]
    for row in range(model["rows"]):
        for col in range(model["cols"]):
            a0 = Fraction(c0[row][col])
            a1 = Fraction(c1[row][col])
            a2 = Fraction(c2[row][col])
            out["coefficients"][0][row][col] = _q(
                a0 + TARGET_SHIFT * a1 + TARGET_SHIFT**2 * a2
            )
            out["coefficients"][1][row][col] = _q(
                TARGET_SCALE * a1
                + 2 * TARGET_SHIFT * TARGET_SCALE * a2
            )
            out["coefficients"][2][row][col] = _q(
                TARGET_SCALE**2 * a2
            )
    return out


def _restrict_previous(previous: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(previous)
    for name in ("Iminus", "Iplus"):
        state = out["chart_states"][name]
        state["z"] = _restrict_ivtm(state["z"])
        state["amplitude"] = _restrict_ivtm(state["amplitude"])
    return out


def _load_stage_matrices(
    child: int,
    stage: int,
    artifact_dir: Path,
    repo_root: Path,
) -> tuple[dict[str, Any], list[dict[str, Any] | None]]:
    """Load only the factors used by one stage from the pinned Phase-3 cover."""
    manifest_path = (
        artifact_dir / "infinity_plane_manifests" / f"q{child:02d}.json"
    )
    manifest = json.loads(manifest_path.read_text())
    declared = manifest.pop("payload_sha256")
    actual = base.canonical_sha256(manifest)
    manifest["payload_sha256"] = declared
    if declared != actual:
        raise AmplitudeTransportError("pinned factor manifest hash mismatch")
    steps = manifest["steps"]
    matrices: list[dict[str, Any] | None] = [None] * len(steps)
    context = base.build_microfactor_render_context()
    for ordinal in manifest["stages"][stage]["step_ordinals"]:
        step = steps[ordinal]
        if step["kind"] == "exact-prefix-to-fixed-frame-crosswalk":
            crosswalk = base.prefix_boundary_crosswalk(child, context)
            if (
                base.canonical_sha256(crosswalk)
                != step["restricted_matrix_payload_sha256"]
                or crosswalk["crosswalk_sha256"] != step["crosswalk_sha256"]
            ):
                raise AmplitudeTransportError(
                    "prefix crosswalk hash mismatch"
                )
            matrix = base.crosswalk_matrix(crosswalk)
        else:
            path = repo_root / step["source_artifact"]["path"]
            if base._file_sha256(path) != step["source_artifact"]["sha256"]:
                raise AmplitudeTransportError(
                    f"factor source hash mismatch at ordinal {ordinal}"
                )
            artifact = json.loads(path.read_text())
            matrix = artifact["matrix"]
            if step["kind"] == "restricted-prefix-factor":
                matrix = base.restrict_prefix_matrix(matrix, child)
            elif step["kind"] != "child-fixed-frame-tail-factor":
                raise AmplitudeTransportError(
                    f"unsupported factor kind {step['kind']}"
                )
        if (
            step["kind"] != "exact-prefix-to-fixed-frame-crosswalk"
            and
            base.canonical_sha256(matrix)
            != step["restricted_matrix_payload_sha256"]
        ):
            raise AmplitudeTransportError(
                f"restricted factor hash mismatch at ordinal {ordinal}"
            )
        matrix = _restrict_linear_matrix(matrix)
        matrices[ordinal] = matrix
    return manifest, matrices


def render_stage(
    *,
    child: int,
    stage: int,
    artifact_dir: Path,
    repo_root: Path,
    previous: dict[str, Any] | None,
) -> tuple[str, dict[str, Any]]:
    render_previous = previous
    if previous is not None and "render_stub" in previous:
        render_previous = copy.deepcopy(previous)
        render_previous["chart_states"] = previous["render_stub"][
            "chart_states"
        ]
        render_previous["basis_change_majorants"] = previous["render_stub"][
            "basis_change_majorants"
        ]
    if (
        render_previous is not None
        and render_previous.get("cell", {}).get("omega_interval")
        != list(TARGET_INTERVAL)
    ):
        render_previous = _restrict_previous(render_previous)
    original_loader = base._load_matrices
    base._load_matrices = lambda loaded_child, _artifact, _root: (
        _load_stage_matrices(
            loaded_child, stage, artifact_dir, repo_root
        )
    )
    try:
        source, metadata = base.render_stage(
            child=child,
            stage=stage,
            artifact_dir=artifact_dir,
            repo_root=repo_root,
            previous=render_previous,
        )
    finally:
        base._load_matrices = original_loader
    source = _retain_amplitude_source(source)
    if stage == 0:
        source = _replace_once(
            source,
            '  let child:IvTaylorCell=match(ivt_cell(7315,big("4097/8192"),\n'
            '    big("1/8192"))){some(z)=>z,none=>{trap();}};',
            '  let child:IvTaylorCell=match(ivt_cell(7315,big("20001/40000"),\n'
            '    big("1/40000"))){some(z)=>z,none=>{trap();}};',
            "target initializer cell",
        )
    source = _import_previous_amplitudes(source, render_previous)
    source = _emit_amplitudes(source)
    if 212 in metadata["factor_ordinals"]:
        local = metadata["factor_ordinals"].index(212)
        source = _replace_once(
            source,
            f"  let mn_{local}:PtState=pt_step_any(phi_{local},minus);",
            f"  let mn_{local}:PtState=pt_step_chart(phi_{local},minus,9);",
            "crosswalk minus chart",
        )
        source = _replace_once(
            source,
            f"  let pn_{local}:PtState=pt_step_any(phi_{local},plus);",
            f"  let pn_{local}:PtState=pt_step_chart(phi_{local},plus,18);",
            "crosswalk plus chart",
        )
    if stage >= 5:
        source = _switch_to_raw_tail(source, metadata, previous)
    metadata = dict(metadata)
    metadata["schema"] = SCHEMA
    if stage == 5 and previous is not None:
        metadata["_render_stub"] = {
            "chart_states": previous["chart_states"],
            "basis_change_majorants": previous["basis_change_majorants"],
        }
    metadata["cell"] = {
        "omega_interval": list(TARGET_INTERVAL),
        "parent_child": 0,
        "parent_epsilon_shift": _q(TARGET_SHIFT),
        "parent_epsilon_scale": _q(TARGET_SCALE),
    }
    metadata["frequency_restriction"] = {
        "source_cell": ["1/2", "2049/4096"],
        "target_cell": list(TARGET_INTERVAL),
        "exact_affine_map": (
            "epsilon_parent=-497/625+(128/625) epsilon_target"
        ),
        "remainder_policy": "inherited unchanged from certified parent",
    }
    metadata["plane_representation"] = {
        "kind": "amplitude-preserving-grassmann-cocycle",
        "identity": "Y=G_chart(Z) A",
        "amplitude_update": {
            "propagation": "A_next=(Phi_II+Phi_IJ Z) A",
            "rechart": "A_next=U_new G_old(Z) A",
        },
        "preserves": [
            "original infinity endpoint normalization",
            "propagated incoming and outgoing frames",
            "propagated subspaces",
            "separate and combined rank",
        ],
    }
    metadata["source_sha256"] = hashlib.sha256(source.encode()).hexdigest()
    return source, metadata


def _parse_amplitudes(stdout: str) -> dict[str, dict[str, Any]]:
    parsed: dict[str, dict[str, Any]] = {}
    for line in stdout.splitlines():
        if line.startswith("MINUS_A "):
            parsed["Iminus"] = _parse_ivtm(line[8:])
        elif line.startswith("PLUS_A "):
            parsed["Iplus"] = _parse_ivtm(line[7:])
    if set(parsed) != {"Iminus", "Iplus"}:
        raise AmplitudeTransportError("stage output lacks amplitude records")
    return parsed


def _parse_ivtm(text: str) -> dict[str, Any]:
    import re

    quoted = re.sub(
        r'(?<![0-9A-Za-z_"])(-?[0-9]+/[0-9]+)(?![0-9A-Za-z_"])',
        r'"\1"',
        text,
    )
    return json.loads(quoted)


def stage_payload(
    *,
    metadata: dict[str, Any],
    stdout: str,
    source: Path,
    log: Path,
    exit_code: int,
) -> dict[str, Any]:
    if "MINUS_RAW " in stdout:
        raw: dict[str, Any] = {}
        ranks = {"Iminus": 0, "Iplus": 0, "combined": 0}
        for line in stdout.splitlines():
            if line.startswith("MINUS_RAW "):
                raw["Iminus"] = _parse_ivtm(line[10:])
            elif line.startswith("PLUS_RAW "):
                raw["Iplus"] = _parse_ivtm(line[9:])
            elif line.startswith("RANKS "):
                values = [int(value) for value in line.split()[1:]]
                ranks = dict(zip(("Iminus", "Iplus", "combined"), values))
        if set(raw) != {"Iminus", "Iplus"}:
            raise AmplitudeTransportError("raw tail output incomplete")
        final = metadata["stage"] == 6
        rank_certified = (
            ranks == {"Iminus": 6, "Iplus": 6, "combined": 12}
        )
        payload = {
            "schema": SCHEMA,
            "status": (
                "CERTIFIED_INFINITY_FRAME_AT_R4"
                if final and rank_certified
                else (
                    "VALIDATED_INFINITY_FRAME_ENCLOSURE_AT_R4"
                    if final else "VALIDATED_RAW_TAIL_CHECKPOINT"
                )
            ),
            **metadata,
            "representation": "physical-frame-ivtaylor-after-crosswalk",
            "raw_frames": raw,
            "terminal_ranks": ranks,
            "terminal_rank_certified": rank_certified,
            "execution": {
                "backend": "c",
                "exit_code": exit_code,
                "stdout_sha256": hashlib.sha256(stdout.encode()).hexdigest(),
            },
            "does_not_establish": [
                "horizon-to-infinity matching",
                "the outgoing connection T_plus",
                "flux positivity, stability, CPT, or unitarity",
            ],
        }
        if not final:
            # Render-only stub; it is not asserted to represent the state
            # after the crosswalk and is never consumed by mathematics.
            payload["render_stub"] = metadata["_render_stub"]
        payload.pop("_render_stub", None)
        payload["payload_sha256"] = base.canonical_sha256(payload)
        return payload
    payload = base.stage_payload(
        metadata=metadata,
        stdout=stdout,
        source=source,
        log=log,
        exit_code=exit_code,
    )
    amplitudes = _parse_amplitudes(stdout)
    for name, amplitude in amplitudes.items():
        payload["chart_states"][name]["amplitude"] = amplitude
    payload["schema"] = SCHEMA
    payload["basis_change_proof"]["does_not_establish"] = (
        "horizon matching or the physical connection before the independent "
        "horizon frame is supplied"
    )
    payload["does_not_establish"] = [
        "horizon-to-infinity matching",
        "endpoint current or flux conservation",
        "a completed connection or scattering matrix",
        "stability, positivity, CPT, or unitarity",
    ]
    payload.pop("payload_sha256", None)
    payload["payload_sha256"] = base.canonical_sha256(payload)
    return payload


def run_stage(
    *,
    child: int,
    stage: int,
    artifact_dir: Path,
    repo_root: Path,
    previous: dict[str, Any] | None,
    scratch: Path,
    output: Path,
    compile_timeout: float = 900,
    run_timeout: float = 900,
) -> dict[str, Any]:
    source_text, metadata = render_stage(
        child=child,
        stage=stage,
        artifact_dir=artifact_dir,
        repo_root=repo_root,
        previous=previous,
    )
    scratch.mkdir(parents=True, exist_ok=True)
    source = scratch / f"q{child:02d}-stage{stage}.forge"
    binary = scratch / f"q{child:02d}-stage{stage}"
    log = scratch / f"q{child:02d}-stage{stage}.log"
    source.write_text(source_text)
    compiled = subprocess.run(
        ["forge", "-o", str(binary), str(source)],
        text=True,
        capture_output=True,
        timeout=compile_timeout,
        check=False,
    )
    if compiled.returncode:
        raise AmplitudeTransportError(
            f"Forge compile refused stage {stage}: {compiled.stderr[-4000:]}"
        )
    ran = subprocess.run(
        [str(binary)],
        text=True,
        capture_output=True,
        timeout=run_timeout,
        check=False,
    )
    log.write_text(ran.stdout + ran.stderr)
    if ran.returncode != 42:
        raise AmplitudeTransportError(
            f"Forge run refused stage {stage} with {ran.returncode}: "
            f"{ran.stdout[-4000:]}{ran.stderr[-4000:]}"
        )
    payload = stage_payload(
        metadata=metadata,
        stdout=ran.stdout,
        source=source,
        log=log,
        exit_code=ran.returncode,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--child", type=int, default=0)
    parser.add_argument("--stage", type=int, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--previous", type=Path)
    parser.add_argument("--scratch", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    previous = json.loads(args.previous.read_text()) if args.previous else None
    payload = run_stage(
        child=args.child,
        stage=args.stage,
        artifact_dir=args.artifact_dir,
        repo_root=args.repo_root,
        previous=previous,
        scratch=args.scratch,
        output=args.output,
    )
    print(
        f"PASS child={payload['child']} stage={payload['stage']} "
        f"payload={payload['payload_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
