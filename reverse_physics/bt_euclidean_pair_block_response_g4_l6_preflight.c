#include <complex.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define L 6
#define N (L*L*L*L)
#define MAXU 12
#define MAXW 4

typedef struct { int x[4]; } Coord;
typedef struct { int deg; double complex a[MAXU+1][MAXU+1]; } Poly;
typedef struct { Poly v, d[2]; } Dual;
typedef struct { int n[4]; double amp; } Wave;

static const double CB[2][2]={{9.0/616.0,1.0/308.0},{1.0/308.0,9.0/616.0}};
static Coord dirs[8], affected[16];
static int naffected;
static double gmom[MAXU+2][MAXU+2];

static Coord addc(Coord a, Coord b){Coord c;for(int j=0;j<4;j++)c.x[j]=a.x[j]+b.x[j];return c;}
static int eqc(Coord a, Coord b){for(int j=0;j<4;j++)if(a.x[j]!=b.x[j])return 0;return 1;}
static int inside(Coord c){Coord o={{0,0,0,0}},e={{1,0,0,0}};if(eqc(c,o))return 0;if(eqc(c,e))return 1;return -1;}
static void init(void){
 int z=0;for(int ax=0;ax<4;ax++)for(int s=-1;s<=1;s+=2){Coord d={{0,0,0,0}};d.x[ax]=s;dirs[z++]=d;}
 Coord base[2]={{{0,0,0,0}},{{1,0,0,0}}};naffected=0;
 for(int b=0;b<2;b++)for(int q=-1;q<8;q++){
  Coord c=q<0?base[b]:addc(base[b],dirs[q]);int seen=0;
  for(int i=0;i<naffected;i++)if(eqc(c,affected[i]))seen=1;
  if(!seen)affected[naffected++]=c;
 }
 memset(gmom,0,sizeof(gmom));gmom[0][0]=1.0;
 for(int total=2;total<=MAXU+1;total+=2)for(int a=0;a<=total;a++){
  int b=total-a;if(a){
   double v=0;if(a>=2)v+=(a-1)*CB[0][0]*gmom[a-2][b];if(b)v+=b*CB[0][1]*gmom[a-1][b-1];gmom[a][b]=v;
  }else gmom[a][b]=(b-1)*CB[1][1]*gmom[0][b-2];
 }
}
static void pzero(Poly*p){memset(p,0,sizeof(*p));p->deg=0;}
static void pconst(Poly*p,double complex z){pzero(p);p->a[0][0]=z;}
static void paddto(Poly*out,const Poly*p){if(p->deg>out->deg)out->deg=p->deg;for(int a=0;a<=p->deg;a++)for(int b=0;b<=p->deg-a;b++)out->a[a][b]+=p->a[a][b];}
static void pscale(Poly*out,const Poly*p,double complex z){pzero(out);out->deg=p->deg;for(int a=0;a<=p->deg;a++)for(int b=0;b<=p->deg-a;b++)out->a[a][b]=p->a[a][b]*z;}
static void pmul(Poly*out,const Poly*p,const Poly*q){
 pzero(out);out->deg=p->deg+q->deg<MAXU?p->deg+q->deg:MAXU;for(int a=0;a<=p->deg;a++)for(int b=0;b<=p->deg-a;b++)if(cabs(p->a[a][b])>0)
 for(int c=0;c<=q->deg&&a+b+c<=MAXU;c++)for(int d=0;d<=q->deg-c&&a+b+c+d<=MAXU;d++)if(cabs(q->a[c][d])>0)out->a[a+c][b+d]+=p->a[a][b]*q->a[c][d];
}
static void dzero(Dual*x){pzero(&x->v);pzero(&x->d[0]);pzero(&x->d[1]);}
static void daddto(Dual*out,const Dual*x){paddto(&out->v,&x->v);paddto(&out->d[0],&x->d[0]);paddto(&out->d[1],&x->d[1]);}
static void dscale(Dual*out,const Dual*x,double complex z){pscale(&out->v,&x->v,z);pscale(&out->d[0],&x->d[0],z);pscale(&out->d[1],&x->d[1],z);}
static void dmul(Dual*out,const Dual*x,const Dual*y){
 Poly t1,t2;pmul(&out->v,&x->v,&y->v);
 for(int ax=0;ax<2;ax++){pmul(&t1,&x->d[ax],&y->v);pmul(&t2,&x->v,&y->d[ax]);paddto(&t1,&t2);out->d[ax]=t1;}
}
static double binom3(int n,int a,int b){
 static const double fact[14]={1,1,2,6,24,120,720,5040,40320,362880,3628800,39916800,479001600,6227020800.0};
 return fact[n]/(fact[a]*fact[b]*fact[n-a-b]);
}
static double complex ipowc(double complex z,int n){double complex out=1;for(int j=0;j<n;j++)out*=z;return out;}
static double ipowd(double z,int n){double out=1;for(int j=0;j<n;j++)out*=z;return out;}
static void edgepower(Dual*out,double complex c,int u0,int u1,int n,int dq0,int dq1){
 dzero(out);out->v.deg=n;out->d[0].deg=out->d[1].deg=n-1;for(int a=0;a<=n;a++)for(int b=0;b<=n-a;b++){
  int r=n-a-b;double complex z=binom3(n,a,b)*ipowc(c,r)*ipowd((double)u0,a)*ipowd((double)u1,b);out->v.a[a][b]+=z;
 }
 if(n>0)for(int a=0;a<n;a++)for(int b=0;b<n-a;b++){
  int r=n-1-a-b;double complex z=n*binom3(n-1,a,b)*ipowc(c,r)*ipowd((double)u0,a)*ipowd((double)u1,b);out->d[0].a[a][b]+=dq0*z;out->d[1].a[a][b]+=dq1*z;
 }
}
static double omega2(const int k[4]){double w=0;for(int j=0;j<4;j++)w+=2.0*(1.0-cos(2.0*M_PI*k[j]/L));return w*w;}
static double complex phase(const int k[4],Coord c){int dot=0;for(int j=0;j<4;j++)dot+=k[j]*c.x[j];return cexp(I*2.0*M_PI*dot/L);}
static double complex raw(const Wave*w,int nw,Coord c){double complex z=0;for(int q=0;q<nw;q++)z+=w[q].amp*phase(w[q].n,c);return z;}
static void field(Poly*out,const Wave*w,int nw,Coord c,const double complex center[2]){
 pconst(out,inside(c)>=0?center[inside(c)]:raw(w,nw,c));int a=inside(c);if(a==0){out->a[1][0]+=1;out->deg=1;}else if(a==1){out->a[0][1]+=1;out->deg=1;}
}
static double complex integrate(const Poly*p,int observed){double complex z=0;for(int a=0;a<=p->deg;a++)for(int b=0;b<=p->deg-a;b++)z+=p->a[a][b]*gmom[a+observed][b];return z;}

