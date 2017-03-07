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
    camera.resolution = (config['image']['width'], config['image']['height'])

    # Capture images in series.
    for i in range(config['total_images']):
        camera.capture(dir + '/image{0:05d}.jpg'.format(i))
        sleep(config['interval'])

finally:
    camera.close()

    # Create an animated gif (Requires ImageMagick).
    if config['create_gif']:
        os.system('convert -delay 10 -loop 0 ' + dir + '/image*.jpg ' + dir + '-timelapse.gif')
