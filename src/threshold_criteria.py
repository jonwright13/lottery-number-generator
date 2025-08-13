from collections import Counter
import numpy as np

from src.utils import generate_pattern_probabilities


class Threshold_Criteria:
    def __init__(self, lottery_numbers, debug=False):
        self.max_pattern_probs = self.get_max_pattern_probabilities(
            lottery_numbers, debug=debug
        )
        _, self.ODD_RANGE = self.analyze_odd_even_distribution(
            lottery_numbers, debug=debug
        )
        self.SUM_MIN, self.SUM_MAX = self.analyze_sum_range(
            lottery_numbers,
            main_count=5,
            lower_percentile=15,
            upper_percentile=85,
            debug=debug,
        )
        self.MAX_MAIN_GAP_THRESHOLD, self.MAX_LUCKY_GAP_THRESHOLD = (
            self.determine_gap_thresholds(lottery_numbers, percentile=95)
        )
        self.MAX_MULTIPLES_ALLOWED = self.generate_max_multiples_allowed(
            lottery_numbers, main_only=True, debug=debug
        )

    def get_max_pattern_probabilities(self, lottery_numbers, debug=True):
        num_positions = len(lottery_numbers[0])
        position_counters = [
            Counter(draw[pos] for draw in lottery_numbers)
            for pos in range(num_positions)
        ]
        total_draws = len(lottery_numbers)
        nums = self.get_top_numbers_historical(lottery_numbers)

        probs = []
        for index, num_str in enumerate(nums):
            count = position_counters[index].get(num_str, 0)
            prob = (count / total_draws) * 100 if total_draws > 0 else 0
            probs.append(prob)

        pattern_prob = generate_pattern_probabilities(probs)

        if debug:
            print("\nMax Pattern Probabilities Possible")
            for k, v in pattern_prob.items():
                print(f"{k:<30}: {v:.2f}%")

        return pattern_prob

    def get_top_numbers_historical(self, lottery_numbers):
        top_numbers = []
        for index in range(len(lottery_numbers[0])):
            counter = Counter([x[index] for x in lottery_numbers])
            most_common_key = counter.most_common(1)[0][0]
            top_numbers.append(most_common_key)

        return tuple(top_numbers)

    def analyze_odd_even_distribution(
        self, lottery_numbers, main_only=True, debug=False
    ):
        """
        Analyze the distribution of odd and even numbers in lottery draws.
        Args:
        lottery_numbers: list of tuples/lists of numbers as strings or ints.
        main_only: If True, analyze only the main numbers (first 5).
        Returns:
        distribution dict mapping number_of_odd_numbers -> count_of_draws,
        and a tuple (low_threshold, high_threshold) of min and max odd counts observed.
        """

        distribution = {}

        length_to_check = 5 if main_only else len(lottery_numbers[0])

        for draw in lottery_numbers:
            # Convert to int if needed
            numbers = [int(n) for n in draw[:length_to_check]]
            odd_count = sum(1 for num in numbers if num % 2 == 1)
            distribution[odd_count] = distribution.get(odd_count, 0) + 1

        total_draws = len(lottery_numbers)

        if debug:
            print(
                f"Total draws analyzed: {total_draws}\nOdd/Even distribution (odd numbers count in main numbers):"
            )
            for odd_count in range(length_to_check + 1):
                count = distribution.get(odd_count, 0)
                pct = (count / total_draws) * 100 if total_draws else 0
                even_count = length_to_check - odd_count
                print(
                    f"  {odd_count} odd / {even_count} even : {count} draws ({pct:.2f}%)"
                )

        odd_counts_with_data = sorted([k for k, v in distribution.items() if v > 0])
        low_threshold = odd_counts_with_data[0] if odd_counts_with_data else None
        high_threshold = odd_counts_with_data[-1] if odd_counts_with_data else None

        return distribution, (low_threshold, high_threshold)

    def analyze_sum_range(
        self,
        lottery_numbers,
        main_count=5,
        lower_percentile=15,
        upper_percentile=85,
        debug=False,
    ):
        """
        Analyze the sum distribution of main numbers from your historical lottery data.
        Returns the sum range between lower_percentile and upper_percentile,
        and prints descriptive statistics.
        """
        sums = []
        for draw in lottery_numbers:
            main_nums = [int(n) for n in draw[:main_count]]
            sums.append(sum(main_nums))

        sums_array = np.array(sums)

        min_sum = sums_array.min()
        max_sum = sums_array.max()
        mean_sum = sums_array.mean()
        median_sum = np.median(sums_array)
        low_pct = np.percentile(sums_array, lower_percentile)
        high_pct = np.percentile(sums_array, upper_percentile)

        if debug:
            print(f"\nTotal draws analyzed: {len(sums)}")
            print(f"Sum range: min={min_sum}, max={max_sum}")
            print(f"Mean sum: {mean_sum:.2f}, Median sum: {median_sum}")
            print(f"{lower_percentile}th percentile sum: {low_pct}")
            print(f"{upper_percentile}th percentile sum: {high_pct}")
            print(
                f"Typical sum range (between {lower_percentile}th and {upper_percentile}th percentiles): {low_pct} - {high_pct}"
            )

        return int(low_pct), int(high_pct)

    def determine_gap_thresholds(
        self, lottery_numbers, count_main=5, count_lucky=2, percentile=95
    ):
        """
        Analyze historical gaps and return max gap thresholds for main and lucky numbers based on percentile.

        Args:
            lottery_numbers: historical lottery draws (list of tuples/lists).
            count_main: number of main numbers.
            count_lucky: number of lucky numbers.
            percentile: the percentile to select gap threshold (default 95).

        Returns:
            (max_main_gap_threshold, max_lucky_gap_threshold)
        """
        # Get the gap distribution data
        gap_data = self.analyze_gap_distribution(
            lottery_numbers, count_main, count_lucky
        )

        # Helper to expand gap counts into sorted list of all gaps observed
        def expand_gaps(counters):
            gaps_list = []
            for counter in counters:
                for gap_size, count in counter.items():
                    gaps_list.extend([gap_size] * count)
            return gaps_list

        main_gaps = (
            expand_gaps(gap_data["main"]["gap_counters"])
            if gap_data["main"]["gap_counters"]
            else []
        )
        lucky_gaps = (
            expand_gaps(gap_data["lucky"]["gap_counters"])
            if gap_data["lucky"]["gap_counters"]
            else []
        )

        # If no data, fallback to defaults
        if not main_gaps:
            max_main_gap = 19
        else:
            max_main_gap = int(np.percentile(main_gaps, percentile))

        if not lucky_gaps:
            max_lucky_gap = 5
        else:
            max_lucky_gap = int(np.percentile(lucky_gaps, percentile))

        return max_main_gap, max_lucky_gap

    def analyze_gap_distribution(self, lottery_numbers, count_main=5, count_lucky=2):
        """
        Analyze gaps (differences) between consecutive numbers for main and lucky numbers across historical draws.
        Return gap counters for main and lucky numbers.

        Args:
            lottery_numbers: List of tuples/lists where each draw has main numbers + lucky numbers.
            count_main: Number of main numbers to consider (default 5).
            count_lucky: Number of lucky numbers to consider (default 2).

        Returns:
            dict with structure:
            {
                'main': {
                    'gap_counters': [Counter(), Counter(), ..., Counter()]  # One per gap position
                },
                'lucky': {
                    'gap_counters': [Counter(), ...]  # Similar for lucky numbers
                }
            }
        """

        main_gap_counters = [Counter() for _ in range(count_main - 1)]
        lucky_gap_counters = (
            [Counter() for _ in range(count_lucky - 1)] if count_lucky > 1 else []
        )

        for draw in lottery_numbers:
            # Assume draw is like (M1, M2, M3, M4, M5, L1, L2) all zero-padded strings
            main_nums = sorted(int(n) for n in draw[:count_main])
            lucky_nums = sorted(
                int(n) for n in draw[count_main : count_main + count_lucky]
            )

            # Calculate gaps for main numbers
            for i in range(len(main_nums) - 1):
                gap = main_nums[i + 1] - main_nums[i]
                main_gap_counters[i][gap] += 1

            # Calculate gaps for lucky numbers if applicable
            for i in range(len(lucky_nums) - 1):
                gap = lucky_nums[i + 1] - lucky_nums[i]
                lucky_gap_counters[i][gap] += 1

        return {
            "main": {"gap_counters": main_gap_counters},
            "lucky": {"gap_counters": lucky_gap_counters},
        }

    def generate_max_multiples_allowed(
        self, lottery_numbers, bases=range(2, 11), main_only=True, debug=False
    ):
        """
        Generate a dictionary of max multiples allowed per base by analyzing historical lottery numbers.
        Uses the 95th percentile of multiples counts as threshold.

        Args:
            lottery_numbers: list of historical draw tuples
            bases: iterable of bases to analyze, default 2 through 10
            main_only: consider only the first 5 numbers if True

        Returns:
            dict mapping base -> max multiples allowed (int)
        """
        max_multiples_dict = {}

        for base in bases:
            _, _, max_allowed = self.analyze_multiples_distribution(
                lottery_numbers, base=base, main_only=main_only, debug=debug
            )
            max_multiples_dict[base] = max_allowed

        if debug:
            print("\nFinal max_multiples_allowed dict:")
            for base, max_count in max_multiples_dict.items():
                print(f"  {base}: {max_count}")

        return max_multiples_dict

    def analyze_multiples_distribution(
        self, lottery_numbers, base=3, main_only=True, debug=False
    ):
        """
        Analyze how many numbers in each draw are multiples of 'base'.
        Args:
            lottery_numbers: list of tuples/lists of numbers (strings or ints)
            base: integer base to check multiples for (e.g., 3)
            main_only: if True, consider only main numbers (first 5), else all numbers (7)
        Returns:
            distribution: dict mapping number_of_multiples -> count_of_draws
            example_draws: list of draws with 3 or more multiples (for illustration)
            max_allowed: suggested max multiples allowed for this base (e.g., 95th percentile)
        """
        distribution = {}
        example_draws = []

        length_to_check = 5 if main_only else len(lottery_numbers[0])

        multiples_counts = []  # For percentile calculation

        for draw in lottery_numbers:
            numbers = [int(n) for n in draw[:length_to_check]]

            count_multiples = sum(1 for num in numbers if num % base == 0)
            multiples_counts.append(count_multiples)

            distribution[count_multiples] = distribution.get(count_multiples, 0) + 1

            if count_multiples >= 3:
                example_draws.append(draw)

        total_draws = len(lottery_numbers)

        if debug:
            print(
                f"\nAnalyzing multiples of {base} in {'main numbers only' if main_only else 'all numbers'}:\n"
            )

        for count in sorted(distribution.keys()):
            pct = (distribution[count] / total_draws) * 100
            if debug:
                print(
                    f"  Draws with exactly {count} multiples of {base}: {distribution[count]} "
                    f"({pct:.2f}%) of all draws"
                )

        # Suggest max allowed using 95th percentile (you can adjust this)
        max_allowed = int(np.percentile(multiples_counts, 95))

        if debug:
            print(
                f"\nSuggested max multiples allowed for base {base} (95th percentile): {max_allowed}\n"
            )

        return distribution, example_draws, max_allowed
