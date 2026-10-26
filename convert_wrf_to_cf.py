"""
Simple script for converting WRF output to CF-compliant NetCDF files.

You need a python environment with xarray, xwrf, and wrf-python installed.

$ conda create -n wrf2cf -c conda-forge python=3.12 xarray pyproj xwrf \
    netcdf4 dask wrf-python
$ conda activate wrf2cf
# Keep the input glob quoted so xarray, not the shell, expands it.
$ python convert_wrf_to_cf.py "wrfout_d01*" "out.nc"

"""

import argparse
from contextlib import ExitStack
from glob import glob
from pathlib import Path

import numpy as np
import xarray as xr
import xwrf  # noqa: F401
from netCDF4 import Dataset
from wrf import ALL_TIMES, getvar, interplevel

PRESSURE_LEVELS_HPA = [1000, 850, 700, 500, 200]
INTERPOLATE_TO_PRESSURE_LEVELS = True


def convert_wrf_to_cf(wrf_files_pattern: str, output_file: str):
    """
    Convert WRF output files to a single CF-compliant NetCDF file.

    Parameters:
    - wrf_files_pattern: A glob pattern to match the WRF output files (e.g., "wrfout_d01*").
    - output_file: The name of the output NetCDF file (e.g., "wrfout_cf_all_times.nc").
    """
    print(
        f"Converting WRF files matching pattern '{wrf_files_pattern}' to CF-compliant NetCDF file '{output_file}'. \n"
        "This may take a while depending on the size of the WRF output files..."
    )

    output_path = Path(output_file).resolve()
    wrf_files = sorted(
        path
        for path in glob(wrf_files_pattern)
        if Path(path).resolve() != output_path and not Path(path).name.endswith(".nc")
    )
    if not wrf_files:
        raise FileNotFoundError(f"No WRF files match pattern: {wrf_files_pattern}")

    with ExitStack() as stack:
        wrfin = [stack.enter_context(Dataset(path)) for path in wrf_files]
        # calculate MSLP
        slp = getvar(
            wrfin, "slp", timeidx=ALL_TIMES, method="cat", squeeze=False
        ).values
        # calculate most-unstable CAPE
        cape_2d = getvar(
            wrfin, "cape_2d", timeidx=ALL_TIMES, method="cat", squeeze=False
        ).values
        fields = {
            # calculate air temperature and relative humidity at model levels
            "air_temperature": getvar(
                wrfin, "tk", timeidx=ALL_TIMES, method="cat", squeeze=False
            ),
            "relative_humidity": getvar(
                wrfin, "rh", timeidx=ALL_TIMES, method="cat", squeeze=False
            ),
        }

    ds = xr.open_mfdataset(
        wrf_files, engine="netcdf4", concat_dim="Time", combine="nested"
    ).xwrf.postprocess()
    if INTERPOLATE_TO_PRESSURE_LEVELS:
        fields["wind_east_pl"] = ds["wind_east"]
        fields["wind_north_pl"] = ds["wind_north"]
        vertical_dimension = "pressure"
        vertical_coordinate = PRESSURE_LEVELS_HPA
    else:
        vertical_dimension = "z"
        vertical_coordinate = ds["z"]

    field_metadata = {
        "air_temperature": ("Air temperature", "K"),
        "relative_humidity": ("Relative humidity", "%"),
        "wind_east_pl": ("Eastward wind", "m s-1"),
        "wind_north_pl": ("Northward wind", "m s-1"),
    }
    for name, field in fields.items():
        if INTERPOLATE_TO_PRESSURE_LEVELS:
            values = np.asarray(
                interplevel(
                    field.values,
                    ds["air_pressure"].values / 100.0,
                    PRESSURE_LEVELS_HPA,
                    missing=np.nan,
                    squeeze=False,
                )
            )
        else:
            values = field.values
        long_name, units = field_metadata[name]
        ds[name] = xr.DataArray(
            values,
            dims=("Time", vertical_dimension, "y", "x"),
            coords={
                "Time": ds["Time"],
                vertical_dimension: vertical_coordinate,
                "y": ds["y"],
                "x": ds["x"],
            },
            attrs={
                "standard_name": {
                    "wind_east_pl": "eastward_wind",
                    "wind_north_pl": "northward_wind",
                }.get(name, name),
                "long_name": long_name,
                "units": units,
                "grid_mapping": "wrf_projection",
            },
        )

    if INTERPOLATE_TO_PRESSURE_LEVELS:
        ds["pressure"].attrs.update(
            standard_name="air_pressure",
            long_name="Pressure level",
            units="hPa",
            positive="down",
            axis="Z",
        )
    ds["air_pressure_at_mean_sea_level"] = xr.DataArray(
        slp,
        dims=("Time", "y", "x"),
        coords={"Time": ds["Time"], "y": ds["y"], "x": ds["x"]},
        attrs={
            "standard_name": "air_pressure_at_mean_sea_level",
            "long_name": "Mean sea-level pressure",
            "units": "hPa",
            "grid_mapping": "wrf_projection",
        },
    )
    for index, name, long_name, units in (
        (
            0,
            "mcape",
            "Most-unstable convective available potential energy",
            "J kg-1",
        ),
        (1, "mcin", "Most-unstable convective inhibition", "J kg-1"),
        (2, "lcl", "Lifted condensation level height", "m"),
        (3, "lfc", "Level of free convection height", "m"),
    ):
        ds[name] = xr.DataArray(
            cape_2d[index],
            dims=("Time", "y", "x"),
            coords={"Time": ds["Time"], "y": ds["y"], "x": ds["x"]},
            attrs={
                "long_name": long_name,
                "units": units,
                "grid_mapping": "wrf_projection",
            },
        )

    ds["wrf_projection"].data = np.full(ds["wrf_projection"].shape, np.nan)

    ds.to_netcdf(output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert WRF output to CF-compliant NetCDF."
    )
    parser.add_argument(
        "wrf_files_pattern",
        type=str,
        help="A glob pattern to match the WRF output files (e.g., 'wrfout_d01*').",
    )
    parser.add_argument(
        "output_file",
        type=str,
        help="The name of the output NetCDF file (e.g., 'wrfout_cf_all_times.nc').",
    )
    args = parser.parse_args()

    convert_wrf_to_cf(args.wrf_files_pattern, args.output_file)
