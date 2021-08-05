#!/usr/bin/env python3

import click

def two_complement_to_int(data, valid_bit, mask):
    valid_data = data & mask
    is_neg = valid_data >> (valid_bit - 1)
    return (-(((~valid_data) & mask) + 1)) if is_neg else valid_data

@click.command()
@click.argument('hex_str', type=click.STRING)
def main(hex_str):
    '''convert hex string into linear num according to PMBus spec'''
    val = int(hex_str, 16)
    multiplier = 1000
    exponent = two_complement_to_int(val >> 11, 5, 0x1f);
    mantissa = two_complement_to_int(val & 0x7ff, 11, 0x7ff);
    click.echo(f'exp={exponent}, man={mantissa}, multiplier={multiplier}')
    result = int(mantissa * (2 ** exponent) * multiplier)
    click.echo(f'result = {result}')


if __name__ == "__main__":
    main()
