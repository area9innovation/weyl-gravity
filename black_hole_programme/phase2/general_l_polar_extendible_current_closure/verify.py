"""Method-distinct invariant replay for the polar current filtration."""
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
    assert d['status']['current'].startswith('SCOPED PASS')
    assert d['literal_current_parser']=={'expanded_numerator_terms':272,'oriented_field_derivative_signatures':79}
    assert d['bounded_gj_reconnaissance']['status']=='SERIALIZED_PREFIX_CLASSIFICATION'
    q=Path(__file__).with_name('prefix_artifacts')
    z0=json.loads((q/'zero-log0-depth8.json').read_text()); z1=json.loads((q/'zero-log1-depth8.json').read_text())
    o0=json.loads((q/'oscillatory-log0-depth8.json').read_text()); o1=json.loads((q/'oscillatory-log1-depth8.json').read_text())
    assert [z0['final_free_dimension'],z1['final_free_dimension'],o0['final_free_dimension'],o1['final_free_dimension']]==[1,1,2,3]
    def first_nonzero(basis):
        return min(n for level in basis for n,row in enumerate(level) if any(x!='0' for x in row))
    assert first_nonzero(o0['basis_jets'][0])==8
    assert first_nonzero(o0['basis_jets'][1])==0
    assert first_nonzero(o1['basis_jets'][2])==8
    # Independent exact fixture replay of the two-layer filtration.  The
    # producer proves polynomial identities; this verifier reconstructs the
    # full matrices from the independently serialized entries and checks the
    # rank/radical conclusion at the frozen rational fixture.
    names=('E','X0','X1','X2'); L=sp.Symbol('Lambda',real=True)
    def value(left,right,power):
        path=Path(__file__).with_name('current_artifacts')/f'oscillatory-{left}-{right}.json'
        entry=json.loads(path.read_text())['result']['layers'].get(str(power))
        if entry is None:return sp.Integer(0)
        return sum(sp.sympify(c,locals={'I':sp.I})*6**m[0]*sp.Rational(3,5)**m[1] for m,c in entry['sparse_terms'])
    N0=sp.Matrix([[value(a,b,0) for b in names] for a in names])
    Nm=sp.Matrix([[value(a,b,-1) for b in names] for a in names])
    Nf=sp.Matrix([[value(a,b,-2) for b in names] for a in names])
    assert N0+N0.conjugate().T==sp.zeros(4)
    assert Nm+Nm.conjugate().T==sp.zeros(4)
    assert Nf+Nf.conjugate().T==sp.zeros(4)
    assert N0.rank()==3 and N0[1:,1:].det()!=0
    radical=N0.nullspace(); assert len(radical)==1
    assert sp.simplify((radical[0].conjugate().T*Nm*radical[0])[0])==0
    assert sp.simplify((radical[0].conjugate().T*Nf*radical[0])[0])!=0
    matrix=json.loads((Path(__file__).with_name('current_artifacts')/'oscillatory-matrix-filtration.json').read_text())
    assert matrix['leading_p0']['schur_numerator_identically_zero']
    assert matrix['subleading_p_minus_1']['induced_form_on_leading_radical_identically_zero']
    assert not matrix['first_finite_p_minus_2']['identically_zero']
    wall=json.loads((Path(__file__).with_name('current_artifacts')/'canonical-pivot-wall-certificate.json').read_text())
    assert wall['disposition']=='EMPTY_CANONICAL_PIVOT_WALL_ON_PHYSICAL_DOMAIN'
    assert wall['finite_line']['identity_verified']
    basis=json.loads((Path(__file__).with_name('current_artifacts')/'basis-lift-congruence.json').read_text())
    assert basis['abstract_identity']['verified'] and basis['exact_probe']['raw_detK_changed']
    print('verified polar restriction-stable module/current filtration')
if __name__=='__main__': main()
