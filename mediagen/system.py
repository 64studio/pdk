import os
import shlex
import shutil
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

def chroot(fs, command):
    stdout, stderr = run_command("/usr/sbin/chroot " + fs + " " + command)

    return stdout, stderr

def rmdir(name):
    if os.path.isdir(name):
        shutil.rmtree(name)

def mkdir(name):
    if not os.path.isdir(name):
        os.makedirs(name)

def cp(src, dst):
    shutil.copy(src, dst)

def sleep(millis):
    time.sleep(millis / 1000)