import peewee
from models import Chat, ChatMember, UnregisteredMember


def create_tables_if_not_exist(database: peewee.SqliteDatabase):
    tables = [
        Chat,
        ChatMember,
        UnregisteredMember
    ]

    database.create_tables(tables)
    database.commit()
