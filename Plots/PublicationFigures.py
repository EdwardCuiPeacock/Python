# -*- coding: utf-8 -*-
"""
Created on Sat Jun 06 13:35:08 2015

@author: Edward
"""
DEBUG = True

import os
import numpy as np
from ImportData import FigureData
# import matplotlib
# matplotlib.use('Agg') # use 'Agg' backend
import matplotlib.pyplot as plt

plotType = 'barplot'
Style = 'Vstack'
exampleFolder = 'C:/Users/Edward/Documents/Assignments/Scripts/Python/Plots/example/'

# global variables
# fontname = os.path.abspath(os.path.join(os.path.dirname(__file__), 'resource/Helvetica.ttf')) # font .ttf file path
fontname = 'Arial'
fontsize = {'title':16, 'xlab':12, 'ylab':12, 'xtick':10,'ytick':10, 'texts':12,
            'legend': 12, 'legendtitle':12} # font size
color = ['#1f77b4','#ff7f0e', '#2ca02c','#d62728','#9467bd','#8c564b','#e377c2','#7f7f7f','#bcbd154','#17becf'] # tableau10, or odd of tableau20
marker = ['o', 's', 'd', '^', '*', 'p']# scatter plot line marker cycle
hatch = ['/','\\','-', '+', 'x', 'o', 'O', '.', '*'] # fill patterns potentially used for filled objects such as bars


