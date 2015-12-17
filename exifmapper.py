################################################################################
# Justin Schoenfeld & Jorge Rojas
# ExifMapper
# Maps GPS data from JPG files using the Google Maps Static API and exiftool.exe
################################################################################

import string,sys,os
import subprocess
import re
import argparse

parser = argparse.ArgumentParser(description='Maps GPS coordinates from EXIF data. Requires exiftool.exe (http://www.sno.phy.queensu.ca/~phil/exiftool) Rename it exiftool.exe and store in same local directory')
parser.add_argument('directory', help='Directory to search')
parser.add_argument('-r', '--recursive', help='Recursively scan directory', action='store_true')
parser.add_argument('-c','--center', help='A specific location to center the map to (Enter location surrounded in quotes) Options can be:  Addresses, GPS coordinates, zip codes, States, Cities, etc.')
parser.add_argument('-z', '--zoom', help='Enter a zoom level for map.  0 for lowest, 21+ for highly zoomed in.')
#parser.add_argument('-e', '--file', help='Enter a file to view raw Exifdata')
args = parser.parse_args()

print ("Searching the directory for files.....\n")

Final_GPS_Coords = {}		
JPG_Files = []
if args.recursive is True:
	#Search for JPG files in the filesystem
	for root, dir, files in os.walk(str(args.directory)):
		for fp in files:
			fp = fp.upper()
			if re.search('\.JPG$|\.PNG$|\.MOV$', fp):			
				fn = root+'/'+fp
				JPG_Files.append(fn)
elif args.recursive is False:
	#files = [f for f in os.listdir(args.directory) if os.path.isfile(f)]
	files = os.listdir(args.directory)
	for file in files:
		file = file.upper()
		if re.search('\.JPG$|\.PNG$|\.MOV$', file):
			fn = args.directory+'/'+file
			JPG_Files.append(fn)

print ("Found " + str(len(JPG_Files)) + " files")

#Search for GPS data in the JPG/MOV/MP4/ Files
for jpg in JPG_Files:
	print ("\nFound a file in: " + jpg + " searching for GPS data...")
	current_cir = "\"" + os.getcwd() + "\""
	command = os.getcwd() + "\\" + "exiftool.exe " + "\"" + jpg +"\""
	#Execute exiftool.exe which should be in the same local directory and store the output
	output = subprocess.Popen(command, stdout=subprocess.PIPE)
	exifdata = filter(lambda x:len(x)>0,(line.strip() for line in output.stdout))

	#Create a new list for GPS data
	GPS = []
	CreateDate = {}
	date= ""
	for line in exifdata:
		#line = line.decode(encoding="UTF-8", errors="strict")
		if b"GPS" in line:
			line = line.decode(encoding="UTF-8", errors="strict")
			GPS.append(line)
#		elif re.search('^Create Date', line):
#			#line = line.decode(encoding="UTF-8", errors="strict")
#			date  = line.split(':')
#			print (date)
#			CreateDate[jpg] = date

	#Create a new dictionary for GPS information where the GPS Position is the key and the 
	#coordinate is the value 
	GPS_info = {}
	for coord in GPS: 
		coord = coord.split(':')
		coord[0] = re.sub(r'\s*$', '', coord[0], flags=re.IGNORECASE)
		coord[1] = re.sub(r'deg', '', coord[1], flags=re.IGNORECASE)
		coord[1] = re.sub(r',', '', coord[1], flags=re.IGNORECASE)
		#create key value pairs for accessing GPS information
		GPS_info[coord[0]] = coord[1]
	#See if the JPG file actually had any GPS data inside of it
	#Use the filename as a key and make the coordinates the value
	if 'GPS Position' in GPS_info:
		Final_GPS_Coords[jpg] = GPS_info['GPS Position']
	
		#command = os.getcwd() + "\\" + "exiftool.exe -CreateDate " + "\"" + jpg +"\""
		#Execute exiftool.exe which should be in the same local directory and store the output
		#print (command)
		output2 = subprocess.Popen(command, stdout=subprocess.PIPE)
		CreateDateLine = filter(lambda x:len(x)>0,(line.strip() for line in output2.stdout))
		#date = output.split(":")
		#print (date)
		#print (CreateDateLine)

	else:
		continue