static void response(const Wave*w,int nw,int maxorder,double complex out[2][5]){
 Coord base[2]={{{0,0,0,0}},{{1,0,0,0}}};double complex kval[2]={0,0},center[2];
 for(int b=0;b<2;b++)for(int q=0;q<nw;q++)kval[b]+=w[q].amp*omega2(w[q].n)*phase(w[q].n,base[b]);
 for(int a=0;a<2;a++){center[a]=raw(w,nw,base[a]);for(int b=0;b<2;b++)center[a]-=CB[a][b]*kval[b];}
 Dual U[4];for(int j=0;j<4;j++)dzero(&U[j]);
 for(int iv=0;iv<naffected;iv++){
  Dual jet[6];for(int p=1;p<=5;p++)dzero(&jet[p]);
  for(int id=0;id<8;id++){
   Coord v=affected[iv],nb=addc(v,dirs[id]);Poly fv,fn;field(&fv,w,nw,v,center);field(&fn,w,nw,nb,center);
   double complex c=fn.a[0][0]-fv.a[0][0];int u0=(int)llround(creal(fn.a[1][0]-fv.a[1][0]));int u1=(int)llround(creal(fn.a[0][1]-fv.a[0][1]));
   int dq0=nb.x[0]*nb.x[0]-v.x[0]*v.x[0],dq1=nb.x[1]*nb.x[1]-v.x[1]*v.x[1];
   for(int p=1;p<=5;p++){Dual pow;edgepower(&pow,c,u0,u1,p,dq0,dq1);daddto(&jet[p],&pow);}
  }
  Dual t1,row;
  dmul(&t1,&jet[1],&jet[2]);dscale(&row,&t1,0.5);daddto(&U[0],&row);
  dmul(&t1,&jet[2],&jet[2]);dscale(&row,&t1,1.0/8);daddto(&U[1],&row);dmul(&t1,&jet[1],&jet[3]);dscale(&row,&t1,1.0/6);daddto(&U[1],&row);
  dmul(&t1,&jet[2],&jet[3]);dscale(&row,&t1,1.0/12);daddto(&U[2],&row);dmul(&t1,&jet[1],&jet[4]);dscale(&row,&t1,1.0/24);daddto(&U[2],&row);
  dmul(&t1,&jet[3],&jet[3]);dscale(&row,&t1,1.0/72);daddto(&U[3],&row);dmul(&t1,&jet[2],&jet[4]);dscale(&row,&t1,1.0/48);daddto(&U[3],&row);dmul(&t1,&jet[1],&jet[5]);dscale(&row,&t1,1.0/120);daddto(&U[3],&row);
 }
 for(int j=0;j<maxorder;j++){U[j].v.a[0][0]=0;U[j].d[0].a[0][0]=0;U[j].d[1].a[0][0]=0;}
 Dual ex[5];dzero(&ex[0]);ex[0].v.a[0][0]=1;
 for(int n=1;n<=maxorder;n++){Dual sum,prod,tmp;dzero(&sum);for(int j=1;j<=n;j++){dmul(&prod,&U[j-1],&ex[n-j]);dscale(&tmp,&prod,(double)j);daddto(&sum,&tmp);}dscale(&ex[n],&sum,-1.0/n);}
 double complex z[5]={0},dz[2][5]={{0}},num[5]={0},dnum[2][5]={{0}},m[5]={0},dm[2][5]={{0}};
 for(int n=0;n<=maxorder;n++){z[n]=integrate(&ex[n].v,0);num[n]=integrate(&ex[n].v,1);for(int ax=0;ax<2;ax++){dz[ax][n]=integrate(&ex[n].d[ax],0);dnum[ax][n]=integrate(&ex[n].d[ax],1);}}
 for(int n=0;n<=maxorder;n++){
  m[n]=num[n];for(int j=1;j<=n;j++)m[n]-=z[j]*m[n-j];
  for(int ax=0;ax<2;ax++){dm[ax][n]=dnum[ax][n];for(int j=1;j<=n;j++)dm[ax][n]-=dz[ax][j]*m[n-j]+z[j]*dm[ax][n-j];out[ax][n]=dm[ax][n];}
 }
}
static double complex orient(const double complex r[2][5],int n){return r[0][n]/8.0+3.0*r[1][n]/8.0;}
static void negk(int out[4],const int k[4]){for(int j=0;j<4;j++)out[j]=(L-k[j])%L;}
static double complex topvertex(int order,const int mom[MAXW][4]){
 double complex total=0,r[2][5];for(int mask=0;mask<(1<<order);mask++){
  Wave w[MAXW];int nw=0,bits=0;for(int q=0;q<order;q++)if(mask&(1<<q)){memcpy(w[nw].n,mom[q],sizeof(w[nw].n));w[nw].amp=1;nw++;bits++;}
  response(w,nw,order,r);double s=((order-bits)&1)?-1:1;total+=s*orient(r,order);
 }return total;
}
static void indexk(int index,int k[4]){for(int j=3;j>=0;j--){k[j]=index%L;index/=L;}}
static void addk(int out[4],const int a[4],const int b[4]){for(int j=0;j<4;j++)out[j]=(a[j]+b[j])%L;}
static void subk(int out[4],const int a[4],const int b[4]){for(int j=0;j<4;j++)out[j]=(a[j]-b[j]+L)%L;}
static double complex Bvertex(int n,const int mom[MAXW][4]){
 double complex z=0;for(int e=0;e<8;e++){double complex p=1;for(int q=0;q<n;q++)p*=phase(mom[q],dirs[e])-1.0;z+=p;}return z;
}
static double complex gamma_vertex(int n,const int mom[MAXW][4]){
 double complex z=0;for(int mask=1;mask<(1<<n)-1;mask++){
  int left[MAXW][4],right[MAXW][4],nl=0,nr=0;for(int q=0;q<n;q++)if(mask&(1<<q))memcpy(left[nl++],mom[q],sizeof(left[0]));else memcpy(right[nr++],mom[q],sizeof(right[0]));
  z+=Bvertex(nl,left)*Bvertex(nr,right);
 }return z/2.0;
}
static double complex mixed_f4_at_scale(const int k[4],const int mk[4],double scale){
 double complex total=0,r[2][5];for(int sa=-1;sa<=1;sa+=2)for(int sb=-1;sb<=1;sb+=2){Wave w[2];memcpy(w[0].n,k,sizeof(w[0].n));memcpy(w[1].n,mk,sizeof(w[1].n));w[0].amp=sa*scale;w[1].amp=sb*scale;response(w,2,4,r);total+=sa*sb*orient(r,4);}return total/4.0;
}
static double complex f42_vertex(const int k[4],const int mk[4]){double complex d1=mixed_f4_at_scale(k,mk,1),d2=mixed_f4_at_scale(k,mk,2);return (16.0*d1-d2)/12.0;}

