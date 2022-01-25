#Importing the libraries
import socket
import os
from os import system
from getpass import getpass
from tqdm import tqdm
import time
#----------------------------------------------------------
IP = socket.gethostbyname(socket.gethostname())
PORT = 4456
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024
CLIENT_PATH="client_data"

def title_page():
    system("cls")
    print("\n\t\t*******FILE SHARING APPICATION********")
    print("\n\n\tFile Sharing application that lets you upload your files onto a server from your local storage,\n and also allows you to download others file from the server.\n")
    print("\n\t\t\tUse \"HELP\" command to get the list of commands available\n")

def help_command():
    print("\n\t\t\t\tUse \"HELP\" command to get the list of commands available")

def new_user_ques(): 
    print("\n\t\tAre you a new user or an existing user?(y/n): ")
    msg=input()
    return msg

def retry_password(client):
    while True:
        msg=client.recv(SIZE).decode(FORMAT)
        username=input("\n\t"+msg)
        client.send(username.encode(FORMAT))
        msg=client.recv(SIZE).decode(FORMAT)
        passw=getpass("\n\t"+msg)
        client.send(passw.encode(FORMAT))
        msg=client.recv(SIZE).decode(FORMAT)
        if "Access" in msg:
            break
        else:
            print("\n\t Invalid Password Try Again") 
            system("cls")
            title_page()
    
def authentication(client):  #AUTHENTICATION OF USER
    new_user_check=client.recv(SIZE).decode(FORMAT)
    checkv=input(new_user_check)
    client.send(checkv.encode(FORMAT))
    if checkv.lower()=='y':
        title_page()
        msg=client.recv(SIZE).decode(FORMAT)
        username=input('\t'+msg)
        client.send(username.encode(FORMAT))
        msg=client.recv(SIZE).decode(FORMAT)
        password=getpass('\t'+msg)
        client.send(password.encode(FORMAT))
        msg=client.recv(SIZE).decode(FORMAT)
        title_page()
        print("\n\n\t",msg)
        time.sleep(3)
        return
    else:
        title_page()
        msg=client.recv(SIZE).decode(FORMAT)
        username=input('\t'+msg)
        client.send(username.encode(FORMAT))
        msg=client.recv(SIZE).decode(FORMAT)
        password=getpass('\t'+msg)
        client.send(password.encode(FORMAT))
        msg=client.recv(SIZE).decode(FORMAT)
        if "Access" in msg:
            title_page()
            print("\n\n\t",msg)
            time.sleep(3)
        else:
            print("\n\n\t"+msg)
            time.sleep(3)
            title_page()   
            retry_password(client)
        return


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    authentication(client)
    title_page()
    while True:
        try:
            client.settimeout(5.0)
            data = client.recv(SIZE).decode(FORMAT)
            cmd, msg = data.split("@")
        except:
            client.settimeout(None)
        if cmd == "DISCONNECTED":
            print(f"[SERVER]: {msg}")
            break
        elif cmd == "OK":
            print(f"{msg}")
        data = input("> ")
        data = data.split(" ")
        cmd = data[0]
        cmd=cmd.upper()
        if cmd == "HELP":
            client.send(cmd.encode(FORMAT))
        elif cmd == "LOGOUT":
            client.send(cmd.encode(FORMAT))
            break
        elif cmd == "LIST":
            client.send(cmd.encode(FORMAT))
            output =client.recv(SIZE).decode(FORMAT)
            print(output)
        elif cmd == "DELETE":
            client.send(f"{cmd}@{data[1]}".encode(FORMAT))
        elif cmd == "UPLOAD":
            path = data[1]
            f=open(path,"rb")
            filename = path
            send_data = f"{cmd}@{filename}"
            client.send(send_data.encode(FORMAT))
            datas=f.read(SIZE)
            while datas:
                client.send(datas)
                datas=f.read(SIZE)      
            f.close()    
        elif cmd == "DOWNLOAD":
            client.send(cmd.encode(FORMAT))
            listdir=client.recv(SIZE).decode(FORMAT)
            system("cls")
            title_page()
            print("\n\t List Of Directories Availbale:")
            dirlist=listdir.split('\n')
            for i in dirlist:
                print("\t\t--> ",i)
            user_dir=input("\n\tEnter the directory you want to download from:")
            client.send(user_dir.encode(FORMAT))
            listfiles=client.recv(SIZE).decode(FORMAT)
            listfiles=listfiles.split('@')[1]
            system("cls")
            title_page()
            if "empty" in listfiles:
                print("\n\t",listfiles)
                time.sleep(3)
                continue
            else: 
                print("\t\t-> ",user_dir)
                listfiles=listfiles.split('\n')
                for i in listfiles:
                    print("\t\t  ->",i)
                user_file=input("Enter the file you wish to download: ")
                client.send(user_file.encode(FORMAT))
                file=client.recv(SIZE).decode(FORMAT)
                if "Not Exist" in file:
                    print("\n\t",file)
                    time.sleep(0.5)
                else:
                    filepath = os.path.join(CLIENT_PATH, user_file)
                    f=open(filepath, "wb")
                    datas=client.recv(SIZE)
                    while datas:
                        f.write(datas)
                        try:
                            client.settimeout(2.0)
                            datas=client.recv(SIZE)  
                        except:
                            client.settimeout(None)
                            break
                    f.close()
                    print("File Downloaded Successfully")
                time.sleep(0.5)
                system("cls")
                title_page()

    print("Disconnected from the server.")
    client.close()

if __name__ == "__main__":
    for i in tqdm (range (3), desc="Loading..."):
        time.sleep(0.5)
    title_page()
    main()