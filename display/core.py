'''Event Display class classes'''
import operator
import math
import os
from ROOT import TCanvas, TH2F, TH1

class Display(object):
    '''
    Main class to produce Event Display windows/plots of the detector and 
    clusters, trajectories etc.
    Separate windows (ViewPane) are shown for the different projections.
    Subscreens (ViewPad) may be used within windows, for exampe to compare 
    simulated and recontructed particles.
    
    Example usage
        self.display = Display(["xy", "yz"], subscreens=["simulated", "reconstructed"])
        self.display.register(self.gdetector, layer=0, clearable=False)
        ... (add clusters tracks lines etc)
        self.display.draw()
    
    '''
    def __init__(self, projections=None, subscreens=None):
        '''@param projections: list of projections eg ['xy', 'yz', 'xz' ,'ECAL_thetaphi', 'HCAL_thetaphi']
                 these will be separate windows
           @param subscreens: list of names of panels within each window eg subscreens=["simulated", "reconstructed"]
                 each of the projection windows will contain all of the subscreens
                 the subscreens can be used to show different aspects of an event, eg simulated particles and reconstructed particles
        '''
        ViewPane.nviews = 0
        if not projections:
            projections = ['xy', 'yz', 'xz']
        self.views = dict() #will store the windows, one per projection
        self.subscreens = subscreens
        #set up the projections
        for view in projections:
            if view in ['yz', 'xz']:
                self.views[view] = ViewPane(view, view, 100, -4, 4, 100, -4, 4, subscreens=subscreens)
            if view in ['xy']:
                self.views[view] = ViewPane(view, view, 100, -4, 4, 100, -4, 4, subscreens=subscreens)
            elif 'thetaphi' in view:
                self.views[view] = ViewPane(view, view,
                                            100, -math.pi/2, math.pi/2,
                                            100, -math.pi, math.pi,
                                            500, 1000, subscreens=subscreens)

    def register(self, obj, layer, clearable=True, sides=None):
        '''object will be registered in every projection and in selected subscreen
           @param obj: thing to be plotted, this will have a draw function. Often will be
                       a ROOT type object such as TGraph, TEllipse etc
           @param layer: what layer in plot to use. Higher layers are plotted **on top- check**
           @param clearable: not sure
           @param sides: if None wil send to all subscreens, otherwise side=0 is first/left subscreen
                         side = 1 is second (right) subscreen
        '''
        elems = [obj]
        if hasattr(obj, '__iter__'):
            elems = obj
        for elem in elems:
            for view in self.views.values():
                view.register(elem, layer, clearable, sides)

    def clear(self):
        for view in self.views.values():
            view.clear()

    def zoom(self, xmin, xmax, ymin, ymax):
        '''intended to be called from the command line
            all projections and subscreens are zoomed
        @param xmin: lower left corner x for the zoomed in screen using hist coordinates
        @param xmax: upper right corner x for the zoomed in screen using hist coordinates
        @param ymin: lower left corner y for the zoomed in screen using hist coordinates
        @param ymax: upper right corner y for the zoomed in screen using hist coordinates
        '''
        for view in self.views.values():
            view.zoom(xmin, xmax, ymin, ymax)

    def unzoom(self):
        '''intended to be called from the command line
           all projections and subscreens are unzoomed
        '''       
        for view in self.views.values():
            view.unzoom()

    def draw(self):
        '''draw all projections and subscreens
        '''           
        for view in self.views.values():
            view.draw()

    def save(self, outdir, filename='', filetype='png'):
        '''write the plot to file (one file per projection)
        @param outdir: directory for output files
        @param filename: base of the final filename eg "event_0" would end up with outputs
                         such as "****xy_event_0_simulation****""
        @param filetype: eg png file output. ***what else is supported***
        '''
        if not os.path.exists(outdir):        
            os.mkdir(outdir) 
        for view in self.views.values():
            view.save(outdir, filename, filetype)

