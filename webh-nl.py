#!/usr/bin/python
import glob, os, sys, shutil, subprocess

info = """
--------------------------------------------------------
# WebH-NL virtual hosts helper
# This tool is an automation helper for
# the WebH-NL project - virtual hosts management
#
# Author: b247
# Version: 1.0
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
		('Manage sites (enable/disable/delete)','sites()'),
		('Exit','exit()'),
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
	
	#def is_valid_hostname(hostname):
#    if len(hostname) > 255:
#        return False
#    if hostname[-1] == ".":
#        hostname = hostname[:-1] # strip exactly one dot from the right, if present
#    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
#    return all(allowed.match(x) for x in hostname.split("."))
    
	#exit()
	def exit(self):
		print
		sys.exit(0)
	# restart webservers (apache/nginx/php-fpm)
	def restart_servers(self):
		print 'Reloading nginx, apache2 and php-fpm servers ...'+color.light_yellow
		subprocess.call(['systemctl','reload','nginx'])
		subprocess.call(['systemctl','reload','apache2'])
		subprocess.call(['systemctl','reload','php7.0-fpm'])
		print color.default+'\nDone'
		Menu().start()
		
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
		print 'Creating the system user for '+self.site_name+' ...'+color.light_yellow
		try:
			subprocess.check_call(['useradd','-r',self.site_user])
			subprocess.check_call(['usermod','-G','www-data',self.site_user])
			subprocess.check_call(['usermod','-g','www-data',self.site_user])
		except :
			pass
		print os.popen('getent group | grep '+self.site_user).read()+color.default		

		print 'Creating the config files for '+self.site_name+' ...'+color.light_yellow
		for file in glob.glob("files/vhosts/fqdn-*.conf"):
			self.server_type_ext = file.split('fqdn')[1]
			shutil.copyfile(file, self.sites_config_path+self.site_name+self.server_type_ext)
			os.popen("sed -i 's/{SITE_NAME}/"+self.site_name+"/g;s/{SITE_USER}/"+self.site_user+"/g' "+self.sites_config_path+self.site_name+self.server_type_ext)
		subprocess.call(['find','/etc/www/','-name',self.site_name+'-*.conf'])
		print color.default
		
		print 'Creating the storage tree for '+self.site_name+' ...'+color.light_yellow
		try:
			os.makedirs(self.sites_storage_path+self.site_name+'/public',0770)
			os.makedirs(self.sites_storage_path+self.site_name+'/logs',0770)
		except Exception as e:
			pass
		subprocess.call(['chown','-R','root:www-data',self.sites_storage_path+self.site_name])	
		subprocess.call(['find','/var/www/'+self.site_name])
		print color.default
		self.restart_servers()
		

	# enable()
	# actions: move /etc/www/site_name*.conf.disabled to /etc/www/site_name*.conf, restart services
	def enable(self):
		print 50 * "-"+color.light_yellow
		os.chdir(self.sites_config_path)
		for file in glob.glob(self.site_name+"-*.conf.disabled"):
			os.rename(file,file.replace('.disabled',''))
		subprocess.call(['find','/var/www/'+self.site_name+'-*.conf'])
		print color.default
		self.restart_servers()
			
	# disable() 		
	# actions: move /etc/www/site_name*.conf to /etc/www/site_name*.conf.disabled, restart services
	def disable(self):
		print 50 * "-"+color.light_yellow
		os.chdir(self.sites_config_path)
		for file in glob.glob(self.site_name+"-*.conf"):
			os.rename(file,file.replace('.conf','.conf.disabled'))
		subprocess.call(['find','/var/www/'+self.site_name+'-*.conf'])
		print color.default
		self.restart_servers()

	# delete ()		
	# actions: remove /etc/www/site_name*, remove -R /var/www/site_name, remove site_user user, restart services
	def delete(self):
		print 50 * "-"+color.light_yellow
		os.chdir(self.sites_config_path)
		for file in glob.glob(self.site_name+"*"):
			try:
				os.remove(file)
			except:
				pass
		try:	
			shutil.rmtree(self.sites_storage_path+self.site_name)
		except:
			pass
		
		try:
			subprocess.call(['userdel',self.site_user])
			subprocess.call(['groupdel',self.site_user])
		except Exception as e:
			pass
			print e
		print os.popen('getent group | grep '+self.site_user).read()+color.default	
		print color.default
		self.restart_servers()
		
	# sites()		
	# actions: scan /etc/www/*-nginx.conf* and create lists with all/enabled/disabled entries		
	# scan /etc/www for sites configs	
	def sites(self):
		os.chdir(self.sites_config_path)
		self.enabled_sites = []
		self.disabled_sites = []
		self.all_sites = []
		for file in glob.glob("*-nginx.conf*"):
			site_available = str(file).split('-nginx.conf')[0]
			site_enabled = str(file).split('-nginx.conf')[1] == ''
			self.all_sites.append(site_available)
			if site_enabled :
				self.enabled_sites.append(site_available)
			else:
				self.disabled_sites.append(site_available)
		self.total_enabled_sites = len(self.enabled_sites)
		self.total_disabled_sites = len(self.disabled_sites)
		self.total_available_sites = self.total_enabled_sites+self.total_disabled_sites
		self.all_sites.sort()
		
		print color.light_blue+'\n'+35*'-'+'AVAILABLE SITES'
		for index,site in enumerate(self.all_sites):
			if site in self.enabled_sites:
				print color.light_green+str(index+1)+'. '+site+(' '+(39-len(site))*'-')+'ENABLED'+color.default
			else:
				print color.light_red+str(index+1)+'. '+site+(' '+(38-len(site))*'-')+'DISABLED'+color.default
		print color.light_blue+50*'-'+color.default
		selected_site = input(">> [1-"+str(self.total_available_sites)+"]: ")
		
		if selected_site <= self.total_available_sites:
			self.site_name = self.all_sites[selected_site-1]
			print color.light_yellow+self.site_name+'selected'+color.default
			if self.site_name in self.disabled_sites:
				action = raw_input(">> [enable/delete]:")
				if action == 'enable':
					self.enable()
				elif action == 'delete':
					self.delete()
			else:
				action = raw_input(">> [disable/delete]:")
				if action == 'disable':
					self.disable()
				elif action == 'delete':
					self.delete()



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


##################################################
# main
##################################################
menu = Menu()
print color.light_yellow + info + color.default
menu.start()
