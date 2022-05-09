# Anime Recommendation System

## Server

Download and unpack data:
```
kaggle datasets download -d hernan4444/anime-recommendation-database-2020
unzip anime-recommendation-database-2020.zip
```

Start server with command: `python server.py < server.txt`

## Client

Interfaces: HTTP, Android application.

Example of HTTP request with curl: `curl -X POST -d 'Girls & Panzer;Shaman King;Death Note' localhost:8080`

Copy `server/anime_titles.txt` to `.../res/raw` for anime title suggestions inside Android application

Security and network warning for Android application: server address is set up to localhost with security check bypass, do not use server and application in real production
