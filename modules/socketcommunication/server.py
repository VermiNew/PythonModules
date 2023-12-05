import socket
from cryptography.fernet import Fernet
from colorama import Fore, Style

def generate_key():
    return Fernet.generate_key()

def encrypt_message(message, key):
    try:
        cipher = Fernet(key)
        encrypted_message = cipher.encrypt(message.encode('utf-8'))
        return encrypted_message
    except Exception as error:
        print("Error while decrypting message! ", error)
        return ""

def decrypt_message(encrypted_message, key):
    cipher = Fernet(key)
    decrypted_message = cipher.decrypt(encrypted_message).decode('utf-8')
    return decrypted_message

def server():
    try:
        host = '127.0.0.1'
        port = 41270

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen(1)

        print(f"{Fore.GREEN}Server is listening on {host}:{port}{Style.RESET_ALL}")

        client_socket, addr = server_socket.accept()
        print(f"{Fore.GREEN}Connection established with {addr}{Style.RESET_ALL}")

        # Receive the key from the client
        key = client_socket.recv(1024)
        print(f"{Fore.YELLOW}Received key from client:{Style.RESET_ALL} {key}")

        encrypted_message = client_socket.recv(1024)
        print(f"{Fore.YELLOW}Received encrypted message from client:{Style.RESET_ALL} {encrypted_message}")

        decrypted_message = decrypt_message(encrypted_message, key)
        print(f"{Fore.YELLOW}Decrypted message:{Style.RESET_ALL} {decrypted_message}")

        response = "Server has finished processing and decrypting the message."
        client_socket.send(response.encode('utf-8'))
        print(f"{Fore.GREEN}Response sent to client:{Style.RESET_ALL} {response}")

        client_socket.close()
        server_socket.close()
    except Exception as error:
        print("Error! Something went wrong [Exception]. Reason: ", error)
        client_socket.close()
        server_socket.close()

if __name__ == "__main__":
    server()
