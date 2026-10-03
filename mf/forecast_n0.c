/* Prediction only: sieve prime exponents and the stated N0 local exclusions.
 * NO q primality test, modular exponentiation, factor search, or census input.
 * Emits per-exponent model means and per-k sums for N0 and L002. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
#include <string.h>
#include <errno.h>

static const int primes[] = {2,3,5,7,11,13,17,19,23,29,31,37,41,43,47};
static long number(const char *s) {
    char *end; errno=0; long n=strtol(s,&end,10);
    if(errno || *end) { fprintf(stderr,"bad integer\n"); exit(2); }
    return n;
}
int main(int argc,char **argv) {
    if(argc!=7) { fprintf(stderr,"lo hi K coefficients means.csv byk.csv\n"); return 2; }
    long lo=number(argv[1]),hi=number(argv[2]),K=number(argv[3]);
    if(lo<3 || hi<lo || hi>100000000 || K<1 || K>1000000) return 2;
    unsigned char *composite=calloc((size_t)hi+1,1), *blocked=malloc((size_t)K+1);
    double *corr=calloc((size_t)K+1,sizeof(double)), *sums=calloc((size_t)K+1,sizeof(double));
    if(!composite || !blocked || !corr || !sums) return 3;
    FILE *cf=fopen(argv[4],"r"); if(!cf) return 4;
    for(long k=1;k<=K;k++) if(fscanf(cf,"%lf",&corr[k])!=1 || !isfinite(corr[k]) || corr[k]<=0) return 4;
    fclose(cf);
    FILE *out=fopen(argv[5],"wx"), *byk=fopen(argv[6],"wx");
    if(!out || !byk) { fprintf(stderr,"output exists or cannot be created\n"); return 4; }
    for(long r=2;r*r<=hi;r++) if(!composite[r])
        for(long j=r*r;j<=hi;j+=r) composite[j]=1;
    double factor=1.;
    for(int i=0;i<15;i++) factor *= (double)primes[i]/(primes[i]-1);
    long count=0;
    for(long p=lo;p<=hi;p++) if(!composite[p]) {
        memset(blocked,0,(size_t)K+1);
        for(int i=1;i<15;i++) {
            int r=primes[i], a=(int)(2*(p%r)%r);
            if(!a) continue;
            int inv=1; while(a*inv%r!=1) inv++;
            int first=r-inv;
            for(long k=first;k<=K;k+=r) blocked[k]=1;
        }
        double n0=0.,l002=0.;
        int odd=(p%4==1 ? 3 : 1);
        for(int part=0;part<2;part++) {
            for(long k=(part==0 ? 4 : odd);k<=K;k+=4) if(!blocked[k]) {
                double q=2.*(double)k*(double)p+1.;
                double w=factor/((double)k*log(q));
                n0+=w; l002+=w*corr[k]; sums[k]+=w;
            }
        }
        fprintf(out,"%ld,%.17g,%.17g\n",p,n0,l002); count++;
    }
    for(long k=1;k<=K;k++) fprintf(byk,"%ld,%.17g\n",k,sums[k]);
    int failed=ferror(out)||ferror(byk); failed |= fclose(out)!=0; failed |= fclose(byk)!=0;
    free(composite); free(blocked); free(corr); free(sums);
    if(failed) return 5;
    printf("{\"exponents\":%ld,\"bounds\":[%ld,%ld,%ld]}\n",count,lo,hi,K);
    return 0;
}
