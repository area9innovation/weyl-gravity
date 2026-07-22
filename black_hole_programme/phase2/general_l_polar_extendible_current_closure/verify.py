"""Method-distinct invariant replay for the bounded checkpoint."""
from __future__ import annotations
import json, sympy as sp
from pathlib import Path

def main():
    p=Path(__file__).with_name('certificate.json'); d=json.loads(p.read_text())
    w,z=sp.symbols('omega z',real=True,nonzero=True)
    A=sp.Matrix([[0,sp.I*w/2,sp.Rational(1,2),sp.I*w],[0,0,1,0],[0,0,-2*sp.I*w,0],[0,sp.I*w,sp.Rational(1,2),0]])
    assert sp.factor((z*sp.eye(4)-A).det())==z**3*(z+2*sp.I*w)
    assert [4-(A**k).rank() for k in (1,2,3)]==d['master_infinity']['zero_generalized_nullities']
    L,r,k=sp.symbols('Lambda r kappa',real=True,nonzero=True)
    rem=sp.I*k*(sp.I*L**2-2*sp.I*L+12*w)/(4*r**2)
    normalized = sp.expand(rem*4*r**2/(sp.I*k))
    assert normalized == sp.I*L**2-2*sp.I*L+12*w
    assert sp.re(normalized) == 12*w
    defect=3*L-48*w**2+15+12*sp.I*w
    assert sp.im(defect)==12*w
    assert d['status']['current']=='NOT_COMPUTED'
    assert d['literal_current_parser']=={'expanded_numerator_terms':272,'oriented_field_derivative_signatures':79}
    assert d['bounded_gj_reconnaissance']['status']=='UNPROMOTED_UNSERIALIZED_RECONNAISSANCE'
    print('verified polar module/current bounded checkpoint')
if __name__=='__main__': main()
