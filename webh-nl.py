#!/usr/bin/python
import glob, os, sys, shutil, subprocess

info = """
--------------------------------------------------------
# WebH-NL virtual hosts helper
# This tool is an automation helper for
# the WebH-NL project - virtual hosts management
#
# Author: b247
# Project details: https://www.b247.eu.org/
--------------------------------------------------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\\
                ||----w |
                ||     ||
"""

##################################################
# menus
##################################################
class Menu:
	main_menu_options = [
		('New site','new()'),
		('Manage sites (enable/disable/delete)','site()'),
		('Exit','exit()'),
	]
	site_menu_options = [
		'enable_site()',
		'disable_site()',
		'delete_site()',
	]
	
	# the start menu	
	def start(self):
		print color.light_yellow+50 * "-"+color.default
		for index, item in enumerate(self.main_menu_options):
			print str(index+1)+'. '+item[0]
		print color.light_yellow+50 * "-"+color.default
		valid_selection = False
		while valid_selection != True:
			try:
				self.selection = input(">> [1-"+str(len(self.main_menu_options))+"]: ")
				valid_selection = 1 <= self.selection <= len(self.main_menu_options)
				if not valid_selection:
					raise Exception() 
			except KeyboardInterrupt:
				Manage().exit()
			except :
				print 'Invalid option, try again'
		try :
			func = 'Manage().'+self.main_menu_options[self.selection-1][1]
			eval(func)
		except KeyboardInterrupt:
				Manage().exit()
		except Exception as e:
			print 'Ooups, the option you have selected is not working or not yet implemented'
			print e
			self.start()

	
##################################################
# main actions (create/enable/disable/delete site)
##################################################
class Manage:
	#server paths
	sites_config_path = '/etc/www/'
	sites_storage_path = '/var/www/'
	
	# exit
	def exit(self):
		print
		sys.exit(0)
		
	# new()
	# actions: create /etc/www/site_name*, create /var/www/site_name folder, create site_name_clean system user, restart services
	def new(self):
		print color.light_yellow+50 * "-"+color.default
		print 'Enter the Fully Qualified Domain Name (FQDN) for the site, ex: example.com, without www'
		self.site_name = raw_input(">> [FQDN]: ")
		self.site_name_have_www = self.site_name.split('www.')[0] == ''
		if self.site_name_have_www:
			self.site_name = self.site_name[4:]
		self.site_user = 'www-'+self.site_name.replace('.','-')
		
		print color.light_yellow+50 * "-"+color.default
		print 'Creating the system user for %s ...' %(self.site_name)
		print color.light_yellow
		try:
			subprocess.check_call(['useradd','-r',self.site_user])
		except :
			pass
		print os.popen('getent group | grep '+self.site_user).read()+color.default		
		
		print 'Creating the config files for %s ...' %(self.site_name)
		for file in glob.glob("files/vhosts/fqdn-*.conf"):
			self.server_type_ext = file.split('fqdn')[1]
			shutil.copyfile(file, self.sites_config_path+self.site_name+self.server_type_ext)
			os.popen("sed -i 's/{SITE_NAME}/"+self.site_name+"/g;s/{SITE_USER}/"+self.site_user+"/g' "+self.sites_config_path+self.site_name+self.server_type_ext)
		print color.light_yellow		
		subprocess.call(['find','/etc/www/','-name',self.site_name+'-*.conf'])
		print color.default
		print 'Creating the storage tree for %s ...' %(site_name)
		
		exit(0)
		
		print 'dodo, chown root:www-data site_name ...'
		print 'dodo, chmod 0770 fqdn ...'
		print 'dodo, create user site_name_clean'
		#	create_system_user(), add www-data as primary group???, for sftp editing capabilities?
		print 'dodo, set www-data as primary group for user site_name_clean'
		print 'dodo, get nginx,apache,php configs from github'
		print 'dodo, replace default.tld with site_name and www-default-tld with site_name_clean, inside confs'
	
		restart_servers()
		print color.light_green+site_name+color.default+' is now created and enabled, waiting for your scripts to be executed '
		print

# enable_site()
# actions:
# move /etc/www/site_name*.conf.disabled to /etc/www/site_name*.conf
# restart_servers()
def enable_site():
	print 50 * "-"
	os.chdir(sites_config_path)
	for file in glob.glob(site_name+"-*.conf.disabled"):
		conf_available = str(file).split(site_name)[1].split('.disabled')[0]
		print 'Enabling '+color.light_green+site_name+color.default+conf_available
		os.rename(file,file.replace('.disabled',''))
	restart_servers()
	print color.light_green+site_name+color.default+' is now enabled'
	print color.light_yellow+'Don\'t forget that you can fine tune server for this site\nusing the above configuration files (located at /etc/www).'+color.default
	print

# disable a site: move /etc/www/fqdn*.conf to /etc/www/fqdn*.conf.disabled, restart services
def disable_site():
	print 50 * "-"
	os.chdir(sites_config_path)
	for file in glob.glob(site_name+"-*.conf"):
		os.rename(file,file.replace('.conf','.conf.disabled'))
		conf_available = str(file).split(site_name)[1]
		print 'Disabling '+color.light_red+site_name+color.default+conf_available
	restart_servers()
	print color.light_red+site_name+color.default+' is now disabled'
	print

#delete a site: remove /etc/www/fqdn*, remove /var/www/fqdn, remove site_name_clean user, restart services
def delete_site():
	print 50 * "-"
	os.chdir(sites_config_path)
	for file in glob.glob(site_name+"*"):
		try:
			os.remove(file)
			print 'Removing '+color.light_red+file+color.default
		except OSError:
			pass
	print 'Removing '+color.light_red+sites_storage_path+'/'+site_name+color.default
	try:	
		shutil.rmtree(sites_storage_path+'/'+site_name)
	except OSError:
		pass 
	delete_system_user()	
	restart_servers()
	print color.light_red+site_name+color.default+' is now deleted'
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
	


# list of selectable available sites  	
def manage_sites():
	available_sites()
	global site_name
	print color.light_blue+'\n'+35*'-'+'AVAILABLE SITES'
	
	for index,site in enumerate(all_sites):
		if site in enabled_sites:
			print color.light_green+str(index+1)+'. '+site+(' '+(39-len(site))*'-')+'ENABLED'+color.default
		else:
			print color.light_red+str(index+1)+'. '+site+(' '+(38-len(site))*'-')+'DISABLED'+color.default
	print color.light_blue+50*'-'+color.default
	selected_site = raw_input(">> [1-"+str(total_available_sites)+"]: ")
	
	try:
		selected_site = int(selected_site)
	except ValueError:
		return
	
	if selected_site <= total_available_sites:
		site_name = all_sites[selected_site-1]
		if site_name in disabled_sites:
			print color.light_red+site_name+color.default
			action = raw_input(">> [enable/delete]:")
			if action == 'enable':
				eval(site_menu_options[0])
			elif action == 'delete':
				eval(site_menu_options[2])
		else:
			print color.light_green+site_name+color.default
			action = raw_input(">> [disable/delete]:")
			if action == 'disable':
				eval(site_menu_options[1])
			elif action == 'delete':
				eval(site_menu_options[2])


	
	
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
	print color.default+'Setting the helper paths ...\n'+color.default+\
	'sites_config_path: '+color.blue+sites_config_path+color.default+'\n'\
	'sites_storage_path: '+color.blue+sites_storage_path+color.default
	print 'Scanning for available/enabled/disabled sites ...'
	print 'Found '+color.light_green+str(total_enabled_sites)+color.default+' enabled sites, '+color.light_red+str(total_disabled_sites)+color.default+' disabled sites, '+str(total_available_sites)+' total available sites'
	print

##################################################
# internal helpers
##################################################
# shell colors
class Color:
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
color = Color()
	
class tools:
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
	


##################################################
# main
##################################################
menu = Menu()

print color.light_yellow + info + color.default
menu.start()


exit(0)




# dodo
print color.light_yellow + info + color.default
available_sites()	
paths()
while menuLoop:
	start()
	choice = raw_input(">> [1-"+str(len(main_menu_options))+"]: ")
	try:
		choice = int(choice)
	except ValueError:
		continue
		
	if choice <= len(main_menu_options):
		choice-=1
		func = main_menu_options[choice][1]
		eval(func)