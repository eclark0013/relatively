""" 
Goal:
For a given user (SUBJECT): 
    For each other user:
        Fetch the ratings corresponding to movies that they and SUBJECT both rated (co-rated)
        Loop over those movies to find the ones they gave the same rating (equal-rated)
        Give their compatability with SUBJECT as a percentage of (equal-rated/co-rated)
        Find the user with highest compatability score for SUBJECT
"""
import pandas as pd
from dotenv import load_dotenv
import os
import psycopg2

# Load .env file
load_dotenv()

# Get database credentials from environment variables
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)

cur = conn.cursor()

# Get a list of all users that have given a rating and are not SUBJECT
cur.execute("SELECT DISTINCT user_id FROM ratings WHERE user_id != 1 ORDER BY user_id;")
user_ids = [row[0] for row in cur.fetchall()]

# Create an empty list to store results
data = []

# Loop through each user and fetch the movie_id's where they both gave a rating (corated)
for user_id in user_ids:
    cur.execute(""" 
    SELECT 
        r1.movie_id         
        FROM ratings r1 JOIN ratings r2 ON r1.movie_id = r2.movie_id
        WHERE r1.user_id = 1 AND r2.user_id = %s;                
     """, (user_id,)) 
    
    corated_movie_ids = [row[0] for row in cur.fetchall()]
    corated_count = len(corated_movie_ids)

    data.append((user_id, corated_count, corated_movie_ids))

# Run SQL query and store result in a DataFrame
# query = "SELECT DISTINCT user_id, AVG(rating) FROM ratings GROUP BY user_id LIMIT 5;"
# df = pd.read_sql(query, conn)

df = pd.DataFrame(data, columns=["user_id", "co_rated_count", "co_rated_movies"])

# Display the table
print(df)

# Close the connection
cur.close()
conn.close()