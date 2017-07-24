#!/usr/bin/env python

import glob, os
from shutil import copyfile


webh_config_path = '/home/catalin/Desktop/etc/www'
site_name = 'fqdn.tld'


print 'Copying template vhosts config files and make necessary replacements ...'
for file in glob.glob("files/vhosts/fqdn-*.conf"):
	copyfile(file, webh_config_path+'/'+site_name+file.split('fqdn')[1])
	os.popen("sed -i 's/{SITE_NAME}/"+site_name+"/g' "+webh_config_path+'/'+site_name+file.split('fqdn')[1])
