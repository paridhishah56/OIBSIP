"""Cryptographically secure password generation and session history."""

from collections import deque
from dataclasses import dataclass
import secrets
import string

MIN_LENGTH = 8
MAX_LENGTH = 128
AMBIGUOUS_CHARACTERS = frozenset("0Oo1lI")


@dataclass(frozen=True)
class PasswordOptions:
    length: int = 16
    uppercase: bool = True
    lowercase: bool = True
    digits: bool = True
    special_characters: bool = True
    exclude_ambiguous: bool = False

    def selected_categories(self) -> tuple[str, ...]:
        categories = []
        if self.uppercase:
            categories.append(string.ascii_uppercase)
        if self.lowercase:
            categories.append(string.ascii_lowercase)
        if self.digits:
            categories.append(string.digits)
        if self.special_characters:
            categories.append(string.punctuation)
        return tuple(categories)


def _filtered_categories(options: PasswordOptions) -> tuple[str, ...]:
    categories = options.selected_categories()
    if options.exclude_ambiguous:
        categories = tuple(
            "".join(character for character in category if character not in AMBIGUOUS_CHARACTERS)
            for category in categories
        )
    return categories


def generate_password(options: PasswordOptions) -> str:
    """Generate a password that includes at least one character per category."""
    if isinstance(options.length, bool) or not isinstance(options.length, int):
        raise ValueError("Password length must be a whole number.")
    if not MIN_LENGTH <= options.length <= MAX_LENGTH:
        raise ValueError(f"Password length must be between {MIN_LENGTH} and {MAX_LENGTH}.")

    categories = _filtered_categories(options)
    if not categories:
        raise ValueError("Select at least one character category.")
    if any(not category for category in categories):
        raise ValueError("The selected categories have no usable characters with this exclusion.")
    if len(categories) > options.length:
        raise ValueError("Password length is too short for the selected categories.")

    password_characters = [secrets.choice(category) for category in categories]
    character_pool = "".join(categories)
    password_characters.extend(
        secrets.choice(character_pool)
        for _ in range(options.length - len(password_characters))
    )
    secrets.SystemRandom().shuffle(password_characters)
    return "".join(password_characters)


def estimate_strength(password: str) -> tuple[str, int]:
    """Return an approximate strength label and progress-bar value."""
    diversity = sum(
        (
            any(character in string.ascii_lowercase for character in password),
            any(character in string.ascii_uppercase for character in password),
            any(character in string.digits for character in password),
            any(character in string.punctuation for character in password),
        )
    )
    if len(password) >= 16 and diversity >= 3:
        return "Strong", 100
    if len(password) >= 12 and diversity >= 2:
        return "Medium", 65
    return "Weak", 30


class SessionHistory:
    """Keep only the most recent generated values in memory."""

    def __init__(self, limit: int = 5) -> None:
        if limit < 1:
            raise ValueError("History limit must be at least one.")
        self._passwords: deque[str] = deque(maxlen=limit)

    def add(self, password: str) -> None:
        self._passwords.appendleft(password)

    def clear(self) -> None:
        self._passwords.clear()

    @property
    def passwords(self) -> tuple[str, ...]:
        return tuple(self._passwords)
