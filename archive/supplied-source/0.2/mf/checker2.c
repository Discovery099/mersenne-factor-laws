/* Independent bounded checker. No search arithmetic is imported. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>
#include <errno.h>
#include <ctype.h>
#include <string.h>
typedef uint64_t U;
typedef __uint128_t W;
static U power(U a,U e,U n){U v=1;while(e){if(e&1)v=(W)v*a%n;a=(W)a*a%n;e>>=1;}return v;}
static U gcd64(U a,U b){while(b){U t=a%b;a=b;b=t;}return a;}
static int prime(U n){
    static const U b[]={2,3,5,7,11,13,17,19,23,29,31,37};
    if(n<2)return 0;
    for(int i=0;i<12;i++)if(n%b[i]==0)return n==b[i];
    U d=n-1;int s=0;while(!(d&1)){d>>=1;s++;}
    for(int i=0;i<12;i++){U x=power(b[i],d,n);if(x==1||x==n-1)continue;
        int hit=0;for(int j=1;j<s;j++){x=(W)x*x%n;if(x==n-1){hit=1;break;}}if(!hit)return 0;}
    return 1;
}
static int parse(const char*s,U*out){
    if(!s||!*s)return 0;
    for(const char*t=s;*t;t++)if(!isdigit((unsigned char)*t))return 0;
    errno=0;char*end;*out=strtoull(s,&end,10);return !errno&&!*end;
}
/* Certificate text consists of distinct r e a lines, equivalent to Python JSON factors. */
static int cert(U n,const char*path){
    FILE*f=fopen(path,"r");if(!f)return 0;
    char line[256],rs[80],es[80],as[80],extra[2];U seen[64],F=1;int count=0,ok=1;
    while(fgets(line,sizeof line,f)){
        U r,e,a;if(sscanf(line,"%79s %79s %79s %1s",rs,es,as,extra)!=3||!parse(rs,&r)||!parse(es,&e)||!parse(as,&a)
           ||count>=64||e<1||e>64||!prime(r)||a<=1||a>=n){ok=0;break;}
        for(int j=0;j<count;j++)if(seen[j]==r)ok=0;
        if(!ok)break;
        seen[count++]=r;
        for(U j=0;j<e;j++){W t=(W)F*r;if(t>n-1){ok=0;break;}F=(U)t;}if(!ok||(n-1)%F){ok=0;break;}
        U x=power(a,(n-1)/r,n);U diff=x?x-1:n-1;
        if(power(a,n-1,n)!=1||gcd64(diff,n)!=1){ok=0;break;}
    }
    if(ferror(f))ok=0;
    fclose(f);return ok&&count&&(W)F*F>n;
}
static int verify(U p,U q,const char*c,U*k,const char**method){
    if(p<3||!prime(p)||q<3||p>(q-1)/2)return 0;
    if((q-1)%(2*p)||(q%8!=1&&q%8!=7)||power(2,p,q)!=1)return 0;
    *k=(q-1)/(2*p);
    if(c){*method="Pocklington";return cert(q,c);}
    if((W)*k<=2*(W)p+1){*method="L2";return 1;}
    *method="deterministic-MR-12";return prime(q);
}
int main(int argc,char**argv){
    if(argc==2&&!strcmp(argv[1],"--batch")){
        char s[256],ps[90],qs[90],ex[2];U p,q,k;const char*m="";
        while(fgets(s,sizeof s,stdin)){
            int ok=sscanf(s,"%89s %89s %1s",ps,qs,ex)==2&&parse(ps,&p)&&parse(qs,&q);
            if(!ok){puts("{\"valid\":false,\"status\":\"unsupported\"}");continue;}
            ok=verify(p,q,NULL,&k,&m);printf("{\"valid\":%s}\n",ok?"true":"false");
        }return ferror(stdin)?2:0;
    }
    U p,q,k;const char*m="";
    if((argc!=3&&argc!=4)||!parse(argv[1],&p)||!parse(argv[2],&q)){
        puts("{\"valid\":false,\"status\":\"unsupported\",\"reason\":\"uint64 inputs required\"}");return 2;}
    int ok=verify(p,q,argc==4?argv[3]:NULL,&k,&m);
    if(ok)printf("{\"valid\":true,\"k\":%"PRIu64",\"primality_method\":\"%s\"}\n",k,m);
    else puts("{\"valid\":false}");
    return ok?0:1;
}
