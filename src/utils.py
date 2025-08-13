import requests, random
from bs4 import BeautifulSoup
from io import StringIO
import pandas as pd


def get_latest_lottery_numbers():
    """
    Download and parse the latest lottery numbers as a list of zero-padded string tuples.
    Each tuple has 7 elements: 5 main numbers + 2 lucky stars, all zero-padded strings.
    """
    url = "https://lottery.merseyworld.com/cgi-bin/lottery?days=20&Machine=Z&Ballset=0&order=1&show=1&year=0&display=CSV"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    pre_tag = soup.find("pre")

    if not pre_tag:
        raise RuntimeError("Could not find lottery data on the page.")

    csv_text = pre_tag.get_text()
    df = pd.read_csv(StringIO(csv_text), header=1)
    df = df.iloc[:-2]  # Remove footer rows
    df.columns = df.columns.str.strip()

    lottery_numbers = []
    for _, row in df.iterrows():
        try:
            numbers_tuple = tuple(
                str(int(row[col])).zfill(2)
                for col in ["N1", "N2", "N3", "N4", "N5", "L1", "L2"]
            )
            lottery_numbers.append(numbers_tuple)
        except ValueError:
            # Skip rows that don't convert cleanly (e.g., header rows)
            continue

    print("Retrieved latest lottery numbers")
    return lottery_numbers


def generate_random_number(min_value, max_value):
    return random.randint(min_value, max_value)


def generate_unique_numbers(
    count, min_value, max_value, existing_combinations=None, max_attempts=1000
):
    """
    Generate 'count' unique random integers between min_value and max_value inclusive,
    avoiding those in existing_combinations (set of tuples).
    """
    attempts = 0
    while attempts < max_attempts:
        numbers = set()
        while len(numbers) < count:
            num = random.randint(min_value, max_value)
            numbers.add(num)
        numbers_tuple = tuple(sorted(numbers))

        if existing_combinations is None or numbers_tuple not in existing_combinations:
            return sorted(numbers)

        attempts += 1

    raise RuntimeError("Could not generate a unique number set after max attempts")


def count_max_consecutive_run(numbers):
    """Return the length of the longest consecutive run in the sorted list."""
    if not numbers:
        return 0
    max_run = 1
    current_run = 1
    for i in range(1, len(numbers)):
        if numbers[i] == numbers[i - 1] + 1:
            current_run += 1
            max_run = max(max_run, current_run)
        else:
            current_run = 1
    return max_run


def count_clusters_main_numbers(main_nums, max_value=50, group_size=10):
    """
    Count how many main numbers fall into each cluster.
    main_nums: list or iterable of main number ints (e.g., [3, 22, 45, ...])
    max_value: maximum number value (default 50)
    group_size: size of each cluster (default 10)
    Returns a dict mapping cluster index to count.
    """
    group_counts = {}
    num_groups = (max_value + group_size - 1) // group_size  # e.g. 50/10=5 groups

    # Initialize counts
    for i in range(num_groups):
        group_counts[i] = 0

    for num in main_nums:
        group_index = (num - 1) // group_size
        group_counts[group_index] += 1

    return group_counts


def count_multiples(numbers, base):
    """Count how many numbers in 'numbers' are multiples of 'base'."""
    return sum(1 for num in numbers if num % base == 0)


def max_gap_exceeds_threshold(main_nums, max_gap_allowed=15):
    """
    Returns True if any consecutive gap in sorted main_nums exceeds max_gap_allowed.
    Otherwise, returns False.
    """
    for i in range(len(main_nums) - 1):
        gap = main_nums[i + 1] - main_nums[i]
        if gap > max_gap_allowed:
            return True
    return False


def is_sum_in_range(main_nums, min_sum, max_sum):
    total = sum(main_nums)
    return min_sum <= total <= max_sum


PATTERNS = [
    (5, 2, None),  # 5 main + 2 specials; None means default last 2 numbers
    (5, 1, 1),  # 5 main + first special number
    (5, 1, 2),  # 5 main + second special number
    (5, 0, None),  # 5 main + no specials
    (4, 2, None),  # 4 main + 2 specials
    (4, 1, 1),  # 4 main + first special number
    (4, 1, 2),  # 4 main + second special number
    (3, 2, None),  # 3 main + 2 lucky stars
    (4, 0, None),  # 4 main + no lucky stars
    (2, 2, None),  # 2 main + 2 lucky stars
    (3, 1, 1),  # 3 main + first lucky star
    (3, 1, 2),  # 3 main + second lucky star
]


def generate_pattern_probabilities(probs):
    pattern_prob = {}
    for pattern in PATTERNS:
        count_main, count_lucky, special = pattern

        # Calculate the slice length: main numbers + lucky numbers (or just main if count_lucky=0)
        if count_lucky == 0:
            slice_end = count_main  # Only main numbers slice
        else:
            slice_end = count_main + count_lucky  # main + lucky slice

        # Extract the relevant probability slice from probs
        # probs is aligned with combined_tuple: main numbers first, then lucky numbers
        pattern_probs_slice = probs[:slice_end]

        # Calculate average score for this pattern slice
        if len(pattern_probs_slice) > 0:
            avg_score = sum(pattern_probs_slice) / len(pattern_probs_slice)
        else:
            avg_score = 0  # Defensive: pattern with zero length

        # Create a descriptive key for the pattern for readability
        key = f"{count_main}_main+{count_lucky}_lucky"
        if special is not None and count_lucky == 1:
            key += f"_special_{special}"

        pattern_prob[key] = avg_score

    return pattern_prob
