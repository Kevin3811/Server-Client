import socket
import threading
import urllib.request as req

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Initialized socket")
host = socket.gethostname()
print("Hostname: ", host)

port = 55555
#'184.57.188.49' #Server's public ip address
PUBLIC_SERVER_IP = '184.57.188.49'
PRIVATE_SERVER_IP = '192.168.1.44'

#Check to see if the client is on the same network as the server and use private ip address if true
ip = req.urlopen('https://v4.ident.me/').read().decode('utf8')
if ip == PUBLIC_SERVER_IP:
    ip = PRIVATE_SERVER_IP

try:
    s.connect(('localhost', port))
except Exception as e:
    print("Unable to connect to server")
    print(e)

    exit(0)

#Thread for listening to what the server sends
def thread_get_input():
    try:
        while True:
            recieved = s.recv(200)
            print("SERVER> ", recieved.decode('ascii'))
    except:
        print("Unable to recieve message from server")
        return

t = threading.Thread(target=thread_get_input, daemon=True)
t.start()

try:
    msg = input("%s: " % host)
    while len(msg):
        s.send(msg.encode('ascii'))
        msg = input("%s: " % host)
except:
    print("Connection closed")
s.close()