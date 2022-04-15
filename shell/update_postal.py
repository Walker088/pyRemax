
import requests as rq
import psycopg2 as pgd
import pathlib
import yaml
import json

PY_GEO_API = "https://codigopostal.paraguay.gov.py/dinacopa/zona/geometry"

def getPgConfig() -> dict:
    crr_parent_path = pathlib.Path(__file__).parent.parent.resolve()
    with open(f"{crr_parent_path}/pyremax/pyremax/pg.conf.yml", "r") as f:
        config = yaml.safe_load(f)
        return {
            "USER": config.get("postgres").get("USER"),
            "PASS": config.get("postgres").get("PASS"),
            "NAME": config.get("postgres").get("NAME"),
            "HOST": config.get("postgres").get("HOST"),
            "PORT": config.get("postgres").get("PORT")
        }

def get_target_prop_list() -> list:
    query = 'SELECT remax_prod_id, ST_X("location"::geometry) lng, ST_Y("location"::geometry) lat FROM paraguay.remax_realestate rr WHERE rr.dpto IS NULL AND "location" IS NOT NULL'
    with conn.cursor() as curs:
        curs.execute(query)
        return [{"remax_id": r[0], "lng": r[1], "lat": r[2] } for r in curs.fetchall()]

def update_postal_info(propLst: list):
    def is_departamento_exists(postal: dict) -> bool:
        query = "SELECT 1 FROM paraguay.departamento WHERE dpto = %(dpto)s"
        with conn.cursor() as curs:
            curs.execute(query, {"dpto": postal["dpto"]})
            res = curs.fetchone()
            if res is None: return False
            else: return True

    def is_distrito_exists(postal: dict) -> bool:
        query = "SELECT 1 FROM paraguay.distrito WHERE dpto = %(dpto)s AND distrito = %(distrito)s"
        with conn.cursor() as curs:
            curs.execute(query, {"dpto": postal["dpto"], "distrito": postal["distrito"]})
            res = curs.fetchone()
            if res is None: return False
            else: return True

    def is_barrio_exists(postal: dict) -> bool:
        query = "SELECT 1 FROM paraguay.barrio WHERE dpto = %(dpto)s AND distrito = %(distrito)s AND barloc = %(barloc)s"
        with conn.cursor() as curs:
            curs.execute(query, {"dpto": postal["dpto"], "distrito": postal["distrito"], "barloc": postal["barloc"]})
            res = curs.fetchone()
            if res is None: return False
            else: return True

    for p in propLst:
        try:
            raw_postal_info = rq.get(f'{PY_GEO_API}?latitud={p["lat"]}&longitud={p["lng"]}').json()
            postal_info = {
                "dpto": raw_postal_info.get("properties").get("dpto"),
                "dpto_desc": raw_postal_info.get("properties").get("dpto_desc"),
                "distrito": raw_postal_info.get("properties").get("distrito"),
                "dist_desc": raw_postal_info.get("properties").get("dist_desc"),
                "barloc": raw_postal_info.get("properties").get("barloc"),
                "barloc_desc": raw_postal_info.get("properties").get("barloc_desc"),
                "cod_post": raw_postal_info.get("properties").get("cod_post"),
                "barrio_polygon": json.dumps(raw_postal_info.get("geometry"))
            }
            query = "UPDATE paraguay.remax_realestate SET dpto = %(dpto)s, distrito = %(distrito)s, barloc = %(barloc)s WHERE remax_prod_id = %(remax_prod_id)s"
            with conn.cursor() as curs:
                try:
                    curs.execute(query, ({"dpto": postal_info["dpto"], "distrito": postal_info["distrito"], "barloc": postal_info["barloc"], "remax_prod_id": p["remax_id"]}))
                except Exception as e:
                    print(e)
            if not is_departamento_exists(postal_info):
                query = "INSERT INTO paraguay.departamento (dpto, dpto_desc) VALUES (%(dpto)s, %(dpto_desc)s)"
                with conn.cursor() as curs:
                    try:
                        curs.execute(query, ({"dpto": postal_info["dpto"], "dpto_desc": postal_info["dpto_desc"]}))
                    except Exception as e:
                        print(e)
                        print(curs.mogrify(query, ({"dpto": postal_info["dpto"], "dpto_desc": postal_info["dpto_desc"]})))
            if not is_distrito_exists(postal_info):
                query = "INSERT INTO paraguay.distrito (dpto, distrito, dist_desc) VALUES (%(dpto)s, %(distrito)s, %(dist_desc)s)"
                with conn.cursor() as curs:
                    try:
                        curs.execute(query, ({"dpto": postal_info["dpto"], "distrito": postal_info["distrito"], "dist_desc": postal_info["dist_desc"]}))
                    except Exception as e:
                        print(e)
                        print(curs.mogrify(query, ({"dpto": postal_info["dpto"], "distrito": postal_info["distrito"], "dist_desc": postal_info["dist_desc"]})))
            if not is_barrio_exists(postal_info):
                query = "INSERT INTO paraguay.barrio (dpto, distrito, barloc, barloc_desc, cod_post, barrio_polygon) VALUES (%(dpto)s, %(distrito)s, %(barloc)s, %(barloc_desc)s, %(cod_post)s, ST_GeomFromGeoJSON(%(barrio_polygon)s))"
                with conn.cursor() as curs:
                    try:
                        curs.execute(query, ({"dpto": postal_info["dpto"], "distrito": postal_info["distrito"], "barloc": postal_info["barloc"],
                                 "barloc_desc": postal_info["barloc_desc"], "cod_post": postal_info["cod_post"], "barrio_polygon": postal_info["barrio_polygon"]}))
                    except Exception as e:
                        print(e)
                        print(curs.mogrify(query, ({"dpto": postal_info["dpto"], "distrito": postal_info["distrito"], "barloc": postal_info["barloc"],
                                "barloc_desc": postal_info["barloc_desc"], "cod_post": postal_info["cod_post"], "barrio_polygon": postal_info["barrio_polygon"]})))
        except Exception as e:
            print(e)
            continue

if __name__ == "__main__":
    try:
        pg_c = getPgConfig()
        conn = pgd.connect(
        host = pg_c.get("HOST"), 
            port=pg_c.get("PORT"),
            user=pg_c.get("USER"),
            password=pg_c.get("PASS"), 
            dbname=pg_c.get("NAME"), 
            options="-c search_path=paraguay,public"
        )
        conn.autocommit = True
        candidates = get_target_prop_list()
        update_postal_info(candidates)

    except Exception as e:
        print(e)
    finally:
        conn.close()
