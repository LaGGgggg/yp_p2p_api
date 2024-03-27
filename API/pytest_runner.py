from os import environ
from sys import argv


environ['IS_TEST'] = 'True'


# imports must be here because we must set environment variables before importing API modules
# (this causes settings setup)
from subprocess import run

from sql.database import SessionLocal
from sql.models import Base


with SessionLocal() as db:

    for table in reversed(Base.metadata.tables.values()):
        db.query(table).delete()

    db.commit()

run('alembic upgrade head', shell=True)
run(f"python -m pytest {' '.join(argv[1:])}", shell=True)