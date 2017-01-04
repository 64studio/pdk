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
    output.mount_rootfs()
    output.debootstrap()
    output.basic_configuration()

    # todo:-
    # configure system
    # install packages

    output.cleanup()

class RaspberryPi:
    def __init__(self):
        self.tmp = mediagen.config.get_path("tmp-dir")
        mediagen.system.rmdir(self.tmp)
        mediagen.system.mkdir(self.tmp)

        self.tmp_rootfs = self.tmp + "/rootfs"
        mediagen.system.mkdir(self.tmp_rootfs)

    def create_base_image(self):
        """Create the base image
        """
        mediagen.logging.info("Creating base image")

        img_size = mediagen.config.get("raspberrypi.img-size")
        output_dest = mediagen.config.get_path("output-dest")
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

        # create partitions
        fdisk = mediagen.modules.fdisk.fdisk(self.image.device)
        fdisk.create_primary_partition(1, "", bootsize, "vfat")
        fdisk.create_primary_partition(2, "", "", "linux")
        fdisk.write_changes()

        # format partitions
        self.image.mount_device_partitions()
        self.image.format_partition(1, "vfat", "boot")
        self.image.format_partition(2, "ext4", "root")

    def mount_rootfs(self):
        # mount rootfs into tmp folder
        self.image.mount_partition(2, self.tmp_rootfs)

    def debootstrap(self):
        #todo: check arguments
        repo_dir = mediagen.config.get_path("repo-dir")
        release = mediagen.config.get("release")
        arch = "armhf"

        print "debootstrappin' "
        stdout, stderr = mediagen.system.run_command("debootstrap --no-check-gpg --foreign --arch " + arch + " " + release + " " + self.tmp_rootfs + " file://" + repo_dir)
        #print "debootstrap out",stdout
        #print "debootstrap err",stderr

        print "secondin' "
        stdout, stderr = mediagen.system.run_command("/usr/sbin/chroot " + self.tmp_rootfs + " /debootstrap/debootstrap --no-check-gpg --second-stage")
        #print "secondin out",stdout
        #print "secondinerr",stderr

        mediagen.system.cp("/usr/bin/qemu-arm-static", self.tmp_rootfs + "/usr/bin/qemu-arm-static")

        # Mount the boot partition
        #mount -t vfat $bootp $bootfs
        mediagen.system.mkdir(self.tmp_rootfs + "/boot")
        self.image.mount_partition(1, self.tmp_rootfs + "/boot")

    def basic_configuration(self):
        pass

    def cleanup(self):
        """Cleans up afterwards.
        """
        mediagen.logging.info("Unmounting & cleaning up")

        # unmount bootfs and rootfs from tmp folder
        self.image.unmount_partition(self.tmp_rootfs + "/boot")
        self.image.unmount_partition(self.tmp_rootfs)

        self.image.unmount_device_partitions()
        self.image.unmount_device()

        # rm tmp dir
        mediagen.system.rmdir(self.tmp)

        mediagen.logging.info("Unmounted & clean!")