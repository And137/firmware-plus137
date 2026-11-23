firmware+ (FW+) for Meshtastic devices - meshtasticd for Linux
==============================================================

meshtasticd is the Linux version of the firmware (Raspberry Pi with a LoRa HAT or a USB LoRa adapter, or a plain
PC as a virtual node). This build is linked against Debian 12 (Bookworm) libraries: Raspberry Pi OS Bookworm and
Debian 12 run it directly; other distributions need the same library versions.

1. Libraries (Debian / Raspberry Pi OS):

   sudo apt install libgpiod2 libyaml-cpp0.7 libbluetooth3 libusb-1.0-0 libi2c0 libuv1 libulfius2.7 \
     liborcania2.3 libssl3 libsdbus-c++1 libjsoncpp25 libcurl3-gnutls libnotify4 libavahi-client3

2. Install:

   sudo install -m 755 meshtasticd /usr/bin/meshtasticd
   sudo mkdir -p /etc/meshtasticd/config.d /etc/meshtasticd/available.d
   sudo cp -n config.yaml /etc/meshtasticd/config.yaml
   sudo cp -r available.d/* /etc/meshtasticd/available.d/
   sudo cp meshtasticd.service /etc/systemd/system/
   sudo cp 99-meshtasticd-udev.rules /etc/udev/rules.d/

3. Pick the file for your LoRa hardware from /etc/meshtasticd/available.d and copy it to
   /etc/meshtasticd/config.d (for example lora-waveshare-sxxx.yaml), or edit config.yaml.

4. Start:

   sudo systemctl daemon-reload
   sudo systemctl enable --now meshtasticd

Connect the Mesh+ 137 app or the Meshtastic app over the network (TCP port 4403).
Configuration reference: https://meshtastic.org/docs/hardware/devices/linux-native-hardware/
