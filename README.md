# Anime Recommendation System

## Recommendation systems

 - System based on distance between users (distances: cosine, TBA)
 - Implicit ALS recommendation (only x86 arch., cold start with high computation cost)

Training data is converted from ratings to binary with rating threshold.

## HTTP Server

Download and unpack data:
```
kaggle datasets download -d hernan4444/anime-recommendation-database-2020
unzip anime-recommendation-database-2020.zip
```

Start server with command: `python server.py < server.txt`

## Client

Interfaces: HTTP requests, Android application.

Example of HTTP request with curl: `curl -X POST -d 'Girls & Panzer;Shaman King;Death Note' localhost:8080`

Copy `server/anime_titles.txt` to `{ANDROID_APP_PREFIX}/res/raw` for anime title suggestions inside Android application

Security and network warning for Android application: server address is set up to localhost with security check bypass, do not use server and application in production
