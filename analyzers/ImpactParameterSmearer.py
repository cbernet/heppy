from heppy.framework.analyzer import Analyzer
from heppy.papas.path import ImpactParameter
from ROOT import TVector3, TLorentzVector, TFile, TTree
# from heppy.papas.path import Helix
import math
import random
# from heppy.utils.computeIP import *

class ImpactParameterSmearer(Analyzer):
    """Smears impact parameter of tracks in jets
    
    Example:
     def aleph_resolution(ptc):
       momentum = ptc.p3().Mag()
       return math.sqrt(25.**2 + 95.**2/ (momentum**2) )*1e-6

     smearer = cfg.Analyzer(
       ImpactParameterSmearer,
       jets = 'jets',
       resolution = aleph_resolution,
     )
    """

    def process(self, event):
        primary_vertex = TVector3(0, 0, 0)
        jets = getattr(event, self.cfg_ana.jets)
        for jet in jets:
            for ptcs in jet.constituents.values():
                for ptc in ptcs:
                    if ptc.q() == 0:
                        continue
                    ptc.path.impact_parameter = ImpactParameter(ptc.path,
                                                                primary_vertex,
                                                                jet.p3())
                    resolution = self.cfg_ana.resolution(ptc)
                    ptc.path.IP_resolution = resolution
                    gx = random.gauss(0, ptc.path.IP_resolution)
                    gy = random.gauss(0, ptc.path.IP_resolution)
                    smear_IP(ptc.path, gx, gy)


def smear_IP(path, gx, gy):
    """Given a particle, smear the IP and compute the track significance
    and the probability that the track comes from the primary vertex.

    The smearing is made with a gaussian variable with mean = 0 and sigma = resolution;
    in addition the smearing is applied to the x' and y' component of the IP,
    that are the component in a frame in which the vector IP lies on the x'y' plane.
    """
    # resolution = self.cfg_ana.resolution(ptc)
    # ptc.path.ip_resolution = resolution
    
    #COLIN->NIC: is this just taking the X and Y component?
    ipvector = path.impact_parameter.vector
    path.x_prime = ipvector.Mag()*math.cos(ipvector.Phi())
    path.y_prime = ipvector.Mag()*math.sin(ipvector.Phi())
    path.z_prime = 0
    
    #COLIN->NIC: is the goal to just do path.vector_impact_parameter.Perp()? why is that called "rotated?"
    path.vector_ip_rotated = TVector3(path.x_prime, path.y_prime, path.z_prime)

    #COLIN->NIC: shouldn't smearing be done on the magnitude of the impact parameter vector?
    #in other words, I think that smearing should be correlated on the x and y components. 
    #COLIN: the resolution should be in the same units as the impact parameter vector (meters?)
    path.x_prime_smeared = path.x_prime + gx
    path.y_prime_smeared = path.y_prime + gy
    path.z_prime_smeared = 0
    path.vector_ip_rotated_smeared = TVector3(path.x_prime_smeared,
                                              path.y_prime_smeared,
                                              path.z_prime_smeared)
    #COLIN->NIC It looks like we are keeping the sign of the impact parameter before smearing. Why?
    # I think that smearing should be able to change the sign. 
    path.smeared_impact_parameter = path.vector_ip_rotated_smeared.Mag() * path.impact_parameter.sign
    path.significance_impact_parameter = path.smeared_impact_parameter / path.IP_resolution
    #COLIN track probability is about tagging, not impact parameter smearing. do that in a separate JetTag analyzer
    # path.track_probability = self.track_probability(ptc)

    

##    def track_probability(self, particle):
##        """Compute the probability that the track comes from the primary vertex according to the resolution.
##
##        The track probability is computed as the p-value of the track significance with respect to the expected distribution produced only by the effect of the resoution.
##        For a gaussian resolution, like in this case, this takes an easy expression.
##
##        If the track has negative significance, the probability as it had positive significance is assigned, but with the negative sign.
##        """
##        #COLIN->NIC: is this method used? 
##        def gaussian(x):
##            return math.exp((-0.5)*x**2)
##        #COLIN->NIC: this does not look like a p-value to me.
##        #The pvalue would be the integral of the gaussian starting from significance_impact_parameter to infinity.  
##        track_prob = gaussian(particle.path.significance_impact_parameter)
##        if particle.path.significance_impact_parameter < 0:
##            #COLIN->NIC check how these guys are used later on. I do not think
##            # these negative probabilities should be used to lower the jet b probability
##            # possibly return None instead?
##            return (-1)*track_prob
##        else:
##            return track_prob

