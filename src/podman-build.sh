#!/bin/bash

set -e

echo "Creating/updating meowton container"

# build / create
podman build . -t meowton
systemctl stop meowton || true
podman rm meowton -f || true
podman create -e MATPLOTLIB=false --stop-timeout=0 --network host --privileged --name meowton -v "$PWD":/app meowton

# add to systemctl
podman generate systemd -n meowton > /etc/systemd/system/meowton.service
systemctl daemon-reload


echo "Done: created and started meowton container. Use systemctl to start/top meowton."

./podman-restart.sh
