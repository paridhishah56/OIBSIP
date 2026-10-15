"""A two-client TCP chat server using newline-delimited UTF-8 messages."""

import argparse
from datetime import datetime
import re
import socket
import threading


HOST = "127.0.0.1"
DEFAULT_PORT = 12345
MAX_CLIENTS = 2
MAX_FRAME_BYTES = 4096
MAX_USERNAME_LENGTH = 20
_USERNAME_PATTERN = re.compile(r"[A-Za-z0-9_-]{1,20}\Z")


def encode_frame(message):
    """Encode one protocol message, ending it with the framing newline."""
    if "\n" in message or "\r" in message:
        raise ValueError("Messages must fit on one line.")

    encoded = message.encode("utf-8")
    if len(encoded) > MAX_FRAME_BYTES:
        raise ValueError("Message is too long.")
    return encoded + b"\n"


def extract_frames(buffer):
    """Return complete decoded messages and the unconsumed partial frame."""
    messages = []
    while b"\n" in buffer:
        frame, buffer = buffer.split(b"\n", 1)
        if frame.endswith(b"\r"):
            frame = frame[:-1]
        if len(frame) > MAX_FRAME_BYTES:
            raise ValueError("Message is too long.")
        messages.append(frame.decode("utf-8"))

    if len(buffer) > MAX_FRAME_BYTES:
        raise ValueError("Message is too long.")
    return messages, buffer


class FrameReader:
    """Read complete lines even when TCP splits or combines socket data."""

    def __init__(self):
        self.buffer = b""
        self.pending_messages = []

    def read_message(self, connection):
        while not self.pending_messages:
            chunk = connection.recv(1024)
            if not chunk:
                if self.buffer:
                    raise ConnectionError("Connection closed during a message.")
                return None
            self.pending_messages, self.buffer = extract_frames(self.buffer + chunk)

        return self.pending_messages.pop(0)


def is_valid_username(username):
    """Allow short usernames made of letters, digits, underscores, or hyphens."""
    return bool(_USERNAME_PATTERN.fullmatch(username)) and len(username) <= MAX_USERNAME_LENGTH


def timestamp():
    return datetime.now().strftime("%H:%M")


class ChatServer:
    """Accept at most two clients and relay each client's messages to the other."""

    def __init__(self, host=HOST, port=DEFAULT_PORT):
        self.host = host
        self.port = port
        self.listener = None
        self._clients = {}
        self._connections = set()
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._accept_thread = None

    def start(self):
        """Bind the listening socket, then accept clients on a background thread."""
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind((self.host, self.port))
        self.port = self.listener.getsockname()[1]
        self.listener.listen(MAX_CLIENTS)
        self.listener.settimeout(0.5)

        # The accept thread handles new connections while one handler thread
        # per client waits for messages, so either client can send at any time.
        self._accept_thread = threading.Thread(
            target=self._accept_clients,
            name="chat-acceptor",
            daemon=True,
        )
        self._accept_thread.start()

    def _accept_clients(self):
        while not self._stop_event.is_set():
            try:
                connection, address = self.listener.accept()
            except socket.timeout:
                continue
            except OSError:
                if not self._stop_event.is_set():
                    print("The listening socket closed unexpectedly.")
                break

            with self._lock:
                is_full = len(self._connections) >= MAX_CLIENTS
                if not is_full:
                    self._connections.add(connection)

            if is_full:
                try:
                    connection.sendall(encode_frame("ERROR Chat is full; only two clients are allowed."))
                except OSError:
                    pass
                finally:
                    connection.close()
                continue

            print(f"Connection from {address[0]}:{address[1]}")
            threading.Thread(
                target=self._handle_client,
                args=(connection,),
                name="chat-client",
                daemon=True,
            ).start()

    def _handle_client(self, connection):
        reader = FrameReader()
        username = None

        try:
            username = reader.read_message(connection)
            if username is None:
                return
            if not is_valid_username(username):
                connection.sendall(encode_frame(
                    "ERROR Use 1-20 letters, digits, underscores, or hyphens for your username."
                ))
                return

            with self._lock:
                self._clients[connection] = username
            connection.sendall(encode_frame(f"OK Connected as {username}."))

            while not self._stop_event.is_set():
                message = reader.read_message(connection)
                if message is None:
                    break
                if message:
                    self._broadcast(
                        f"[{timestamp()}] {username}: {message}",
                        excluded_connection=connection,
                    )
        except (ConnectionError, OSError, UnicodeDecodeError, ValueError) as error:
            if not self._stop_event.is_set():
                print(f"Client connection ended: {error}")
        finally:
            self._remove_client(connection)

    def _broadcast(self, message, excluded_connection=None):
        """Send a framed message to connected peers; the lock keeps sends safe."""
        failed_usernames = []
        framed_message = encode_frame(message)

        # A single lock protects the client list and prevents concurrent writes
        # from interleaving bytes on the same TCP connection.
        with self._lock:
            for connection, username in list(self._clients.items()):
                if connection is excluded_connection:
                    continue
                try:
                    connection.sendall(framed_message)
                except OSError:
                    self._clients.pop(connection, None)
                    self._connections.discard(connection)
                    connection.close()
                    failed_usernames.append(username)

        for username in failed_usernames:
            self._broadcast(f"[{timestamp()}] {username} disconnected.")

    def _remove_client(self, connection):
        with self._lock:
            username = self._clients.pop(connection, None)
            self._connections.discard(connection)

        try:
            connection.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        connection.close()

        if username is not None and not self._stop_event.is_set():
            self._broadcast(f"[{timestamp()}] {username} disconnected.")

    def close(self):
        """Stop accepting clients and close all current client connections."""
        self._stop_event.set()
        if self.listener is not None:
            try:
                self.listener.close()
            except OSError:
                pass

        with self._lock:
            connections = list(self._connections)
            self._clients.clear()
            self._connections.clear()

        for connection in connections:
            try:
                connection.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            connection.close()

        if self._accept_thread is not None:
            self._accept_thread.join(timeout=1)


def main():
    parser = argparse.ArgumentParser(description="Run a two-client localhost chat server.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="TCP port (default: 12345)")
    arguments = parser.parse_args()

    server = ChatServer(port=arguments.port)
    try:
        server.start()
        print(f"Chat server listening on {server.host}:{server.port}. Press Ctrl+C to stop.")
        threading.Event().wait()
    except KeyboardInterrupt:
        print("\nStopping chat server...")
    except OSError as error:
        print(f"Could not start the server: {error}")
    finally:
        server.close()
        print("Chat server stopped.")


if __name__ == "__main__":
    main()