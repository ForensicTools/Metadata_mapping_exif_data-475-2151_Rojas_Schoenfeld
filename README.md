# Metadata_mapping_exif_data-475-2151_Rojas_Schoenfeld
Mostly all pictures, videos, documents taken with a smartphone, or created with a computer will have metadata associated with it.  Some of this metadata allows us to create maps and timelines of where these pictures were taken.  Using ExifTool.exe, we can scrape out GPS coordinates from pictures and documents then using an API we can plot these coordinates in Google Maps or some similar mapping program.  This can help forensic investigators and law enforcement identify the location of interesting places in an investigation or show the origin in which a file was created.  

==================================================================================================================
In order to run the tool you first need to install exiftool.exe from http://www.sno.phy.queensu.ca/~phil/exiftool
Rename it exiftool.exe and store it in the same directory as the exifmappy.py
Next, download the python libraries used in exifmapper.py if they are not installed already:
  - pip install string
  - pip install os
  - pip install subprocess
  - pip install re
  - pip install sys

In order to use the tool you need to register for a Google Maps Static API key.  
Around line 57 you should enter in your key.  




