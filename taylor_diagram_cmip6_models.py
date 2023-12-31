#!/usr/bin/env python
# coding: utf-8

# # Script for Taylor Diagram

# In[1]:


# import modules
import numpy as NP
import matplotlib.pyplot as PLT
import pandas as pd


# In[2]:


#Read csv file with model values

Data = pd.read_csv("_path_\\dataframe_models.csv")
Data_df = Data.drop(labels='Year', axis=1) #to calculate stddev
Data_df.std(axis =0, skipna = True)


# In[3]:


# defining refernece data as the 'avg' column from the dataframe
X = Data.avg
X.std()


# In[6]:


########## TAYLOR-DIAGRAM ###############

labels= ['BCC-CSM2-MR','CanESM5','NorESM2-LM','CESM2','MPI-ESM1-2-LR','EC-Earth3-CC','ACCESS-ESM1-5','GISS-E2-1-G-CC'] # name of models

class TaylorDiagram(object):
    """
    Taylor diagram.
    Plot model standard deviation and correlation to reference (data)
    sample in a single-quadrant polar plot, with r=stddev and
    theta=arccos(correlation).
    """

    def __init__(self, refstd,fig=None, rect=111, label='_', srange=(0, 1.8), extend=False):
        """
        Set up Taylor diagram axes, i.e. single quadrant polar
        plot, using `mpl_toolkits.axisartist.floating_axes`.
        Parameters:
        * refstd: reference standard deviation to be compared to
        * fig: input Figure or None
        * rect: subplot definition
        * label: reference label
        * srange: stddev axis extension, in units of *refstd*
        * extend: extend diagram to negative correlations
        """

        from matplotlib.projections import PolarAxes
        import mpl_toolkits.axisartist.floating_axes as FA
        import mpl_toolkits.axisartist.grid_finder as GF

        self.refstd = refstd            # Reference standard deviation

        tr = PolarAxes.PolarTransform()
        
          # Correlation labels
        rlocs = NP.array([0, 0.2, 0.3, 0.4, 0.6, 0.8, 0.9, 0.95, 0.99, 1])
        if extend:
            # Diagram extended to negative correlations
            self.tmax = NP.pi
            rlocs = NP.concatenate((-rlocs[:0:-1], rlocs))
        else:
            # Diagram limited to positive correlations
            self.tmax = NP.pi/2
        tlocs = NP.arccos(rlocs)        # Conversion to polar angles
        gl1 = GF.FixedLocator(tlocs)    # Positions
        tf1 = GF.DictFormatter(dict(zip(tlocs, map(str, rlocs))))
        
         # Standard deviation axis extent (in units of reference stddev)
        self.smin = srange[0] * self.refstd
        self.smax = srange[1] * self.refstd
        
        ghelper = FA.GridHelperCurveLinear(
            tr,
            extremes=(0, self.tmax, self.smin, self.smax),
            grid_locator1=gl1, tick_formatter1=tf1)

        if fig is None:
            fig = PLT.figure()

        ax = FA.FloatingSubplot(fig, rect, grid_helper=ghelper)
        fig.add_subplot(ax)

        # Adjust axes
        ax.axis["top"].set_axis_direction("bottom")   # "Angle axis"
        ax.axis["top"].toggle(ticklabels=True, label=True)
        ax.axis["top"].major_ticklabels.set_axis_direction("top")
        ax.axis["top"].label.set_axis_direction("top")
        ax.axis["top"].label.set_text("Correlation coefficient")

        ax.axis["left"].set_axis_direction("bottom")  # "X axis"
        ax.axis["left"].label.set_text("Standard deviation")

        ax.axis["right"].set_axis_direction("top")    # "Y-axis"
        ax.axis["right"].toggle(ticklabels=True)
        ax.axis["right"].major_ticklabels.set_axis_direction(
            "bottom" if extend else "left")

        if self.smin:
            ax.axis["bottom"].toggle(ticklabels=False, label=False)
        else:
            ax.axis["bottom"].set_visible(False)          # Unused

        self._ax = ax                   # Graphical axes
        self.ax = ax.get_aux_axes(tr)   # Polar coordinates

        # Add reference point and stddev contour
        l, = self.ax.plot([0], self.refstd, 'k*',
                          ls='', ms=10, label=label)
        t = NP.linspace(0, self.tmax)
        r = NP.zeros_like(t) + self.refstd
        self.ax.plot(t, r, 'k--', label='_')

        # Collect sample points for latter use (e.g. legend)
        self.samplePoints = [l]

    def add_sample(self, stddev, corrcoef, *args, **kwargs):
        """
        Add sample (*stddev*, *corrcoeff*) to the Taylor
        diagram. *args* and *kwargs* are directly propagated to the
        `Figure.plot` command.
        """

        l, = self.ax.plot(NP.arccos(corrcoef), stddev,
                          *args, **kwargs)  # (theta, radius)
        self.samplePoints.append(l)

        return l

    def add_grid(self, *args, **kwargs):
        """Add a grid."""

        self._ax.grid(*args, **kwargs)

    def add_contours(self, levels=5, **kwargs):
        """
        Add constant centered RMS difference contours, defined by *levels*.
        """

        rs, ts = NP.meshgrid(NP.linspace(self.smin, self.smax),
                             NP.linspace(0, self.tmax))
        # Compute centered RMS difference
        rms = NP.sqrt(self.refstd**2 + rs**2 - 2*self.refstd*rs*NP.cos(ts))

        contours = self.ax.contour(ts, rs, rms, levels, **kwargs)

        return contours


def test1():
    #"""Display a Taylor diagram in a separate axis."""

    # Reference dataset - avg of models
    x = X
    data = X
    refstd = 174.0605         # Reference standard deviation data.std(ddof=1)

    # Model data
    m1 = Data['BCC-CSM2-M']    # Model 1
    m2 = Data['CanESM5_esm']       # Model 2
    m3 = Data['NorESM2-LM']  # Model 3
    m4 = Data['CESM2_esm']     #Model 4
    m5 = Data['MPI-ESM1-2']    #Model 5
    m6 = Data['EC-Earth3']     # Model 6
    m7 = Data['ACCESS-ESM1']  # Model 7
    m8 = Data['GISS-E2-1-G']   # Model 8
    

    # Compute stddev and correlation coefficient of models
    samples = NP.array([ [m.std(ddof=1), NP.corrcoef(data, m)[0, 1]]
                      for m in (m1, m2, m3, m4, m5, m6, m7, m8)])

    fig = PLT.figure(figsize=(12,5.5))

    #Taylor diagram
    dia = TaylorDiagram(refstd, fig=fig, rect=122, label="Average",
                        srange=(0, 1.8))

    colors = PLT.matplotlib.cm.jet(NP.linspace(0, 1, len(samples)))



     #Add the models to Taylor diagram
    for i, (stddev, corrcoef) in enumerate(samples):
       dia.add_sample(stddev, corrcoef,
                     marker='.', ms=10, ls='',
                     mfc=colors[i], mec=colors[i],
                     label=labels[i])

    #Add grid
    dia.add_grid()

    #Add RMS contours, and label them
    contours = dia.add_contours(colors='0.5')
    PLT.clabel(contours, inline=1, fontsize=10, fmt='%.2f')

    #Add a figure legend
    fig.legend(dia.samplePoints,
              [ p.get_label() for p in dia.samplePoints ],
             numpoints=1, prop=dict(size='small'), loc='upper right')

    return dia


if __name__ == '__main__':

    dia = test1()
    PLT.show()


# In[ ]:




