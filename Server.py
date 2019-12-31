#For sockets and connections
import socket
import threading
#For time stamps
from time import gmtime, strftime
#For getting files from host
from os import listdir
from os.path import isfile, join

#Create socket object
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
print("Socket successfully created on host %s" % host)

port = 55555
ip = '192.168.1.44' #Computer's local ip address

serversocket.bind(('', port))
time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
print(time, "- Socked bound to port: ", port)
print("IP: ", socket.gethostbyname(host))

serversocket.listen(5)
sockapp_lock = threading.Lock()
clientsockets = {}

def timeNow():
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())

#Gets all the files in the host directory
def getFilesInHost():
    mypath = 'C:\Parse'
    files = []
    for f in listdir(mypath):
        if isfile(join(mypath, f)):
            files.append(f)
    return files

#Thread in charge of an individual client connection
def threaded_client(conn, addr, sock):
    while True:
        try:
            data = conn.recv(1024)
            if data:
                print(str(addr), "> %s" % data.decode("utf-8"))
                split = data.decode("utf-8").split()

                #Check if the command is getDocs
                if split[0] == "getDocs":
                    files = getFilesInHost()
                    #Check if there are even any files in the host directory
                    if files is None:
                        conn.send("NONE").encode("utf-8")
                    else:
                        #There are, send the names
                        try:
                            conn.send(str(files).encode("utf-8"))
                        except Exception as e:
                            print(timeNow(), "- Unable to send file names - ", e)

                #Check if the command is getNumClients
                if split[0] == "getNumClients":
                    numClients = len(clientsockets)
                    try:
                        conn.send(str(numClients).encode("utf-8"))
                    except Exception as e:
                        print(timeNow(), "- Unable to send number of connections - ", e)
            else:
                break
        except:
            break
    conn.close()
    sockapp_lock.acquire()
    clientsockets.pop(sock)
    sockapp_lock.release()
    print(timeNow(), "- ", str(addr), " closed")
    return

#Thread in charge of listening for new connections
def thread_connection_listener():
    while True:
        try:
            clientsocket, addr = serversocket.accept()
        except:
            print("Unable to recieve connection from client")
            return
        sockapp_lock.acquire()
        ip = str(addr)[2:str(addr).find('\'', 2)]
        port = str(addr)[str(addr).rfind(' ') + 1:-1]

        sock = ip + ":" + port
        clientsockets[sock] = clientsocket
        sockapp_lock.release()
        print(timeNow(), "- Recieved connection from %s" % str(addr))

        new_client = threading.Thread(target=threaded_client, args=(clientsocket, addr, sock), daemon=True)
        new_client.start()

#Thread for listening to consol commands for the server
def thread_server_commands():
    while True:
        cmd = input("%s> " % host)
        if cmd == "exit":
            sockapp_lock.acquire()
            clients = clientsockets.values()
            for client in clients:
                client.close()
                print("Closed connection")
            sockapp_lock.release()
            return

        if cmd == "broadcast":
            send_message = input("tell> ")
            for client in clientsockets.values():
                try:
                    client.send(send_message.encode('ascii'))
                except:
                    print("Unable to send message to client")

        if cmd == "kick":
            sock = input("IP:PORT to kick> ")
            sockapp_lock.acquire()
            conn = clientsockets.get(sock)
            sockapp_lock.release()
            if conn is None:
                print("Couldn't find client with that socket")
                continue
            conn.close()
            print(timeNow(), "- Kicked - ", sock)

        if cmd == "clients":
            clients = clientsockets.keys()
            if len(clients) == 0:
                print("No clients connected")
            for client in clients:
                print(client)

listener_thread = threading.Thread(target=thread_connection_listener, daemon=True)

server_thread = threading.Thread(target=thread_server_commands)

listener_thread.start()

server_thread.start()

server_thread.join()

print("Server terminated")
















