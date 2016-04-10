Wrote this script to download the different podcasts I listen to, speed them up each by their own suitable degree and then move them into a folder on my phone.
Works on Linux and requires python 3.
To do this it has a configuration file that contains the location of the folder to save the files to and the folder to send the sped up files to as well as the required speedup ratios.
The repo contains an example configuration called shorten-example.cfg. When the script is called it will first try to read the configuration file called shorten.cfg. **Be sure to change the name of the config file to match that when trying to run it**. 
Possible future improvements (that I don't need myself but might do if asked):
 - Add support for python2
 - Add command line options to ad hoc change the configuration settings
 - Add option to delete downloaded files at the end