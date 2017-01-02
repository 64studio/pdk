def info(*args):
    print "[INFO]", " ".join(map(str, args))

def warn(*args):
    print "[WARN]", " ".join(map(str, args))

def error(*args):
    print "[ERROR]", " ".join(map(str, args))