import socket
import threading
import json
import os
import time

HOST = '127.0.0.1'  # localhost
PORT = 8081  # port number

# create socket object and bind to the host and port
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))

# create list to store client connections and list to store messages
clients = []
messages = []

# load previously saved messages from JSON file, if it exists
if os.path.exists('messages.json'):
    with open('messages.json', 'r') as f:
        data = json.load(f)
        for message in data:
            messages.append(f"{message['Message']}")

# create function to handle client connections
def handle_client(client_socket, client_address):
    # get the client's username and add the client's connection to the clients list
    username = client_socket.recv(1024).decode('utf-8')
    clients.append((username, client_socket))

    # send the chat history to the client
    for message in messages:
        client_socket.send(message.encode('utf-8'))

    # loop to receive messages from the client and broadcast them to all clients
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            messages.append(message)

            # save messages to a JSON file
            data = []
            if os.path.exists('messages.json'):
                with open('messages.json', 'r') as f:
                    data = json.load(f)

            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            data.append({'Message': message})

            with open('messages.json', 'w') as f:
                json.dump(data, f, indent=4)

            # broadcast message to all clients
            for client in clients:
                client[1].send(message.encode('utf-8'))
        except:
            # remove the client from the clients list and close the connection
            clients.remove((username, client_socket))
            client_socket.close()
            break

# function to start the server and handle incoming connections
def start_server():
    # listen for incoming connections
    server_socket.listen()
    print("Listening for incoming messages...")
    # loop to handle incoming connections
    while True:
        client_socket, client_address = server_socket.accept()

        # create a new thread to handle the client connection
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.daemon = True
        client_thread.start()
        print('Connected to ',HOST, ':', str(PORT))


        
# start the server
start_server()
