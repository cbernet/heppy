import unittest
from tlv.jet import Jet
from jet import JetConstituents
from tlv.particle import Particle
from ROOT import TLorentzVector

class TestJet(unittest.TestCase):

    
    def test_jet(self):
        ptcs = [ Particle(211, 1, TLorentzVector(1, 0, 0, 1)),
                 Particle(211, 1, TLorentzVector(2, 0, 0, 2)),
                 Particle(22, 0, TLorentzVector(5, 0, 0, 5)) ]
        jetp4 = TLorentzVector()
        jet_const = JetConstituents()
        for ptc in ptcs:
            jetp4 += ptc.p4()
            jet_const.append(ptc)
        jet_const.sort()
        jet = Jet(jetp4)
        self.assertEqual( jet.e(), 8)
        keys = sorted(list(jet_const.keys()))
        self.assertEqual( keys, [11, 13, 22, 130, 211])
        self.assertEqual(jet_const[211], [ptcs[1], ptcs[0]])
        self.assertEqual(jet_const[22], [ptcs[2]])
        self.assertEqual(jet_const[211].e(), 3)
        self.assertEqual(jet_const[130].num(), 0)
        self.assertEqual(jet_const[11].num(), 0)
        self.assertEqual(jet_const[130].num(), 0)
        self.assertEqual(jet_const[22].e(), 5)
        self.assertEqual(jet_const[22].pdgid(), 22)
        self.assertEqual(jet_const[211].pdgid(), 211)
        self.assertRaises(ValueError, jet_const[211].append, ptcs[2])
        print jet_const[211]
        
        
if __name__ == '__main__':
    unittest.main()

