# This is the Raspberry PI version, still work in progress!

![logo](https://raw.githubusercontent.com/psy0rz/meowton/master/logo/normal.png)
# Automatic cat dieting system 

Use Pi zero 2 W, with  rpi-imager with Ubuntu server 22 64-bit

Meowton is a system that will automaticly diet your cat and create nice graphs.

For more info look at the wiki: https://github.com/psy0rz/meowton/wiki


## Instructions 

### cleanup useless overhad

```console
apt purge snapd multipath-tools
systemctl disable --now unattended-upgrades.service packagekit

```

### install podman and build/start image

```console
apt install podman-docker -y
./podman-build.sh
```

