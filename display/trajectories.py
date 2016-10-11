from ROOT import TPolyLine, TGraph, TArc, TEllipse, kGray
import numpy as np
import operator
import math
from heppy.papas.path import Helix, StraightLine, Info
from pfobjects import Blob

class GTrajectories(list):
    
    def __init__(self, particles):
        for ptc in particles:
            is_neutral = abs(ptc.q())<0.5
            TrajClass = GStraightTrajectory if is_neutral else GHelixTrajectory
            gtraj = TrajClass(ptc)
            self.append(gtraj)
            # display.register(gtraj,1)

    def draw(self, projection):
        for traj in self:
            traj.draw(projection)
            

class GTrajectory(object):

    draw_smeared_clusters = True
    
    def __init__(self, detector, particle, ecals = dict(), hcals = dict(),linestyle=1, linecolor=1, grey = False):
   
        #npoints=0
        self.points = []
        self.path = particle.path
        print len(particle.path.points)
        if len(particle.path.points) >1 : #use the points in the path if they are present
            self.points=particle.path.points.values()
        else: #reconstructed particle             
            npoints =  6
            if len(hcals):
                npoints = 6
            elif len(ecals) or particle.pdgid() == 22:
                    npoints = 3
            elif abs(particle.pdgid()) in [11,13]:
                    npoints = 7  
            for i in range(npoints):
                position=self.path.position(detector.cylinders()[i])
                if position!=None:
                    self.points.append(position)
        
        npoints= len(self.points)
        self.graph_xy = TGraph(npoints)
        self.graph_yz = TGraph(npoints)
        self.graph_xz = TGraph(npoints)
        self.graph_thetaphi = TGraph(npoints)
        self.graphs = [self.graph_xy, self.graph_yz, self.graph_xz, self.graph_thetaphi]
        
        if grey:
            linecolor=17
            
        def set_graph_style(graph):
            graph.SetMarkerStyle(2)
            graph.SetMarkerSize(0.7)
            graph.SetMarkerColor(linecolor)
            graph.SetLineStyle(linestyle)
            graph.SetLineColor(linecolor)
            
        for g in self.graphs:
            set_graph_style(g)
        
        
        
        for i, position in enumerate(self.points):
            #self.graph_xy.SetPointColor(linecolor)            
            #self.graph_xy.SetLineColor(linecolor)
            self.graph_xy.SetPoint( i, position.X(), position.Y() )
            self.graph_yz.SetPoint( i, position.Z(), position.Y() )
            self.graph_xz.SetPoint( i, position.Z(), position.X() )
            #self.graph_xy.SetPointColor(linecolor)
            
            tppoint = position
            if i == 0:
                tppoint = particle.p4().Vect()
            self.graph_thetaphi.SetPoint(i, math.pi/2. - tppoint.Theta(), tppoint.Phi() )
            #i= 1+i
        self.blobs = map(Blob, ecals.values() + hcals.values(), [grey]*len(ecals.values() + hcals.values()))            

    def set_color(self, color):
        for graph in self.graphs:
            graph.SetMarkerColor(color)
        
    def draw(self, projection, opt=''):
        for blob in self.blobs: 
            blob.draw(projection, opt)
        if projection == 'xy':
            self.graph_xy.Draw(opt+"psame")
        elif projection == 'yz':
            self.graph_yz.Draw(opt+"psame")
        elif projection == 'xz':
            self.graph_xz.Draw(opt+"psame")
        elif 'thetaphi' in projection:
            self.graph_thetaphi.Draw(opt+"psame")            
        else:
            raise ValueError('implement drawing for projection ' + projection )

            
class GStraightTrajectory(GTrajectory):
    def __init__(self,  detector, particle, ecals =dict(), hcals = dict(), grey=False):
        super(GStraightTrajectory, self).__init__( detector, particle, ecals, hcals,
                                                  linestyle=2, linecolor=1, grey= grey)

    def draw(self, projection):
        super(GStraightTrajectory, self).draw(projection, 'l')
   

class GHelixTrajectory(GTrajectory):    
    def __init__(self, detector, particle, ecals = dict(), hcals= dict(),linestyle=1, linecolor=1, grey=False):
        super(GHelixTrajectory, self).__init__( detector, particle, ecals, hcals, linestyle, linecolor, grey=grey)
        last_cylinder=6  
        max_time = 0 
        if hasattr(particle, "path"):
            helix = self.path
            max_time = helix.time_at_z(self.points[-1].Z())
            
        else: #reconstructed particle
            helix = self.path

            #TODO this is patchy,need to access the last point, whatever its name
            
            last_cylinder=6
            if len(hcals):
                last_cylinder=6
            elif len(ecals):
                last_cylinder=3
            if abs(particle.pdgid()) in [11,13]:
                last_cylinder=8
            
            position=helix.position(detector.cylinders()[last_cylinder-1])
            max_time = helix.time_at_z(position.Z())
            
        if grey:
            linecolor =17
        self.helix_xy = TArc(helix.center_xy.X(),
                     helix.center_xy.Y(),
                     helix.rho, helix.phi_min, helix.phi_max)
        self.helix_xy.SetFillStyle(0)
        npoints = 100
        self.graphline_xy = TGraph(npoints)
        self.graphline_yz = TGraph(npoints)
        self.graphline_xz = TGraph(npoints)
        self.graphline_thetaphi = TGraph(npoints)
        self.graphline_xy.SetLineColor(linecolor)
        self.graphline_yz.SetLineColor(linecolor)
        self.graphline_xz.SetLineColor(linecolor) 
        self.graphline_xy.SetMarkerColor(linecolor)
        self.graphline_yz.SetMarkerColor(linecolor)
        self.graphline_xz.SetMarkerColor(linecolor) 
        
        
        for i, time in enumerate(np.linspace(0, max_time, npoints)):
            point = helix.point_at_time(time)
            self.graphline_xy.SetPoint(i, point.X(), point.Y())
            self.graphline_yz.SetPoint(i, point.Z(), point.Y())
            self.graphline_xz.SetPoint(i, point.Z(), point.X())
            tppoint = point
            if i == 0:
                tppoint = particle.p4().Vect()
            self.graphline_thetaphi.SetPoint(i, math.pi/2.-tppoint.Theta(), tppoint.Phi())
        if abs(particle.pdgid()) in [11,13]:
            def set_graph_style(graph):
                graph.SetLineWidth(3)
                graph.SetLineColor(5)
            set_graph_style(self.graphline_xy)
            set_graph_style(self.graphline_xz)
            set_graph_style(self.graphline_yz)
            set_graph_style(self.graphline_thetaphi)


    def draw(self, projection):
        if projection == 'xy':
            # self.helix_xy.Draw("onlysame")
            self.graphline_xy.Draw("lsame")
        elif projection == 'yz':
            self.graphline_yz.Draw("lsame")
        elif projection == 'xz':
            self.graphline_xz.Draw("lsame")
        elif 'thetaphi' in projection:
            self.graphline_thetaphi.Draw("lsame")            
        else:
            raise ValueError('implement drawing for projection ' + projection )
        super(GHelixTrajectory, self).draw(projection) 


class GHistoryBlock(list):
    
    def __init__(self, particles, ecals, hcals, detector, is_grey=False):
        first = True
        for ptc in particles.values():
            is_neutral = abs(ptc.q())<0.5
            TrajClass = GStraightTrajectory if is_neutral else GHelixTrajectory     
            if first:
                first = False
                gtraj = TrajClass(detector, ptc, ecals, hcals,grey=is_grey)
            else:
                gtraj = TrajClass(detector, ptc,grey=is_grey)
            self.append(gtraj)  
