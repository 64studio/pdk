import mediagen.config
import mediagen.logging
import mediagen.modules.image
import mediagen.system

def create():
    img_size = mediagen.config.get("raspberrypi.img-size")
    output_dest = mediagen.config.get("output-dest")

    # create image
    # todo: check img_size is a reasonable size in MB
    mediagen.logging.info("Creating image")
    img = mediagen.modules.image.Image(mediagen.config.get_full_path(output_dest))
    img.create(img_size)
    mediagen.logging.info("Image created!")

    # todo
    # mount image as a device
    # partition image
    # run debootstrap
    # configure system
    # install packages
    # unmount image device