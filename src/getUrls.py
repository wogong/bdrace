import re
import urlparse
# import logging
import random
import urllib
from bs4 import BeautifulSoup
from difflib import SequenceMatcher

def get_all_url(url): # get all urls in the given url page
   urls = []
   web = urllib.urlopen(url)
   soup = BeautifulSoup(web.read())
   tags_a =soup.findAll(name='a', attrs={'href':re.compile("^https*://")})
   try :
       for tag_a in tags_a:
           urls.append(tag_a['href'])
   except:
       pass
   #print(urls)
   return urls

def get_all_url2(url): # get all urls in the given url page
   urls = []
   web = urllib.urlopen(url)
   soup = BeautifulSoup(web.read(), "lxml")
   tags_a =soup.findAll(name='a', attrs={'href':re.compile(".*?")})
   try :
       for tag_a in tags_a:
           urls.append(tag_a['href'])
   except:
       pass
   #print(urls)
   return urls

def get_local_urls(url): # get urls of the same domain
   local_urls = []
   urls = get_all_url2(url)
   netloc = urlparse.urlparse(url).netloc
   scheme = urlparse.urlparse(url).scheme
   for _url in urls:
       if _url.startswith('http'):
           ret = _url
       else:
           ret = scheme + '://' + netloc + '/' + _url
       if netloc in ret.replace('//', '').split('/')[0]:
           similar(ret, url)
           local_urls.append(ret)
   #print(local_urls)
   return local_urls

def get_slr_url(url, benchmark): # get similar urls in the given url page
    slr_urls = []
    local_urls = get_local_urls(url)
    for _url in local_urls:
        if similar(benchmark, _url) > 0.98:
            slr_urls.append(_url)
    #print(slr_urls)
    return slr_urls

def similar(a, b): # calculate similarity
    a = re.sub(r'\d', '', a)
    b = re.sub(r'\d', '', b)
    res =  SequenceMatcher(None, a, b).ratio()
    return res

def get_n_slr(url, n): # get n urls similar to the given url
    slr_urls = []
    local_urls = get_local_urls(url)
    print local_urls
    slr_urls.append(url)
    count1 = 0
    count2 = 0
    while len(set(slr_urls)) < n:

        #local_urls = local_urls + get_local_urls(random.choice(local_urls))
        #local_urls = local_urls + get_local_urls(local_urls[0])
        slr_urls = slr_urls + get_slr_url(local_urls[count1], url)
        count1 = count1 + 1
        print len(set(slr_urls))
        print set(slr_urls)
        if count1 > len(local_urls):
            local_urls = local_urls + get_local_urls(local_urls[count2])
            count2 = count2 +1
    # print(len(set(slr_urls)))
    # print(set(slr_urls))
    return slr_urls



# u = "http://8.7k7k.com/thread-1453189-1-1.html"
u = "https://bbs.hupu.com/18983709.html"
# u3 = "http://bbs.coolpad.com/thread-5147419-1-1.html"
# u4 = 'http://bbs.dospy.com/thread-17787932-1-144-1.html'
# u5 = 'https://bbs.hupu.com/18994823.html'
#print get_all_url2(u1)
#print(get_local_urls(u3))
#similar(u1,u2)
#get_slr_url(u3, u3)
#get_mass_urls(u3)
#print get_all_url2("http://bbs.coolpad.com/forum-1252-1.html")
#print get_local_urls(u1)
# url_list =  set(get_n_slr(u5, 5))
# print url_list
# print len(url_list)
get_n_slr(u,10)