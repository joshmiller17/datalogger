# Josh Aaron Miller 2021
# Data logging server main

from http.server import BaseHTTPRequestHandler, HTTPServer
import sys, ssl, argparse, os.path
from os import path
import datadb, datahandler


HOST_NAME = ''
PORT_NUMBER = 3004
	

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Data logging server.')
	parser.add_argument('-db', default='log.db', help="Path to database file (default log.db)")
	parser.add_argument('-keyfile', default=None, help="Path to private key if using HTTPS")
	parser.add_argument('-certfile', default=None, help="Path to cert file if using HTTPS")
	parser.add_argument('--nocert', action='store_true', help="Disable HTTPS encryption")
	parser.add_argument('-port', type=int, default=3004, help="Port number (default 3004)")
	
	args = parser.parse_args()

	
	httpd = HTTPServer((HOST_NAME, args.port), datahandler.DataHandler)
	if not args.nocert:
		if args.keyfile is None or args.certfile is None:
			raise argparse.ArgumentTypeError("keyfile and certfile required without --nocert flag")
		if not path.exists(args.keyfile):
			raise argparse.ArgumentTypeError("No such file " + args.keyfile)
		if not path.exists(args.certfile):
			raise argparse.ArgumentTypeError("No such file " + args.certfile)
		httpd.socket = ssl.wrap_socket(httpd.socket, keyfile=args.keyfile, certfile=args.certfile, server_side=True)
	httpd.db = datadb.DataDB(args.db)

	try:
		print("Ready")
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass

	httpd.server_close()
