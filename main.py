import sqlalchemy
import pandas as pd 
from sqlalchemy.orm import sessionmaker
import requests
import urllib
import json
from datetime import datetime
import datetime
import sqlite3
import os
from dotenv import load_dotenv
load_dotenv(os.path.join("./", '.env'))
DATABASE_LOCATION = "sqlite:///my_played_tracks.sqlite"
TOKEN= os.getenv("TOKEN_SPOTIFY")
def check_if_valid_data(df: pd.DataFrame) -> bool:
    if df.empty:
        print("No songs downloaded. Finishing execution")
        return False
    if pd.Series(df['played_at']).is_unique:
       pass 
    else:
        raise Exception("Primary Key Check is violated")
    if df.isnull().values.any():
        raise Exception("Null valued found")

    # yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    # yesterday = yesterday.replace(hour=0, minute=0,second=0, microsecond=0)
    # timestamps = df["timestamp"].tolist()
    # for timestamp in timestamps:
    #     if datetime.datetime.strptime(timestamp, "%Y-%m-%d") != yesterday:
    #         raise Exception("At least one of the returned songs does not come from within the last 24 hours")
    # return True
#Get last played song
def last_played_song(headers):
    print(headers)
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=60)
    yesterday_unix_timestamp = int(yesterday.timestamp()) * 1000


    r = requests.get("https://api.spotify.com/v1/me/player/recently-played?after={time}".format(time=yesterday_unix_timestamp),headers=headers)
    data = r.json()
    song_names = []
    artist_names = []
    played_at_list = []
    timestamps = []
    print(data)
    for song in data["items"]:
        print(song["track"]["name"])
        song_names.append(song["track"]["name"])
        artist_names.append(song["track"]["album"]["artists"][0]["name"])
        played_at_list.append(song["played_at"])
        timestamps.append(song["played_at"][0:10])

    song_dict = {
        "song_name" : song_names,
        "artist_name": artist_names,
        "played_at": played_at_list,
        "timestamp": timestamps
    }

    song_df = pd.DataFrame(song_dict, columns = ["song_name","artist_name","played_at","timestamp"] )
    
    #Validate
    if check_if_valid_data(song_df):
        print("Data valid, proceed to Load stage")
    
    #Load

    engine = sqlalchemy.create_engine(DATABASE_LOCATION)
    conn = sqlite3.connect('my_played_tracks.sqlite')
    cursor = conn.cursor()

    sql_query = """
    CREATE TABLE IF NOT EXISTS my_played_tracks(
        song_name VARCHAR(200),
        artist_name VARCHAR(200),
        played_at VARCHAR(200),
        timestamp VARCHAR(200),
        CONSTRAINT primary_key_constraint PRIMARY KEY (played_at)
    ) """

    cursor.execute(sql_query)
    print("Opened database succesfully")

    try:
        song_df.to_sql("my_played_tracks", engine, index=False, if_exists='append')
    except:
        print("Data alredy exists in the database")

    conn.close()

    print("Close database successfully")

def searchSong(songname,typeSearch,headers):
    params=[('q',songname), ('type',typeSearch)]
    r = requests.get("https://api.spotify.com/v1/search",headers=headers,params=params)
    searchData =r.json()
    
    for song in searchData["tracks"]["items"]:
        print(song)
if __name__ == "__main__":
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {token}".format(token=TOKEN)
    }
    #last_played_song(headers)
    searchSong("Ride it","track",headers)

