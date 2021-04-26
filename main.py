import requests
import os
import pandas as pd
from datetime import datetime
import datetime
from sqlalchemy.orm import sessionmaker


DATABASE_LOCATION = "sqlite:///my_played_tracks.sqlite"
TOKEN= os.environ['TOKEN_SPOTIFY']

if __name__ == "__main__":
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {token}".format(token=TOKEN)
    }
    print(headers)
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=25)
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
        timestamps.append(song["played_at"][0:101])

    song_dict = {
        "song_names" : song_names,
        "artist_name": artist_names,
        "played_at_list": played_at_list,
        "timestamps": timestamps
    }

    song_df = pd.DataFrame(song_dict, columns = ["song_names","artist_name","played_at_list","timestamps"] )
    print(song_df)