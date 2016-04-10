#! /usr/bin/env python
import glob
import os
import shutil
import requests
import json
from collections import namedtuple
import subprocess
import sys


def get_ratio(good_urls, ratiodict):
    """
    Finds the speedup ratios for each of the mp3 files
    :param good_urls: list of urls that files have been downloaded from
    :param ratiodict: dictionary of search strings and corresponding speedup ratios
    :return: a list of the ratios that where found
    """
    ratios = []
    for url in good_urls:
        ratio2add = False
        for name, ratio in ratiodict.items():
            if name in url:
                ratio2add = ratio
                break
        if not ratio2add:
            print("Could not find saved ratio. Using default instead.")
            ratio2add = ratiodict['default']
        ratios.append(ratio2add)
    return ratios


def correct_mp3(folder):
    """
    Before speeding up the mp3 files they are corrected for metadata mistakes using the mp3val program
    :param folder: the location of the mp3 files
    :return:
    """
    mp3s = glob.glob(os.path.join(folder, "*.mp3"))
    for mp3 in mp3s:
        subprocess.call(["mp3val", "-f", os.path.abspath(mp3)])


def check_outfolder(folder):
    """
    check whether or not the final destination folder is accessible or not
    :param folder: destination folder
    :return:
    """
    if os.path.isdir(folder):
        print("Output directory ready")
    else:
        print("Output directory not available. Please fix and try again")
        sys.exit(-1)


def move(outfolder, folder):
    """
    Move the sped up files to the destination folder one by one
    :param outfolder: destination folder
    :param folder: the source folder, location of mp3 files
    :return:
    """
    mp3s = glob.glob(os.path.join(folder, "*-short.mp3"))
    for mp3 in mp3s:
        filename = os.path.split(mp3)[1]
        print("Moving {} to {}".format(filename, outfolder))
        shutil.move(mp3, outfolder)
        print("Done moving {}".format(filename))


def print_leftover(urls, good_urls):
    """
    At the end prints out the list of urls that were not good (a file couldn't be downloaded from them)
    :param urls: list of urls that were tried
    :param good_urls: list of successful urls
    :return:
    """
    bad_urls = set(urls).difference(set(good_urls))
    if len(bad_urls) > 0:
        print("Could not get:")
        for bad in bad_urls:
            print(bad)


def main():
    conf = namedtuple('config', ['urlfile', 'ratiodict', 'storage', 'outfolder'])
    config = conf(*get_config())
    check_outfolder(config.outfolder)
    urls = get_url_from_file(config.urlfile)
    good_urls, filenames = savemp3(urls, config.storage)
    ratios = get_ratio(good_urls, config.ratiodict)
    correct_mp3(config.storage)
    speedup(filenames, ratios, config.storage)
    move(config.outfolder, config.storage)
    print_leftover(urls, good_urls)


def savemp3(urls, storage):
    """
    go over each url and try to save the mp3 linked there
    :param urls: list of urls to try
    :param storage: folder to save the files to
    :return: lists of successful urls and the names of the saved files
    """
    good_urls = []
    filenames = []
    for url in urls:
        file = os.path.split(url)[1]
        print("Saving {}".format(file))
        r = requests.get(url, stream=True)
        if not r.ok:
            continue
        filename = ''
        try:
            filename = r.headers['filename']
        except KeyError:
            print("Couldn't get 'filename' from response header")
        if not filename:
            filename = os.path.abspath(os.path.join(storage, file))
            print("Using {} instead".format(os.path.split(filename)[1]))
        with open(filename, 'wb') as of:
            shutil.copyfileobj(r.raw, of)
            good_urls.append(url)
            filenames.append(filename)
            print("Done saving")
    return good_urls, filenames


def get_url_from_file(filename):
    """
    Read urls from the containing text file
    :param filename: the text file
    :return: list of urls to try
    """
    with open(filename, 'r') as f:
        urls = f.readlines()
        for row in urls:
            print(row)
    return [url.rstrip() for url in urls]


def speedup(files, ratios, folder):
    """
    Runs ffmpeg on each mp3 file to speed it up by the corresponding ratio
    :param files: list of mp3 files
    :param ratios: list of suitable ratios
    :param folder: the folder containing the mp3 files
    :return:
    """
    for ind, mp3file in enumerate(files):
        print("Increasing speed of {} by factor {}".format(mp3file, ratios[ind]))
        filename = os.path.abspath(os.path.join(folder, mp3file))
        if os.path.isfile(filename):
            subprocess.call(["ffmpeg", '-y', '-i', filename, "-filter:a", "atempo={}".format(ratios[ind]),
                             '-vn', os.path.splitext(filename)[0] + '-short.mp3'])
        else:
            print("Problem with {}, did not speed it up".format(mp3file))


def get_config():
    """
    Get the parameters to use from the configuration file
    :return: The contents of the file
    """
    with open(os.path.join(os.path.dirname(__file__), 'shorten.cfg'), 'r') as f:
        return json.load(f)

if __name__ == '__main__':
    main()
