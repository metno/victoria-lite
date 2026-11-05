
## Victoria-lite

Minimal WMS based on [victoria-maps](https://gitlab.met.no/met/proj/magellan/victoria-maps).

This is a beta version based on a custom Victoria build. Once these changes are merged into Victoria, we can use the Victoria release images.


### Prerequisites

To run this, you will need:
- Docker and Docker Compose installed ([set up instuctions for MET internal laptops](https://it.brukerdok.met.no/klienter/linux/noble/50-installer-programvare.html#docker-og-docker-compose))

### Quickstart

- Clone the repository.

```
git clone https://github.com/metno/victoria-lite.git
```

If you are working in a country which has a preconfigured setup you need to checkout the branch for your country (we currently have setups for malawi, tanzania and vietnam):

```
git checkout <country-name>
```

If you do not have a preconfigured setup, you will have to read the instructions under "How to configure data sources" and create a configuration before proceeding.

If you want to use your own local data directory, set `VICTORIA_DATA_PATH`, e.g.

```
export VICTORIA_DATA_PATH=/absolute/path/to/your/data
```

Alternatively, you can place data in a folder `data` under victoria-lite, which will automatically be mounted into the image.

- Then, to start the server, run:

```
docker compose up
```

Or set the environment variable inline (this means it is not persisted in your local environment):

```
VICTORIA_DATA_PATH=/absolute/path/to/your/data docker compose up
```

The capabilities will then be available at:

```
http://localhost:8000/wms?service=WMS&request=GetCapabilities
```

- Paste this link into GeoWeb's layer select and click "Save". Change the service name if you like.
- In the layer select window, select the new pill with the name of the service you just added (default: "Victoria WMS").
- You should see a list of four parameters. Select the ones you want to view. The example model domain covers Malawi, so make sure you zoom to the right area to see the data.
- You can also use the `i` icon to get values at a point (currently not supported for vector layers), and use the legend to check that the style is correct.

- To remove everything so you can start from fresh, run:

```
docker compose down --volumes
```

It is a good tip to run `docker compose down --volumes` whenever your configuration or datafiles change.

### How to configure data sources

Set up a model in `config/model_config.json`. This file can contain as many different models as you like, e.g.

```
{
    "model_1": {
        ....
    },
    "model_2": {
        ....
    },
    "model_3": {
        ....
    }        
}
```

Each model can then be set up as follows.

The model key (in this case `bris-malawi`) is the name Victoria uses to identify the model, and it will be visible in GeoWeb.
```
{
    "bris-malawi": {
```
The format should be either `nc-static` for NetCDF files or `zarr-static` for Zarr stores (note that Zarr on S3 requires additional setup).
```
        "format": "nc-static",
```
`path` is the path to the data _inside the Docker container_. If the data is on your local PC or a connected network drive, you can either place it in a folder called `data/` in the directory you run `docker compose up` from, or set the `VICTORIA_DATA_PATH` environment variable to point to the folder containing the file. In both cases, the file will then be available at `/data/<my-file.nc>`.
```
        "path": "/data/20260105T00-0_025.nc",
```

Under `variables`, list the scalar variable names you would like to view from the NetCDF file.
```
        "variables": [
            "air_temperature_2m",
            "air_pressure_at_sea_level",
            "precipitation_amount_acc"
        ],
```
Vector fields (i.e., arrows or wind barbs, which have two components) have a slightly more complex setup. The key, in this case `wind_10m_vector`, is the layer name used in requests. `long_name` is used as the display name in GeoWeb. Set the `x` and `y` components to the NetCDF parameter names. You can also set unit conversion (currently scaling and offset). Here, values are scaled by `1.94384` to convert from m/s to knots.
```
        "vector_fields": {
            "wind_10m_vector": {
                "x": "x_wind_10m",
                "y": "y_wind_10m",
                "long_name": "Wind vector at 10m",
                "unit_conversion": {
                    "scale": 1.94384,
                    "offset": 0
                }
            }
        },
```
Use `layer_config` to override a layer's display title and convert its values. The layer keys should match a variable or vector field defined above. Set `"deaccumulate": true` to calculate the difference between timesteps, primarily for precipitation fields that are accumulated in NetCDF files.

```
        "layer_config": {
            "air_temperature_2m": {
                "title": "Air temperature at 2m",
                "unit_conversion": {
                    "scale": 1.0,
                    "offset": -273.15
                }
            },
            "air_pressure_at_sea_level": {
                "title": "Air pressure at sea level",
                "unit_conversion": {
                    "scale": 0.01,
                    "offset": 0.0
                }
            },
            "precipitation_amount_acc": {
                "title": "Deaccumulated precipitation amount",
                "unit_conversion": {
                    "scale": 1.0,
                    "offset": 0.0,
                    "deaccumulate": true
                }
            }
        },
```
Keywords can help when searching for layers in GeoWeb, but they are not particularly important. This can also be set to an empty list: `"keywords": []`. (This will most likely be made optional in future versions.)
```
        "keywords": [
            "bris",
            "malawi",
            "weather",
            "forecast"
        ]
    }
}
```

The full config for one model then looks something like:


```
{
    "bris-malawi": {
        "format": "nc-static",
        "path": "/data/20260105T00-0_025.nc",
        "time_config": {
            "start_time": "2026-01-05T00:00:00Z",
            "interval_hours": 6,
            "duration_hours": 240
        },
        "variables": [
            "air_temperature_2m",
            "air_pressure_at_sea_level",
            "precipitation_amount_acc"
        ],
        "vector_fields": {
            "wind_10m_vector": {
                "x": "x_wind_10m",
                "y": "y_wind_10m",
                "long_name": "Wind vector at 10m",
                "unit_conversion": {
                    "scale": 1.94384,
                    "offset": 0
                }
            }
        },
        "layer_config": {
            "air_temperature_2m": {
                "title": "Air temperature at 2m",
                "unit_conversion": {
                    "scale": 1.0,
                    "offset": -273.15
                }
            },
            "air_pressure_at_sea_level": {
                "title": "Air pressure at sea level",
                "unit_conversion": {
                    "scale": 0.01,
                    "offset": 0.0
                }
            },
            "precipitation_amount_acc": {
                "title": "Deaccumulated precipitation amount",
                "unit_conversion": {
                    "scale": 1.0,
                    "offset": 0.0,
                    "deaccumulate": true
                }
            }
        },
        "keywords": [
            "bris",
            "malawi",
            "weather",
            "forecast"
        ]
    }
}
```

Style selection is configured separately in `config/data_source_style.json`. Use the same model key as in `model_config.json`, then map each layer name to a style category defined in `config/unit_style_config.json`. Victoria can select a style based on the data's units when no category is specified; set `style_category` to choose a specific category.

```
{
    "bris-malawi": {
        "layer_styling": {
            "air_temperature_2m": {
                "style_category": "temperature_C"
            },
            "air_pressure_at_sea_level": {
                "style_category": "pressure"
            },
            "precipitation_amount_acc": {
                "style_category": "amount"
            },
            "wind_10m_vector": {
                "style_category": "wind_barb"
            }
        }
    }
}
```

The layer names must match the variables or vector fields in the model config. For another model, add a top-level entry named after that model in `data_source_style.json` as well.

### WRF NetCDF files

The NetCDF files output by the WRF model do not follow the NetCDF-CF convention, which is what Victoria currently expects. The simplest solution for now is to convert the WRF output files to CF convention. A conversion script is included in the repository. It uses `xarray` and `xwrf` for dataset conversion, and `wrf-python` to calculate mean sea-level pressure and interpolate fields to pressure levels. Create an environment with the required packages using conda:
```
$ conda create -n wrf2cf -c conda-forge python=3.12 xarray pyproj xwrf netcdf4 dask wrf-python
$ conda activate wrf2cf
```

In this environment, you can then run the Python script. WRF output is usually one NetCDF file per timestep, so you can use a wildcard `*` to select the original WRF files you wish to combine. It is important to use quotation marks when using the wildcard. Already converted files ending in `.nc` are excluded from the input set.
```
$ python convert_wrf_to_cf.py "wrfout_d01*" "<out-file-name>.nc"
```

You can then use the output NetCDF file as normal with the Victoria configuration.

Pressure-level interpolation is enabled by `INTERPOLATE_TO_PRESSURE_LEVELS = True` in the conversion script. Temperature, relative humidity, and winds are interpolated to `PRESSURE_LEVELS_HPA` (1000, 850, 700, 500, and 200 hPa); pressure-level wind vectors use `wind_east_pl` and `wind_north_pl`. Setting the switch to `False` adds temperature and relative humidity on the existing model-level `z` coordinate instead; use `wind_east` and `wind_north` for model-level wind vectors in that case. Mean sea-level pressure and the MCAPE, MCIN, LCL, and LFC diagnostics remain horizontal fields at each time.

Depending on the size of the model files, conversion can take some time and storage space. If you want to save time and/or disk space, you can adapt the conversion script to select or drop variables from the xarray dataset as needed. If you do this, make sure all relevant coordinate variables and grid mappings are kept in the resulting xarray dataset.

### Adding new styles and customising existing styles

The currently available colour palettes are defined in `config/palettes.json`. These are used by the style definitions in `config/unit_style_config.json`. Each style category contains the styles available for a layer (selectable from the style dropdown in GeoWeb). If you do not specify a style category for a layer in `data_source_style.json`, Victoria attempts to select one based on the data's units.

Each style name either matches a palette name, or contains a reference to which colour palette it uses, e.g. `"palette": "Yellow-orange"`. It then defines a list of intervals that match the number of colours in the selected palette, and options for specifying whether the style should be discrete colours or a gradient.

The simplest way to add a new style is to add it under an existing category in `unit_style_config.json`. If you want to create your own category, add the category definition there with the desired style configurations.

Try copying and adapting existing styles to see if you can get what you want. If you have problems, contact a member of the Victoria team.

### Troubleshooting

#### Layers visible in capabilities/layer select, but no data shown in GeoWeb when a layer is selected

- Check that the time step is within the model range.
- Check for any errors in the terminal log
- There may be an issue reading the projection. In that case, try adding a projection parameter in the model config, e.g. `projection: "EPSG:4326"`, where you can specify an EPSG code or proj string (use an EPSG code rather than a proj string if possible). This attempts to override the model projection. If this works, check that the projection is correctly defined in the NetCDF file.
- Check that the data values are within the ranges specified by the style palette. The legend and the `i` icon can be useful in GeoWeb for check this.
