# Task 5: Chat Application

## Project Overview

This beginner-tier project is a small real-time chat application for two users on one computer. A TCP server listens only on `127.0.0.1`, and both clients connect to that same server from separate terminal windows. Each client can send and receive messages while the other user is typing.

## Objectives

- Practice Python sockets for communication over TCP.
- Use threads to accept connections and handle simultaneous chat activity.
- Frame messages so partial or combined TCP reads are handled correctly.
- Practice input validation, exception handling, and automated tests.

## Features

- Supports up to two connected clients; additional connections receive a clear rejection.
- Timestamps every chat message and identifies its sender.
- Uses UTF-8 and newline-delimited message frames.
- Announces when a joined user disconnects.
- Handles server shutdown, lost connections, and Ctrl+C without a traceback.
- Uses only Python standard-library modules.

## Technologies

- Python 3
- `socket`, `threading`, `datetime`, `argparse`, `re`, and `unittest`

## Folder Structure

```text
Python-Task5-ChatApplication/
|-- client.py
|-- server.py
|-- test_chat.py
`-- README.md
```

## Prerequisites

- Python 3 installed. The commands below use this workspace's Python 3.14 interpreter at `C:\Python314\python.exe`.
- No third-party packages, accounts, passwords, or external services are needed.

## Run the Chat

Use three separate PowerShell terminal windows. Both users should connect to the same server on this computer; do not start a separate server for each user.

In **Terminal 1**, start the server:

```powershell
Set-Location "C:\Users\parid\OneDrive\Documents\python intern\OIBSIP\Python-Task5-ChatApplication"
& "C:\Python314\python.exe" .\server.py
```

The default server address is `127.0.0.1:12345`. To use a different available port, pass it to the server with `python .\server.py --port 12346`. The client in this beginner version uses the default port, so keep `12345` for the documented two-client setup.

In **Terminal 2**, start the first client:

```powershell
Set-Location "C:\Users\parid\OneDrive\Documents\python intern\OIBSIP\Python-Task5-ChatApplication"
& "C:\Python314\python.exe" .\client.py
```

In **Terminal 3**, start the second client using the same command:

```powershell
Set-Location "C:\Users\parid\OneDrive\Documents\python intern\OIBSIP\Python-Task5-ChatApplication"
& "C:\Python314\python.exe" .\client.py
```

Each client asks for a username; use a unique name containing 1-20 letters, digits, underscores, or hyphens.

## Sample Conversation

```text
Alice's terminal: > Hello, Bob!
Bob's terminal:   [14:35] Alice: Hello, Bob!
Bob's terminal:   > Hi, Alice!
Alice's terminal: [14:36] Bob: Hi, Alice!
```

The displayed time is the local time on the server computer.

## Exit and Troubleshooting

- Type `/quit` in either client to leave. The other client receives a timestamped disconnect notice.
- Press `Ctrl+C` in the server terminal to stop the server. Connected clients will report that the connection closed.
- If a client cannot connect, confirm that the server is running in Terminal 1 and that both scripts are using port `12345`.
- If the port is already occupied, stop the other local process using it before starting the server.
- A third client is rejected until one of the two connected users leaves.

## Run the Tests

From the task folder in PowerShell:

```powershell
& "C:\Python314\python.exe" -m unittest -v
```

The tests check UTF-8 framing, partial and multiple frames, username validation, bidirectional delivery, the two-client limit, and disconnect announcements. The integration tests start their own server on an OS-assigned free port; no manual server is required.

## Beginner-Version Limitations

- The server is local-only and binds to `127.0.0.1`; it is not reachable by another computer.
- Only two clients can chat at once.
- Messages are plain text and are not encrypted.
- Chat history is not saved, and there is no user authentication or graphical interface.
- The client connects to port `12345`; changing the server port requires updating `SERVER_PORT` in `client.py` too.

## Internship Demo Video and Screenshot Checklist

- Show the project folder and the server running in its own terminal.
- Show two separate client terminals joining with different usernames.
- Demonstrate a message sent in each direction and the timestamped output.
- Type `/quit` in one client and show the disconnect notice in the remaining client.
- Optionally demonstrate that a third client is rejected and show the passing test output.
- Capture clear screenshots of the server, both clients, and the test results; avoid showing unrelated personal information.