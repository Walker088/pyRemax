# pyRemax

## Environment Setup
Create a file named **.proj.env** from **.proj.env.example**

## Python and Selenium Setup

```bash
$ python3 venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ sudo apt-get install firefox-geckodriver

$ python3 pyremax/runSpider.py
```

## Database setup - Postgres

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE SCHEMA IF NOT EXISTS paraguay AUTHORIZATION postgres; --modify the user name if is needed
```

```bash
$ bash migratedb.sh migrate
$ bash migratedb.sh info
```
