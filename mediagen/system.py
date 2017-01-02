import os
import shlex
import subprocess
import time


"""Run a command, wait for it to exit then return both the stdout and stderr.
"""
def run_command(args_raw):
    args = shlex.split(args_raw)

    # open process
    process = subprocess.Popen(args=args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)

    # wait for process to end
    stdout, stderr = process.communicate()

    return stdout, stderr

def mkdir(name):
    if not os.path.isdir(name):
        os.makedirs(name)