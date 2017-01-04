import re
import os

import mediagen.system

class Image:
    def __init__(self, filename):
        self.filename = filename

    def exists(self):
        """Check whether the image exists."""
        return os.path.exists(self.filename)

    def create(self, size):
        stdout, stderr = mediagen.system.run_command("dd if=/dev/zero of=" + self.filename + " bs=1MB count=" + size)
        return True

    def mount_device(self):
        # mount
        stdout, stderr = mediagen.system.run_command("losetup -f --show " + self.filename)
        device = stdout.rstrip()
        if not device.startswith("/dev/loop"):
            mediagen.logging.error("could not mount loop! mounted as: " + device)
            return False

        self.device = device
        return True

    def unmount_device(self):
        # unmount

        # todo: does this belong here?
        stdout, stderr = mediagen.system.run_command("dmsetup remove_all")

        stdout, stderr = mediagen.system.run_command("losetup -d " + self.device)

    def mount_device_partitions(self):
        # mount

        # count number of partitions
        stdout, stderr = mediagen.system.run_command("kpartx -l " + self.device)
        self.partition_count = len(stdout.split("\n")) - 1

        # mount partitions
        stdout, stderr = mediagen.system.run_command("kpartx -va " + self.device)
        self.partition_device = "/dev/mapper/" + re.search("(loop[0-9]+)p", stdout).group(1)

        # sometimes we miss it
        mediagen.system.sleep(1000)

    def unmount_device_partitions(self):
        # unmount
        stdout, stderr = mediagen.system.run_command("kpartx -d " + self.partition_device)

    def format_partition(self, num, filesystem, label=""):
        # format the partition
        device = self.get_partition_device(num)

        command = ""
        if filesystem == "vfat":
            command = "mkfs.vfat " + device + " -n " + label
        if filesystem == "ext4":
            command = "mkfs.ext4 " + device + " -L " + label

        stdout, stderr = mediagen.system.run_command(command)

    def mount_partition(self, num, location):
        # mount the partition
        device = self.get_partition_device(num)

        stdout, stderr = mediagen.system.run_command("mount " + device + " " + location)

    def unmount_partition(self, location):
        # unmount the partition

        stdout, stderr = mediagen.system.run_command("umount " + location)

    def get_partition_device(self, num):
        # starting with partition 1
        return self.partition_device + "p" + str(num)