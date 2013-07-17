WebDAVNav Redirector
=====================

This is a simple python script to show how you can redirect initial connections when using the mobile application WebDAV Nav on iOS and Android.
This would be of most use to organisations that have shared devices and each user has their own folder for storing documents on the server.
This could also be used to redirect different users/classes to different servers if required.

WebDAV Navigator for iPhone and Android
---------------------------------------
[App Store](https://itunes.apple.com/app/webdav-nav/id412341302?mt=8)  
[Google Play](https://play.google.com/store/apps/details?id=com.schimera.webdavnav)

Background
-----------
Both WebDAV Nav for iOS v1.7.4+ and WebDAV Nav for Android v1.26+ support redirects (HTTP 302 or 307) on the initial request to retrieve a list of files.
It is therefore possible to setup a generic URL in all shared devices without storing the authentication details for any users.

On the initial attempt to connect, the generic URL can request the user to enter their authentication details. 
When the app then submits the authentication details, the generic script could extract the username and construct a new URL endpoint to redirect the app to. 

**for example**  

  * The app is configured with a URL of http://example.org/, with no username or password entered
  * The user attempts a connection to http://example.org/, the server responds requesting username and password
  * A pop up appears on the users device requesting username and password, and then resubmits the request
  * The server extracts the username from the request, and then sends a redirect response (HTTP 302 or 307) to the app with the users custom URL e.g. http://server2.example.org/username/
  * The app then follows the redirect and connects to the new URL endpoint http://server2.example.org/username/
  * To the user it appears that they have connected directly to their own folder

Many servers can be configured directly to do some basic redirects. e.g. using mod_rewrite or similar
  
Installation
-------------
WebDAVNav Redirector is a single file script written in Python that can be run on most platforms with minimal additional configuration. 

### Unix/Linux
Simply copy the .py file to a folder of your choice and run it from the command line using the options you require.

### Windows
Because the script is written in Python, you would likely need to install Python in order to run it.   
[Python 2.7.5 download](http://www.python.org/getit/)  
Once installed, simply copy the .py file to a folder of your choice. Create a .bat file to launch the script using the options you require.

Options
-------------
The script accepts a couple of basic command line parameters in order to set the available options

    usage: webdavnav_redir.py [-h] [-l L] [-p P] [-f F] [-c C]

    WebDAVNav Redirector

    optional arguments:
      -h, --help  show this help message and exit
      -l L        Address to listen on
      -p P        Port to listen on
      -f F        Redirect url format     
  
By default the app will listen on all available addresses for incoming connections on port 8080.
Connections will also by default be redirected to http://current_host/username/
Using the command line options you can configure which IP address and Port to use, as well as the default format for the redirected URL. 

**Examples**

    python webdavnav_redir.py -l 192.168.1.100 -p 9091 -f "http://example.org/{{username}}/"  
    
    python webdavnav_redir.py -p 8081 -f "http://{{host}}/webdav/{{username}}"
    
Advanced Example
-----------------
The script allows you to extend the lookup behaviour by implementing a lookup to a database table or some other lookup.
The example_plugin.py file includes some basic examples of constructing your own URL using Python.
Within this routine you could perform a database, ldap or other query in order to calculate the correct URL required for the user.
In order to use the advanced mechanism, copy the contents of the example_plugin.py file to plugin.py and edit the contents.

Configure the script to use SSL
--------------------------------
The script can be configured to use SSL rather than plain HTTP. In order to use SSL you need to include a link to a suitably encoded .pem certificate file. 
Replace the line at the top of the certificate with the correct path to your file

    SSL_CERTIFICATE = None

    SSL_CERTIFICATE = 'server.pem'

To generate a self-signed certificate for testing purposes you can use the following command on a Unix/Linux machine.

    openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes
