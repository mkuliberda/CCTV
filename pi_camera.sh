#!/bin/bash

DATE=$(date +"%Y-%m-%d_%H%M%S")

#raspistill -vf -hf -o /home/pi/CCTV/camera/$DATE.jpg

docker build -t cctv-main .
docker run --privileged --env LD_LIBRARY_PATH=/opt/vc/lib -v /opt/vc:/opt/vc -v /home/pi:/home/pi --rm cctv-main