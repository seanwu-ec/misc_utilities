#!/usr/bin/env python3.7
import click
import subprocess
from collections import namedtuple
import re

PrDesc = namedtuple('PrDesc', [
   'num',
   'title',
   'branch',
   'status'
])

def print_list(l):
    for i in l:
        click.echo(f'  {i}')

def run_cmd(args):
    ret = subprocess.run(args, capture_output=True)
    if ret.returncode != 0:
        raise RuntimeError(f'Cmd: {args} failed, ret={ret.returncode})')
    return ret.stdout.decode('utf-8', errors='replace').splitlines()

class PrReader():
    @staticmethod
    def list_all():
        ''' return a list of (opened) PR'''
        lines = run_cmd(['gh', 'pr', 'list', '-L', '800'])
        prs = []
        for l in lines:
            words = l.split('\t')
            if words[3] == 'OPEN':
                prs.append(PrDesc(words[0], words[1], words[2], words[3]))
        return prs

    @staticmethod
    def list_mod_files_by_pr(num):
        '''list all modified files by given PR num(type:str)'''
        diff = run_cmd(['gh', 'pr', 'diff', num])
        file_lines = [l for l in diff if l.startswith('diff --git')]
        files = [l.split()[2][2:] for l in file_lines] # drop first two chars 'a/'
        return files

@click.command()
@click.argument('regex_patt', type=click.STRING)
def main(regex_patt):
    '''
    Output PR-Files hierarchy while the PR has matched files with the given
    regex_pattern.\n
    NOTE: This script is using github cli cmd `gh` to achieve our goal. So,
    before using this script, please follow the instruction at
    https://cli.github.com/ install it, and finish all token and repo setup
    until `gh pr list` can list PRs of your target repo.
    '''
    prs = PrReader.list_all()
    click.echo(f'Total {len(prs)} PRs, start grepping...')
    for pr in prs:
        files = PrReader.list_mod_files_by_pr(pr.num)
        matches = [f for f in files if re.search(regex_patt, f)]
        if matches:
            click.echo(f'==== {pr.num}: {pr.title} ====')
            print_list(matches)

if __name__ == "__main__":
    main()