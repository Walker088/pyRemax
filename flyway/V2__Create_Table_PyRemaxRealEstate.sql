
CREATE TABLE IF NOT EXISTS paraguay.remax_realestate (
    remax_prod_id TEXT NOT NULL,
    serial_number INT2 NOT NULL,
    business_type TEXT,
    prop_title TEXT,
    prop_type TEXT,
    prop_price INT4,
    currency TEXT,
    total_rooms INT2,
    bed_rooms INT2,
    bath_rooms INT2,
    living_sqm NUMERIC(12, 4),
    living_sqm_note TEXT,
    prop_link TEXT,
    location geography,
    creation_timestamp TIMESTAMP,
    PRIMARY KEY (remax_prod_id, serial_number)
);


