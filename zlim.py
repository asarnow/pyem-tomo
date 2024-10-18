#!/usr/bin/env python
import click
import mrcfile
import numpy as np
import sys


@click.command()
@click.argument("maskfile", required=True, type=click.Path(exists=True))
@click.option("-a", type=int, default=0)
def main(maskfile, a):
    with mrcfile.open(maskfile, permissive=True) as mrc:
        mask = mrc.data
    first = np.argmax(mask.flat)
    last = mask.size - np.argmax(mask.flat[::-1]) - 1
    zmin = np.unravel_index(first, mask.shape)[0]
    zmax = np.unravel_index(last, mask.shape)[0]
    print(f'{max(zmin - a, 0)} {min(zmax + a, mask.shape[0] - 1)}')
    return 0


if __name__ == "__main__":
    sys.exit(main())
