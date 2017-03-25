from picamera import PiCamera
import errno
import os
from datetime import datetime
from time import sleep
import yaml

config = yaml.safe_load(open("config.yml"))
camera = PiCamera()

def create_timestamped_dir(dir):
    try:
        os.makedirs(dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

try:
    # Create directory based on current timestamp.
    dir = os.path.join(os.getcwd(), 'series-' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    create_timestamped_dir(dir)

    # Set camera resolution.
    if config['resolution']:
        camera.resolution = (config['resolution']['width'], config['resolution']['height'])

    # Set ISO.
    camera.iso = config['iso']
    sleep(2)

    # Set shutter speed and sleep to allow camera to lock in exposure.
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

    # Capture images in series.
    for i in range(config['total_images']):
        camera.capture(dir + '/image{0:05d}.jpg'.format(i))
        sleep(config['interval'] - 2)

finally:
    camera.close()

    # Create an animated gif (Requires ImageMagick).
    if config['create_gif']:
        os.system('convert -delay 10 -loop 0 ' + dir + '/image*.jpg ' + dir + '-timelapse.gif')

    # Create a video (Requires avconv - which is basically ffmpeg).
    if config['create_video']:
        os.system('avconv -framerate 20 -i ' + dir + '/image%05d.jpg -vf format=yuv420p ' + dir + '/timelapse.mp4')
