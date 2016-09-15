import logging

pdebugger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
pdebugger.addHandler(ch)

def set_file(filename = "pdebug.log", mode='a', level ="WARNING"):
    #todo add checks
    cf = logging.FileHandler(filename, mode)
    ch.setLevel(level)
    pdebugger.addHandler(cf)

def set_stream(level ="WARNING"):
    ch.setLevel(level)


if __name__ == '__main__':
    logger = logging.getLogger('__main__')
    logger.warning('blah')
