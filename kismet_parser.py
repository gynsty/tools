#!/usr/bin/python 

import sys
import re
import xml.etree.ElementTree as ET
import sys
import os.path
from math import sin, cos, sqrt, atan2, radians
import argparse

# here you can get 8bit hexcolor:
# https://www.schemecolor.com/sample?getcolor=942D8C

# Global values
aplist = []
cplist = []
apdict = {}
buggydict = {}
output = ""
style = "mystyle"
formats="full"
max_distance=0

# defined methods:

def calc_distance(la1,lo1,la2,lo2):  # get distance in metres

 # approximate radius of earth in km
 R = 6373.0
 lat1 = radians(la1)
 lon1 = radians(lo1)
 lat2 = radians(la2)
 lon2 = radians(lo2)
 dlon = lon2 - lon1
 dlat = lat2 - lat1
 a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
 c = 2 * atan2(sqrt(a), sqrt(1 - a))
 distance = (R * c)
 distance = distance * 1000
 return round(distance,2)

output = output + "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n"
output = output + " <Document>\n"
output = output + "\t<Style id=\"green\"><IconStyle><Icon><href>icons/ap_green.png</href></Icon></IconStyle></Style>\n"
output = output + "\t<Style id=\"red\"><IconStyle><Icon><href>icons/ap_red.png</href></Icon></IconStyle></Style>\n"
output = output + "\t<Style id=\"blue\"><IconStyle><Icon><href>icons/ap_blue.png</href></Icon></IconStyle></Style>\n"
output = output + "\t<Style id=\"purple\"><IconStyle><Icon><href>icons/ap_purple.png</href></Icon></IconStyle></Style>\n"
output = output + "\t<Style id=\"yellow\"><IconStyle><Icon><href>icons/ap_yellow.png</href></Icon></IconStyle></Style>\n"
output = output + "\t<Style id=\"orange\"><IconStyle><Icon><href>icons/ap_orange.png</href></Icon></IconStyle></Style>\n"
output = output + "\n"

""" KML ALLOWS ONLY 1 Placemark inside xml file. So put all placemarks inside Document tag!"""

# prepare argparse:
parser = argparse.ArgumentParser()

# setup options:
parser.add_argument('-l',action="store",dest="log",help="Kismet netxml log file.")
parser.add_argument('-e',action="store",dest="essids",help="Target AP ESSID. Accept multiple values separated by ','.")
parser.add_argument('-lat',action="store",dest="lat",type=float,help="Gps point langitude.")
parser.add_argument('-lon',action="store",dest="lon",type=float,help="Gps point longitude.")
parser.add_argument('-dist',action="store",type=int,dest="dist",help="Show me all networks in perimeter from -lan, -lon. If defined -lat,-lon must be also defined.")

parser.add_argument('-mins',action="store",dest="mins",help="Minimum signal strenght in -dBm. Example: -70.")

parser.add_argument('-c',action="store",dest="chan",help="Channel set.")
parser.add_argument('-enc',action="store",dest="enc",help="Encryption to filer: open,wep,psk,wpa2.\nColors are: open - green, wep - red, blue - aes, yellow - tkip/psk, purple - captive portal.")
parser.add_argument('-cp',action="store",dest="cp",help="AP with Captive Portal. APs can be separated by comma.")

parser.add_argument('-stat',action="store_true",default=False,help="Print statistics and exit.")
parser.add_argument('-o',action="store",dest="output",help="Output KML file.")

parser.add_argument('-with3d', '--with3d', action="store_true", default=False,help="3d style in output")	# 3d mode
parser.add_argument('-f', '--format', action="store", dest="formats",help="Output format. Options: essid,signal,full. This options has effect only if used with -with3d option. Default format is: APNAME -signal dBm.")	
parser.add_argument('-d', action="store_true", default=False,help="Debugging output")		# debug

# parse all arguments
args = parser.parse_args()

if len(sys.argv) <= 2:          # 1 is always program name
 parser.print_help(sys.stderr)
 sys.exit(1)

if args.log:
 netxml = args.log
 if not re.search("\.netxml",netxml):
  print("Error, logfile has not .netxml extension!\n")
  sys.exit(1)
else:
 print("Missing logfile on input via -l option.")
 sys.exit(1)

# parse wanted essids
netname = ""
if args.essids:
 netname = args.essids 
 if re.search(",",netname):
  aplist = netname.split(",")
 else:
  aplist.append(netname)
else:
 netname = "all"
 aplist.append(netname)

# global vars
if args.mins:
 mins = args.mins
 if not re.search("-",mins):
  print("You meant -"+mins+" value. Signal is always defined as -value not plus!\n");
  sys.exit(1);
else:
 mins = 0

