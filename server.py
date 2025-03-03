import socket
import threading
import en

HOST = '192.168.152.218'  # Replace with your IP
PORT = 9090

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
nicknames = []

def broadcast(message):
    """Send a message to all connected clients."""
    for client in clients:
        client.send(message)

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            if not message:
                raise ConnectionResetError  # Handle empty message (client closed)
            print(f"{nicknames[clients.index(client)]} says {message}")
            broadcast(message)
        except (ConnectionResetError, ConnectionAbortedError):
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames.pop(index)
            print(f"{nickname} disconnected.")
            broadcast(f"{nickname} has left the chat.".encode('utf-8'))
            break

def receive():
    """Accept new client connections."""
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}!")

        client.send("NICK".encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')  # Decode nickname

        nicknames.append(nickname)
        clients.append(client)

        join_message = f"{nickname} has joined the chat."
        print(join_message)
        broadcast(en.enc(join_message, 2).encode('utf-8'))  # Notify others

        welcome_message = "Connected to the server"
        client.send(en.enc(welcome_message, 2).encode('utf-8'))  # Send welcome message

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print("Server running...")
receive()
