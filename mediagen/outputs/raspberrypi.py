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
        self.assets = mediagen.config.get_path("assets")
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
        print "Debootstrap"
        stdout, stderr = mediagen.system.run_command("debootstrap --no-check-gpg --foreign --arch " + self.arch + " " + self.release + " " + self.rootfs + " file://" + self.repo)
        print "Debootstrap out", stdout
        print "Debootstrap err", stderr

        # copy in required files to do chroot
        mediagen.system.cp("/usr/bin/qemu-arm-static", self.rootfs + "/usr/bin/qemu-arm-static")

        # Mount the boot partition
        mediagen.system.mkdir(self.rootfs + "/boot")
        self.image.mount_partition(1, self.rootfs + "/boot")

        print "Debootstrap second stage"
        stdout, stderr = mediagen.system.chroot(self.rootfs, "/debootstrap/debootstrap --no-check-gpg --second-stage")
        print "Debootstrap second stage out", stdout
        print "Debootstrap second stage err", stderr

    def configuration(self):
        # mount the generated repo into the rootfs
        pdktmp = self.rootfs + "/tmp/pdk/"
        repo = pdktmp + "repo"
        mediagen.system.mkdir(repo)
        mediagen.system.mount_bind(self.repo, repo)

        # mount the assets folder into the rootfs
        if not self.assets == "":
            assets = pdktmp + "assets"
            mediagen.system.mkdir(assets)
            mediagen.system.mount_bind(self.assets, assets)


        # preseed file
        if not self.preseed == "" and mediagen.system.isfile(self.preseed):
            print "Running preseed"
            mediagen.system.cp(self.preseed, pdktmp + "preseed.conf")
            stdout, stderr = mediagen.system.chroot(self.rootfs, "debconf-set-selections /tmp/pdk/preseed.conf")
            print "preseed out: ", stdout
            print "preseed err: ", stderr


        # install packages
        print "Installing custom packages"
        f = open(self.rootfs + "/etc/apt/sources.list", "w")
        f.write("deb [trusted=yes] file:///tmp/pdk/repo " + self.release + " main\n")
        f.write("deb-src [trusted=yes] file:///tmp/pdk/repo " + self.release + " main")
        f.close()

        task = "cdd"
        stdout, stderr = mediagen.system.chroot(self.rootfs, "apt-get update")
        print "apt update out: ", stdout
        print "apt update err: ", stderr

        # todo: fix this. Just crashes.
        #stdout, stderr = mediagen.system.chroot(self.rootfs, "aptitude install --without-recommends -q -y -o Dpkg::Options::=\"--force-confdef\" -o Dpkg::Options::=\"--force-confold\" ~t" + task)
        #print "apt install out: ", stdout
        #print "apt install err: ", stderr

        # postinst file
        if not self.postinst == "" and mediagen.system.isfile(self.postinst):
            print "Running postinst"
            mediagen.system.cp(self.postinst, pdktmp + "postinst.sh")
            mediagen.system.run_command("chmod +x /tmp/pdk/postinst.sh")
            stdout, stderr = mediagen.system.chroot(self.rootfs, "/tmp/pdk/postinst.sh")
            print "postinst out: ", stdout
            print "postinst err: ", stderr


        # remove the repo mount
        mediagen.system.umount(repo)
        mediagen.system.rmdir(repo)


        # remove the assets mount
        if not self.assets == "":
            mediagen.system.umount(assets)
            mediagen.system.rmdir(assets)


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