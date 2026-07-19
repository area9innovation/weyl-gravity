#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
from jsonschema import Draft202012Validator
import sympy as sp
ROOT=Path(__file__).resolve().parents[2]
CERT=ROOT/"bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_finite_minus_dressing_no_go.json"
SCHEMA=ROOT/"bridge/einstein_sector/schema/einstein_maxwell_weyl_exceptional_ellipse_finite_minus_dressing_no_go.schema.json"
def verify():
 v=json.loads(CERT.read_text());s=json.loads(SCHEMA.read_text());Draft202012Validator.check_schema(s);Draft202012Validator(s).validate(v)
 for item in v['provenance']['inputs'].values():
  p=ROOT/item['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']
 t=sp.symbols('t',positive=True);g=2*t**2-4*t-9+6/t-3/t**2
 assert sp.simplify(g.subs(t,2*sp.sqrt(3))-(sp.Rational(59,4)-7*sp.sqrt(3)))==0
 assert sp.Rational(59,4)-7*sp.sqrt(3)>0
 for a in range(2,9):
  for b in range(2,9):
   w=lambda l:sp.sqrt(l*(l+1)-sp.sqrt(2*l*(l+1)))
   assert w(a+b-1)<w(a)+w(b)<w(a+b)
 c=v['classification'];assert c['arbitrary_finite_minus_superpositions_covered'] and c['bounded_extension_obstructed'];assert not c['additional_nonminus_carriers_classified']
if __name__=='__main__':verify();print('EINSTEIN_MAXWELL_WEYL_EXCEPTIONAL_ELLIPSE_FINITE_MINUS_DRESSING_NO_GO independent verification: PASS')
