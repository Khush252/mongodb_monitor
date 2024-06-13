from pymongo import MongoClient
import config

class MongoDBProfiler:
    def __init__(self):
        self.client = MongoClient(config.MONGODB_CONNECTION_STRING)
        self.db = self.client[config.DATABASE_NAME]

    def enable_profiling(self):
        self.db.command("profile", 1, slowms=config.SLOWMS)
        print(f"Profiling enabled with slowms set to {config.SLOWMS} ms")

    def disable_profiling(self):
        self.db.command("profile", 0)
        print("Profiling disabled")

    def get_database(self):
        return self.db
