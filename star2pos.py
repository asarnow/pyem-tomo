#!/usr/bin/env python
import click
import pathlib
import starfile
import subprocess
import sys


@click.command()
@click.argument('starpath', type=click.Path(exists=True, path_type=pathlib.Path))
@click.argument('out', type=click.Path(path_type=pathlib.Path))
@click.option('--write-mod', '-m', type=bool, default=False)
@click.option('--sphere', '-sp', type=int, default=6)
@click.option('--circle', '-ci', type=int, default=3)
def main(starpath, out, write_mod, sphere, circle):
    star_tables = starfile.read(starpath, always_dict=True)
    df = star_tables['particles']
    for k in ['rlnTomoName', 'rlnMicrographName']:
        if k in df.columns:
            break
    gb = df.groupby(k)
    for n, g in gb:
        fn = out / f'{n}.pos'
        g.to_csv(fn, index=False, header=False, sep='\t')
        if write_mod:
            subprocess.run(f'point2model -sc -sp {sphere} -ci {circle} {fn} {fn[:-4] + ".mod"}', shell=True)


if __name__ == '__main__':
    sys.exit(main())