# -lat, -lon, -dist
if args.dist:
 if not args.lat or not args.lon:
  print("If you use -dist, -lat and -lon must be defined!")
  sys.exit(1)
 max_distance = args.dist

encarg = ""
if args.enc:
 encarg = args.enc 		# encryption argument

encryption = ""
achannel = 0 			# scan channel
kmlfile = args.output
with3d = args.with3d
debug = args.d

ap_counter = 0 			# count final result of ap

if args.formats:
 formats = args.formats

# DEBUG:
#if debug:
# sys.stderr.write(""+str(args))

# fixed to check if -l has value
if netxml:
 dummy = 1
else:
 print("Missing -l value for input file!")
 sys.exit(1)

# parse cplist
if args.cp:
 cp = args.cp
 if re.search(",",cp):
  cplist = cp.split(",")
 else:
  cplist.append(cp)

if args.chan:
 achannel = int(args.chan)

if kmlfile: 
 if os.path.exists(kmlfile):
  print("Error! Output file exists!")
  sys.exit(1)

#if tree:
 #sys.stderr.write("File: "+netxml+"parsed successfully!\n")

tree = ET.parse(netxml)
root = tree.getroot()

for child in root: 
 if child.tag == "wireless-network":
  network = child 
  
  # in wireless network mode
  essid = ""
  bssid = ""
  enctag = ""		# None|TKIP|PSK|AES
  signal = ""
  avg_lat = ""
  avg_lon = ""
  channel = 0
  lineheight = 0 
  test = ""
  encryptions = []
 
  for element in network:
   # get essid:
   if element.tag == "SSID":
    for x in element:
     if x.tag == "essid":
      essid = str(x.text)
      #print("Found:"+essid)
      if not essid:
       essid = "Unknown"
      # bug fix - kml does not like ampersand
      if re.search("&",essid):
       essid = re.sub("&","0x26",essid)
       #print("Found buggy ESSID:"+essid),
      # -e match:

     if x.tag == "encryption":
      enctag = str(x.text)
      #print("ENC:"+enctag)
      encryptions.append(enctag)

      # here is the issue - some AP accept PSK/TKIP and also AES CCMP - both are WPA, but if we detect TKIP - we
      # print them as 

   if element.tag == "BSSID":
    bssid = str(element.text)
    #print("BSSID:"+bssid+"\n")
    apdict[essid] = bssid 

   if element.tag == "channel":
    channel = int(element.text)
    #print("channel:"+str(channel))

   if element.tag == "snr-info":
    for x in element:
     if x.tag == "max_signal_dbm":
      signal = str(x.text)
      #print("Maxsignal:"+signal),

   if element.tag == "gps-info":
    for x in element:
     if x.tag == "avg-lat":
      avg_lat = str(x.text)
      #print("GPS:"+avg_lat+","),
     if x.tag == "avg-lon":
      avg_lon = str(x.text)
      #print(avg_lon) 

  # in wireless-network node 
  #print(encryptions) 
  if 'None' in encryptions:
   style = "green"
   linestyle = "FF2EE83A"
   encryption = "open"
  elif "WEP" in encryptions:
   style = "red"
   linestyle = "FF0000CC"
   encryption = "#wep"
  elif "WPA+TKIP" in encryptions and "WPA+PSK" in encryptions and not "WPA+AES+CCM" in encryptions:
   style = "yellow"
   linestyle = "FF00CCCC"
   encryption = "tkip"

  # 'WPA+TKIP', 'WPA+PSK', 'WPA+AES-CCM'
  # 'WPA+PSK', 'WPA+AES-CCM'
  elif "WPA+PSK" in encryptions and "WPA+AES-CCM" in encryptions:
   style = "orange"
   linestyle = "FFDD29FF"
   encryption = "psk"
  elif "WPA+AES-CCM" in encryptions and not "WPA+PSK" in encryptions:
   style = "blue"
   linestyle = "FFFFA500"
   encryption = "aes"
  else:
   style = ""
   linestyle = "00000000"
   encryption = "unknown"

  # ..
  if essid not in aplist and netname !="all": # this behaviour works but is buggyyyy
   continue

  # create regexp
  # x = re.compile(essid,re.IGNORECASE)
  # if not filter(x.match,aplist):
  # continue
  # print("essid")
  # sys.exit(1)  

  # this filter works fine
  if mins:
   if signal > mins:
    continue

  if max_distance:
   distance = calc_distance(args.lat,args.lon,float(avg_lat),float(avg_lon))
   if distance > max_distance:
    continue

  if achannel:
   if achannel != channel or channel == 0: # bug fix for ap with channel 0
    continue
   
  # open, wep, psk, tkip, aes
  if encarg:
   if not re.search(encarg,encryption,re.IGNORECASE):
    continue

  # print only filtered aps:
  # print(essid+encryption)

  ap_counter+=1			# count ap results
  
  # if AP is protected with CP we change linestyle
  if cplist:				# bug hunter if essid exists
    for apx in cplist:
     if re.search(apx,essid,re.IGNORECASE):
      style = "purple"
      #linestyle = "FF942D8C"
      linestyle = "FFFF00FF" # looks better ?? :-)

  if with3d:
   strength = signal[1:]
   strength = int(strength)
   if strength == 0:
    continue 
   else:
    lineheight = (100 - strength) /2    # 100 - we need reverse number to signal strenght  
    					   # because line height must be lower as signal is weaker
  					   # /2 - because lines were to high	
   thickness = 0
   # line thickness: 
   # -40-(-30) - 10 
   # -50-(-40) - 7
   # -50-(-60) - 5
   # -60-(70)  - 3  

   if signal <= 40:
    thickness = 10
   elif signal <= 50:
    thickness = 7
   elif signal <= 60:
    thickness = 5
   else:
    thickness = 2

   # 3d modeling:
   output = output+"\n"
   output = output + "\t<Placemark>\n"

   # adding possible formats of output
   if formats == "full":
    output = output + "\t<name chan=\""+str(channel)+"\">"+essid+" "+signal+"dBm"+"</name>"+"\n"
   elif formats == "essid":
    output = output + "\t<name chan=\""+str(channel)+"\">"+essid+"</name>"+"\n"
   else:
    output = output + "\t<name chan=\""+str(channel)+"\">"+signal+"dBm"+"</name>"+"\n"
    
   # add style to point:
  
   output = output + "\t<Style>\n"
   output = output + "\t <IconStyle><Icon><href></href></Icon></IconStyle>\n"

   output = output + "\t <LineStyle><color>"+str(linestyle)+"</color>\n"
   output = output + "\t  <width>"+str(thickness)+"</width>\n"
   output = output + "\t  <gx:labelVisibility>1</gx:labelVisibility>\n"
   output = output + "\t </LineStyle>\n"
   output = output + "\t</Style>\n"
   
   output = output + "\t<Point>\n"
   output = output + "\t <extrude>1</extrude>\n"
   output = output + "\t <altitudeMode>relativeToGround</altitudeMode>\n"
   output = output + "\t <coordinates>"+avg_lon+","+avg_lat+","+str(lineheight)+"</coordinates>\n"
   output = output + "\t</Point>\n"
   output = output + "\t</Placemark>\n"

  else:
   output = output+"\n"
   output = output + "\t<Placemark>\n"
   output = output + "\t<name chan=\""+str(channel)+"\">"+essid+","+signal+"dBm</name>"+"\n"
   if style:
    output = output + "\t<styleUrl>"+style+"</styleUrl>\n"
   output = output + "\t<Point><coordinates>"+avg_lon+","+avg_lat+",0</coordinates></Point>\n"
   output = output + "\t</Placemark>\n"
   # print "ESSID:"+essid+","+"BSSID:"+bssid+",SIGNAL:"+signal+",GPS:"+avg_lat+","+avg_lon 

