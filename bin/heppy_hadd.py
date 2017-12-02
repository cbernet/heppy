#!/usr/bin/env python
# Copyright (C) 2014 Colin Bernet
# https://github.com/cbernet/heppy/blob/master/LICENSE

import os
import pprint
import dill
import pickle
import shutil
import yaml
from heppy.bin.heppy_check import check_chunk

MAX_ARG_STRLEN = 131072

def haddPck(file, odir, idirs):
    '''add pck files in directories idirs to a directory outdir.
    All dirs in idirs must have the same subdirectory structure.
    Each pickle file will be opened, and the corresponding objects added to a destination pickle in odir.
    '''
    objsum = None
    basedir = os.getcwd()
    fileName = os.path.basename(file)
    for dirpath in idirs:
        # fileName = file.replace( idirs[0], dirpath )
        os.chdir(dirpath)
        pckfile = open(fileName)
        sys.path.insert(0, dirpath)
        obj = pickle.load(pckfile)
        sys.path.pop(0)
        if objsum is None:
            objsum = obj
        else:
            try:
                objsum += obj
            except TypeError:
                # += not implemented, nevermind
                pass
        os.chdir(basedir)
                
    oFileName = file.replace( idirs[0], odir )
    pckfile = open(oFileName, 'w')
    print 'output:', oFileName
    pickle.dump(objsum, pckfile, protocol=-1)
    txtFileName = oFileName.replace('.pck','.txt')
    txtFile = open(txtFileName, 'w')
    txtFile.write( str(objsum) )
    txtFile.write( '\n' )
    txtFile.close()
    

def hadd(fname, odir, idirs, appx=''):
    if fname.endswith('.pck'):
        haddPck(fname, odir, idirs)
        return
    elif fname.endswith('.yaml') or fname.endswith('.py'):
        # just copy the yaml file to the output dir
        shutil.copy(fname, odir)
        return 
    elif not fname.endswith('.root'):
        return
    haddCmd = ['hadd']
##    ngoodfiles = 0
    haddCmd.append( fname.replace( idirs[0], odir ).replace('.root', appx+'.root') )
    for dir in idirs:
        prov_fname = fname.replace( idirs[0], dir )
        assert(os.path.isfile(prov_fname))
##        if os.path.isfile(prov_fname):
##            ngoodfiles += 1
        haddCmd.append( prov_fname )
    # import pdb; pdb.set_trace()
    cmd = ' '.join(haddCmd)
    print cmd
    if len(cmd) > MAX_ARG_STRLEN:
        print 'Command longer than maximum unix string length; dividing into 2'
        hadd(fname, odir, idirs[:len(idirs)/2], '1')
        hadd(fname.replace(idirs[0], idirs[len(idirs)/2]), odir, idirs[len(idirs)/2:], '2')
        haddCmd = ['hadd']
        haddCmd.append( fname.replace( idirs[0], odir ).replace('.root', appx+'.root') )
        haddCmd.append( fname.replace( idirs[0], odir ).replace('.root', '1.root') )
        haddCmd.append( fname.replace( idirs[0], odir ).replace('.root', '2.root') )
        cmd = ' '.join(haddCmd)
        print 'Running merge cmd:', cmd
        os.system(cmd)
    else:
        os.system(cmd)
##    data = {
##        'processing' : {
##            'ngoodfiles' : ngoodfiles,
##            'nfiles' : len(idirs)
##        }   
##    }   
##    with open('processing.yaml', 'w') as outyaml:
##        yaml.dump(data)
        
def haddRec(odir, idirs):
    print 
    print 'adding' 
    pprint.pprint(idirs)
    print
    print 'to' 
    print odir 
    print 

    cmd = ' '.join( ['mkdir', odir])
    if os.path.isdir(odir):
        shutil.rmtree(odir)
    os.mkdir(odir)
##    try:
##        os.mkdir( odir )
##    except OSError:
##        print 
##        print 'ERROR: directory in the way. Maybe you ran hadd already in this directory? Remove it and try again'
##        print 
##        raise
    for root,dirs,files in os.walk( idirs[0] ):
        # print root, dirs, files
        for dir in dirs:
            dir = '/'.join([root, dir])
            dir = dir.replace(idirs[0], odir)
            cmd = 'mkdir ' + dir 
            # print cmd
            # os.system(cmd)
            os.mkdir(dir)
        for file in files:
            hadd('/'.join([root, file]), odir, idirs)

def haddChunks(idir, removeDestDir, cleanUp=False, base_odir='./'):
    chunks = {}
    nchunks = {}
    for path in sorted(os.listdir(idir)):
        filepath = '/'.join( [idir, path] )
        if os.path.isdir(filepath):
            compdir = path
            try:
                prefix,num = compdir.split('_Chunk')
            except ValueError:
                # ok, not a chunk
                continue
            nchunks[prefix] = nchunks.setdefault(prefix, 0) + 1
            code = check_chunk(filepath)
            if code == 1:
                chunks.setdefault( prefix, list() ).append(filepath)
    if len(chunks)==0:
        print 'warning: no chunk found.'
        return
    for comp, cchunks in chunks.iteritems():
        # odir = base_odir+'/'+'/'.join( [idir, comp] )
        odir = '/'.join( [base_odir, comp] )
        print odir, cchunks
        if removeDestDir:
            if os.path.isdir( odir ):
                shutil.rmtree(odir)
        haddRec(odir, cchunks)
        data = {
            'processing' : {
                'ngoodfiles' : len(cchunks),
                'nfiles' : nchunks[prefix]
            }   
        }   
        with open('/'.join([odir, 'processing.yaml']), 'w') as outyaml:
            yaml.dump(data, outyaml, default_flow_style=False)        
    if cleanUp:
        chunkDir = 'Chunks'
        if os.path.isdir('Chunks'):
            shutil.rmtree(chunkDir)
        os.mkdir(chunkDir)
        print chunks
        for comp, chunks in chunks.iteritems():
            for chunk in chunks:
                shutil.move(chunk, chunkDir)
 
    

if __name__ == '__main__':

    import os
    import sys
    from optparse import OptionParser
    
    sys.path.insert(0,'.')

    parser = OptionParser()
    parser.usage = """
    %prog <dir>
    Find chunks in dir, and run recursive hadd to group all chunks.
    For example: 
    DYJets_Chunk0/, DYJets_Chunk1/ ... -> hadd -> DYJets/
    WJets_Chunk0/, WJets_Chunk1/ ... -> hadd -> WJets/
    """
    parser.add_option("-r","--remove", dest="remove",
                      default=False,action="store_true",
                      help="remove existing destination directories.")
    parser.add_option("-c","--clean", dest="clean",
                      default=False,action="store_true",
                      help="move chunks to Chunks/ after processing.")

    (options,args) = parser.parse_args()

    if len(args)>2:
        print 'provide at most 2 directory as arguments: first the source, then the destination (optional)'
        sys.exit(1)

    dirname = args[0]
    if(len(args)>1):
        odir = args[1]
    else:
        odir = dirname
        
    haddChunks(dirname, options.remove, options.clean, odir)

