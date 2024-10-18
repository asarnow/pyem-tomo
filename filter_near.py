#!/usr/bin/env python
import mrcfile
import numpy as np
import starfile
import click
import sys
from scipy.ndimage import distance_transform_edt
from pyem.star import Relion
from pyem.vop import binary_volume_opening


def extract_particle_distance(df, dt):
    pd = df.apply(lambda x: dt[int(np.round(x[Relion.COORDZ])),
                               int(np.round(x[Relion.COORDY])),
                               int(np.round(x[Relion.COORDX]))], axis=1)
    return pd


@click.command()
@click.option('--mask', '-m', required=True, type=click.Path(exists=True),
              help='Binary tomogram mask (.mrc) to pick near')
@click.option('--particles', '-p', required=True, type=click.Path(exists=True),
              help='Path to the input particles (.star)')
@click.option('--output', '-o', required=True, type=click.Path(),
              help='Path to save the output filtered particles (.star or .pos)')
@click.option('--threshold', '-t', required=True, type=float,
              help='Distance threshold for rejecting particles')
@click.option('--threshold-z', '-tz', type=float,
              help='Separate distance threshold along Z')
@click.option("--minvol", type=int, default=0)
def main(mask, particles, output, threshold, threshold_z, minvol):
    """
    Command line tool to reject particle picks from a .star file based on proximity to binary tomogram masks in a directory.
    """
    star_data = starfile.read(particles, always_dict=True)
    with mrcfile.open(mask, permissive=True) as mrc:
        mask = mrc.data
    if minvol != 0:
        mask = binary_volume_opening(mask, minvol)
    dt = distance_transform_edt(1 - mask)
    pd = extract_particle_distance(star_data['particles'], dt)
    accepted = pd <= threshold
    if threshold_z is not None:
        dt_z = distance_transform_edt(1 - mask, sampling=[1, 0, 0])
        pd_z = extract_particle_distance(star_data['particles'], dt_z)
        accepted &= pd_z <= threshold_z
    star_data['particles'] = star_data['particles'].loc[accepted]
    if output.endswith('.pos'):
        star_data['particles'][Relion.COORDS3D].to_csv(output, header=None, index=False, sep=" ")
    else:
        starfile.write(star_data, output)
    return 0


if __name__ == '__main__':
    sys.exit(main())
