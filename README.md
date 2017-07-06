# convox-clone
Clones all apps and their environment variables from one rack to a second rack.

Clones the current build image and promotes then this on the destination rack.

```
usage: convox-clone.py [-h] -s Ssurce -d destination -k key [-v Verbosity]
                       [-a [application [application ...]]]

Clones apps from one rack

optional arguments:
  -h, --help            show this help message and exit
  -s source             source rack (required)
  -d destination        destination rack (required)
  -k key                API key (required)
  -v verbosity          Verbosity: INFO|DEBUG
  -a [application [application ...]] Application name
 ```
