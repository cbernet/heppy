#!/bin/env python

def var( tree, varName, type=float ):
    tree.var(varName, type)

def fill( tree, varName, value ):
    tree.fill( varName, value )

# simple particle

def bookParticle( tree, pName ):
    var(tree, '{pName}_pt'.format(pName=pName))
    var(tree, '{pName}_eta'.format(pName=pName))
    var(tree, '{pName}_phi'.format(pName=pName))
    var(tree, '{pName}_mass'.format(pName=pName))

def fillParticle( tree, pName, particle ):
    fill(tree, '{pName}_pt'.format(pName=pName), particle.P4().Pt )
    fill(tree, '{pName}_eta'.format(pName=pName), particle.P4().Eta )
    fill(tree, '{pName}_phi'.format(pName=pName), particle.P4().Phi )
    fill(tree, '{pName}_mass'.format(pName=pName), particle.P4().Mass )
    
# jet

def bookJet( tree, pName ):
    bookParticle(tree, pName )
    var(tree, '{pName}_npart'.format(pName=pName))

def fillJet( tree, pName, jet ):
    fillParticle(tree, pName, jet )
    fill(tree, '{pName}_npart'.format(pName=pName), len(jet.particles) )

# lepton

def bookLepton( tree, pName ):
    bookParticle(tree, pName )
    var(tree, '{pName}_iso'.format(pName=pName))

def fillLepton( tree, pName, lepton ):
    fillParticle(tree, pName, lepton )
    fill(tree, '{pName}_iso'.format(pName=pName), lepton.iso )
