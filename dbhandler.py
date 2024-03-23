from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from datetime import datetime
import logging

format_str = '%(asctime)s %(process)d %(message)s'
logging.basicConfig(format=format_str, level=logging.DEBUG, datefmt='%H:%M:%S')


class DbHandler:
    MONGO_CONSTR = "mongodb://admin:password@mongodb:27017/test?retryWrites=true&w=majority&authSource=admin"
    COLLECTION_NAME = 'messsages'

    def __init__(self):
        self.client = MongoClient(
            self.MONGO_CONSTR,
            server_api=ServerApi('1')
        )

        try:
            self.db = self.client.chathistory
        except Exception as e:
            print(e)
            self.db = None

        logging.debug(f'Connected to mongo')
        logging.debug(f'Collections: {self.db.list_collection_names()}')

        if self.COLLECTION_NAME not in self.db.list_collection_names():
            self.db.create_collection(self.COLLECTION_NAME, validator={
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['date', 'username', 'message'],
                    'properties': {
                        'date': {
                            'bsonType': 'string',
                        },
                        'username': {
                            'bsonType': 'string',
                        },
                        'message': {
                            'bsonType': 'string',
                        }
                    }
                }
            })

        self.collection = self.db[self.COLLECTION_NAME] if self.db is not None else None

        logging.debug(f'Collections: {self.db.list_collection_names()}')

    def __del__(self):
        if self.client is not None:
            self.client.close()

    def save_message(self, user: str, message: str) -> bool:
        try:
            logging.debug(f'Msg received: {user}: {message}')
            self.collection.insert_one({
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
                'username': user,
                'message': message
            })
            return True
        except Exception as e:
            logging.warning(f'Save message error: {e}')
            return False

    # Приймає один json документ, повертає ObjectId
    def insert_one(self, json: dict) -> ObjectId | None:
        if self.collection is None:
            return None

        try:
            return self.collection.insert_one(json).inserted_id
        except Exception as e:
            logging.warning(f'Db error: {e}')
            return None

    # Приймає один чи декілька json документів у списку, повертає список ObjectId
    def insert_many(self, json: list[dict]) -> list[ObjectId] | None:
        if self.collection is None:
            return None

        try:
            return self.collection.insert_many(json).inserted_ids
        except Exception as e:
            logging.warning(f'Db error: {e}')
            return None

    # Приймає словник фільтрів або пустий, повертає dict
    def find_one(self, json: dict = {}) -> dict | None:
        if self.collection is None:
            return None

        try:
            return self.collection.find_one(json)
        except Exception as e:
            logging.warning(f'Db error: {e}')
            return None

    # Приймає словник фільтрів або пустий, повертає список знайдених об'єктів
    def find_many(self, json: dict = {}) -> list[dict] | None:
        if self.collection is None:
            return None

        try:
            return [i for i in self.collection.find(json)]
        except Exception as e:
            logging.warning(f'Db error: {e}')
            return None

    # Приймає словник фільтрів та словник змін, повертає число оновлених об'єктів - оновлює тільки перший об'єкт
    def update_one(self, json: dict, upd: dict) -> int | None:
        if self.collection is None:
            return None

        try:
            return self.collection.update_one(json, upd).modified_count
        except Exception as e:
            logging.warning(f'Db error: {e}')
            return None

    # Приймає словник фільтрів та словник змін, повертає число оновлених об'єктів
    def update_many(self, json: dict, upd: dict) -> int | None:
        if self.collection is None:
            return None

        try:
            return self.collection.update_many(json, upd).modified_count
        except Exception as e:
            logging.warning(f'Db error: {e}')
            return None

    # Приймає словник фільтрів, повертає число видалених об'єктів - видаляє тільки перший
    def delete_one(self, json: dict) -> int | None:
        if self.collection is None:
            return None

        try:
            return self.collection.delete_one(json).deleted_count
        except Exception as e:
            logging.warning(f'Db error: {e}')
            return None

    # Приймає словник фільтрів, повертає число видалених об'єктів
    def delete_many(self, json: dict = {}) -> int | None:
        if self.collection is None:
            return None

        try:
            return self.collection.delete_many(json).deleted_count
        except Exception as e:
            logging.warning(f'Db error: {e}')
            return None


if __name__ == "__main__":
    db = DbHandler()
    db.save_message('user1', 'message1')
    logging.debug(db.find_one({'user': 'user1'}))
