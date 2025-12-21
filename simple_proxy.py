#!/usr/bin/env python3
"""
Simple proxy server to serve frontend and API from same origin
"""

from http.server import SimpleHTTPRequestHandler, HTTPServer
import http.server
import socketserver
import os

class ProxyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Serve frontend files
        if self.path.startswith('/api/'):
            # Proxy API requests
            self.send_response(307)  # Temporary redirect
            self.send_header('Location', f'http://localhost:8002{self.path}')
            self.end_headers()
        else:
            # Serve static files
            super().do_GET()

if __name__ == '__main__':
    PORT = 8005
    print(f"🚀 Starting proxy server on port {PORT}")
    print(f"📍 This will serve frontend from http://localhost:{PORT}")
    print(f"🔗 API requests will be proxied to http://localhost:8002")
    print(f"🎯 Open: http://localhost:{PORT}/hf_spaces_frontend.html")
    
    with socketserver.TCPServer(("", PORT), ProxyHandler) as httpd:
        httpd.serve_forever()