class PublicationFigures(object):
    """Generate publicatino quantlity figures
        Data: FigureData, or data file path
        PlotType: currently supported plot types include:
            ~ LinePlot: for categorical data, with error bar
                Style:
                    'Twin' -- Same plot, 2 y-axis (left and right of plot)
                    'Vstacked' (default) -- vertically stacked subplots
            ~ Beeswarm: beeswarm plot; boxplot with scatter points
                Style: 'hex','swarm' (default),'center','square'
    """
    def __init__(self, dataFile=None, SavePath=None):
        """Initialize class
        """
        if isinstance(dataFile, str):
            self.LoadData(dataFile) # load data
        elif isinstance(dataFile, FigureData):
            self.data = dataFile
        self.SavePath = SavePath
        self.cache=0 # for progressive draw of objects

    def LoadData(self, dataFile):
        """To be called after object creation"""
        self.data = FigureData(dataFile)
  
    def AdjustFigure(func):
        """Used as a decotrator to set the figure properties"""
        def wrapper(self, *args, **kwargs):
            res = func(self, *args, **kwargs) # execute the function as usual
            self.SetFont() # adjust font
            self.fig.set_size_inches(6, 5) # set figure size
            self.fig.tight_layout() # tight layout
            return res
        return wrapper
        
    def Save(self, SavePath=None, dpi=300):
        """
        SavePath: full path to save the image. Image type determined by file
            extention
        dpi: DPI of the saved image. Default 300.
        """
        if SavePath is not None: # overwrite with new savepath
            self.SavePath = SavePath
        if self.SavePath is None: # save to current working directory
            self.SavePath = os.path.join(os.getcwd(),'Figure.eps')
        self.fig.savefig(self.SavePath, bbox_inches='tight', dpi=dpi)

    """ ####################### Plot utilities ####################### """
    @AdjustFigure
    def Traces(self, groupings=None, scalebar=True, annotation=None,
               color=['#000000', '#ff0000', '#0000ff', '#ffa500', '#007f00',
               '#00bfbf', '#bf00bf']):
        """Plot time series / voltage and current traces
        groupings: grouping of y data. E.g [[1,2],[3]] will result two
        subplots, where y1 and y2 are in the same subplot above, and y3 below.
        color: default MATLAB's color scheme
        """
        m = 0 # row, indexing y axis data
        n = 0 # column, indexing x axis or time data
        c = 0 # indexing color cycle or traces in a subplot
        self.fig, self.axs = plt.subplots(nrows=1,ncols=1, sharex=True)
        hline = plt.plot(self.data.series['x'][m], self.data.series['y'][n],
                         color=color[c%len(color)])
        # set aspect ratio
        self.SetAspectRatio(r=2, adjustable='box-forced',continuous=True)
        if scalebar: # Use scale bar instead of axis
            self.AddTraceScaleBar(hline[0], xunit=self.data.meta['xunit'],
                                  yunit=self.data.meta['yunit'])
        else: # Use axis
            self.SetDefaultAxis() # use default axis
            self.axs.set_xlabel(self.data.meta['xlabel'])
            self.axs.set_ylabel(self.data.meta['ylabel'])
        if annotation:
            self.TextAnnotation(text=annotation) # description of the trace
    
    @AdjustFigure
    def Scatter(self, color=color, marker=marker, alpha=0.5, legend_on=True):
        """2D Scatter plot
        color = blue, magenta, purple, orange, green
        marker = circle, pentagon, pentagram star,star, + sign
        """
        self.fig, self.axs = plt.subplots(nrows=1,ncols=1)
        for n in range(self.data.num['x']): # add each set of data
            label = self.data.meta['group'][n] \
                    if 'group' in self.data.meta else None
            plt.scatter(self.data.series['x'][n],
                        self.data.series['y'][n],  alpha=alpha, s=50,
                        marker=marker[n%len(marker)],
                        color=color[n%len(color)], label=label)
        self.SetDefaultAxis()
        self.axs.set_xlabel(self.data.meta['xlabel'])
        self.axs.set_ylabel(self.data.meta['ylabel'])
        if self.data.num['x']>1 and legend_on: # set legend
            self.axs.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

    @AdjustFigure
    def Scatter3D(self, color=color, marker=['.', '+', 'x', (5, 2), '4']):
        from mpl_toolkits.mplot3d import Axes3D # for 3D plots
        self.fig = plt.figure()
        self.axs = self.fig.add_subplot(111, projection='3d')
        for n in range(self.data.num['x']):
            try: # lazy handling, error upon KeyError, IndexError
                label = self.data.meta['group'][n]
            except:
                label = None
            self.axs.scatter(self.data.series['x'][n],self.data.series['y'][n],
                             self.data.series['z'][n],zdir=u'z', s=144,
                             c='k', label=label,marker=marker[n%len(marker)],
                             depthshade=True) # s=144 --> sqrt(s) point font
        self.axs.set_xlabel(self.data.meta['xlabel'])
        self.axs.set_ylabel(self.data.meta['ylabel'])
        if self.data.series['z']:
            self.axs.set_zlabel(self.data.meta['zlabel'])
        # Add annotations
        #self.AddRegions()
        self.SetDefaultAxis3D() # default axis, view, and distance
    
    @AdjustFigure
    def BarPlot(self, Style='Vertical', width=0.27, color=color, hatch=None, 
                alpha=0.4, linewidth=0):
        """Plot bar graph
        Style: style of bar graph, can choose 'Vertical' and 'Horizontal'
        width: width of bar. Default 0.27
        space: space between bar. Default 0.
        color: blue, magenta, purple, orange, green
        """
        # Get bar plot function according to style
        nseries = self.data.num['y']
        # number of series
        ngroups = max(self.data.size['y'])
        # leftmost position of bars
        pos = np.arange(ngroups)-nseries/2*width
        self.x = range(0,len(self.data.series['x'][0]))
        # initialize plot
        self.fig, self.axs = plt.subplots(nrows=1,ncols=1, sharex=True)
        # plot each series at a time
        for n, s in enumerate(self.data.series['y']):
            try:
                err = self.data.series['errorbar'][n]
            except: # lazy handling, error upon KeyError, IndexError
                err = None
            if Style=='Vertical':
                bars = self.axs.bar(pos+n*width, s, width,  yerr=err, 
                                    alpha=alpha, align='center',
                                    label=self.data.meta['y'][n])
            else:
                bars = self.axs.barh(pos+n*width, s, width,  yerr=err, 
                                    alpha=alpha,align='center',
                                    label=self.data.meta['y'][n])
            # Set color
            self.SetColor(bars, color, n, linewidth)             
            # Set hatch if available
            self.SetHatch(bars, hatch, n)
        self.SetDefaultAxis()
        if Style=='Vertical':
            self.SetCategoricalXAxis()
            self.AdjustBarPlotXAxis()
        else: # horizontal
            self.AdjustBarPlotYAxis()
            self.SetCategoricalYAxis()
        # Set labels
        self.axs.set_xlabel(self.data.meta['xlabel'])
        self.axs.set_ylabel(self.data.meta['ylabel'])

        if n>0: # for multiple series, add legend
            self.axs.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        
    @AdjustFigure
    def Beeswarm(self, Style='swarm',color=color):
        """Beeswarm style boxplot
        color: blue, magenta, purple, orange, green
        """
        from beeswarm import beeswarm
        # boardcasting color cycle
        num = self.data.num['y']
        color = num/len(color)*color+color[0:num%len(color)]
        self.bs, self.axs = beeswarm(self.data.series['y'], method=Style,
                                     labels=self.data.series['x'][0],col=color)
        # Format style
        # make sure axis tickmark points out
        self.axs.tick_params(axis='both',direction='out')
        self.axs.spines['right'].set_visible(False)
        self.axs.spines['top'].set_visible(False)
        self.axs.xaxis.set_ticks_position('bottom')
        self.axs.yaxis.set_ticks_position('left')
        # Set Y label, if exsit
        try:
            self.axs.set_ylabel(self.data.names['x'][0])
        except:
            pass
        self.SetAspectRatio(r=0.5, adjustable='box-forced',continuous=True)
        # save current figure handle
        self.fig = plt.gcf()

    @AdjustFigure
    def Histogram(self, Style='Hstack'):
        """Plot histogram"""
        n, bins, patches = P.hist(x, 50, normed=1, histtype='stepfilled')
        P.setp(patches, 'facecolor', 'g', 'alpha', 0.75)
        return

    def HistogramHstack(self):
        return

    def HistogramMirror(self):
        return
        
    @AdjustFigure
    def LinePlot(self, Style='Vstack'):
        self.x = range(len(self.data.series['x'][0])) # set categorical x
        if Style=='Vstack' or self.data.num['y'] < 2:
            self.LinePlotVstack()
        else:
            self.LinePlotTwin()
        self.SetAspectRatio(r=2, adjustable='box-forced',continuous=True)
        self.SetCategoricalXAxis() # make some space for each category
        # Add some margins to the plot so that it is not touching the axes
        plt.margins(0.25,0.25)

    def LinePlotVstack(self):
        """ Line plots stacked vertically"""
        self.fig, self.axs = plt.subplots(nrows=self.data.num['y'],ncols=1,
                                          sharex=True)
        boolmultiplot = isinstance(self.axs, np.ndarray)
        self.axs = np.array([self.axs]) if not boolmultiplot else self.axs
        for n, ax in enumerate(self.axs):
            # Plot error bar
            ax.errorbar(self.x,self.data.series['y'][n], color='k',
                        yerr = [self.data.stats['y']['ebp'][n],
                                self.data.stats['y']['ebn'][n]])
        self.axs = self.axs[0] if not boolmultiplot else self.axs
        self.SetVstackAxis() # set vertical stacked subplot axes

    def LinePlotTwin(self, color=('k','r')):
        """ Line plots with 2 y-axis"""
        self.fig, self.axs = plt.subplots(nrows=1,ncols=1, sharex=True)
        self.axs = np.array([self.axs, self.axs.twinx()])
        for n, ax in enumerate(self.axs):
             # Plot error bar
            ax.errorbar(self.x, self.data.series['y'][n], color=color[n],
                        yerr = [self.data.stats['y']['ebp'][n],
                                self.data.stats['y']['ebn'][n]])
        self.SetTwinPlotAxis(colors=color) # set twin plot subplot axes

    """ ####################### Axis schemas ####################### """
    def SetDefaultAxis(self, ax=None):
        """Set default axis appearance"""
        def SDA(ax): # short for set default axis
            ax.tick_params(axis='both',direction='out')
            ax.spines['left'].set_visible(True)
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.spines['bottom'].set_visible(True)
            ax.xaxis.set_ticks_position('bottom')
            ax.yaxis.set_ticks_position('left')
        SDA_vec = np.frompyfunc(SDA,1,1) # vectorize the closure
        if ax is None:
            SDA_vec(self.axs)
        else:  # allow this function to be called outside class
            SDA_vec(ax)

    def SetDefaultAxis3D(self, ax=None, elev=45, azim=60, dist=12):
        def SDA3D(ax): # short for set default axis 3d
            ax.tick_params(axis='both', direction='out')
            ax.view_init(elev=elev, azim=azim) # set perspective
            ax.dist = dist # use default axis distance 10
            if ax.azim > 0: # z axis will be on the left
                ax.zaxis.set_rotate_label(False) # prevent auto rotation
                a = ax.zaxis.label.get_rotation()
                ax.zaxis.label.set_rotation(90+a) # set custom rotation
                ax.invert_xaxis() # make sure (0,0) in front
                ax.invert_yaxis() # make sure (0,0) in front
            else:
                ax.invert_xaxis() # make sure (0,0) in front
            #ax.zaxis.label.set_color('red')
            #ax.yaxis._axinfo['label']['space_factor'] = 2.8
        SDA3D_vec = np.frompyfunc(SDA3D,1,1)
        if ax is None:
            SDA3D_vec(self.axs)
        else: # allow this function to be called outside class
            SDA3D_vec(ax)

    def TurnOffAxis(self, ax=None):
        """Turn off all axis"""
        def TOA(ax): # short for turn off axis
            ax.spines['left'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.xaxis.set_visible(False)
            ax.yaxis.set_visible(False)
        TOA_vec = np.frompyfunc(TOA,1,1) # vectorize the closure
        if ax is None:
            TOA_vec(self.axs)
        else: # allow this function to be called outside class
            TOA_vec(ax)

    def AdjustBarPlotXAxis(self):
        """Adjust bar plot's x axis for categorical axis"""
        # get y axis extent
        ymin, ymax = self.axs.get_ybound()
        if ymax <= 0.0: # only negative data present
            # flip label to top
            self.axs.spines['bottom'].set_position('zero') # zero the x axis
            self.axs.tick_params(labelbottom=False, labeltop=True)
        elif ymin >= 0.0: # only positive data present. Default
            self.axs.spines['bottom'].set_position('zero') # zero the x axis
        else: # mix of positive an negative data : set all label to bottoms
            self.axs.spines['bottom'].set_visible(False)
            self.axs.spines['top'].set_visible(True)
            self.axs.spines['top'].set_position('zero')
        self.axs.xaxis.set_ticks_position('none')

    def AdjustBarPlotYAxis(self):
        """Adjust bar plot's y axis for categorical axis"""
        #set all label to left
        self.axs.spines['left'].set_visible(False)
        self.axs.spines['right'].set_visible(True)
        self.axs.spines['right'].set_position('zero')
        self.axs.yaxis.set_ticks_position('none')

    def SetTwinPlotAxis(self, colors=('k', 'r')):
        """Axis style  of 2 plots sharing y axis"""
        spineName = ('left','right')
        for n, ax in enumerate(self.axs):             # For twin Plot
            ax.tick_params(axis='both',direction='out') # tick mark out
            ax.spines['top'].set_visible(False) # remove top boundary
            ax.xaxis.set_ticks_position('bottom') # keep only bottom ticks
            ax.set_ylabel(self.data.names['y'][n]) # set y label
            ax.yaxis.label.set_color(colors[n]) # set y label color
            ax.tick_params(axis='y',colors=colors[n]) # set y tick color
            ax.spines[spineName[n]].set_color(colors[n]) # set y spine color
        self.axs[0].set_xlabel(self.data.names['x'][0]) # x label

    def SetVstackAxis(self):
        """Axis style of vertically stacked subplots"""
        def SVsA(ax, n):
            ax.tick_params(axis='both', direction='out') #tick mark out
            ax.spines['top'].set_visible(False) # remove top boundary
            ax.spines['right'].set_visible(False) # remove right spine
            ax.yaxis.set_ticks_position('left') # keep only left ticks
            ax.set_ylabel(self.data.names['y'][n]) # set different y labels
            if ax.is_last_row():     #keep only bottom ticks
                ax.xaxis.set_ticks_position('bottom')
                ax.set_xlabel(self.data.names['x'][0]) # x label
            else:
                ax.xaxis.set_visible(False)
                ax.spines['bottom'].set_visible(False)
        SVsA_vec = np.frompyfunc(SVsA,2,1)
        num_axs = len(self.axs) if isinstance(self.axs, np.ndarray) else 1
        SVsA_vec(self.axs, range(num_axs))
        self.fig.tight_layout(h_pad=0.01) # pad height

    def SetHstackAxis(self):
        """Axis style of horizontally stacked / concatenated subplots"""
        def SHsA(ax, n):
            ax.tick_params(axis='both', direction='out') # tick mark out
            ax.spine['top'].set_visible(False) #remove top boundary
            ax.spine['right'].set_visible(False) # remove right spine
            ax.yaxis.set_ticks_position('left') # keep only left ticks
            ax.set_xlabel(self.data.names['x'][n]) # set different x labels
            if ax.is_first_col(): # keep only first ticks
                ax.yaxis.set_ticks_position('left')
                ax.set_ylabel(self.data.names['y'][0]) # y label
            else:
                ax.yaxis.set_visible(False)
                ax.spines['left'].set_visible(False)
        SHsA_vec = np.frompyfunc(SHsA,2,1)
        num_axs = len(self.axs) if isinstance(self.axs, np.ndarray) else 1
        SHsA_vec(self.axs, range(num_axs))
        self.fig.tight_layout(w_pad=0.01) # pad width

    def SetCategoricalXAxis(self, ax=None):
        """Additional settings for plots with categorical data"""
        # change the x lim on the last, most buttom subplot
        if ax is None: # last axis, or self.axs is a single axis
            ax = self.axs[-1] if isinstance(self.axs, np.ndarray) else self.axs
        if ax.get_xlim()[0] >= self.x[0]:
            ax.set_xlim(ax.get_xticks()[0]-1,ax.get_xlim()[-1])
        if ax.get_xlim()[-1] <= self.x[-1]:
            ax.set_xlim(ax.get_xlim()[0], ax.get_xticks()[-1]+1)
        plt.xticks(self.x, self.data.series['x'][0])

    def SetCategoricalYAxis(self, ax=None):
        """Additional settings for plots with categorical data"""
        if ax is None: # last axis, or self.axs is a single axis
            ax = self.axs[-1] if isinstance(self.axs, np.ndarray) else self.axs
        if ax.get_ylim()[0] >= self.x[0]:
            ax.set_ylim(ax.get_yticks()[0]-1,ax.get_ylim()[-1])
        if ax.get_ylim()[-1] <= self.x[-1]:
            ax.set_ylim(ax.get_ylim()[0], ax.get_yticks()[-1]+1)
        plt.yticks(self.x, self.data.series['x'][0])

    def SetDiscontinousAxis(self, x=None, y=None):
        """Plot with discontious axis. Allows one discontinuity for each axis.
        Assume there is only 1 plot in the figure
        x: x break point
        y: y break point
        """
        if x is not None and y is not None:
            f,axs = plt.subplots(2,2,sharex=True,sharey=True)
        elif x is not None and y is None:
            f,axs = plt.subplots(2,1,sharey=True)
        elif x is None and y is not None:
            f,axs = plt.subplots(2,1,sharex=True)
        line = self.axs.get_lines()
        # plot the same data in all the subplots
        [ax.add_line(line) for ax in axs]
        # set axis
        self.SetVstackAxis() # set vertical stacked subplot axes
        for ax in self.axs:
            if not ax.is_first_col:
                ax.yaxis.set_visible(False)
                ax.spines['left'].set_visible(False)
        # add slashes between two plots

    def SetAspectRatio(self, r=2, adjustable='box-forced', continuous=True):
        def SAR(ax):
            if not isinstance(r, str) and continuous:
                X, Y = np.ptp(ax.get_xticks()), np.ptp(ax.get_yticks())
                aspect = X/Y/r
            else:
                aspect = r
            ax.set_aspect(aspect=aspect, adjustable=adjustable)
        SAR_vec = np.frompyfunc(SAR,1,1) # vectorize the closure
        SAR_vec(self.axs)
        #self.fig.tight_layout(h_pad=0.05) # enforce tight layout
        
    def SetColor(self, plotobj, color, n, linewidth=0):
        """Set colors. Would allow optionally turn off color"""
        if color is not None:
            for p in plotobj:
                p.set_color(color[n%len(color)])
                p.set_linewidth(linewidth)
        else:
            for p in plotobj:
                p.set_color('w')
                p.set_edgecolor('k')
                p.set_linewidth(1)
                
    def SetHatch(self, plotobj, hatch, n):
        """Set hatch for patchs"""
        if hatch is not None:
            for p in plotobj:
                p.set_hatch(hatch[n%len(hatch)])
        


    """ ####################### Annotations ####################### """
    def AddTraceScaleBar(self, hline, xunit, yunit, color=None):
        """Add scale bar on trace. Specifically designed for voltage /
        current / stimulus vs. time traces."""
        def scalebarlabel(x, unitstr):
            if unitstr.lower()[0] == 'm':
                return(str(x)+unitstr if x<1000 else str(x/1000)+
                    unitstr.replace('m',''))
            elif unitstr.lower()[0] == 'p':
                return(str(x)+unitstr if x<1000 else str(x/1000)+
                    unitstr.replace('p','n'))

        self.TurnOffAxis() # turn off axis
        X, Y = np.ptp(self.axs.get_xticks()), np.ptp(self.axs.get_yticks())
        # calculate scale bar unit length
        X, Y = self.roundto125(X/5), self.roundto125(Y/5)
        # Parse scale bar labels
        xlab, ylab = scalebarlabel(X, xunit), scalebarlabel(Y, yunit)
        # Get color of the scalebar
        color = plt.getp(hline,'color')
        # Calculate position of the scale bar
        xi = np.max(self.axs.get_xticks()) + X/10.0
        yi = np.mean(self.axs.get_yticks())
        # calculate position of text
        xtext1, ytext1 = xi+X/2.0, yi-Y/10.0 # horizontal
        xtext2, ytext2 = xi+X+X/10.0, yi+Y/2.0 # vertical
        # Draw text
        txt1 = self.axs.text(xtext1, ytext1, xlab, ha='center',va='top',
                             color=color)
        self.AdjustText(txt1) # adjust texts just added
        txt2 = self.axs.text(xtext2, ytext2, ylab, ha='left',va='center',
                             color=color)
        self.AdjustText(txt2) # adjust texts just added
        # Draw Scale bar
        self.axs.annotate("", xy=(xi,yi), xycoords='data',  # horizontal
                          xytext=(xi+X,yi), textcoords = 'data',
                          annotation_clip=False,arrowprops=dict(arrowstyle="-",
                          connectionstyle="arc3", shrinkA=0, shrinkB=0,
                          color=color))
        self.axs.annotate("", xy=(xi+X,yi), xycoords='data',  # vertical
                          xytext=(xi+X,yi+Y), textcoords = 'data',
                          annotation_clip=False,arrowprops=dict(arrowstyle="-",
                          connectionstyle="arc3", shrinkA=0, shrinkB=0,
                          color=color))
        #txtbb = txt1.get_bbox_patch().get_window_extent()
        #print(txtbb.bounds)
        #print(self.axs.transData.inverted().transform(txtbb).ravel())

    def TextAnnotation(self, text="", position='south'):
        return # not done yet

    def DrawEllipsoid(self, center, radii=None, rvec=np.eye(3), \
                      A=None, numgrid=100, ax=None, color=color, alpha=0.6):
        """Draw an ellipsoid given its parameters
        center: center [x0,y0,z0]
        radii: radii of the ellipsoid [rx, ry, rz]
        rvec: vector of the radii that indicates orientation. Default identity
        A: orientation matrix 3x3, where each row is a vector of radii, can be
            supplied directly instead of radii and rvec
        numgrid: number of points to estimate the ellipsoid. The higher the 
            number, the smoother the plot. Defualt 100.
        """
        
        # Caculate ellipsoid coordinates
        x,y,z = self.Ellipsoid(center, radii, rvec, A, numgrid)
        if ax is None:
            if not (isinstance(self.axs, np.ndarray) or \
                    isinstance(self.axs, list)):
                ax = self.axs # only 1 axis
            else:
                return
        ax.plot_surface(x,y,z,rstride=4,cstride=4,linewidth=0,\
                              alpha=alpha,color=color[self.cache%len(color)])
        self.cache += 1 # increase color cache index by 1
    
    def DrawRect(self, x,y,w,h, ax=None, color=color, alpha=0.6):
        """Draw a rectangular bar
        x,y,w,h: xcenter, ycenter, width, height        
        """
        from matplotlib.patches import Rectangle
        if ax is None:
            if not (isinstance(self.axs, np.ndarray) or \
                    isinstance(self.axs, list)):
                ax = self.axs # only 1 axis
            else:
                return
        ax.add_patch(Rectangle((x-w/2.0, y-h/2.0), w, h, angle=0.0, \
                            facecolor=color[self.cache%len(color)]))
        self.caceh += 1 # increase color cache index by 1

    def AnnotateOnGroup(self, m, text='*', vpos=None):
        """Help annotate statistical significance over each group in Beeswarm /
        bar graph. Annotate several groups at a time.
        m: indices of the group. This is required.
        text: text annotation above the group. Default is an asterisk '*'
        vpos: y value of the text annotation, where text is positioned. Default
              is calculated by this method. For aesthetic reason, vpos will be
              applied to all groups specified in m
        """
        # Calculate default value of vpos
        if vpos is None:
            I = self.axs.get_yticks()
            yinc = I[1]-I[0] # y tick increment
            Y = [max(x) for x in self.data.series['y']]
            vpos = max([Y[k] for k in m])+yinc/5.0
        X = self.axs.get_xticks()
        for k in m:
            txt = self.axs.text(X[k], vpos, text, ha='center',va='top')
            # adjust text so that it is not overlapping with data or title
            self.AdjustText(txt)

    def AnnotateBetweenGroups(self, m=0, n=1, text='*', hgap=0):
        """Help annotate statistical significance between two groups in the
        Beeswarm / bar plot. Annotate one pair at a time.
            m, n indicates the index of the loci to annotate between.
            By default, m=0 (first category), and n=1 (second category)
        text: annotation text above the bracket between the two loci.
            Default is an asterisk "*" to indicate significance.
        hgap: horizontal gap between neighboring annotations. Default is 0.
            No gap will be added at m=0 or n=1
        All annotations are stored in self.axs.texts, a list of text objects.
        """
        # Calculate Locus Position
        X = self.axs.get_xticks()
        I = self.axs.get_yticks()
        Y = [max(x) for x in self.data.series['y']]
        yinc = I[1]-I[0] # y tick increment
        ytop = max(I) + yinc/10.0 # top of the annotation
        yoffset = (ytop-max(Y[m],Y[n]))/2.0
        # position of annotation bracket
        xa, xb = X[m]+hgap*int(m!=0), X[n]-hgap*int(n!=max(X))
        ya, yb = yoffset + Y[m], yoffset + Y[n]
        # position of annotation text
        xtext, ytext = (X[m]+X[n])/2.0, ytop+yinc/10.0
        # Draw text
        txt = self.axs.text(xtext,ytext, text, ha='center',va='bottom')
        # adjust text so that it is not overlapping with data or title
        self.AdjustText(txt)
        # Draw Bracket
        self.axs.annotate("", xy=(xa,ya), xycoords='data',
                          xytext=(xa,ytop), textcoords = 'data',
                          annotation_clip=False,arrowprops=dict(arrowstyle="-",
                          connectionstyle="arc3", shrinkA=0, shrinkB=0))
        self.axs.annotate("", xy=(xa,ytop), xycoords='data',
                          xytext=(xb,ytop), textcoords = 'data',
                          annotation_clip=False,arrowprops=dict(arrowstyle="-",
                          connectionstyle="arc3", shrinkA=0, shrinkB=0))
        self.axs.annotate("", xy=(xb,ytop), xycoords='data',
                          xytext=(xb,yb), textcoords = 'data',
                          annotation_clip=False,arrowprops=dict(arrowstyle="-",
                          connectionstyle="arc3", shrinkA=0, shrinkB=0))

    def AdjustText(self,txt):
        """Adjust text so that it is not being cutoff"""
        #renderer = self.axs.get_renderer_cache()
        txt.set_bbox(dict(facecolor='w', alpha=0, boxstyle='round, pad=1'))
        plt.draw() # update the text draw
        txtbb = txt.get_bbox_patch().get_window_extent() # can specify render
        xmin, ymin, xmax, ymax = tuple(self.axs.transData.inverted().
                                        transform(txtbb).ravel())
        xbnd, ybnd = self.axs.get_xbound(), self.axs.get_ybound()
        if xmax > xbnd[-1]:
            self.axs.set_xbound(xbnd[0], xmax)
        if xmin < xbnd[0]:
            self.axs.set_xbound(xmin, xbnd[-1])
        if ymax > ybnd[-1]:
            self.axs.set_ybound(ybnd[0], ymax)
        if ymin < ybnd[0]:
            self.axs.set_ybound(ymin, ybnd[-1])

    def RemoveAnnotation(self):
        """Remove all annotation and start over"""
        self.axs.texts = []

    """ ####################### Misc ####################### """

    @staticmethod
    def roundto125(x, r=np.array([1,2,5,10])): # helper static function
        """5ms, 10ms, 20ms, 50ms, 100ms, 200ms, 500ms, 1s, 2s, 5s, etc.
        5mV, 10mV, 20mV, etc.
        5pA, 10pA, 20pA, 50pA, etc."""
        p = int(np.floor(np.log10(x))) # power of 10
        y = r[(np.abs(r-x/(10**p))).argmin()] # find closest value
        return(y*(10**p))

    def SetFont(self, fontsize=fontsize,fontname=fontname,items=None):
        """Change font properties of all axes
        fontsize: size of the font, specified in the global variable
        fontname: fullpath of the font, specified in the global variable
        items: select a list of items to change font. ['title', 'xlab','ylab',
               'xtick','ytick', 'texts','legend','legendtitle']
        """
        if (fontname is None) and (fontsize is None):
            return
        import matplotlib.font_manager as fm
        def CF(ax):
            itemDict = {'title':[ax.title], 'xlab':[ax.xaxis.label],
                        'ylab':[ax.yaxis.label], 'xtick':ax.get_xticklabels(),
                        'ytick':ax.get_yticklabels(),
                        'texts':ax.texts if isinstance(ax.texts, np.ndarray)
                                or isinstance(ax.texts, list) else [ax.texts],
                        'legend': [] if ax.legend_ is None
                                        else ax.legend_.get_texts(),
                        'legendtitle':[] if ax.legend_ is None
                                            else [ax.legend_.get_title()]}
            itemList, keyList = [], []
            if items is None: # get all items
                for k, v in iter(itemDict.items()):
                    itemList += v
                    keyList += [k]*len(v)
            else: # get only specified item
                for k in items:
                    itemList += itemDict[k] # add only specified in items
                    keyList += [k]*len(itemDict[k])
            # initialize fontprop object
            fontprop = fm.FontProperties(style='normal', weight='normal',
                                         stretch = 'normal')
            if os.path.isfile(fontname): # check if font is a file
                fontprop.set_file(fontname)
            else:# check if the name of font is available in the system
                if not any([fontname.lower() in a.lower() for a in
                        fm.findSystemFonts(fontpaths=None, fontext='ttf')]):
                     print('Cannot find specified font: %s' %(fontname))
                fontprop.set_family(fontname) # set font name
            # set font for each object
            for n, item in enumerate(itemList):
                if isinstance(fontsize, dict):
                    fontprop.set_size(fontsize[keyList[n]])
                elif n <1: # set the properties only once
                    fontprop.set_size(fontsize)
                item.set_fontproperties(fontprop) # change font for all items

        CF_vec = np.frompyfunc(CF,1,1) # vectorize the closure
        CF_vec(self.axs)
    
    @staticmethod
    def Ellipsoid(center, radii=None, rvec=np.eye(3), A=None, numgrid=100):
        """Matrix description of ellipsoid
        center: center [x0,y0,z0]
        radii: radii of the ellipsoid [rx, ry, rz]
        rvec: vector of the radii that indicates orientation. Default identity
        A: orientation matrix 3x3, where each row is a vector of radii, can be
            supplied directly instead of radii and rvec
        numgrid: number of points to estimate the ellipsoid. The higher the 
            number, the smoother the plot. Defualt 100.
        return: x, y, z coordinates
        """
        # Ellipsoid (x-c)'A(x-c) = 1
        # find the rotation matrix and radii of the axes
        # A = eigvec * diag(eigvalue) * inv(eigvec)
        if A is None:
            if radii is None:
                raise IOError("radii/rvec and A cannot be both None")
            A = rvec.dot(np.diag(1.0/radii**2)).dot(np.linalg.inv(rvec))
        # Note that this step is necessary to sort out x, y, z
        U, S, V = np.linalg.svd(A) # A = USV', V is returned as V'
        radii = 1.0/np.sqrt(S)
        # Spherical coordinate
        u = np.linspace(0.0, 2.0*np.pi, numgrid) # 100 grid resolution
        v = np.linspace(0, np.pi, numgrid-10) #100 grid resolution
        # Convert to Cartesian
        x = radii[0] * np.outer(np.cos(u), np.sin(v))
        y = radii[1] * np.outer(np.sin(u), np.sin(v))
        z = radii[2] * np.outer(np.ones_like(u), np.cos(v))
        X = np.rollaxis(np.array([x,y,z]), 0, 3)
        X = X.dot(V.T) + center.reshape((1, 1, -1)) # rotation and translation
        return(X[:,:,0], X[:,:,1], X[:,:,2])


if __name__ == "__main__":
    dataFile = os.path.join(exampleFolder, '%s.csv' %plotType)
    # Load data
    K = PublicationFigures(dataFile=dataFile, SavePath=os.path.join(exampleFolder,'%s.png'%plotType))
    if plotType == 'lineplot':
        # Line plot example
        K.LinePlot(Style=Style)
        #K.axs[0].set_ylim([0.5,1.5])
        #K.axs[1].set_ylim([0.05, 0.25])
    elif plotType == 'beeswarm':
        # Beeswarm example
        K.Beeswarm()
        #K.AnnotateOnGroup(m=[0,1])
        K.AnnotateBetweenGroups(text='p=0.01234')
    elif plotType == 'trace':
        # Time series example
        K.Traces()
    elif plotType == 'barplot':
        K.BarPlot(Style='Vertical')
    elif plotType == 'scatter':
        K.Scatter()
    elif plotType == 'scatter3d':
        K.Scatter3D()
    # Final clean up
    K.Save()
