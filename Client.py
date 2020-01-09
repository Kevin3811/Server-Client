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
else:
    ip = PUBLIC_SERVER_IP

try:
    s.connect(('localhost', port))
except Exception as e:
    print("Unable to connect to server")
    print(e)
    exit(0)

clientDir = "C:\\Users\\Kevin\\Desktop\\client"
#clientDir = "C:\\Users\\mcs52\\Desktop\\python"

#Main thread that's listening for user entered commands
try:
    msg = input("%s: " % host)
    while len(msg):
        #Check the message for the 'upload' command
        command = msg.split()
        if command[0] == "upload":
            #Make sure a file to upload has been specified
            if len(command) < 2:
                print("No file specified to upload")
                msg = input("%s: " % host)
                continue
            filename = command[1]
            #Notify the server by sending flag 'upload {filename}'
            s.send(f"upload {filename}".encode("utf-8"))
            fullFile = clientDir + "\\" + filename
            try:
                #Open file handle
                file = open(fullFile, "rb")
                #Read initial frame of data from file
                fileData = file.read(1024)
                while fileData:
                    s.send(fileData)
                    fileData = file.read(1024)
                file.close()
                response = s.recv(1024)
                if response.decode("utf-8") == "SUCCESS":
                    print(f"Successfully uploaded [{filename}] to server")
                else:
                    print(f"Server unable to receive file [{filename}]")
            except Exception as e:
                print(f"Unable to upload [{filename}] to server")
                print(e)
                msg = input("%s: " % host)
                continue
        if command[0] == "download":
            # Check to see if a file is being sent from the server by checking the format: SENDING {filename}
            # How the server sends the flag: conn.send(f"SENDING {filename}".encode("utf-8"))
            if len(command) < 2:
                print("No filename provided")
                msg = input("%s: " % host)
                continue
            s.send(f"download {command[1]}".encode("utf-8"))
            received = s.recv(1024)
            command = received.decode("utf-8").split()
            if command[0] == "SENDING":
                filename = command[1]
                print(f"Receiving file [{filename}]")
                # Open new file as write and binary
                fileLoc = clientDir + "\\" + filename
                # Open a new file with the specified name for the data that will be received to be stored
                with open(fileLoc, "wb") as file:
                    fileData = s.recv(1024)
                    while fileData:
                        print(f"Received data [{len(fileData)} bytes]")
                        file.write(fileData)
                        # If the last chunk of data we received wasn't a full frame, then it was the last one
                        # and stop listening for more data
                        if len(fileData) < 1024:
                            break
                        fileData = s.recv(1024)
                file.close()
                print(f"Successfully downloaded file [{filename}]")
        if command[0] == "getFiles":
            try:
                s.send("getFiles".encode("utf-8"))
                fileList = s.recv(1024)
                while True:
                    print(fileList)
                    if len(fileList) < 1024:
                        break
                    fileList = s.recv
            except Exception as e:
                print("Unable to get list of files")
                print(e)
        if command[0] == "deleteFile":
            if len(command) < 2:
                print("No file provided to delete")
                msg = input("%s: " % host)
                continue
            try:
                s.send(f"deleteFile {command[1]}".encode("utf-8"))
                print(f"Deleted file [{command[1]}]")
            except Exception as e:
                print("Unable to delete file from server")
                print(e)

        msg = input("%s: " % host)
except:
    print("Connection closed")
s.close()


