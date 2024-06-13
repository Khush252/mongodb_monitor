from pymongo import MongoClient
import config

class MongoDBProfiler:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.client = MongoClient(config.MONGODB_CONNECTION_STRING)
        self.db = self.client[config.DATABASE_NAME]
        self._initialized = True

    def enable_profiling(self):
        self.db.command("profile", 1, slowms=config.SLOWMS)
        print(f"Profiling enabled with slowms set to {config.SLOWMS} ms")

    def disable_profiling(self):
        self.db.command("profile", 0)
        print("Profiling disabled")

    def get_database(self):
        return self.db
