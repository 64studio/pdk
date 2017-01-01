
"""
Something.
"""

import mediagen.config
import mediagen.modload

def create():
    # load module
    module = None
    try:
        module_name = mediagen.config.get("module")
        module = mediagen.modload.load_module(module_name)
    except ImportError:
        print "ERROR: cannot find module " + module_name
        return

    # test
    module.test()
