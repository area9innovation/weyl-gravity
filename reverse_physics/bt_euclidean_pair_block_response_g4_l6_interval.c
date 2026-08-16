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
typedef struct { long double complex mid; long double rad; } Ball;
typedef struct { int deg; Ball a[MAXU+1][MAXU+1]; } Poly;
typedef struct { Poly v, d[2]; } Dual;
typedef struct { int n[4]; int amp; } Wave;

static Ball CB[2][2];
static Coord dirs[8], affected[16];
static int naffected;
static Ball gmom[MAXU+2][MAXU+2];

static const long double ERR = 1.0e-17L;
static Ball bz(void){Ball z={0,0};return z;}
static Ball bi(long n){Ball z={(long double)n,0};return z;}
static long double upper_abs(Ball z){return fabsl(creall(z.mid))+fabsl(cimagl(z.mid))+z.rad;}
static Ball bf(long n,long d){Ball z;z.mid=(long double)n/(long double)d;z.rad=2*ERR*fabsl(creall(z.mid));return z;}
static Ball ba(Ball x,Ball y){Ball z;z.mid=x.mid+y.mid;z.rad=(x.rad+y.rad+ERR*(upper_abs(x)+upper_abs(y)))*(1+4*ERR);return z;}
static Ball bn(Ball x){x.mid=-x.mid;return x;}
static Ball bs(Ball x,Ball y){return ba(x,bn(y));}
static Ball bm(Ball x,Ball y){Ball z;z.mid=x.mid*y.mid;z.rad=(upper_abs(x)*y.rad+upper_abs(y)*x.rad+x.rad*y.rad+8*ERR*upper_abs(x)*upper_abs(y))*(1+8*ERR);return z;}
static Ball bscalei(Ball x,long n){return bm(x,bi(n));}
static int bexactzero(Ball x){return x.mid==0&&x.rad==0;}

