# this file works in conjunction with the apache2 module, mod_wsgi
# (libapache2-mod-wsgi-py3 - Python 3 WSGI adapter module for Apache)
# the paths will need to be absolute, and coorispond to the paths for your system
# In addition to this file, you will also need to configure apache2 to load this

#activate_this = '/home/plchuser/apps/patron-savings-calculator/venv/bin/activate_this.py'

#with open(activate_this) as file_:
#    exec(file_.read(), dict(__file__=activate_this))

from app import app as application
