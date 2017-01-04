import os
import shlex
import subprocess

import mediagen.system

class fdisk:
    def __init__(self, device):
        self.device = device
        self.open_process()

    def open_process(self):
        args = shlex.split("fdisk " + self.device)

        self.process = subprocess.Popen(args=args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)

    def write_stdin(self, data):
        self.process.stdin.write(str(data) + "\n")

    def create_primary_partition(self, number, start, end, part_type="linux"):
        self.write_stdin("n")
        self.write_stdin("p")
        self.write_stdin(number)
        self.write_stdin(start)
        self.write_stdin(end)

        if part_type == "linux":
            pass
        if part_type == "vfat":
            self.write_stdin("t")
            self.write_stdin("c")

    def write_changes(self):
        self.write_stdin("w")

        # wait for process to end
        stdout, stderr = self.process.communicate()

        #print "fdisk out", stdout
        #print "fdisk err", stderr