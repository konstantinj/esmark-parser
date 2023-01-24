# ESMARK parser

### Tool to compare houses on esmark.de

Uses selenium and beautiful soup to parse the esmark page and write results to csv.

### How to use

The parser runs on `python3` and needs some libs:

```shell
pip install -r requirements.txt
```

Pick houses you like and put links to a txt file. One link per line.
Then run parser like this:

```shell
python3 esmark-parser.py --year=23 --week=16 --separator="," < urls.txt >> urls.csv
```

### TODO

- use html page instead if csv
- add a search to actually find houses
- add other pages like novasol and dansk
- make it a platform