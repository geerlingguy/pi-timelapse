# Raspberry Pi Time-Lapse App

[![Build Status](https://travis-ci.org/geerlingguy/pi-timelapse.svg?branch=master)](https://travis-ci.org/geerlingguy/pi-timelapse)

There are a ton of different Time-Lapse scripts and apps built for the Raspberry Pi, but I wanted to make a more customized setup for my own needs.

Here's an example time-lapse video I recorded of cirrus clouds in the sky outside my window (click to view on YouTube):

<p align="center"><a href="https://www.youtube.com/watch?v=mThXDhkj0aA"><img src="https://img.youtube.com/vi/mThXDhkj0aA/0.jpg" alt="Cirrus clouds on a sunny day - Raspberry Pi Zero W time-lapse by Jeff Geerling" /></a></p>

## Usage

  1. See my blog post for an in-depth overview: [Raspberry Pi Zero W as a headless time-lapse camera](https://www.jeffgeerling.com/blog/2017/raspberry-pi-zero-w-headless-time-lapse-camera).
  2. Install dependencies: `sudo apt-get install -y python-picamera python-yaml`
  3. Download or clone this repository to your Pi.
  4. Copy `example.config.yml` to `config.yml`.
  5. Configure the timelapse by modifying values in `config.yml`.
  6. In the Terminal, `cd` into this project directory and run `python timelapse.py`.

After the capture is completed, the images will be stored in a directory named `series-[current date]`.

## Run on Raspberry Pi Startup and manage timelapses via Systemd

This project includes a Systemd unit file that allows the timelapse script to be managed like any other service on the system (e.g. start with `systemctl start timelapse`, stop with `systemctl stop timelapse`).

To use this feature, do the following:

  1. In your `config.yml`, set the `total_images` variable to a large number—as large as you want, within Python's limitations. This way you won't start a timelapse and it stops after very few images are taken.
  1. Copy the `timelapse.service` file into the Systemd unit file location: `sudo cp timelapse.service /etc/systemd/system/timelapse.service`.
  1. Reload the Systemd daemon (`sudo systemctl daemon-reload`) to load in the new unit file.
  1. Choose how you want to manage the `timelapse` service:
    1. **To start a timelapse at system boot**: `sudo systemctl enable timelapse` (`disable` to turn off, `is-enabled` to check current status)
    1. **To start a timelapse at any time**: `sudo systemctl start timelapse` (if one is not already running)
    1. **To stop a timelapse in progress**: `sudo systemctl stop timelapse`

Note: You should not try running a timelapse via the Python script directly _and_ via Systemd at the same time. This could do weird things, and is not a typical mode of operation!

## Creating animated gifs or videos

### Animated gifs

Requirements: You should install [ImageMagick](https://www.imagemagick.org/script/index.php) (`sudo apt-get -y install imagemagick`)

If you have `create_gif` set to `True` in `config.yml`, the Pi will also generate an animated gif immediately following the conclusion of the capture.

> Note: Animated gif generation can take a very long time on slower Pis, like the Pi Zero, A+, or original A or B.

### Videos

Requirements: You should install [FFmpeg](https://ffmpeg.org) (which is actually `avconv` on Raspbian — `sudo apt-get -y install libav-tools`)

If you have `create_video` set to `True` in `config.yml`, the Pi will also generate a video immediately following the conclusion of the capture.

> Note: Video generation can take a very long time on slower Pis, like the Pi Zero, A+, or original A or B.

## Manual Settings

For a more pleasing timelapse, it's best to lock in manual settings for exposure and white balance (otherwise the video has a lot of inconsistency from frame to frame). This project allows almost complete control over manual exposure settings through variables in `config.yml`, and below are listed some rules of thumb for your own settings.

> Read more about the [Raspberry Pi's Camera hardware](https://picamera.readthedocs.io/en/latest/fov.html).

### Resolution

The most common and useful Pi Camera resolutions (assuming a V2 camera module—V1 modules have different optimal resolutions) are listed below:

| Size (width x height) | Aspect | Common name            |
| --------------------- | ------ | ---------------------- |
| 3280 x 2464           | 4:3    | (max resolution)       |
| 1920 x 1080           | 16:9   | 1080p                  |
| 1280 x 720            | 16:9   | 720p (2x2 binning)     |
| 640 x 480             | 4:3    | 480p (2x2 binning)     |

Binning allows the Pi to sample a grid of four pixels and downsample the average values to one pixel. This makes for a slightly more color-accurate and sharp picture at a lower resolution than if the Pi were to skip pixels when generating the image.

### ISO

ISO is basically an indication of 'light sensitivity'. Without getting too deep in the weeds, you should use lower ISO values (`60` (V2 camera only), `100`, `200`) in bright situations, and higher ISO values (`400`, `800`) in dark situations. There's a lot more to it than that, and as you find out creative ways to use shutter speed and ISO together, those rules go out the window, but for starters, you can choose the following manual values to lock in a particular ISO on the Pi Camera:

  - `60` (not available on V1 camera module)
  - `100`
  - `200`
  - `400`
  - `800`

### Shutter Speed

Most photographers are familiar with the fractional values for common shutter speeds (1s, 1/10s, 1/30s, 1/60s, etc.), so here's a table to help convert some of the most common shutter speeds into microseconds (the value used in `config.yml`):

| Fractional Shutter Speed | µs       |
| ------------------------ | -------- |
| 6 seconds (max)          | 6000000  |
| 1 second                 | 1000000  |
| 1/8                      | 125000   |
| 1/15                     | 66666    |
| 1/30                     | 33333    |
| 1/60                     | 16666    |
| 1/125                    | 8000     |
| 1/250                    | 4000     |
| 1/500                    | 2000     |
| 1/500                    | 2000     |
| 1/1000                   | 1000     |
| 1/2000                   | 500      |

### White Balance

White balance values on the Raspberry Pi camera are set by adjusting the red and blue gain values—the green value is constant. You need to amplify red and blue certain amounts to set a specific color temperature, and here are some of the settings that worked in specific situations for _my_ camera. Note that you might need to adjust/eyeball things a little better for your own camera, as some unit-to-unit variance is to be expected on such an inexpensive little camera!

| White Balance Setting | Color Temperature (approx) | red_gain | blue_gain |
| --------------------- | -------------------------- | -------- | --------- |
| Clear blue sky        | 8000K+                     | 1.5      | 1.5       |
| Cloudy sky / overcast | 6500K                      | 1.5      | 1.2       |
| Daylight              | 5500K                      | 1.5      | 1.45      |
| Fluorescent / 'cool'  | 4000K                      | 1.3      | 1.75      |
| Incandescent / 'warm' | 2700K                      | 1.25     | 1.9       |
| Candle                | <2000K                     | TODO     | TODO      |

Note: These values will be updated over time as I find more time to calibrate my Pi camera against a few DSLRs and other devices which are much more accurate! Please file an issue if you can help make these mappings better, or find a nicer way to adjust calibrations rather than a `red_gain` and `blue_gain` value.

### Rotation

Depending on the placement of your camera, the picture taken could be upside down. To correct this, set `rotation` to a value of `0` (no rotation), or `90`, `180` or `270` degrees to rotate the image.

## License

MIT License.

## Author

This project is maintained by [Jeff Geerling](https://www.jeffgeerling.com/), author of [Ansible for DevOps](https://www.ansiblefordevops.com/).
