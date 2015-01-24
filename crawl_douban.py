#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import re
import sys
import time
import urllib2

class Error(Exception):
  """Exception class of this module"""


kTimeOut = 30  # in seconds


def _GetData(url):
  page = urllib2.urlopen(url, timeout=kTimeOut)
  if page.getcode() != 200:
    raise Error("http code error: %s" % page.getcode())
  else:
    return page.read()

class DoubanCrawler(object):

  def __init__(self, domain, number_hint, data_type, page_pattern=None):
    self.domain_ = domain
    self.number_hint_ = number_hint
    self.data_type_ = data_type
    self.page_pattern_ = page_pattern
    
  def GetDomain(self):
    return self.domain_

  def GetNumberHint(self):
    return self.number_hint_

  def GetType(self):
    return self.data_type_

  def GetNumber(self, user):
    cover_url_pattern = (
        "http://" + self.GetDomain() + ".douban.com/people/%s/" + self.GetType())
    url = cover_url_pattern % user
    data = _GetData(url)
    search_pattern = re.compile(self.GetNumberHint() + r"\((.+)\)")
    mo = search_pattern.search(data)
    if not mo:
      raise Error("cannot find number for %s" % user)
    else:
      return int(mo.group(1))
  
  def GetOutputFolder(self, base_dir):
    path = os.path.join(base_dir, self.GetDomain())
    path = os.path.expandvars(os.path.expanduser(path))
    if not os.path.exists(path):
      os.makedirs(path)

    return path
     
  def _GetPagePattern(self):
    if self.page_pattern_:
      return self.page_pattern_

    page_pattern = ("http://" + self.GetDomain() + ".douban.com/people/%s/" + self.GetType() +
        "?start=%s&sort=time&rating=all&filter=all&mode=grid")
    return page_pattern

  def GetPages(self, user, base_output_dir):
    page_pattern = self._GetPagePattern() 
    num = self.GetNumber(user)
    counter = 0
    output_dir = self.GetOutputFolder(base_output_dir)
    for start in xrange(0, num, 15):
      url = page_pattern % (user, start)
      data = _GetData(url)
      path = os.path.join(output_dir, "%s-%s-%s-%s.html" % (
          user, self.GetType(), start, start + 15))
      with open(path, "w") as f:
        f.write(data) 
        counter += 1
      # To respect doubam.com
      time.sleep(0.5)
  
    return counter


def CrawlUserData(user, base_output_dir):
  kCelebritiesPattern = "http://movie.douban.com/people/%s/celebrities?start=%s"

  kSpecs = (("book", "读过的书", "collect"), ("book", "想读的书", "wish"),
      ("book", "在读的书", "do"), ("movie", "看过的电影", "collect"),
      ("movie", "想看的电影", "wish"), ("movie", "在看的电视剧", "do"),
      ("music", "听过的音乐", "collect"), ("music", "想听的音乐", "wish"),
      ("music", "在听的音乐", "do"), ("movie", "收藏的影人", "celebrities", kCelebritiesPattern))
  #for spec in kSpecs:
  for spec in kSpecs[-1:]:
    crawler = DoubanCrawler(*spec)
    counter = crawler.GetPages(user, base_output_dir)
    print spec[1], counter


def main(argv):
  CrawlUserData(argv[1], argv[2])


if __name__ == "__main__":
  main(sys.argv)
