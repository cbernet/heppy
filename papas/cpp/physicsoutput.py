#from heppy.papas.cpp.physicsoutput import  PhysicsOutput

class PhysicsOutput(object) :
    
    _is_in_use = False
    _file = None
    
    
    @classmethod
    def open(cls, outfilename):
        cls._file = open(outfilename, 'w')
        cls._is_in_use = True
        pass

    @classmethod
    def close(cls):
        cls._file.close()
        pass
    
    @classmethod
    def write(cls, text):
        if cls._is_in_use :
            cls._file.write(text)
            #print "PB: " +  text
        pass

    
    
if __name__ == '__main__':
        from heppy.papas.cpp.physicsoutput import PhysicsOutput as  pdebug
        pdebug.open("junk.txt")
        pdebug.write("hello from alice")
        pdebug.write("and more")
        pdebug.close()
      
