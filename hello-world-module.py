#!/usr/bin/env python3


import os
import yaml
import urllib.request

import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _html(self, message):
        """This just generates an HTML document that includes `message`
        in the body. Override, or re-write this do do more interesting stuff.
        """
        content = f"<html><body><h1>{message}</h1></body></html>"
        return content.encode("utf8")  # NOTE: must return a bytes object!

    def do_GET(self):
        self._set_headers()
        self.wfile.write(self._html("hi!"))
        logging.info("GET request\n")

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        self.wfile.write(self._html("POST!"))
        logging.info("POST request\n")

def run(server_class=HTTPServer, handler_class=S, addr="localhost", port=8000):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)

    logging.info(f"Starting httpd server on {addr}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("\nHello World Read Module!")

    with open('../etc/conf/conf.yaml', 'r') as stream:
        content = yaml.safe_load(stream)
        for key,val in content.items():
            if "data" in key:
                data = val[0]
                url = data['qqq']
                connectionName = data["name"]
                connectionFormat = data["format"]
                s3Bucket = data["s3.bucket"]
                s3Endpoint = data["s3.endpoint"]
        

    logging.info("\nname is " + connectionName)
    logging.info("\nConnection format is " + connectionFormat)
    logging.info("\nS3 bucket is " + s3Bucket)
    logging.info("\nS3 endpoint is " + s3Endpoint)
    logging.info("\nurl is " + url)
    logging.info ("\nREAD SUCCEEDED")
    link = urllib.request.urlopen(url)
    #print(link.read())
    run()
    


if __name__ == "__main__":
    '''parser = argparse.ArgumentParser(description="Run a simple HTTP server")
    parser.add_argument(
        "-l",
        "--listen",
        default="localhost",
        help="Specify the IP address on which the server listens",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8000,
        help="Specify the port on which the server listens",
    )
    args = parser.parse_args()
    run(addr=args.listen, port=args.port)'''
    main()




"""
Very simple HTTP server in python for logging requests
Usage::
    ./hello-world-read-module.py [<port>]
"""
'''
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging

import os
import yaml

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))


    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))

        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=S, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    print("\nHello World Read Module!")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
'''
