"""
This is a webCrawler designed for extracting urls and its contents from Daily Mail website. It gets contents from json
file, which contains title, highlight, article and videos.
"""
import requests
import bs4 as bs
import urllib.request
import codecs
import os
import socket
import time
from contextlib import closing


def analyze_json(json_path):
    """
    request website and get its json file to convert dictionary
    :param json_path: json path of an article
    :return:
    """
    try:
        r = requests.get(json_path)
    except (requests.exceptions.ConnectionError, socket.timeout, AttributeError):
        print("error!")
        return None

    web_dict_list = r.json()
    return web_dict_list


def extracts_contents_from_dict_list(web_dict_list, url_set):
    dictionary = {} # record corresponding url and its video src in one website
    for web_dict in web_dict_list:
        url, video_src = extracts_contents_from_dict(web_dict)
        if url not in url_set:
            url_set.add(url)
            if dictionary.get(url) is None:
                dictionary[url] = [video_src]
            else:
                dictionary[url] = dictionary.get(url).append(video_src)
    return dictionary


def extracts_contents_from_dict(web_dict):
    """
    extract contents from dictionary
    :param web_dict: a dictionary converted from json file
    :return:
    """
    url = web_dict['grapeshot']['article']['articleURL']
    video_src = web_dict['src']
    return url, video_src


def extracts_contents_from_url(soup, video_paths, save_path, flag):
    """
    extract necessary contentes from url and download video from video path
    :param soup: bs4 object
    :param video_path: video path in current website
    :return:
    """

    if flag:
        os.makedirs(save_path)

        # get title
        title_file = codecs.open(save_path + "/title.txt", 'a', encoding='utf-8')
        title = soup.h2.text
        title_file.write(title)

        # get highlight
        highlight_file = codecs.open(save_path + "/highlight.txt", 'a', encoding='utf-8')
        if len(soup.select('.mol-bullets-with-font')) != 0:
            highlight_manager = soup.select('.mol-bullets-with-font')[0].contents
        else:
            highlight_manager = soup.find("div", {"itemprop": "articleBody"}).contents[1].contents
        for child in highlight_manager:
            highlight = child.text
            highlight.replace(r"\\", "")
            highlight_file.write(highlight)

        # get article
        article_file = codecs.open(save_path + "/article.txt", 'a', encoding='utf-8')
        article_manager = soup.select(".mol-para-with-font")
        flag = True
        if len(article_manager) == 0:
            article_manager = soup.find_all("font", {"style": "font-size: 1.2em;"})
            flag = False
        for child in article_manager:
            if flag:
                article = child.string
            else:
                article = child.text
            if article is not None:
                article_file.write(article)

        # get video
        for url in video_paths:
            try:
                print("video url is:", url)
                data_res = requests.get(url, stream=True)
                data = data_res.content
                print("request finish")
                file = codecs.open(save_path + "/video.mp4", "wb")
                file.write(data)
            except (TypeError, AttributeError, requests.ConnectionError) as e:
                print("Errors!", e)
            print("finish")
            # with closing(requests.get(url, stream=True)) as r:
            #     chunk_size = 1024
            #     with open(save_path + "/video.mp4", "wb") as f:
            #         for chunk in r.iter_content(chunk_size=chunk_size):
            #             f.write(chunk)


def construct_json_address(json_id):
    """
    construct json website address by json id
    :param json_id: the id of every news
    :return:
    """
    address = "https://www.dailymail.co.uk/api/player/" + json_id + "/related-videos.json?geo=CN"
    return address


def check_website(soup):
    """
    make sure the assigned website contains necessary contents
    :param soup: a bs4 object of assigned website
    :return:
    """
    flag = True

    # check highlight
    highlight1 = soup.select('.mol-bullets-with-font')
    highlight2 = soup.find("div", {"itemprop": "articleBody"}).contents[1]
    if len(highlight1) == 0:
        if highlight2.name != "ul":
            flag = False

    return flag


def scrape_content(url_videosrc_dictionary, max_url_num, url_set, json_id, save_path):
    count = 1461
    while count < max_url_num:
        if not url_videosrc_dictionary: # url dictionary is empty
            json_id = str(int(json_id) + 100)
            print("jsonid", json_id)
            new_json_address = construct_json_address(json_id)
            print("analyse")
            web_dict_list = analyze_json(new_json_address)
            print("finish")
            if web_dict_list is not None:
                url_videosrc_dictionary = extracts_contents_from_dict_list(web_dict_list, url_set)

        else: # there exists some url and its corresponding video src in dictionary
            example = url_videosrc_dictionary.popitem()
            url = example[0]
            video_paths = example[1]
            new_path = save_path + "/" + str(count)

            print(url)
            try:
                # timeout = 20
                # socket.setdefaulttimeout(timeout)
                # sleep_download_time = 10
                # time.sleep(sleep_download_time)
                sauce = urllib.request.urlopen(url).read()
                soup = bs.BeautifulSoup(sauce, 'lxml')
            except (urllib.error.URLError, urllib.error.HTTPError, socket.timeout, AttributeError):
                print("error!")
            flag = check_website(soup)  # make sure website contains necessary contents
            print(flag)

            if flag:
                extracts_contents_from_url(soup, video_paths, new_path, flag)
                count += 1
            print("over！")
    return


def main():
    max_url_num = 10000
    json_id = "25050060"
    save_path = r""

    timeout = 20
    socket.setdefaulttimeout(timeout)
    sleep_download_time = 10
    time.sleep(sleep_download_time)

    start_json = construct_json_address(json_id)
    web_dict_list = analyze_json(start_json)
    url_set = set()
    url_videosrc_dictionary = extracts_contents_from_dict_list(web_dict_list, url_set)
    scrape_content(url_videosrc_dictionary, max_url_num, url_set, json_id, save_path)


if __name__ == "__main__":
    main()