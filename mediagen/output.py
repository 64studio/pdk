
"""
Something.
"""

import mediagen.config
import mediagen.logging
import mediagen.modload

def create():
    # load output script
    output_script_name = mediagen.config.get("output-type")

    output_script = None
    try:
        output_script = mediagen.modload.load_output_script(output_script_name)
    except ImportError:
        mediagen.logging.error("cannot find output script ", output_script_name)
        return

    # create
    output_script.create()