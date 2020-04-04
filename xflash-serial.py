#!/usr/bin/env python
import serial
import sys
import struct
import pprint
import argparse
import code

pp = pprint.PrettyPrinter()


class ConsoleUI:
    def opStart(self, name):
        sys.stdout.write(name.ljust(40))

    def opProgress(self, progress, total=-1):
        if (total >= 0):
            prstr = "0x%04x / 0x%04x" % (progress, total)
        else:
            prstr = "0x%04x" % (progress)

        sys.stdout.write(prstr.ljust(20))
        sys.stdout.write('\x08' * 20)
        sys.stdout.flush()

    def opEnd(self, result):
        sys.stdout.write(result.ljust(20))
        sys.stdout.write("\n")


class XFlash:
    def __init__(self, serialport):
        self.serial = serial.Serial(serialport, baudrate=115200)

    def __del__(self):
        try:
            self.serial.close()
            del self.serial
        except:
            pass

    def cmd(self, cmd, argA=0, argB=0):
        buffer = struct.pack("<LL", argA, argB)

        self.serial.write(bytes([cmd]))
        self.serial.write(buffer)
        self.serial.flush()

    def flashPowerOn(self):
        self.cmd(0x10)

    def flashShutdown(self):
        self.cmd(0x11)

    def update(self):
        try:
            self.cmd(0xF0)
        except:
            pass

    def flashInit(self):
        self.cmd(0x03)

        buffer = self.serial.read(4)
        return struct.unpack("<L", buffer)[0]

    def flashDeInit(self):
        self.cmd(0x04)

    def flashStatus(self):
        self.cmd(0x05)

        buffer = self.serial.read(2)
        return struct.unpack("<H", buffer)[0]

    def flashErase(self, block):
        self.cmd(0x06, block)
        # return self.flashStatus()

    def flashReadBlock(self, block):
        self.cmd(0x01, block, 528 * 32)

        # for i in range(0, 32):
        buffer = self.serial.read(528 * 32)

        status = self.flashStatus()
        return (status, buffer)

    def flashWriteBlock(self, block, buffer):
        self.cmd(0x02, block, len(buffer))

        self.serial.write(buffer)

        return self.flashStatus()

    # def calcecc(data):


#   assert len(data) == 0x210
#   val = 0
#   for i in range(0x1066):
#     if not i & 31:
#       v = ~struct.unpack("<L", data[i/8:i/8+4])[0]
#     val ^= v & 1
#     v >>= 1
#     if val & 1:
#       val ^= 0x6954559
#     val >>= 1
#
#   val = ~val
#   return data[:-4] + struct.pack("<L", (val << 6) & 0xFFFFFFFF)
#
# def addecc(data, block = 0, off_8 = "\x00" * 4):
#   res = ""
#   while len(data):
#     d = (data[:0x200] + "\x00" * 0x200)[:0x200]
#     data = data[0x200:]
#
#     d += struct.pack("<L4B4s4s", block / 32, 0, 0xFF, 0, 0, off_8, "\0\0\0\0")
#     d = calcecc(d)
#     block += 1
#     res += d
#   return res


def main(argv):
    parser = argparse.ArgumentParser(description='XBox 360 NAND Flasher')
    parser.add_argument('port', metavar='port', type=str,
                        help='serial port for comms (e.g. COM5 or /dev/ttyUSB0)')

    subparsers = parser.add_subparsers(title='Operations', dest='action')

    parser_read = subparsers.add_parser('read', help='Dumps an image from the NAND')
    parser_read.add_argument('file', nargs=1, type=argparse.FileType('wb'), help='The file to dump the NAND to')
    parser_read.add_argument('start', nargs='?', metavar='start', action='store', type=int, default=0,
                             help='The block to start the action from')
    parser_read.add_argument('end', nargs='?', metavar='end', action='store', type=int, default=0x400,
                             help='The count of blocks to perform the action to')

    parser_write = subparsers.add_parser('write', help='Writes an image into the NAND')
    parser_write.add_argument('file', nargs=1, type=argparse.FileType('rb'), help='The image file to write to the NAND')
    parser_write.add_argument('start', nargs='?', metavar='start', action='store', type=int, default=0,
                              help='The block to start the action from')
    parser_write.add_argument('end', nargs='?', metavar='end', action='store', type=int, default=0x400,
                              help='The count of blocks to perform the action to')

    # parser_erase = subparsers.add_parser('erase', help='Erases blocks in the NAND')
    # parser_erase.add_argument('start', nargs='?', metavar='start', action='store', type=int, default=0,
    #                           help='The block to start the action from')
    # parser_erase.add_argument('end', nargs='?', metavar='end', action='store', type=int, default=0x400,
    #                           help='The count of blocks to perform the action to')
    #
    # parser_update = subparsers.add_parser('update',
    #                                       help='Jumps into the bootloader of the NAND Flashing device for updating the firmware')
    # parser_shutdown = subparsers.add_parser('shutdown', help='Shuts down the attached XBox 360')
    # parser_poweron = subparsers.add_parser('powerup', help='Powers up the attached XBox 360')

    arguments = parser.parse_args(argv[1:])

    ui = ConsoleUI()

    xf = XFlash(arguments.port)

    if arguments.action in ('erase', 'write', 'read'):
        try:
            flash_config = xf.flashInit()
            print("FlashConfig: 0x%08x" % (flash_config))
            if flash_config <= 0:
                raise Exception("FlashConfig invalid!")
        except Exception as e:
            print("Error!", e)
            xf.flashDeInit()
            return 1

    try:
        if arguments.action == 'erase':
            # start = 0
            # end = (options.flashsize * 1024) / 16
            start = arguments.start
            end = arguments.end

            ui.opStart('Erase')

            ui.opProgress(0, end)
            for b in range(start, end):
                status = xf.flashErase(b)
                ui.opProgress(b + 1, end)

            ui.opEnd('0x%04x blocks OK' % (end))

        if arguments.action == 'read':
            # start = 0
            # end = (options.flashsize * 1024) / 16
            start = arguments.start
            end = arguments.end

            ui.opStart('Read')

            ui.opProgress(0, end)
            for b in range(start, end):
                (status, buffer) = xf.flashReadBlock(b)
                ui.opProgress(b + 1, end)
                arguments.file[0].write(buffer)

        if arguments.action == 'write':
            # start = 0
            # end = (options.flashsize * 1024) / 16

            start = arguments.start
            end = arguments.end
            blocksize = 528 * 32

            ui.opStart('Write')

            ui.opProgress(0, end)
            for b in range(start, end):
                buffer = arguments.file[0].read(blocksize)

                if len(buffer) < blocksize:
                    buffer += ('\xFF' * (blocksize - len(buffer)))

                status = xf.flashWriteBlock(b, buffer)
                ui.opProgress(b + 1, end)
        #
        # if arguments.action == 'update':
        #     xf.update()
        #
        # if arguments.action == 'powerup':
        #     xf.flashPowerOn()
        #
        # if arguments.action == 'shutdown':
        #     xf.flashShutdown()
    except Exception as e:
        raise e
    finally:
        xf.flashDeInit()
        return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))

