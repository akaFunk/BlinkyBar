# Buildroot config

## How to build

```bash
git clone git://git.busybox.net/buildroot
cd buildroot
git checkout 2021.02
make BR2_EXTERNAL=../path/to/repo/buildroot_external/ BlinkyBar_defconfig
make
```

Das SD-Karten-Image liegt im Buildrootordner unter output/images/sdcard.img.
