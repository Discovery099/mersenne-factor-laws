/* Engine B: p inside k; fresh sieve of q over integer p; plain remainders. */
#include <stdint.h>
#include <inttypes.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
typedef uint64_t N;
static N modexp(N a,N e,N n) {N v=1;while(e){if(e%2)v=(__uint128_t)v*a%n;e/=2;a=(__uint128_t)a*a%n;}return v;}
static int isprime(N n) {
    const N b[]={2,3,5,7,11,13,17,19,23,29,31,37};
    /* First twelve bases cover >2^64 (Sorenson--Webster). */
    if(n<2)return 0;for(int i=0;i<12;i++)if(n%b[i]==0)return n==b[i];
    N d=n-1;int s=0;while(d%2==0){d/=2;s++;}
    for(int i=0;i<12;i++){N x=modexp(b[i],d,n);if(x==1||x==n-1)continue;int pass=0;
        for(int j=1;j<s;j++){x=(__uint128_t)x*x%n;if(x==n-1){pass=1;break;}}if(!pass)return 0;}
    return 1;
}
typedef struct {N p,k;} Pair;
static int cmp(const void *a,const void *b){const Pair *x=a,*y=b;return x->p!=y->p?(x->p>y->p?1:-1):(x->k>y->k)-(x->k<y->k);}
static int readnum(char *s,N *n){if(!*s||*s=='-'||*s=='+')return 0;char *e;errno=0;*n=strtoull(s,&e,10);return !errno&&!*e;}
int main(int argc,char **argv) {
    N lo,hi,K;
    if(argc!=4||!readnum(argv[1],&lo)||!readnum(argv[2],&hi)||!readnum(argv[3],&K)||lo>hi||K<1
       ||hi>100000000||K>10000000||(__uint128_t)2*hi*K+1>=((__uint128_t)1<<63)) {
        fprintf(stderr,"{\"error\":\"invalid or unsupported bounds\"}\n");return 2;
    }
    if(hi<3)return 0;if(lo<3)lo=3;size_t width=(size_t)(hi-lo+1);
    unsigned char *composite=calloc((size_t)hi+1,1),*strike=malloc(width);
    N *primes=malloc(((size_t)hi+1)*sizeof(N));Pair *out=NULL;size_t count=0,cap=0,np=0;
    if(!composite||!strike||!primes){free(composite);free(strike);free(primes);return 3;}
    for(N n=2;n<=hi;n++)if(!composite[n]) {
        if(n>=lo)primes[np++]=n;
        if(n<=hi/n)for(N m=n*n;m<=hi;m+=n)composite[m]=1;
    }
    const N sieve[]={3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97};
    for(N k=1;k<=K;k++) {
        if(k%4==2)continue;memset(strike,0,width);
        for(size_t i=0;i<sizeof(sieve)/sizeof(*sieve);i++) {
            N r=sieve[i],a=(2*k)%r;if(!a)continue;N root=0;while((a*root+1)%r)root++;
            N first=lo+(root+r-lo%r)%r;
            for(N p=first;p<=hi;p+=r)if(2*k*p+1!=r)strike[p-lo]=1;
        }
        for(size_t j=0;j<np;j++) {
            N p=primes[j];if(strike[p-lo])continue;N q=2*k*p+1;
            if((q&7)!=1&&(q&7)!=7)continue;
            if(modexp(2,p,q)!=1||!isprime(q))continue;
            if(count==cap){cap=cap?cap*2:128;Pair *tmp=realloc(out,cap*sizeof(Pair));if(!tmp){free(out);free(composite);free(strike);free(primes);return 3;}out=tmp;}
            out[count++]=(Pair){p,k};
        }
    }
    if(count)qsort(out,count,sizeof(Pair),cmp);
    for(size_t i=0;i<count;i++)printf("%"PRIu64" %"PRIu64"\n",out[i].p,out[i].k);
    free(out);free(composite);free(strike);free(primes);return ferror(stdout)?4:0;
}
