import unittest
import os
import logging
import pdebug as pdebugging
from StringIO import StringIO

class TestPDebug(unittest.TestCase):

    def test_debug_output(self):
        out = StringIO()
        pdebugging.pdebugger.setLevel(logging.ERROR)
        pdebugging.set_stream(out)
        pdebugging.pdebugger.error('error console')
        pdebugging.pdebugger.info('info console')
        pdebugging.pdebugger.info('debug console')
        output = out.getvalue().strip()
        assert output == "error console"


        pdebugging.pdebugger.setLevel(logging.INFO)
        pdebugging.pdebugger.error('error console')
        pdebugging.pdebugger.info('info console')
        pdebugging.pdebugger.debug('debug console')
        output = out.getvalue().strip()
        assert output == "error console\nerror console\ninfo console"


        #add in file handler
        filename = "tempunittestdebug.log"
        pdebugging.set_file(filename)
        pdebugging.pdebugger.error('error file')
        pdebugging.pdebugger.info('info file')
        pdebugging.pdebugger.debug('debug file')
        with open(filename, 'r') as dbfile:
            data=dbfile.read()
        assert data == "error file\ninfo file\n"
        os.remove("tempunittestdebug.log")
        output = out.getvalue().strip()
        assert output == "error console\nerror console\ninfo console\nerror file\ninfo file"


if __name__ == '__main__':

    unittest.main()
