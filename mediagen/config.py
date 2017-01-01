
"""
Handle configuration.
"""

config = {}

def handle_meta(meta):
    for key, val in meta.iteritems():
        # only handle mediagen meta
        if key[0] == "mediagen":
            config[key[1]] = val

def handle_args(args):
    for key, value in args.opts.__dict__.iteritems():
        # replace _ with dashes
        key = key.replace("_", "-")

        # if its a default argument then do not accept it
        if value != None:
            config[key] = value

def get(key):
    if key in config:
        return config[key]
    return ""
