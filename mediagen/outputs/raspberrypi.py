import os

import mediagen.config
import mediagen.logging
import mediagen.modules.image
import mediagen.modules.fdisk
import mediagen.system

def create():
    output = RaspberryPi()
    output.create_base_image()
    output.mount_image()
    output.partition()

    # todo:-
    # run debootstrap
    # configure system
    # install packages

    output.cleanup()

class RaspberryPi:
    def create_base_image(self):
        """Create the base image
        """
        mediagen.logging.info("Creating base image")

        img_size = mediagen.config.get("raspberrypi.img-size")
        output_dest = mediagen.config.get("output-dest")
        output_dest = mediagen.config.get_full_path(output_dest)
        output_dir = os.path.dirname(output_dest)

        # create output directory
        mediagen.system.mkdir(output_dir)

        # create image
        # todo: check img_size is a reasonable size in MB
        self.image = mediagen.modules.image.Image(output_dest)
        self.image.create(img_size)
        mediagen.logging.info("Base image created!")

    def mount_image(self):
        """Mounts the base image
        """
        mediagen.logging.info("Mounting base image")
        self.image.mount_device()
        mediagen.logging.info("Base image mounted!")

    def partition(self):
        bootsize = mediagen.config.get("raspberrypi.boot-size")
        # todo: check bootsize is a reasonable size in MB
        bootsize = "+" + bootsize + "M"

        fdisk = mediagen.modules.fdisk.fdisk(self.image.device)
        fdisk.create_primary_partition(1, "", bootsize, "fat")
        fdisk.create_primary_partition(2, "", "", "linux")
        fdisk.write_changes()

    def cleanup(self):
        """Cleans up afterwards.
        """
        mediagen.logging.info("Unmounting base image")
        self.image.unmount_device()
        mediagen.logging.info("Base image unmounted!")