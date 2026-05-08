#!/bin/bash

IMAGE_NAME=zwhu/lubancat:medicine

docker run -it --rm \
--net=host \
--ipc=host \
--pid=host \
--privileged \
-v /dev:/dev \
-v /tmp/.X11-unix:/tmp/.X11-unix \
-v $(pwd):/workspace \
-e DISPLAY=$DISPLAY \
-v /dev/bus/usb:/dev/bus/usb --device-cgroup-rule='c 189:* rmw' \
-w /workspace \
$IMAGE_NAME python3 main.py
