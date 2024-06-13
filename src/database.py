from pymongo import MongoClient
import config


#getting database - function 
def get_database():
    client=MongoClient(config.MONGODB_CONNECTION_STRING)
    return client[config.DATABASE_NAME]

def enable_profiling(db):
    db.command("profile",1,slowms=config.SLOWMS)

def disable_profiling(db):
    db.command("profile",0)

    



