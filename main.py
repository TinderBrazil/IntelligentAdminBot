import asyncio
import settings
import logging

from peewee import SqliteDatabase
from utils import create_tables_if_not_exist
from bot import dp

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    db = SqliteDatabase(settings.DB_FILENAME)
    db.connect()  # connect to database

    create_tables_if_not_exist(db)  # create tables

    loop = asyncio.get_event_loop()
    loop.create_task(dp.start_polling())
    loop.run_forever()