#Create markers for our final Google Maps URL
base_marker = "markers=color:blue|label:"
marker = ""

#Create the URL parameter to list all of the markers for the locations we found
x=0 #A counter to see how many coordinates/files we found
Label_Tracker ={}
#Every possible label for the google maps static API.  Only able to have 36 labels on a map at time which should be a sufficient amount
Letters = { '1':'1', '2':'2', '3':'3', '4':'4', '5':'5', '6':'6', '7':'7', '8':'8', '9':'9',
			'10': 'A', '11': 'B', '12' : 'C', '13':'D', '14':'E', '15':'F', '16':'G', '17':'H', '18':'I', '19':'J', '20':'K', '21':'L', '22':'M',
			'23':'N', '24':'O', '25':'P', '26':'Q', '27':'R', '28':'S', '29':'T', '30':'U', '31':'V', '32':'W', '33':'X', '34':'Y', '35':'Z' }
#Create the URL parameter to list all of the markers for the locations we found
for coord in Final_GPS_Coords.values():
	#if x < 9:
	x = x + 1
	x=str(x)
	marker += base_marker + Letters[x] + "|" + coord + "&"
	Label_Tracker[x] = coord
	x=int(x)
	#else: #we need to use letters if we have over 9 pictures because of the Google Maps API limit on their Labels
	#	x = x +1 
	#	x = str(x)
	#	marker += base_marker + Letters[x] + "|" + coord + "&"
	#	Label_Tracker[x] = coord
	#	x=int(x)

#Remove any extra trailing "&" after crafting the marker URL
marker = re.sub(r'&$', '', marker, flags=re.IGNORECASE)
x = str(x)
print ("\n\nFound " + x + " file(s) with GPS coordinates\n\n")

# Ready to plug the coordinates into google 
key = "key=AIzaSyBhnG9rbyb8Z4hS88tiQ3qqoZr9a4Hr48Y"
if args.center and args.zoom:
	baseurl = "https://maps.googleapis.com/maps/api/staticmap?" + key + "&" + "center=" + args.center + "&" + "zoom=" + args.zoom
elif args.zoom:
	baseurl = "https://maps.googleapis.com/maps/api/staticmap?" + key + "&" + "zoom=" + args.zoom
elif args.center:
	baseurl = "https://maps.googleapis.com/maps/api/staticmap?" + key + "&" + "center=" + args.center
else:
	baseurl = "https://maps.googleapis.com/maps/api/staticmap?" + key

scale = "scale=2"
size = "size=1024x1024"
base_color = "&color:blue"

#Craft our Final Google Maps URL and print out the files we found
#Labe_Tracker is so that we can create Labels on the map to associate which file is where on the map
#We need to match the coordinates from both of our dictionaries so if they're equal we'll be able to 
#match the appropriate labels so that our labels are accurate
for jpg in Final_GPS_Coords:
	for i in Label_Tracker:
		if Final_GPS_Coords[jpg] == Label_Tracker[i]: #If we find two coordinates that are equal, proceed
			print ("========================================================================================================================================================================================")
			print ("File Identifier:  " +  Letters[i]  )
			#print ("File Create Date: " +  CreateDate[jpg])
			print ("Raw GPS:         " + Final_GPS_Coords[jpg])
			per_coord_url = baseurl + "&" + scale + "&" + size + "&" + base_marker + Label_Tracker[i]
			per_coord_url = re.sub(r'label:\s', '', per_coord_url, flags=re.IGNORECASE)
			print ("File:             " + jpg + "\nGoogle Map Link:  " + per_coord_url )
			per_coord_url = "" 
			print ("========================================================================================================================================================================================\n\n\n")

if int(x) > 0 :
#Put together all of the strings for the final URL if we find any files with GPS Information
	Final_url = baseurl + "&" + scale + "&" + size + "&" + marker
	print ("THE URL FOR YOUR MAP:\n" + Final_url)
else:
	print ("Could not find any files with GPS information...Maybe you mistyped the directory\n")
