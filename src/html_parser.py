#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
=========================================================
html parser
=========================================================
"""


import urllib
import re
from lxml import html
import getUrls
from lxml.html.clean import clean_html
import requests

# from lxml import etree

# The stop tags that we drop directly
STOPTAG = ["script", "style"]
class Element:
    """
    Element class
    """
    def __init__(self, path_orig, attrib, text, score=0.0):
        self.path_orig = path_orig
        self.attrib = attrib
        self.text = text
        self.score = score
    def __cmp__(self,other):
        return cmp(self.score, other.score)
    def __str__(self):
        return str(self.score)+" "+ str(self.text) + " " + str(self.path_orig)


def build_etree(url):
    """
    Build an element tree from a url link
    :param url: html link
    :return: tree
    """
    header = {
        'Referer': 'http://www.baidu.com',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4',
    }

    response = requests.get(url, headers=header)
    rawcontent = response.content
    clear = re.compile('(<br.*/*>|<em>|</*font.*?>|</*b>|</*p.*?>)')
    clean_content = re.sub(clear, '',rawcontent)
    print clean_content
    page = html.fromstring(clean_content)
    tree = html.etree.ElementTree(page)
    return tree


def get_all_text(element):
    """
    Get all the text in an element
    :param element: 
    :return: 
    """

    text_list = []
    for node in element.itertext():
        text_list.append(node.strip())
    return ''.join(text_list)

# def parser_etree(tree):
#     """
#     Extract the elements with text in the tree. We store all the elements in
#     a list.
#     :param tree: element tree
#     :return: element list
#     """
#     element_list = []
#     for element in tree.iter():
#         if element.text is not None and element.text.strip() and \
#                         element.tag not in STOPTAG and isinstance(element.tag, basestring):
#             path_orig = tree.getpath(element)
#             attrib = element.attrib
#             text = element.text.strip()
#             element_with_text = Element(path_orig, attrib,text)
#             element_list.append(element_with_text)
#     return element_list


def parser_etree(tree):
    """
    Extract the elements with text in the tree. We store all the elements in
    a list.
    :param tree: element tree 
    :return: element list
    """
    element_list = []
    for element in tree.iter():
        if element.tag not in STOPTAG and isinstance(element.tag, basestring):
            text = ""
            tail = ""
            if element.text is not None:
                text = element.text.strip()
            if element.tail is not None:
                tail = element.tail.strip()
            whole_text = text + tail
            # print whole_text
            if whole_text.strip():
                path_orig = tree.getpath(element)
                attrib = element.attrib
                element_with_text = Element(path_orig, attrib, whole_text)
                element_list.append(element_with_text)
    return element_list


def get_title_text(tree):
    """
    Get the title content of a html
    :param tree: 
    :return: 
    """
    title_text = ''
    try:
        title_text_orig = tree.xpath('/html/head/title')[0].text
        title_list = title_text_orig.split('-')
        title_text = title_list[0].strip()
    except Exception:
        pass

    return title_text

def cal_text_frequency(element_list):
    """
    Calculate the text frequency in a html file. For example, text_frequency_dict['hello'] = 5
    means the text 'hello' emerges 5 times in html file.
    :param element_list: 
    :return: 
    """
    text_frequency_dict = {}
    for element in element_list:
        if element.text in text_frequency_dict.keys():
            text_frequency_dict[element.text] += 1
        else:
            text_frequency_dict[element.text] = 1.0
    return text_frequency_dict


def update_text_frequency(text_frequency_sum_dict, text_frequency_dict):
    """
    We calculate the path frequency in all extension html (use getUrls.py)
    :param text_frequency_sum_dict: 
    :param text_frequency_dict: 
    :return: 
    """
    for key in text_frequency_dict.keys():
        if key in text_frequency_sum_dict.keys():
            text_frequency_sum_dict[key] += text_frequency_dict[key]
        else:
            text_frequency_sum_dict[key] = text_frequency_dict[key]
    return text_frequency_sum_dict