##    def jet_tag(self, jet):
##        """Combine all the track probabilities for tracks with positive significance passing the track selection to obtain the probability that the jet comes from the primary vertex.
##
##        Jet tags are stored as attributes of the jet object.
##        In particular these new attributes are added:
##        - btag: proability that the jet comes from the primary vertex
##        - logbtag: -log(btag), to better see the difference between jets with very small btag
##        - log10btag: log_10(btag), it's easier to compare with other works if you use this variable
##
##        If a jet doesn't contain any track with positive significance, btag = 1 is assigned.
##        """
##        logtag = 0.
##        n_track = 0
##        log_prob_product = 0.
##
##        for id, ptcs in jet.constituents.iteritems():
##            for ptc in ptcs :
##                if self.cfg_ana.track_selection(ptc) == True and \
##                   ptc.path.significance_impact_parameter > 0:
##                    n_track += 1
##                    log_prob_product += 0.5 * ptc.path.significance_impact_parameter**2
##
##        if n_track == 0:
##            jet.btag = 1.
##            jet.logbtag = 0.
##            jet.log10btag = 0.
##            jet.tags['b_pvprob'] = 1
##        else:
##            sum_tr = 0
##            for j in range(n_track):
##                sum_tr += (log_prob_product)**j/math.factorial(j)
##
##            logtag = log_prob_product - math.log(sum_tr)
##            pvprob = math.exp(-logtag)
##            jet.btag = pvprob
##            jet.tags['b_pvprob'] = pvprob 
##            jet.logbtag = logtag
##            jet.log10btag = - logtag * math.log10(math.exp(1))
##        #COLIN hack to define working point, necessary for integration
##        #should have a flag in the cfg for the working point.
##        jet.tags['b_ip'] = jet.tags['b_pvprob'] < 1e-2
##
##        
##    def jet_attributes(self, jet, significance, sign):
##        """Given a jet, compute the multiplicity, invariant mass and angle of the tracks with signficance larger or smaller than a given value, passing the track selection.
##
##        If sign is positive (negative) only the track with significance larger (smaller) than the given value of significance are taken into account. If sign is 0 all the tracks are considered.
##
##        If no track inside the jet passes this selection, it returns 0, 0, 0.
##        """
##        track_list = []
##
##        for id, ptcs in jet.constituents.iteritems():
##            for ptc in ptcs :
##                if self.cfg_ana.track_selection(ptc) == True:
##                    if sign > 0:
##                        if ptc.path.significance_impact_parameter > significance:
##                            track_list.append(ptc)
##                    elif sign < 0:
##                        if ptc.path.significance_impact_parameter < significance:
##                            track_list.append(ptc)
##                    elif sign == 0:
##                        track_list.append(ptc)
##
##        totalp4 = reduce(lambda total, particle: total + particle.p4(),
##                         track_list, TLorentzVector(0., 0., 0., 0.))
##        angle_totalp4_wrt_jet = totalp4.Angle(jet.p3())
##
##        return len(track_list), totalp4.M(), angle_totalp4_wrt_jet

##    def beginLoop(self, setup):
##
##        super(ImpactParameterSmearer, self).beginLoop(setup)
##
##        if hasattr(self.cfg_ana, 'mva_bg_tree'):
##            my_file = TFile(self.cfg_ana.mva_filename, "OPEN")
##            my_tree = my_file.Get(self.cfg_ana.mva_treename)
##            mva_variables = ["jet_logbtag",
##                             "jet_n_signif_larger3",
##                             "jet_m_inv_signif_larger3",
##                             "jet_angle_wrt_jet_dir_larger3"]
##
##            self.b_tag_mva = ComputeMVA(mva_variables,
##                                        my_tree.CopyTree(self.cfg_ana.mva_background_selection),
##                                        my_tree.CopyTree(self.cfg_ana.mva_signal_selection)
##                                        )
##
