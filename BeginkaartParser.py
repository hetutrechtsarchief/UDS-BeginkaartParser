#!/usr/bin/env python3

import xml.parsers.expat
import json,sys,os,argparse,time,re
from html.parser import HTMLParser
import logging
import urllib.request

class Parse(HTMLParser):

  def handle_comment(self, data):
    global weEnteredTheText

    if data.find("einde tekst")>-1:
      weEnteredTheText = False

  def handle_starttag(self, name, attrs):
    global obj, weEnteredTheText, weEnteredTheLabel

    if name=="div":
      for k,v in attrs:
        if (k=="id" and v=="tekst"):
          weEnteredTheText = True
          weEnteredTheLabel = True

    if name=="br":
      if weEnteredTheLabel:
        obj["label"] = re.sub(r"\s+", " ", obj["label"]).strip()  # replace multiple dashes by 1 dash

        weEnteredTheLabel = False


  def handle_data(self, data):
    global obj, weEnteredTheText

    if weEnteredTheLabel:
      obj["label"] = obj["label"] + " " + data.strip()

####################################################

# parse command line parameters/arguments
argparser = argparse.ArgumentParser(description='UDS Image Area parser')
# argparser.add_argument('--url',help='input URL for example: <http://www.documentatie.org/data/plpr/BEKA/BPU--/BPU-d/Utrecht%20-%20Domplein%2031%20_beginkaart%20[0000.1001].htm>', required=True)
argparser.add_argument('--html',help='input html file', required=True)
argparser.add_argument('--originalURL',help='original URL used as identifier for the article', required=True)
args = argparser.parse_args()

obj = {
  "label": "",
  "articleBody": ""
}

weEnteredTheText = False
weEnteredTheLabel = False

# load data from URL
# with urllib.request.urlopen(args.url) as response:
  # html = response.read()

# response = urllib.request.urlopen(args.url)

# lines = response.readlines()

# lines = lines.decode("utf-8")

# for line in lines:
#   print(line)



# # open xml file and read lines
# with open(args.html, 'r') as file:
#   for line in file:
#     xml = Parse()
#     xml.feed(line)


# open xml file and read lines
with open(args.html, 'r') as file:
  for line in file:
    xml = Parse()
    xml.feed(line)

print("@prefix sdo: <https://schema.org/> .")
print("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .")
print("@prefix trefwoord: <http://documentatie.org/id/trefwoord/> .")
print("@prefix def: <http://documentatie.org/def/> .")
print("@prefix page: <http://documentatie.org/id/pagina/> .")
print("@prefix foaf: <http://xmlns.com/foaf/0.1/> .")
print()
print("<"+args.originalURL+">")
print("  a sdo:Article ;")
print(f"  rdfs:label \"{obj['label']}\"")

