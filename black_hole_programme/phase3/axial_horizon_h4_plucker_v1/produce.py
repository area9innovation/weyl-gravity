#!/usr/bin/env python3
"""Render a bounded q00 Λ^3(C^6) future-horizon transport preflight.

The predecessor represents a complex three-plane by Grassmann graph
coordinates and repeatedly solves chart denominators.  This disjoint
successor instead propagates its 20 complex Pluecker coordinates under the
exact induced exterior-cube action.  It stops after shell 3, segment 0: the
first boundary that the historical graph rail did not certify.
"""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from fractions import Fraction
from itertools import combinations
from pathlib import Path

import sympy as sp

from black_hole_programme.phase3.axial_horizon_grassmann_mobius_to_r4 import (
    produce as affine,
)
from black_hole_programme.phase3.axial_horizon_grassmann_mobius_to_r4_taylor2 import (
    plane,
)
from black_hole_programme.phase3.axial_horizon_grassmann_mobius_to_r4_taylor2 import (
    produce as taylor2,
)
from black_hole_programme.phase3.axial_horizon_h4_resume_v1 import (
    produce as resume,
)

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "plucker_q00_preflight.forge"
METADATA = HERE / "source_metadata.json"

CELL = affine.CELLS[0]
GENERATOR = 7315
PANELS_PER_SHELL = 128
SEGMENTS_PER_SHELL = 4
TAYLOR_ORDER = 12
TRIPLES = tuple(combinations(range(6), 3))
TRIPLE_INDEX = {triple: index for index, triple in enumerate(TRIPLES)}
# hc_runtime is standard-realified Re(6),Im(6).  The initializer alone is
# converted to the predecessor's block layout before pl_centry reads it.
REAL_ROW = (0, 1, 2, 3, 4, 5)
IMAG_ROW = (6, 7, 8, 9, 10, 11)
TARGET_SEGMENTS = tuple(
    (shell, segment)
    for shell in range(4)
    for segment in range(4 if shell < 3 else 1)
)


def rational_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def permutation_sign(values: tuple[int, ...]) -> int:
    if len(set(values)) != len(values):
        return 0
    inversions = sum(
        values[left] > values[right]
        for left in range(len(values))
        for right in range(left + 1, len(values))
    )
    return -1 if inversions % 2 else 1


def induced_contributions() -> dict[
    tuple[int, int], tuple[tuple[int, int, int], ...]
]:
    """Return B=A^[3] as signed source entries of the complex 6x6 A."""
    result: dict[tuple[int, int], dict[tuple[int, int], int]] = {}
    for col, source_triple in enumerate(TRIPLES):
        for position, old_row in enumerate(source_triple):
            for new_row in range(6):
                replaced = list(source_triple)
                replaced[position] = new_row
                sign = permutation_sign(tuple(replaced))
                if not sign:
                    continue
                row = TRIPLE_INDEX[tuple(sorted(replaced))]
                entries = result.setdefault((row, col), defaultdict(int))
                entries[(new_row, old_row)] += sign
    return {
        key: tuple(
            (source_row, source_col, coefficient)
            for (source_row, source_col), coefficient
            in sorted(entries.items())
            if coefficient
        )
        for key, entries in sorted(result.items())
    }


def plucker_relations() -> tuple[
    tuple[tuple[tuple[int, int], int], ...], ...
]:
    """Return the 45 distinct quadratic Gr(3,6) Pluecker relations."""
    relations: set[tuple[tuple[tuple[int, int], int], ...]] = set()
    for left in combinations(range(6), 2):
        for right in combinations(range(6), 4):
            terms: dict[tuple[int, int], int] = defaultdict(int)
            for position, item in enumerate(right):
                first = left + (item,)
                sign = permutation_sign(first)
                if not sign:
                    continue
                first_index = TRIPLE_INDEX[tuple(sorted(first))]
                second_index = TRIPLE_INDEX[
                    tuple(value for value in right if value != item)
                ]
                pair = tuple(sorted((first_index, second_index)))
                terms[pair] += (-1) ** (position + 1) * sign
            normalized = tuple(
                (pair, coefficient)
                for pair, coefficient in sorted(terms.items())
                if coefficient
            )
            if not normalized:
                continue
            if normalized[0][1] < 0:
                normalized = tuple(
                    (pair, -coefficient)
                    for pair, coefficient in normalized
                )
            relations.add(normalized)
    output = tuple(sorted(relations))
    if len(output) != 45:
        raise RuntimeError("Gr(3,6) relation inventory drift")
    return output


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def induced_inventory() -> list:
    return [
        {
            "row": row,
            "col": col,
            "terms": [list(term) for term in terms],
        }
        for (row, col), terms in induced_contributions().items()
    ]


