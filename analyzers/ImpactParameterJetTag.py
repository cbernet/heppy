from heppy.framework.analyzer import Analyzer
from ROOT import TVector3, TLorentzVector, TFile, TTree
from heppy.papas.path import Helix
import math
import random
from heppy.utils.computeIP import *
# from heppy.utils.ComputeMVA import ComputeMVA

class ImpactParameterJetTag(Analyzer):
    """Compute impact paramaters for every charged track and combine them to obtain b-tag variables for every jet inside the event.

    The analyzer requires a resolution function for the impact parameter and a track selection function.

    In particular the analyzer does these steps:
    - loop on every charged track
        - compute the IP in the simple way
        - apply a smearing on the IP according to the resolution
        - compute track significance and track probability
    - for each jet select the tracks according to the selection function and compute
        - b tag variable, that is the probability that the jet comes from the primary vertex
        - multiplicity, invariant mass and angle wrt to jet direction for the tracks with significance larger than 3 (it's an approximation of the secondary vertex variables)

    Every variable is stored as an attribute of the corresponding object.

    Here is an example to use the code inside the configuration file.

    def track_selection_function(track):
        return track.q() != 0 and \
        abs(track.path.smeared_impact_parameter) < 2.5e-3 and \
        track.path.ip_resolution < 7.5e-4 and \
        track.e() > 0.4

    import math
    def aleph_resolution(ptc):
        momentum = ptc.p3().Mag()
        return math.sqrt(25.**2 + 95.**2/ (momentum**2) )*1e-6

    from heppy.analyzers.ImpactParameterJetTag import ImpactParameterJetTag
    ip_wrt_jet_dir = cfg.Analyzer(
        ImpactParameterJetTag,
        jets = 'jets',
        method = 'simple',
        track_selection = track_selection_function,
        resolution = aleph_resolution,
        #mva attributes, not mandatory
        mva_filename = '../02_b_tagging/18_without_beampipe_simple_ILD/ntuple/qq_ILD_spIP/analyzers.ZqqIPJetsTreeProducer.ZqqIPJetsTreeProducer_1/tree.root',
        mva_treename = 'events',
        mva_background_selection = 'quark_type <= 4',
        mva_signal_selection = 'quark_type == 5',
    )

    TODO: Fix implementation with MVA
    """

    def smearing_significance_IP(self, ptc):
        """Given a particle, smear the IP and compute the track significance and the probability that the track comes from the primary vertex.

        The smearing is made with a gaussian variable with mean = 0 and sigma = resolution; in addition the smearing is applied to the x' and y' component of the IP, that are the component in a frame in which the vector IP lies on the x'y' plane.
        """
        resolution = self.cfg_ana.resolution(ptc)
        ptc.path.ip_resolution = resolution

        ptc.path.x_prime = ptc.path.vector_impact_parameter.Mag()*math.cos(ptc.path.vector_impact_parameter.Phi())
        ptc.path.y_prime = ptc.path.vector_impact_parameter.Mag()*math.sin(ptc.path.vector_impact_parameter.Phi())
        ptc.path.z_prime = 0
        ptc.path.vector_ip_rotated = TVector3(ptc.path.x_prime, ptc.path.y_prime, ptc.path.z_prime)

        ptc.path.ip_smear_factor_x = random.gauss(0, ptc.path.ip_resolution)
        ptc.path.ip_smear_factor_y = random.gauss(0, ptc.path.ip_resolution)
        ptc.path.x_prime_smeared = ptc.path.x_prime + ptc.path.ip_smear_factor_x
        ptc.path.y_prime_smeared = ptc.path.y_prime + ptc.path.ip_smear_factor_y
        ptc.path.z_prime_smeared = 0
        ptc.path.vector_ip_rotated_smeared = TVector3(ptc.path.x_prime_smeared, ptc.path.y_prime_smeared, ptc.path.z_prime_smeared)

        ptc.path.smeared_impact_parameter = ptc.path.vector_ip_rotated_smeared.Mag() * ptc.path.sign_impact_parameter
        ptc.path.significance_impact_parameter = ptc.path.smeared_impact_parameter / ptc.path.ip_resolution
        ptc.path.track_probability = self.track_probability(ptc)

        if self.cfg_ana.method == 'complex':
            ptc.path.min_dist_to_jet_significance = ptc.path.sign_impact_parameter\
                                                    * ptc.path.min_dist_to_jet.Mag()\
                                                    / ptc.path.ip_resolution

    def track_probability(self, particle):
        """Compute the probability that the track comes from the primary vertex according to the resolution.

        The track probability is computed as the p-value of the track significance with respect to the expected distribution produced only by the effect of the resoution. For a gaussian resolution, like in this case, this takes an easy expression.

        If the track has negative significance, the probability as it had positive significance is assigned, but with the negative sign.
        """
        def gaussian(x):
            return math.exp((-0.5)*x**2)

        track_prob = gaussian(particle.path.significance_impact_parameter)
        if particle.path.significance_impact_parameter < 0:
            return (-1)*track_prob
        else:
            return track_prob

    def jet_tag(self, jet):
        """Combine all the track probabilities for tracks with positive significance passing the track selection to obtain the probability that the jet comes from the primary vertex.

        Jet tags are stored as attributes of the jet object.
        In particular these new attributes are added:
        - btag: proability that the jet comes from the primary vertex
        - logbtag: -log(btag), to better see the difference between jets with very small btag
        - log10btag: log_10(btag), it's easier to compare with other works if you use this variable

        If a jet doesn't contain any track with positive significance, btag = 1 is assigned.
        """
        logtag = 0.
        n_track = 0
        log_prob_product = 0.

        for id, ptcs in jet.constituents.iteritems():
            for ptc in ptcs :
                if self.cfg_ana.track_selection(ptc) == True and \
                ptc.path.significance_impact_parameter > 0:
                    n_track += 1
                    log_prob_product += 0.5 * ptc.path.significance_impact_parameter**2

        if n_track == 0:
            jet.btag = 1.
            jet.logbtag = 0.
            jet.log10btag = 0.
            jet.tags['b_pvprob'] = 1
        else:
            sum_tr = 0
            for j in range(n_track):
                sum_tr += (log_prob_product)**j/math.factorial(j)

            logtag = log_prob_product - math.log(sum_tr)
            pvprob = math.exp(-logtag)
            jet.btag = pvprob
            jet.tags['b_pvprob'] = pvprob 
            jet.logbtag = logtag
            jet.log10btag = - logtag * math.log10(math.exp(1))
        #COLIN hack define working point for integration
        jet.tags['b'] = jet.tags['b_pvprob'] < 1e-2

    def jet_attributes(self, jet, significance, sign):
        """Given a jet, compute the multiplicity, invariant mass and angle of the tracks with signficance larger or smaller than a given value, passing the track selection.

        If sign is positive (negative) only the track with significance larger (smaller) than the given value of significance are taken into account. If sign is 0 all the tracks are considered.

        If no track inside the jet passes this selection, it returns 0, 0, 0.
        """
        track_list = []

        for id, ptcs in jet.constituents.iteritems():
            for ptc in ptcs :
                if self.cfg_ana.track_selection(ptc) == True:
                    if sign > 0:
                        if ptc.path.significance_impact_parameter > significance:
                            track_list.append(ptc)
                    elif sign < 0:
                        if ptc.path.significance_impact_parameter < significance:
                            track_list.append(ptc)
                    elif sign == 0:
                        track_list.append(ptc)

        totalp4 = reduce(lambda total, particle: total + particle.p4(),
                         track_list, TLorentzVector(0., 0., 0., 0.))
        angle_totalp4_wrt_jet = totalp4.Angle(jet.p3())

        return len(track_list), totalp4.M(), angle_totalp4_wrt_jet

    def beginLoop(self, setup):

        super(ImpactParameterJetTag, self).beginLoop(setup)

        if hasattr(self.cfg_ana, 'mva_bg_tree'):
            my_file = TFile(self.cfg_ana.mva_filename, "OPEN")
            my_tree = my_file.Get(self.cfg_ana.mva_treename)
            mva_variables = ["jet_logbtag",
                             "jet_n_signif_larger3",
                             "jet_m_inv_signif_larger3",
                             "jet_angle_wrt_jet_dir_larger3"]

            self.b_tag_mva = ComputeMVA(mva_variables,
                                        my_tree.CopyTree(self.cfg_ana.mva_background_selection),
                                        my_tree.CopyTree(self.cfg_ana.mva_signal_selection)
                                        )

    def process(self, event):

        primary_vertex = TVector3(0, 0, 0)
        jets = getattr(event, self.cfg_ana.jets)

        for i, jet in enumerate(jets):
            for id, ptcs in jet.constituents.iteritems():
                for ptc in ptcs:
                    if ptc.q() == 0:
                        continue
                    if self.cfg_ana.method == 'simple':
                        compute_IP(ptc.path, primary_vertex, jet.p3())
                    elif self.cfg_ana.method == 'complex':
                        compute_IP_wrt_direction(ptc.path, primary_vertex, jet.p3())
                    self.smearing_significance_IP(ptc)

            self.jet_tag(jet)
            jet.n_signif_larger3, jet.m_inv_signif_larger3, jet.angle_wrt_jet_dir_larger3 = self.jet_attributes(jet,3,1)

            if hasattr(self, 'b_tag_mva'):
                jet_mva_variables = [jet.logbtag,
                                     jet.n_signif_larger3,
                                     jet.m_inv_signif_larger3,
                                     jet.angle_wrt_jet_dir_larger]

                jet.combined_b_tag = self.b_tag_mva.ComputePvalue(jet_mva_variables)

