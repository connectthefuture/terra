"""
A module for visualizing Kepler data.

The idea is to keep it rough.
"""
import atpy
from numpy import *
import glob
import matplotlib.pylab as plt
from matplotlib.pylab import *

from matplotlib import rcParams
from matplotlib.gridspec import GridSpec,GridSpecFromSubplotSpec
from keptoy import *
import keptoy
import qalg

def cdpp():
    t = atpy.Table('sqlite','all.db',table='ch1cdpp')

    cdppmin = min(t.cdpp12hr)
    cdppmax = max(t.cdpp12hr)

    nplots = 8
    cdpp = logspace(log10(20),log10(200),nplots)

    for i in range(nplots):
        print cdpp[i]
        closest  = argsort( abs( t.cdpp12hr - cdpp[i] ))[0]
        starcdpp = t.cdpp12hr[closest]
        keplerid = t.KEPLERID[closest]
        file = glob.glob('archive/data3/privkep/EX/Q3/kplr%09i-*_llc.fits' %
                         keplerid)

        star = atpy.Table(file[0],type='fits') 
        ax = plt.subplot(nplots,1,i+1)

        med = median(star.SAP_FLUX )

        ax.plot(star.TIME,(star.SAP_FLUX/med-1)*1e6,'.',ms=2,
                label='KIC-%i, CDPP-12hr %.2f' % (keplerid,starcdpp) )
        ax.legend()




def markT(ax,tT,**kwargs):
    for t in tT:
        ax.axvline(t,**kwargs)
    return ax

    
def inspectT(t0,f0,P,ph,darr=None):
    """
    Take a quick look at a transit
    """
    size = 150
    pad = 0.1 # amount to pad in units of size
    cW = 2 
    linscale = 3
    
    fig = plt.gcf()

    f = f0.copy()
    t = t0.copy()

    f -= f.mean()
    t -= t[0]
    tbase = t.ptp()

    nt = int(ntrans( tbase, P, ph ))
    otT =  P * (arange(nt) + ph ) 
    print otT,t0[0]

    # Plot the time series
    nstack = int(ceil( t.ptp() / size))
    gs = GridSpec(2,1)

    gsStack = GridSpec(nstack, 1)
    gsStack.update(hspace=0.001,bottom=.3,left=0.03,right=0.98)
    gsT = GridSpec(1, nt)
    gsT.update(top=0.28,wspace=0.001,left=0.03,right=0.98)

    axStackl = []
    for i in range(nstack):
        axStackl.append( plt.subplot( gsStack[i]) ) 
        ax = axStackl[i]
        offset = size*i
        ax.plot(t,f,marker='.',ms=2,lw=0,alpha=.6)
        ax.set_xlim(offset-pad*size,offset+(1+pad)*size)
        ax.axvline(offset,ls='--',lw=1,label='Padded')
        ax.axvline(offset+size,ls='--',lw=1)
        ax.annotate('Offset = %i' % offset,xy=(.01,.1),
                    xycoords='axes fraction')

        xa = ax.get_xaxis()
        ya = ax.get_yaxis()

        rms = std(f)
        linthreshy = linscale*rms
        ax.set_yscale('symlog',linthreshy=linthreshy)
        ax.axhline(linthreshy,color='k',ls=':')
        ax.axhline(-linthreshy,color='k',ls=':')
        ax = markT(ax,otT,color='red',lw=3,alpha=0.4)

        if darr != None:
            inT = int(ntrans( tbase, darr['P'], darr['phase'] ))
            itT =  darr['P']*arange(inT) + darr['phase'] * darr['P'] - t0[0]
            ax = markT(ax,itT,color='green',lw=3,alpha=0.4)

        if i == 0:
            xa.set_ticks_position('top')
            ax.legend(loc='upper left')
        else:
            xa.set_visible(False)
            ya.set_visible(False)

    tdur = a2tdur(P2a(P))

    axTl = []    
    for i in range(nt):
        axTl.append( plt.subplot( gsT[i] ) )
        axT = axTl[i]
        axT.plot(t,f,'.')        

        tfit,yfit = lightcurve(tbase=tbase,phase=ph,P=P,df=f)
        axT.plot(tfit,yfit-1,color='red')
        axT.set_xlim( otT[i] - cW*tdur , otT[i] + cW*tdur )
        lims = axT.axis()

        tm = ma.masked_outside( t,lims[0],lims[1] )
        fm = ma.masked_array(f,mask=tm.mask)        

        axT.axis( ymax=fm.max() , ymin=fm.min() )        
        xticklabels = axT.get_xticklabels()
        [xtl.set_rotation(30) for xtl in xticklabels]
        ya = axT.get_yaxis()

        if i != 0:
            plt.setp(ya,visible=False)

    limarr = array([ ax.axis() for ax in axTl ])
    yMi = min(limarr[:,2])
    yMa = max(limarr[:,3])


    for ax in axTl:
        ax.axis(ymax=yMa , ymin=yMi) 
        


