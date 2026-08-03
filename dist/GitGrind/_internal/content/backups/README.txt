Automatic pre-write backups of question-bank files.

Before an import modifies content/questions/*.json, the original is copied
here with a timestamp. The 20 most recent are kept.

To undo a bad import, copy the relevant .bak back over the original and
press "Reload from disk" in the Bank tab.
