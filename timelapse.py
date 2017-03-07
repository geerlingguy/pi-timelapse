from picamera import PiCamera
import errno
import os
from datetime import datetime
from time import sleep

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
    camera.resolution = (720, 480)

    # Capture images in series.
    for i in range(10):
        camera.capture(dir + '/image{0:05d}.jpg'.format(i))
        sleep(1)

finally:
    camera.close()

    # Create an animated gif.
    # os.system('convert -delay 10 -loop 0 ' + dir + '/image*.jpg ' + dir + '-timelapse.gif')