def relation_inventory() -> list:
    return [
        [
            {"pair": list(pair), "coefficient": coefficient}
            for pair, coefficient in relation
        ]
        for relation in plucker_relations()
    ]


def relation_span_rank() -> int:
    relations = plucker_relations()
    monomials = sorted({
        pair for relation in relations for pair, _ in relation
    })
    columns = {monomial: index for index, monomial in enumerate(monomials)}
    matrix = sp.zeros(len(relations), len(monomials))
    for row, relation in enumerate(relations):
        for pair, coefficient in relation:
            matrix[row, columns[pair]] = coefficient
    return int(matrix.rank())


def induced_matrix(matrix: sp.Matrix) -> sp.Matrix:
    if matrix.shape != (6, 6):
        raise ValueError("exterior generator input must be 6x6")
    output = sp.zeros(20, 20)
    for (row, col), terms in induced_contributions().items():
        output[row, col] = sum(
            coefficient * matrix[source_row, source_col]
            for source_row, source_col, coefficient in terms
        )
    return output


def plucker_coordinates(matrix: sp.Matrix) -> sp.Matrix:
    if matrix.shape != (6, 3):
        raise ValueError("wedge input must be 6x3")
    return sp.Matrix([
        matrix.extract(triple, range(3)).det() for triple in TRIPLES
    ])


def projective_scale_exponent(norm: float) -> int:
    if not norm > 0:
        raise ValueError("projective norm must be positive")
    exponent = 0
    while norm > 1.0:
        norm /= 2.0
        exponent += 1
    while norm < 0.5:
        norm *= 2.0
        exponent -= 1
    return exponent


def _base_prefix() -> str:
    """Rebuild the exact q00 initializer/coefficient prefix without a pilot."""
    original_cells = affine.CELLS
    try:
        affine.CELLS = (CELL,)
        fresh_affine = affine.render(0)
        frozen_prefix = fresh_affine.split("pub type HrSolve", 1)[0].replace(
            "import math/ivaffine;",
            "import math/ivaffine;\nimport math/ivtaylor;",
        )
        center = (CELL[0] + CELL[1]) / 2
        radius = (CELL[1] - CELL[0]) / 2
        cell = f"""
fn hr_cell()->IvAffineCell{{
  return match(iva_cell({GENERATOR},{affine.rat(center)},
    {affine.rat(radius)})){{
    some(z)=>z,none=>{{trap();}}}};
}}
"""
        taylor_source = (
            frozen_prefix
            + taylor2.taylor_common()
            + affine.dispatch()
            + cell
            + taylor2.taylor_run()
        )
        run_marker = "fn hr_run(q:i64)->bool"
        source = taylor_source.split(run_marker, 1)[0] + plane.PLANE
    finally:
        affine.CELLS = original_cells
    marker = "pub fn main()->i64{"
    prefix = resume._degree4_prefix(source.split(marker, 1)[0])
    return prefix.split("pub type HpState", 1)[0]


def _signed_rat(source: str, sign: int) -> str:
    return (
        f"rat_clone({source})"
        if sign > 0
        else f"(rat(0,1)-rat_clone({source}))"
    )


def _signed_iv(source: str, sign: int) -> str:
    return source if sign > 0 else f"iv_neg({source})"


