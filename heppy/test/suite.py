
if __name__ == '__main__':   
    import unittest
    import sys
    import os

    import heppy.framework.context as context

    os.chdir(context.heppy_path)

    suites = []
    
    pcks = [
        'test',  # if particles is before test, test fails! 
        'analyzers',
        'display', 
        'framework',
        'papas', 
        'particles',
        'statistics',
        'utils'
        ]

    for pck in pcks:
        loader =  unittest.TestLoader()
        suites.append(loader.discover(pck))

    suite = unittest.TestSuite(suites)
    # result = unittest.TextTestResult(sys.stdout, True, 1)
    # suite.run(result)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

 

