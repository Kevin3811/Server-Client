import socket
import threading
from time import gmtime, strftime

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


def threaded_client(conn, addr, sock):
    conn.send("Successfully connected to server".encode('ascii'))
    while True:
        try:
            data = conn.recv(1024)
            if data:
                print(str(addr), "> %s" % data.decode("utf-8"))
            else:
                break
        except:
            break
    conn.close()
    sockapp_lock.acquire()
    clientsockets.pop(sock)
    sockapp_lock.release()
    time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print(time, "- ", str(addr), " closed")
    return

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
        time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        print(time, "- Recieved connection from %s" % str(addr))

        new_client = threading.Thread(target=threaded_client, args=(clientsocket, addr, sock), daemon=True)
        new_client.start()

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

            if cmd == "tell":
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
                time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                print(time, "- Kicked - ", sock)

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
