def stack(axL,xmin,size,pad=0.1):
    """
    Given a list of axis, we'll adjust the x limits so we can fit a very long
    data string on the computer screen.
    """
    nAx = len(axL)
    for i in range(nAx):

        ax = axL[i]
        offset = xmin + i*size

        ax.set_xlim(offset-pad*size,offset+(1+pad)*size)
        ax.axvline(offset,ls='--',lw=1,label='Padded')
        ax.axvline(offset+size,ls='--',lw=1)
        ax.annotate('Offset = %i' % offset,xy=(.01,.1),
                    xycoords='axes fraction')
        
        xa = ax.get_xaxis()
        ya = ax.get_yaxis()

        if i == 0:
            xa.set_ticks_position('top')
        elif i ==nAx-1:
            ax.legend(loc='lower right')
            xa.set_visible(False)
            ya.set_visible(False)
        else:
            xa.set_visible(False)
            ya.set_visible(False)

def stackold(x,y,size,pad=0.1,axl=None,**kw):
    """

    """
    # How many regions
    npanel = int(ceil( x.ptp() / size))
    gs = GridSpec(npanel,1)
    gs.update(hspace=0.001)

    for i in range(npanel):
        if axl != None:
            ax = axl[i]

        offset = size*i
        ax = plt.subplot( gs[i])
        ax.plot(x,y,**kw)
        ax.set_xlim(offset-pad*size,offset+(1+pad)*size)
        ax.axvline(offset,ls='--',lw=1,label='Padded')
        ax.axvline(offset+size,ls='--',lw=1)
        ax.annotate('Offset = %i' % offset,xy=(.01,.1),
                    xycoords='axes fraction')

        xa = ax.get_xaxis()
        ya = ax.get_yaxis()

        if i == 0:
            xa.set_ticks_position('top')
            ax.legend(loc='upper left')
        else:
            xa.set_visible(False)
            ya.set_visible(False)


        if axl != None:
            axl[i] = ax

    if axl != None:
        return axl

from keptoy import lc
import tfind

def DM(dM,P):
    plt.clf()
    Pcad = int(round(P/lc))
    dMW = tfind.XWrap(dM,Pcad,fill_value=nan)
    nT = dMW.shape[0]
    ncad = dMW.shape[1]
    t = arange(ncad)*lc


    [plt.plot(t,dMW[i,:]+i*2e-4,aa=False) for i in range(nT)]    
    dMW = ma.masked_invalid(dMW)
    plt.plot(t,dMW.mean(axis=0)*sqrt(nT) - 5e-4,lw=3)

def XWrap(XW,step=1):
    """
    Plot XWrap arrays, folded on the right period.
    """

    nT = XW.shape[0]
    ncad = XW.shape[1]
    [plt.plot(XW[i,:]+i*step,aa=False) for i in range(nT)]    

def FOM(dM,P):
    """
    Plot the figure of merit

    """
    step = np.nanmax(dM)
    Pcad = int(round(P/lc))
    dMW = tfind.XWrap(dM,Pcad,fill_value=nan)
    XWrap(dMW, step = step  )
    res = tfind.ep(dM,Pcad)
    fom = res['fom']
    plot(fom -step )
    return dMW


