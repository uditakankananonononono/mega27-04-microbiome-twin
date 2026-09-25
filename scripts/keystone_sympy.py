"""Symbolic vector-field invariants of cNODE and gLV; preregistration_sympy.md."""
import json
import sympy as sp


def check(f,x):
    h=sum(x[i]*f[i] for i in range(3))
    rhs=[x[i]*(f[i]-h) for i in range(3)]
    tangent=sp.factor(sum(rhs).subs(x[2],1-x[0]-x[1]))
    boundary=[sp.simplify(rhs[i].subs(x[i],0)) for i in range(3)]
    return {'tangent_zero':bool(tangent==0),'boundary_zero':[bool(z==0) for z in boundary]}


def main():
    x=sp.symbols('x0:3'); z=sp.symbols('z0:3'); W=sp.Matrix(3,3,sp.symbols('w0:9')); A=sp.Matrix(3,3,sp.symbols('a0:9')); r=sp.Matrix(sp.symbols('r0:3'))
    J={'tool':'SymPy symbolic algebra','cnode':check(W*sp.Matrix(z),x),'glv':check(r+A*sp.Matrix(x),x)}
    J['G1_pass']=all(q['tangent_zero'] and all(q['boundary_zero']) for q in (J['cnode'],J['glv']))
    J['SY1_pass']=J['G1_pass']
    with open('results/keystone_sympy.json','w') as out: json.dump(J,out,indent=1)
    print(json.dumps(J))
if __name__=='__main__': main()
