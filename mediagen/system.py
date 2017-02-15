import os
import os.path
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

def cp(src, dest):
    shutil.copy(src, dest)

def mount_bind(src, dest):
    stdout, stderr = run_command("mount --bind " + src + " " + dest)

def umount(dest):
    stdout, stderr = run_command("umount " + dest)

def isfile(dest):
    return os.path.isfile(dest)

def sleep(millis):
    time.sleep(millis / 1000)