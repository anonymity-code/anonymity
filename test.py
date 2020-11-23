import bs4 as bs
import urllib.request
import requests

url = "https://www.dailymail.co.uk/news/article-6301091/Taco-Bell-offer-free-taco-player-steals-base-World-Series.html"

sauce = urllib.request.urlopen(url).read()
soup = bs.BeautifulSoup(sauce, 'lxml')


img_group_manager = soup.select(".artSplitter")
count = 0
for img_group in img_group_manager:
    img_caption_tag = img_group.contents[3].text
    print("A", img_caption_tag)
    if img_group.contents[1].attrs['class'][0] == "mol-img":
        img_tag = img_group.contents[1].contents[1].contents[1].attrs["data-src"]
        print("B", img_tag)
        html = requests.get(img_tag)
        img_name = str(count) + '.png'
        with open(img_name, 'wb') as file:  # 以byte形式将图片数据写入
            file.write(html.content)
        count += 1

# article_manager = soup.select(".vjs-tech")
# tmp = soup.find("video").contents[1].attrs["src"]



