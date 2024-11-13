import argparse
import re
import requests
from datetime import datetime


def get_nyt_response_text() -> str:
    url = "https://www.nytimes.com/puzzles/letter-boxed"
    response = requests.get(url)
    return response.text


def get_nyt_solution(text: str) -> str:
    return set(re.findall(r'"ourSolution":\[(["A-Z,]+)', text)[0].replace('"', "").split(","))


def get_nyt_sides(text: str) -> list[str]:
    return list(
        re.findall(
            r'"sides":\["([A-Z]{3})","([A-Z]{3})","([A-Z]{3})","([A-Z]{3})"\]',
            text,
        )[0]
    )


def dict_file_to_word_list(dict_file: str) -> list[str]:
    with open(dict_file, "r") as f:
        return f.read().upper().split()


def get_nyt_word_list(text: str) -> list[str]:
    return (
        re.findall(r'"dictionary":\[(["A-Z,]+)', text)[0]
        .replace('"', "")
        .split(",")
    )


def is_valid_word(word: str, sides: list[str]) -> bool:
    """Check if word can be made from given letter sides according to puzzle rules.

    A valid word must:
    - Be at least 3 letters long
    - Only use letters from the provided sides
    - Not have consecutive letters from the same side

    Args:
        word (str): Word to check for validity
        sides (list[str]): List of strings, each containing letters from one side of the puzzle

    Returns:
        bool: True if word follows all puzzle rules, False otherwise
    """
    if len(word) < 3:  # Words must be 3+ letters
        return False

    # Check all letters are from the sides
    valid_letters = list("".join(sides))
    if not all(c in valid_letters for c in word):
        return False

    # Check consecutive letters aren't from same side
    for i in range(len(word) - 1):
        for side in sides:
            if word[i] in side and word[i + 1] in side:
                return False

    return True


def group_words_by_start(
    sides: list[str], valid_words: list[str]
) -> dict[str, list[str]]:
    """Group valid words by their starting letter for efficient lookup.

    Args:
        valid_words (list[str]): List of words that are valid for the puzzle

    Returns:
        dict[str, list[str]]: Dictionary mapping starting letters to lists of words
            that begin with that letter
    """
    return {
        letter: [word for word in valid_words if word[0] == letter]
        for letter in "".join(sides)
    }


def prepare_valid_words(
    word_list: list[str], sides: list[str], skip_validation: bool
) -> tuple[list[str], dict[str, list[str]]]:
    """Prepare and organize valid words for efficient puzzle solving.

    Filters word list to only valid words according to puzzle rules,
    sorts them by length and alphabetically, and groups them by starting letter.

    Args:
        word_list (list[str]): List of all possible dictionary words
        sides (list[str]): List of strings representing letters on each side of puzzle

    Returns:
        tuple[list[str], dict[str, list[str]]]: Tuple containing:
            - List of valid words sorted by length, then alphabetically
            - Dictionary mapping starting letters to lists of valid words
    """
    valid_words = (
        [word for word in word_list if is_valid_word(word, sides)]
        if not skip_validation
        else word_list
    )
    valid_words.sort(key=lambda x: (len(x), x))
    words_by_start = group_words_by_start(sides, valid_words)
    return valid_words, words_by_start


def get_candidate_words(
    current_words: list[str],
    words_by_start: dict[str, list[str]],
    valid_words: list[str],
    remaining_letters: set[str],
    best_length: float,
    current_length: int,
) -> list[str]:
    """Get and filter valid candidate words for the next position in the solution.

    Finds words that:
    - Start with the last letter of the previous word (if any)
    - Contain at least one remaining required letter
    - Could make a solution shorter than the current best solution

    Args:
        current_words (list[str]): Words in the current partial solution
        words_by_start (dict[str, list[str]]): Words grouped by starting letter
        valid_words (list[str]): List of all valid words
        remaining_letters (set[str]): Letters that still need to be used
        best_length (float): Length of current best solution
        current_length (int): Length of current partial solution

    Returns:
        list[str]: List of valid candidate words for the next position
    """
    last_letter = current_words[-1][-1] if current_words else None
    word_pool = words_by_start[last_letter] if last_letter else valid_words
    return [
        word
        for word in word_pool
        if any(letter in word for letter in remaining_letters)
        and len(word) <= (best_length - current_length)
    ]


def calculate_solution_length(words: list[str]) -> int:
    """Calculate the total length of a solution, not double counting characters at the end of one word and the beginning of the next.

    Args:
        words (list[str]): List of words in the solution

    Returns:
        int: Total length
    """
    return sum(len(w) for w in words) - len(words) + 1


