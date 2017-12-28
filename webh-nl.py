#!/usr/bin/python
import glob, os, sys, shutil, subprocess, re, pexpect

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
# menu
##################################################
class Menu:
	main_menu_options = [
		('New site','new()'),
		('Manage sites (enable/disable/delete)','sites()'),
		('Exit','exit()'),
	]
		
	# the start menu	
	def start(self):
		print color.light_yellow + 50 * '-'+color.default
		for index, item in enumerate(self.main_menu_options):
			print str(index+1)+'. '+item[0]
		print color.light_yellow + 50 * '-'+color.default
		test_valid_menu = True
		while test_valid_menu == True:
			try:
				self.selection = input(">> [1-"+str(len(self.main_menu_options))+"]: ")
				valid_menu_option = 1 <= self.selection <= len(self.main_menu_options)
				if not valid_menu_option:
					raise Exception() 
				test_valid_menu = False
			except KeyboardInterrupt:
				Manage().exit()
			except:
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
	
	#valid_fqdn();
	def valid_fqdn(self):
		pattern = re.compile(
			r'^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|'
			r'([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|'
			r'([a-zA-Z0-9][-_.a-zA-Z0-9]{0,61}[a-zA-Z0-9]))\.'
			r'([a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})$'
		)
		return pattern.match(self.site_name)
	#exit()
	def exit(self):
		print
		sys.exit(0)
	# restart webservers (apache/nginx/php-fpm)
	def restart_servers(self,reverttomenu = True):
		print 'Reloading nginx, apache2 and php-fpm servers ...'+color.light_yellow
		subprocess.call(['systemctl','reload','nginx'])
		subprocess.call(['systemctl','reload','apache2'])
		subprocess.call(['systemctl','restart','php7.0-fpm'])
		print color.default+'\nDone'
		if reverttomenu == True:
			Menu().start()
		
	# new()
	# actions: create /etc/www/site_name*, create /var/www/site_name folder, create site_name_clean system user, restart services
	def new(self):
		print color.light_yellow + 50 * '-'+color.default
		print 'Enter the Fully Qualified Domain Name (FQDN) for the site, ex: example.com, demo.example.com'
		
		test_valid_fqdn = True
		while test_valid_fqdn == True:
			try:
				import readline
				self.site_name = raw_input(">> [FQDN]: ")
				if len(self.site_name) == 0:
					raise ValueError()
				if not self.valid_fqdn():
					raise Exception()
				test_valid_fqdn = False	
			except KeyboardInterrupt:
				self.exit()
			except ValueError:
				Menu().start()
			except:
				print 'Invalid FQDN, try again'

		self.site_name_have_www = self.site_name.split('www.')[0] == ''
		if self.site_name_have_www:
			self.site_name = self.site_name[4:]
		self.site_user = 'www-'+self.site_name.replace('.','-')
		
		print color.light_yellow + 50 * '-'+color.default
		print 'Creating the system user for '+self.site_name+' ...'+color.light_yellow
		try:
			subprocess.check_call(['useradd','-r',self.site_user])
			subprocess.check_call(['usermod','-g','www-data',self.site_user])
			subprocess.check_call(['groupdel',self.site_user])
		except:
			pass
		print os.popen('cat /etc/passwd | grep '+self.site_user).read()+color.default		

		print 'Creating the config files for '+self.site_name+' ...'+color.light_yellow
		for file in glob.glob("files/vhosts/fqdn-*.conf"):
			self.server_type_ext = file.split('fqdn')[1]
			shutil.copyfile(file, self.sites_config_path+self.site_name+self.server_type_ext)
			os.popen("sed -i 's/{SITE_NAME}/"+self.site_name+"/g;s/{SITE_USER}/"+self.site_user+"/g' "+self.sites_config_path+self.site_name+self.server_type_ext)
		shutil.move('/etc/www/'+self.site_name+'-nginx-ssl.conf', '/etc/www/'+self.site_name+'-nginx.ssl')		
		subprocess.call(['find','/etc/www/','-name',self.site_name+'-*'])

		print color.default
		print 'Creating the storage tree for '+self.site_name+' ...'+color.light_yellow
		try:
			os.makedirs(self.sites_storage_path+self.site_name+'/public')
			os.makedirs(self.sites_storage_path+self.site_name+'/logs')
			os.makedirs(self.sites_storage_path+self.site_name+'/nodejs')
			os.makedirs(self.sites_storage_path+self.site_name+'/tmp')
		except Exception as e:
			pass
		subprocess.call(['find','/var/www/'+self.site_name])
		
		print color.default
		self.restart_servers(False)		
		
		print color.default
		print 'Configuring Let\'s Encrypt for '+self.site_name+' ...'+color.light_yellow
		certbot = pexpect.spawn ('certbot-auto certonly -a webroot --webroot-path=/var/www/'+self.site_name+'/public -d '+self.site_name)
		certbot.interact()
		shutil.move('/etc/www/'+self.site_name+'-nginx.ssl', '/etc/www/'+self.site_name+'-nginx.conf')
		print color.default
		self.restart_servers()
		

	# enable()
	# actions: move /etc/www/site_name*.conf.disabled to /etc/www/site_name*.conf, restart services
	def enable(self):
		print 50 * '-'+color.light_yellow
		os.chdir(self.sites_config_path)
		for file in glob.glob(self.site_name+"-*.conf.disabled"):
			os.rename(file,file.replace('.disabled',''))
		subprocess.call(['find','/etc/www/','-name',self.site_name+'-*'])
		print color.default
		self.restart_servers()
			
	# disable() 		
	# actions: move /etc/www/site_name*.conf to /etc/www/site_name*.conf.disabled, restart services
	def disable(self):
		print color.light_yellow + 50 * '-'
		os.chdir(self.sites_config_path)
		for file in glob.glob(self.site_name+"-*.conf"):
			os.rename(file,file.replace('.conf','.conf.disabled'))
		subprocess.call(['find','/etc/www/','-name',self.site_name+'-*'])
		print color.default
		self.restart_servers()

	# delete ()		
	# actions: remove /etc/www/site_name*, remove -R /var/www/site_name, remove site_user user, restart services
	def delete(self):
		print color.light_yellow + 50 * '-'
		print 'Removing config files ...'
		os.chdir(self.sites_config_path)
		for file in glob.glob(self.site_name+"*"):
			try:
				os.remove(file)
			except:
				pass
		print 'Removing storage files ...'		
		try:	
			shutil.rmtree(self.sites_storage_path+self.site_name)
		except:
			pass
		print 'Removing '+self.site_user+' system user ...'
		try:
			subprocess.call(['userdel',self.site_user])
		except Exception as e:
			pass
		print 'Removing '+self.site_name+' Let\'s Encrypt certificate ...'
		try:
			subprocess.call(['certbot-auto','delete','--cert-name',self.site_name])
		except Exception as e:
			pass
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
		print color.light_blue + 50*'-'+color.default
		
		test_valid_selected_site = True
		while test_valid_selected_site == True:
			try:
				import readline
				selected_site = input(">> [1-"+str(self.total_available_sites)+"]: ")
				valid_menu_option = 1 <= selected_site <= self.total_available_sites
				if not valid_menu_option:
					raise Exception()
				test_valid_selected_site = False	
			except SyntaxError:
				Menu().start()
			except KeyboardInterrupt:
				self.exit()
			except:
				print 'Invalid option, try again'
		
		self.site_name = self.all_sites[selected_site-1]
		self.site_user = 'www-'+self.site_name.replace('.','-')
		print color.light_yellow + 50 * '-'
		print self.site_name+' selected\n'+color.default
		
		test_valid_action = True
		while test_valid_action == True:
			try:
				if self.site_name in self.disabled_sites:
					action = raw_input(">> [enable/delete]:")
					if action == 'enable':
						self.enable()
					elif action == 'delete':
						self.delete()
					elif action == '':
						raise ValueError()
					else:
						raise Exception()
				else:
					action = raw_input(">> [disable/delete]:")
					if action == 'disable':
						self.disable()
					elif action == 'delete':
						self.delete()
					elif action == '':
						raise ValueError()
					else:
						raise Exception()
				test_valid_action = False
			except KeyboardInterrupt:
				self.exit()	
			except ValueError:
				self.sites()			
			except:
				print 'Invalid action, try again'



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
