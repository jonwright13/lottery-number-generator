# Lottery Number Generator

## Overview

This project is a **Lottery Number Generator** designed to create lottery number combinations based on historical data and statistical heuristics. Unlike purely random generators, it filters candidate sets using multiple criteria derived from past draws, such as odd/even distribution, sum ranges, gap thresholds, multiples restrictions, clustering, and pattern probabilities.

The generator aims to find valid lottery number combinations that have a higher historical likelihood, improving the quality of generated numbers according to historical positional frequency and various constraints.

## Features

- Downloads and parses the latest lottery draw results automatically.
- Analyzes historical draws for statistical patterns including:
  - Odd/even number distributions
  - Sum range percentiles
  - Number gap thresholds (max gaps between numbers)
  - Maximum multiples allowed per base (2 through 10)
  - Clustering of numbers in predefined intervals
- Generates unique number sets meeting all heuristic filters:
  - No duplicates with historical draws
  - Balanced odd/even counts
  - Restricted maximum consecutive runs and number gaps
  - Valid sum-of-numbers within typical historical range
  - Pattern probability based on positional frequencies
- Uses efficient rejection and scoring strategies to find high-probability combinations.
- Highly customizable filtering thresholds and parameters.
- Includes debug information and detailed iteration rejection statistics.
- Supports progress tracking through integration with the `tqdm` progress bar.

## Usage

### Requirements

- Python 3.7 or higher
- Required packages:
  - `requests`
  - `beautifulsoup4`
  - `pandas`
  - `numpy`
  - `tqdm`
  - `numpy`

Install dependencies via:
```pip install -r requirements.txt```

### Running the Generator

In a termainl, run

```python main.py```

Use `debug=True` for detailed iteration filtering logs and statistics.

### Progress Tracking

The generator integrates `tqdm` to provide a progress bar during generation attempts.

## Customization

All filtering parameters, thresholds, and constraints can be easily adjusted via function arguments in `generate_valid_number_set` to tailor complexity and strictness.

## Limitations

- The generator approximates "better" picks based on past draws statistics but **cannot guarantee winnings**.
- Lottery results are inherently random, and odds remain as per official lottery rules.
- This tool is for study, exploration, and entertainment of lottery patterns.

## Contributing

Contributions, improvements, and suggestions are welcome via pull requests or issues.

## License

Specify your license here (e.g., MIT License).
