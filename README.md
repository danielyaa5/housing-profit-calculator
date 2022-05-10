# Goal
Calculate the growth of a home investment vs an index fund

# Requirements
- https://github.com/pyenv/pyenv
- https://github.com/pyenv/pyenv-virtualenv

# Installation
```
pyenv virtualenv <name>
pyenv activate <name>
pip install -r requirements.txt
```

# Example Usage
```
python main.py -i scenarios/house.yaml
open output/house.csv
```

# Notes
- The tax benefit calculation logic was only built to work for CA. Any PRs to help introduce other states are welcome.
