import socket
import threading
import sys
import time

odd_key_dict = {}
even_key_dict = {}
primary_server_running = True  # Global flag to track server state
secondary_server_running = True  # Global flag to track server state
client_sockets = {}


# primary code

# Function to handle each client connection
# def handle_client(client_socket):
#     global primary_server_running
#     while primary_server_running:
#         try:
#             input_message = client_socket.recv(1024).decode('utf-8')  # Receive message from the client
#             if not input_message:
#                 break
           
#             #print(f"Received from client: {input_message}")

#             time.sleep(3)
#             split_message = input_message.split()
#             command = split_message[0]
#             key = int(split_message[1])

#             client_ip = split_message[-2]  # Second-to-last word
#             client_port = int(split_message[-1])  # Last word (convert to integer)


#             if key % 2 == 1:
#                 if command == "insert":
#                     odd_key_dict[key] = split_message[2]
#                     print(f"Successfully inserted key {key}")
#                     response = f"Success"
#                     #response = f"Success"
#                 elif command == "lookup":
#                     value = odd_key_dict.get(key, "NOT FOUND")
#                     print(value)
#                     response = f"{value}"
#                 client_socket.send(f"{response}".encode('utf-8'))  # Echo the message back
#             else:
#                 forward_message(input_message, client_ip, client_port)
#                 response = "wait"
#                 client_socket.send(f"{response}".encode('utf-8'))  # Echo the message back
#         except ConnectionResetError:
#             break
#         except Exception as e:
#             #print(f"Error handling client {client_ip}, {client_port}: {e}")
#             break
#     #print("Closing client socket...")
#     client_socket.close()  # Close the connection when done
#     #print("Client socket is closed.")


## Modified for Gradescope
def handle_client(client_socket):
    global primary_server_running
    while primary_server_running:
        try:
            input_message = client_socket.recv(1024).decode('utf-8')  # Receive message from the client
            if not input_message:
                break

            # Start a new thread to process each message
            threading.Thread(target=process_client_message, args=(client_socket, input_message), daemon=True).start()

        except ConnectionResetError:
            break
        except Exception as e:
            # Handle exceptions as needed
            break
    client_socket.close()  # Close the connection when done

def process_client_message(client_socket, input_message):
    try:
        # Simulate processing time
        time.sleep(3)

        split_message = input_message.split()
        command = split_message[0]
        key = int(split_message[1])
        client_ip = split_message[-2]  # Second-to-last word
        client_port = int(split_message[-1])  # Last word (convert to integer)


        if key % 2 == 1:
            if command == "insert":
                odd_key_dict[key] = split_message[2]
                print(f"Successfully inserted key {key}")
                response = f"Success"
                #response = f"Success"
            elif command == "lookup":
                value = odd_key_dict.get(key, "NOT FOUND")
                print(value)
                response = f"{value}"
            client_socket.send(f"{response}".encode('utf-8'))  # Echo the message back
        else:
            forward_message(input_message, client_ip, client_port)
            response = "wait"
            client_socket.send(f"{response}".encode('utf-8'))  # Echo the message back

    except Exception as e:
        # Handle exceptions as needed
        pass


def forward_message(message, client_ip, client_port):
    try:
        secondary_message = f"{message} {client_ip} {client_port}"
        secondary_socket.send(secondary_message.encode('utf-8'))
        print("Forwarding to secondary server")
    except Exception as e:
        pass
    #print("Error forwarding to secondary server")

# Function to handle server standard input
def handle_primary_server_input(server_socket):
    global primary_server_running
    while primary_server_running:
        command = input()
        if command.lower() == "exit":
            primary_server_running = False  # Set flag to stop server
            close_primary_server()
        elif command.lower() == "dictionary":
            message = "dict"
            secondary_socket.send(message.encode('utf-8'))
            response = secondary_socket.recv(1024).decode('utf-8')
            #print(f"Returned dictionary before sleep: {response}")
            time.sleep(3)
            #print(f"Returned dictionary after sleep: {response}")
            odd_dict_string = dict_to_custom_string(odd_key_dict)
            print(f"primary {odd_dict_string}, secondary {response}")


def dict_to_custom_string(my_dict):
    # Create a list of string representations of each key-value pair as tuples
    tuple_pairs = [f"({key}, {value})" for key, value in sorted(my_dict.items())]
    
    # Join the list of tuple pairs with commas and wrap it in curly braces
    result = "{" + ", ".join(tuple_pairs) + "}"
    
    return result

def close_primary_server():
    #print("Closing secondary socket...")
    secondary_socket.close()
    #print("Secondary server is closed...")
    #print("Closing primary server...")
    server_socket.close()
    #print("Primary server is closed...")
    sys.stdout.flush()
    sys.exit(0)

def start_primary_server():
    global primary_server_running
    global server_socket 
    global secondary_socket
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('127.0.0.1', 9000))  # Bind to any address on port 9999


    server_socket.listen(5)  # Start listening for connections
    #print("Server started on port 9999")

    # Start a thread to handle server standard input (exit and dictionary commands)
    threading.Thread(target=handle_primary_server_input, args=(server_socket,), daemon=True).start()

    try:
        secondary_socket, addr = server_socket.accept()  # Accept connections
        #print(f"Accepted secondary server connection at {addr}")

    except Exception as e:
        pass
        #print("Error accepting connection from secondary server...")

    while primary_server_running:
        try:
            client_socket, addr = server_socket.accept()  # Accept client connections
            #print(f"Accepted connection from {addr}")
            client_handler = threading.Thread(target=handle_client, args=(client_socket,), daemon=True)  # Create a new thread
            client_handler.start()  # Start the new thread
        except Exception as e:
            if not primary_server_running:
                break
            #print(f"Error accepting connection: {e}")
    
    # Close the server socket when done
    server_socket.close()
    #print("Primary server shutdown complete.")


