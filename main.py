
from src.database import get_database, enable_profiling, disable_profiling
from src.profiling import profile_queries
from src.queries import perform_queries


def main():
    db = get_database()

    # Enable profiling
    enable_profiling(db)
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
    disable_profiling(db)
    print("Profiling disabled.")

if __name__ == "__main__":
    main()
