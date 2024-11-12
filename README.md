# NYT Letter Boxed Puzzle Solver
This Python script solves arbitrary New York Times Letter Boxed puzzles. As opposed to optimizing for the game's scoring system of finding solutions with the fewest total words, this script finds a solution that uses the minimum number of total letters.

## Notes
- The game uses the official Oxford English Dictionary, which is not freely available, so you must provide your own dictionary file. This script was tested using a list of English words obtained from https://github.com/dwyl/english-words.
- The script outputs its current best solution as it searches for the optimal solution.
- This is not intended to provide a comprehensive list of solutions, but rather a single solution that uses the minimum number of total letters.
- While unlikely, it is theoretically possible that an optimal solution would contain a word that does not introduce any new letters. To reduce the search space, this script skips those words and therefore could miss an optimal solution.
- Many Letter Boxed games can be solved using only 2 words, so the default maximum number of words is 2. You can override this by specifying a different number with the `--max-words` flag.

## Usage

Run the script from the command line with the following arguments:
```
python ltrbxd.py --dict path/to/dictionary.txt --sides abc def ghi jkl --max-words 2
```
