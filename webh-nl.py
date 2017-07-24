#!/usr/bin/python
import glob, os, signal, sys, shutil, subprocess

#declaring paths
sites_config_path = '/etc/www'
sites_storage_path = '/var/www'

menuLoop = True

info = """
--------------------------------------------------------
# WebH-NL virtual hosts helper
# This tool is an automation helper for
# the WebH-NL project - virtual hosts management
#
# Author: b247
# Project details: https://www.b247.eu.org/
--------------------------------------------------------
"""

#main menu
main_menu_options = [
	('Manage sites (enable/disable/delete)','manage_sites()'),
	('New site','new_site()'),
	('Exit','exit_menu()'),
]
#site_menu
site_menu_options = [
	'enable_site()',
	'disable_site()',
	'delete_site()',
]

# enable a site: move /etc/www/fqdn*.conf.disabled to /etc/www/fqdn*.conf, restart services
def enable_site():
	print 50 * "-"
	os.chdir(sites_config_path)
	for file in glob.glob(site_name+"-*.conf.disabled"):
		os.rename(file,file.replace('.disabled',''))
		conf_available = str(file).split(site_name)[1].split('.disabled')[0]
		print 'Enabling '+fcolor.light_green+site_name+fcolor.default+conf_available
	restart_servers()
	print fcolor.light_green+site_name+fcolor.default+' is now enabled'
	print fcolor.light_yellow+'Don\'t forget that you can fine tune server for this site\nusing the above configuration files (located at /etc/www).'+fcolor.default
	print

# disable a site: move /etc/www/fqdn*.conf to /etc/www/fqdn*.conf.disabled, restart services
def disable_site():
	print 50 * "-"
	os.chdir(sites_config_path)
	for file in glob.glob(site_name+"-*.conf"):
		os.rename(file,file.replace('.conf','.conf.disabled'))
		conf_available = str(file).split(site_name)[1]
		print 'Disabling '+fcolor.light_red+site_name+fcolor.default+conf_available
	restart_servers()
	print fcolor.light_red+site_name+fcolor.default+' is now disabled'
	print

#delete a site: remove /etc/www/fqdn*, remove /var/www/fqdn, remove site_name_clean user, restart services
def delete_site():
	print 50 * "-"
	os.chdir(sites_config_path)
	for file in glob.glob(site_name+"*"):
		try:
			os.remove(file)
			print 'Removing '+fcolor.light_red+file+fcolor.default
		except OSError:
			pass
	print 'Removing '+fcolor.light_red+sites_storage_path+'/'+site_name+fcolor.default
	try:	
		shutil.rmtree(sites_storage_path+'/'+site_name)
	except OSError:
		pass 
	delete_system_user()	
	restart_servers()
	print fcolor.light_red+site_name+fcolor.default+' is now deleted'
	print

#create a site: create /etc/www/fqdn*, create /var/www/fqdn, create site_name_clean system user, restart services
def new_site():
	print 50 * "-"
	print 'Enter the Fully Qualified Domain Name (FQDN) for the site, ex: example.com, without www'
	global site_name
	site_name = raw_input(">> [FQDN]: ")
	print 'Creating the config files for %s ...' %(site_name)
	print 'Test some things and exit'
	print subprocess.check_output('ls')
	exit(0)
	#for file in glob.glob("files/vhosts/fqdn-*.conf"):
#		server_type_ext = file.split('fqdn')[1]
#		copyfile(file, webh_config_path+'/'+site_name+server_type_ext)
#		os.popen("sed -i 's/{SITE_NAME}/"+site_name+"/g' "+webh_config_path+'/'+site_name+server_type_ext)
	
	print 'Creating the storage tree for %s ...' %(site_name)
	
	print 'dodo, chown root:www-data site_name ...'
	print 'dodo, chmod 0770 fqdn ...'
	print 'dodo, create user site_name_clean'
	#	create_system_user(), add www-data as primary group???, for sftp editing capabilities?
	print 'dodo, set www-data as primary group for user site_name_clean'
	print 'dodo, get nginx,apache,php configs from github'
	print 'dodo, replace default.tld with site_name and www-default-tld with site_name_clean, inside confs'

	restart_servers()
	print fcolor.light_green+site_name+fcolor.default+' is now created and enabled, waiting for your scripts to be executed '
	print

# restart webservers (apache/nginx/php-fpm)
def restart_servers():
	print
	print 'Restarting nginx ...'
	print os.popen("systemctl reload nginx").read()
	print 'Restarting apache ...'
	print os.popen("systemctl reload apache2").read()
	print 'Restarting php-fpm ...'
	print os.popen("systemctl reload php7.0-fpm").read()
	
