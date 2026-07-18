#!/usr/bin/env python3
"""Export direct exact Maxwell Delta1 and codifferential charge blocks."""
from __future__ import annotations
import argparse,hashlib,json
from fractions import Fraction
from pathlib import Path
from jsonschema import Draft202012Validator
import sympy as sp
from closed_universe_observers.generate_berger_peter_weyl_form_laplacian import C,d_matrix,laplacian
from closed_universe_observers.generate_berger_streamable_polarization_sectors import helicity_sectors
ROOT=Path(__file__).resolve().parents[1];PACKAGE=ROOT/"closed_universe_observers";CERTIFICATE=PACKAGE/"certificates/BERGER_EXACT_MAXWELL_CHARGE_BLOCK_FORMULAS.json";SCHEMA=PACKAGE/"schema/berger-exact-maxwell-charge-block-formulas-v1.schema.json";REPORT=PACKAGE/"reports/berger-exact-maxwell-charge-block-formulas.md";DEPENDENCY=PACKAGE/"certificates/BERGER_STREAMABLE_POLARIZATION_SECTORS.json";SOURCE_FILES=[Path(__file__),PACKAGE/"verify_berger_exact_maxwell_charge_blocks.py",PACKAGE/"tests/test_berger_exact_maxwell_charge_blocks.py",SCHEMA,REPORT]
def _sha256(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def charge_block(two_j:int,q:Fraction)->tuple[list[tuple[int,Fraction]],sp.Matrix]:
 j=sp.Rational(two_j,2);members=helicity_sectors(two_j).get(q,[]);B=sp.zeros(len(members));pos={c:i for i,(c,m) in enumerate(members)}
 for i,(c,mf) in enumerate(members):
  m=sp.Rational(mf.numerator,mf.denominator)
  if c==0:B[i,i]=j*(j+1)+(31*m*m+71*m+40)/9
  elif c==1:B[i,i]=j*(j+1)+31*m*m/9+sp.Rational(9,40)
  else:B[i,i]=j*(j+1)+(31*m*m-71*m+40)/9
 if 0 in pos and 1 in pos:
  m=sp.Rational(members[pos[0]][1].numerator,members[pos[0]][1].denominator);x=-C/sp.sqrt(2)*sp.sqrt((j-m)*(j+m+1));B[pos[0],pos[1]]=B[pos[1],pos[0]]=x
 if 1 in pos and 2 in pos:
  m=sp.Rational(members[pos[1]][1].numerator,members[pos[1]][1].denominator);x=C/sp.sqrt(2)*sp.sqrt((j-m)*(j+m+1));B[pos[1],pos[2]]=B[pos[2],pos[1]]=x
 return members,sp.simplify(B)
def delta_row(two_j:int,q:Fraction)->tuple[list[tuple[int,Fraction]],sp.Matrix]:
 j=sp.Rational(two_j,2);members=helicity_sectors(two_j).get(q,[]);row=sp.zeros(1,len(members))
 for i,(c,mf) in enumerate(members):
  m=sp.Rational(mf.numerator,mf.denominator)
  if c==0:row[i]=sp.I/sp.sqrt(2)*sp.sqrt((j-m)*(j+m+1))
  elif c==1:row[i]=sp.I*m/C
  else:row[i]=sp.I/sp.sqrt(2)*sp.sqrt((j+m)*(j-m+1))
 return members,sp.simplify(row)
def scalar_eigenvalue(two_j:int,q:Fraction):
 j=sp.Rational(two_j,2);return sp.simplify(j*(j+1)+sp.Rational(31,9)*sp.Rational(q.numerator,q.denominator)**2)
def audit(max_two_j=8):
 defects=delta_defects=blocks=0;rt=sp.sqrt(2);H=sp.Matrix([[1/rt,0,1/rt],[sp.I/rt,0,-sp.I/rt],[0,1,0]])
 for tj in range(max_two_j+1):
  d=tj+1;U=sp.kronecker_product(H,sp.eye(d));A=sp.simplify(U.conjugate().T*laplacian(tj,1)*U);delta=sp.simplify(d_matrix(tj,0).conjugate().T*U);j=Fraction(tj,2)
  for q,members in helicity_sectors(tj).items():
   inds=[c*d+int(m+j) for c,m in members];_,B=charge_block(tj,q);_,D=delta_row(tj,q);defects+=sum(sp.simplify(x)!=0 for x in A.extract(inds,inds)-B);direct_delta=delta.extract([int(q+j)],inds) if -j<=q<=j else sp.zeros(1,len(inds));delta_defects+=sum(sp.simplify(x)!=0 for x in direct_delta-D);blocks+=1
 return {"audited_two_j_maximum":max_two_j,"charge_block_count":blocks,"laplacian_entry_defect_count":defects,"codifferential_entry_defect_count":delta_defects}
def build():
 v=json.loads(DEPENDENCY.read_text());a=audit()
 if a["laplacian_entry_defect_count"] or a["codifferential_entry_defect_count"]:raise AssertionError("direct charge formula mismatch")
 boundary="This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result exports closed formulas for every finite q=m+s Maxwell Delta1 charge block and the corresponding spatial codifferential row. Blocks have dimension at most three and are tridiagonal in theta_plus,theta3,theta_minus. Exact comparison with the authoritative dense de Rham engine through two_j=8 has zero Laplacian and codifferential entry defects. These formulas enable streaming order-14 Green application; they do not apply the polynomial, certify its remainder or spatial tail, construct full images, evaluate recoil, activate Bridge 3 or make quantum claims."
 return {"schema":"closed-universe-berger-exact-maxwell-charge-block-formulas-v1","result_id":"BERGER_EXACT_MAXWELL_CHARGE_BLOCK_FORMULAS","setting_id":v["setting_id"],"claim_status":"EXACT_ALL_FINITE_TWO_J_MAXWELL_CHARGE_BLOCK_AND_CODIFFERENTIAL_FORMULAS_EXPORTED","dependency_tags":["LOCAL-ALGEBRAIC","LORENTZIAN-CAUSAL"],"dependency_refs":{"sectors":{"path":str(DEPENDENCY.relative_to(ROOT)),"result_id":v["result_id"],"sha256":_sha256(DEPENDENCY)}},"basis":{"order":["theta_plus","theta3","theta_minus"],"charge":"q=m+s","maximum_dimension":3},"formulas":{"theta_plus_diagonal":"j(j+1)+(31m^2+71m+40)/9","theta3_diagonal":"j(j+1)+31m^2/9+9/40","theta_minus_diagonal":"j(j+1)+(31m^2-71m+40)/9","plus_to_theta3":"-(c/sqrt(2))*sqrt((j-m)(j+m+1))","theta3_to_minus":"+(c/sqrt(2))*sqrt((j-m)(j+m+1))","delta_plus":"i/sqrt(2)*sqrt((j-m)(j+m+1))","delta_theta3":"i*m/c","delta_minus":"i/sqrt(2)*sqrt((j+m)(j-m+1))","scalar_Delta0":"j(j+1)+31q^2/9"},"dense_engine_audit":a,"flags":{"ALL_FINITE_TWO_J_EXACT_MAXWELL_CHARGE_BLOCK_FORMULAS_EXPORTED":True,"ALL_FINITE_TWO_J_EXACT_CODIFFERENTIAL_CHARGE_ROWS_EXPORTED":True,"ORDER14_TEMPORAL_GREEN_CHARGE_BLOCKS_APPLIED":False,"GREEN_WEIGHTED_OPERATOR_NORM_TAIL_EXPORTED":False,"QUANTUM_CLAIM":False},"next_gate":"APPLY_COMMON_ORDER14_COSINE_AND_CODIFFERENTIAL_SINE_POLYNOMIALS_THROUGH_TWO_J138","claim_boundary":boundary,"provenance":{"source_commit":"WORKTREE","source_manifest":[{"path":str(p.relative_to(ROOT)),"sha256":_sha256(p)} for p in SOURCE_FILES]}}
def main():
 p=argparse.ArgumentParser();p.add_argument("--emit",action="store_true");p.add_argument("--check",action="store_true");x=p.parse_args();v=build();s=json.loads(SCHEMA.read_text());Draft202012Validator.check_schema(s);Draft202012Validator(s).validate(v);r=json.dumps(v,indent=2,sort_keys=True)+"\n";
 if x.emit:CERTIFICATE.write_text(r)
 if x.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text()!=r):raise SystemExit("stale charge-block formula certificate")
 print("BERGER_EXACT_MAXWELL_CHARGE_BLOCK_FORMULAS generation: PASS");return 0
if __name__=="__main__":raise SystemExit(main())
