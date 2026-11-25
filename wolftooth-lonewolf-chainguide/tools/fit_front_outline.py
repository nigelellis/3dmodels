import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); os.chdir(ROOT)           # run from anywhere; paths are project-relative
os.makedirs("build", exist_ok=True); os.makedirs("renders", exist_ok=True)
import numpy as np, json
from PIL import Image, ImageOps
from scipy import ndimage
from scipy.spatial import ConvexHull
from scipy.optimize import least_squares
im=ImageOps.exif_transpose(Image.open("reference/photos/05_front_straight_on.jpg"))
rgb=np.asarray(im).astype(float); g=rgb.mean(2)
skin=(rgb[:,:,0]-rgb[:,:,2])>35
part=ndimage.binary_opening((g<185)&~skin,iterations=2)
lab,n=ndimage.label(part); part=ndimage.binary_fill_holes(lab==(1+np.argmax(ndimage.sum(part,lab,range(1,n+1)))))
R=[(np.nonzero(part[y])[0].max(),y) for y in range(1225,2170,10)]
Lf=[(np.nonzero(part[y])[0].min(),y) for y in range(1225,2170,10)]
B=[(x,np.nonzero(part[:,x])[0].max()) for x in range(700,1660,20)]
T=[(x,np.nonzero(part[:,x])[0].min()) for x in range(1180,1820,20)]
# inner edge of the light side-face strip (front edge of the sloped right side)
sm=ndimage.uniform_filter(g,9); FR=[]
for y in range(1640,2160,20):
    xr=np.nonzero(part[y])[0].max()
    row=sm[y,xr-260:xr-8]; xs=np.arange(xr-260,xr-8)
    k=np.nonzero(row<95)[0]
    if len(k): FR.append((xs[k.max()],y))
PX=(508/11.6+442/10.21)/2; HC=np.array([1456,1485])
mm=lambda P: np.c_[(np.array(P,float)[:,0]-HC[0])/PX,(HC[1]-np.array(P,float)[:,1])/PX]
R,Lf,B,T,FR=map(mm,(R,Lf,B,T,FR))
pad_auto=np.vstack([T, R[R[:,1]>-2.6], Lf[Lf[:,1]>0.1]])            # top, pad right corner, pad top-left edge
base_auto=np.vstack([R[R[:,1]<=-2.6], Lf[Lf[:,1]<=0.1], B])
pad_manual=mm([(1140,1690),(1270,1780),(1480,1832)])                  # pad lower edge (inside the outline)
pad_pts=np.vstack([pad_auto,pad_manual])

def circ(c,r,a0=0,a1=2*np.pi,n=90):
    t=np.linspace(a0,a1,n); return np.c_[c[0]+r*np.cos(t),c[1]+r*np.sin(t)]
def hull2(P): return P[ConvexHull(P).vertices]
def dense(Q,n=1000):
    Q=np.vstack([Q,Q[:1]]); d=np.r_[0,np.cumsum(np.linalg.norm(np.diff(Q,axis=0),axis=1))]
    t=np.linspace(0,d[-1],n); return np.c_[np.interp(t,d,Q[:,0]),np.interp(t,d,Q[:,1])]
NAMES=["top_r","clx","clz","crx","crz","ftx","ftz","blx","blz","brx","brz","pcr","bcr","arch"]
p0=json.load(open("reference/fit/front_fit.json")); p0["crz"]=-0.5
def outlines(p):
    def corner(pt,r):
        pt=np.array(pt); d=-pt/np.linalg.norm(pt); return circ(pt+d*r*0.8,r,n=40)
    blk=np.vstack([circ((0,0),p["top_r"]),corner((p["clx"],p["clz"]),p["pcr"]),corner((p["crx"],p["crz"]),p["pcr"])])
    block=dense(hull2(blk))
    skirt=dense(hull2(np.vstack([blk,corner((p["ftx"],p["ftz"]),p["bcr"]),corner((p["blx"],p["blz"]),p["bcr"]),
                                 corner((p["brx"],p["brz"]),p["bcr"])])))
    a,b=np.array([p["blx"],p["blz"]]),np.array([p["brx"],p["brz"]]); u=(b-a)/np.linalg.norm(b-a); nn=np.array([-u[1],u[0]])
    t=(skirt-a)@u/np.linalg.norm(b-a); off=(skirt-a)@nn; on=(t>0.08)&(t<0.92)&(np.abs(off)<0.6)
    skirt[on]+=np.outer(p["arch"]*4*t[on]*(1-t[on]),nn)
    return block,skirt
def nearest(A,Bq): return np.sqrt(((A[:,None,:]-Bq[None,:,:])**2).sum(-1)).min(1)
def resid(v):
    p=dict(zip(NAMES,v)); blk,sk=outlines(p)
    return np.r_[nearest(pad_pts,blk),nearest(base_auto,sk),[max(0,.3-p["pcr"])*20,max(0,.3-p["bcr"])*20]]
r=least_squares(resid,np.array([p0[k] for k in NAMES]),diff_step=1e-3,max_nfev=3000,loss="soft_l1",f_scale=0.3)
p=dict(zip(NAMES,r.x)); res=resid(r.x)[:-2]
print(f"rms {np.sqrt(np.mean(res**2)):.2f} mm  95th pct {np.percentile(res,95):.2f} mm  n={len(res)}")
# draft: horizontal gap between back silhouette and front edge at the same height
Rb=R[R[:,1]<=-2.6]; gaps=[np.interp(z,Rb[::-1,1],Rb[::-1,0])-x for x,z in FR]
print("front-edge points",len(FR)," draft gaps mm:",np.round(gaps,2))
p["draft"]=float(np.median(gaps)); p["px_per_mm"]=PX
json.dump({k:float(v) for k,v in p.items()},open("reference/fit/front_fit.json","w"),indent=1)
print({k:round(float(v),2) for k,v in p.items()})
blk,sk=outlines(p); print("width",round(sk[:,0].max()-sk[:,0].min(),2),"height",round(sk[:,1].max()-sk[:,1].min(),2))
