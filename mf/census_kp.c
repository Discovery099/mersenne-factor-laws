/* Engine A: k inside p, progression sieve, Montgomery modular powering. */
#include <stdint.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
typedef uint64_t U; typedef __uint128_t W;
static const U small[]={3,5,7,11,13,17,19,23,29,31,37,41,43,47};
typedef struct {U n, inv, one, two;} Mont;
static U mm(U a,U b,Mont m) {
    W t=(W)a*b;U c=(U)t*m.inv;U v=(U)((t+(W)c*m.n)>>64);
    return v>=m.n?v-m.n:v;
}
static Mont ctx(U n) {
    U x=1;for(int i=0;i<6;i++)x*=2-n*x;
    U one=(U)(((W)1<<64)%n);Mont m={n,0-x,one,0};m.two=(one*2)%n;return m;
}
static U power(U a,U d,U n) {
    Mont m=ctx(n);U b=(U)((W)a*m.one%n),x=m.one;
    while(d){if(d&1)x=mm(x,b,m);b=mm(b,b,m);d>>=1;}return mm(x,1,m);
}
static int prime(U n) {
    const U bases[]={2,325,9375,28178,450775,9780504,1795265022};
    if(n<2)return 0;if(!(n&1))return n==2;
    U d=n-1;int s=0;while(!(d&1)){d>>=1;s++;}
    for(int i=0;i<7;i++) {U a=bases[i]%n;if(!a)continue;U x=power(a,d,n);
        if(x==1||x==n-1)continue;int j;
        for(j=1;j<s;j++){x=(U)((W)x*x%n);if(x==n-1)break;}if(j==s)return 0;
    }return 1;
}
static int input(const char *s,U *v) {
    if(!*s||*s=='-'||*s=='+')return 0;char *end;errno=0;*v=strtoull(s,&end,10);return !errno&&!*end;
}
int main(int argc,char **argv) {
    U lo,hi,K;
    if(argc!=4||!input(argv[1],&lo)||!input(argv[2],&hi)||!input(argv[3],&K)||lo>hi||K<1
       ||hi>100000000||K>10000000||(W)2*hi*K+1>=((W)1<<63)) {
        fprintf(stderr,"{\"error\":\"invalid or unsupported bounds\"}\n");return 2;
    }
    unsigned char *ps=calloc((size_t)hi+1,1),*bad=malloc((size_t)K+1);
    if(!ps||!bad){free(ps);free(bad);return 3;}
    for(U r=2;r*r<=hi;r++)if(!ps[r])for(U p=r*r;p<=hi;p+=r)ps[p]=1;
    for(U p=lo<3?3:lo;p<=hi;p++)if(!ps[p]) {
        memset(bad,0,(size_t)K+1);
        for(size_t i=0;i<sizeof(small)/sizeof(*small);i++) {
            U r=small[i],step=(2*p)%r;if(!step)continue;
            U inverse=1;while((step*inverse)%r!=1)inverse++;
            for(U k=(r-inverse)%r;k<=K;k+=r)if(2*k*p+1!=r)bad[k]=1;
        }
        for(U k=1;k<=K;k++) {
            if(bad[k])continue;U q=2*k*p+1;if(q%8!=1&&q%8!=7)continue;
            if(power(2,p,q)==1&&(k<=2*p+1||prime(q)))printf("%"PRIu64" %"PRIu64"\n",p,k);
        }
    }
    free(ps);free(bad);return ferror(stdout)?4:0;
}
