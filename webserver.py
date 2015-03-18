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
                output += "<a href=/restaurants/new>Make a new restaurant</a></br>"
                restolist = session.query(Restaurant).all()
                for resto in restolist:
                    output += ("</br>%s</br>" % resto.name)
                    output += "<a href='/restaurants/%s/edit'>Edit</a></br>" % resto.id
                    output += "<a href='/restaurants/%s/delete'>Delete</a>" % resto.id
                output += "</body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "Add new Restaurant"
                output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>
                            <h2>Name of restaurant to add:</h2><input name="name" type="text" >
                            <input type="submit" value="Submit"></form>'''
                output += "</body></html>"
                self.wfile.write(output)
                return

            if self.path.endswith("/edit"):
                restaurantIDPath = self.path.split("/")[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(id=
                    restaurantIDPath).one()
                if myRestaurantQuery != []:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                output = "<html><body>"
                output +="<h1>"
                output += myRestaurantQuery.name
                output += "</h1>"
                output += '''<form method='POST' enctype='multipart/form-data'
                            action='/restaurants/%s/edit'>''' % restaurantIDPath
                output += '''<input name="newRestaurantName" type="text" 
                            placeholder = '%s' >''' % myRestaurantQuery.name
                output += "<input type='submit' value='Rename'></form>"
                output += "</body></html>"
                self.wfile.write(output)

            if self.path.endswith("/delete"):
                restaurantIDPath = self.path.split("/")[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(id=
                    restaurantIDPath).one()
                if myRestaurantQuery != []:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                output = "<html><body>"
                output +="<h1>Are you sure you want to delete %s?" % myRestaurantQuery.name
                output += "</h1>"
                output += '''<form method='POST' enctype='multipart/form-data'
                            action='/restaurants/%s/delete'>''' % restaurantIDPath
                output += "<input type='submit' value='Delete'></form>"
                output += "</body></html>"
                self.wfile.write(output)

        except IOError:
            self.send_error(404, "File Not Found %s" % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/delete"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

                restaurantIDPath = self.path.split("/")[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(id=
                                    restaurantIDPath).one()
                if myRestaurantQuery != []:
                    session.delete(myRestaurantQuery)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('newRestaurantName')
                restaurantIDPath = self.path.split("/")[2]

                myRestaurantQuery = session.query(Restaurant).filter_by(id=
                                    restaurantIDPath).one()
                if myRestaurantQuery != []:
                    myRestaurantQuery.name = messagecontent[0]
                    session.add(myRestaurantQuery)
                    session.commit()
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

            if self.path.endswith("/restaurants/new"):
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