def render_induced_builder() -> str:
    """Generate the exact linear realification of A^[3]."""
    flattened = []
    for (row, col), entries in induced_contributions().items():
        for source_row, source_col, sign in entries:
            real_source = (REAL_ROW[source_row], REAL_ROW[source_col])
            imag_source = (IMAG_ROW[source_row], REAL_ROW[source_col])
            flattened.extend(
                (
                    (row, col, *real_source, sign),
                    (row + 20, col + 20, *real_source, sign),
                    (row + 20, col, *imag_source, sign),
                    (row, col + 20, *imag_source, -sign),
                )
            )
    lines = [
        "pub type PlTerm = value struct {",
        "  pub dest_row:i64,pub dest_col:i64,",
        "  pub source_row:i64,pub source_col:i64,pub sign:i64,",
        "};",
        "",
        "fn pl_term(index:i64)->PlTerm{",
        "  return match(index){",
    ]
    lines.extend(
        f"    {index}=>PlTerm({dest_row},{dest_col},"
        f"{source_row},{source_col},{sign}),"
        for index, (dest_row, dest_col, source_row, source_col, sign)
        in enumerate(flattened)
    )
    lines += [
        "    _=>PlTerm(-1,-1,-1,-1,0),",
        "  };",
        "}",
        "",
        "fn pl_induced(a:borrow IvTaylor4Mat)->H4Result{",
        "  if(a.rows!=12 || a.cols!=12){",
        "    return h4_result_fail(IVTAY_BAD_SHAPE);}",
        "  let c0:QMat=qm_new(40,40);let c1:QMat=qm_new(40,40);",
        "  let c2:QMat=qm_new(40,40);let c3:QMat=qm_new(40,40);",
        "  let c4:QMat=qm_new(40,40);let rem:IvMat=ivm_zeros(40,40);",
        f"  let index:i64=0;while(index<{len(flattened)}){{",
        "    let term:PlTerm=pl_term(index);",
        "    let factor:Rat=rat(term.sign,1);",
    ]
    for degree in range(5):
        matrix = f"c{degree}"
        lines += [
            f"    {matrix}=qm_set({matrix},term.dest_row,term.dest_col,",
            f"      rat_clone(qm_get({matrix},term.dest_row,term.dest_col))",
            f"      +(rat_clone(factor)*rat_clone(qm_get(a.c{degree},",
            "        term.source_row,term.source_col))));",
        ]
    lines += [
        "    let source_rem:Iv=ivm_at(a.remainder,",
        "      term.source_row,term.source_col);",
        "    let signed_rem:Iv=if(term.sign>0){source_rem}",
        "      else{iv_neg(source_rem)};",
        "    let next_rem:Iv=match(iv_add_checked(",
        "      ivm_at(rem,term.dest_row,term.dest_col),signed_rem)){",
        "      some(z)=>z,none=>{return",
        "        h4_result_fail(IVTAY_INTERVAL_OVERFLOW);}};",
        "    ivm_set(rem,term.dest_row,term.dest_col,next_rem);",
        "    index=index+1;",
        "  }",
        "  let out:IvTaylor4Result=ivtm4_new(",
        "    a.generator,c0,c1,c2,c3,c4,rem);",
        "  return h4_result(out);",
        "}",
        "",
    ]
    return "\n".join(lines)


def render_relation_checks() -> str:
    lines = [
        "fn pl_relations(a:borrow IvTaylor4Mat)->PlCheck{",
        "  if(a.rows!=40 || a.cols!=1){return PlCheck(false,34);}",
    ]
    for relation_index, relation in enumerate(plucker_relations()):
        lines.append(
            f"  let rel_{relation_index}:PlCx=pl_czero(a.generator);"
        )
        for term_index, ((left, right), sign) in enumerate(relation):
            lines += [
                f"  let term_{relation_index}_{term_index}:PlCx="
                f"pl_cmul(pl_coord(a,{left}),pl_coord(a,{right}));",
                f"  if(!term_{relation_index}_{term_index}.ok){{"
                f"return PlCheck(false,"
                f"term_{relation_index}_{term_index}.refusal_code);}}",
                f"  rel_{relation_index}=pl_cadd_signed("
                f"rel_{relation_index},term_{relation_index}_{term_index},"
                f"{sign});",
                f"  if(!rel_{relation_index}.ok){{return PlCheck(false,"
                f"rel_{relation_index}.refusal_code);}}",
            ]
        lines += [
            f"  if(!pl_c_contains_zero(rel_{relation_index})){{",
            f"    println(\"PLUCKER_RELATION_DEFECT relation="
            f"{relation_index}\");",
            "    return PlCheck(false,31);",
            "  }",
        ]
    lines += ["  return PlCheck(true,IVTAY_OK);", "}", ""]
    return "\n".join(lines)


