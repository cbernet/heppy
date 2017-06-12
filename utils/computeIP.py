import math
from ROOT import TVector3, TLorentzVector
from scipy.optimize import minimize_scalar
from numpy import sign

class straight_line(object):
    """Simple class describing a straight line, based on ROOT TVector3 class.

    Straight line is described by an origin and a direction:
    point = origin + direction * par, where par is a number that parametrizes the line.

    It includes methods to get the point given a certain parameter,
    and to find the minimum approach between the line and an external point.
    """

    def __init__(self, origin, direction):
        """Simple constructor with 2 TVector3 objects, origin and direction
        (which is then normalized)."""
        self.origin = origin
        self.direction = direction.Unit()

    def point_at_parameter(self, par):
        """Returns the point (TVector3 object) at a certain value of the parameter parametrizing the line."""
        return self.origin + par * self.direction

    def distance_from_point(self, point):
        """Given an external point, returns the TVector3 starting from this
        point and going to the line point of closest approach to the external one.

        The result is of the form: w = origin + alpha*direction - point
        """
        alpha = self.direction.Dot( ( point - self.origin ) )
        w =  self.point_at_parameter(alpha) - point
        return w


def velocity_at_time(helix, time):
    """Given a helix object, compute the velocity vector at a given time"""
    v_x = helix.v_over_omega.Y() * math.sin(helix.omega*time) * helix.omega \
        + helix.v_over_omega.X() * math.cos(helix.omega*time) * helix.omega
    v_y = - helix.v_over_omega.X() * math.sin(helix.omega*time) * helix.omega \
        + helix.v_over_omega.Y() * math.cos(helix.omega*time) * helix.omega
    v_z = helix.vz()
    return TVector3(v_x, v_y, v_z)


def compute_IP_wrt_direction(helix, primary_vertex, jet_direction, debug = False):
    """Given a helix object, compute the impact parameter with respect to a given direction, as illustrated in the following note:
    D. Brown, M. Frank, Tagging b hadrons using impact parameters, ALEPH note 92-135.

    primary_vertex and jet_direction must be TVector3 objects.
    The function computes the IP and all the other quantities and store these as attributes of the helix object.

    This version of the impact parameter is more complicated than the common one,
    because it computes firstly the minimum approach between the helix and the jet
    direction, then the track is linearized at this point, and the impact
    parameter is computed as the closest approach between
    the linearized track and the primary vertex.

    debug option prints some important variables while running the code.

    In the code you can find a few comments with the names of the variables
    used in the ALEPH note.
    """
    helix.primary_vertex = primary_vertex    # primary_vertex = v
    helix.jet_direction = jet_direction      # jet_direction = j
    helix.jet_line = straight_line(helix.primary_vertex, helix.jet_direction)

    def jet_track_distance(time):
        helix_point = helix.point_at_time(time)
        jet_track_vector = helix.jet_line.distance_from_point(helix_point)
        return jet_track_vector.Mag()

    helix.min_approach = minimize_scalar(jet_track_distance,
                                        bracket = None,
                                        bounds = [-1e-11, 1e-11],
                                        args=(),
                                        method='bounded',
                                        tol=None,
                                        options={'disp': 0, 'maxiter': 1e5, 'xatol': 1e-20} )
    helix.min_approach_time = helix.min_approach.x

    if debug:
        print
        print "time_min_approach"
        print helix.min_approach_time
        print

    helix.point_min_approach = helix.point_at_time(helix.min_approach_time)          # S_t
    helix.velocity_min_approach = velocity_at_time(helix, helix.min_approach_time)
    helix.linearized_track = straight_line(helix.point_min_approach, helix.velocity_min_approach)

    if debug:
        print "point_min_approach"
        helix.point_min_approach.Dump()
        print
        print "velocity_min_approach"
        helix.velocity_min_approach.Dump()
        print
        print "distance between point min approach and jet dir"
        print jet_track_distance(helix.min_approach_time)
        print

    # S_j
    helix.jet_point_min_approach = helix.point_min_approach \
                                   + helix.jet_line.distance_from_point(helix.point_min_approach)

    if debug:
        print "helix.jet_line.distance_from_point(point_min_approach)"
        helix.jet_line.distance_from_point(point_min_approach).Dump()
        print
        print "jet_point_min_approach"
        jet_point_min_approach.Dump()
        print


    helix.min_dist_to_jet = helix.point_min_approach - helix.jet_point_min_approach    # D_j = S_t - S_j

    # D
    helix.vector_impact_parameter = helix.linearized_track.distance_from_point(helix.primary_vertex)
    helix.s_j_minus_v_wrt_jet_dir = helix.jet_direction.Dot( helix.jet_point_min_approach\
                                                           - helix.primary_vertex )
    helix.sign_impact_parameter = sign( helix.s_j_minus_v_wrt_jet_dir )
    helix.s_j_wrt_pr_vtx = (helix.jet_point_min_approach - helix.primary_vertex).Mag() * helix.sign_impact_parameter
    helix.impact_parameter = helix.vector_impact_parameter.Mag() * helix.sign_impact_parameter

    if debug:
        print "jet_point_min_approach - primary_vertex"
        (jet_point_min_approach - primary_vertex).Dump()
        print
        print "vector_impact_parameter"
        vector_impact_parameter.Dump()
        print


