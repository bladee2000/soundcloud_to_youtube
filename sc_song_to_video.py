import os
import requests
from bs4 import BeautifulSoup
import urllib.request
import json
import random
import shutil


def mp3_download(url, path):
    os.system(f"scdl -l {url} --no-original --path {path}")

def get_image(url,path):
    page = requests.get(url)
    html = page.text
    soup = BeautifulSoup(html, 'html.parser')
    image_url = soup.select('head > meta:nth-child(59)')
    image_url = str(image_url)
    image_url = image_url.replace('[<meta content="', '')
    image_url = image_url.replace('" property="og:image"/>]', '')

    print(image_url)

    urllib.request.urlretrieve(image_url, os.getcwd()+rf'\{path}\image.jpg')

def get_title(path):
    listdir = os.listdir(path)
    for filename in listdir:
        ext = os.path.splitext(filename)[-1]
        if ext == ".mp3":
            title = os.path.splitext(filename)[0]
    return title

def get_artist(title,path):
    os.system(f'ffprobe -print_format json -show_format "{path}\{title}.mp3" > "{path}\meta.json')

    with open(f"{path}\meta.json","r",encoding='UTF8') as st_json:
        metadata = json.load(st_json)

    return metadata["format"]["tags"]["artist"]

def delete(path):
    if os.path.isdir(path):
        shutil.rmtree(path)


def youtube_upload(track_title, track_artist):
    answer = input("upload on youtube? \n (Y/N) : ")
    if answer == "Y" or answer == "y":
        youtube_title = f"{track_artist} - {track_title}"
        if len(youtube_title) > 100:
            youtube_title = youtube_title[:100]
        print(youtube_title)
        result = os.popen(rf'python upload_video.py --file="videos\{track_artist} - {track_title}.mkv"  --title="{youtube_title}" --description="{url}"  --keywords=" " --category="22" --privacyStatus="public"').read()

        print('"'+result+'"')
        result.rstrip()
        print(result[-2:])

        delanswer = input("delete video file? \n (Y/N) : ")
        if delanswer == "Y" or delanswer == "y":
            os.remove(rf"videos\{track_artist} - {track_title}.mkv")
        else:
            pass
    else:
        pass

def main():
    r = str(random.random())
    temp_path = "temp" + r[2:]
    os.mkdir(temp_path)

    mp3_download(url,temp_path)

    get_image(url,temp_path)

    track_title = get_title(temp_path)
    print(track_title)

    track_artist = get_artist(track_title, temp_path)
    print(track_artist)

    if os.path.isdir("videos") == False:
        os.mkdir("videos")

    os.system(rf'ffmpeg -loop 1 -framerate 2 -i "{temp_path}\image.jpg" -i "{temp_path}\{track_title}.mp3" -c:v libx264 -preset medium -tune stillimage -crf 18 -c:a copy -shortest -pix_fmt yuv420p "videos\{track_artist} - {track_title}.mkv"')

    delete(temp_path)

    youtube_upload(track_title,track_artist)

if __name__ == '__main__':
    while True:
        url = input("url : ")
        main()