#!/usr/bin/env python3


import os
import yaml
import urllib.request
import csv
import base64

import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging

data_dict = {}


class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def readurl(self,url):
        response = urllib.request.urlopen(url)
        lines = [l.decode('utf-8') for l in response.readlines()]
        cr = csv.reader(lines)
        count = 0
        for row in cr:
            if count > 10:
                break
            count += 1
            row_str = ", ".join(row)+'\n'
            self.wfile.write(row_str.encode("utf8"))

    def _html(self, message):
        """This just generates an HTML document that includes `message`
        in the body. Override, or re-write this do do more interesting stuff.
        """
        content = f"<html><body><h1>{message}</h1></body></html>"
        return content.encode("utf8")  # NOTE: must return a bytes object!

    def do_GET(self):
        self._set_headers()
        logging.info("path is " + self.path)
        data = data_dict.get(self.path[1:], "notfound")
        #logging.info("url is " + url)
        logging.info("GET request")
        self.wfile.write("GET request for {}\n".format(self.path).encode('utf-8'))
        if(data != "notfound"):
            url = data['endpoint_url']
            self.readurl(url)
            logging.info("Transformation action is {} for the columns {}\n".format(data['action'],data['transferred_columns']))
        else:
            self.wfile.write("invalid request\n".encode('utf-8'))
            self.wfile.write("The available datasets:\n".encode('utf-8'))
            for key in data_dict:
                self.wfile.write("dataset name: {}\n".format(key).encode('utf-8'))
                for k in data_dict[key]:
                    self.wfile.write("    {}: {}\n".format(k,data_dict[key][k]).encode('utf-8'))
            logging.info(data_dict)
        

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        self.wfile.write(self._html("POST!"))
        logging.info("POST request\n")

def run(config_path=None, server_class=HTTPServer, handler_class=S, addr="localhost", port=8000):
    logging.basicConfig(level=logging.INFO)
    logging.info("\nHello World Read Module!")
                
    with open(config_path, 'r') as stream:
        content = yaml.safe_load(stream)
        #logging.info(content)
        for key,val in content.items():
            if "data" in key:
                for i in range(len(val)):
                    data = val[i]
                    connectionName = data["name"]
                    name = connectionName.split("/")[1]
                    format = data["format"]
                    endpoint_url = data["connection"]["s3"]["endpoint_url"]
                    transformations = base64.b64decode(data["transformations"])
                    data_dict[name] = {'format':format, 'endpoint_url':endpoint_url, 'transformations':transformations}
                    
    logging.info("The available datasets:\n")
    for key in data_dict:
        logging.info("dataset name: {}\n".format(key))
        for k in data_dict[key]:
            logging.info("    {}: {}\n".format(k,data_dict[key][k]))
    
    #logging.info(data_dict)
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)

    logging.info(f"Starting httpd server on {addr}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run an HTTP server")
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
    parser.add_argument(
        '-c', 
        '--config', 
        type=str, 
        default='../etc/conf/conf.yaml', 
        help='Path to config file'
    )
    args = parser.parse_args()
    run(config_path=args.config, addr=args.listen, port=args.port)
    #main()
