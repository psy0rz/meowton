#!/bin/bash

set -e

echo "Creating/updating meowton container"

podman build . -t meowton
podman rm meowton -f || true
podman run -e MATPLOTLIB=false --stop-timeout=0 --network host --privileged --name meowton -d  -v "$PWD":/app meowton
podman generate systemd -n meowton > /etc/systemd/system/meowton.service
echo "Done: created and started meowton container. To view logs:"
echo "podman logs -f meowton"
