import os

import mediagen.config
import mediagen.logging
import mediagen.modules.image
import mediagen.modules.fdisk
import mediagen.system

def create():
    output = RaspberryPi()
    try:
        output.prepare()
        output.create_base_image()
        output.mount_image()
        output.partition()
        output.mount_rootfs()
        output.debootstrap()
        output.configuration()
    except Exception as exc:
        print type(exc)
        print exc.args
        print exc
    finally:
        output.cleanup()

class RaspberryPi:
    def __init__(self):
        # read in configuration
        self.tmp = mediagen.config.get_path("tmp-dir")
        self.rootfs = self.tmp + "/rootfs"
        self.preseed = mediagen.config.get_path("raspberrypi.preseed")
        self.postinst = mediagen.config.get_path("raspberrypi.postinst")
        self.img_size = mediagen.config.get("raspberrypi.img-size")
        self.output_dest = mediagen.config.get_path("output-dest")
        self.output_dir = os.path.dirname(self.output_dest)
        self.bootsize = mediagen.config.get("raspberrypi.boot-size")
        self.repo = mediagen.config.get_path("repo")
        self.release = mediagen.config.get("release")
        self.arch = mediagen.config.get("arch")

    def prepare(self):
        mediagen.system.rmdir(self.tmp)
        mediagen.system.mkdir(self.tmp)
        mediagen.system.mkdir(self.rootfs)

    def create_base_image(self):
        """Create the base image
        """
        mediagen.logging.info("Creating base image")

        # create output directory
        mediagen.system.mkdir(self.output_dir)

        # create image
        # todo: check img_size is a reasonable size in MB
        self.image = mediagen.modules.image.Image(self.output_dest)
        self.image.create(self.img_size)
        mediagen.logging.info("Base image created!")

    def mount_image(self):
        """Mounts the base image
        """
        mediagen.logging.info("Mounting base image")
        self.image.mount_device()
        mediagen.logging.info("Base image mounted!")

    def partition(self):
        # todo: check bootsize is a reasonable size in MB
        bootsize = "+" + self.bootsize + "M"

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
        self.image.mount_partition(2, self.rootfs)

    def debootstrap(self):
        #print "Debootstrap"
        stdout, stderr = mediagen.system.run_command("debootstrap --no-check-gpg --foreign --arch " + self.arch + " " + self.release + " " + self.rootfs + " file://" + self.repo)
        #print "debootstrap out",stdout
        #print "debootstrap err",stderr

        # copy in required files to do chroot
        mediagen.system.cp("/usr/bin/qemu-arm-static", self.rootfs + "/usr/bin/qemu-arm-static")

        # Mount the boot partition
        mediagen.system.mkdir(self.rootfs + "/boot")
        self.image.mount_partition(1, self.rootfs + "/boot")

        #print "Debootstrap second stage"
        stdout, stderr = mediagen.system.chroot(self.rootfs, "/debootstrap/debootstrap --no-check-gpg --second-stage")
        #print "secondin out",stdout
        #print "secondinerr",stderr

    def configuration(self):
        # preseed file
        if not self.preseed == "":
            print "preseed", self.preseed

        # install packages
        print "installing packages"

        # postinst file
        if not self.postinst == "":
            print "postinst", self.postinst


    def cleanup(self):
        """Cleans up afterwards.
        """
        mediagen.logging.info("Unmounting & cleaning up")

        # unmount bootfs and rootfs from tmp folder
        self.image.unmount_partition(self.rootfs + "/boot")
        self.image.unmount_partition(self.rootfs)

        self.image.unmount_device_partitions()
        self.image.unmount_device()

        # rm tmp dir
        mediagen.system.rmdir(self.tmp)

        mediagen.logging.info("Unmounted & clean!")