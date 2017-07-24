#!/usr/bin/env python

import glob, os


webh_config_path = '/home/catalin/Desktop/etc/www'
site_name = 'fqdn.tld'

print os.popen("echo $(pwd)").read()
exit(0)

os.chdir(webh_config_path)
print ''
for file in glob.glob("fqdn-*.conf"):
	print "Configuring "+file+" ..."
	print os.popen("sed -i 's/{SITE_NAME}/"+site_name+"/g' "+file).read()
	
	