int main(int argc,char**argv){
 init();int outer_limit=argc>1?atoi(argv[1]):N;if(outer_limit<1||outer_limit>N)outer_limit=N;printf("affected=%d outer_limit=%d\n",naffected,outer_limit);
 double complex r0[2][5];response(NULL,0,4,r0);double complex f20=orient(r0,2),f40=orient(r0,4);printf("F20 %.17g F40 %.17g\n",creal(f20),creal(f40));
 static int modes[N][4];static double g[N];static double complex f22[N],f42[N];
 #pragma omp parallel for schedule(dynamic)
 for(int ix=0;ix<N;ix++){int mk[4],mom[4][4]={{0}};indexk(ix,modes[ix]);negk(mk,modes[ix]);memcpy(mom[0],modes[ix],sizeof(mom[0]));memcpy(mom[1],mk,sizeof(mom[1]));double w2=omega2(modes[ix]);g[ix]=w2>1e-24?1.0/w2:0;f22[ix]=topvertex(2,mom);f42[ix]=f42_vertex(modes[ix],mk);}
 double s2=0,s42=0;for(int ix=0;ix<N;ix++){s2+=creal(f22[ix])*g[ix];s42+=creal(f42[ix])*g[ix];}
 double b2=creal(f20)+s2/(2.0*N);printf("b2 %.17g expected %.17g error %.3g\n",b2,956585197.0/10069092633600.0,b2-956585197.0/10069092633600.0);printf("f42_one_loop %.17g\n",s42/(2.0*N));fflush(stdout);
 double sf44=0,sf33=0,sf22g4=0,sf22g3=0;int done=0;
 #pragma omp parallel for schedule(dynamic) reduction(+:sf44,sf33,sf22g4,sf22g3)
 for(int ix=0;ix<outer_limit;ix++){
  int k[4],mk[4];memcpy(k,modes[ix],sizeof(k));negk(mk,k);double local44=0,local33=0,local22g4=0,local22g3=0;
  for(int iy=0;iy<N;iy++){
   int l[4],ml[4],sum[4],msum[4],kml[4],lmk[4];memcpy(l,modes[iy],sizeof(l));negk(ml,l);addk(sum,k,l);negk(msum,sum);subk(kml,k,l);subk(lmk,l,k);
   int mom4[4][4];memcpy(mom4[0],k,sizeof(k));memcpy(mom4[1],mk,sizeof(k));memcpy(mom4[2],l,sizeof(k));memcpy(mom4[3],ml,sizeof(k));
   int mom3[4][4];memcpy(mom3[0],k,sizeof(k));memcpy(mom3[1],l,sizeof(k));memcpy(mom3[2],msum,sizeof(k));
   double complex F44=topvertex(4,mom4),F33=topvertex(3,mom3);
   int opp3[4][4];memcpy(opp3[0],mk,sizeof(k));memcpy(opp3[1],ml,sizeof(k));memcpy(opp3[2],sum,sizeof(k));
   double complex G3=gamma_vertex(3,opp3),G4=gamma_vertex(4,mom4);
   int ga[4][4],gb[4][4];memcpy(ga[0],mk,sizeof(k));memcpy(ga[1],l,sizeof(k));memcpy(ga[2],kml,sizeof(k));memcpy(gb[0],k,sizeof(k));memcpy(gb[1],ml,sizeof(k));memcpy(gb[2],lmk,sizeof(k));
   double complex G3a=gamma_vertex(3,ga),G3b=gamma_vertex(3,gb);
   local44+=creal(F44)*g[ix]*g[iy];local33+=creal(F33*G3)*g[ix]*g[iy]*g[(sum[0]*L+sum[1])*L*L+sum[2]*L+sum[3]];
   local22g4+=creal(f22[ix]*G4)*g[ix]*g[ix]*g[iy];local22g3+=creal(f22[ix]*G3a*G3b)*g[ix]*g[ix]*g[iy]*g[(kml[0]*L+kml[1])*L*L+kml[2]*L+kml[3]];
  }
  sf44+=local44;sf33+=local33;sf22g4+=local22g4;sf22g3+=local22g3;
  #pragma omp atomic
  done++;
  if((done%64)==0){
   #pragma omp critical
   {printf("outer %d/%d\n",done,outer_limit);fflush(stdout);}
  }
 }
 double norm=(double)N*N,t40=creal(f40),t42=s42/(2.0*N),t44=sf44/(8*norm),t33=-sf33/(6*norm),t24=-sf22g4/(4*norm),t233=sf22g3/(4*norm);
 printf("terms %.17g %.17g %.17g %.17g %.17g %.17g\n",t40,t42,t44,t33,t24,t233);if(outer_limit==N)printf("T4 %.17g\n",t40+t42+t44+t33+t24+t233);return 0;
}
