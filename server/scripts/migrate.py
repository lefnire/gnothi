from common.database import init_db
import common.models as M
from sqlalchemy import text

def migrate_before(engine):
    engine.execute("drop table jobs;drop table jobs_status;")

def migrate_after(engine):
    pass
