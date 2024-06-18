
from src.database import MongoDBProfiler
from src.profiling import profile_queries
from src.queries import perform_queries


def main():
    profiler = MongoDBProfiler()

    db = profiler.get_database()

    # Enable profiling
    profiler.enable_profiling()
    print("Profiling enabled.")

    # Perform queries
    perform_queries()

#----------------------------------------------------------------TESTING----------------------------------------------------------------
    # print("*******************************||||| Sleeping for 3 seconds ||||||********************************")
    # time.sleep(3)
    # perform_queries()
    # print("*******************************||||| Sleeping for 3 seconds ||||||********************************")
    # time.sleep(3)
    # perform_queries()
    # print("Queries performed. Sleeping to capture any additional manual queries...")
    # time.sleep(config.PROFILING_TIME)
#----------------------------------------------------------------TESTING----------------------------------------------------------------
    
    # Profile the queries
    profile_queries(db)

    # Disable profiling
    profiler.disable_profiling()
    print("Profiling disabled.")

if __name__ == "__main__":
    main()
