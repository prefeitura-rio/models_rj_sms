import sqlite3
import pysqlite3
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from fastapi import FastAPI

from app.api import router
from app.config import API_PREFIX, PROJECT_NAME, VERSION


def get_application() -> FastAPI:
    application = FastAPI(title=PROJECT_NAME, version=VERSION)
    application.include_router(router, prefix=API_PREFIX)

    return application


app = get_application()
