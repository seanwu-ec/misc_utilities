#!/usr/bin/env python3

from tabulate import tabulate
import click

ignore_chksum_err = False

def is_checksum_valid(buf, length):
    if length > len(buf):
        return False
    else:
        return sum(buf[0:length]) % 256 == 0


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

class CommonHeader():
    """CommonHeader class takes bytes and provides info like dict """

    LENGTH = 8

    def __init__(self, buf):
        self.valid = is_checksum_valid(buf, self.LENGTH)
        if self.is_valid:
            self.data = dict()
            self.data['version'] = buf[0]
            self.data['internal'] = buf[1] * 8
            self.data['chassis'] = buf[2] * 8
            self.data['board'] = buf[3] * 8
            self.data['product'] = buf[4] * 8
            self.data['multirecord'] = buf[5] * 8

    @property
    def is_valid(self):
        return self.valid if not ignore_chksum_err else True

    @property
    def product_info_base_offset(self):
        return self.data['product'] if self.is_valid else None



class ProductInfo():
    """This class takes types (starts from Product Info Area) and provide specific info"""

    DYNAMIC_FILEDS = ['manufacturer', 'product', 'model', 'version', 'serial', 'asset', 'fru_id']
    INIT_DYNAMIC_FIELDS_OFFSET = 3

    def parse_fields(self, name, addr):
        self.info[name + '_addr'] = addr + 1
        self.info[name + '_len'] = self.buf[addr] & 0x3f
        return addr + self.info[name + '_len'] + 1

    def __init__(self, buf, base_ofs):
        self.length = buf[1] * 8
        self.valid = is_checksum_valid(buf, self.length)
        if self.is_valid is False:
            print('ERROR: The product info chksum fail.')
            return

        self.buf = buf
        self.info = dict()
        addr = self.INIT_DYNAMIC_FIELDS_OFFSET + base_ofs
        for field in self.DYNAMIC_FILEDS:
            addr = self.parse_fields(field, addr)

    @property
    def is_valid(self):
        return self.valid if not ignore_chksum_err else True

    def get_field(self, name):
        ''' return addr_in_hex, len, value of the specified field'''
        addr = self.info[name + '_addr']
        len = self.info[name + '_len']
        val = self.buf[addr: addr + len].decode('utf-8') # might exception here
        return hex(addr), len, val

    def dump(self):
        header = ['field', 'addr', 'len', 'value']
        if self.is_valid is False:
            return

        print('----- Dump Product Info ----- ')
        table = []
        for f in self.DYNAMIC_FILEDS:
            if f == 'asset': # asset str cannot be decoded in utf-8, skip it.
                continue
            info = [f]
            info.extend(self.get_field(f))
            table.append(info)
        print(tabulate(table, header, tablefmt='simple', stralign='left'))


def parse(data):
    hdr = CommonHeader(data)
    if hdr.is_valid is False:
        print('ERROR: The Header is not valid')
        return

    prod_info = ProductInfo(data, hdr.product_info_base_offset)
    prod_info.dump()


"""
TODO:
# Usage ./xxx.py [--ignore-error] [file i2cdump_output.txt] [i2c bus_no i2c_addr]
1. add arguments to
    a. flag that whether take data from i2cdump format
2. handle the content that doesn't follow standard
"""

@click.group()
@click.option('--ignore-error', '-I', is_flag=True, default=False,
              help='continue parsing if checksum error occurs')
# ('--shout/--no-shout', default=False)
def root(ignore_error):
    """IPMI FRU parser"""
    global ignore_chksum_err
    ignore_chksum_err = ignore_error

@root.command(name='i2c')
@click.argument('bus_no', type=click.INT)
@click.argument('i2c_addr', type=click.STRING)
def parse_i2c(bus_no, i2c_addr):
    i2c_addr = int(i2c_addr, 0) # str to int, this handle both hex and dec.
    data = bytes(SmbusReader(bus_no, i2c_addr).read(0, 128))
    parse(data)


if __name__ == "__main__":
    root()
