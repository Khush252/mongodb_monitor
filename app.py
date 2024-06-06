import signal
import sys
import uvicorn
import asyncio

from fastapi import FastAPI, BackgroundTasks
from datetime import datetime
from pydantic import BaseModel
from src.database import get_database, enable_profiling, disable_profiling
from src.profiling import profile_queries
from src.queries import perform_queries
from src.alerts import send_slack_alert

# Global variable to store the database connection
db = None

#content of post request
class Item(BaseModel):
    time: int | None = 10
    profiling: bool | None = False

app = FastAPI()

#Api call for profiling
#Post request which includes time(in seconds) and profiling(True or False) information
@app.post("/profiling/")

async def profiling(item: Item, background_tasks: BackgroundTasks):
    if item.profiling:
        return start_profiling(item.time, background_tasks) #Profiling = True 
    else:
        return end_profiling()   #Profiling  = False 


def end_profiling():
    global db
    if db is None:
        db = get_database() #Get database
    profiling_end_message = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"❄️Profiling Disabled❄️",
                "emoji": True
            }
        }
    ]
    
    # Send acknowledgment message
    send_slack_alert(profiling_end_message,is_block=True)   
    disable_profiling(db)  #Disable profiling
    print("Profiling disabled( through api call)")
    return {"message": "Profiling stopped."}

def start_profiling(time_in_seconds: int, background_tasks: BackgroundTasks):
    global db
    db = get_database()
    
    # Start profiling
    enable_profiling(db) 
    profiling_start_message = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"⭐️⭐️⭐️Profiling Started for Duration: {time_in_seconds} seconds⭐️⭐️⭐️",
                "emoji": True
            }
        }
    ]
    
    # Send acknowledgment message
    send_slack_alert(profiling_start_message,is_block=True)   
    
    # Add the task to run in the background
    background_tasks.add_task(run_profiling, time_in_seconds, db)
    
    
    return {"message": f"Profiling started for {time_in_seconds} seconds."}

async def run_profiling(time_in_seconds: int, db):
    try:
        start_time = datetime.utcnow()
        #performing queries
        perform_queries()
        #profiling queries
        profile_queries(db)
        
        # Wait for the specified duration using asyncio.sleep
        await asyncio.sleep(time_in_seconds)
        
        end_time = datetime.utcnow()
        # Send completion message as JSON block
        completion_message = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Profiling completed. Duration: {time_in_seconds} seconds\nFrom {start_time} - {end_time} ",
                    "emoji": True
                }
            }
        ]
        send_slack_alert(completion_message, is_block=True)
    except asyncio.CancelledError:
        # Handle task cancellation (e.g., due to a signal)
        disable_profiling(db)
        cancel_message = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Profiling was stopped prematurely."
                }
            }
        ]
        send_slack_alert(cancel_message, is_block=True)
        print("Profiling stopped because CTRL+C is pressed")
    except Exception as e:
        print("exception caught")
        error_message = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"An error occurred during profiling: {e}"
                }
            }
        ]
        send_slack_alert(error_message, is_block=True)
    finally:
        # Ensure the profiler is disabled
        print("profiling disabled (finally)")
        disable_profiling(db)


def handle_signal(sig, frame):
    global db
    if db is not None:
        disable_profiling(db)
        print("Profiling disabled")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
