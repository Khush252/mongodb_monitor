from datetime import datetime, timedelta
import json
import csv
import os
import signal
import sys
import uvicorn
import asyncio

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from src.alerts import send_slack_alert

from src.database import MongoDBProfiler
from src.profiling import profile_queries
# from src.queries import perform_queries

# Global variable to store the MongoDBProfiler instance
profiler = MongoDBProfiler()

# Content of post request
class Item(BaseModel):
    time: int | None = 10
    profiling: bool | None = False

app = FastAPI()

# API call for profiling
# Post request which includes time (in seconds) and profiling (True or False) information
@app.get("/")
async def status():
    return JSONResponse(content={"message": "OK"}, status_code=200)


@app.post("/profiling/")
async def profiling(item: Item, background_tasks: BackgroundTasks):
    if item.profiling:
        return start_profiling(item.time, background_tasks)  # Profiling = True 
    else:
        return end_profiling()  # Profiling = False 

def end_profiling():
    global profiler
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
    send_slack_alert(profiling_end_message, is_block=True)
    profiler.disable_profiling()  # Disable profiling
    print("Profiling disabled (through API call)")
    return {"message": "Profiling stopped."}

def start_profiling(time_in_seconds: int, background_tasks: BackgroundTasks):
    global profiler
    
    # Create folder for CSV files if it doesn't exist
    folder_name = "profiler_data"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    # Get the current timestamp for naming the files
    current_time = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    # Set the filenames with the timestamp
    general_csv_file = f"{folder_name}/general_profiler_data_{current_time}.csv"
    update_csv_file = f"{folder_name}/update_profiler_data_{current_time}.csv"
    
    # Clean CSV files (not necessary to clean as we create new files each time)
    # clean_csv_files([general_csv_file, update_csv_file])
    
    # Start profiling
    profiler.enable_profiling()
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
    send_slack_alert(profiling_start_message, is_block=True)
    
    # Add the task to run in the background
    background_tasks.add_task(run_profiling, time_in_seconds, general_csv_file, update_csv_file)
    
    return {"message": f"Profiling started for {time_in_seconds} seconds."}

async def run_profiling(time_in_seconds: int, general_csv_file: str, update_csv_file: str):
    global profiler
    db = profiler.get_database()
    try:
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(seconds=time_in_seconds)

        # Performing queries
        # perform_queries()
        
        while True:
            current_time = datetime.utcnow()
            if current_time + timedelta(seconds=5) >= end_time:
                break
            profile_queries(db, general_csv_file, update_csv_file)
            await asyncio.sleep(5)  # Wait for 5 seconds before the next profiling
            
        # Call profile_queries one last time
        profile_queries(db, general_csv_file, update_csv_file)

        # Send completion message as JSON block
        completion_message = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"❄️Profiling completed. Duration: {time_in_seconds} seconds\nFrom {start_time} - {end_time}❄️",
                    "emoji": True
                }
            }
        ]
        send_slack_alert(completion_message, is_block=True)
    except asyncio.CancelledError:
        # Handle task cancellation (e.g., due to a signal)
        profiler.disable_profiling()
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
        print("Profiling stopped because CTRL+C was pressed")
    except Exception as e:
        print("Exception caught")
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
        send_slack_alert(profiling_end_message, is_block=True)
        print("Profiling disabled (finally)")
        profiler.disable_profiling()

def handle_signal(sig, frame):
    global profiler
    profiler.disable_profiling()
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
    send_slack_alert(profiling_end_message, is_block=True)
    print("Profiling disabled")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)