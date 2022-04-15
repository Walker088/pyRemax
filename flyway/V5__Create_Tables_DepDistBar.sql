ALTER TABLE paraguay.remax_realestate ADD COLUMN dpto TEXT;
ALTER TABLE paraguay.remax_realestate ADD COLUMN distrito TEXT;
ALTER TABLE paraguay.remax_realestate ADD COLUMN barloc TEXT;

CREATE TABLE IF NOT EXISTS paraguay.departamento (
    dpto TEXT NOT NULL,
    dpto_desc TEXT,
    PRIMARY KEY (dpto)
);

CREATE TABLE IF NOT EXISTS paraguay.distrito (
    dpto TEXT NOT NULL,
    distrito TEXT NOT NULL,
    dist_desc TEXT,
    PRIMARY KEY (dpto, distrito)
);

CREATE TABLE IF NOT EXISTS paraguay.barrio (
    dpto TEXT NOT NULL,
    distrito TEXT NOT NULL,
    barloc TEXT,
    barloc_desc TEXT,
    cod_post TEXT,
    barrio_polygon geometry(MultiPolygon, 4326),
    PRIMARY KEY (dpto, distrito, barloc)
);
