/* Independent acceptance checker. GNU mini-gmp provides arbitrary integers. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "mini-gmp.h"

static const unsigned long bases[]={2,3,5,7,11,13,17,19,23,29,31,37,41};
static int number(mpz_t z, const char *s) {
    if(!s || !*s) return 0;
    for(const char *t=s; *t; ++t) if(!isdigit((unsigned char)*t)) return 0;
    return mpz_set_str(z,s,10)==0;
}
static int prime(const mpz_t n) {
    mpz_t lim,d,x,a,nm; mpz_init(lim); mpz_init(d); mpz_init(x); mpz_init(a); mpz_init(nm);
    mpz_set_str(lim,"3317044064679887385961981",10);
    int ok=0;
    if(mpz_cmp_ui(n,2)<0 || mpz_cmp(n,lim)>=0) goto done;
    for(size_t i=0;i<13;i++) if(mpz_fdiv_ui(n,bases[i])==0) {
        ok=mpz_cmp_ui(n,bases[i])==0; goto done;
    }
    mpz_sub_ui(nm,n,1); mpz_set(d,nm);
    unsigned long s=0;
    while(mpz_fdiv_ui(d,2)==0) {mpz_fdiv_q_2exp(d,d,1); s++;}
    for(size_t i=0;i<13;i++) {
        mpz_set_ui(a,bases[i]); mpz_powm(x,a,d,n);
        if(mpz_cmp_ui(x,1)==0 || mpz_cmp(x,nm)==0) continue;
        unsigned long j;
        for(j=1;j<s;j++) {mpz_mul(x,x,x);mpz_mod(x,x,n);if(mpz_cmp(x,nm)==0)break;}
        if(j==s) goto done;
    }
    ok=1;
done:
    mpz_clear(lim);mpz_clear(d);mpz_clear(x);mpz_clear(a);mpz_clear(nm);return ok;
}
static int pock(const mpz_t n, int count, char **rows) {
    mpz_t F,r,e,a,nm,t,u,g,seen[128];
    if(count<1 || count>128) return 0;
    mpz_init(F);mpz_set_ui(F,1);mpz_init(r);mpz_init(e);mpz_init(a);
    mpz_init(nm);mpz_sub_ui(nm,n,1);mpz_init(t);mpz_init(u);mpz_init(g);
    for(int i=0;i<count;i++) mpz_init(seen[i]);
    int ok=0;
    for(int i=0;i<count;i++) {
        char *s=malloc(strlen(rows[i])+1);if(!s)goto done;strcpy(s,rows[i]);
        char *c=strchr(s,':'), *d=c?strchr(c+1,':'):NULL;
        if(!c||!d||strchr(d+1,':')) {free(s);goto done;}
        *c=0;*d=0;
        int parsed=number(r,s)&&number(e,c+1)&&number(a,d+1);free(s);
        if(!parsed || !prime(r) || mpz_cmp_ui(e,1)<0 || mpz_cmp_ui(e,mpz_sizeinbase(n,2))>0
            ||mpz_cmp_ui(a,1)<=0||mpz_cmp(a,n)>=0) goto done;
        for(int j=0;j<i;j++) if(mpz_cmp(seen[j],r)==0)goto done;
        mpz_set(seen[i],r);mpz_pow_ui(t,r,mpz_get_ui(e));mpz_mul(F,F,t);
        mpz_mod(t,nm,F);if(mpz_sgn(t)!=0)goto done;
        mpz_powm(t,a,nm,n);if(mpz_cmp_ui(t,1))goto done;
        mpz_fdiv_q(u,nm,r);mpz_powm(t,a,u,n);mpz_sub_ui(t,t,1);mpz_gcd(g,t,n);
        if(mpz_cmp_ui(g,1))goto done;
    }
    mpz_mul(t,F,F);ok=mpz_cmp(t,n)>0;
done:
    for(int i=0;i<count;i++)mpz_clear(seen[i]);
    mpz_clear(F);mpz_clear(r);mpz_clear(e);mpz_clear(a);mpz_clear(nm);mpz_clear(t);mpz_clear(u);mpz_clear(g);
    return ok;
}
static int check(int argc,char **argv) {
    mpz_t p,q,k,t,u;mpz_init(p);mpz_init(q);mpz_init(k);mpz_init(t);mpz_init(u);
    int ok=0; const char *method="none";
    if(argc<2 || !number(p,argv[0]) || !number(q,argv[1]))goto done;
    if(mpz_cmp_ui(p,3)<0 || !prime(p)||mpz_cmp_ui(q,3)<0)goto done;
    mpz_mul_ui(t,p,2);mpz_sub_ui(u,q,1);mpz_mod(k,u,t);if(mpz_sgn(k))goto done;
    mpz_fdiv_q(k,u,t);unsigned long mod=mpz_fdiv_ui(q,8);if(mod!=1&&mod!=7)goto done;
    mpz_set_ui(u,2);mpz_powm(u,u,p,q);if(mpz_cmp_ui(u,1))goto done;
    if(argc>2) {ok=pock(q,argc-2,argv+2);method="Pocklington";}
    else {mpz_add_ui(t,t,1);if(mpz_cmp(k,t)<=0){ok=1;method="L2";}
        else {ok=prime(q);method="deterministic-MR-13";}}
done:
    printf("{\"valid\":%s,\"primality_method\":\"%s\"}\n",ok?"true":"false",ok?method:"none");
    mpz_clear(p);mpz_clear(q);mpz_clear(k);mpz_clear(t);mpz_clear(u);return ok;
}
int main(int argc,char **argv) {
    if(argc==2 && strcmp(argv[1],"--batch")==0) {
        char line[65536];int all=1;
        while(fgets(line,sizeof(line),stdin)) {
            if(!strchr(line,'\n')&&!feof(stdin)){fprintf(stderr,"oversized line\n");return 2;}
            char *tokens[131];int n=0;char *s=strtok(line," \r\n\t");
            while(s&&n<131){tokens[n++]=s;s=strtok(NULL," \r\n\t");}
            if(s||n>130){puts("{\"valid\":false}");all=0;continue;}
            if(!check(n,tokens))all=0;
        }
        return all?0:1;
    }
    return check(argc-1,argv+1)?0:1;
}