output = output + "\n </Document>\n</kml>"

if ap_counter == 0:
 print("\nNOT RESULTS FOUND! Try to filter less.")
 output = ""						# be careful here

# Statistics:
if args.stat:
 print("Found ESSIDs:")
 for x in apdict:
  print(x,apdict[x])
#sys.exit(1)
 
if args.d:
 print(output)

# Write output to file
if kmlfile:
 if ap_counter > 0:
  f = open(kmlfile, "a")
  f.write(output)
  f.close()
  sys.stderr.write("Results successfully written into:"+str(kmlfile)+"\n")
 else:
  print("Nothing writeen into file. We have no results.")

"""
<Placemark>
    <name>Visitor,-75dBm</name>
    <description>Visitor AP</description>
    <!-- <description>This is a new point.</description> --> 
    <styleUrl> #mystyle</styleUrl> 
    <Point>
     <coordinates>14.358,50.048,0.</coordinates>
    </Point>
  </Placemark>

"""

# blue, red, yellow, green, blue, purple, black

sys.exit(0)

# Idea show only places with best signal!

# riadok 236 still messing up

# bug essid becomes sometimes None
# because signal is reverse to line heigh we do simple math: -80dBm is max 80-signal=value

# nejaka bugu s cp, ked tam je tak neukazuje dane apcko
# ked ma essid vo vypise specialny znak napr. &, tak to to xmlko vyhodnoti ako chybu
# napr. <name chan="8">Tom&Gabi,-57dBm</name>
# enc filtering nefunguje..
# allow to show clients, not just ap

# almost done, do not fucked up!

# if icons are missing you must place them to directory where .kml is
