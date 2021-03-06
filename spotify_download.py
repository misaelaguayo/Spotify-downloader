from __future__ import unicode_literals
import sys
import spotipy
import spotipy.util as util
from apiclient.discovery import build
from apiclient.errors import HttpError
import os
import urllib
import youtube_dl

### tries to read API keys from text file if it exists, if not asks for info and creates file in directory
try:
	API_file = open("API_file.txt","r")
	spotifyUsername = API_file.readline().rstrip()
	spotifyClientID = API_file.readline().rstrip()
	spotifyClientSecret = API_file.readline().rstrip()
	youtubeAPIKey = API_file.readline().rstrip()
	path = API_file.readline().rstrip()
	API_file.close()
	
except(FileNotFoundError):
	
	print("A file with your API info was not found. Please enter in all required information.\n")
	spotifyUsername = input("Enter your spotify username: ")
	spotifyClientID = input("Enter your spotify client id: ")
	spotifyClientSecret = input("Enter your spotify client secret: ")
	youtubeAPIKey = input("Enter your youtube API key: ")
	path = input("Enter a path for songs to be downloaded into: ")
	
	API_file = open("API_file.txt","w")
	API_file.write(spotifyUsername+"\n")
	API_file.write(spotifyClientID+"\n")
	API_file.write(spotifyClientSecret+"\n")
	API_file.write(youtubeAPIKey + "\n")
	API_file.write(path + "\n")
	API_file.close()
	
	

#spotify token
scope = 'user-library-read'
username = spotifyUsername

#enter your client id and client secrets from your spotify api
token = util.prompt_for_user_token(username,scope,client_id = spotifyClientID,client_secret = spotifyClientSecret,redirect_uri = "http://localhost/")

def totalSongs():
    results = {}
    SongList = []
    startPoint = 0
    while True:
        results.update(sp.current_user_saved_tracks(limit = 50,offset = startPoint))
        startPoint = startPoint +50

        if results:
            for count, item in enumerate(results['items']):
                track = item['track']
                Song = track['name'] + " " + track['artists'][0]['name']
                SongList.append(Song)
        if count < 49:  #checks to see if songcount is less than 50, if it is, we've reached the end of the track list
            return SongList
            
    

if token:
    sp = spotipy.Spotify(auth=token)
    SongList = totalSongs()
    print("Song List ready")
    
else:
    print ("Can't get token for", username)

#enter your youtube API_KEY 	
API_KEY = youtubeAPIKey
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def search_by_keyword(track): #returns a youtube ID of type string for one song
	youtube = build(
		YOUTUBE_API_SERVICE_NAME, 
		YOUTUBE_API_VERSION, 
		developerKey=API_KEY
    )
	search_response = youtube.search().list(
		q=track,
		part="id,snippet",
		maxResults=1
    ).execute()

	videos = ""

	for search_result in search_response.get("items", []):
		if search_result["id"]["kind"] == "youtube#video":
			videos ="%s" % (search_result["id"]["videoId"])
			

	return videos


#use download_archive in ydl_opts to prevent multiple downloads

ydl_opts = {
    'outtmpl': path + '/%(title)s.%(ext)s',
    'download_archive' : 'downloaded_songs.txt',
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}


def downloadList(SongList):
        youtubeLinks = []
        if SongList:
                for song in SongList:
                        youtubeLinks.append("https://www.youtube.com/watch?v=" + search_by_keyword(song))
        return youtubeLinks



if __name__ == "__main__":
    if SongList:
        youtubeLinks = downloadList(SongList[0:10]) #list of youtube links, this one only downloads 10 songs
        try:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        ydl.download(youtubeLinks)
        except(KeyboardInterrupt):
                print("Program interrupted manually")
                sys.exit()
        except (HttpError):
                print("An HTTP error occurred: ")
                sys.exit()