SUPPORT = r'''
pub type PlCx = scoped struct {
  pub ok: bool,
  pub re: IvTaylor4Mat,
  pub im: IvTaylor4Mat,
  pub refusal_code: i64,
};

pub type PlCheck = value struct {
  pub ok: bool,
  pub refusal_code: i64,
};

pub type PlPivot = value struct {
  pub ok: bool,
  pub index: i64,
  pub margin: f64,
  pub norm: f64,
  pub refusal_code: i64,
};

pub type PlState = scoped struct {
  pub ok: bool,
  pub value: IvTaylor4Mat,
  pub pivot: i64,
  pub margin: f64,
  pub norm: f64,
  pub scale_exponent: i64,
  pub refusal_code: i64,
};

fn pl_zero(rows:i64,cols:i64)->IvTaylor4Mat{
  return ivtm4_constant(7315,qm_new(rows,cols));
}

fn pl_fail(code:i64)->PlState{
  return new PlState(false,pl_zero(40,1),-1,0.0,0.0,0,code);
}

fn pl_scalar(a:borrow IvTaylor4Mat,row:i64,col:i64)->IvTaylor4Mat{
  let c0:QMat=qm_new(1,1);let c1:QMat=qm_new(1,1);
  let c2:QMat=qm_new(1,1);let c3:QMat=qm_new(1,1);
  let c4:QMat=qm_new(1,1);let rem:IvMat=ivm_zeros(1,1);
  c0=qm_set(c0,0,0,qm_get(a.c0,row,col));
  c1=qm_set(c1,0,0,qm_get(a.c1,row,col));
  c2=qm_set(c2,0,0,qm_get(a.c2,row,col));
  c3=qm_set(c3,0,0,qm_get(a.c3,row,col));
  c4=qm_set(c4,0,0,qm_get(a.c4,row,col));
  ivm_set(rem,0,0,ivm_at(a.remainder,row,col));
  let out:IvTaylor4Result=ivtm4_new(
    a.generator,c0,c1,c2,c3,c4,rem);
  if(!out.ok){return pl_zero(1,1);}
  return ivtm4_clone(out.value);
}

fn pl_czero(generator:i64)->PlCx{
  return new PlCx(true,ivtm4_constant(generator,qm_new(1,1)),
    ivtm4_constant(generator,qm_new(1,1)),IVTAY_OK);
}

fn pl_cfail(generator:i64,code:i64)->PlCx{
  return new PlCx(false,ivtm4_constant(generator,qm_new(1,1)),
    ivtm4_constant(generator,qm_new(1,1)),code);
}

fn pl_centry(y:borrow IvTaylor4Mat,row:i64,col:i64)->PlCx{
  let rr:i64=if(row<4){row}else{row+4};
  let ri:i64=if(row<4){row+4}else{row+6};
  return new PlCx(true,pl_scalar(y,rr,col),pl_scalar(y,ri,col),IVTAY_OK);
}

fn pl_coord(y:borrow IvTaylor4Mat,index:i64)->PlCx{
  return new PlCx(true,pl_scalar(y,index,0),
    pl_scalar(y,index+20,0),IVTAY_OK);
}

fn pl_cmul(a:borrow PlCx,b:borrow PlCx)->PlCx{
  if(!a.ok){return pl_cfail(a.re.generator,a.refusal_code);}
  if(!b.ok){return pl_cfail(b.re.generator,b.refusal_code);}
  let rr:IvTaylor4Result=ivtm4_mul_checked(a.re,b.re);
  let ii:IvTaylor4Result=ivtm4_mul_checked(a.im,b.im);
  let ri:IvTaylor4Result=ivtm4_mul_checked(a.re,b.im);
  let ir:IvTaylor4Result=ivtm4_mul_checked(a.im,b.re);
  if(!rr.ok){return pl_cfail(a.re.generator,rr.refusal_code);}
  if(!ii.ok){return pl_cfail(a.re.generator,ii.refusal_code);}
  if(!ri.ok){return pl_cfail(a.re.generator,ri.refusal_code);}
  if(!ir.ok){return pl_cfail(a.re.generator,ir.refusal_code);}
  let real:IvTaylor4Result=ivtm4_sub_checked(rr.value,ii.value);
  let imag:IvTaylor4Result=ivtm4_add_checked(ri.value,ir.value);
  if(!real.ok){return pl_cfail(a.re.generator,real.refusal_code);}
  if(!imag.ok){return pl_cfail(a.re.generator,imag.refusal_code);}
  return new PlCx(true,ivtm4_clone(real.value),
    ivtm4_clone(imag.value),IVTAY_OK);
}

fn pl_cadd_signed(a:borrow PlCx,b:borrow PlCx,sign:i64)->PlCx{
  if(!a.ok){return pl_cfail(a.re.generator,a.refusal_code);}
  if(!b.ok){return pl_cfail(b.re.generator,b.refusal_code);}
  let rr:IvTaylor4Result=if(sign>0){
    ivtm4_add_checked(a.re,b.re)
  }else{ivtm4_sub_checked(a.re,b.re)};
  let ii:IvTaylor4Result=if(sign>0){
    ivtm4_add_checked(a.im,b.im)
  }else{ivtm4_sub_checked(a.im,b.im)};
  if(!rr.ok){return pl_cfail(a.re.generator,rr.refusal_code);}
  if(!ii.ok){return pl_cfail(a.re.generator,ii.refusal_code);}
  return new PlCx(true,ivtm4_clone(rr.value),
    ivtm4_clone(ii.value),IVTAY_OK);
}

fn pl_cmul3(a:borrow PlCx,b:borrow PlCx,c:borrow PlCx)->PlCx{
  let ab:PlCx=pl_cmul(a,b);
  if(!ab.ok){return ab;}
  return pl_cmul(ab,c);
}

fn pl_minor3(y:borrow IvTaylor4Mat,i:i64,j:i64,k:i64)->PlCx{
  let out:PlCx=pl_czero(y.generator);
  let t0:PlCx=pl_cmul3(
    pl_centry(y,i,0),pl_centry(y,j,1),pl_centry(y,k,2));
  out=pl_cadd_signed(out,t0,1);
  let t1:PlCx=pl_cmul3(
    pl_centry(y,i,1),pl_centry(y,j,2),pl_centry(y,k,0));
  out=pl_cadd_signed(out,t1,1);
  let t2:PlCx=pl_cmul3(
    pl_centry(y,i,2),pl_centry(y,j,0),pl_centry(y,k,1));
  out=pl_cadd_signed(out,t2,1);
  let t3:PlCx=pl_cmul3(
    pl_centry(y,i,2),pl_centry(y,j,1),pl_centry(y,k,0));
  out=pl_cadd_signed(out,t3,-1);
  let t4:PlCx=pl_cmul3(
    pl_centry(y,i,1),pl_centry(y,j,0),pl_centry(y,k,2));
  out=pl_cadd_signed(out,t4,-1);
  let t5:PlCx=pl_cmul3(
    pl_centry(y,i,0),pl_centry(y,j,2),pl_centry(y,k,1));
  out=pl_cadd_signed(out,t5,-1);
  return out;
}

fn pl_embed(z:borrow PlCx,index:i64)->H4Result{
  if(!z.ok){return h4_result_fail(z.refusal_code);}
  let c0:QMat=qm_new(40,1);let c1:QMat=qm_new(40,1);
  let c2:QMat=qm_new(40,1);let c3:QMat=qm_new(40,1);
  let c4:QMat=qm_new(40,1);let rem:IvMat=ivm_zeros(40,1);
  c0=qm_set(c0,index,0,qm_get(z.re.c0,0,0));
  c1=qm_set(c1,index,0,qm_get(z.re.c1,0,0));
  c2=qm_set(c2,index,0,qm_get(z.re.c2,0,0));
  c3=qm_set(c3,index,0,qm_get(z.re.c3,0,0));
  c4=qm_set(c4,index,0,qm_get(z.re.c4,0,0));
  ivm_set(rem,index,0,ivm_at(z.re.remainder,0,0));
  c0=qm_set(c0,index+20,0,qm_get(z.im.c0,0,0));
  c1=qm_set(c1,index+20,0,qm_get(z.im.c1,0,0));
  c2=qm_set(c2,index+20,0,qm_get(z.im.c2,0,0));
  c3=qm_set(c3,index+20,0,qm_get(z.im.c3,0,0));
  c4=qm_set(c4,index+20,0,qm_get(z.im.c4,0,0));
  ivm_set(rem,index+20,0,ivm_at(z.im.remainder,0,0));
  let out:IvTaylor4Result=ivtm4_new(
    z.re.generator,c0,c1,c2,c3,c4,rem);
  return h4_result(out);
}

fn pl_initial(y:borrow IvTaylor4Mat)->H4Result{
  if(y.rows!=12 || y.cols<3){return h4_result_fail(IVTAY_BAD_SHAPE);}
  let out:IvTaylor4Mat=pl_zero(40,1);
  let index:i64=0;
  while(index<20){
    let i:i64=if(index<10){if(index<4){0}else{if(index<7){1}else{2}}}
      else{if(index<16){if(index<13){0}else{1}}else{if(index<19){0}else{3}}};
    // The generated caller replaces this function with explicit triples.
    index=index+1;
  }
  return h4_result_fail(34);
}

fn pl_c_contains_zero(a:borrow PlCx)->bool{
  if(!a.ok){return false;}
  let rh:IvMat=match(ivtm4_hull_checked(a.re)){
    some(z)=>z,none=>{return false;}};
  let ih:IvMat=match(ivtm4_hull_checked(a.im)){
    some(z)=>z,none=>{return false;}};
  let r:Iv=ivm_at(rh,0,0);let i:Iv=ivm_at(ih,0,0);
  return r.lo<=0.0 && r.hi>=0.0 && i.lo<=0.0 && i.hi>=0.0;
}

fn pl_complex_linear(a:borrow IvTaylor4Mat)->PlCheck{
  let h:IvMat=match(ivtm4_hull_checked(a)){
    some(z)=>z,none=>{return PlCheck(false,IVTAY_INTERVAL_OVERFLOW);}};
  let i:i64=0;while(i<6){let j:i64=0;while(j<6){
    let ri:i64=i;let ii:i64=i+6;
    let rj:i64=j;let ij:i64=j+6;
    let d0:Iv=match(iv_sub_checked(ivm_at(h,ri,rj),ivm_at(h,ii,ij))){
      some(z)=>z,none=>{return PlCheck(false,IVTAY_INTERVAL_OVERFLOW);}};
    let d1:Iv=match(iv_add_checked(ivm_at(h,ii,rj),ivm_at(h,ri,ij))){
      some(z)=>z,none=>{return PlCheck(false,IVTAY_INTERVAL_OVERFLOW);}};
    if(d0.lo>0.0 || d0.hi<0.0 || d1.lo>0.0 || d1.hi<0.0){
      return PlCheck(false,33);}
    j=j+1;}i=i+1;}
  return PlCheck(true,IVTAY_OK);
}

fn pl_pivot(a:borrow IvTaylor4Mat)->PlPivot{
  let h:IvMat=match(ivtm4_hull_checked(a)){
    some(z)=>z,none=>{return PlPivot(false,-1,0.0,0.0,
      IVTAY_INTERVAL_OVERFLOW);}};
  let best:i64=-1;let margin:f64=0.0;let norm:f64=0.0;
  let i:i64=0;while(i<20){
    let re:Iv=ivm_at(h,i,0);let im:Iv=ivm_at(h,i+20,0);
    let ar:Iv=iv_abs(re);let ai:Iv=iv_abs(im);
    if(ar.hi>norm){norm=ar.hi;}if(ai.hi>norm){norm=ai.hi;}
    let mr:f64=if(re.lo>0.0){re.lo}else{if(re.hi<0.0){0.0-re.hi}else{0.0}};
    let mi:f64=if(im.lo>0.0){im.lo}else{if(im.hi<0.0){0.0-im.hi}else{0.0}};
    let candidate:f64=if(mr>mi){mr}else{mi};
    if(candidate>margin){margin=candidate;best=i;}
    i=i+1;
  }
  if(best<0 || margin<=0.0){return PlPivot(false,-1,0.0,norm,32);}
  return PlPivot(true,best,margin,norm,IVTAY_OK);
}

fn pl_projective_normalize(a:borrow IvTaylor4Mat)->PlState{
  let before:PlPivot=pl_pivot(a);
  if(!before.ok){return pl_fail(before.refusal_code);}
  if(before.norm<=0.0 || !f64_is_finite(before.norm)){
    return pl_fail(IVTAY_INTERVAL_OVERFLOW);}
  let scale:Rat=rat(1,1);let exponent:i64=0;let n:f64=before.norm;
  while(n>1.0 && exponent<1024){
    scale=rat_clone(scale)/rat(2,1);n=n/2.0;exponent=exponent+1;}
  while(n<0.5 && exponent>(-1024)){
    scale=rat_clone(scale)*rat(2,1);n=n*2.0;exponent=exponent-1;}
  if(exponent==1024 || exponent==(-1024)){
    return pl_fail(IVTAY_INTERVAL_OVERFLOW);}
  let scaled:IvTaylor4Result=ivtm4_scale_rat_checked(a,scale);
  if(!scaled.ok){return pl_fail(scaled.refusal_code);}
  let rebased:IvTaylor4Result=ivtm4_rebase_dyadic(scaled.value,160);
  if(!rebased.ok){return pl_fail(rebased.refusal_code);}
  let after:PlPivot=pl_pivot(rebased.value);
  if(!after.ok){return pl_fail(after.refusal_code);}
  return new PlState(true,ivtm4_clone(rebased.value),after.index,
    after.margin,after.norm,exponent,IVTAY_OK);
}

fn pl_step(a:borrow IvAffineMat,h:borrow Rat,start:borrow IvTaylor4Mat,
order:i64)->H4Result{
  if(a.rows!=12 || a.cols!=12 || order<1 || rat_sign(h)<=0){
    return h4_result_fail(IVTAY_BAD_SHAPE);}
  let at:IvTaylor4Mat=h4_from_affine(a);
  let linear:PlCheck=pl_complex_linear(at);
  if(!linear.ok){return h4_result_fail(linear.refusal_code);}
  let induced:H4Result=pl_induced(at);
  if(!induced.ok){return induced;}
  let bh:IvMat=match(ivtm4_hull_checked(induced.value)){
    some(z)=>z,none=>{return h4_result_fail(IVTAY_INTERVAL_OVERFLOW);}};
  let alpha:f64=sl_inf_norm_hi(bh);
  let start_stats:H4Stats=h4_stats(start);
  if(!start_stats.ok || alpha<0.0){
    return h4_result_fail(IVTAY_INTERVAL_OVERFLOW);}
  let sum:IvTaylor4Mat=ivtm4_clone(start);
  let power:IvTaylor4Mat=ivtm4_clone(start);
  let coefficient:Rat=rat(1,1);let n:i64=1;
  while(n<=order){
    let next:IvTaylor4Result=ivtm4_mul_checked(induced.value,power);
    if(!next.ok){return h4_result(next);}
    power=ivtm4_clone(next.value);
    coefficient=(rat_clone(coefficient)*rat_clone(h))/rat(n,1);
    let scaled:IvTaylor4Result=ivtm4_scale_rat_checked(power,coefficient);
    if(!scaled.ok){return h4_result(scaled);}
    let added:IvTaylor4Result=ivtm4_add_checked(sum,scaled.value);
    if(!added.ok){return h4_result(added);}
    sum=ivtm4_clone(added.value);n=n+1;
  }
  let tail:f64=start_stats.norm*
    sl_exp_tail(rat_to_f64(h)*alpha,order+1);
  return h4_pad_checked(sum,tail);
}

fn pl_attempt(shell:i64,segment:i64,cell:borrow IvAffineCell,
start:borrow PlState)->PlState{
  if(!start.ok){return pl_fail(start.refusal_code);}
  let state:PlState=new PlState(true,ivtm4_clone(start.value),
    start.pivot,start.margin,start.norm,start.scale_exponent,IVTAY_OK);
  let count:i64=32;let panel:i64=segment*count;
  while(panel<(segment+1)*count){
    let lo:Rat=hr_shell_lo(shell);
    let width:Rat=hr_panel_width(shell);
    let xc:Rat=rat_clone(lo)+(rat(2*panel+1,2)*rat_clone(width));
    let ta:Iv=iv_from_rat(rat_clone(lo)+rat(panel,1)*rat_clone(width));
    let tb:Iv=iv_from_rat(rat_clone(lo)+rat(panel+1,1)*rat_clone(width));
    let a:IvAffineMat=hc_runtime(
      xc,iv(ta.lo,tb.hi),rat_clone(width)/rat(2,1),cell);
    let stepped:H4Result=pl_step(a,width,state.value,12);
    if(!stepped.ok){return pl_fail(stepped.refusal_code);}
    let normalized:PlState=pl_projective_normalize(stepped.value);
    if(!normalized.ok){return normalized;}
    state=new PlState(true,ivtm4_clone(normalized.value),
      normalized.pivot,normalized.margin,normalized.norm,
      normalized.scale_exponent,IVTAY_OK);
    panel=panel+1;
  }
  return state;
}
'''


