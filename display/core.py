from ROOT import TCanvas, TH1, TH2F
import operator
import math
import os


'''Display class
Main class to produce ROOT plots of the detector and display clusters, trajectories etc

Example usage
    self.display = Display(["xy", "yz"], subscreens=["simulated", "reconstructed"])
    self.display.register(self.gdetector, layer=0, clearable=False)
    ... (add clusters tracks lines etc)
    self.display.draw()

'''

class Display(object):

    def __init__(self, projections=None, subscreens=None):
        '''projections: list of projections eg ['xy', 'yz', 'xz'] these will be separate windows
           subscreens: list of names of panels within each window eg subscreens=["simulated", "reconstructed"]
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
                self.views[view] = ViewPane(view, view, 100, -2.8, 2.8, 100, -2.8, 2.8, subscreens=subscreens)
            elif 'thetaphi' in view:
                self.views[view] = ViewPane(view, view,
                                            100, -math.pi/2, math.pi/2,
                                            100, -math.pi, math.pi,
                                            500, 1000, subscreens=subscreens)

    def register(self, obj, layer, clearable=True, sides=None):
        '''add in an object such as a cluster or trajectory
           the object will be registered in every projection and subscreen
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

    def save(self, outdir, filetype='png'):
        '''write the plot to a png file (one file per projection)'''
        os.mkdir(outdir)
        for view in self.views.values():
            view.save(outdir, filetype)

class ViewPane(object): #a graphics window
    nviews = 0
    def __init__(self, name, projection, nx, xmin, xmax, ny, ymin, ymax,
                 dx=600, dy=600, subscreens=None):
        '''arguments
        projection = name of the projection (string)
        nx, xmin, xmax, ny,ymin, ymax = the axis specification for the ROOT hists
        dx dy = size of each subscreen (pixels?)
        subscreens = list of names of the subscreens
        '''
        self.projection = projection
        self.hists = dict()
        self.registered = dict()
        self.locked = dict()
        tx = 50 + self.__class__.nviews * (dx+10)
        ty = 50
        width = 1
        height = 1
        self.nsubscreens = 1
        self.subscreens = dict()
 
        #decide how to subdivide the window for the subscreens       
        #normally split screen into horizontally side by side
        if subscreens is None:
            #The projection name and the subscreen name get concatenated. eg "xy: simulated",
            #when there is only one subscreen the subscreen string is not needed so is set to ""             
            subscreens = [""]
        self.nsubscreens = len(subscreens)
        width = width * self.nsubscreens # normal case
        #experimental case for large number of small subscreens
        if self.nsubscreens%8 == 0 and self.nsubscreens >= 8: 
            # make the sceen be 4 subscreens wide, and halve the size of each subscreen                
            width = width*4
            height = height *self.nsubscreens/4
            dx = dx/2
            dy = dy/2
            xmax = 2
            ymin = -xmax
            xmin = -xmax
            ymax = xmax

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
        #register this object on all the subscreens for this projection
        if sides is None:
            sides = range(0, len(self.subscreens))
        for x in sides:
            self.subscreens[x].register(obj, layer, clearable)

    def clear(self):
        for p in self.subscreens.itervalues():
            p.clear()
        
    def draw(self):
        #draw all the subcreens for this projection window
        for x in range(0, self.nsubscreens):
            if self.canvas is None:
                pass
            else:
                self.canvas.cd(x+1)
                self.subscreens[x].draw()
                self.canvas.Update()

    def zoom(self, xmin, xmax, ymin, ymax):
        #all the subscreens are zoomed at once
        for p in self.subscreens.itervalues():
            p.zoom(xmin, xmax, ymin, ymax)
        self.draw()    

    def unzoom(self):
        for p in self.subscreens.itervalues():
            p.unzoom()
        self.draw()   

    def save(self, outdir, filetype):
        fname = '{outdir}/{name}.{filetype}'.format(outdir=outdir,
                                                    name=self.canvas.GetName(),
                                                    filetype=filetype)
        self.canvas.SaveAs(fname)

  
class ViewPad(object):  #a graphics subscreen (within a window)
    
    def __init__(self, name, projection, nx, xmin, xmax, ny, ymin, ymax, side=0):
        #side is the index saying which subscreen we are plotting to
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
        #adds an object that will be plotted
        self.registered[obj] = layer
        if not clearable:
            self.locked[obj] = layer

    def clear(self):
        self.registered = dict(self.locked.items())
        
    def draw(self):
        #draw everything in this subscreen
        for obj, layer in sorted(self.registered.items(),
                                 key=operator.itemgetter(1)):
            obj.draw(self.projection)

    def zoom(self, xmin, xmax, ymin, ymax):
        #zoom a subscreen
        self.hist.GetXaxis().SetRangeUser(xmin, xmax)
        self.hist.GetYaxis().SetRangeUser(ymin, ymax)

    def unzoom(self):
        #unzoom a subscreen
        self.hist.GetXaxis().UnZoom()
        self.hist.GetYaxis().UnZoom()
        
     