# secondary code

# # Function to handle each client connection
# def handle_primary_message(primary_socket):
#     global secondary_server_running
#     while secondary_server_running:
#         try:
#             input_message = primary_socket.recv(1024).decode('utf-8')  # Receive message from the primary server


#             if not input_message:
#                 continue
            
#             time.sleep(3)
#             if input_message == "dict":
#                 #print(f"Raw dictionary: {even_key_dict}")
#                 string_dict = dict_to_custom_string(even_key_dict)
#                 #print(f"Dictionary after string_dict: {string_dict}")
#                 primary_socket.send(string_dict.encode('utf-8'))
#                 #print("Sent dictionary to primary server")
#                 continue

#             split_message = input_message.split()
#             command = split_message[0]
#             key = int(split_message[1])
#             client_ip = split_message[-2]
#             client_port = int(split_message[-1])

#             if command == "insert":
#                 even_key_dict[key] = split_message[2]
#                 print(f"Successfully inserted key {key}")
#                 response = f"Success"
#                 send_to_client(response, client_ip, client_port)

#             elif command == "lookup":
#                 response = even_key_dict.get(key, "NOT FOUND")
#                 print(response)
#                 send_to_client(response, client_ip, client_port)
            
            
                

#         except (ConnectionResetError, Exception) as e:
#             #print(f"Error processing message from primary server: {e}")
#             pass
#     primary_socket.close()  # Close the connection when done
#     if not secondary_server_running:
#         close_secondary_server()




##ADDED FOR GRADESCOPE
def handle_primary_message(primary_socket):
    global secondary_server_running
    while secondary_server_running:
        try:
            input_message = primary_socket.recv(1024).decode('utf-8')
            if not input_message:
                continue

            # Start a new thread to process each message
            threading.Thread(target=process_primary_message, args=(input_message,), daemon=True).start()
        except Exception as e:
            pass  # Handle exceptions as needed
    primary_socket.close()

def process_primary_message(input_message):
    global secondary_server_running
    # Simulate processing time
    time.sleep(3)
    
    # Existing processing logic
    if input_message == "dict":
        string_dict = dict_to_custom_string(even_key_dict)
        primary_socket.send(string_dict.encode('utf-8'))
    else:
        split_message = input_message.split()
        command = split_message[0]
        key = int(split_message[1])
        client_ip = split_message[-2]
        client_port = int(split_message[-1])

        if command == "insert":
            even_key_dict[key] = split_message[2]
            print(f"Successfully inserted key {key}")
            response = "Success"
            send_to_client(response, client_ip, client_port)
        elif command == "lookup":
            response = even_key_dict.get(key, "NOT FOUND")
            print(response)
            send_to_client(response, client_ip, client_port)

def send_to_client(response, client_ip, client_port):
    try:
        # Look up the client's socket using their (IP, port) as the key
        client_socket = client_sockets.get((client_ip, client_port))
        if client_socket:
            client_socket.send(response.encode())  # Send the response to the client
            #print(f"Sent to client {client_ip}:{client_port}: {response}")
        else:
            pass
            #print(f"Client {client_ip}:{client_port} not found.")
    except Exception as e:
        print(f"Error sending message to client {client_ip}:{client_port}: {e}")



def close_secondary_server():
    secondary_server_running = False
    secondary_server.close()
    primary_socket.close()
    
    #print("Shut down secondary server...")

    sys.stdout.flush()
    sys.exit(0)


def connection_handler(client_socket, addr):
    # Store the client socket in the dictionary with the client's address as the key
    client_sockets[addr] = client_socket
    #print(f"Stored client connection from {addr}")


# Function to handle server standard input
def handle_secondary_server_input(secondary_server):
    global secondary_server_running
    while secondary_server_running:
        command = input()
        if command.lower() == "exit":
            secondary_server_running = False  # Set flag to stop server
            close_secondary_server()


def start_secondary_server():
    global secondary_server_running
    global secondary_server
    global primary_socket

    secondary_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket
    secondary_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    secondary_server.bind(('127.0.0.1', 9001))  # Bind to any address on port 9998
    secondary_server.listen(5)  # Start listening for connections
    #print("Secondary server started on port 9998")

    primary_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket
    primary_socket.connect(('127.0.0.1', 9000))  # Connect to the primary server at localhost on port 9999
    #print("Connected to primary server at 127.0.0.1:9999")

    # Start a thread to handle messages from the primary server
    primary_handler_thread = threading.Thread(target=handle_primary_message, args=(primary_socket,))
    primary_handler_thread.start()
    
    # Start a thread to handle server standard input (exit and dictionary commands)
    threading.Thread(target=handle_secondary_server_input, args=(secondary_server,), daemon=True).start()

    while secondary_server_running:
        try:
            client_connection, addr = secondary_server.accept()  # Accept connections
            #print(f"Accepted connection at {addr}")
            client_handler = threading.Thread(target=connection_handler, args=(client_connection, addr))
            client_handler.start()
        except Exception as e:
            if not secondary_server_running:
                break
            #print(f"Error accepting connection: {e}")
    
    secondary_server.close()
    #print("Secondary server shutdown complete")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 server.py [primary|secondary]")
        sys.exit(1)

    server_type = sys.argv[1]
    if server_type == 'primary':
        start_primary_server()
    elif server_type == 'secondary':
        start_secondary_server()
    else:
        print("Invalid server type. Use 'primary' or 'secondary'.")