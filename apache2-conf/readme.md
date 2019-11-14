# Apache 2 config

This configuration shows how to set up apache to work with mod_wsgi (https://www.python.org/dev/peps/pep-3333/). 

you may need to install this on the server:

```
sudo apt-get install libapache2-mod-wsgi libapache2-mod-wsgi-py3
```

It can then be enabled for apache:

```
sudo a2enmod wsgi

```

Don't forget to restart apache to enable the module:

```
sudo service apache2 restart
```