static Coord addc(Coord a, Coord b){Coord c;for(int j=0;j<4;j++)c.x[j]=a.x[j]+b.x[j];return c;}
static int eqc(Coord a, Coord b){for(int j=0;j<4;j++)if(a.x[j]!=b.x[j])return 0;return 1;}
static int inside(Coord c){Coord o={{0,0,0,0}},e={{1,0,0,0}};if(eqc(c,o))return 0;if(eqc(c,e))return 1;return -1;}
static void init(void){
 CB[0][0]=CB[1][1]=bf(9,616);CB[0][1]=CB[1][0]=bf(1,308);
 int z=0;for(int ax=0;ax<4;ax++)for(int s=-1;s<=1;s+=2){Coord d={{0,0,0,0}};d.x[ax]=s;dirs[z++]=d;}
 Coord base[2]={{{0,0,0,0}},{{1,0,0,0}}};naffected=0;
 for(int b=0;b<2;b++)for(int q=-1;q<8;q++){
  Coord c=q<0?base[b]:addc(base[b],dirs[q]);int seen=0;
  for(int i=0;i<naffected;i++)if(eqc(c,affected[i]))seen=1;
  if(!seen)affected[naffected++]=c;
 }
 memset(gmom,0,sizeof(gmom));gmom[0][0]=bi(1);
 for(int total=2;total<=MAXU+1;total+=2)for(int a=0;a<=total;a++){
  int b=total-a;if(a){
   Ball v=bz();if(a>=2)v=ba(v,bscalei(bm(CB[0][0],gmom[a-2][b]),a-1));if(b)v=ba(v,bscalei(bm(CB[0][1],gmom[a-1][b-1]),b));gmom[a][b]=v;
  }else gmom[a][b]=bscalei(bm(CB[1][1],gmom[0][b-2]),b-1);
 }
}
static void pzero(Poly*p){memset(p,0,sizeof(*p));p->deg=0;}
static void pconst(Poly*p,Ball z){pzero(p);p->a[0][0]=z;}
static void paddto(Poly*out,const Poly*p){if(p->deg>out->deg)out->deg=p->deg;for(int a=0;a<=p->deg;a++)for(int b=0;b<=p->deg-a;b++)out->a[a][b]=ba(out->a[a][b],p->a[a][b]);}
static void pscale(Poly*out,const Poly*p,Ball z){pzero(out);out->deg=p->deg;for(int a=0;a<=p->deg;a++)for(int b=0;b<=p->deg-a;b++)out->a[a][b]=bm(p->a[a][b],z);}
static void pmul(Poly*out,const Poly*p,const Poly*q){
 pzero(out);out->deg=p->deg+q->deg<MAXU?p->deg+q->deg:MAXU;for(int a=0;a<=p->deg;a++)for(int b=0;b<=p->deg-a;b++)if(!bexactzero(p->a[a][b]))
 for(int c=0;c<=q->deg&&a+b+c<=MAXU;c++)for(int d=0;d<=q->deg-c&&a+b+c+d<=MAXU;d++)if(!bexactzero(q->a[c][d]))out->a[a+c][b+d]=ba(out->a[a+c][b+d],bm(p->a[a][b],q->a[c][d]));
}
static void dzero(Dual*x){pzero(&x->v);pzero(&x->d[0]);pzero(&x->d[1]);}
static void daddto(Dual*out,const Dual*x){paddto(&out->v,&x->v);paddto(&out->d[0],&x->d[0]);paddto(&out->d[1],&x->d[1]);}
static void dscale(Dual*out,const Dual*x,Ball z){pscale(&out->v,&x->v,z);pscale(&out->d[0],&x->d[0],z);pscale(&out->d[1],&x->d[1],z);}
static void dmul(Dual*out,const Dual*x,const Dual*y){
 Poly t1,t2;pmul(&out->v,&x->v,&y->v);
 for(int ax=0;ax<2;ax++){pmul(&t1,&x->d[ax],&y->v);pmul(&t2,&x->v,&y->d[ax]);paddto(&t1,&t2);out->d[ax]=t1;}
}
static long binom3(int n,int a,int b){
 static const long fact[14]={1,1,2,6,24,120,720,5040,40320,362880,3628800,39916800,479001600,6227020800};
 return fact[n]/(fact[a]*fact[b]*fact[n-a-b]);
}
static Ball bpow(Ball z,int n){Ball out=bi(1);for(int j=0;j<n;j++)out=bm(out,z);return out;}
static long ipowi(long z,int n){long out=1;for(int j=0;j<n;j++)out*=z;return out;}
static void edgepower(Dual*out,Ball c,int u0,int u1,int n,int dq0,int dq1){
 dzero(out);out->v.deg=n;out->d[0].deg=out->d[1].deg=n-1;for(int a=0;a<=n;a++)for(int b=0;b<=n-a;b++){
  int r=n-a-b;Ball z=bscalei(bpow(c,r),binom3(n,a,b)*ipowi(u0,a)*ipowi(u1,b));out->v.a[a][b]=ba(out->v.a[a][b],z);
 }
 if(n>0)for(int a=0;a<n;a++)for(int b=0;b<n-a;b++){
  int r=n-1-a-b;Ball z=bscalei(bpow(c,r),n*binom3(n-1,a,b)*ipowi(u0,a)*ipowi(u1,b));out->d[0].a[a][b]=ba(out->d[0].a[a][b],bscalei(z,dq0));out->d[1].a[a][b]=ba(out->d[1].a[a][b],bscalei(z,dq1));
 }
}
static int omega(const int k[4]){static const int x[6]={0,1,3,4,3,1};int w=0;for(int j=0;j<4;j++)w+=x[k[j]];return w;}
static Ball phase(const int k[4],Coord c){int dot=0;for(int j=0;j<4;j++)dot+=k[j]*c.x[j];dot=(dot%6+6)%6;static const long double re[6]={1,.5L,-.5L,-1,-.5L,.5L};static const int si[6]={0,1,1,0,-1,-1};Ball z;z.mid=re[dot]+I*si[dot]*0.86602540378443864675L;z.rad=si[dot]?2.0e-19L:0;return z;}
static Ball raw(const Wave*w,int nw,Coord c){Ball z=bz();for(int q=0;q<nw;q++)z=ba(z,bscalei(phase(w[q].n,c),w[q].amp));return z;}
static void field(Poly*out,const Wave*w,int nw,Coord c,const Ball center[2]){
 pconst(out,inside(c)>=0?center[inside(c)]:raw(w,nw,c));int a=inside(c);if(a==0){out->a[1][0]=ba(out->a[1][0],bi(1));out->deg=1;}else if(a==1){out->a[0][1]=ba(out->a[0][1],bi(1));out->deg=1;}
}
static Ball integrate(const Poly*p,int observed){Ball z=bz();for(int a=0;a<=p->deg;a++)for(int b=0;b<=p->deg-a;b++)z=ba(z,bm(p->a[a][b],gmom[a+observed][b]));return z;}

