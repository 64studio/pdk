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

    def mount_device(self):
        # mount
        pass

    def unmount_device(self):
        # unmount
        pass