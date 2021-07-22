#!/usr/bin/env python3


def is_checksum_valid(buf, length):
    if length > len(buf):
        return False
    else:
        return sum(buf[0:length]) % 256 == 0


class CommonHeader():
    """CommonHeader class takes bytes and provides info like dict """

    LENGTH = 8

    def __init__(self, buf):
        self.valid = is_checksum_valid(buf, self.LENGTH)
        if self.valid:
            self.data = dict()
            self.data['version'] = buf[0]
            self.data['internal'] = buf[1] * 8
            self.data['chassis'] = buf[2] * 8
            self.data['board'] = buf[3] * 8
            self.data['product'] = buf[4] * 8
            self.data['multirecord'] = buf[5] * 8

    @property
    def is_valid(self):
        return self.valid

    @property
    def product_info_base_offset(self):
        return self.data['product'] if self.is_valid else None



class ProductInfo():
    """This class takes types (starts from Product Info Area) and provide specific info"""

    DYNAMIC_FILEDS = ['manufacturer', 'product', 'model', 'version', 'serial', 'asset', 'fru_id']

    def parse_fields(self, name, idx):
        self.info[name + '_idx'] = idx + 1
        self.info[name + '_len'] = self.buf[idx] & 0x3f
        return idx + self.info[name + '_len'] + 1

    def __init__(self, buf):
        self.length = buf[1] * 8
        self.valid = is_checksum_valid(buf, self.length)
        if self.valid is False:
            return

        self.buf = buf
        self.info = dict()
        idx = 3
        for field in self.DYNAMIC_FILEDS:
            idx = self.parse_fields(field, idx)

    @property
    def is_valid(self):
        return self.valid

    def get_field(self, name):
        start = self.info[name + '_idx']
        end = start + self.info[name + '_len']
        return self.buf[start:end].decode('utf-8') # might exception here

    def dump(self):
        if self.is_valid is False:
            print('The product info is NOT valid.')
            return

        print('----- Dump Product Info ----- ')
        for f in self.DYNAMIC_FILEDS:
            print(f'{f}: {self.get_field(f)}')


