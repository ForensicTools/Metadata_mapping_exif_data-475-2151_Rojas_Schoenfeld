import string,sys,os
import subprocess
import re

Final_GPS_Coords = {}		
JPG_Files = []
for root, dir, files in os.walk(str(sys.argv[1])):
		for fp in files:
			if ".JPG" in fp.upper():
				fn = root+'/'+fp
				JPG_Files.append(fn)

for jpg in JPG_Files:
	#print ("\nFound a JPG in: " + jpg + " searching for GPS data...\n")
	current_cir = "\"" + os.getcwd() + "\""
	command = os.getcwd() + "\\" + "exiftool.exe " + "\"" + jpg +"\""
	output = subprocess.Popen(command, stdout=subprocess.PIPE)
	exifdata = filter(lambda x:len(x)>0,(line.strip() for line in output.stdout))
	#print ("Checking if " + jpg + " has any GPS information in its EXIF DATA\n\n")

	GPS = []
	for line in exifdata:
		if b"GPS" in line:
			line = line.decode(encoding="UTF-8", errors="strict")
			GPS.append(line)

	GPS_info = {}
	for coord in GPS: 
		coord = coord.split(':')
		coord[0] = re.sub(r'\s*$', '', coord[0], flags=re.IGNORECASE)
		coord[1] = re.sub(r'deg', '', coord[1], flags=re.IGNORECASE)
		GPS_info[coord[0]] = coord[1]

	if 'GPS Position' in GPS_info:
		Final_GPS_Coords[jpg] = GPS_info['GPS Position']
	else:
		continue

base_marker = "markers=color:blue|label:"
marker = ""
#Create the URL parameter to list all of the markers for the locations we found
x=0
Label_Tracker ={}
#Create the URL parameter to list all of the markers for the locations we found
for coord in Final_GPS_Coords.values():
	x = x + 1
	x=str(x)
	marker += base_marker + x + "|" + coord + "&"
	Label_Tracker[x] = coord
	x=int(x)

marker = re.sub(r'&$', '', marker, flags=re.IGNORECASE)
x = str(x)
print ("Found " + x + " files with GPS coordinates\n\n")

# Ready to plug the coordinates into google 
key = "key=AIzaSyBhnG9rbyb8Z4hS88tiQ3qqoZr9a4Hr48Y"
baseurl = "https://maps.googleapis.com/maps/api/staticmap?" + key
scale = "scale=2"
size = "size=1024x1024"

for jpg in Final_GPS_Coords:
	for x in Label_Tracker:
		if Final_GPS_Coords[jpg] == Label_Tracker[x]:
			print ("=======================================================================================")
			print ("File Number " +  x  )
			print ("Value of " + x )
			print ("Raw GPS " + Final_GPS_Coords[jpg])
			per_coord_url = baseurl + "&" + scale + "&" + size + "&" + base_marker + Label_Tracker[x]
			per_coord_url = re.sub(r'label:\s', '', per_coord_url, flags=re.IGNORECASE)
			print ("File   ----->  " + jpg + "\nGoogle Map Link:  " + per_coord_url )
			per_coord_url = ""
			print ("=======================================================================================\n\n\n")

Final_url = baseurl + "&" + scale + "&" + size + "&" + marker
print ("THE URL FOR YOUR MAP:\n" + Final_url)
