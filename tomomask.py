#!/usr/bin/env python
import click
import numpy as np
import mrcfile
import sys
from pyem.vop import resample_volume
from pyem.vop.binary import binary_volume_opening
from scipy.ndimage import distance_transform_edt
from scipy.ndimage import label
from scipy.ndimage import find_objects


@click.command()
@click.argument("inpfile", type=click.Path(exists=True))
@click.argument("outfile", type=click.Path())
@click.option("--extend", "-e", type=int, required=True)
@click.option("--extend-z", "-ez", type=int)
@click.option("--minvol", "-m", type=int)
@click.option("--unbin", "-ub", type=int)
def main(inpfile, outfile, extend, extend_z, minvol, unbin):
    with mrcfile.open(inpfile, permissive=True) as mrc:
        data = mrc.data
        psz = mrc.voxel_size.copy()
    data = binary_volume_opening(data, minvol)
    lb_vol, n_obj = label(data)
    lbs = np.arange(1, n_obj + 1)
    obj_slices = find_objects(lb_vol)
    if extend_z is None:
        extend_z = extend
    newvol = np.zeros(data.shape, dtype=bool)
    for lb, obj in zip(lbs, obj_slices):
        sz = slice(max(obj[0].start - extend - 1, 0),
                   min(obj[0].stop + extend + 1, data.shape[0] - 1),
                   obj[0].step)
        sy = slice(max(obj[1].start - extend - 1, 0),
                   min(obj[1].stop + extend + 1, data.shape[1] - 1),
                   obj[1].step)
        sx = slice(max(obj[2].start - extend_z - 1, 0),
                   min(obj[2].stop + extend_z + 1, data.shape[2] - 1),
                   obj[2].step)
        subvol = lb_vol[sz, sy, sx]
        submask = subvol != lb
        scale_z = extend / extend_z if extend_z > 0 else 0
        dt = distance_transform_edt(submask, sampling=[scale_z, 1, 1])
        submask = ~submask
        submask[(dt <= extend)] = True
        newvol[sz, sy, sx] |= submask
    if unbin is not None:
        newvol = resample_volume(newvol, scale=unbin, output_shape=np.array(newvol.shape) * unbin, order=0)
    with mrcfile.new(outfile, overwrite=True) as mrc:
        mrc.set_data(newvol.astype(np.float16))
        mrc.voxel_size = psz / unbin
    return 0


if __name__ == '__main__':
    sys.exit(main())
