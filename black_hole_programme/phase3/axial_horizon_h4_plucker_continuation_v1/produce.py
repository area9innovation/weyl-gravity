#!/usr/bin/env python3
"""Render exact-state Plücker continuation chunks and their joins."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PREDECESSOR = (
    HERE.parent / "axial_horizon_h4_plucker_v1"
)
PREDECESSOR_CERTIFICATE = PREDECESSOR / "certificate.json"
PREDECESSOR_SOURCE = PREDECESSOR / "plucker_q00_preflight.forge"
PREDECESSOR_LOG = PREDECESSOR / "plucker_q00_preflight_run.txt"

EXPECTED_PREDECESSOR_CERTIFICATE_SHA256 = (
    "230173e50fed0933530ae43c6033bb0b2e4e667ae190224bf33a63a3d7cfb857"
)
EXPECTED_PREDECESSOR_SOURCE_SHA256 = (
    "703e75a73ec5c3fb3d698727d2acb551661da96ffde82b9e61572a012f972559"
)
GENERATOR = 7315
ROWS = 40

EXPORTER_SOURCE = HERE / "boundary_exporter.forge"
EXPORTER_LOG = HERE / "boundary_exporter_run.txt"
STATE_DIR = HERE / "states"
CHUNK_DIR = HERE / "chunks"
MANIFEST = HERE / "join_manifest.json"

CHUNKS = (
    {
        "label": "shell3_tail",
        "segments": ((3, 1), (3, 2), (3, 3)),
        "output_position": {"shell": 3, "segment": 3},
    },
    {
        "label": "shell4",
        "segments": ((4, 0), (4, 1), (4, 2), (4, 3)),
        "output_position": {"shell": 4, "segment": 3},
    },
    {
        "label": "shell5",
        "segments": ((5, 0), (5, 1), (5, 2), (5, 3)),
        "output_position": {"shell": 5, "segment": 3},
    },
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def checked_predecessor() -> tuple[dict, str]:
    if sha256(PREDECESSOR_CERTIFICATE) != (
        EXPECTED_PREDECESSOR_CERTIFICATE_SHA256
    ):
        raise RuntimeError("predecessor certificate hash drift")
    certificate = json.loads(PREDECESSOR_CERTIFICATE.read_text())
    if certificate.get("status") != "CERTIFIED":
        raise RuntimeError("predecessor is not certified")
    source = PREDECESSOR_SOURCE.read_text()
    if hashlib.sha256(source.encode()).hexdigest() != (
        EXPECTED_PREDECESSOR_SOURCE_SHA256
    ):
        raise RuntimeError("predecessor source hash drift")
    if certificate["hashes"]["plucker_q00_preflight.forge"] != (
        EXPECTED_PREDECESSOR_SOURCE_SHA256
    ):
        raise RuntimeError("certificate/source binding drift")
    return certificate, source


def support_prefix() -> str:
    _, source = checked_predecessor()
    marker = "pub fn main()->i64{"
    if source.count(marker) != 1:
        raise RuntimeError("predecessor main marker drift")
    return source.split(marker, 1)[0]


EMITTER = r'''
fn pl_emit_shared_state(a:borrow IvTaylor4Mat)->void{
  if(a.rows!=40 || a.cols!=1){println("PLSTATE_BAD_SHAPE");return;}
  let row:i64=0;while(row<40){
    let c0:String=rat_str(qm_get(a.c0,row,0));
    let c1:String=rat_str(qm_get(a.c1,row,0));
    let c2:String=rat_str(qm_get(a.c2,row,0));
    let c3:String=rat_str(qm_get(a.c3,row,0));
    let c4:String=rat_str(qm_get(a.c4,row,0));
    let rem:Iv=ivm_at(a.remainder,row,0);
    println(strfmt(system_allocator(),
      "PLSTATE row={} c0={} c1={} c2={} c3={} c4={} rlo={} rhi={}",
      [row,str_view(c0),str_view(c1),str_view(c2),str_view(c3),
       str_view(c4),f64_bits(rem.lo),f64_bits(rem.hi)]));
    drop(c0);drop(c1);drop(c2);drop(c3);drop(c4);row=row+1;
  }
}
'''


def render_exporter() -> str:
    _, predecessor = checked_predecessor()
    call_marker = (
        '  println(strfmt(system_allocator(),"PLUCKER_RESULT pivot={} '
    )
    if predecessor.count(call_marker) != 1:
        raise RuntimeError("predecessor result marker drift")
    instrumented = predecessor.replace(
        "pub fn main()->i64{",
        EMITTER + "\npub fn main()->i64{",
        1,
    )
    return instrumented.replace(
        call_marker,
        "  pl_emit_shared_state(state.value);\n" + call_marker,
        1,
    )


STATE_RE = re.compile(
    r"^PLSTATE row=(\d+) c0=([^ ]+) c1=([^ ]+) c2=([^ ]+) "
    r"c3=([^ ]+) c4=([^ ]+) rlo=(-?\d+) rhi=(-?\d+)$",
    flags=re.MULTILINE,
)


def parse_state_lines(text: str) -> list[dict]:
    matches = STATE_RE.findall(text)
    if len(matches) != ROWS:
        raise RuntimeError(f"expected {ROWS} state rows, got {len(matches)}")
    rows = []
    for expected, match in enumerate(matches):
        row, *values = match
        if int(row) != expected:
            raise RuntimeError("state row order drift")
        coefficients = values[:5]
        for value in coefficients:
            Fraction(value)
        lo_bits, hi_bits = (int(values[5]), int(values[6]))
        lo = struct.unpack(">d", struct.pack(">q", lo_bits))[0]
        hi = struct.unpack(">d", struct.pack(">q", hi_bits))[0]
        if not lo <= hi:
            raise RuntimeError("invalid remainder interval")
        rows.append(
            {
                "row": expected,
                "coefficients": coefficients,
                "remainder_bits": [lo_bits, hi_bits],
            }
        )
    return rows


def state_path(position: dict) -> Path:
    return STATE_DIR / (
        f"boundary_shell{position['shell']}_segment"
        f"{position['segment']}.json"
    )


def write_state(
    log: Path,
    source: Path,
    position: dict,
    output: Path,
    input_state_sha256: str | None,
) -> dict:
    payload = {
        "schema": "phase3-axial-h4-plucker-shared-state-v1",
        "status": "CERTIFIED_ENCLOSURE_HANDOFF",
        "frequency_cell": ["1/2", "2049/4096"],
        "shared_parameter_generator": GENERATOR,
        "typed_layout": "Re(20),Im(20)",
        "position": position,
        "rows": parse_state_lines(log.read_text()),
        "producer_source_sha256": sha256(source),
        "producer_log_sha256": sha256(log),
        "input_state_sha256": input_state_sha256,
        "predecessor_certificate_sha256": (
            EXPECTED_PREDECESSOR_CERTIFICATE_SHA256
        ),
    }
    payload["payload_sha256"] = canonical_hash(payload)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return payload


def render_state_builder(state: dict) -> str:
    lines = [
        "fn pl_shared_initial()->IvTaylor4Mat{",
        "  let c0:QMat=qm_new(40,1);let c1:QMat=qm_new(40,1);",
        "  let c2:QMat=qm_new(40,1);let c3:QMat=qm_new(40,1);",
        "  let c4:QMat=qm_new(40,1);let rem:IvMat=ivm_zeros(40,1);",
    ]
    for record in state["rows"]:
        row = record["row"]
        for degree, value in enumerate(record["coefficients"]):
            lines.append(
                f'  c{degree}=qm_set(c{degree},{row},0,big("{value}"));'
            )
        lo_bits, hi_bits = record["remainder_bits"]
        lines.append(
            f"  ivm_set(rem,{row},0,iv(f64_from_bits({lo_bits}),"
            f"f64_from_bits({hi_bits})));"
        )
    lines += [
        "  let made:IvTaylor4Result=ivtm4_new(",
        "    7315,c0,c1,c2,c3,c4,rem);",
        "  if(!made.ok){trap();}return ivtm4_clone(made.value);",
        "}",
        "",
    ]
    return "\n".join(lines)


def render_chunk_main(
    label: str,
    segments: tuple[tuple[int, int], ...],
    input_hash: str,
) -> str:
    lines = [
        "pub fn main()->i64{",
        "  let cell:IvAffineCell=hr_cell();",
        "  let initial:IvTaylor4Mat=pl_shared_initial();",
        "  let initial_pivot:PlPivot=pl_pivot(initial);",
        '  if(!initial_pivot.ok){println("PLCHUNK_REFUSE '
        'stage=input-pivot code=32");return 3;}',
        "  let state:PlState=new PlState(true,ivtm4_clone(initial),",
        "    initial_pivot.index,initial_pivot.margin,initial_pivot.norm,",
        "    0,IVTAY_OK);",
        "  let input_rel:PlCheck=pl_relations(state.value);",
        '  if(!input_rel.ok){println(strfmt(system_allocator(),'
        '"PLCHUNK_REFUSE stage=input-relations code={}",'
        "[input_rel.refusal_code]));return 3;}",
        f'  println("PLCHUNK_BEGIN label={label} '
        f'input_state_sha256={input_hash} '
        f'predecessor_certificate_sha256='
        f'{EXPECTED_PREDECESSOR_CERTIFICATE_SHA256}");',
    ]
    for index, (shell, segment) in enumerate(segments):
        lines += [
            f"  let next_{index}:PlState=pl_attempt("
            f"{shell},{segment},cell,state);",
            f"  if(!next_{index}.ok){{println(strfmt("
            f'system_allocator(),"PLCHUNK_REFUSE shell={shell} '
            f'segment={segment} code={{}}",'
            f"[next_{index}.refusal_code]));return 3;}}",
            f"  state=new PlState(true,ivtm4_clone(next_{index}.value),"
            f"next_{index}.pivot,next_{index}.margin,next_{index}.norm,"
            f"next_{index}.scale_exponent,IVTAY_OK);",
            f"  let rel_{index}:PlCheck=pl_relations(state.value);",
            f"  if(!rel_{index}.ok){{println(strfmt("
            f'system_allocator(),"PLCHUNK_REFUSE shell={shell} '
            f'segment={segment} relations code={{}}",'
            f"[rel_{index}.refusal_code]));return 3;}}",
            f'  println(strfmt(system_allocator(),"PLCHUNK_SEGMENT '
            f'shell={shell} segment={segment} pivot={{}} margin={{}} '
            'norm={} relations=45",[state.pivot,state.margin,state.norm]));',
        ]
    final_shell, final_segment = segments[-1]
    lines += [
        "  pl_emit_shared_state(state.value);",
        f'  println("PLCHUNK_PASS label={label} reached_shell='
        f'{final_shell} reached_segment={final_segment} '
        'rank_witness=true parameter_correlation=true");',
        "  return 42;",
        "}",
        "",
    ]
    return "\n".join(lines)


def render_chunk(
    state: dict,
    label: str,
    segments: tuple[tuple[int, int], ...],
) -> str:
    if state["payload_sha256"] != canonical_hash(
        {key: value for key, value in state.items()
         if key != "payload_sha256"}
    ):
        raise RuntimeError("input state payload hash drift")
    return (
        support_prefix()
        + EMITTER
        + render_state_builder(state)
        + render_chunk_main(label, segments, state["payload_sha256"])
    )


def write_chunk_source(
    state_path_value: Path,
    label: str,
    segments: tuple[tuple[int, int], ...],
) -> tuple[Path, Path]:
    state = json.loads(state_path_value.read_text())
    source = render_chunk(state, label, segments)
    source_path = CHUNK_DIR / f"{label}.forge"
    metadata_path = CHUNK_DIR / f"{label}_metadata.json"
    metadata = {
        "schema": "phase3-axial-h4-plucker-chunk-source-v1",
        "status": "RENDERED_NOT_YET_VERIFIED",
        "label": label,
        "segments": [list(value) for value in segments],
        "input_state_path": str(state_path_value.relative_to(HERE)),
        "input_state_sha256": state["payload_sha256"],
        "predecessor_certificate_sha256": (
            EXPECTED_PREDECESSOR_CERTIFICATE_SHA256
        ),
        "predecessor_source_sha256": EXPECTED_PREDECESSOR_SOURCE_SHA256,
        "support_prefix_sha256": hashlib.sha256(
            support_prefix().encode()
        ).hexdigest(),
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "typed_layout": "Re(20),Im(20)",
        "does_not_establish": [
            "the complete 23-shell horizon transport",
            "canonical endpoint amplitudes",
            "a horizon-to-infinity scattering theorem",
        ],
    }
    CHUNK_DIR.mkdir(parents=True, exist_ok=True)
    source_path.write_text(source)
    metadata_path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n"
    )
    return source_path, metadata_path


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("export-source")
    state_parser = sub.add_parser("state-from-log")
    state_parser.add_argument("log", type=Path)
    state_parser.add_argument("source", type=Path)
    state_parser.add_argument("shell", type=int)
    state_parser.add_argument("segment", type=int)
    state_parser.add_argument("output", type=Path)
    state_parser.add_argument("--input-state-sha256")
    chunk_parser = sub.add_parser("chunk-source")
    chunk_parser.add_argument("state", type=Path)
    chunk_parser.add_argument("label")
    chunk_parser.add_argument("segments", nargs="+")
    args = parser.parse_args()

    if args.command == "export-source":
        HERE.mkdir(parents=True, exist_ok=True)
        source = render_exporter()
        EXPORTER_SOURCE.write_text(source)
        print(hashlib.sha256(source.encode()).hexdigest())
    elif args.command == "state-from-log":
        payload = write_state(
            args.log,
            args.source,
            {"shell": args.shell, "segment": args.segment},
            args.output,
            args.input_state_sha256,
        )
        print(payload["payload_sha256"])
    else:
        segments = tuple(
            tuple(int(value) for value in item.split(":"))
            for item in args.segments
        )
        source, metadata = write_chunk_source(
            args.state, args.label, segments
        )
        print(source)
        print(metadata)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
