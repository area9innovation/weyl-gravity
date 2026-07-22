"""Produce one exact dangerous-layer current entry."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import sympy as sp
from sympy.polys.domains import QQ_I
ROOT=Path(__file__).resolve().parents[3]; PKG=Path(__file__).resolve().parent

def profiles():
 L=sp.Symbol('Lambda',real=True);w=sp.Symbol('omega',real=True,nonzero=True);loc={'Lambda':L,'omega':w,'I':sp.I}
 def coeffs(rows):return [[sp.sympify(row[i],locals=loc) for row in rows] for i in range(4)]
 z=json.loads((PKG/'prefix_artifacts/zero-log0-depth8.json').read_text());o=json.loads((PKG/'prefix_artifacts/oscillatory-log0-depth8.json').read_text())
 p={'zero':{'E':{'rate':0,'beta':1,'coeffs':coeffs(z['basis_jets'][0][0])}},'oscillatory':{'E':{'rate':-2*sp.I*w,'beta':1-4*sp.I*w,'coeffs':coeffs(o['basis_jets'][1][0])}}}
 base=ROOT/'black_hole_programme/phase2/general_l_polar_completion/branch_artifacts'
 for s in p:
  for i in range(3):
   d=json.loads((base/f'{s}-{i}.json').read_text());p[s][f'X{i}']={'rate':sp.sympify(d['rate'],locals=loc),'beta':sp.sympify(d['metric_reconstruction']['base'],locals=loc),'coeffs':coeffs(d['metric_reconstruction']['canonical_metric_jets'][0])}
 # Reconstruction jets use exp(+I*omega*v), whereas the literal current's
 # left slot was Fourier-reduced with exp(-I*omega*v).  Cross the convention
 # boundary once here; current_layer_table then conjugates this left profile
 # into the right slot.  omega and Lambda themselves remain fixed and real.
 for modes in p.values():
  for prof in modes.values():
   prof['rate']=sp.conjugate(prof['rate']).subs({sp.conjugate(w):w,sp.conjugate(L):L})
   prof['beta']=sp.conjugate(prof['beta']).subs({sp.conjugate(w):w,sp.conjugate(L):L})
   prof['coeffs']=[[sp.conjugate(c).subs({sp.conjugate(w):w,sp.conjugate(L):L}) for c in row] for row in prof['coeffs']]
 return p

def denominator_clear(p):
 out={}; ledger={}
 for sector,modes in p.items():
  out[sector]={};ledger[sector]={}
  for name,prof in modes.items():
   vals=[c for row in prof['coeffs'] for c in row if c!=0]
   dens=[sp.denom(sp.cancel(c)) for c in vals]
   D=max(dens,key=lambda x:(sp.Poly(x,sp.Symbol('Lambda'),sp.Symbol('omega')).total_degree(),len(sp.sstr(x)))) if dens else sp.Integer(1)
   cleared=[[sp.cancel(D*c) for c in row] for row in prof['coeffs']]
   if any(sp.denom(x)!=1 for row in cleared for x in row):
    for den in dens: D=sp.lcm(D,den)
    cleared=[[sp.expand(sp.cancel(D*c)) for c in row] for row in prof['coeffs']]
    if any(sp.denom(x)!=1 for row in cleared for x in row): raise RuntimeError('denominator clearing failed')
   else:
    cleared=[[sp.expand(x) for x in row] for row in cleared]
   out[sector][name]={**prof,'coeffs':cleared};ledger[sector][name]=sp.sstr(D)
 return out,ledger

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--sector',choices=['zero','oscillatory'],required=True);ap.add_argument('--left',required=True);ap.add_argument('--right',required=True);a=ap.parse_args()
 pv=json.loads((ROOT/'black_hole_programme/phase2/general_l_polar/certificate.json').read_text())
 cur=pv['exact_symbolic_lambda_result']['literal_lee_wald_current']['sphere_integrated_slice_current']
 allp=profiles(); selected={a.sector:{a.left:allp[a.sector][a.left],a.right:allp[a.sector][a.right]}}
 cleared,denominators=denominator_clear(selected)
 L=sp.Symbol('Lambda',real=True);w=sp.Symbol('omega',real=True,nonzero=True);r=sp.Symbol('r');alpha=sp.Symbol('alpha');ell=sp.Symbol('ell',integer=True)
 names=['FAa_r','FBa_r','FCa_r','FKa_r','FAb_r','FBb_r','FCb_r','FKb_r'];funcs={n:sp.Function(n) for n in names}
 local={**funcs,'r':r,'Lambda':L,'m':1,'omega':w,'alpha':alpha,'ell':ell,'I':sp.I,'pi':sp.pi,'Derivative':sp.Derivative}
 expr=sp.sympify(cur,locals=local);pref=4*sp.pi*alpha/(3*(2*ell+1));terms=sp.Add.make_args(sp.expand(sp.cancel(expr/pref)))
 def P(x):return sp.Poly(sp.expand(x),L,w,domain=QQ_I)
 parsed=[]
 for term in terms:
  ds=list(term.atoms(sp.Derivative));occupied={d.expr for d in ds};atoms=[(d.expr.func.__name__,sum(n for _,n in d.variable_count),d) for d in ds]
  atoms += [(f.func.__name__,0,f) for f in term.atoms(sp.Function) if f.func.__name__ in names and f not in occupied]
  fac=atoms[0][2]*atoms[1][2];coef=term/fac;rp=int(coef.as_powers_dict().get(r,0));parsed.append(([(n.endswith('a_r'),n[:2],o) for n,o,_ in atoms],P(coef/r**rp),rp))
 fi={'FA':0,'FB':1,'FC':2,'FK':3}; maxd=max(o for atoms,_,_ in parsed for _,_,o in atoms)
 def conj(x):return sp.conjugate(x).subs({sp.conjugate(L):L,sp.conjugate(w):w})
 def cache(prof,right=False):
  beta=conj(prof['beta']) if right else prof['beta'];rate=conj(prof['rate']) if right else prof['rate'];css=[[conj(c) for c in row] for row in prof['coeffs']] if right else prof['coeffs']
  towers={}
  for stem,i in fi.items():
   arr=[P(c) for c in css[i]];towers[stem,0]=arr
   for order in range(1,maxd+1):
    prev=towers[stem,order-1];nxt=[P(0)]*(len(prev)+1)
    for n,c in enumerate(prev):
     nxt[n]=nxt[n]+P(rate)*c;nxt[n+1]=nxt[n+1]+P(beta-n)*c
    towers[stem,order]=nxt
  return beta,towers
 left=cleared[a.sector][a.left];right=cleared[a.sector][a.right];bl,cl=cache(left);br,cr=cache(right,True)
 prep=[];structural=None
 for atoms,c0,rp in parsed:
  jets=[]
  for isleft,stem,o in atoms:jets.append((bl if isleft else br,(cl if isleft else cr)[stem,o]))
  nz0=[(n,x) for n,x in enumerate(jets[0][1]) if not x.is_zero];nz1=[(n,x) for n,x in enumerate(jets[1][1]) if not x.is_zero]
  if not nz0 or not nz1:continue
  top=int(sp.expand(jets[0][0]+jets[1][0]+rp-nz0[0][0]-nz1[0][0]));structural=top if structural is None else max(structural,top);prep.append((jets,c0,rp,nz0,nz1))
 cancelled=[];layers={}
 # The dangerous threshold is p>=-1.  Keep one finite layer p=-2 as an
 # explicit witness that the cancellation audit crosses that boundary.
 for target in range(structural,-3,-1):
  value=P(0)
  for jets,c0,rp,nz0,nz1 in prep:
   off=int(sp.expand(jets[0][0]+jets[1][0]+rp))
   for n,x in nz0:
    m=off-target-n
    if 0<=m<len(jets[1][1]):value=value+c0*x*jets[1][1][m]
  if value.is_zero:cancelled.append(target);continue
  # ``Poly.terms()`` returns exact SymPy QQ_I expressions rather than
  # Gaussian-rational carrier objects on all supported SymPy versions.
  # Serialize their canonical strings; the monomial ordering is fixed above,
  # so the resulting digest remains byte-stable and independently replayable.
  sparse=[[list(mon),sp.sstr(coeff)] for mon,coeff in sorted(value.terms())]
  blob=json.dumps(sparse,separators=(',',':')).encode()
  probe=value.eval({L:sp.Integer(6),w:sp.Rational(3,5)})
  layers[str(target)]={'sparse_terms':sparse,'sha256':hashlib.sha256(blob).hexdigest(),
    'term_count':len(sparse),'exact_probe_Lambda6_omega3_over_5':sp.sstr(probe)}
 leading=max(map(int,layers)) if layers else None
 result={'structural_maximum_power':structural,'exact_zero_cancellations':cancelled,'layers':layers,'leading_power':leading,'disposition':'DANGEROUS' if leading is not None and leading>=-1 else 'FINITE_BELOW_P_MINUS_1'}
 out=PKG/'current_artifacts'/f'{a.sector}-{a.left}-{a.right}.json';out.parent.mkdir(exist_ok=True)
 Dl=denominators[a.sector][a.left];Dr=sp.sstr(sp.conjugate(sp.sympify(denominators[a.sector][a.right],locals={'Lambda':L,'omega':w,'I':sp.I})).subs({sp.conjugate(L):L,sp.conjugate(w):w}))
 out.write_text(json.dumps({'schema_version':'polar-current-entry-v1','sector':a.sector,'pair':[a.left,a.right],
  'profile_common_denominators':{a.left:denominators[a.sector][a.left],a.right:denominators[a.sector][a.right]},
  'reported_fraction_denominator':f'({Dl})*({Dr})',
  'result':result,'claim_boundary':'formal radial filtration through p=-2; p>=-1 is the dangerous threshold and reported coefficients are denominator-cleared numerators'},indent=2,sort_keys=True)+'\n');print(out)
if __name__=='__main__':main()
