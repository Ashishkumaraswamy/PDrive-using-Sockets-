#Importing the libraries
import os
import socket
import threading
from getpass import getpass
import time
#----------------------------------------------------------
IP = socket.gethostbyname(socket.gethostname())
PORT = 4456
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_DATA_PATH = "server_data"

def listdir(path=""): #FUNCTION TO LIST THE DIRECTORIES IN THE SERVER DIRECTORY
    send_data="OK@"
    files = os.listdir(SERVER_DATA_PATH+"\\"+path)
    if len(files) == 0:
        send_data += "The server directory is empty"
    else:
        send_data += "\n".join(f for f in files)
    return send_data

def handle_client(conn, addr):
    username=authentication_of_user(conn)
    print(f"[NEW CONNECTION] {addr} connected.")
    conn.send("OK@Welcome to the File Server.".encode(FORMAT))

    while True:
        data = conn.recv(SIZE).decode(FORMAT)
        data = data.split("@")
        cmd = data[0]
        if cmd == "LIST":
            send_data=listdir()
            conn.send(send_data.encode(FORMAT))

        elif cmd == "UPLOAD":
            name=data[1]
            filepath = os.path.join(SERVER_DATA_PATH,username, name)
            try:
                os.listdir(SERVER_DATA_PATH+"\\"+username)
            except:
                os.mkdir(SERVER_DATA_PATH+"\\"+username)
            filepath=SERVER_DATA_PATH+"\\"+username+"\\"+name
            f=open(filepath, "wb")
            datas=conn.recv(SIZE)
            while datas:
                f.write(datas)
                try:
                    conn.settimeout(2.0)
                    datas=conn.recv(SIZE)  
                except:
                    conn.settimeout(None)
                    break
            f.close()
            send_data = "OK@File uploaded successfully."
            conn.send(send_data.encode(FORMAT))

        elif cmd == "DELETE":
            files = os.listdir(SERVER_DATA_PATH+"\\"+username)
            send_data = "OK@"
            filename = data[1]

            if len(files) == 0:
                send_data += "The server directory is empty"
            else:
                if filename in files:
                    cmd="del \""+SERVER_DATA_PATH+"\\"+username+"\\"+filename+"\""
                    os.system(cmd)
                    send_data += "File deleted successfully."
                else:
                    send_data += "File not found."
            conn.send(send_data.encode(FORMAT))

        elif cmd == "LOGOUT":
            break

        elif cmd == "DOWNLOAD":
            files = os.listdir(SERVER_DATA_PATH)
            send_data=""
            print(files)
            if len(files) == 0:
                send_data += "The server directory is empty"
            else:
                send_data += "\n".join(f for f in files)
            conn.send(send_data.encode(FORMAT))
            user_dir=conn.recv(SIZE).decode(FORMAT)
            items_in_dir=listdir(user_dir)
            if "empty" in items_in_dir:
                conn.send(items_in_dir.encode(FORMAT))
            else:
                conn.send(items_in_dir.encode(FORMAT))
                user_file=conn.recv(SIZE).decode(FORMAT)
                path=SERVER_DATA_PATH+'\\'+user_dir+'\\'+user_file
                try:
                    f=open(path,"rb")
                    filename = path.split("/")[-1]
                    send_data = f"{filename}"
                    conn.send(send_data.encode(FORMAT))
                    datas=f.read(SIZE)
                    while datas:
                        conn.send(datas)
                        datas=f.read(SIZE)
                    conn.send("OK@ ".encode(FORMAT))
                except:
                    conn.send("File Does Not Exist under this name".encode(FORMAT))
                    conn.send("OK@ ".encode(FORMAT))

        elif cmd == "HELP":
            data = "OK@"
            data += "LIST: List all the files from the server.\n"
            data += "UPLOAD <path>: Upload a file to the server.\n"
            data += "DELETE <filename>: Delete a file from the server.\n"
            data += "LOGOUT: Disconnect from the server.\n"
            data += "HELP: List all the commands."

            conn.send(data.encode(FORMAT))

    print(f"[DISCONNECTED] {addr} disconnected")
    conn.close()

def retry_password(conn,username,password):
    while True:
        conn.send("Re Enter Password: ".encode(FORMAT))
        passw=conn.recv(SIZE).decode(FORMAT)
        if password==passw:
            return 
        else:
            conn.send("Invalid Password: ".encode(FORMAT))

def authentication_of_user(conn):
    conn.send("Are you a new user ?(y/n): ".encode(FORMAT))
    new_user_check=conn.recv(SIZE).decode(FORMAT)
    username=""
    if new_user_check=='y':
        conn.send("Username:".encode(FORMAT))
        username=conn.recv(1024).decode(FORMAT)
        conn.send("Password:".encode(FORMAT))
        password=conn.recv(1024).decode(FORMAT)
        f=open('password_file\password_file.txt','a')
        text=username+" "+password+"\n"
        f.write(text)
        f.close()
        conn.send("From Server: Access Granted .....LOADING.....".encode(FORMAT))
    else:
        while True:
            conn.send("Username:".encode(FORMAT))
            username=conn.recv(1024).decode(FORMAT)
            conn.send("Password:".encode(FORMAT))
            password=conn.recv(1024).decode(FORMAT)
            f = open('password_file\password_file.txt','r')
            datas = f.readlines()
            for temp in datas:
                lines= str(temp)
                print(lines)
                usernamef=lines.split()[0]
                passwordf=lines.split()[1]
                print(usernamef,passwordf)
                if username==usernamef:
                    if password==passwordf:
                        conn.send("From Server: Access Granted .....LOADING.....".encode(FORMAT))
                        return username
                    
            conn.send("Invalid username or password Try again!!".encode(FORMAT))

        


def main():
    print("[STARTING] Server is starting")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server is listening on {IP}:{PORT}.")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

if __name__ == "__main__":
    main()