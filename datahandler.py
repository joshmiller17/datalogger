# Josh Aaron Miller 2021
# Data logging HTTP Request Handler

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from collections import defaultdict
import hashlib, json, sys, time
import rate_limiter

ACCEPT_ALL_INPUTS = True

OUTFILE = "datalog.txt"

PATHS = {
"LOG" : "/log"
}

MAX_REQUEST_SIZE = 10000
MSG_REQ_LARGE = "Message too large"

class DataHandler(BaseHTTPRequestHandler):

	def log_message(self, format, *args):
		client_short = hashlib.md5(('dataserver' + self.client_address[0]).encode('utf-8')).hexdigest()[:8]

	def respond(self, data):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.send_header('Access-Control-Allow-Origin','*')
		self.end_headers()
		self.wfile.write(json.dumps(data).encode('utf-8'))


	def check_keys(self, args, keys_req, keys_opt=[]):
		for key in keys_req:
			if key not in args:
				return {"success":False, "info":'Missing required key ' + key + '.'}
		for key in args.keys():
			if key not in keys_req and key not in keys_opt and not ACCEPT_ALL_INPUTS:
				return {"success":False, "info":'Unknown key ' + key + '.'}
		return None

	def do_HEAD(self):
	
		if rate_limiter.is_rate_limited(self.client_address[0]):
			return self.respond({"success":False, "info":MSG_TOO_MANY_REQ})
	
		parse = urlparse(self.path)
		path = parse.path
		if len(path) > MAX_REQUEST_SIZE:
			return self.respond({"success":False, "info":MSG_REQ_LARGE})

		if path in [val for key, val in PATHS.items()]:
			return self.respond({"success":True})
		else:
			return self.respond({"success":False})
			
	def do_OPTIONS(self):
			if rate_limiter.is_rate_limited(self.client_address[0]):
				return self.respond({"success":False, "info":MSG_TOO_MANY_REQ})
	
			self.send_response(200)
			self.send_header('Access-Control-Allow-Origin','*')
			self.send_header('Access-Control-Allow-Headers', '*')
			self.send_header('Access-Control-Allow-Methods', 'OPTIONS, GET, HEAD, POST')
			self.send_header('Allow', 'OPTIONS, GET, HEAD, POST')
			self.send_header('Content-type', 'text/html')
			self.end_headers()
			
	def do_POST(self):
	
		if rate_limiter.is_rate_limited(self.client_address[0]):
			return self.respond({"success":False, "info":MSG_TOO_MANY_REQ})
		
		content_length = int(self.headers['Content-Length'])
		if content_length > MAX_REQUEST_SIZE:
			return self.respond({"success":False, "info":MSG_REQ_LARGE})
			
		post_data = self.rfile.read(content_length)
		post_data = post_data.decode('utf-8')
		
		filename = str(self.client_address[0] + str(time.time())) + ".log"
		with open (filename, 'w') as out:
			out.write(post_data)
		
		return self.respond({"success":True})
		

	def do_GET(self):
	
		if rate_limiter.is_rate_limited(self.client_address[0]):
			return self.respond({"success":False, "info":MSG_TOO_MANY_REQ})
	
		parse = urlparse(self.path)
		path = parse.path
		if len(path) > MAX_REQUEST_SIZE:
			return self.respond({"success":False, "info":MSG_REQ_LARGE})

		# get the arguments
		args = parse_qs(parse.query)
		
		# convert key, [val] to key, val
		for k,v in args.items():
			args[k] = v[0]			
			
	
		if path == PATHS["LOG"]:
			entry = []
			entry.append(str(self.client_address[0]))
			entry.append(str(time.time()))
			for k,v in args.items():
				entry.append(str(k) + "=" + str(v))
			
			with open (OUTFILE, 'a') as out:
				out.write("\t".join(entry) + "\n")
				
			return self.respond({"success":True})
			
		else:
			# return error for unrecognized request
			return self.respond('Bad request path.')
