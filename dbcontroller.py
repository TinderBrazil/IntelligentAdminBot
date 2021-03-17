import sqlite3
from models import Chat


class DBController:
    def __init__(self, filename):
        self.connection = sqlite3.connect(filename)
        self.cursor = self.connection.cursor()

    def create_chat(self, chat_id):
        chat = Chat(chat_id, 0, False, ['+'])
        self.cursor.execute(f'INSERT INTO Chats VALUES("{chat.chat_id}", "{chat.total_messages}")')
        self.cursor.execute(f'INSERT INTO RPTriggers VALUES({chat.chat_id}, "+")')
        self.connection.commit()
        return chat

    def get_chat(self, chat_id):
        data = self.cursor.execute(f"SELECT * FROM Chats WHERE chat_id = '{chat_id}'")
        if not data:
            return self.create_chat(chat_id)

    def get_user(self, chat_id):
        pass
