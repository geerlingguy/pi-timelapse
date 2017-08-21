from picamera import PiCamera
import errno
import os
import sys
import threading
from datetime import datetime
from time import sleep
import yaml

config = yaml.safe_load(open(os.path.join(sys.path[0], "config.yml")))
image_number = 0


def create_timestamped_dir(dir):
    try:
        os.makedirs(dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def set_camera_options(camera):
    # Set camera resolution.
    if config['resolution']:
        camera.resolution = (
            config['resolution']['width'],
            config['resolution']['height']
        )

    # Set ISO.
    if config['iso']:
        camera.iso = config['iso']

    # Set shutter speed.
    if config['shutter_speed']:
        camera.shutter_speed = config['shutter_speed']
        # Sleep to allow the shutter speed to take effect correctly.
        sleep(1)
        camera.exposure_mode = 'off'

    # Set white balance.
    if config['white_balance']:
        camera.awb_mode = 'off'
        camera.awb_gains = (
            config['white_balance']['red_gain'],
            config['white_balance']['blue_gain']
        )

    # Set camera rotation
    if config['rotation']:
        camera.rotation = config['rotation']

    return camera


def capture_image():
    try:
        global image_number

        # Set a timer to take another picture at the proper interval after this
        # picture is taken.
        if (image_number < (config['total_images'] - 1)):
            thread = threading.Timer(config['interval'], capture_image).start()

        # Start up the camera.
        camera = PiCamera()
        set_camera_options(camera)

        # Capture a picture.
        camera.capture(dir + '/image{0:05d}.jpg'.format(image_number))
        camera.close()

        if (image_number < (config['total_images'] - 1)):
            image_number += 1
        else:
            print '\nTime-lapse capture complete!\n'
            # TODO: This doesn't pop user into the except block below :(.
            sys.exit()

    except KeyboardInterrupt, SystemExit:
        print '\nTime-lapse capture cancelled.\n'

# Create directory based on current timestamp.
dir = os.path.join(
    sys.path[0],
    'series-' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
)
create_timestamped_dir(dir)

# Kick off the capture process.
capture_image()

# TODO: These may not get called after the end of the threading process...
# Create an animated gif (Requires ImageMagick).
if config['create_gif']:
    print '\nCreating animated gif.\n'
    os.system('convert -delay 10 -loop 0 ' + dir + '/image*.jpg ' + dir + '-timelapse.gif')  # noqa

# Create a video (Requires avconv - which is basically ffmpeg).
if config['create_video']:
    print '\nCreating video.\n'
    os.system('avconv -framerate 20 -i ' + dir + '/image%05d.jpg -vf format=yuv420p ' + dir + '/timelapse.mp4')  # noqa
