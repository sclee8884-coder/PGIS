CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS pgis_assets (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    zone TEXT,
    description TEXT,
    tags TEXT,
    route_ids TEXT,
    source TEXT,
    geom geometry(Point, 4326) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS pgis_assets_geom_idx
    ON pgis_assets
    USING GIST (geom);

CREATE INDEX IF NOT EXISTS pgis_assets_type_idx
    ON pgis_assets (type);
