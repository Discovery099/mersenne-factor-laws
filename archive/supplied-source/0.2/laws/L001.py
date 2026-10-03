"""Zero-fit Wagstaff/BH/Kummer predictor. No observed-count imports."""
import math
import numpy as np
from numpy.polynomial import chebyshev as ch
from mf.stats import primes
FITTED_PARAMETERS=0
# This is a mathematical constant, computed and bounded in constants.json.
C2=0.6601618158468696
NODES=32

def coefficients(K):
    k=np.arange(1,K+1,dtype=np.int64)
    s=np.full(K,2*C2)
    for r in primes(K):
        if r>2:s[r-1::r]*=(r-1)/(r-2)
    return k,s/k

def weight(p,k):
    if k%4 not in ((0,3) if p%4==1 else (0,1)):return 0.
    n=k;f=1.;r=2
    while r*r<=n:
        if n%r==0:
            if r>2:f*=(r-1)/(r-2)
            while n%r==0:n//=r
        r+=1
    if n>2:f*=(n-1)/(n-2)
    return 2*C2*f/(k*math.log(2*k*p))

def predict(bounds):
    lo,hi,K=bounds
    ps=np.array([p for p in primes(hi) if p>=max(3,lo)],dtype=np.int64)
    k,a=coefficients(K);nb=K.bit_length();b=np.floor(np.log2(k)).astype(int)
    joint=np.zeros((nb,120));mu=np.zeros(len(ps))
    if len(ps)==0:return {"joint":joint.tolist(),"mu":[],"exponents":0}
    mid=(math.log(lo)+math.log(hi))/2;half=(math.log(hi)-math.log(lo))/2
    nodes=np.cos(np.pi*(np.arange(NODES)+.5)/NODES)
    lp=np.log(ps);x=(lp-mid)/half if half else np.zeros(len(ps))
    for c in (1,3):
        sel=(ps%4==c);ks=(k%4==0)|(k%4==(3 if c==1 else 1))
        kk=k[ks];aa=a[ks];idx=b[ks]*120+kk%120
        values=np.array([np.bincount(idx,weights=aa/(np.log(2*kk)+mid+half*t),minlength=nb*120) for t in nodes])
        co=ch.chebfit(nodes,values,NODES-1)
        # Evaluate moments instead of constructing a primes-by-cells array.
        moments=ch.chebvander(x[sel],NODES-1).sum(axis=0)
        joint+=(moments@co).reshape(nb,120)
        mu[sel]=ch.chebval(x[sel],co.sum(axis=1))
    return {"joint":joint.tolist(),"mu":mu.tolist(),"exponents":len(ps)}

def summaries(raw):
    j=np.array(raw['joint']);mu=np.array(raw['mu']);cells={"total":float(j.sum())}
    cells.update({f"dyadic:{i}":float(v) for i,v in enumerate(j.sum(axis=1))})
    for m in (3,4,5,8,12):
        for r in range(m):cells[f"mod{m}:{r}"]=float(j[:,np.arange(120)%m==r].sum())
    cells['ge1']=float((-np.expm1(-mu)).sum())
    cells['ge2']=float((1-(1+mu)*np.exp(-mu)).sum())
    prob=np.exp(-mu);cdf=prob.copy();maximum=0.
    for t in range(1,33):
        maximum+=float(-np.expm1(np.log(np.minimum(cdf,1)).sum()))
        prob*=mu/t;cdf+=prob
    cells['maximum']=maximum
    return cells
