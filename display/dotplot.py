from ROOT import TGraphStruct,TGraphNode, TGraphEdge, gPad, TCanvas

gs = TGraphStruct()
n0 = TGraphNode("no", "Node 0")
gs.AddNode(n0)
n1 = gs.AddNode("ned1", "Node 1")
n1.SetFillColor(2)
n2 = gs.AddNode("n2", "Node 3")
n3 = gs.AddNode("n3", "Node 4")
n4 = gs.AddNode("n4", "Node 5")
n5 = gs.AddNode("n5", "Node 7")
n6 = gs.AddNode("n6", "Node 6")
gs.AddEdge(n0,n1)
gs.AddEdge(n0,n2)
gs.AddEdge(n1,n2)
gs.AddEdge(n2,n3)
gs.AddEdge(n3,n4)
gs.AddEdge(n4,n5)
gs.AddEdge(n4,n6)
#hframe = TH3F("hframe","", 10, -2, 2, 10, -2, 2, 10, -2, 2)
#hframe.Draw()
c=TCanvas("c","c",800,600)
c.SetFillColor(38)
#
gs.Draw()
gPad.Update()

pass

