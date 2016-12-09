#!/usr/bin/python
# -*- coding:utf-8-*-
"""运用百度识图来进行图片识别
"""
import requests
import re

import ssl

if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36"


def baidu_image_upload(im):
    url = "http://image.baidu.com/pictureup/uploadshitu?fr=flash&fm=index&pos=upload"

    im.save("./query_temp_img.png")
    raw = open("./query_temp_img.png", 'rb').read()

    files = {
        'fileheight': "0",
        'newfilesize': str(len(raw)),
        'compresstime': "0",
        'Filename': "image.png",
        'filewidth': "0",
        'filesize': str(len(raw)),
        'filetype': 'image/png',
        'Upload': "Submit Query",
        'filedata': ("image.png", raw)
    }

    resp = requests.post(url, files=files, headers={'User-Agent': UA})

    #  resp.url
    redirect_url = "http://image.baidu.com" + resp.text
    return redirect_url


def baidu_stu_lookup(im):
    redirect_url = baidu_image_upload(im)

    # print redirect_url
    resp = requests.get(redirect_url)

    html = resp.text

    return baidu_stu_html_extract(html)


def baidu_stu_html_extract(html):
    pattern = re.compile(r"'multitags':\s*'(.*?)'")
    matches = pattern.findall(html)
    if not matches:
        return '未知'

    tags_str = matches[0]

    result = list(filter(None, tags_str.replace('\t', ' ').split()))

    return '|'.join(result) if result else '未知'