def window(tRES,tLC):
    PcadG = (tRES.PG[0]/keptoy.lc).astype(int)
    filled = tfind.isfilled(tLC.t,tLC.f,20)
    win = tval.window(filled,PcadG)
    plot(PcadG*keptoy.lc,win)
    xlabel('Period (days)')
    ylabel('Window')

import tval
import copy

def LDT(t,f,p):
    """
    Visualize how the local detrender works
    """

    ax = gca()

    d  = tval.LDT(t,f,p,wd=2)
    p1L = d['p1L']
    sL = ma.notmasked_contiguous( d['tdt'] )

    twd = 2./lc

    for i in range(len(p1L)):
        s = sL[i]
        x = xarr(t,s, p['P'] ,twd=150)
        const = mean(f[s])
        color = rcParams['axes.color_cycle'][mod(i,4)]
        ax.plot(x,f[s]-const,'.',color=color)
        ax.plot(x,d['trend'][s] -const,'r',lw=2)
        ax.plot(x,d['ffit'][s] -const,'c',lw=2)

    ymin,ymax = plt.ylim()
    disp = 2*ymin
    fdt = d['fdt']
    res = tval.fitcand(t,f,p)
    pl = [res['P'],res['epoch'],res['df'],res['tdur'] ] # This is the global fit.
    for i in range(len(p1L)):
        s = sL[i]
        x = xarr(t , s , res['P'] ,twd=150)
        color = rcParams['axes.color_cycle'][mod(i,4)]
        ax.plot(x,d['fdt'][s] +disp,'.',lw=2,color=color)
        y = keptoy.P05( pl, d['tdt'][s] ) + disp
        ax.plot(x,y,'c',lw=2)


def xarr(t,s,P,twd=20):
    iT =  round(mean(t[s]) - mean( t[0]) ) /P
    return t[s]-mean(t[s])+twd*iT*lc

def xarrL(t,sL,P,twd=20):
    out = []
    for i in range(len(sL)):
        s = sL[i]
        out.append( xarr(t,s,P,twd=twd) )
    return xarrL



def LDTW(t,f,pL):
    i = 0 
    for p in pL:
        fig = plt.gcf() 
        fig.clf()
        try:
            LDT(t,f,p) 
        except:
            pass
        fig.savefig("LDTW%03i.png" % i)
        i +=1 

def tfit(tsim,tfit):
    plot(tset.RES.PG[0],tset.RES.ddd[1]/tset.RES.sss[1],'o')
    
def eta(tres,KIC):
    """
    Plot detection efficency as a function of depth for a given star.
    """
    PL = unique(tres.Pblock)
    for P in PL:
        dfL = unique(tres.df)
        fgL = []
        efgL = []
        for df in dfL:
            cut = (tres.KIC == KIC ) & (tres.Pblock == P) & (tres.df == df)
            tc = tres.where( cut    ) 
            tg = tres.where( cut & tres.bg   ) 
            tb = tres.where( cut & ~tres.bg  )            
            nc,ng,nb = tc.data.size,tg.data.size,tb.data.size

            print "%s %03d %7.5f %02d %02d %02d" % (KIC,P,df,ng,nb,nc)
            fgL.append(1.*ng/nc )
            efgL.append(1./sqrt(nc)  )
        errorbar(dfL,fgL,efgL,label='P-%03d' % P)

    xlabel(r'$\Delta F / F$')
    ylabel('Detection Efficiency')
    title('%d' % KIC)
    legend(loc='best')
    draw()

def markT(f,p,wd=2):
    P = p['P']
    epoch = p['epoch']
    tdur = p['tdur']

    twd      = round(tdur/lc)
    Pcad     = int(round(P/lc))
    epochcad = int(round(epoch/lc))
    wdcad    = int(round(wd/lc))

    f0W = tfind.XWrap(f,Pcad,fill_value=np.nan)

    ### Determine the indecies of the points to fit. ###
    ms   = np.arange( f0W.shape[0] ) * Pcad + epochcad

    # Exclude regions where the convolution returned a nan.
    sLDT = [slice(m - wdcad/2 , m+wdcad/2) for m in ms]

    return sLDT

