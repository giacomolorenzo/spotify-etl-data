import requests
import os
import pandas as pd
from datetime import datetime
import datetime
from sqlalchemy.orm import sessionmaker


DATABASE_LOCATION = "sqlite:///my_played_tracks.sqlite"
TOKEN= os.environ['TOKEN_SPOTIFY']
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

    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    yesterday = yesterday.replace(hour=0, minute=0,second=0, microsecond=0)
    timestamps = df["timestamp"].tolist()
    for timestamp in timestamps:
        if datetime.datetime.strptime(timestamp, "%Y-%m-%d") != yesterday:
            raise Exception("At least one of the returned songs does not come from within the last 24 hours")
    return True
if __name__ == "__main__":
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {token}".format(token=TOKEN)
    }
    print(headers)
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
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
        "song_names" : song_names,
        "artist_name": artist_names,
        "played_at": played_at_list,
        "timestamp": timestamps
    }

    song_df = pd.DataFrame(song_dict, columns = ["song_names","artist_name","played_at","timestamp"] )
    
    #Validate
    if check_if_valid_data(song_df):
        print("Data valid, proceed to Load stage")
    