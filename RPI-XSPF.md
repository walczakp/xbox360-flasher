I used these steps to program my Matrix v1 RGH chip on RPi Zero W. YMMV and you're on your own.

1. Building OpenOCD from latest source:
```bash
sudo apt-get install git autoconf libtool make pkg-config libusb-1.0-0 libusb-1.0-0-dev telnet
git clone http://openocd.zylin.com/openocd
cd openocd
./bootstrap
./configure --enable-sysfsgpio --enable-bcm2835gpio
make
sudo make install
```

2. edit `/usr/local/share/openocd/scripts/interface/raspberrypi-native.cfg`, set your GPIO according to the comment and how you connected your chip (BCM numbering):
```
# Each of the JTAG lines need a gpio number set: tck tms tdi tdo
# Header pin numbers: 23 22 19 21
bcm2835gpio_jtag_nums 11 25 10 9
```

3. Create a directory to your RPi and cd to it, upload your xsvf file there.
4. Create a file with following config (eg. XC2C64A.cfg):
```
source [find interface/raspberrypi-native.cfg]
adapter driver raspberrypi-native

adapter speed 1000
transport select jtag
```

5. `sudo openocd -f XC2C64A.cfg`
6. search for `Warn : AUTO auto0.tap - use "jtag newtap auto0 tap -irlen 8 -expected-id 0x06e59093"`
7. Quit OpenOCD and append what's in quotes (without quotes) at the end of your .cfg file, then start OpenOCD once again.
8. `telnet localhost 4444` and enter
```
xsvf auto0.tap name-of-your-timing-script.xsvf
```
9. After getting `XSVF file programmed successfully` - that's it