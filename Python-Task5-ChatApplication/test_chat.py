import socket
import unittest

from client import connect_to_server
from server import ChatServer, FrameReader, encode_frame, extract_frames, is_valid_username


class ChatProtocolTests(unittest.TestCase):
    def test_encode_and_extract_utf8_message(self):
        frame = encode_frame("Hello, world! こんにちは")
        messages, remainder = extract_frames(frame)

        self.assertEqual(messages, ["Hello, world! こんにちは"])
        self.assertEqual(remainder, b"")

    def test_extracts_partial_and_multiple_frames(self):
        messages, remainder = extract_frames(b"first\nsecond par")
        self.assertEqual(messages, ["first"])
        self.assertEqual(remainder, b"second par")

        messages, remainder = extract_frames(remainder + b"t\nthird\n")
        self.assertEqual(messages, ["second part", "third"])
        self.assertEqual(remainder, b"")

    def test_rejects_line_breaks_and_oversized_frames(self):
        with self.assertRaises(ValueError):
            encode_frame("one\ntwo")
        with self.assertRaises(ValueError):
            encode_frame("x" * 4097)
        with self.assertRaises(ValueError):
            extract_frames(b"x" * 4097)

    def test_validates_usernames(self):
        self.assertTrue(is_valid_username("Alice_2"))
        self.assertFalse(is_valid_username(""))
        self.assertFalse(is_valid_username("two words"))
        self.assertFalse(is_valid_username("x" * 21))


class ChatServerIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.server = ChatServer(port=0)
        self.server.start()
        self.clients = []

    def tearDown(self):
        for client in self.clients:
            client.close()
        self.server.close()

    def connect_client(self, username):
        client = socket.create_connection(("127.0.0.1", self.server.port), timeout=3)
        client.settimeout(3)
        self.clients.append(client)
        client.sendall(encode_frame(username))
        reader = FrameReader()
        response = reader.read_message(client)
        self.assertEqual(response, f"OK Connected as {username}.")
        return client, reader

    def test_client_socket_stays_blocking_after_connection(self):
        client = connect_to_server(port=self.server.port)
        self.clients.append(client)

        self.assertIsNone(client.gettimeout())

    def test_messages_are_bidirectional_and_disconnect_is_announced(self):
        alice, alice_reader = self.connect_client("Alice")
        bob, bob_reader = self.connect_client("Bob")

        alice.sendall(encode_frame("Hello, Bob!"))
        bob_message = bob_reader.read_message(bob)
        self.assertRegex(bob_message, r"^\[\d{2}:\d{2}\] Alice: Hello, Bob!$")

        bob.sendall(encode_frame("Hi, Alice!"))
        alice_message = alice_reader.read_message(alice)
        self.assertRegex(alice_message, r"^\[\d{2}:\d{2}\] Bob: Hi, Alice!$")

        bob.shutdown(socket.SHUT_RDWR)
        bob.close()
        self.assertRegex(
            alice_reader.read_message(alice),
            r"^\[\d{2}:\d{2}\] Bob disconnected\.$",
        )

    def test_rejects_a_third_client(self):
        self.connect_client("Alice")
        self.connect_client("Bob")

        extra_client = socket.create_connection(("127.0.0.1", self.server.port), timeout=3)
        extra_client.settimeout(3)
        self.clients.append(extra_client)
        message = FrameReader().read_message(extra_client)

        self.assertEqual(message, "ERROR Chat is full; only two clients are allowed.")


if __name__ == "__main__":
    unittest.main()