static void response(const Wave*w,int nw,int maxorder,Ball out[2][5]){
 Coord base[2]={{{0,0,0,0}},{{1,0,0,0}}};Ball kval[2]={bz(),bz()},center[2];
 for(int b=0;b<2;b++)for(int q=0;q<nw;q++){int om=omega(w[q].n);kval[b]=ba(kval[b],bscalei(phase(w[q].n,base[b]),w[q].amp*om*om));}
 for(int a=0;a<2;a++){center[a]=raw(w,nw,base[a]);for(int b=0;b<2;b++)center[a]=bs(center[a],bm(CB[a][b],kval[b]));}
 Dual U[4];for(int j=0;j<4;j++)dzero(&U[j]);
 for(int iv=0;iv<naffected;iv++){
  Dual jet[6];for(int p=1;p<=5;p++)dzero(&jet[p]);
  for(int id=0;id<8;id++){
   Coord v=affected[iv],nb=addc(v,dirs[id]);Poly fv,fn;field(&fv,w,nw,v,center);field(&fn,w,nw,nb,center);
   Ball c=bs(fn.a[0][0],fv.a[0][0]);int u0=(int)llroundl(creall(bs(fn.a[1][0],fv.a[1][0]).mid));int u1=(int)llroundl(creall(bs(fn.a[0][1],fv.a[0][1]).mid));
   int dq0=nb.x[0]*nb.x[0]-v.x[0]*v.x[0],dq1=nb.x[1]*nb.x[1]-v.x[1]*v.x[1];
   for(int p=1;p<=5;p++){Dual pow;edgepower(&pow,c,u0,u1,p,dq0,dq1);daddto(&jet[p],&pow);}
  }
  Dual t1,row;
  dmul(&t1,&jet[1],&jet[2]);dscale(&row,&t1,bf(1,2));daddto(&U[0],&row);
  dmul(&t1,&jet[2],&jet[2]);dscale(&row,&t1,bf(1,8));daddto(&U[1],&row);dmul(&t1,&jet[1],&jet[3]);dscale(&row,&t1,bf(1,6));daddto(&U[1],&row);
  dmul(&t1,&jet[2],&jet[3]);dscale(&row,&t1,bf(1,12));daddto(&U[2],&row);dmul(&t1,&jet[1],&jet[4]);dscale(&row,&t1,bf(1,24));daddto(&U[2],&row);
  dmul(&t1,&jet[3],&jet[3]);dscale(&row,&t1,bf(1,72));daddto(&U[3],&row);dmul(&t1,&jet[2],&jet[4]);dscale(&row,&t1,bf(1,48));daddto(&U[3],&row);dmul(&t1,&jet[1],&jet[5]);dscale(&row,&t1,bf(1,120));daddto(&U[3],&row);
 }
 for(int j=0;j<maxorder;j++){U[j].v.a[0][0]=bz();U[j].d[0].a[0][0]=bz();U[j].d[1].a[0][0]=bz();}
 Dual ex[5];dzero(&ex[0]);ex[0].v.a[0][0]=bi(1);
 for(int n=1;n<=maxorder;n++){Dual sum,prod,tmp;dzero(&sum);for(int j=1;j<=n;j++){dmul(&prod,&U[j-1],&ex[n-j]);dscale(&tmp,&prod,bi(j));daddto(&sum,&tmp);}dscale(&ex[n],&sum,bf(-1,n));}
 Ball z[5],dz[2][5],num[5],dnum[2][5],m[5],dm[2][5];memset(z,0,sizeof(z));memset(dz,0,sizeof(dz));memset(num,0,sizeof(num));memset(dnum,0,sizeof(dnum));memset(m,0,sizeof(m));memset(dm,0,sizeof(dm));
 for(int n=0;n<=maxorder;n++){z[n]=integrate(&ex[n].v,0);num[n]=integrate(&ex[n].v,1);for(int ax=0;ax<2;ax++){dz[ax][n]=integrate(&ex[n].d[ax],0);dnum[ax][n]=integrate(&ex[n].d[ax],1);}}
 for(int n=0;n<=maxorder;n++){
  m[n]=num[n];for(int j=1;j<=n;j++)m[n]=bs(m[n],bm(z[j],m[n-j]));
  for(int ax=0;ax<2;ax++){dm[ax][n]=dnum[ax][n];for(int j=1;j<=n;j++)dm[ax][n]=bs(dm[ax][n],ba(bm(dz[ax][j],m[n-j]),bm(z[j],dm[ax][n-j])));out[ax][n]=dm[ax][n];}
 }
}
static Ball orient(const Ball r[2][5],int n){return ba(bm(r[0][n],bf(1,8)),bm(r[1][n],bf(3,8)));}
static void negk(int out[4],const int k[4]){for(int j=0;j<4;j++)out[j]=(L-k[j])%L;}
static Ball topvertex(int order,const int mom[MAXW][4]){
 Ball total=bz(),r[2][5];for(int mask=0;mask<(1<<order);mask++){
  Wave w[MAXW];int nw=0,bits=0;for(int q=0;q<order;q++)if(mask&(1<<q)){memcpy(w[nw].n,mom[q],sizeof(w[nw].n));w[nw].amp=1;nw++;bits++;}
  response(w,nw,order,r);int s=((order-bits)&1)?-1:1;total=ba(total,bscalei(orient(r,order),s));
 }return total;
}
static void indexk(int index,int k[4]){for(int j=3;j>=0;j--){k[j]=index%L;index/=L;}}
static void addk(int out[4],const int a[4],const int b[4]){for(int j=0;j<4;j++)out[j]=(a[j]+b[j])%L;}
static void subk(int out[4],const int a[4],const int b[4]){for(int j=0;j<4;j++)out[j]=(a[j]-b[j]+L)%L;}
static Ball Bvertex(int n,const int mom[MAXW][4]){
 Ball z=bz();for(int e=0;e<8;e++){Ball p=bi(1);for(int q=0;q<n;q++)p=bm(p,bs(phase(mom[q],dirs[e]),bi(1)));z=ba(z,p);}return z;
}
static Ball gamma_vertex(int n,const int mom[MAXW][4]){
 Ball z=bz();for(int mask=1;mask<(1<<n)-1;mask++){
  int left[MAXW][4],right[MAXW][4],nl=0,nr=0;for(int q=0;q<n;q++)if(mask&(1<<q))memcpy(left[nl++],mom[q],sizeof(left[0]));else memcpy(right[nr++],mom[q],sizeof(right[0]));
  z=ba(z,bm(Bvertex(nl,left),Bvertex(nr,right)));
 }return bm(z,bf(1,2));
}
static Ball mixed_f4_at_scale(const int k[4],const int mk[4],int scale){
 Ball total=bz(),r[2][5];for(int sa=-1;sa<=1;sa+=2)for(int sb=-1;sb<=1;sb+=2){Wave w[2];memcpy(w[0].n,k,sizeof(w[0].n));memcpy(w[1].n,mk,sizeof(w[1].n));w[0].amp=sa*scale;w[1].amp=sb*scale;response(w,2,4,r);total=ba(total,bscalei(orient(r,4),sa*sb));}return bm(total,bf(1,4));
}
static Ball f42_vertex(const int k[4],const int mk[4]){Ball d1=mixed_f4_at_scale(k,mk,1),d2=mixed_f4_at_scale(k,mk,2);return bm(bs(bscalei(d1,16),d2),bf(1,12));}

