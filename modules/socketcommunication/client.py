import socket
from cryptography.fernet import Fernet
from colorama import Fore, Style, init

init(autoreset=True)

def generate_key():
    return Fernet.generate_key()

def encrypt_message(message, key):
    try:
        cipher = Fernet(key)
        encrypted_message = cipher.encrypt(message.encode('utf-8'))
        return encrypted_message
    except Exception as error:
        print("Something went wrong while encrypting message!", error)

def client():
    try:
        host = '127.0.0.1'
        port = 41270

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        print(f"{Fore.GREEN}Connected to server at {host}:{port}{Style.RESET_ALL}")

        # Generate key on the client side
        key = generate_key()
        print(f"{Fore.YELLOW}Generated key:{Style.RESET_ALL} {key}")

        # Send the key to the server
        client_socket.send(key)

        message = input(f"{Fore.BLUE}Enter the message to send:{Style.RESET_ALL} ")
        encrypted_message = encrypt_message(message, key)
        print(f"{Fore.YELLOW}Encrypted message:{Style.RESET_ALL} {encrypted_message}")

        client_socket.send(encrypted_message)

        response = client_socket.recv(1024).decode('utf-8')
        print(f"{Fore.GREEN}Server response:{Style.RESET_ALL} {response}")

        client_socket.close()
    except Exception as error:
        print("Error! Something went wrong: ", error)
        client_socket.close()

if __name__ == "__main__":
    client()
