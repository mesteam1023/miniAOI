import subprocess
import os
import cv2 as cv
from capture_image.gpio_controller import raspi_io

async def capture_frame(source):
    raspi_io.__init__()
    raspi_io.flash_on()
    if source:
        file_name = "Sources/source_image.jpg"
    else:
        file_name = "captured_image.jpg"
    ffmpeg_cmd = [
        "libcamera-still",
        "--timeout",
        "1000",
        "--width",
        "1000",
        "--height",
        "1000",
        # "--autofocus-mode",
        # "auto",
        # "--autofocus-range",
        # "full",
        # "--autofocus-speed",
        # "fast",
        # "--autofocus-window","0.2,0.2,0.8,0.8",
        # "--shutter",
        # "3000",
        # "--sharpness",
        # "15",
        # "--contrast",
        # "1",
        # "--brightness",
        # "0.2",
        # "--hdr","sensor",
        # "--autofocus-on-capture",
        # "1",
        "-o",
        file_name
    ]
    subprocess.run(ffmpeg_cmd)
    raspi_io.flash_off()
    raspi_io.cleanup()

def take_picture_ocr():
    ffmpeg_cmd = [
        "libcamera-still",
        "--timeout",
        "0",
        "--vflip",
        "1",
        "--hflip",
        "1",
        # "--lens-position","5"
        # "--autofocus-mode","auto",
        # "--autofocus-range","full",
        # "--autofocus-speed","fast",
        # "--autofocus-window","0.3,0.3,0.5,0.5",
        "--width",
        "4608",
        "--height",
        "2592",
        # "--shutter", "10000",
        "--sharpness",
        "10",
        "--contrast",
        "0.5",
        "--brightness",
        "-0.1",
        # "--immediate","1",
        # "--hdr",
        # "sensor",
        # "--autofocus-on-capture","1",
        "--denoise",
        "off",
        "--o",
        "ocr.jpg",
        "--quality",
        "1000",
        "--roi",
        "0.4,0.4,0.5,0.5",
    ]
    subprocess.run(ffmpeg_cmd)


def take_live_ocr():
    ffmpeg_cmd = [
        "libcamera-still",
        "--timeout",
        "0",
        # "--lens-position","5",
        "--autofocus-mode",
        "auto",
        "--autofocus-range",
        "full",
        "--autofocus-speed",
        "fast",
        "--autofocus-window",
        "0.3,0.3,0.5,0.5",
        # "--width", "1536",
        # "--height", "864",
        # "--shutter", "10000",
        # "--sharpness", "10",
        # "--contrast", "1",
        # "--brightness", "0.5",
        # "--immediate","1",
        # "--hdr",
        # "sensor",
        "--autofocus-on-capture",
        "1",
        "--denoise",
        "cdn_hq",
        "--o",
        "ocr.jpg",
        # "-q","1000"
        "--roi",
        "0.3,0.3,0.5,0.5",
    ]
    subprocess.run(ffmpeg_cmd)


def take_picture(image_name):
    cap = cv.VideoCapture(0)

    while True:
        success, img = cap.read()
        cv.imshow("Image", img)
        if cv.waitKey(1) & 0xFF == ord("q"):
            cv.imwrite(filename='captured_image.jpg', img=img)

            break


#capture_frame(False)

    # cvlc v4l2:///dev/video0 :v4l2-standard= :live-caching=300 :sout='#transcode{vcodec=h264,acodec=none}:rtp{sdp=rtsp://:8554/}' :sout-keep


# ffmpeg -f -framerate 24 video4linux2 -i /dev/video0 -c:v libx264 -f rtp rtp://0.0.0.0:8888
# libcamera-vid -t 0 --inline --listen -o - | ffmpeg -i - -f lavfi -i anullsrc -c:v copy -c:a aac -strict experimental -f flv rtmp://0.0.0.0:8888/live/1

# libcamera-vid --inline --listen -o - | ffmpeg -i - -c:v copy -f mpegts http://<Your_IP>:<Port>
# [tcp @ 0x559c113990] Connection to tcp://0.0.0.0:8888 failed: Connection refused http://0.0.0.0:8888: Connection refused
