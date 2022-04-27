import sys, signal
import socketserver
from http.server import SimpleHTTPRequestHandler
import urllib.parse

#base class of any TCP session.
#It contains methods to handle user authentication, which is based on the ip address matching.
class SessionAuth(object) :
      
    auth_user = ""
    
    def __init__(self):
        SessionAuth.auth_user = ""

    def setAuth(self, client_socket, new_auth_user):
        clients[client_socket[0]] = new_auth_user

    def removeAuth(self, client_socket):
        if(not self.isAuthUser(client_socket)) : 
            return
        del clients[client_socket[0]]

    def getAuthUser(self, client_socket):
        if(self.isAuthUser(client_socket)) :
            return clients[client_socket[0]]
        
        return ""

    def isAuthUser(self, client_socket):
        return client_socket[0] in clients.keys()



#class of ano TCP session.
#Extends SessionAuth to access user auth functions
class ClientSession(SimpleHTTPRequestHandler, SessionAuth) :
        
    def __init__(self, a, b, c):
        SimpleHTTPRequestHandler.__init__(self, a, b, c)
        SessionAuth.__init__(self)
        
        print("New Session " + self.client_address.__str__() + " --> " + str(self.isAuthUser(self.client_address)))
        
    def do_GET(self) :
        
        
        #login error message
        error = ""
        
        #handle user authentication.
        #If mail is not valid, error will show up.
        if(self.path.find('?') > 0) :
            arguments = urllib.parse.parse_qs(self.path[self.path.find('?')+1:])            
            if("email" in arguments.keys()) :
                if(len(arguments["email"][0]) < 5 or arguments["email"][0].find("@") < 0) :
                    error = "Inserisci una mail valida"
                else :
                    self.setAuth(self.client_address, arguments["email"][0])
        
        
        
        current_header = "text/html"
        current_page = "home.html"
        
        if(self.path.endswith("sea")) :
            current_page = "sea.html"
            
        if(self.path.endswith("city")) :
            current_page = "city.html"
        
        if(self.path.endswith("mountain")) :
            current_page = "mountain.html"
        
        if(self.path.endswith("brochure.pdf")) :
            current_header = "application/octet-stream"
            current_page = "media/brochure.pdf"

        if(self.path.endswith("logout")) :
            current_page = "login.html"
            self.removeAuth(self.client_address)
            
        if(not self.isAuthUser(self.client_address)) :
            current_page = "login.html"
        
        
        self.send_response(200)
        self.send_header("Content-type", current_header)
        self.end_headers()                  
                
        if(current_header == "text/html") :
            with open("public_html/script/base.js", 'rb') as fh:
                html = fh.read()
                self.wfile.write(b"<script>" + html + b"</script>")
            
            with open("public_html/style/base.css", 'rb') as fh:
                html = fh.read()
                self.wfile.write(b"<style>" + html + b"</style>")
              
                
        with open("public_html/" + current_page, 'rb') as fh:
            html = fh.read()
            
            if(current_header == "text/html") :
                html = html.replace(b"#customer_email", bytes(self.getAuthUser(self.client_address), "utf-8"))
                html = html.replace(b"#localhost", bytes(get_root_url(), "utf-8"))
                html = html.replace(b"#error", bytes(error, "utf-8"))
            
            self.wfile.write(html)


def signal_handler(signal, frame):
    #stop server
    print("Server stopped.")
    try:
      if( server ):
        server.server_close()
    finally:
      sys.exit(0)

def get_root_url():
    return "http://" + server_ip_address + ":" + str(server_port)

#server configuration
server_ip_address = 'localhost'
server_port = 8000

#server object
server = socketserver.ThreadingTCPServer((server_ip_address, server_port), ClientSession)
server.daemon_threads = True
server.allow_reuse_address = True

#clients auth storage
clients = {}

#handle keyboard CTRL+C
signal.signal(signal.SIGINT, signal_handler)

#run main activity
try:
  while True:
    server.serve_forever()
except KeyboardInterrupt:
  pass

server.server_close()



