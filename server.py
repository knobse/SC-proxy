import socket

# create colors for display in terminal/console
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    crproxycolor = '\033[94m'

print(bcolors.crproxycolor + "[INFO] " + bcolors.ENDC +"starting server")

# create socket
s = socket.socket()
#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
#s.setsockopt(socket.SOL_TCP,socket.SO_KEEPALIVE,True)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


# bind to your ip (localhost)
host = '0.0.0.0'
port = 9339
s.bind((host, port))
#s.setblocking(0)

# start listening on this socket
s.listen(5)
print(bcolors.crproxycolor + "[INFO] " + bcolors.ENDC +"Listening for incoming connections")

def recvall(sock,size):
    data = [] 
    while size > 0:
        sock.settimeout(5.0)
        s = sock.recv(size)
        sock.settimeout(None)
        if not s: raise EOFError
        data.append(s)
        size -= len(s)
    return ''.join(data)

# create new socket for realserver
r = socket.socket()
#sock.setsockopt(SOL_TCP, TCP_NODELAY, 1)
r.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
#r.setsockopt(socket.SOL_TCP,socket.SO_KEEPALIVE,True)
r.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# connect to 
#SC server
host = 'SC server'
port = 9339
r.connect((host, port))
r.setblocking(1)
#print('connected to realserver')
#Proxy attached to real game server
print(bcolors.crproxycolor + "[INFO] " + bcolors.ENDC +"Proxy attached to gameserver")
#
KnownPackets = { 10100: "ClientHello" ,
 20100: "ServerHello" }
#
def HexToDec(data):
  data = data.encode('hex')
  #hex -> dec
  if data != '':
      data = int(data, 16)
  else:
      data = int(0)
  #to string
  data = str(data)
  return data
#
def packetIDToStr(packetID):
  packetID = packetID.encode('hex')
  #hex -> dec
  if packetID != '':
      packetID = int(packetID, 16)
  else:
      packetID = int(0)
  #print KnownPackets
  if packetID in KnownPackets:
    realpacketID = KnownPackets[packetID]
  else:
    realpacketID = "unknown packet"
  
  if realpacketID:
    return realpacketID
  '''else:
    return "unknown packet"'''
#
def clientside(sock,realserver):
   packetID = sock.recv(2)
   packetSize = sock.recv(3)
   unknown = sock.recv(2)
   content = recvall(sock, int(HexToDec(packetSize)))
   print(bcolors.crproxycolor + "[CLIENT_PACKET] " + bcolors.ENDC + packetID.encode('hex')+" : "+ packetSize.encode('hex') +" : "+unknown.encode('hex')+" : "+content.encode('hex'))
   #make right content
   fullcontent = packetID + packetSize + unknown + content
   #send to realserver
   realserver.send(fullcontent)
   #call other function
   #serverside(sock,realserver)
#
def serverside(sock,realserver):
   packetID = realserver.recv(2)
   packetSize = realserver.recv(3)
   unknown = realserver.recv(2)
   content = recvall(realserver, int(HexToDec(packetSize)))
   print(bcolors.crproxycolor + "[SERVER_PACKET] " + bcolors.ENDC + HexToDec(packetID)+"("+packetIDToStr(packetID)+")"+" : "+ packetSize.encode('hex') +" : "+unknown.encode('hex')+" : "+content.encode('hex'))
   #make right content
   fullcontent = packetID + packetSize + unknown + content
   #send to realserver
   sock.send(fullcontent)


while True:
   c, addr = s.accept() # Establish connection with client.
   #print 'Got connection from', addr
   print(bcolors.crproxycolor + "[INFO] " + bcolors.ENDC +"Remote connection from client ("+addr[0]+")")
   
   while 1:
      clientside(c,r)
      serverside(c,r)

   c.close() # Close the connection
