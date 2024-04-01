#!/bin/bash

#podman restart meowton
#podman logs -f meowton
systemctl restart meowton
journalctl -f -u meowton
