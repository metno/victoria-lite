db.getSiblingDB('admin').auth(
    process.env.MONGO_INITDB_ROOT_USERNAME,
    process.env.MONGO_INITDB_ROOT_PASSWORD
);

db = db.getSiblingDB('status');

db.createUser({ user: process.env.MONGO_USER, pwd: process.env.MONGO_PASSWORD, roles: [{ role: "readWrite", db: "status" }, { role: "readWrite", db: "zarr_metadata" }, { role: "readWrite", db: "volcanoes" }, { role: "readWrite", db: "gdal_metadata" }, { role: "readWrite", db: "unit_styles" }, { role: "readWrite", db: "palette_and_unit" }, { role: "readWrite", db: "data_source_styles" }, { role: "readWrite", db: "drifty_style" }] });
