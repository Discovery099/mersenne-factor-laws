/* Engine A: k progression sieve, Montgomery exponentiation, p outer loop. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>
#include <errno.h>
typedef uint64_t U; typedef __uint128_t W;
typedef struct {U n,ni,r2;} Mod;
/* n<2^63 ensures t+m*n<2^128 in Montgomery reduction. */
static U mul(U a,U b,Mod c){W t=(W)a*b;U m=(U)t*c.ni;U v=(U)((t+(W)m*c.n)>>64);return v>=c.n?v-c.n:v;}
static Mod mod(U n){U inv=1;for(int j=0;j<6;j++)inv*=2-n*inv;U r=(U)(((W)1<<64)%n);return (Mod){n,0-inv,(U)((W)r*r%n)};}
static U powmod(U a,U e,U n){Mod c=mod(n);U x=mul(a%n,c.r2,c),v=mul(1,c.r2,c);while(e){if(e&1)v=mul(v,x,c);x=mul(x,x,c);e>>=1;}return mul(v,1,c);}
static int prime(U n){const U bs[]={2,3,5,7,11,13,17,19,23,29,31,37};if(n<2)return 0;
    for(int j=0;j<12;j++)if(n%bs[j]==0)return n==bs[j];
    U d=n-1;int s=0;while(!(d&1)){s++;d>>=1;}
    for(int j=0;j<12;j++){U x=powmod(bs[j],d,n);if(x==1||x==n-1)continue;int hit=0;
        for(int a=1;a<s;a++){x=(W)x*x%n;if(x==n-1){hit=1;break;}}if(!hit)return 0;}return 1;}
static U arg(char*s){errno=0;char*end;U v=strtoull(s,&end,10);if(errno||!*s||*s=='-'||*end){fprintf(stderr,"bad argument\n");exit(2);}return v;}
int main(int argc,char**argv){
    if(argc!=4)return 2;
    U lo=arg(argv[1]),hi=arg(argv[2]),K=arg(argv[3]);
    if(lo>hi||hi>100000000||!K||K>10000000||(W)2*hi*K+1>=((W)1<<63)){fprintf(stderr,"unsupported bounds\n");return 2;}
    unsigned char*ps=malloc(hi+1),*bad=malloc(K+1);if(!ps||!bad)return 2;memset(ps,1,hi+1);ps[0]=0;if(hi>=1)ps[1]=0;
    for(U a=2;a*a<=hi;a++)if(ps[a])for(U b=a*a;b<=hi;b+=a)ps[b]=0;
    unsigned char sp[1001];memset(sp,1,sizeof sp);sp[0]=sp[1]=0;
    for(int a=2;a*a<=1000;a++)if(sp[a])for(int b=a*a;b<=1000;b+=a)sp[b]=0;
    U count=0,tests=0;
    for(U p=lo<3?3:lo;p<=hi;p++)if(ps[p]){
        memset(bad,0,K+1);
        for(U r=3;r<=1000;r++)if(sp[r]){U c=(2*p)%r;if(!c)continue;
            U inv=powmod(c,r-2,r),start=(r-inv)%r;if(!start)start=r;
            for(U k=start;k<=K;k+=r)if(2*p*k+1!=r)bad[k]=1;}
        for(U k=1;k<=K;k++){
            if(bad[k]||!((k%4==0)||(k%4==(p%4==1?3:1))))continue;
            U q=2*p*k+1;tests++;if(powmod(2,p,q)!=1)continue;
            if(k<=2*p+1||prime(q)){printf("%"PRIu64" %"PRIu64"\n",p,k);count++;}
        }
    }
    fprintf(stderr,"{\"engine\":\"kp\",\"count\":%"PRIu64",\"modular_tests\":%"PRIu64",\"complete\":true}\n",count,tests);
    free(ps);free(bad);return ferror(stdout)?2:0;
}
