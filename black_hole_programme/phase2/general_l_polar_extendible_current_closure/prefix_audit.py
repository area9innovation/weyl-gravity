"""Exact GJ full-seven-row homogeneous prefix producer.

This intentionally reuses only the frozen equation assembler.  Its fraction-
field elimination is replaced by GJ, which avoids the former FF blow-up.
"""
from __future__ import annotations
import argparse, contextlib, hashlib, io, json, time
from pathlib import Path
import sympy as sp
from sympy.polys.matrices import DomainMatrix
from black_hole_programme.phase2.general_l_polar_completion.incremental_recurrence import direct_all_seven, ROOT

PKG=Path(__file__).resolve().parent

def data(sector:str):
    exact=json.loads((ROOT/'black_hole_programme/phase2/general_l_polar/certificate.json').read_text())['exact_symbolic_lambda_result']
    r=sp.Symbol('r',positive=True); L=sp.Symbol('Lambda'); w=sp.Symbol('omega',real=True,nonzero=True)
    fs={n:sp.Function(n) for n in ('a','bc','cc','f','Ah','Bh','Ch','Kh')}
    local={**fs,'r':r,'m':sp.Integer(1),'Lambda':L,'omega':w,'I':sp.I,'Derivative':sp.Derivative}
    rate=sp.Integer(0) if sector=='zero' else -2*sp.I*w
    beta=sp.Integer(1) if sector=='zero' else 1-4*sp.I*w
    return {'reconstruction':exact['ricci_to_metric_reconstruction'],'local':local,
            'symbols':(r,L,w),'rate':rate,'sigma':beta,
            'carrier_jet':[[sp.Integer(0)]*6 for _ in range(20)]}, beta

def produce_prefix(sector:str, logs:int, depth:int=8):
    d,beta=data(sector); original=DomainMatrix.rref
    def gj(self, method='auto'): return original(self,method='GJ')
    started=time.perf_counter()
    DomainMatrix.rref=gj
    try:
        with contextlib.redirect_stdout(io.StringIO()): out=direct_all_seven(d,depth,logs,0)
    finally: DomainMatrix.rref=original
    nlevels=depth+3; free=out['final_homogeneous_parameter_count']; split=out['final_affine_splitting']
    bases=[]
    for k in range(free):
        levels=[]
        for level in range(logs+1):
            jets=[]
            for n in range(depth+1):
                row=[]
                for field in range(4):
                    idx=str(4*(level*nlevels+n)+field)
                    coeff=split.get(idx,{'free_coefficients':['0']*free})['free_coefficients']
                    row.append(coeff[k] if k<len(coeff) else '0')
                jets.append(row)
            levels.append(jets)
        bases.append(levels)
    payload={'schema_version':'polar-seven-row-prefix-v1','sector':sector,'rate':sp.sstr(d['rate']),
      'beta':sp.sstr(beta),'logs':logs,'depth':depth,'field_order':['Ah','Bh','Ch','Kh'],
      'final_free_dimension':free,'basis_jets':bases,'q_counts':out['q_counts'],
      'pivot_denominator_factors':out['pivot_denominator_factors'],
      'per_order_affine_rank_witnesses':out['per_order_affine_rank_witnesses'],
      'final_affine_splitting':split,'original_seven_row_residuals_zero':out['original_seven_row_residuals_zero'],
      'elapsed_seconds_observed':round(time.perf_counter()-started,6),
      'claim_boundary':'finite formal prefix only; no all-order solution, quotient identification or current theorem'}
    canonical=json.dumps({k:v for k,v in payload.items() if k!='elapsed_seconds_observed'},sort_keys=True,separators=(',',':')).encode()
    payload['payload_sha256']=hashlib.sha256(canonical).hexdigest()
    return payload

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--sector',choices=['zero','oscillatory'],required=True);ap.add_argument('--logs',type=int,choices=[0,1],required=True);ap.add_argument('--depth',type=int,default=8);a=ap.parse_args()
    out=PKG/'prefix_artifacts'/f'{a.sector}-log{a.logs}-depth{a.depth}.json';out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(produce_prefix(a.sector,a.logs,a.depth),indent=2,sort_keys=True)+'\n')
    print(out)
if __name__=='__main__':main()
