import peewee
from models import Chat, ChatMember


def create_tables_if_not_exist(database: peewee.SqliteDatabase):
    tables = [
        Chat,
        ChatMember, 
    ]

    database.create_tables(tables)
    database.commit()
