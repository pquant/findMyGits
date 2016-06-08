# findMyGits
A small python program for the bash terminal to list all local git repos. Outputs bare repos first, then working repos with corresponding remotes and status. Missing remotes and modified status appear in red

# Tested on...
Ubuntu 16.04 (Xenial), Windows 10 (with cygwin)

# Install
* Linux:
      * git clone to _some_location_: you now have the bash script _findmygits_ in the _some_location/findMyGits/_ folder 
      * add the folder _some_location/findMyGits/_ to your _PATH_ environment variable (typically in your .bashrc as _PATH=$PATH:/some_location/findMyGits_): you should now be able to call _findmygits_ from the terminal

* Windows: same as above if done from the Cygwin terminal (note that any git repo installed outside _C:\cygwin\$HOME_ won't be picked up as it is the home directory in Cygwin). Not implemented for native Windows command prompt.

# _findmygits -h/--help_
usage: Lists all local git repos on your computer. Prints bare repos and working repos (with corresponding remotes and statuses
       [-h] [--exclude-dirs [dir [dir ...]]] [--include-only dir]

optional arguments:
  -h, --help            show this help message and exit
  --exclude-dirs [dir [dir ...]]  Directories to exclude
  --include-only dir    One Directory to include exclusively
