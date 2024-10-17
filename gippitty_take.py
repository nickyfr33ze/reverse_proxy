import socket
import threading

# Configuration
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 8888  # Port for reverse proxy to listen on
DEST_HOST = '127.0.0.1'  # Destination server IP (where traffic is forwarded)
DEST_PORT = 80  # Destination server port

def handle_client(client_socket, destination_host, destination_port):
    """Handle incoming client connections and forward to the destination server."""
    try:
        # Connect to the destination server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((destination_host, destination_port))
        
        # Start a thread to send data from client to server
        client_to_server = threading.Thread(target=forward_data, args=(client_socket, server_socket))
        client_to_server.start()

        # Start a thread to send data from server to client
        server_to_client = threading.Thread(target=forward_data, args=(server_socket, client_socket))
        server_to_client.start()

        # Wait for both threads to complete
        client_to_server.join()
        server_to_client.join()

    finally:
        client_socket.close()
        server_socket.close()

def forward_data(source_socket, destination_socket):
    """Forward data between two sockets."""
    try:
        while True:
            # Receive data from the source
            data = source_socket.recv(4096)
            if len(data) == 0:
                break  # No more data, close the connection

            # Send the data to the destination
            destination_socket.sendall(data)
    except:
        pass  # Handle disconnections or exceptions
    finally:
        source_socket.close()
        destination_socket.close()

def start_proxy(host, port, destination_host, destination_port):
    """Start the reverse proxy server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as proxy_socket:
        proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        proxy_socket.bind((host, port))
        proxy_socket.listen(5)

        print(f"Reverse Proxy listening on {host}:{port}, forwarding to {destination_host}:{destination_port}")
        
        while True:
            client_socket, addr = proxy_socket.accept()
            print(f"Connection accepted from {addr}")

            # Handle each client connection in a new thread
            client_handler = threading.Thread(
                target=handle_client,
                args=(client_socket, destination_host, destination_port)
            )
            client_handler.start()

# Start the reverse proxy
if __name__ == "__main__":
    start_proxy(HOST, PORT, DEST_HOST, DEST_PORT)