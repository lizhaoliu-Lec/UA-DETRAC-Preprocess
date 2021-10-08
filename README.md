# UA-DETRAC-Preprocess
A preprocess tool for converting UA-Detrac detection dataset into coco format

## File structure
```
--- main.py # the main script for converting ua-detrac detection dataset into coco format
--- change4to1.py # the script for changing the 4 vehicel class into 1 class
```

## Usage
```
# 1. modify the related pathes in the main() fuction in main.py
# 2. python -u main.py

# additionally, if you want to change 4 classes into 1 class
# 3. modify the related pathes in the _4to1() fuction in change4to1.py
# python -u change4to1.py
```