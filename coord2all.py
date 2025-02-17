#!/usr/bin/env python
import click
import pandas as pd
import pathlib
import starfile
import subprocess
import sys
from pyem.star import Relion


@click.command()
@click.argument('starpath', type=click.Path(exists=True, path_type=pathlib.Path))
@click.argument('out', type=click.Path(path_type=pathlib.Path))
@click.option('--write-mod', '-m', is_flag=True, default=False)
@click.option('--sphere', '-sp', type=int, default=6)
@click.option('--circle', '-ci', type=int, default=3)
def main(starpath, out, write_mod, sphere, circle):
    if starpath.suffix == '.star':
        star_tables = starfile.read(starpath, always_dict=True)
        df = star_tables['particles']
    elif starpath.suffix == '.txt':
        df = pd.read_csv(starpath, sep='\s+')
        df.rename(columns={'image_name': 'rlnTomoName',
                            'x_coord': 'rlnCoordinateX',
                            'y_coord': 'rlnCoordinateY',
                            'z_coord': 'rlnCoordinateZ'},
                  inplace=True)
        df[Relion.DETECTORPIXELSIZE] = 10.5408
        df[Relion.MAGNIFICATION] = 10000
        df[Relion.CS] = 2.7
        df[Relion.VOLTAGE] = 300
        df[Relion.AC] = 0.07
        starfile.write(df, starpath.with_suffix('.star'))
    else:
        return 1
    for k in ['rlnTomoName', 'rlnMicrographName']:
        if k in df.columns:
            break
    gb = df.groupby(k)
    for n, g in gb:
        fn = out / f'{n}.pos'
        g[Relion.COORDS3D].to_csv(fn, index=False, header=False, sep='\t')
        if write_mod:
            subprocess.run(f'point2model -sc -sp {sphere} -ci {circle} {fn} {fn.with_suffix(".mod")}', shell=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
