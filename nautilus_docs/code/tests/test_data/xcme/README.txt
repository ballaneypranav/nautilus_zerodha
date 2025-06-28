TITLE: Reading Gzipped CSV Data with Pandas in Python
DESCRIPTION: This snippet demonstrates how to directly read a gzipped CSV file into a pandas DataFrame. It specifies the file path, sets the header row, and disables the index column creation, leveraging pandas' ability to handle compressed files efficiently.
SOURCE: tests/test_data/xcme/README.md
LANGUAGE: python
KEYWORDS: CSV,data format,data:loading,gzip,library:pandas
CODE:
```
import pandas as pd

df = pd.read_csv(
    "6EH4.XCME_1min_bars_20240101_20240131.csv.gz",  # update path as needed
    header=0,
    index_col=False,
)
```