def compute_IP(helix, primary_vertex, jet_direction):
    """ Given a helix object and a primary vertex, compute the impact parameter
    with respect to the primary vertex.

    The impact parameter is the vector of closest approach between the helix and
    the primary vertex. The jet direction is used only to give a sign to the IP.
    Primary vertex and jet direction must be TVector3 objects.

    The function returns the vector IP (pointing from the primary vertex to the
    helix point of closest approach), the sign and the IP (that is the magnitude
    of the vector IP with the proper sign) as attributes of the helix object.
    """
    helix.primary_vertex = primary_vertex
    helix.jet_direction = jet_direction.Unit()

    def pr_vertex_track_distance(time):
        helix_point = helix.point_at_time(time)
        pr_vertex_track_vector = helix_point - helix.primary_vertex
        return pr_vertex_track_vector.Mag()

    helix.min_approach = minimize_scalar(pr_vertex_track_distance,
                                        bracket = None,
                                        bounds = [-1e-11, 1e-11],
                                        args=(),
                                        method='bounded',
                                        tol=None,
                                        options={'disp': 0, 'maxiter': 1e5, 'xatol': 1e-20} )
    helix.min_approach_time = helix.min_approach.x

    helix.vector_impact_parameter = helix.point_at_time(helix.min_approach_time) - helix.primary_vertex
    helix.ip_proj_jet_axis = helix.jet_direction.Dot( helix.vector_impact_parameter )
    helix.sign_impact_parameter = sign( helix.ip_proj_jet_axis )
    helix.impact_parameter = helix.vector_impact_parameter.Mag() * helix.sign_impact_parameter