def ROC(tres):
    """
    
    """
    assert len(unique(tres.Pblock))==1,'Periods must be the same'
    assert len(unique(tres.KIC))==1,'Must compare the same star'

    KIC = unique(tres.KIC)[0]
    dfL = unique(tres.df)
    
    for df in dfL:
        t = tres.where( tres.df == df)
        fapL,etaL = qalg.ROC(t)
        plot(fapL,etaL,lw=2,label='df  = %03d ' % (df*1e6) )
    
    x = linspace(0,1,100)
    plot(x,x)

    legend(loc='best')
    title( 'ROC for %i' % KIC ) 
    xlabel('FAP' )
    ylabel('Detection Efficiency' )

def hist(tres):
    """
    
    """
    assert len(unique(tres.Pblock))==1,'Periods must be the same'
    assert len(unique(tres.KIC))==1,'Must compare the same star'

    KIC = unique(tres.KIC)[0]
    dfL = unique(tres.df)

    fig,axL = subplots(nrows=len(dfL),sharex=True,figsize=( 11,  12))
    for df,ax in zip(dfL,axL):
        tg = tres.where( (tres.df == df) & tres.bg)
        tb = tres.where( (tres.df == df) & ~tres.bg)
        ax.hist(tg.os2n,color='green',bins=arange(100),
                label='Good %d' % len(tg.data))
        ax.hist(tb.os2n,color='red',bins=arange(100),
                label='Fail %d' % len(tb.data))
        ax.legend()

        label = r"""
$\Delta F / F$  = %(df)i ppm
""" % {'df':df * 1e6}

        ax.annotate(label,xy=(.8,.1),xycoords='axes fraction',
                    bbox=dict(boxstyle="round", fc="w", ec="k"))


    xlabel('s2n')
    title('%d, %i days' % (KIC,tres.Pblock[0])  )


def simplots(tres):
    PL = unique(tres.Pblock)
    fcount = 0 
    for P in PL:
        t = tres.where(tres.Pblock == P)
        hist(t)
        fig = gcf()
        fig.savefig('%02d.png' % fcount )
        fcount +=1
        fig.clf()

    for P in PL:
        t = tres.where(tres.Pblock == P)
        ROC(t)
        fig = gcf()
        fig.savefig('%02d.png' % fcount )
        fcount +=1
        fig.clf()
    
def inspFail(tPAR,tLC,tRES):
    """

    """

    assert tPAR.data.size == 1, "Must be length 1 tables"

    # Generate the lightcurve.
    f = keptoy.genEmpLC( qalg.tab2dl(tPAR)[0] ,tLC.t,tLC.f   )
    t = tLC.t

    # Find the parameters:
    pkwn   = dict(P = tPAR.P, epoch=tPAR.epoch, tdur=0.3 )
    
    iclose = argmin( abs(tRES.PG - tPAR.P) )
    pclose = dict(
        P     = tRES.PG[0][iclose], 
        epoch = tRES.epoch[0][iclose],
        tdur  = 0.3 
        )

    phigh = dict(
        P     = tPAR.oP, 
        epoch = tPAR.oepoch,
        tdur  = 0.3 ,
        df    = tPAR.df,
        )

    
    fig,axL = subplots(nrows=5,figsize=( 11, 12))

    iax = 0
    axL[iax].axvline( pkwn['P'],label='Input Period' )
    axL[iax].plot( tRES.PG[0],tRES.s2n[0] )
    axL[iax].legend()
    iax += 1

    sca(axL[iax])
