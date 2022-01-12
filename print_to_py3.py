#!/usr/bin/env python3
import click
import os

def is_next_to_open_parenth(line, idx):
    for i in range(idx, len(line)):
        if line[i] == ' ':
            continue
        if line[i] == '(':
            return True
        else:
            return False

def correct_print(fpath):
    fpath_out = fpath + '_out'
    with open(fpath, 'r') as fi:
        with open(fpath_out, 'w') as fo:
            for line in fi:
                idx = line.find('print')
                if idx==-1:
                    fo.write(line)
                    continue
                # deal with 'print'
                idx += len('print')
                if is_next_to_open_parenth(line, idx):
                    fo.write(line)
                    continue
                # need to insert parenthese
                line_out = line[:idx] + '(' + line[idx:-1] + ')' + line[-1]
                fo.write(line_out)

@click.command()
@click.argument('filepath', type=click.STRING)
def main(filepath):
    if not os.path.exists(filepath):
        click.echo(f'invalid file path: {filepath}')
        return
    correct_print(filepath)

if __name__ == '__main__':
    main()