from ROOT import TCanvas, TGraph, TLine
class vertex_displayer(object):
    """Debug class for displaying vertices, tracks and impact parameters on the transverse plane, based on ROOT classes.
    """

    def __init__(self, name, title, lenght, time_min, time_max, helix, n_points = 100, ip_algorithm = 'complex'):
        """
        Constructor providing:
        name: string used to identify ROOT objects
        title: string used as title of canvases and graphs
        lenght: half of the axis dimension
        time_min and time_max: defining the time interval for which the track is shown
        helix: helix object to be shown; having the ip attributes is mandatory
        n_points: number of points that show the track
        ip_algorithm: if 'complex' it shows also the distance of
        closest approach to the jet direction, and the linearized track at
        that point. It requires to have run the function compute_IP_wrt_direction
        on the helix object.
        """
        self.name = name
        self.title = title
        self.helix = helix
        self.ip_algorithm = ip_algorithm

        self.gr_transverse = TGraph()
        self.gr_transverse.SetNameTitle("g_tr_" + name, title)
        self.gr_transverse.SetPoint(0,0.,0.)
        self.gr_transverse.SetPoint(1,0.,lenght)
        self.gr_transverse.SetPoint(2,0.,-lenght)
        self.gr_transverse.SetPoint(3,lenght,0.)
        self.gr_transverse.SetPoint(4,-lenght,0.)
        self.gr_transverse.SetMarkerStyle(22)
        self.gr_transverse.SetMarkerColor(3)
        self.gr_transverse.GetXaxis().SetTitle("X axis")
        self.gr_transverse.GetYaxis().SetTitle("Y axis")

        # Origin
        self.gr_transverse.SetPoint(5, helix.origin.X(), helix.origin.Y())

        # Track
        self.ell_transverse = TGraph()
        self.ell_transverse.SetNameTitle("g_ellipse_" + name, title)
        self.ell_transverse.SetMarkerStyle(7)
        self.ell_transverse.SetMarkerColor(1)

        for i in range(n_points):
            time_coord = time_min + i*(time_max-time_min)/n_points
            point = helix.point_at_time(time_coord)
            self.ell_transverse.SetPoint(i, point.X(), point.Y())

        # Jet direction
        jet_dir_x1 = self.helix.primary_vertex.X() - lenght * self.helix.jet_direction.X()
        jet_dir_x2 = self.helix.primary_vertex.X() + lenght * self.helix.jet_direction.X()
        jet_dir_y1 = self.helix.primary_vertex.Y() - lenght * self.helix.jet_direction.Y()
        jet_dir_y2 = self.helix.primary_vertex.Y() + lenght * self.helix.jet_direction.Y()

        self.jet_dir = TLine(jet_dir_x1, jet_dir_y1, jet_dir_x2, jet_dir_y2)
        self.jet_dir.SetLineColor(6)
        self.jet_dir.SetLineStyle(1)
        self.jet_dir.SetLineWidth(1)

        # Impact Parameter D
        impact_parameter_x1 = self.helix.primary_vertex.X()
        impact_parameter_y1 = self.helix.primary_vertex.Y()
        impact_parameter_x2 = self.helix.vector_impact_parameter.X()
        impact_parameter_y2 = self.helix.vector_impact_parameter.Y()

        self.impact_parameter = TLine(impact_parameter_x1,
                                      impact_parameter_y1,
                                      impact_parameter_x2,
                                      impact_parameter_y2)
        self.impact_parameter.SetLineColor(4)
        self.impact_parameter.SetLineStyle(6)
        self.impact_parameter.SetLineWidth(4)

        if self.ip_algorithm == 'complex':
            # Linearized_track
            lin_track_x1 = self.helix.linearized_track.origin.X() \
                         - lenght * self.helix.linearized_track.direction.X()
            lin_track_x2 = self.helix.linearized_track.origin.X() \
                         + lenght * self.helix.linearized_track.direction.X()
            lin_track_y1 = self.helix.linearized_track.origin.Y() \
                         - lenght * self.helix.linearized_track.direction.Y()
            lin_track_y2 = self.helix.linearized_track.origin.Y() \
                         + lenght * self.helix.linearized_track.direction.Y()

            self.lin_track = TLine(lin_track_x1,
                                   lin_track_y1,
                                   lin_track_x2,
                                   lin_track_y2)
            self.lin_track.SetLineColor(2)
            self.lin_track.SetLineStyle(9)
            self.lin_track.SetLineWidth(2)

            # Jet-track distance D_j: vector from S_j to S_t
            jet_track_distance_x1 = self.helix.jet_point_min_approach.X()
            jet_track_distance_y1 = self.helix.jet_point_min_approach.Y()
            jet_track_distance_x2 = self.helix.point_min_approach.X()
            jet_track_distance_y2 = self.helix.point_min_approach.Y()

            self.jet_track_distance = TLine(jet_track_distance_x1,
                                            jet_track_distance_y1,
                                            jet_track_distance_x2,
                                            jet_track_distance_y2)
            self.jet_track_distance.SetLineColor(3)
            self.jet_track_distance.SetLineStyle(3)
            self.jet_track_distance.SetLineWidth(4)

    def draw(self):
        """Draw the canvas showing the transverse plane to the beam axis.

        In particular it shows the x-y axis, the track, the jet direction and
        the impact parameter.
        If the ip_algorithm 'complex' is enabled it also shows the distance of
        closest approach to the jet direction, and the linearized track at
        that point.
        """
        self.c_transverse = TCanvas("c_tr_" + self.name, self.title, 800, 600)
        self.c_transverse.cd()
        self.c_transverse.SetGrid()
        self.gr_transverse.Draw("AP")
        self.ell_transverse.Draw("same LP")
        self.jet_dir.Draw("same")
        self.impact_parameter.Draw("same")

        if self.ip_algorithm == 'complex':
            self.lin_track.Draw("same")
            self.jet_track_distance.Draw("same")
