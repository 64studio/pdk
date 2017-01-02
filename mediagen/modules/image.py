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
        stdout, stderr = mediagen.system.run_command("losetup -d " + self.device)
        pass