import os
import requests
from bs4 import BeautifulSoup
import urllib.request
import json
import random
import shutil
from soundcloud import SoundCloud, BasicTrack, MiniTrack
from scdl import scdl
from pathvalidate import sanitize_filename

def get_image(track: BasicTrack, path):
    url = track.artwork_url.replace("large", "t500x500")
    print(url)
    urllib.request.urlretrieve(url, os.getcwd()+rf'\{path}\{track.id}.jpg')


def delete(path):
    if os.path.isdir(path):
        shutil.rmtree(path)


def track_youtube_upload(item: BasicTrack, video_path):
    answer = input("upload on youtube? \n (Y/N) : ")
    if answer == "Y" or answer == "y":
        youtube_title = f"{item.user.username} - {item.title}"

        if len(youtube_title) > 100:
            youtube_title = youtube_title[:100]
        print(youtube_title)

        result = os.popen(rf'python upload_video.py --file="{video_path}"  --title="{youtube_title}"'
                          f' --description="{item.permalink_url}"  --keywords=" " --category="22" --privacyStatus="public"').read()
        print(result)


def main(url):
    r = str(random.random())
    temp_path = "temp" + r[2:]
    os.mkdir(temp_path)

    os.system(f"scdl -l {url} --no-original --path {temp_path}")

    client = SoundCloud("a3e059563d7fd3372b49b37f00a00bcf")
    item = client.resolve(url)

    if item.kind == "track":
        video_path = make_video_only_track(temp_path, item)
        track_youtube_upload(item, video_path)
    if item.kind == "playlist":
        pass


def get_track_list(item, client):
    for i in range(len(item.tracks)):
        if isinstance(item.tracks[i], MiniTrack):
            item.tracks[i] = client.get_track(item.tracks[i].id)

def make_video_only_track(temp_path, track: BasicTrack):
    get_image(track, temp_path)

    mp3_filename = scdl.limit_filename_length(track.title, ".mp3")
    mp3_filename = sanitize_filename(mp3_filename)

    os.system(rf'ffmpeg -loop 1 -framerate 2 -i "{temp_path}\{track.id}.jpg" -i "{temp_path}\{mp3_filename}" ' +
              rf'-c:v libx264 -preset medium -tune stillimage -crf 18 -c:a copy -shortest -pix_fmt yuv420p ' +
              rf'"{temp_path}\{track.id}.mkv"')

    return rf"{temp_path}\{track.id}.mkv"

if __name__ == '__main__':
    while True:
        input_url = input("url : ")
        main(input_url)