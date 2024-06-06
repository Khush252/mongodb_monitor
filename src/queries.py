from datetime import datetime
import random
import config
from src.database import get_database

#runtime -> 538 - 1793
#year ->1914 - 2014
genres = ['Biography','Crime','Drama','Comedy','Short','Action','Romance','Thriller','War','Musical','Western','Adventure','Animation','Comedy','Family','Fantasy','History','Mystery','Sci-Fi','Sport']
#imdb.rating -> 1.6 to 9.6   
#imdb.votes -> 5 to 1521105 


def perform_queries():
    db = get_database()
    collection = db[config.COLLECTION_NAME]

    queries = [

        ("Simple query (genres)", {"genres": random.choice(genres)}),
        ("Full collection scan", {}),
        ("Aggregation query", [
            {"$match": {"year": {"$gte": random.randint(1914,2014)}}},
            {"$group": {"_id": "$year", "average_rating": {"$avg": "$imdb.rating"}, "count": {"$sum": 1}}},
            {"$sort": {"average_rating": -1}},
            {"$limit": 10}
        ]),
        ("Text search query", {"$text": {"$search": "love"}}),
        ("Complex query with sorting", {"genres": random.choice(genres)}, [("title", 1)]),
        ("Regex query", {"title": {"$regex": ".*love.*"}}),
        ("Simple query (year)", {"year": random.randint(1914,2014)}),
        ("Complex query (year and genres)", {"year": {"$lt": random.randint(1914,2014)}, "genres": {"$in": [ random.choice(genres) ]}}),
        ("Aggregation query (average rating by year)", [
            {"$group": {"_id": "$year", "average_rating": {"$avg": "$imdb.rating"}}},
            {"$sort": {"_id": 1,"runtime":1}}
        ]),
        ("Text search query (plot contains 'love')", {"$text": {"$search": "love"}}),
        ("Complex query (multiple criteria and sorting)", {
            "year": {"$gte": random.randint(1914,2014)},
            "genres": random.choice(genres),
            "imdb.rating": {"$gte": random.uniform(1.6,9.6)},
            "imdb.votes" : {"$gt":random.randint(5,1521105)}
        }, [("imdb.rating", -1)]),
        ("Regex query (titles starting with 'H')", {"title": {"$regex": "^H"}}),
        ("Create operation (insert new movie)", {
            "title": "New Movie2",
            "year": random.randint(1914,2014),
            "genres": random.choice(genres),
            "runtime": random.randint(538,1793),
            "cast": ["Actor A2", "Actor B2"],
            "imdb": {"rating":random.uniform(1.6,9.6), "votes": random.randint(5,1521105)},
            "languages": ["English"],
            "released": datetime.utcnow(),
            "directors": ["Director X1"],
            "awards": {"wins": 1, "nominations": 2, "text": "1 win & 2 nominations."},
        }, "insert"),
        ("Read operation (find by runtime)", {"runtime":random.randint(538,1793)}),
        ("Update operation (increment runtime)", {"runtime": {"$exists": True}}, {"$inc": {"runtime": random.randint(1,8)}}, "update_many"),
        ("Delete operation (remove old movie)", {"year": {"$lt": random.randint(1914,2014)}}, "delete_one")
    ]
#Performing Query Operations
    for description, query, *args in queries:
        start_time = datetime.utcnow()
        if description.startswith("Aggregation"):
            result = list(collection.aggregate(query))
        elif description.startswith("Create"):
            result = collection.insert_one(query)
        elif description.startswith("Update"):
            result = collection.update_many(query, args[0])
        elif description.startswith("Delete"):
            result = collection.delete_one(query)
        else:
            result = list(collection.find(query))
        end_time = datetime.utcnow()
        print(f"{description}: {end_time - start_time}")
        print(f"Result count: {len(result) if isinstance(result, list) else 'N/A'}")