# Task 3: Random Password Generator

## Project Overview

A desktop password generator built with Python and Tkinter. It uses the operating system's cryptographic randomness, lets you choose password length and character categories, estimates password strength, copies passwords to the clipboard, and keeps a short session-only history.

The strength indicator is approximate. It is not a guarantee that a password is uncrackable, and it does not check passwords against known breaches or account-specific risks.

## Features

- Adjustable password length from 8 to 128 characters.
- Uppercase, lowercase, digit, and special-character options; each selected category is guaranteed at least once.
- Optional exclusion of ambiguous characters: `0`, `O`, `o`, `1`, `l`, and `I`.
- Weak, Medium, or Strong visual strength feedback.
- Automatic clipboard copy after generation and a separate copy button.
- Optional password reveal and in-memory history limited to the last five values.
- Helpful validation messages and graceful clipboard error handling.

## Prerequisites and Installation

- Python 3.10 or newer with Tkinter available. Tkinter is included with most Windows and macOS Python installers. On Linux, install the distribution's Tk package if needed (for example, `python3-tk`).
- `pyperclip` for clipboard integration.

From this folder, install the dependency with:

```powershell
python -m pip install -r requirements.txt
```

Clipboard access depends on the desktop environment. If the package is missing or the operating system clipboard is unavailable, password generation still works and the application displays a message.

## Run the Application

```powershell
python .\main.py
```

Choose a length and at least one character category, then select **Generate Password**. The generated password is copied automatically when clipboard access is available. Use **Show** to reveal or conceal it. The session history shows up to five recent passwords; select **Clear History** to remove them.

**Security note:** History contains sensitive passwords and remains visible in the app until cleared or the window closes. It is held in memory only and is not written to files, databases, or logs. The clipboard may retain a copied password after the application closes; clear it when appropriate.

## Run Automated Tests

The test suite uses the standard library `unittest` module and does not require a display or clipboard:

```powershell
python -m unittest discover -s tests -v
```

Tests cover length boundaries, category selection and representation, ambiguous-character exclusion, invalid options, use of secure randomness, strength estimates, and the five-item history limit.

## How Secure Generation Works

`password_generator.py` builds a character set for each selected category, optionally removes ambiguous characters, selects one cryptographically random character from each category using `secrets.choice`, fills the remaining positions from the combined pool, and securely shuffles the result with `secrets.SystemRandom().shuffle()`. It rejects invalid lengths, empty category selections, and unusable character pools.

Python's `secrets` module is designed for security-sensitive values and draws from the operating system's strongest available randomness source. The `random` module is intended for simulations and general-purpose use; its output is deterministic when its state is known and is not suitable for passwords.

## Project Files

```text
Task-3-Random-Password-Generator/
|-- main.py                         Tkinter application and clipboard integration
|-- password_generator.py           Secure generation, strength estimate, session history
|-- requirements.txt                Clipboard dependency
|-- README.md                        Setup, use, and security notes
|-- .gitignore                       Python cache and virtual environment exclusions
|-- tests/
|   `-- test_password_generator.py   Automated unit tests
|-- screenshots/                     Application screenshots (capture locally)
`-- recordings/                      Optional demo recording location
```

Screenshots and recordings are not generated automatically. Save screenshots in `screenshots/` and, if recording a demo, use `recordings/OIBSIP_Python_Task3_Random_Password_Generator.mp4`.

## Usage Demonstration

1. Set the length to `20`, leave all four categories enabled, and check **Exclude ambiguous characters**.
2. Click **Generate Password**. Confirm the result contains uppercase, lowercase, digits, and punctuation, none of the excluded characters, and appears in the history. It is copied automatically when supported.
3. Click **Show** to inspect the result, then **Copy to Clipboard** to copy it again. Generate additional passwords to see history retain only the newest five.
4. Click **Clear History**, then close the window. No generated values are persisted by the application.

## Screenshots and Recording

Capture the main window after generating a password for `screenshots/main_window.png`. To show the strength indicator, use a sufficiently long password with at least three categories and capture `screenshots/password_strength.png`. Record the usage demonstration above to `recordings/OIBSIP_Python_Task3_Random_Password_Generator.mp4`; avoid exposing real passwords or unrelated personal information in shared recordings.
