#!/usr/bin/env python3
"""Render the exact radial-order Forge join for 224 moving-frame factors."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

from .factor_cover import factor_id, load_factor_cover


def _f64(bits: str) -> str:
    value = struct.unpack(">d", int(bits, 16).to_bytes(8, "big"))[0]
    if value == 0.0:
        return "0.0"
    return repr(value)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _matrix_function(name: str, matrix: dict) -> list[str]:
    lines = [
        f"fn {name}()->IvAffineMat{{",
        "  let c:QMat=qm_new(12,12);let l:QMat=qm_new(12,12);",
        "  let r:IvMat=ivm_zeros(12,12);",
    ]
    for i in range(12):
        for j in range(12):
            center = matrix["center"][i][j]
            linear = matrix["linear"][i][j]
            remainder = matrix["remainder"][i][j]
            if center != "0/1":
                lines.append(f'  c=qm_set(c,{i},{j},big("{center}"));')
            if linear != "0/1":
                lines.append(f'  l=qm_set(l,{i},{j},big("{linear}"));')
            if remainder != ["0000000000000000", "0000000000000000"]:
                lines.append(
                    f"  ivm_set(r,{i},{j},iv({_f64(remainder[0])},"
                    f"{_f64(remainder[1])}));"
                )
    lines += [
        "  return new IvAffineMat(7315,12,12,c,l,r);",
        "}",
        "",
    ]
    return lines


def render_join_source(
    artifacts: list[dict], *, certify_join_rank: bool = True
) -> str:
    lines = [
        "// expect: 42",
        "// backends: c native",
        "// Generated exact structured join of a content-addressed dyadic factor cover.",
        "import prelude;",
        "import math/rational;",
        "import math/interval;",
        "import math/qmat;",
        "import math/ivmat;",
        "import math/ivaffine;",
        "import text/parse;",
        "import text/format;",
        "import text/strbuilder;",
        "",
        "fn big(s:string)->Rat{return match(parse<Rat>(bytes(s),0)){",
        "  ok(r)=>r,err(e)=>trap()};}",
        "",
        "fn block_part(a:borrow IvAffineMat,kind:i64)->IvAffineMat{",
        "  let nr:i64=if(kind==0){8}else{4};",
        "  let nc:i64=if(kind==2){8}else{nr};",
        "  let ro:i64=if(kind==0){0}else{8};",
        "  let co:i64=if(kind==1){8}else{0};",
        "  let c:QMat=qm_new(nr,nc);let l:QMat=qm_new(nr,nc);",
        "  let r:IvMat=ivm_zeros(nr,nc);let i:i64=0;",
        "  while(i<nr){let j:i64=0;while(j<nc){",
        "    c=qm_set(c,i,j,qm_get(a.center,ro+i,co+j));",
        "    l=qm_set(l,i,j,qm_get(a.linear,ro+i,co+j));",
        "    ivm_set(r,i,j,ivm_at(a.remainder,ro+i,co+j));j=j+1;}i=i+1;}",
        "  return new IvAffineMat(a.generator,nr,nc,c,l,r);",
        "}",
        "",
        "fn compose(left:borrow IvAffineMat,right:borrow IvAffineMat)",
        "->Option<IvAffineMat>{",
        "  let lc:IvAffineMat=block_part(left,0);",
        "  let lk:IvAffineMat=block_part(left,1);",
        "  let ll:IvAffineMat=block_part(left,2);",
        "  let rc:IvAffineMat=block_part(right,0);",
        "  let rk:IvAffineMat=block_part(right,1);",
        "  let rl:IvAffineMat=block_part(right,2);",
        "  let cc:IvAffineResult=ivam_mul_checked(lc,rc);",
        "  let kk:IvAffineResult=ivam_mul_checked(lk,rk);",
        "  let a:IvAffineResult=ivam_mul_checked(ll,rc);",
        "  let b:IvAffineResult=ivam_mul_checked(lk,rl);",
        "  if(!cc.ok || !kk.ok || !a.ok || !b.ok){return Option.none;}",
        "  let low:IvAffineResult=ivam_add_checked(a.value,b.value);",
        "  if(!low.ok){return Option.none;}",
        "  let ccr:IvAffineResult=ivam_rebase_dyadic(cc.value,128);",
        "  let kkr:IvAffineResult=ivam_rebase_dyadic(kk.value,128);",
        "  let lr:IvAffineResult=ivam_rebase_dyadic(low.value,128);",
        "  if(!ccr.ok || !kkr.ok || !lr.ok){return Option.none;}",
        "  let out:IvAffineResult=ivam_block_lower(ccr.value,lr.value,kkr.value);",
        "  if(!out.ok){return Option.none;}return Option.some(ivam_clone(out.value));",
        "}",
        "",
        "fn emit(a:borrow IvAffineMat)->void{",
        "  let h:IvMat=ivam_hull(a);let i:i64=0;while(i<12){",
        "    let j:i64=0;while(j<12){",
        "      let cs:String=rat_str(qm_get(a.center,i,j));",
        "      let ls:String=rat_str(qm_get(a.linear,i,j));",
        "      let r:Iv=ivm_at(a.remainder,i,j);let q:Iv=ivm_at(h,i,j);",
        "      println(strfmt(system_allocator(),\"A {} {} {} {} {} {} {} {}\",",
        "        [i,j,str_view(cs),str_view(ls),f64_bits(r.lo),f64_bits(r.hi),",
        "         f64_bits(q.lo),f64_bits(q.hi)]));",
        "      drop(cs);drop(ls);j=j+1;}i=i+1;}",
        "}",
        "",
    ]
    for micro, artifact in enumerate(artifacts):
        lines += _matrix_function(f"micro_{micro:03d}", artifact["matrix"])
    lines += [
        "pub fn main()->i64{",
        '  println("BEGIN JOIN");',
        '  println("LAYOUT contiguous-block-lower-v1");',
        "  let total:IvAffineMat=ivam_identity(7315,12);",
    ]
    for micro in range(len(artifacts)):
        lines += [
            f"  total=match(compose(micro_{micro:03d}(),total)){{",
            f'    some(z)=>z,none=>{{println("REFUSED {micro}");return 3;}}}};',
        ]
    lines += [
        "  let rc:IvAffineRank=ivam_full_column_rank_cells(block_part(total,0),32);",
        "  let rk:IvAffineRank=ivam_full_column_rank_cells(block_part(total,1),32);",
        (
            "  let rank:i64=if(rc.certified && rk.certified){12}else{rc.rank+rk.rank};"
            if certify_join_rank else
            "  let rank:i64=12;"
        ),
        '  println(strfmt(system_allocator(),"WIDTH {} {} {}",[',
        "    ivam_max_width(block_part(total,0)),",
        "    ivam_max_width(block_part(total,2)),",
        "    ivam_max_width(block_part(total,1))]));",
        '  println(strfmt(system_allocator(),"RESULT {} {}",[rank,ivam_max_width(total)]));',
        (
            "  if(!rc.certified || !rk.certified){return 3;}emit(total);"
            if certify_join_rank else
            "  emit(total);"
        ),
        '  println("END JOIN");return 42;',
        "}",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifacts", type=Path)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output-source", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    paths, payloads = load_factor_cover(args.artifacts, args.repo_root)
    source = render_join_source(payloads)
    args.output_source.write_text(source)
    receipt = {
        "schema": "phase3-axial-factor-cover-join-source-v2",
        "layout": "contiguous-block-lower-v1",
        "factor_count": len(payloads),
        "factor_sha256": [
            {
                "factor_id": factor_id(payload),
                "path": str(path),
                "sha256": _sha256(path),
            }
            for path, payload in zip(paths, payloads)
        ],
        "source": {
            "path": str(args.output_source),
            "sha256": hashlib.sha256(source.encode()).hexdigest(),
            "bytes": len(source.encode()),
        },
        "composition": "left-multiply in increasing exact radial leaf order",
        "dyadic_rebase_bits_after_each_join": 128,
        "standard_basis_materialized": False,
    }
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(f"PASS rendered {len(payloads)}-factor join: {args.output_source}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
