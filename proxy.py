import binascii
import socket
import threading

# Target server details
TARGET_HOST = '172.30.2.70'  # Change to the actual server's address if needed
TARGET_PORT = 8800

# Proxy server details
PROXY_HOST = '0.0.0.0'
PROXY_PORT = 8800


def log_data(data, direction):
    hex_data = binascii.hexlify(data).decode('utf-8')
    ascii_data = data.decode('utf-8', errors='replace')
    print(f"{direction} - {ascii_data}")


def handle_client(client_socket):
    # Connect to the target server
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((TARGET_HOST, TARGET_PORT))

    def forward(src_socket, dest_socket, direction):
        while True:
            data = src_socket.recv(4096)
            if len(data) == 0:
                break
            log_data(data, direction)
            dest_socket.sendall(data)

    # Start forwarding traffic between client and target server
    client_to_remote = threading.Thread(target=forward, args=(client_socket, remote_socket, '>'))
    remote_to_client = threading.Thread(target=forward, args=(remote_socket, client_socket, '<'))

    client_to_remote.start()
    remote_to_client.start()

    client_to_remote.join()
    remote_to_client.join()

    # Close sockets
    client_socket.close()
    remote_socket.close()


def start_proxy():
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.bind((PROXY_HOST, PROXY_PORT))
    proxy_socket.listen(5)
    print(f"Proxy server started and listening on {PROXY_HOST}:{PROXY_PORT}")

    while True:
        client_socket, addr = proxy_socket.accept()
        print(f"Accepted connection from {addr}")

        # Handle the client connection in a new thread
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()


if __name__ == '__main__':
    start_proxy()
