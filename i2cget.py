#!/usr/bin/env python3

import click

def hexdump(src, length=16, sep='.'):
    FILTER = ''.join([(len(repr(chr(x))) == 3) and chr(x) or sep for x in range(256)])
    lines = []
    for c in range(0, len(src), length):
        chars = src[c:c+length]
        hexstr = ' '.join(["%02x" % ord(x) for x in chars]) if type(chars) is str else ' '.join(['{:02x}'.format(x) for x in chars])
        if len(hexstr) > 24:
            hexstr = "%s %s" % (hexstr[:24], hexstr[24:])
        printable = ''.join(["%s" % ((ord(x) <= 127 and FILTER[ord(x)]) or sep) for x in chars]) if type(chars) is str else ''.join(['{}'.format((x <= 127 and FILTER[x]) or sep) for x in chars])
        lines.append("%08x:  %-*s  |%s|" % (c, length*3, hexstr, printable))
    return '\n'.join(lines)


class SmbusReader():
    def __init__(self, bus_no, i2c_addr, force=True):
        from smbus2 import SMBus
        self.bus = SMBus(bus_no, force)
        self.i2c_addr = i2c_addr

    def __del__(self):
        self.bus.close()

    def __read_blk(self, offset, length):
        return self.bus.read_i2c_block_data(self.i2c_addr, offset, length)

    def read(self, offset, length):
        BLK_MAX = 32
        data = []
        while 0 < length:
            rd_len = length if length < BLK_MAX else BLK_MAX
            data.extend(self.__read_blk(offset, rd_len))
            length -= rd_len
            offset += rd_len
        return data


@click.command()
@click.argument('bus_no', type=click.INT)
@click.argument('i2c_addr', type=click.STRING)
@click.argument('cmd', type=click.STRING)
@click.argument('length', type=click.STRING, default='1')
def main(bus_no, i2c_addr, cmd, length):
    print(f'read i2c-{bus_no}-{i2c_addr}, cmd({cmd}), length({length})')
    i2c_addr = int(i2c_addr, 0) # str to int, this handle both hex and dec.
    cmd = int(cmd, 0)
    length = int(length, 0)
    data = bytes(SmbusReader(bus_no, i2c_addr).read(cmd, length))
    print(hexdump(data))

if __name__ == "__main__":
    main()
