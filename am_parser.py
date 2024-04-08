#!/usr/bin/python3

import xml.etree.ElementTree as ET
import sys
from termcolor import colored
import re

dangerous_permissions = [
		"android.permission.READ_CALENDAR", 		# CALENDAR
		"android.permission.WRITE_CALENDAR",
		"android.permission.CAMERA",					# CAMERA
		"android.permission.READ_CONTACTS",
		"android.permission.WRITE_CONTACTS",
		"android.permission.GET_ACCOUNTS",
		"android.permission.ACCESS_FINE_LOCATION", # LOCATION
		"android.permission.ACCESS_COARSE_LOCATION",
		"android.permission.RECORD_AUDIO",			 # MICROPHONE
		"android.permission.READ_PHONE_STATE",		 # PHONE
		"android.permission.CALL_PHONE",
		"android.permission.READ_CALL_LOG",
		"android.permission.WRITE_CALL_LOG",
		"android.permission.ADD_VOICEMAIL",
		"android.permission.USE_SIP",
		"android.permission.PROCESS_OUTGOING_CALLS",
		"android.permission.BODY_SENSORS",			# SENSORS
		"android.permission.SEND_SMS",				# SMS
		"android.permission.RECEIVE_SMS",
		"android.permission.READ_SMS",
		"android.permission.RECEIVE_WAP_PUSH",
		"android.permission.RECEIVE_MMS",
	   "android.permission.READ_EXTERNAL_STORAGE", #STORAGE
		"android.permission.WRITE_EXTERNAL_STORAGE",
]

perm_count = 0 # perm count
activity_count = 0
serv_count = 0
prov_count = 0
recv_count = 0

manifest="Manifest attributes"
permissions="permissions"
act='activities'
serv='services'
prov='providers'
recv='receivers'
stats="statistics"

# dangerous permissions list

dlist = list()
exported = list()

filename = ""
try:
 filename = sys.argv[1]
except: 
 print("You need to use AndroidManifest.xml as 1. argument of this program! Otherwise you do not know what are you doing!")
 sys.exit(1)

try:
 tree = ET.parse(filename)
except: 
 print("Manifest file incomplete or damaged. Unable to parse file !")
 sys.exit(1)

root = tree.getroot()
schema='{http://schemas.android.com/apk/res/android}'

app = root.find('application')

print()
print("Manifest details")
print("| Tag | value |")
print("| :----: | :----: |");

md = root.attrib
for a in md:
 print("| ",end="")
 print(a.replace(schema,""),md[a],sep=" | ",end="")
 print(" |")
 
print()
print("| Permissions |")
#print("*" * len(permissions))
print("| :----: |")
for x in root.iter('uses-permission'):
 d = x.attrib
 for y in d: # iterate over new dictionary and get values instead of keys
   perm = d[y].lstrip()

   if perm in dangerous_permissions:
    dlist.append(perm)
   print("| "+perm + " |") 
   perm_count+=1 

# 
print()
print("| Application attributes |")
print("| :----: | :----: |");

unwanted = ["icon","label","roundIcon","theme","supportsRtl"]

for elem in app.iter('application'):
 attr = elem.attrib
 for x,y in attr.items():
  x = x.replace(schema,"")

  # remove unwated attributes
  if x in unwanted:
   continue

  if (re.search("usesCleartextTraffic",x) or re.search("debuggable",x) or re.search("allowBackup",x) or re.search("exported",x)):
   print(colored("| " + x + " | " + y + " |","yellow"))
  else:
   print("| " + x + " | " + y + " |")
  
# get activities
activity_count = len(app.findall('activity'))

print()
print("| Activities |")
# print("*" * len(act))
print("| :---- |")

for e in app.findall('activity'):
 attr = e.attrib
 print("| " + attr[schema+'name'] + " |")

 # if android:exported is true append to exported list
for x,y in attr.items():
	x = x.replace(schema,"")
	print(f"DEBUG:{x}:{y}")
	if x == "exported" and y == true:
		exported.append(attr[schema+'name'])


# get services

#services_count = len(app.findall('service'))
print()
print("| Services |")
# print("*" * len(serv))
print("| :---- |")
for e in app.findall('service'):
	attr = e.attrib
	print( "| " + attr[schema+'name'] + " |")
	serv_count+=1
 # if android:exported is true append to exported list
	for x,y in attr.items():
		x = x.replace(schema,"")

		# skip disabled services even if exported
		if x == "enabled" and y == "false":
			break
		if x == "exported" and y == "true":
		 exported.append(attr[schema+'name'])

print()
print("| Providers |")
# print("*" * len(prov))
print("| :---- |")

# get providers
for e in app.findall('provider'):
 attr = e.attrib
 print("| " + attr[schema+'name'] + " |")
 prov_count+=1
 # if android:exported is true append to exported list
 for x,y in attr.items():
  x = x.replace(schema,"")
  
 # get exported
 if attr[schema+'exported']:
  exported.append(attr[schema+'name'])
   

print()
print("| Receivers |")
# print("*" * len(serv))
print("| :---- |")

# get receivers 

for e in app.findall('receiver'):
 attr = e.attrib
 print("| " +attr[schema+'name'] +" |")
 recv_count+=1
 # if android:exported is true append to exported list
 for x,y in attr.items():
  x = x.replace(schema,"")
  if x == "exported" and y == "true":
   exported.append(attr[schema+'name'])

# STATS
print()
# print("*" * len(stats))

print("| Statistics |")
print("| :----: | :----: |")
print("| Permissions | "+str(perm_count)+" |")
print("| Activities | "+str(activity_count) +" | ")
print("| Services |"+str(serv_count) +" | ")
print("| Provider | "+str(prov_count) + " | ")
print("| Receivers | "+str(recv_count) +" | ")

# get receivers 
#print(f'application:')
#for e in app.findall('application'):
 #attr = e.attrib
 #print("| " + attr[schema+'name'] +" |")

if dlist:
 print("")
 print("| Dangerous permissions |")
 print("| :---- |")
 for xperm in dlist:
  print(f"| {xperm} ")

 print("\nOn Anroid > 6 (API level 23) you need to request above permissions during runtime. We explicitly checked for those permissions in application code.")
# print exported components

if exported:
 print("")
 print("| Exported components |")
 print("| :---- |")
 for ex in exported:
  print(f"| {ex} |")

# final empty line 
print()

# BUGS
# exported=true not added even if activity is exported properly

## add network_security_config

# choose language
# get application debugable, backup, exported components
# network security config