#    axes(sharex=axL[0])
    axL[iax].scatter(tRES[0]['PG'],tRES[0]['epoch'],c=tRES[0]['s2n'],
                     cmap=cm.gray_r,edgecolors='none',vmin=7)
    iax += 1

    axL[iax].set_title('Known site of transit')
    sca(axL[iax])
    try:
        LDT(t,f,pkwn)
    except ValueError:
        pass

    iax += 1

    axL[iax].set_title('Closest Peak')
    sca(axL[iax])
    try:
        LDT(t,f,pclose)
    except ValueError:
        pass

    iax += 1

    axL[iax].set_title('Highest Peak')
    sca(axL[iax])

    LDT(t,f,phigh)
    X2,X2A,pA,fTransitA , mTransit, mTransitA = tval.alias(t,f,phigh)

    label = r"""
$\chi^2 $ Input  = %(X2)e
$\chi^2 $ Alias  = %(X2A)e 
""" % { 'X2':X2 , 'X2A':X2A }
    ax = gca()
    ax.annotate(label,xy=(.8,.1),xycoords='axes fraction',
                bbox=dict(boxstyle="round", fc="w", ec="k"))



    iax += 1

    return #X2,X2A,fTransitA , mTransit, mTransitA



def inspSim():

    tLC = atpy.Table('tLC.fits')
    tRED = atpy.Table('tRED.fits')
    P   = np.unique(tRED.Pblock)
    dfL = np.unique(tRED.df)
    tfail = tRED.where((tRED.df == dfL[1]) & (tRED.Pblock == P[2]) &  ~tRED.bg)
    LDTfail = []
    seeds = []
    nl    = []
    Aseeds = tfail.seed
    for seed in Aseeds:
        try:
            tPAR = tRED.where(tRED.seed == seed)
            tRES = atpy.Table('tRES%04d.fits' % seed)

            ikwn = argmin(abs( tRES.PG - tPAR.P  ))
            nT = tRES.nT[0][ikwn]

            nl.append(nT)        
            sketch.inspFail(tPAR,tLC,tRES)
            fig = gcf()
            fig.savefig('insp%04d.png' % tPAR.seed)
            close('all')
        except ValueError:
            LDTfail.append( tPAR.seed[0] )


def inspVAL(tLC,tRES,*pL):
    f = tLC.f # - tLC.fcbv
    t = tLC.t

    nrows = 4 + 2*len(pL)

    colors = ['r']

    fig = gcf()
    fig.clf()
    ax0 = fig.add_subplot(nrows,1,1)
    ax1 = fig.add_subplot(nrows,1,2,sharex = ax0)
    axL = [ax0,ax1]
    axL[0].plot(t,f)
    dM,bM,aM,DfDt,f0 = tfind.MF(f,20)
    axL[1].plot(t,dM)

    for i in range(3,nrows+1):
        axL.append( fig.add_subplot(nrows,1,i) )

    sca(axL[2])
    periodogram(tRES)

    sca(axL[4])
    pep(tRES)


    for i in range(len(pL)):
        p = pL[i]
        c = colors[i]

#        ms = tval.midTransId( t ,  p)
#        sL = [tval.getSlice(m,100) for m in ms]
#        [axL[0].plot(t[s],f[s],c) for s in sL]
#        [axL[1].plot(t[s],dM[s],c) for s in sL]

        ifom = 3+2*i
        ildt = 4+2*i

        sca( axL[ifom] )
        FOM(dM,p['P'])

        try:
            axvline(p['epoch']/lc)
            sca( axL[ildt] )
            LDT(t,f,p)
        except:
            pass

#    for ax in axL:
#        xa = ax.get_xaxis()
#        ya = ax.get_yaxis()
#        xa.set_visible(False)
##        ya.set_visible(False)

    plt.subplots_adjust(hspace=0.16)
    
    draw()


def pep(tRES):
    """
    Show best epoch as a function of period
    """
    ax = gca()

    x = tRES.PG[0]
    y = tRES.epoch[0]
    c = tRES.s2n[0]
    ax.scatter(x,y,c=c,cmap=cm.gray_r,edgecolors='none',vmin=7)

def periodogram(tRES):
    ax = gca()
    x = tRES.PG[0]
    y = tRES.epoch[0]
    ax.plot(x,y)


def DM():
    return





def dMLDT(t,f,p,axL):
    """
    Plot folded mean depth and local detrending
    """
    assert axL.size==2 

    sca(axL[0])
    FOM(dM,pknown['P'])
    axvline(pknown['epoch']/lc)
    sca(axL[1])
    LDT(tLC.t,f,p)
        

    
