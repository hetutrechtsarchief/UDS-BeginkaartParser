#!/usr/bin/env python3

import xml.parsers.expat
import json,sys,os,argparse,time,re
from html.parser import HTMLParser
import logging
import urllib.request
import urllib.parse

def makeSafeURIPart(s):
  s = re.sub(r"[–’+?&=|,\.() \"$/']", "-", s) # replace different characters by a dash
  s = re.sub(r"-+", "-", s) # replace multiple dashes by 1 dash
  s = re.sub(r"[^a-zA-Z0-9\-]", "", s) # strip anything else now that is not a alpha or numeric character or a dash
  s = re.sub(r"^-|-$", "", s) # prevent starting or ending with . or -
  if len(s)==0:
    s="x"
  return s.lower()

def makeSafeLiteral(s):
  return re.sub(r"\"", "\\\"", s) # replace " quote by ""

class Parse(HTMLParser):
      
  def handle_starttag(self, name, attrs):
    global obj, isText, isLabel, isImage, isAuthor

    for k,v in attrs:
      if name=="div" and k=="id" and v=="tekst":
        isText = True
        isLabel = True

      if name=="div" and k=="id" and v=="plaatje":
        isImage = True

      if isImage and name=="img" and k=="src":
        obj["image"] = v
        isImage = False

      if name=="a" and k=="href":
        m = re.findall(r"/uds4/zoekpagina5a\.asp\?id=(.*)", v) 
        for r in m:
          obj["imageDetailsPage"] = r

        if not obj["imageDetailsPage"]: # different link for example at: utrecht-domplein-18-gesloopt-1938
          m = re.findall(r"/idUDSpagina\.asp\?id=(.*)", v) 
          for r in m:
            obj["imageDetailsPage"] = r

        m = re.findall(r"/uds4/zoekpagina3t\.asp\?search=(.*)", v.lower()) 
        for r in m:
          obj["mainTopic"] = makeSafeURIPart(r)

        m = re.findall(r"/uds4/zoekpagina3\.asp\?search=(.*)", v.lower()) # sometimes UDS4 is with capitals
        for r in m:
          obj["otherTopics"].append("trefwoord:"+makeSafeURIPart(r))

      if name=="span" and k=="id" and v=="auteur":
        isText = False
        isAuthor = True

        # finalize articleBody
        obj["articleBody"] = re.sub(r"\s+", " ", obj["articleBody"]).strip()
        obj["articleBody"] = re.sub(r" \.", ".", obj["articleBody"])
        obj["articleBody"] = re.sub(r" \,", ",", obj["articleBody"])
        obj["articleBody"] = makeSafeLiteral(obj["articleBody"])

    if name=="br":
      if isLabel:
        obj["label"] = makeSafeLiteral(re.sub(r"\s+", " ", obj["label"]).strip())  # replace multiple dashes by 1 dash

        isLabel = False


  def handle_data(self, data):
    global obj, isLabel, isText, isAuthor

    if isLabel:
      obj["label"] = obj["label"] + " " + data.strip()

    elif isText:
      obj["articleBody"] = obj["articleBody"] + " " + data.strip()      

    elif isAuthor:
      obj["author"] = makeSafeLiteral((obj["author"] + " " + data.strip()).strip())

      if obj["author"]: # done
        isAuthor = False 

####################################################

# parse command line parameters/arguments
argparser = argparse.ArgumentParser(description='UDS Image Area parser')
argparser.add_argument('--html',help='input html file', required=True)
# argparser.add_argument('--originalURL',help='original URL used as identifier for the article', required=True)
args = argparser.parse_args()

obj = {
  "label": "",
  "articleBody": "",
  "image": "" ,
  "imageDetailsPage": "",
  "mainTopic": "", # the main topic this kaart belongs to
  "author": "",
  "otherTopics": []
}

isText = False
isLabel = False
isImage = False
isAuthor = False

# open xml file and read lines
with open(args.html, 'r') as file:
  for line in file:
    xml = Parse()
    xml.feed(line)

obj['otherTopics'] = " , ".join(obj['otherTopics'])
obj['image'] = urllib.parse.quote(obj['image'])

if obj["mainTopic"]:
  print(f"trefwoord:{obj['mainTopic']} def:hasBeginkaart [")   # blank node [ ]
  print(f"  a sdo:Article ;")
  print(f"  rdfs:label \"{obj['label']}\" ; ")
  print(f"  sdo:articleBody \"{obj['articleBody']}\" ;")
  print(f"  foaf:depiction <{obj['image']}> ;") 
  print(f"  def:imageDetailsPage page:{obj['imageDetailsPage']} ;")
  print(f"  def:mainTopic trefwoord:{obj['mainTopic']} ;")
  print(f"  sdo:author \"{obj['author']}\" ; ")
  # if obj["otherTopics"]:
  print(f"  def:otherTopics {obj['otherTopics']} ] .")
  print()