# def cal_text_length(tree):
#     """
#     Calculate the sum of text length in the same path in a html. For example,
#
#     <html>
#      <body>
#       <p>Hello</p>
#       <p>World</p>
#      </body>
#     <html>
#
#     The text_length of path /html/body/p is 5+5=10
#     :param tree:
#     :return:
#     """
#     text_length_dict = {}
#     for element in tree.iter():
#         if element.text is not None and element.text.strip() and \
#                         element.tag not in STOPTAG and isinstance(element.tag, basestring):
#             # pattern of index in the path.
#             path_orig = tree.getpath(element)
#             pat = re.compile('\[\d+\]')
#             path_modified = pat.sub('', path_orig)
#             text = element.text.strip()
#             key = path_modified + '_' + ''.join(element.attrib.keys())
#             if key in text_length_dict.keys():
#                 text_length_dict[key] += len(text)
#             else:
#                 text_length_dict[key] = len(text)
#     return text_length_dict

def cal_text_length(element_list):
    """
    Calculate the sum of text length in the same path in a html. For example,
    
    <html>
     <body>
      <p>Hello</p>
      <p>World</p>
     </body>
    <html>
    
    The text_length of path /html/body/p is 5+5=10
    :param element_list: 
    :return: 
    """
    text_length_dict = {}

    for element in element_list:
        path_orig = element.path_orig
        pat = re.compile('\[\d+\]')
        path_modified = pat.sub('', path_orig)
        text = element.text.strip()
        key = path_modified + '_' + ''.join(element.attrib.keys())
        if key in text_length_dict.keys():
            text_length_dict[key] += len(text)
        else:
            text_length_dict[key] = len(text)
    return text_length_dict


def update_text_length(text_length_sum_dict, text_length_dict):
    """
    We calculate the text length in all extension html (use getUrls.py)
    :param text_length_sum_dict: 
    :param text_length_dict: 
    :return: 
    """
    for key in text_length_dict.keys():
        if key in text_length_sum_dict.keys():
            text_length_sum_dict[key] += text_length_dict[key]
        else:
            text_length_sum_dict[key] = text_length_dict[key]
    return text_length_sum_dict


def cal_path_frequency(element_list):
    """
    Generate the path frequency dict. We eliminate the index in the path.
    For example /html/body/div[1]/div/ul/li[2] --> /html/body/div/div/ul/li.
    We only take the element with information text into account.
    :param element_list: The element list
    :return: 
    """
    path_frequency_dict = {}
    for element in element_list:
        path_orig = element.path_orig
        pat = re.compile('\[\d+\]')
        path_modified = pat.sub('', path_orig)
        key = path_modified + '_' + ''.join(element.attrib.keys())
        if key in path_frequency_dict.keys():
            path_frequency_dict[key] += 1
        else:
            path_frequency_dict[key] = 1
    return path_frequency_dict

# def cal_path_frequency(tree):
#     """
#     Generate the path frequency dict. We eliminate the index in the path.
#     For example /html/body/div[1]/div/ul/li[2] --> /html/body/div/div/ul/li.
#     We only take the element with information text into account.
#     :param tree: The element tree
#     :return:
#     """
#     path_frequency_dict = {}
#     for element in tree.iter():
#         if element.text is not None and element.text.strip() and \
#                         element.tag not in STOPTAG and isinstance(element.tag, basestring):
#             # pattern of index in the path.
#             path_orig = tree.getpath(element)
#             pat = re.compile('\[\d+\]')
#             path_modified = pat.sub('', path_orig)
#             # print "tag: %s | path: %s | text: %s | attrib: %s"\
#             #       % (element.tag, path_orig, text, element.attrib.keys())
#             # print element.text.strip()
#             key = path_modified + '_' + ''.join(element.attrib.keys())
#             if key in path_frequency_dict.keys():
#                 path_frequency_dict[key] += 1
#             else:
#                 path_frequency_dict[key] = 1
#     return path_frequency_dict


def update_path_frequency(path_frequency_sum_dict, path_frequency_dict):
    """
    We calculate the path frequency in all extension html (use getUrls.py) 
    :param path_frequency_sum_dict: 
    :param path_frequency_dict: 
    :return: 
    """
    for key in path_frequency_dict.keys():
        if key in path_frequency_sum_dict.keys():
            path_frequency_sum_dict[key] += path_frequency_dict[key]
        else:
            path_frequency_sum_dict[key] = path_frequency_dict[key]

    return path_frequency_sum_dict


def time_detector(timeString):
    """
    Detect the time in a string
    :param timeString: 
    :return: formatted_time, e.g. 20170421
    """
    formatted_time = ""
    pat_whole_time = re.compile('(?<!\d)\d{2,4}\D\d{1,2}\D\d{1,2}(?!\d)')
    pat_time = re.compile('\d')
    whole_time = re.search(pat_whole_time, timeString)
    if whole_time:
        time_list = re.findall(pat_time, whole_time.group())
        formatted_time = ''.join(time_list)
    return formatted_time