def render_initial() -> str:
    lines = [
        "fn pl_initial(y:borrow IvTaylor4Mat)->H4Result{",
        "  if(y.rows!=12 || y.cols<3){",
        "    return h4_result_fail(IVTAY_BAD_SHAPE);}",
        "  let out:IvTaylor4Mat=pl_zero(40,1);",
    ]
    for index, (first, second, third) in enumerate(TRIPLES):
        lines += [
            f"  let minor_{index}:PlCx=pl_minor3("
            f"y,{first},{second},{third});",
            f"  if(!minor_{index}.ok){{return "
            f"h4_result_fail(minor_{index}.refusal_code);}}",
            f"  let embedded_{index}:H4Result=pl_embed(minor_{index},{index});",
            f"  if(!embedded_{index}.ok){{return embedded_{index};}}",
            f"  let added_{index}:IvTaylor4Result=ivtm4_add_checked("
            f"out,embedded_{index}.value);",
            f"  if(!added_{index}.ok){{return h4_result(added_{index});}}",
            f"  out=ivtm4_clone(added_{index}.value);",
        ]
    lines += ["  return new H4Result(true,ivtm4_clone(out),IVTAY_OK);", "}", ""]
    return "\n".join(lines)


def render_main() -> str:
    lines = [
        "pub fn main()->i64{",
        "  let cell:IvAffineCell=hr_cell();",
        "  let initial_basis:IvTaylor4Mat=hr_reorder_rows(",
        "    h4_from_affine(hc_initial_model(cell)),true);",
        "  let initial_wedge:H4Result=pl_initial(initial_basis);",
        '  if(!initial_wedge.ok){println(strfmt(system_allocator(),'
        '"PLUCKER_REFUSE stage=initial-wedge code={}",'
        "[initial_wedge.refusal_code]));return 3;}",
        "  let state:PlState=pl_projective_normalize(initial_wedge.value);",
        '  if(!state.ok){println(strfmt(system_allocator(),'
        '"PLUCKER_REFUSE stage=initial-normalize code={}",'
        "[state.refusal_code]));return 3;}",
        "  let initial_rel:PlCheck=pl_relations(state.value);",
        '  if(!initial_rel.ok){println(strfmt(system_allocator(),'
        '"PLUCKER_REFUSE stage=initial-relations code={}",'
        "[initial_rel.refusal_code]));return 3;}",
        f'  println("PLUCKER_BEGIN cell=[{rational_text(CELL[0])},'
        f'{rational_text(CELL[1])}] coordinates=20-complex '
        'relations=45 target=shell3-segment0");',
    ]
    for position, (shell, segment) in enumerate(TARGET_SEGMENTS):
        lines += [
            f"  let next_{position}:PlState=pl_attempt("
            f"{shell},{segment},cell,state);",
            f"  if(!next_{position}.ok){{println(strfmt("
            f'system_allocator(),"PLUCKER_REFUSE shell={shell} '
            f'segment={segment} code={{}}",'
            f"[next_{position}.refusal_code]));return 3;}}",
            f"  state=new PlState(true,ivtm4_clone(next_{position}.value),"
            f"next_{position}.pivot,next_{position}.margin,"
            f"next_{position}.norm,next_{position}.scale_exponent,IVTAY_OK);",
            f"  let rel_{position}:PlCheck=pl_relations(state.value);",
            f"  if(!rel_{position}.ok){{println(strfmt("
            f'system_allocator(),"PLUCKER_REFUSE shell={shell} '
            f'segment={segment} relations code={{}}",'
            f"[rel_{position}.refusal_code]));return 3;}}",
            f'  println(strfmt(system_allocator(),"PLUCKER_SEGMENT '
            f'shell={shell} segment={segment} pivot={{}} margin={{}} '
            'norm={} relations=45",[state.pivot,state.margin,state.norm]));',
        ]
    lines += [
        '  println(strfmt(system_allocator(),"PLUCKER_RESULT pivot={} '
        'margin={} norm={} rank_witness=true",'
        "[state.pivot,state.margin,state.norm]));",
        '  println("PLUCKER_PASS reached_shell=3 reached_segment=0 '
        'rank_witness=true parameter_correlation=true");',
        "  return 42;",
        "}",
        "",
    ]
    return "\n".join(lines)


