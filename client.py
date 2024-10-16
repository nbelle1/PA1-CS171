import socket
import threading
import time
import sys
import threading

print_lock = threading.Lock()
server_running = True

def handle_input_message(message, secondary_address):
    global server_running
    if message.lower() == 'exit':
        server_running = False
        close_client()

    else:
        full_message = f"{message} {secondary_address[0]} {secondary_address[1]}"
        primary_client.send(full_message.encode('utf-8'))  # Send the message to the server
        response = primary_client.recv(1024).decode('utf-8')
        
        time.sleep(3)
        if(response == "wait"):
            #time.sleep(3)
            time.sleep(.01)
        else:
            with print_lock:
                print(response)

def handle_secondary_response(secondary_client):
    global server_running
    while server_running:
        try:
            response = secondary_client.recv(1024).decode('utf-8')
            if(response):
                threading.Thread(target=process_secondary_response, args=(response,), daemon=True).start()
            if not response:
                break
        except ConnectionAbortedError:
            #print("Connection closed...")
            break


def process_secondary_response(response):
    time.sleep(3)
    with print_lock:
        print(response)



def close_client():
    global server_running
    server_running = False
    primary_client.close()
    secondary_client.close()
    #print("Closed all sockets.")
    sys.stdout.flush()
    sys.exit(0)


def start_client():
    global server_running
    global primary_client
    primary_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket
    primary_client.connect(('127.0.0.1', 9000))  # Connect to the primary server at localhost on port 9999

    global secondary_client
    secondary_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket
    secondary_client.connect(('127.0.0.1', 9001))  # Connect to the secondary server at localhost on port 9998

    # Get the full address (IP and port) that the client is using for the connection to the secondary server
    secondary_address = secondary_client.getsockname()

    secondary_response_thread = threading.Thread(target=handle_secondary_response, args=(secondary_client,), daemon=True)
    secondary_response_thread.start()

    while server_running:
        message = input()  # Input message from the user
        threading.Thread(target=handle_input_message, args=(message, secondary_address,), daemon=True).start()

    secondary_response_thread.join()

    

if __name__ == "__main__":
    start_client()