# def get_content_path(element_list):
#     """
#
#     :param element_list:
#     :param path_frequency_dict:
#     :return:
#     """
#     content_path = ""
#     score_max = 0.0
#     for element in element_list:
#         pat = re.compile('\[\d+\]')
#         path_modified = pat.sub('', element.path_orig)
#         key = path_modified + '_' + ''.join(element.attrib.keys())
#         element.score = path_frequency_dict[key] * text_avg_length_dict[key] / text_frequency_dict[element.text]
#         if element.score > score_max:
#             score_max = element.score
#             content_path = key
#     return content_path

if __name__ == '__main__':

    url = "https://bbs.hupu.com/17774182.html"
    # slr_urls = set(getUrls.get_n_slr(url, 50))
    # print slr_urls
    tree = build_etree(url)

    title_text = get_title_text(tree)
    print title_text

    element_list = parser_etree(tree)
    text_frequency_dict = cal_text_frequency(element_list)
    path_frequency_dict = cal_path_frequency(element_list)
    # print path_frequency_dict
    # for key in path_frequency_dict.keys():
    #     print "%s: %s"%(key, path_frequency_dict[key])
    text_length_dict = cal_text_length(element_list)

    slr_urls = list(set(getUrls.get_n_slr(url, 1)))[:1]
    # print len(slr_urls)
    for slr_url in slr_urls:
        tree_ex = build_etree(slr_url)
        slr_element_list = parser_etree(tree_ex)
        slr_text_frequency_dict = cal_text_frequency(slr_element_list)
        slr_path_frequency_dict = cal_path_frequency(slr_element_list)
        slr_text_length_dict = cal_text_length(slr_element_list)
        text_frequency_dict = update_text_frequency(text_frequency_dict, slr_text_frequency_dict)
        path_frequency_dict = update_path_frequency(path_frequency_dict, slr_path_frequency_dict)
        text_length_dict = update_text_length(text_length_dict, slr_text_length_dict)

    # calculate the avg text length
    text_avg_length_dict = {}
    for key in path_frequency_dict.keys():
        text_avg_length_dict[key] = text_length_dict[key] / path_frequency_dict[key]
    #
    # # print pathDict
    # # print textAvgLengthDict
    # # print textFrequencyDict

    path_max = ''
    score_max = float(0)
    for element in element_list:
        pat = re.compile('\[\d+\]')
        path_modified = pat.sub('', element.path_orig)
        key = path_modified + '_' + ''.join(element.attrib.keys())
        path_depth = len(element.path_orig.split('/'))
        # element.score = path_frequency_dict[key] * text_avg_length_dict[key] / text_frequency_dict[element.text]
        element.score = text_length_dict[key] * path_depth / text_frequency_dict[element.text]
        if element.score > score_max:
            score_max = element.score
            path_max = key
        # print element.text + ' : ' + str(element.score) + ' : ' + element.path_orig
        print "text: %s | score: %f" % (element.text, element.score)

    print path_max + " : " + str(score_max)
    # print get_content_path(element_list)

    pat = re.compile('\[\d+\]')
    for e in element_list:
        path_modified = pat.sub('', e.path_orig)
        key = path_modified + '_' + ''.join(e.attrib.keys())
        if key == path_max:
            print e.text

    # for e in tree.iter():
    #     path_modified = pat.sub('', e.path_orig)
    #     key = path_modified + '_' + ''.join(e.attrib.keys())
    #     if key == path_max:
    #         print e.text

# page = html.fromstring(urllib.urlopen(url).read())
# htmlEtree = html.etree.ElementTree(page)
# result = etree.tostring(htmlEtree, pretty_print=True)
# # print result
#
#
#
# for e in htmlEtree.iter():
#     if e.text is not None and e.text.strip() and e.tag not in STOPTAG:
#         print "tag: %s | path: %s | text: %s"%(e.tag, htmlEtree.getpath(e), e.text)
#         pat = re.compile('\[\d+\]')
#         pathModified = pat.sub('', htmlEtree.getpath(e))
#         print pathModified

# print html.tostring(page, pretty_print=True, method="html")
# htmlPage = urllib.urlopen(url).read()
# print htmlPage
# page = html.fromstring(htmlPage)

