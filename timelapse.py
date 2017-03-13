from picamera import PiCamera
import errno
import os
import sys
import threading
from datetime import datetime
from time import sleep
import yaml

config = yaml.safe_load(open("config.yml"))
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
        camera.resolution = (config['resolution']['width'], config['resolution']['height'])

    # Set ISO.
    camera.iso = config['iso']

    # Set shutter speed.
    if config['shutter_speed']:
        camera.shutter_speed = config['shutter_speed']
        camera.exposure_mode = 'off'

    # Set white balance.
    if config['white_balance']:
        camera.awb_mode = 'off'
        camera.awb_gains = (config['white_balance']['red_gain'], config['white_balance']['blue_gain'])

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
            thread = threading.Timer(config['interval'], capture_image)
            thread.daemon=True
            thread.start()

        # Start up the camera.
        camera = PiCamera()
        set_camera_options(camera)

        # Sleep to allow camera to calibrate, then take a picture.
        sleep(1)
        camera.capture(dir + '/image{0:05d}.jpg'.format(image_number))
        camera.close()

        if (image_number < (config['total_images'] - 1)):
            image_number += 1
        else:
            print '\nTime lapse capture complete! Press Ctrl-C to continue.\n'
            # TODO: This doesn't pop user into the except block below :(.
            sys.exit()

        # Needed to allow manual KeyboardInterrupt between captures.
        while True: sleep(100)

    except KeyboardInterrupt, SystemExit:
        print '\nRendering artifacts; timelapse.py will exit when complete.\n'

# Create directory based on current timestamp.
dir = os.path.join(os.getcwd(), 'series-' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
create_timestamped_dir(dir)

# Kick off the capture process.
capture_image()

# Create an animated gif (Requires ImageMagick).
if config['create_gif']:
    os.system('convert -delay 10 -loop 0 ' + dir + '/image*.jpg ' + dir + '-timelapse.gif')

# Create a video (Requires avconv - which is basically ffmpeg).
if config['create_video']:
    os.system('avconv -framerate 20 -i ' + dir + '/image%05d.jpg -vf format=yuv420p ' + dir + '/timelapse.mp4')