# the start menu	
def main_menu():
	print fcolor.light_yellow+50 * "-"+fcolor.default
	for index, item in enumerate(main_menu_options):
		print str(index+1)+'. '+item[0]
	print fcolor.light_yellow+50 * "-"+fcolor.default

# list of selectable available sites  	
def manage_sites():
	available_sites()
	global site_name
	print fcolor.light_blue+'\n'+35*'-'+'AVAILABLE SITES'
	
	for index,site in enumerate(all_sites):
		if site in enabled_sites:
			print fcolor.light_green+str(index+1)+'. '+site+(' '+(39-len(site))*'-')+'ENABLED'+fcolor.default
		else:
			print fcolor.light_red+str(index+1)+'. '+site+(' '+(38-len(site))*'-')+'DISABLED'+fcolor.default
	print fcolor.light_blue+50*'-'+fcolor.default
	selected_site = raw_input(">> [1-"+str(total_available_sites)+"]: ")
	
	try:
		selected_site = int(selected_site)
	except ValueError:
		return
	
	if selected_site <= total_available_sites:
		site_name = all_sites[selected_site-1]
		if site_name in disabled_sites:
			print fcolor.light_red+site_name+fcolor.default
			action = raw_input(">> [enable/delete]:")
			if action == 'enable':
				eval(site_menu_options[0])
			elif action == 'delete':
				eval(site_menu_options[2])
		else:
			print fcolor.light_green+site_name+fcolor.default
			action = raw_input(">> [disable/delete]:")
			if action == 'disable':
				eval(site_menu_options[1])
			elif action == 'delete':
				eval(site_menu_options[2])

def exit_menu():
	exit('Have a nice day')
	
	
# scan /etc/www for sites configs	
def available_sites():
	os.chdir(sites_config_path)
	global enabled_sites, disabled_sites, all_sites
	enabled_sites = []
	disabled_sites = []
	all_sites = []
	for file in glob.glob("*-nginx.conf*"):
		site_available = str(file).split('-nginx.conf')[0]
		site_enabled = str(file).split('-nginx.conf')[1] == ''
		all_sites.append(site_available)
		if site_enabled :
			enabled_sites.append(site_available)
		else:
			disabled_sites.append(site_available)
	global total_enabled_sites,total_disabled_sites,total_available_sites
	total_enabled_sites = len(enabled_sites)
	total_disabled_sites = len(disabled_sites)
	total_available_sites = total_enabled_sites+total_disabled_sites
	all_sites.sort()

# inform admin about paths used and available sites
def paths():
	print fcolor.default+'Setting the helper paths ...\n'+fcolor.default+\
	'sites_config_path: '+fcolor.blue+sites_config_path+fcolor.default+'\n'\
	'sites_storage_path: '+fcolor.blue+sites_storage_path+fcolor.default
	print 'Scanning for available/enabled/disabled sites ...'
	print 'Found '+fcolor.light_green+str(total_enabled_sites)+fcolor.default+' enabled sites, '+fcolor.light_red+str(total_disabled_sites)+fcolor.default+' disabled sites, '+str(total_available_sites)+' total available sites'
	print

## other helpers
#Ctrl+C helper
def signal_handler(signal, frame):
	print
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
#color helper
class fcolor:
	default = '\033[0m'
	white = '\033[1;37m'
	light_white = '\033[0;37m'
	blue = '\033[1;34m'
	light_blue = '\033[0;34m'
	green = '\033[1;32m'
	light_green = '\033[0;32m'
	red = '\033[1;31m'
	light_red = '\033[0;31m'
	yellow = '\033[1;33m'
	light_yellow = '\033[0;33m'
	magenta = '\033[1;35m'
def site_name_clean_func():
	global site_name_clean
	site_name_clean = 'www-'+site_name.replace('.','-')	
def create_system_user():
	site_name_clean_func()
	print 'Creating system user '+site_name_clean+' ...'
	print os.popen("useradd -r "+site_name_clean).read()
def delete_system_user():
	site_name_clean_func()
	print 'Removing system user '+site_name_clean+' ...'
	print os.popen("userdel "+site_name_clean).read()
	
#main()
print fcolor.light_yellow + info + fcolor.default
available_sites()	
paths()
while menuLoop:
	main_menu()
	choice = raw_input(">> [1-"+str(len(main_menu_options))+"]: ")
	try:
		choice = int(choice)
	except ValueError:
		continue
		
	if choice <= len(main_menu_options):
		choice-=1
		func = main_menu_options[choice][1]
		eval(func)






