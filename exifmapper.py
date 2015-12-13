################################################################################
# Justin Schoenfeld
# MetaDataMapper
# Maps GPS data from JPG files using the Google Maps Static API and exiftool.exe
################################################################################

import string,sys,os
import subprocess
import re



Final_GPS_Coords = {}		
JPG_Files = []

#Search for JPG files in the filesystem
for root, dir, files in os.walk(str(sys.argv[1])):
		for fp in files:
			if ".JPG" or ".MOV" in fp.upper():			# ADD FEATURE FOR CUSTOM FILE FORMATS
				fn = root+'/'+fp
				JPG_Files.append(fn)

#Search for GPS data in the JPG Files
for jpg in JPG_Files:
	#print ("\nFound a JPG in: " + jpg + " searching for GPS data...\n")
	current_cir = "\"" + os.getcwd() + "\""
	command = os.getcwd() + "\\" + "exiftool.exe " + "\"" + jpg +"\""
	#Execute exiftool.exe which should be in the same local directory and store the output
	output = subprocess.Popen(command, stdout=subprocess.PIPE)
	exifdata = filter(lambda x:len(x)>0,(line.strip() for line in output.stdout))

	#Create a new list for GPS data
	GPS = []
	for line in exifdata:
		if b"GPS" in line:
			line = line.decode(encoding="UTF-8", errors="strict")
			GPS.append(line)

	#Create a new dictionary for GPS information where the GPS Position is the key and the 
	#coordinate is the value 
	GPS_info = {}
	for coord in GPS: 
		coord = coord.split(':')
		coord[0] = re.sub(r'\s*$', '', coord[0], flags=re.IGNORECASE)
		coord[1] = re.sub(r'deg', '', coord[1], flags=re.IGNORECASE)
		#create key value pairs for accessing GPS information
		GPS_info[coord[0]] = coord[1]
	#See if the JPG file actually had any GPS data inside of it
	#Use the filename as a key and make the coordinates the value
	if 'GPS Position' in GPS_info:
		Final_GPS_Coords[jpg] = GPS_info['GPS Position']
	else:
		continue


#Create markers for our final Google Maps URL
base_marker = "markers=color:blue|label:"
marker = ""

#Create the URL parameter to list all of the markers for the locations we found
x=0 #A counter to see how many coordinates/files we found
Label_Tracker ={}
#Every possible label for the google maps static API.  Only able to have 35 labels on a map at time which should be a sufficient amount
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
print ("Found " + x + " files with GPS coordinates\n\n")

# Ready to plug the coordinates into google 
key = "key=$GOOGLEMAPSSTATICAPIKEY"
baseurl = "https://maps.googleapis.com/maps/api/staticmap?" + key
scale = "scale=2"
size = "size=1024x1024"

#Craft our Final Google Maps URL and print out the files we found
#Labe_Tracker is so that we can create Labels on the map to associate which file is where on the map
#We need to match the coordinates from both of our dictionaries so if they're equal we'll be able to 
#match the appropriate labels so that our labels are accurate
for jpg in Final_GPS_Coords:
	for x in Label_Tracker:
		if Final_GPS_Coords[jpg] == Label_Tracker[x]: #If we find two coordinates that are equal, proceed
			print ("=======================================================================================")
			print ("File Identifier " +  Letters[x]  )
			print ("Raw GPS " + Final_GPS_Coords[jpg])
			per_coord_url = baseurl + "&" + scale + "&" + size + "&" + base_marker + Label_Tracker[x]
			per_coord_url = re.sub(r'label:\s', '', per_coord_url, flags=re.IGNORECASE)
			print ("File   ----->  " + jpg + "\nGoogle Map Link:  " + per_coord_url )
			per_coord_url = "" 
			print ("=======================================================================================\n\n\n")

#Put together all of the strings for the final URL
Final_url = baseurl + "&" + scale + "&" + size + "&" + marker
print ("THE URL FOR YOUR MAP:\n" + Final_url)
