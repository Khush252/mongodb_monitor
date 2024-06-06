from datetime import datetime, timedelta
import json
import csv
import config

from utils.serialize_csv import serialize_for_csv
from src.alerts import send_slack_alert
from config import SeverityLevel

#Queries slower than config.SLOWMS
def get_slow_queries(db, start_time, end_time):
    return db.system.profile.find({
        "ts": {"$gte": start_time, "$lte": end_time},
        "millis": {"$gte": config.SLOWMS}
    })


def write_to_csv(queries, columns, file_name):
    with open(file_name, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        for query in queries:
            row = {}
            for column in columns:
                keys = column.split('.')
                value = query
                for key in keys:
                    value = value.get(key, {})
                    if not isinstance(value, dict):
                        break
                row[column] = json.dumps(serialize_for_csv(value)) if isinstance(value, (dict, list)) else value
            writer.writerow(row)


SEVERITY_EMOJIS = {
    SeverityLevel.CRITICAL: "🚨",
    SeverityLevel.HIGH: "🔴",
    SeverityLevel.MEDIUM: "🟡",
    SeverityLevel.LOW: "🔵"
}

def check_thresholds(query, thresholds):
    thresholds_exceeded = []
    highest_severity = SeverityLevel.LOW

    for key, threshold in thresholds.items():
        if key == 'keysExamined=0':
            value = query.get('keysExamined', 0)
            if value == 0:
                thresholds_exceeded.append((key, True, threshold))
                highest_severity = SeverityLevel.CRITICAL
        elif key == 'docsExamined/docsReturned':
            docs_examined = query.get('docsExamined', 0)
            docs_returned = max(query.get('nReturned', 1), 1)
            value = docs_examined / docs_returned
            if value > threshold:
                thresholds_exceeded.append((key, value, threshold))
                highest_severity = update_severity(value, threshold, highest_severity)
        else:
            value = query.get(key, 0)
            if isinstance(value, dict):
                continue  # Skip comparison if the value is a dict
            if value > threshold:
                thresholds_exceeded.append((key, value, threshold))
                highest_severity = update_severity(value, threshold, highest_severity)
    
    return thresholds_exceeded, highest_severity

def update_severity(value, threshold, current_severity):
    if value > threshold * 4:
        return SeverityLevel.CRITICAL
    elif value > threshold * 3:
        return SeverityLevel.HIGH
    elif value > threshold * 2:
        return SeverityLevel.MEDIUM
    else:
        return max(current_severity, SeverityLevel.LOW, key=lambda s: s.value)

def build_alert_blocks(query, thresholds_exceeded, highest_severity):
    command_description = query.get('command', {}).get('find', 'None')
    command_filter = query.get('command', {}).get('filter', 'None')
    light_emoji = SEVERITY_EMOJIS[highest_severity]

    alert_blocks = [
        build_header_block(f"{light_emoji} MongoDB Query Profiler Alert {light_emoji}"),
        build_header_block("✨Query Details✨"),
        build_query_details_section(query),
        build_section_block(f"*Command:*\n```Find: {command_description}\nFilter: {command_filter}```"),
        build_section_block(f"*Plan Summary:* {query.get('planSummary')}"),
        build_section_block(f"*InputStage IndexBounds:* {query.get('execStats', {}).get('inputStage', {}).get('indexBounds')}"),
        build_execution_stage_section(query),
        {"type": "divider"},
        build_header_block("💥Thresholds Exceeded💥")
    ]

    for key, value, threshold in thresholds_exceeded:
        if key == 'keysExamined=0':
            alert_blocks.append(build_section_block(f"*{key}:* `True` *(COLLSCAN)*"))
        else:
            alert_blocks.append(build_section_block(f"*{key}:* `{value}` (Threshold: {threshold})"))
    
    return alert_blocks

def build_header_block(text):
    return {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": text,
            "emoji": True
        }
    }

def build_query_details_section(query):
    return {
        "type": "section",
        "fields": [
            {"type": "mrkdwn", "text": f"*Operation:*\n {query.get('op')}"},
            {"type": "mrkdwn", "text": f"*Namespace:*\n{query.get('ns')}"},
            {"type": "mrkdwn", "text": f"*Timestamp:*\n{query.get('ts')}"},
            {"type": "mrkdwn", "text": f"*Client:*\n{query.get('client')}"}
        ]
    }

def build_section_block(text):
    return {
        "type": "section",
        "text": {"type": "mrkdwn", "text": text}
    }

def build_execution_stage_section(query):
    return {
        "type": "section",
        "fields": [
            {"type": "mrkdwn", "text": f"*Execution Stage:*\n{query.get('execStats', {}).get('stage')}"},
            {"type": "mrkdwn", "text": f"*InputStage IndexName:*\n{query.get('execStats', {}).get('inputStage', {}).get('indexName')}"}
        ]
    }

def check_thresholds_and_alert(query):
    try:
        op = query.get('op')
        thresholds = config.THRESHOLDS_2 if op == 'update' else config.THRESHOLDS_1

        thresholds_exceeded, highest_severity = check_thresholds(query, thresholds)

        if thresholds_exceeded:
            alert_blocks = build_alert_blocks(query, thresholds_exceeded, highest_severity)
            send_slack_alert(alert_blocks, is_block=True)
    except Exception as e:
        error_blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"An error occurred during profiling: {str(e)}"
                }
            }
        ]
        send_slack_alert(error_blocks, is_block=True)


#profiling queries
def profile_queries(db):
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=config.PROFILING_TIME / 60.0)

    print(f"Profiling from {start_time} to {end_time}...")

    slow_queries = get_slow_queries(db, start_time, end_time)

    general_queries = []
    update_queries = []

#slow queries are those which take time more than slowms 
    for query in slow_queries:
        #checking threshold for slow queries and sending alerts 
        check_thresholds_and_alert(query)
        if query.get("op") == "update":
            update_queries.append(query)
        else:
            general_queries.append(query)

    print(f"Found {len(general_queries)} general queries and {len(update_queries)} update queries.")
#writing to CSV files
    if general_queries:
        write_to_csv(general_queries, config.GENERAL_COLUMNS, config.GENERAL_CSV_FILE)
        print(f"General queries written to {config.GENERAL_CSV_FILE}")
    else:
        print("No general queries found.")

    if update_queries:
        write_to_csv(update_queries, config.UPDATE_COLUMNS, config.UPDATE_CSV_FILE)
        print(f"Update queries written to {config.UPDATE_CSV_FILE}")
    else:
        print("No update queries found.")
