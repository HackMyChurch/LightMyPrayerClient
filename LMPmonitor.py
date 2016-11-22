#!/usr/bin/env python
##################################################################
#               L I G H T   M Y   P R A Y E R 
#
# 							Monitoring 
#
##################################################################
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from SocketServer import ThreadingMixIn
import threading
import json, os

PORT_NUMBER = 9000
SESSION_TIMEOUT = 5 # in Second

#
# Espace disponible
#
def used_space():
	result = os.popen("df -hm /home/pi | grep '/' | cut -d' ' -f23").read()
	return result.rstrip()

#
# nb d'images
#
def images_count():
	result = os.popen("sudo ls -l /home/pi/lmp/img/rasp*.jpg | wc -l").read()
	return result.rstrip()

#
# service python
#
def lues_service():
	result = os.popen('ps aux | grep "sudo python client.py" | grep -v "grep" | wc -l').read()
	return result.rstrip()

#
# service python
#
def dhcp_service():
	result = os.popen('ps aux | grep "dhcpd" | grep -v "grep" | wc -l').read()
	return result.rstrip()

#
# Commande de cleanup
#
def cleanup():
	result = os.popen('/home/pi/lmp/scripts/cleanup.sh').read()
	return result.rstrip()

#
# Commande de reboot
#
def reboot():
	result = os.popen('sudo reboot').read()
	return result.rstrip()

#
# Commande de halt
#
def halt():
	result = os.popen('sudo halt').read()
	return result.rstrip()

#This class will handles any incoming request from the browser 
class httpMonitor(BaseHTTPRequestHandler):

        # self.request.settimeout(SESSION_TIMEOUT)

	# Handler for the GET requests
	def do_GET(self):
		print self.path

		# Monitoring
		if self.path == '/monitor':
			json_resp = { 
							"stderr":"", "data" : 
							{ 
								"used_space": used_space(), 
								"images_count":images_count(), 
								"lues_service": lues_service(),
								"dhcp_service": dhcp_service()
							}
						}
			send_response = True

		# Cleanup
		elif self.path == '/cleanup':
			json_resp = {
							"stdout": cleanup()
						}
			send_response = True

		# Reboot
		elif self.path == '/reboot':
			json_resp = {
							"stdout": reboot()
						}
			send_response = True

		# halt
		elif self.path == '/halt':
			json_resp = {
							"stdout": halt()
						}
			send_response = True

		# Route inconnue
		else:
			self.send_response(404)
			self.send_header('Access-Control-Allow-Origin', '*')
			self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, PATCH, DELETE')
			self.send_header('Access-Control-Allow-Headers', 'X-Requested-With,content-type')
			self.send_header('Content-type','application/json')
			self.end_headers()
			return

		# Envoir de la reponse
		if send_response:
			self.send_response(200)
			self.send_header('Access-Control-Allow-Origin', '*')
			self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, PATCH, DELETE')
			self.send_header('Access-Control-Allow-Headers', 'X-Requested-With,content-type')
			self.send_header('Content-type','application/json')
			self.end_headers()
			# Send the html message
			json.dump(json_resp, self.wfile)
			return

# class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
#     """Handle requests in a separate thread."""

# if __name__ == '__main__':
#     server = ThreadedHTTPServer(('', PORT_NUMBER), httpMonitor)
#     server.socket.settimeout(SESSION_TIMEOUT)
#     print 'Starting server, use <Ctrl-C> to stop'
#     server.serve_forever()

try:
	#Create a web server and define the handler to manage the incoming request
	server = HTTPServer(('', PORT_NUMBER), httpMonitor)
	print server
	server.socket.settimeout(SESSION_TIMEOUT)
	print 'Started httpserver on port ' , PORT_NUMBER
	
	#Wait forever for incoming htto requests
	server.serve_forever()

except KeyboardInterrupt:
	print '^C received, shutting down the web server'
	server.socket.close()