static void printball(const char*name,Ball x){printf("%s %.21Lg +/- %.3Le imag %.3Le +/- %.3Le\n",name,creall(x.mid),x.rad,cimagl(x.mid),x.rad);}

int main(int argc,char**argv){
 init();int outer_limit=argc>1?atoi(argv[1]):N;if(outer_limit<1||outer_limit>N)outer_limit=N;printf("affected=%d outer_limit=%d\n",naffected,outer_limit);
 Ball r0[2][5];response(NULL,0,4,r0);Ball f20=orient(r0,2),f40=orient(r0,4);printball("F20",f20);printball("F40",f40);
 static int modes[N][4];static Ball g[N],f22[N],f42[N];
 #pragma omp parallel for schedule(dynamic)
 for(int ix=0;ix<N;ix++){int mk[4],mom[4][4]={{0}};indexk(ix,modes[ix]);negk(mk,modes[ix]);memcpy(mom[0],modes[ix],sizeof(mom[0]));memcpy(mom[1],mk,sizeof(mom[1]));int w=omega(modes[ix]);g[ix]=w?bf(1,w*w):bz();f22[ix]=topvertex(2,mom);f42[ix]=f42_vertex(modes[ix],mk);}
 Ball s2=bz(),s42=bz();for(int ix=0;ix<N;ix++){s2=ba(s2,bm(f22[ix],g[ix]));s42=ba(s42,bm(f42[ix],g[ix]));}
 Ball b2=ba(f20,bm(s2,bf(1,2*N))),t42base=bm(s42,bf(1,2*N));printball("b2",b2);printball("f42_one_loop",t42base);fflush(stdout);
 static Ball row44[N],row33[N],row22g4[N],row22g3[N];int done=0;
 #pragma omp parallel for schedule(dynamic)
 for(int ix=0;ix<outer_limit;ix++){
  int k[4],mk[4];memcpy(k,modes[ix],sizeof(k));negk(mk,k);Ball local44=bz(),local33=bz(),local22g4=bz(),local22g3=bz();
  for(int iy=0;iy<N;iy++){
   int l[4],ml[4],sum[4],msum[4],kml[4],lmk[4];memcpy(l,modes[iy],sizeof(l));negk(ml,l);addk(sum,k,l);negk(msum,sum);subk(kml,k,l);subk(lmk,l,k);
   int mom4[4][4];memcpy(mom4[0],k,sizeof(k));memcpy(mom4[1],mk,sizeof(k));memcpy(mom4[2],l,sizeof(k));memcpy(mom4[3],ml,sizeof(k));
   int mom3[4][4];memcpy(mom3[0],k,sizeof(k));memcpy(mom3[1],l,sizeof(k));memcpy(mom3[2],msum,sizeof(k));
   Ball F44=topvertex(4,mom4),F33=topvertex(3,mom3);
   int opp3[4][4];memcpy(opp3[0],mk,sizeof(k));memcpy(opp3[1],ml,sizeof(k));memcpy(opp3[2],sum,sizeof(k));
   Ball G3=gamma_vertex(3,opp3),G4=gamma_vertex(4,mom4);
   int ga[4][4],gb[4][4];memcpy(ga[0],mk,sizeof(k));memcpy(ga[1],l,sizeof(k));memcpy(ga[2],kml,sizeof(k));memcpy(gb[0],k,sizeof(k));memcpy(gb[1],ml,sizeof(k));memcpy(gb[2],lmk,sizeof(k));
   Ball G3a=gamma_vertex(3,ga),G3b=gamma_vertex(3,gb);
   local44=ba(local44,bm(bm(F44,g[ix]),g[iy]));local33=ba(local33,bm(bm(bm(bm(F33,G3),g[ix]),g[iy]),g[(sum[0]*L+sum[1])*L*L+sum[2]*L+sum[3]]));
   local22g4=ba(local22g4,bm(bm(bm(bm(f22[ix],G4),g[ix]),g[ix]),g[iy]));local22g3=ba(local22g3,bm(bm(bm(bm(bm(bm(f22[ix],G3a),G3b),g[ix]),g[ix]),g[iy]),g[(kml[0]*L+kml[1])*L*L+kml[2]*L+kml[3]]));
  }
  row44[ix]=local44;row33[ix]=local33;row22g4[ix]=local22g4;row22g3[ix]=local22g3;
  #pragma omp atomic
  done++;
  if((done%64)==0){
   #pragma omp critical
   {printf("outer %d/%d\n",done,outer_limit);fflush(stdout);}
  }
 }
 Ball sf44=bz(),sf33=bz(),sf22g4=bz(),sf22g3=bz();for(int ix=0;ix<outer_limit;ix++){sf44=ba(sf44,row44[ix]);sf33=ba(sf33,row33[ix]);sf22g4=ba(sf22g4,row22g4[ix]);sf22g3=ba(sf22g3,row22g3[ix]);}
 long norm=(long)N*N;Ball t40=f40,t42=t42base,t44=bm(sf44,bf(1,8*norm)),t33=bm(sf33,bf(-1,6*norm)),t24=bm(sf22g4,bf(-1,4*norm)),t233=bm(sf22g3,bf(1,4*norm));
 printball("t40",t40);printball("t42",t42);printball("t44",t44);printball("t33",t33);printball("t24",t24);printball("t233",t233);if(outer_limit==N){Ball total=ba(ba(ba(t40,t42),ba(t44,t33)),ba(t24,t233));printball("T4",total);}return 0;
}
