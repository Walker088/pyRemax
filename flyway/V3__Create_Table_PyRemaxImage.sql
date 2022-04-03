CREATE TABLE IF NOT EXISTS paraguay.remax_realestate_img (
    remax_prod_id TEXT NOT NULL,
    serial_number INT2 NOT NULL,
    image_path TEXT,
    creation_timestamp TIMESTAMP,
    PRIMARY KEY (remax_prod_id, serial_number)
);
