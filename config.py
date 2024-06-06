import os
from dotenv import load_dotenv
from enum import Enum

class SeverityLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


load_dotenv()

SLACK_WEBHOOK_URL='https://hooks.slack.com/services/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'

#For General Queries ( except update queries)
THRESHOLDS_1 = {
    'keysExamined': 1000,         
    'docsExamined': 1000,         
    'nBatches': 500,              
    'cursorExhausted': 1,        
    'numYield': 100,            
    'nReturned': 100,             
    'locks': 50,                  
    'responseLength': 1000000,    
    'millis': 100,                
    'planningTimeMicros': 1000,  
    'execStats.inputStage.seeks': 50, 

    'docsExamined/nReturned': 1000, 
    'keysExamined=0': True 
}


#For Update Queries
THRESHOLDS_2 = {
    'keysExamined': 1000,
    'docsExamined': 1000,
    'nMatched': 100,
    'nModified': 100,
    'nUpserted': 10,
    'keysInserted': 500,
    'keysDeleted': 500,
    'numYield': 100,
    'locks': 50,
    'flowControl': 1,
    'millis': 100,
    'execStats.nReturned': 100,
    'execStats.executionTimeMillisEstimate': 100,
    'execStats.works': 1000,
    'execStats.needTime': 500,
    'execStats.saveState': 50,
    'execStats.restoreState': 50,
    'execStats.inputStage.nReturned': 100,
    'execStats.inputStage.executionTimeMillisEstimate': 100,
    'execStats.inputStage.works': 1000,
    'execStats.inputStage.advanced': 100,
    'execStats.inputStage.needTime': 500,
    'execStats.inputStage.needYield': 50,
    'execStats.inputStage.saveState': 50,
    'execStats.inputStage.restoreState': 50,
    
    'docsExamined/nReturned': 1000, 
    'keysExamined=0': True 
}

#For running locally(without docker)

MONGODB_CONNECTION_STRING = os.getenv("MONGO_DB_CONNECTION_STRING")

# For running using Docker

# DOCKER_CONNECTION_STRING = os.getenv("DOCKER_DB_CONNECTION_STRING")
# MONGODB_CONNECTION_STRING = os.getenv("DATABASE_URI", DOCKER_CONNECTION_STRING)


DATABASE_NAME = "mydatabase"
COLLECTION_NAME = "movies"

PROFILING_TIME = 20 #seconds
SLOWMS = 10 #milliseconds

GENERAL_COLUMNS = [ "op", "ns", "command", "nbatches", "cursorExhausted", "numYield",
    "keysExamined", "responseLength", "planSummary", "docsExamined",
    "nReturned", "planningTimeMicros", "execStats.Stage",
    "execStats.executionTimeMillisEstimate", "execStats.works",
    "execStats.inputStage.indexName", "execStats.inputStage.indexBounds",
    "execStats.inputStage.seek"]

UPDATE_COLUMNS = [ "op", "ns", "command", "keysExamined", "docsExamined", "nMatched", "nModified", 
    "nUpserted", "keysInserted", "keysDeleted", "numYield", "locks", "flowControl", 
    "millis", "planSummary", "execStats.stage", "execStats.executionTimeMillisEstimate", 
    "execStats.works", "execStats.needTime", "execStats.saveState", 
    "execStats.restoreState", "execStats.nMatched", "execStats.nWouldModify", 
    "execStats.nWouldUpsert"]

GENERAL_CSV_FILE = "general_profiler_data.csv"
UPDATE_CSV_FILE = "update_profiler_data.csv"



