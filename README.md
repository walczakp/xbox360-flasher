# xbox360-teensy-flasher
XBOX360 NAND reader/writer for Teensy, communicating with PC using USB Serial (with optional debug serial)

Based on the great work of G33KatWork: https://github.com/G33KatWork/XBox-360-AVR-flasher

Tested only on Teensy LC, should work on all Teensys from 3.0 upwards without any changes.
Probably will work even with Atmega based boards (all Arduinos) with few tweaks here and there, but no Teensy specific doe has been used.

Tested only on Trinity 16MB flash, don't know if it will behave on any other console (all 16MBs should do fine).

Included a modified version of XFlash script to use serial communication.

Highly experimental, YMMV.
