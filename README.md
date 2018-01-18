# BlackHatPython
<b>Reworked (and working!) scripts from Black Hat Python</b>

Many of the scripts in the book don't work or are outdated. These are my reworks of all the scripts from the book, working and updated. Still built for Python 2.x.

Main differences:
<br>
<br>
<b>pycat.py</b>
<ul>
  <li>used argparse instead of getopt for cmd line parsing</li>
  <li>created network protocol to get rid of the blocking issues of original script</li>
  <li>added change dirctory functionality to cmd shell</li>
  <li>added cat ascii art</li>
 </ul>
 <br>
 <b>tcp-proxy.py</b>
 <ul>
    <li>instead of having to manually choose if the application needs to receive data first,
      it will automatically listen then time out if nothing arrives before entering loop</li>
  </ul>