class ViewPane(object): #a graphics window
    nviews = 0
    def __init__(self, name, projection, nx, xmin, xmax, ny, ymin, ymax,
                 dx=600, dy=600, subscreens=None):
        '''arguments
        @name  name = title name for the pane
        @param projection = name of the projection (string)
                            eg one of 'xy', 'yz', 'xz' ,'ECAL_thetaphi', 'HCAL_thetaphi'
        @param nx: points on x axis
        @param xmin: lower left corner x for ROOT hists
        @param xmax: upper right corner x for ROOT hists
        @param nx: points on x axis
        @param ymin: lower left corner y for ROOT hists
        @param ymax: upper right corner y for ROOT hists
        @param dx: horizontal size of each subscreen in pixels
        @param dy: vertical size of each subscreen in pixels
        @param subscreens: list of names of the subscreens
        '''
        self.projection = projection
        self.hists = dict()
        self.registered = dict()
        self.locked = dict()
        tx = 50 + self.__class__.nviews * (dx+10)
        ty = 50
        width = 1
        height = 1
       
        
        #decide how to subdivide the window for the subscreens       
        #normally split screen into horizontally side by side
        self.subscreens = dict()
        if subscreens is None:
            #The projection name and the subscreen name get concatenated. eg "xy: simulated",
            #when there is only one subscreen the subscreen string is not needed so is set to ""             
            subscreens = [""]
        self.nsubscreens = len(subscreens)
        width = width * self.nsubscreens # normal case
        
        self.canvas = TCanvas(name, name, tx, ty, width *dx, height*dy)
        self.canvas.SetRightMargin(0.)
        self.canvas.SetLeftMargin(0.)
        self.canvas.SetTopMargin(0.) 
        self.canvas.SetBottomMargin(0.) 
        #command to divide the window up into width*height subscreens           
        self.canvas.Divide(width, height)
            
        #manufacture the subscreens
        for x in range(0, self.nsubscreens):
            c1 = self.canvas.cd(x+1)
            c1.SetLeftMargin(0.0015)
            c1.SetRightMargin(0.0015)  
            c1.SetTopMargin(0.0015)  
            c1.SetBottomMargin(0.0015)  
            panename = name + ": " + subscreens[x]
            #create a ViewPad, this is the subscreen on which outputs will be plotted.
            #side is used to index the subscreens
            self.subscreens[x] = ViewPad(panename, name, nx, xmin, xmax, ny, ymin, ymax, side=x)
            
        self.__class__.nviews += 1 
        
    def register(self, obj, layer, clearable=True, sides=None):
        ''' the object will be registered in selected subscreens
            @param obj: thing to be plotted, this will have a draw function. Often will be
                        a ROOT type object such as TGraph, TEllipse etc
            @param layer: what layer in plot to use. Higher layers are plotted **on top- check**
            @param clearable: not sure
            @param sides: if None will send to all subscreens, otherwise side=0 is first/left subscreen
                          side = 1 is second (right) subscreen
        '''        
        if sides is None:
            sides = range(0, len(self.subscreens))
        for x in sides:
            self.subscreens[x].register(obj, layer, clearable)

    def clear(self):
        for p in self.subscreens.itervalues():
            p.clear()
        
    def draw(self):
        '''draw all subscreens
        '''
        for x in range(0, self.nsubscreens):
            if self.canvas is None:
                pass
            else:
                self.canvas.cd(x+1)
                self.subscreens[x].draw()
                self.canvas.Update()

    def zoom(self, xmin, xmax, ymin, ymax):
        '''intended to be called from the command line
            all subscreens are zoomed
        @param xmin: lower left corner x for the zoomed in screen using hist coordinates
        @param xmax: upper right corner x for the zoomed in screen using hist coordinates
        @param ymin: lower left corner y for the zoomed in screen using hist coordinates
        @param ymax: upper right corner y for the zoomed in screen using hist coordinates
        '''
        for p in self.subscreens.itervalues():
            p.zoom(xmin, xmax, ymin, ymax)
        self.draw()    

    def unzoom(self):
        '''intended to be called from the command line
            all subscreens are unzoomed
         '''          
        for p in self.subscreens.itervalues():
            p.unzoom()
        self.draw()   

    def save(self, outdir, filename, filetype):
        '''write the screen to file 
            @param outdir: directory for output files
            @param filename: base of the final filename eg "event_0" would end up with outputs
                             such as "****xy_event_0_simulation****""
            @param filetype: eg png file output. ***what else is supported***
            '''        
        fname = '{outdir}/{name}.{filetype}'.format(outdir=outdir,
                                                    name= filename + self.canvas.GetName(),
                                                    filetype=filetype)
        self.canvas.SaveAs(fname)

  
class ViewPad(object):  
    '''ViewPad is a graphics subscreen, ie a subscreen within a projection window
    '''   
    def __init__(self, name, projection, nx, xmin, xmax, ny, ymin, ymax, side=0):
        '''arguments
        @name  name = title name for the pane
        @param projection = name of the projection (string)
                            eg one of 'xy', 'yz', 'xz' ,'ECAL_thetaphi', 'HCAL_thetaphi'
        @param nx: points on x axis
        @param xmin: lower left corner x for ROOT hists
        @param xmax: upper right corner x for ROOT hists
        @param nx: points on x axis
        @param ymin: lower left corner y for ROOT hists
        @param ymax: upper right corner y for ROOT hists
        @param side: documents which subscreen we are in 0 = main or left, 1 = right
        '''        
        self.side = side
        self.projection = projection
        TH1.AddDirectory(False)
        self.hist = TH2F(name, name, nx, xmin, xmax, ny, ymin, ymax)
        TH1.AddDirectory(True)
        self.hist.Draw()
        self.hist.SetStats(False)
        self.registered = dict()
        self.locked = dict()
 
    def register(self, obj, layer, clearable=True):
        ''' registers an object on a subscreen
            @param obj: thing to be plotted, this will have a draw function. Often will be
                        a ROOT type object such as TGraph, TEllipse etc
            @param layer: what layer in plot to use. Higher layers are plotted **on top- check**
            @param clearable: not sure
        '''    
        self.registered[obj] = layer
        if not clearable:
            self.locked[obj] = layer

    def clear(self):
        self.registered = dict(self.locked.items())
        
    def draw(self):
        '''draw everything in this subscreen
        '''
        for obj, layer in sorted(self.registered.items(),
                                 key=operator.itemgetter(1)):
            obj.draw(self.projection)

    def zoom(self, xmin, xmax, ymin, ymax):
        '''intended to be called from the command line
            subscreen is zoomed
        @param xmin: lower left corner x for the zoomed in screen using hist coordinates
        @param xmax: upper right corner x for the zoomed in screen using hist coordinates
        @param ymin: lower left corner y for the zoomed in screen using hist coordinates
        @param ymax: upper right corner y for the zoomed in screen using hist coordinates
        '''
        self.hist.GetXaxis().SetRangeUser(xmin, xmax)
        self.hist.GetYaxis().SetRangeUser(ymin, ymax)

    def unzoom(self):
        '''intended to be called from the command line
           subscreen is unzoomed
        '''  
        self.hist.GetXaxis().UnZoom()
        self.hist.GetYaxis().UnZoom()
        
     

