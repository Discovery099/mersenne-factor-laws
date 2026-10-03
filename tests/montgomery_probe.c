/* Test-only access to engine A's actual modular arithmetic implementation. */
#define main census_program_main
#include "../mf/census_kp.c"
#undef main
int main(void) {
    U a,e,n;
    while(scanf("%"SCNu64" %"SCNu64" %"SCNu64,&a,&e,&n)==3) {
        if(n<3 || !(n&1) || n>=((U)1<<63))return 2;
        printf("%"PRIu64"\n",power(a,e,n));
    }
    return ferror(stdin)?1:0;
}
