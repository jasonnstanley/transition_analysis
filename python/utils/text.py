"""
Text formatting utilities used throughout the Transition Analysis Toolkit.
"""

NUMBER_WORDS = {
    0: "zero",
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
    10: "ten",
}


def number_to_word(value: int) -> str:
    """
    Convert a small integer into its English word.

    Values outside the dictionary fall back to their numeric string.
    """
    return NUMBER_WORDS.get(value, str(value))