def solve_letterboxed(
    sides: list[str],
    valid_words: list[str],
    words_by_start: dict[str, list[str]],
    max_words: int,
) -> set[str]:
    """Find optimal solutions for NYT Letterboxed puzzle.

    Uses a recursive depth-first search to find solutions that:
    - Use all required letters from the puzzle
    - Follow puzzle rules for letter placement
    - Use the minimum number of letters possible
    - Use no more than max_words words

    Solutions are written to results.txt and printed to console.

    Args:
        sides (list[str]): List of strings representing letters on each side of puzzle
        valid_words (list[str]): List of valid words that can be used in the puzzle
        words_by_start (dict[str, list[str]]): Dictionary mapping starting letters to lists of valid words
        max_words (int, optional): Maximum number of words allowed in solution. Defaults to 2.

    Returns:
        set[str]: The last solution found, as a set of words
    """
    letter_set = set("".join(sides))

    target_length = 12
    best_length = float("inf")
    solution_found = False
    last_solution = None

    def recursive_solve(
        current_words: list[str], remaining_letters: set[str], depth: int = 0
    ) -> None:
        """Recursively search for valid solutions using depth-first search.

        Args:
            current_words: List of words in the current partial solution
            remaining_letters: Set of letters that still need to be used
            depth: Current recursion depth (number of words used so far)
        """
        nonlocal solution_found, best_length, last_solution

        # Stop if we found optimal solution or exceeded max words
        if solution_found or depth >= max_words:
            return

        current_length = calculate_solution_length(current_words)

        # Stop if current solution is longer than best found
        if current_length > best_length:
            return

        # Get valid candidate words that could be added next
        candidates = get_candidate_words(
            current_words,
            words_by_start,
            valid_words,
            remaining_letters,
            best_length,
            current_length,
        )

        # Try each candidate word
        for word in candidates:
            # Calculate remaining unused letters after adding this word
            new_remaining = remaining_letters - set(word)

            # Check if we found a complete solution using all letters
            if not new_remaining:
                solution_words = current_words + [word]
                solution_length = calculate_solution_length(solution_words)

                # If this is a better solution than previous best
                if solution_length < best_length:
                    best_length = solution_length
                    last_solution = set(solution_words)
                    solution = (
                        f"{' -> '.join(solution_words)} ({solution_length} letters)"
                    )
                    print(solution)

                    # Stop if we found optimal length solution
                    if solution_length == target_length:
                        solution_found = True
                    return

            # Recursively try adding more words to current partial solution
            recursive_solve(current_words + [word], new_remaining, depth + 1)

    # Start recursive search with empty solution
    recursive_solve([], letter_set)
    return last_solution


def daily_check(sides: list[str], valid_words: list[str], words_by_start: dict[str, list[str]], nyt_solution: set[str]):
    one_word = solve_letterboxed(sides, valid_words, words_by_start, 1)
    one_word_match = False
    found_one_word = "❌"
    if one_word:
        found_one_word = "✅"
        if one_word == nyt_solution:
            one_word_match = True

    two_word = solve_letterboxed(sides, valid_words, words_by_start, 2)
    two_word_match = False
    found_two_word = "❌"
    if two_word:
        found_two_word = "✅"
        if two_word == nyt_solution:
            two_word_match = True

    nyt_match = "❌"
    if one_word_match or two_word_match:
        nyt_match = "✅"
    
    five_word = solve_letterboxed(sides, valid_words, words_by_start, 5)
    twelve_letter_solution = "❌"
    if five_word:
        five_word_length = calculate_solution_length(five_word)
        if five_word_length == 12:
            twelve_letter_solution = "✅"
    
    print(f"{datetime.now().strftime('%Y-%m-%d')}|{found_one_word}|{found_two_word}|{twelve_letter_solution}|{nyt_match}")



def main():
    parser = argparse.ArgumentParser(description="Solve NYT Letter Boxed puzzle")
    parser.add_argument("--dict", type=str, help="Path to dictionary file")
    parser.add_argument(
        "--sides",
        type=str,
        nargs=4,
        help="Four sides of the puzzle, each as a string of 3 letters",
    )
    parser.add_argument(
        "--max-words", type=int, default=2, help="Maximum number of words in solution"
    )
    parser.add_argument(
        "--daily-check",
        action="store_true",
    )
    args = parser.parse_args()

    if args.sides and not args.dict:
        print("WARNING: --sides provided, but not --dict. Using today's NYT dictionary, which may not match sides provided.")

    if not args.sides or not args.dict:
        nyt_text = get_nyt_response_text()

    if not args.sides:
        args.sides = get_nyt_sides(nyt_text)
    args.sides = [side.upper().strip() for side in args.sides]

    word_list = None
    if args.dict:
        word_list = dict_file_to_word_list(args.dict)
        valid_words, words_by_start = prepare_valid_words(word_list, args.sides)
    else:
        word_list = get_nyt_word_list(nyt_text)
        valid_words, words_by_start = prepare_valid_words(word_list, args.sides, True)

    # Validate sides input
    if not all(len(side) == 3 for side in args.sides):
        parser.error("Each side must contain exactly 3 letters")

    if args.daily_check:
        nyt_solution = get_nyt_solution(nyt_text)
        daily_check(args.sides, valid_words, words_by_start, nyt_solution)
    else:
        solve_letterboxed(args.sides, valid_words, words_by_start, args.max_words)


if __name__ == "__main__":
    main()
