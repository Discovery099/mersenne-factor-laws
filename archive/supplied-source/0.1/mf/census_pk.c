/* Engine B: p progression sieve, ordinary uint128 powering, k outer loop. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>
#include <errno.h>
typedef uint64_t U;
typedef __uint128_t W;
typedef struct {U p,k;} Pair;
static U power(U a,U b,U m){U out=1;for(;b;b/=2){if(b%2)out=(W)out*a%m;a=(W)a*a%m;}return out;}
static int isprime(U n){
    if(n<2)return 0;
    U bases[]={2,3,5,7,11,13,17,19,23,29,31,37};
    for(unsigned i=0;i<12;i++)if(n%bases[i]==0)return n==bases[i];
    U e=n-1;unsigned s=0;while(e%2==0){e/=2;s++;}
    for(unsigned i=0;i<12;i++){U x=power(bases[i],e,n);if(x==1||x==n-1)continue;unsigned j;
        for(j=1;j<s;j++){x=(W)x*x%n;if(x==n-1)break;}if(j==s)return 0;}return 1;
}
static int cmp(const void*a,const void*b){const Pair*x=a,*y=b;return x->p!=y->p?(x->p>y->p?1:-1):(x->k>y->k)-(x->k<y->k);}
static U get(char*s){errno=0;char*e;U v=strtoull(s,&e,10);if(errno||!*s||*s=='-'||*e)exit(2);return v;}
int main(int argc,char**argv){
    if(argc!=4)return 2;
    U low=get(argv[1]),high=get(argv[2]),maxk=get(argv[3]);
    if(low>high||high>100000000||maxk<1||maxk>10000000||(W)2*high*maxk+1>=((W)1<<63))return 2;
    unsigned char *composite=calloc(high+1,1),*blocked=calloc(high-low+1,1);U*plist=malloc((high+1)*sizeof(U));
    if(!composite||!blocked||!plist)return 2;
    U np=0;
    for(U n=2;n<=high;n++)if(!composite[n]){if(n>=low&&n>2)plist[np++]=n;if(n<=high/n)for(U t=n*n;t<=high;t+=n)composite[t]=1;}
    U small[200],ns=0;for(U n=3;n<=997;n+=2){int ok=1;for(U j=2;j*j<=n;j++)if(n%j==0){ok=0;break;}if(ok)small[ns++]=n;}
    size_t size=0,capacity=128;Pair*found=malloc(capacity*sizeof(Pair));if(!found)return 2;
    U tests=0;
    for(U k=1;k<=maxk;k++){
        memset(blocked,0,high-low+1);
        for(U i=0;i<ns;i++){U r=small[i],c=2*k%r;if(!c)continue;U residue=r-power(c,r-2,r);
            U start=low+(residue+r-low%r)%r;
            for(U p=start;p<=high;p+=r)if(2*k*p+1!=r)blocked[p-low]=1;}
        for(U i=0;i<np;i++){U p=plist[i],q=2*k*p+1;if(blocked[p-low]||(q%8!=1&&q%8!=7))continue;
            tests++;if(power(2,p,q)!=1||!isprime(q))continue;
            if(size==capacity){capacity*=2;Pair*t=realloc(found,capacity*sizeof(Pair));if(!t)return 2;found=t;}found[size++]=(Pair){p,k};}
    }
    qsort(found,size,sizeof(Pair),cmp);for(size_t i=0;i<size;i++)printf("%"PRIu64" %"PRIu64"\n",found[i].p,found[i].k);
    fprintf(stderr,"{\"engine\":\"pk\",\"count\":%zu,\"modular_tests\":%"PRIu64",\"complete\":true}\n",size,tests);
    free(composite);free(blocked);free(plist);free(found);return ferror(stdout)?2:0;
}
