"""Interactive terminal client for the two-client TCP chat server."""

import socket
import threading

from server import FrameReader, encode_frame, is_valid_username


SERVER_HOST = "127.0.0.1"
SERVER_PORT = 12345


def connect_to_server(host=SERVER_HOST, port=SERVER_PORT):
    """Use a connection timeout, then keep the chat socket open while idle."""
    connection = socket.create_connection((host, port), timeout=5)
    connection.settimeout(None)
    return connection


def ask_username():
    while True:
        username = input("Choose a username (letters, digits, _ or -, up to 20 characters): ").strip()
        if is_valid_username(username):
            return username
        print("Invalid username. Use 1-20 letters, digits, underscores, or hyphens.")


def receive_messages(connection, reader, stop_event):
    try:
        while not stop_event.is_set():
            message = reader.read_message(connection)
            if message is None:
                print("\nThe server closed the connection.")
                break
            print(f"\n{message}")
    except (ConnectionError, OSError, UnicodeDecodeError, ValueError) as error:
        if not stop_event.is_set():
            print(f"\nConnection lost: {error}")
    finally:
        stop_event.set()


def send_messages(connection, stop_event):
    try:
        while not stop_event.is_set():
            message = input("> ")
            if message.strip() == "/quit":
                stop_event.set()
                break
            if message:
                connection.sendall(encode_frame(message))
    except EOFError:
        stop_event.set()
    except (ConnectionError, OSError, ValueError) as error:
        if not stop_event.is_set():
            print(f"\nCould not send message: {error}")
            stop_event.set()


def run_client():
    username = ask_username()

    try:
        connection = connect_to_server()
    except OSError as error:
        print(f"Could not connect to {SERVER_HOST}:{SERVER_PORT}: {error}")
        print("Start the server first, then try again.")
        return

    reader = FrameReader()
    try:
        connection.sendall(encode_frame(username))
        response = reader.read_message(connection)
        if response is None or response.startswith("ERROR "):
            print(response or "The server closed the connection before joining.")
            return
        print(response)
        print("Type /quit to leave the chat.")

        stop_event = threading.Event()
        # One thread blocks on incoming socket data while the main thread reads
        # keyboard input, allowing messages to arrive during typing.
        receiver = threading.Thread(
            target=receive_messages,
            args=(connection, reader, stop_event),
            name="chat-receiver",
            daemon=True,
        )
        receiver.start()
        send_messages(connection, stop_event)
        stop_event.set()
        receiver.join(timeout=1)
    except (ConnectionError, OSError, UnicodeDecodeError, ValueError) as error:
        print(f"Connection ended: {error}")
    except KeyboardInterrupt:
        print("\nLeaving the chat...")
    finally:
        try:
            connection.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        connection.close()


if __name__ == "__main__":
    run_client()