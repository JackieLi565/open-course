from bs4 import BeautifulSoup
import requests
import sys

def get_html(url):
  html = requests.get(url)

  if (html.status_code != 200):
    exit(f'request error for url: {url}')
  return BeautifulSoup(html.content, 'html.parser')

def build_url(dir):
  return 'https://www.torontomu.ca' + dir

def get_argv():
  return sys.argv[1::]