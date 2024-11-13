# NYT Letter Boxed Puzzle Solver
This Python script solves arbitrary New York Times Letter Boxed puzzles. As opposed to optimizing for the game's scoring system of finding solutions with the fewest total words, this script finds a solution that uses the minimum number of total letters. Under this scoring system, a 12-letter solution is optimal, regardless of the number of words.

## Notes
- Some puzzles can be solved with only 12 letters (using each letter exactly once), however, this is only possible using 5 words or fewer. Why 5? Because:
  - The last letter of the previous word is automatically used as the first letter of the next word and is not double counted.
  - Each word uses a minimum of 3 letters (including the first letter).
  - Therefore, the minimum number of letters for a given number of words is 2n + 1. A solution with 6 words would therefore require a minimum of 13 letters and could never return a 12-letter solution.
- The script outputs its current best solution as it searches for the optimal solution.
- This is not intended to provide a comprehensive list of solutions, but rather to settle on a single solution that uses the minimum number of total letters. In practice, there may be other optimal solutions.
- While highly unlikely, it is theoretically possible that an optimal solution would contain a word that does not introduce any new letters. To reduce the search space, this script skips those words and therefore could miss an optimal solution.

## Usage
Run the script from the command line with the following arguments:
```
python ltrbxd.py --dict path/to/dictionary.txt --sides abc def ghi jkl --max-words 2
```
- If `--sides` is omitted, the script will automatically fetch the current day's sides from the NYT website.
- If `--dict` is omitted, the script will automatically fetch today's dictionary from the NYT website, but please note that this dictionary contains only valid words for the current day's sides, so it will not work for other puzzles. The game reportedly uses the official Oxford English Dictionary, which is not freely available, so you must provide your own dictionary file when solving anything other than today's puzzle. While the script allows you to specify `--sides` without `--dict`, the script will likely ultimately fail in this case because the dictionary of valid words will not match the sides provided.
- If `--max-words` is omitted, the script will default to a maximum of 2 words for solutions, as many puzzles can be solved with only 2 words and this would be an excellent solution using the NYT scoring method. In theory, there could be a one-word solution, so you could choose to set this to 1 to check. To check if there are any 12-letter solutions, you would need to set this to at least 5 (see Notes section above).