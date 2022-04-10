
import psycopg2 as pgd
import yaml

def getPgConfig() -> dict:
    with open("pyremax/pyremax/pg.conf.yml", "r") as f:
        config = yaml.safe_load(f)
        return {
            "USER": config.get("postgres").get("USER"),
            "PASS": config.get("postgres").get("PASS"),
            "NAME": config.get("postgres").get("NAME"),
            "HOST": config.get("postgres").get("HOST"),
            "PORT": config.get("postgres").get("PORT")
        }


pg_c = getPgConfig()
conn = pgd.connect(
    host=pg_c.get("HOST"), port=pg_c.get("PORT"), user=pg_c.get("USER"),
    password=pg_c.get("PASS"), dbname=pg_c.get("NAME"), options="-c search_path=paraguay,public"
)
conn.autocommit = True
