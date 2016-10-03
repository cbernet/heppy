from ROOT import TCanvas, TH1, TH2F
import operator
import math
import os
from heppy.papas.pfobjects import Cluster

class Display(object):
    
    def __init__(self, views=None):
        ViewPane.nviews = 0
        if not views:
            views = ['xy', 'yz', 'xz']
        self.views = dict()
        for view in views:
            if view in ['xy', 'yz', 'xz']:
                self.views[view] = ViewPane(view, view,
                                            100, -4, 4, 100, -4, 4)
            elif 'thetaphi' in view:
                self.views[view] = ViewPane(view, view,
                                            100, -math.pi/2, math.pi/2,
                                            100, -math.pi, math.pi,
                                            500, 1000)

    def register(self, obj, layer, clearable=True):
        elems = [obj]
        if hasattr(obj, '__iter__'):
            elems = obj
        for elem in elems: 
            for view in self.views.values():
                view.register(elem, layer, clearable)

    def clear(self):
        for view in self.views.values():
            view.clear()

    def zoom(self, xmin, xmax, ymin, ymax):
        for view in self.views.values():
            view.zoom(xmin, xmax, ymin, ymax)

    def unzoom(self):
        for view in self.views.values():
            view.unzoom()
            
    def draw(self):
        for view in self.views.values():
            view.draw()

    def save(self, outdir, filetype='png'):
        os.mkdir(outdir)
        for view in self.views.values():
            view.save(outdir, filetype)
        

class ViewPane(object):
    nviews = 0
    def __init__(self, name, projection, nx, xmin, xmax, ny, ymin, ymax,
                 dx=600, dy=600,pads = [""]):
        self.projection = projection
        self.hists = dict()
        self.registered = dict() 
        self.locked = dict()
        tx = 50 + self.__class__.nviews * (dx+10) 
        ty = 50
        width = dx
        self.npads =1 
        self.pads = dict()
        if not pads is None:
            self.npads = len(pads)
            width = width * len(pads)
            
        self.canvas = TCanvas(name, name, tx, ty, width, dy)
        self.canvas.Divide(self.npads,1)
            
        for x in range(0, self.npads):
            self.canvas.cd(x+1)
            panename = name + ": " + pads[x]
            self.pads[x] = ViewPad(panename, name, nx, xmin, xmax, ny, ymin, ymax, side = x)
                                                                
            
        self.__class__.nviews += 1 
        
    def register(self, obj, layer, clearable=True, sides = None):
        if sides is None:
            sides = range(0, len(self.pads))
        
        for x in sides:
            self.pads[x].register(obj, layer, clearable)

    def clear(self):
        for p in self.pads.itervalues():
            p.clear()
        
    def draw(self):
        for x in range(0, self.npads):
            self.canvas.cd(x+1)
            self.pads[x].draw()
        self.canvas.Update()

    #def zoom(self, xmin, xmax, ymin, ymax):
        #self.hist.GetXaxis().SetRangeUser(xmin, xmax)
        #self.hist.GetYaxis().SetRangeUser(ymin, ymax)
        #self.canvas.Update()

    #def unzoom(self):
        #self.hist.GetXaxis().UnZoom()
        #self.hist.GetYaxis().UnZoom()
        #self.canvas.Modified()
        #self.canvas.Update()

    def save(self, outdir, filetype):
        fname = '{outdir}/{name}.{filetype}'.format(outdir=outdir,
                                                    name=self.canvas.GetName(),
                                                    filetype=filetype)
        self.canvas.SaveAs(fname)
        
        
        
class ViewPad(object):
    
    def __init__(self, name, projection, nx, xmin, xmax, ny, ymin, ymax,
                 dx=600, dy=600, side = 0):
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
        self.registered[obj] = layer
        if not clearable:
            self.locked[obj] = layer
        #TODO might need to keep track of views in objects

    def clear(self):
        
        self.registered = dict(self.locked.items())
        
    def draw(self):
        for obj, layer in sorted(self.registered.items(),
                                 key = operator.itemgetter(1)):
            obj.draw(self.projection)
        

    #def zoom(self, xmin, xmax, ymin, ymax):
        #self.hist.GetXaxis().SetRangeUser(xmin, xmax)
        #self.hist.GetYaxis().SetRangeUser(ymin, ymax)
        #self.canvas.Update()

    #def unzoom(self):
        #self.hist.GetXaxis().UnZoom()
        #self.hist.GetYaxis().UnZoom()
        #self.canvas.Modified()
        #self.canvas.Update()

    
        
class DoubleDisplay(object):
    
    def __init__(self, views=None, pads = None):
        ViewPane.nviews = 0
        if not views:
            views = ['xy', 'yz', 'xz']
        self.views = dict()
        self.pads = pads
        for view in views:
            if view in ['xy', 'yz', 'xz']:
                self.views[view] = ViewPane(view, view,100, -4, 4, 100, -4, 4, pads = pads)
            elif 'thetaphi' in view:
                self.views[view] = ViewPane(view, view,
                                            100, -math.pi/2, math.pi/2,
                                            100, -math.pi, math.pi,
                                            500, 1000, pads = pads)

    def register(self, obj, layer, clearable=True, sides = None ):
        if sides is None:
            sides = range(0, len(self.pads))
        elems = [obj]
        if hasattr(obj, '__iter__'):
            elems = obj
        for elem in elems: 
            for view in self.views.values():
                for x in sides:
                    view.register(elem, layer, clearable, [x])

    def clear(self):
        for view in self.views.values():
            view.clear()

    def zoom(self, xmin, xmax, ymin, ymax):
        for view in self.views.values():
            view.zoom(xmin, xmax, ymin, ymax)

    def unzoom(self):
        for view in self.views.values():
            view.unzoom()
            
    def draw(self):
        for view in self.views.values():
            view.draw()

    def save(self, outdir, filetype='png'):
        os.mkdir(outdir)
        for view in self.views.values():
            view.save(outdir, filetype)
        

    