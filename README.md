# SongsPlatform

*    Title: Songs Platform        
*    Author: Guillem Nicolau Alomar Sitjes      
*    Initial release: July 23rd, 2017                     
*    Code version: 0.1                         
*    Availability: Public                      

This client<->server application simulates the behaviour of a music database service, with different channels and songs being reproduced in them.

Requirements:
 - Python+2.5 (not tested on python3, at least the prints should be removed)
 - SQLite3: is already installed in Python +2.5, so you don't need to install it.
 - Web.py: 
    pip install web.py

After loading the songs and plays information, the user will be able to use the service to find when has a song been reproduced and in which channels, get the songs that have been reproduced in a channel in a specified period of time, and get the top songs in the current week (in descending order, by the number of times it's been played since a specified time).

To use the application, first you should start by running the server:

    python webservice.py [-H hostname] [-P port]

Once the server is up (it shouldn't take more than a few seconds), you can run the testing application:

    python test.py [-H hostname] [-P port] [--add-data]
    
The '--add-data' option should be used the first time, as it creates a folder named 'data', and an empty file that will be used by the SQLite database. If you already have a file from a previous execution, you can put it in that folder, and the server will adopt it as if it was his own.

In case that the server has any problem when filtering the data, some descriptive errors will be shown.
