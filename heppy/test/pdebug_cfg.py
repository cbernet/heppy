from heppy.analyzers.PDebugger import PDebugger
import heppy.framework.config as cfg
import os

pdebug = cfg.Analyzer(
PDebugger,
output_to_stdout = False, #optional
debug_filename = os.getcwd()+'/python_physics_debug.log' #optional argument
)
