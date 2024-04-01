#!/bin/bash

set -e

echo "Creating/updating meowton container"

podman build . -t meowton
podman rm meowton -f || true
podman run -e MATPLOTLIB=false --stop-timeout=0 --network host --privileged --name meowton -d  -v "$PWD":/app meowton

echo "Done: created and started meowton container. To view logs:"
echo "podman logs -f meowton"
