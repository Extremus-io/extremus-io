from djwebsocket import server
from djwebsocket.testSocket import testSocket
server = server.WebSocketServer("localhost", 8000)
server.run_server()
