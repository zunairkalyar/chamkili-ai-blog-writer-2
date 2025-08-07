from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            'status': 'success',
            'message': 'Python API is working!',
            'environment': {
                'gemini_api_key_set': bool(os.getenv('GEMINI_API_KEY')),
                'shopify_store_set': bool(os.getenv('SHOPIFY_STORE_NAME')),
                'shopify_token_set': bool(os.getenv('SHOPIFY_ACCESS_TOKEN'))
            },
            'timestamp': '2025-08-07T12:17:18Z'
        }
        
        self.wfile.write(json.dumps(response, indent=2).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
