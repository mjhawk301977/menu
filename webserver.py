''' Simple web server for menu CRUD app '''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

class webServerHandler(BaseHTTPRequestHandler):
    ''' Handles GET requests '''
    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Restaurants</h1>"
                restolist = session.query(Restaurant).all()
                for resto in restolist:
                    output += ("</br>%s</br>" % resto.name)
                    output += "<a href=#>Edit</a></br>"
                    output += "<a href=#>Delete</a>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "Add new Restaurant"
                output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants'>
                            <h2>Name of restaurant to add:</h2><input name="name" type="text" >
                            <input type="submit" value="Submit"></form>'''
                output += "</body></html"
                self.wfile.write(output)
                print output
                return

        except IOError:
            self.send_error(404, "File Not Found %s" % self.path)

    def do_POST(self):
        try:
            self.send_response(301)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('name')
            newResto = Restaurant(name = messagecontent[0])
            session.add(newResto)
            session.commit()
            print "creating output"
            output = ""
            output += "<html><body>"
            output += " <h2>Restaurant added!</h2>"
            restolist = session.query(Restaurant).all()
            for resto in restolist:
                output += ("</br>%s</br>" % resto.name)
                output += "<a href=#>Edit</a></br>"
                output += "<a href=#>Delete</a>"
            output += "</body></html>"
            self.wfile.write(output)
            print output

        except:
            pass
def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print "Web server running on port %s" % port
        server.serve_forever()

    except KeyboardInterrupt():
        print "^C entered, stopping web server..."
        server.socket.close()

if __name__ == '__main__':
    main()