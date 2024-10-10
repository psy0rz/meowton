#!/bin/bash

set -e

echo "Creating/updating meowton container"

### build / create

systemctl stop meowton || true
podman rm meowton -f || true
podman build . -t meowton --pull
podman create -e MATPLOTLIB=false --stop-timeout=0 --network host --privileged --name meowton -v /etc/localtime:/etc/localtime:ro -v "$PWD":/app meowton

# add to systemctl
podman generate systemd -n meowton > /etc/systemd/system/meowton.service
systemctl daemon-reload
systemctl enable meowton --now


echo "Done: created and started meowton container."
echo "Use systemctl to start/top meowton."
echo "Use jouralctl -f to see logs."