def render() -> str:
    support = SUPPORT.replace(
        "fn pl_initial(y:borrow IvTaylor4Mat)->H4Result{",
        "fn pl_initial_placeholder(y:borrow IvTaylor4Mat)->H4Result{",
        1,
    )
    return (
        _base_prefix()
        + resume.DEGREE4_SUPPORT
        + support
        + render_induced_builder()
        + render_relation_checks()
        + render_initial()
        + render_main()
    )


def main() -> int:
    HERE.mkdir(parents=True, exist_ok=True)
    source = render()
    SOURCE.write_text(source)
    metadata = {
        "schema": "phase3-axial-horizon-h4-plucker-source-v1",
        "status": "RENDERED_NOT_YET_VERIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "frequency_cell": [rational_text(value) for value in CELL],
        "shared_parameter_generator": GENERATOR,
        "taylor_degree": 4,
        "taylor_order": TAYLOR_ORDER,
        "panels_per_shell": PANELS_PER_SHELL,
        "target": {"shell": 3, "segment": 0},
        "plucker_coordinates": 20,
        "realified_state_rows": 40,
        "plucker_relation_count": len(plucker_relations()),
        "plucker_relation_span_rank": relation_span_rank(),
        "induced_inventory_sha256": canonical_hash(induced_inventory()),
        "relation_inventory_sha256": canonical_hash(relation_inventory()),
        "typed_layouts": {
            "initializer": "block-realified",
            "runtime_generator": "standard Re(6),Im(6)",
            "plucker_state": "Re(20),Im(20)"
        },
        "projective_normalization": "exact dyadic power-of-two per panel",
        "rank_witness": "one complex Pluecker coordinate component excludes zero",
        "forge_substrate_commit": "9cf17af8c7f4f834a5925cc7b9945816941010c9",
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "does_not_establish": [
            "the complete 23-shell horizon transport",
            "canonical endpoint amplitudes",
            "a horizon-to-infinity connection or scattering theorem",
        ],
    }
    METADATA.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    print(metadata["source_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