### Test Code Here ####
def main():
    # test_buf = bytes([
    #     0x01, 0x00, 0x00, 0x00, 0x01, 0x0b, 0x00, 0xf3, 0x01, 0x0a, 0x19, 0xc8, 0x33, 0x59, 0x20, 0x50,
    #     0x4f, 0x57, 0x45, 0x52, 0xca, 0x55, 0x52, 0x4d, 0x31, 0x41, 0x31, 0x35, 0x31, 0x41, 0x4d, 0xc8,
    #     0x59, 0x4d, 0x2d, 0x31, 0x31, 0x35, 0x31, 0x44, 0xc4, 0x41, 0x30, 0x33, 0x52, 0xd2, 0x53, 0x41,
    #     0x30, 0x36, 0x30, 0x50, 0x31, 0x35, 0x32, 0x30, 0x32, 0x35, 0x30, 0x30, 0x30, 0x38, 0x32, 0x31,
    #     0x03, 0x14, 0x06, 0x1b, 0xc9, 0x50, 0x32, 0x43, 0x33, 0x30, 0x33, 0x41, 0x30, 0x32, 0xc3, 0x41,
    #     0x30, 0x36, 0xc1, 0x00, 0x00, 0x00, 0x00, 0x55, 0x00, 0x02, 0x18, 0x68, 0x7e, 0x96, 0x00, 0xb4,
    #     0x00, 0x19, 0x01, 0x28, 0x23, 0x20, 0x67, 0x00, 0x00, 0x00, 0x00, 0x2f, 0x3f, 0x11, 0x1f, 0xb4,
    #     0x10, 0x00, 0x00, 0x00, 0x00, 0x01, 0x82, 0x0d, 0x67, 0x09, 0x01, 0xb0, 0x04, 0x8c, 0x04, 0xd4,
    #     0x04, 0x78, 0x00, 0x00, 0x00, 0xd4, 0x30, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff
    #     ])

    # test_buf = bytes([
    #     0x01, 0x00, 0x00, 0x00, 0x01, 0x0b, 0x00, 0xf3, 0x01, 0x0a, 0x19, 0xc8, 0x33, 0x59, 0x20, 0x50,
    #     0x4f, 0x57, 0x45, 0x52, 0xca, 0x53, 0x50, 0x52, 0x49, 0x4e, 0x36, 0x35, 0x31, 0x41, 0x4d, 0xc8,
    #     0x59, 0x4d, 0x2d, 0x32, 0x36, 0x35, 0x31, 0x59, 0xc4, 0x42, 0x52, 0x20, 0x20, 0xd2, 0x53, 0x41,
    #     0x31, 0x36, 0x30, 0x4e, 0x30, 0x39, 0x31, 0x35, 0x33, 0x39, 0x30, 0x34, 0x36, 0x35, 0x36, 0x35,
    #     0x03, 0x0f, 0x0a, 0x15, 0xc9, 0x50, 0x33, 0x43, 0x33, 0x30, 0x30, 0x41, 0x30, 0x34, 0xc3, 0x41,
    #     0x31, 0x36, 0xc1, 0x00, 0x00, 0x00, 0x00, 0x1d, 0x00, 0x02, 0x18, 0x4c, 0x9a, 0x8a, 0x02, 0x0c,
    #     0x03, 0x3c, 0x05, 0x28, 0x23, 0x90, 0x33, 0x00, 0x00, 0x00, 0x00, 0x2f, 0x3f, 0x0e, 0x1f, 0x3c,
    #     0xf3, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x0d, 0x0e, 0xe2, 0x01, 0xb0, 0x04, 0x8c, 0x04, 0xd4,
    #     0x04, 0x78, 0x00, 0xe8, 0x03, 0xa4, 0xce, 0x01, 0x82, 0x0d, 0x59, 0x17, 0x82, 0xf4, 0x01, 0xdb,
    #     0x01, 0x0d, 0x02, 0x32, 0x00, 0x64, 0x00, 0xa0, 0x0f, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff
    # ])

    test_buf = bytes([
        0x01, 0x00, 0x00, 0x00, 0x01, 0x0b, 0x00, 0xf3, 0x01, 0x0a, 0x19, 0xc8, 0x41, 0x43, 0x42, 0x45,
        0x4c, 0x50, 0x53, 0x55, 0xca, 0x46, 0x53, 0x46, 0x30, 0x34, 0x35, 0x2d, 0x36, 0x31, 0x31, 0xc8,
        0x46, 0x53, 0x46, 0x30, 0x34, 0x35, 0x20, 0x20, 0xc4, 0x36, 0x31, 0x31, 0x47, 0xd2, 0x46, 0x53,
        0x46, 0x30, 0x34, 0x35, 0x31, 0x39, 0x31, 0x32, 0x30, 0x30, 0x30, 0x35, 0x36, 0x38, 0x20, 0x20,
        0x03, 0x60, 0x7b, 0xba, 0xc9, 0x34, 0x35, 0x2d, 0x36, 0x31, 0x31, 0x47, 0x20, 0x20, 0xc3, 0x30,
        0x31, 0x20, 0xc1, 0x00, 0x00, 0x00, 0x00, 0xf6, 0x00, 0x02, 0x18, 0x66, 0x80, 0x8a, 0x02, 0x8a,
        0x02, 0x28, 0x01, 0x28, 0x23, 0x90, 0x33, 0x00, 0x00, 0x00, 0x00, 0x2f, 0x3f, 0x0c, 0x1f, 0x8a,
        0x28, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x0d, 0x0e, 0xe2, 0x01, 0xb0, 0x04, 0x8c, 0x04, 0xd4,
        0x04, 0x78, 0x00, 0xe8, 0x03, 0xa4, 0xce, 0x01, 0x82, 0x0d, 0x45, 0x2b, 0x82, 0xf4, 0x01, 0xdb,
    ])

    hdr = CommonHeader(test_buf)
    if hdr.is_valid is False:
        print('The Header is not valid, exit..')
        return

    prod_info = ProductInfo(test_buf[hdr.product_info_base_offset:])
    prod_info.dump()


if __name__ == "__main__":
    main()