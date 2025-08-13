from collections import Counter
from tqdm import trange

from src.utils import (
    generate_unique_numbers,
    count_multiples,
    max_gap_exceeds_threshold,
    is_sum_in_range,
    count_max_consecutive_run,
    count_clusters_main_numbers,
    generate_pattern_probabilities,
)

iteration_check_dict = {
    "generation_duplicate": 0,
    "exceed_multiples": 0,
    "max_run": 0,
    "cluster_count": 0,
    "odd_even_balance": 0,
    "gap_exceeds_threshold": 0,
    "sum_in_range": 0,
    "historical_duplicate": 0,
    "pattern_prob_threshold": 0,
}


def generate_valid_number_set(
    lottery_numbers,
    min_main=1,
    max_main=50,
    count_main=5,
    min_lucky=1,
    max_lucky=11,
    count_lucky=2,
    min_score=10,
    max_iterations=1000000,
    SUM_MIN=42,
    SUM_MAX=222,
    MAX_MAIN_GAP_THRESHOLD=19,
    MAX_LUCKY_GAP_THRESHOLD=4,
    ODD_RANGE=(1, 4),
    MAX_MULTIPLES_ALLOWED={2: 4, 3: 4, 4: 3, 5: 2, 6: 2, 7: 2, 8: 2, 9: 2, 10: 2},
    PATTERN_PROB_THRESHOLD=8,
    debug=False,
):
    """
    Generate a combination of main and lucky numbers that:
      - Does NOT exist in lottery_numbers
      - Has an average positional historical frequency score >= min_score %
    Retries up to max_iterations times, returns the best found if none matches criteria.
    """

    print(f"\nRunning Lottery Number Generator. Max Iterations: {max_iterations}")

    # Convert lottery_numbers to a set for O(1) lookups
    lottery_numbers_set = set(lottery_numbers)
    total_draws = len(lottery_numbers)
    num_positions = len(lottery_numbers[0])

    # Precompute frequency counters per position
    position_counters = [
        Counter(draw[pos] for draw in lottery_numbers) for pos in range(num_positions)
    ]

    tried_main_combinations = set()
    tried_lucky_combinations = set()
    tried_combined_combinations = set()

    best_score = 0
    best_combination = None
    best_pattern_prob = None

    for iteration in trange(1, max_iterations + 1, desc="Generating"):
        main_nums = generate_unique_numbers(
            count_main,
            min_main,
            max_main,
            existing_combinations=tried_main_combinations,
        )

        # Check multiples count per base in main numbers
        exceeds_multiples_limit = False
        for base, max_allowed in MAX_MULTIPLES_ALLOWED.items():
            if count_multiples(main_nums, base) > max_allowed:
                exceeds_multiples_limit = True
                iteration_check_dict["exceed_multiples"] += 1
                tried_main_combinations.add(tuple(main_nums))
                if debug:
                    print(
                        f"Iteration {iteration}: Too many multiples of {base} in main numbers. Regenerating..."
                    )
                break
        if exceeds_multiples_limit:
            continue

        # Check gap between number positions
        if max_gap_exceeds_threshold(main_nums, max_gap_allowed=MAX_MAIN_GAP_THRESHOLD):
            iteration_check_dict["gap_exceeds_threshold"] += 1
            tried_main_combinations.add(tuple(main_nums))
            if debug:
                print(
                    f"Iteration {iteration}: Gap exceeds max allowed {MAX_MAIN_GAP_THRESHOLD}. Regenerating..."
                )
            continue

        # Check sum range of main numbers
        if not is_sum_in_range(main_nums, SUM_MIN, SUM_MAX):
            iteration_check_dict["sum_in_range"] += 1
            tried_main_combinations.add(tuple(main_nums))
            if debug:
                print(
                    f"Iteration {iteration}: Sum {sum(main_nums)} outside range ({SUM_MIN}-{SUM_MAX}). Regenerating..."
                )
            continue

        # Check consecutive runs only on main_nums
        max_run = count_max_consecutive_run(main_nums)
        if max_run >= 3:
            # Reject this set because it has 3 or more consecutive numbers
            iteration_check_dict["max_run"] += 1
            tried_main_combinations.add(tuple(main_nums))
            if debug:
                print(
                    f"Iteration {iteration}: Main numbers have {max_run} consecutive numbers. Regenerating..."
                )
            continue

        # Odd/even balance check
        odd_count = sum(1 for num in main_nums if num % 2 == 1)
        if odd_count < ODD_RANGE[0] or odd_count > ODD_RANGE[1]:
            iteration_check_dict["odd_even_balance"] += 1
            tried_main_combinations.add(tuple(main_nums))
            if debug:
                print(
                    f"Iteration {iteration}: Odd count {odd_count} outside balanced range (2 or 3). Regenerating..."
                )
            continue

        # Check clustering on main_nums
        cluster_counts = count_clusters_main_numbers(main_nums)
        if any(count > 3 for count in cluster_counts.values()):
            iteration_check_dict["cluster_count"] += 1
            tried_main_combinations.add(tuple(main_nums))
            if debug:
                print(
                    f"Iteration {iteration}: Main numbers too clustered. Groups: {cluster_counts}. Regenerating..."
                )
            continue

        lucky_nums = generate_unique_numbers(
            count_lucky,
            min_lucky,
            max_lucky,
            existing_combinations=tried_lucky_combinations,
        )

        # Check gap between number positions
        if max_gap_exceeds_threshold(
            lucky_nums, max_gap_allowed=MAX_LUCKY_GAP_THRESHOLD
        ):
            iteration_check_dict["gap_exceeds_threshold"] += 1
            tried_lucky_combinations.add(tuple(lucky_nums))
            if debug:
                print(
                    f"Iteration {iteration}: lucky_nums Gap exceeds max allowed {MAX_LUCKY_GAP_THRESHOLD}. Regenerating..."
                )
            continue

        combined_nums = main_nums + lucky_nums
        combined_tuple = tuple(str(num).zfill(2) for num in combined_nums)

        if combined_tuple in tried_combined_combinations:
            iteration_check_dict["generation_duplicate"] += 1
            if debug:
                print(
                    f"Iteration {iteration}: Generation duplicate found. Regenerating..."
                )
                continue

        # Check if comnbination appears in historical numbers
        if combined_tuple in lottery_numbers_set:
            iteration_check_dict["historical_duplicate"] += 1
            tried_combined_combinations.add(combined_tuple)
            if debug:
                print(f"Iteration {iteration}: Combination exists. Retrying...")
            continue

        # Calculate propbability score based on historical draws
        probs = []
        for index, num_str in enumerate(combined_tuple):
            count = position_counters[index].get(num_str, 0)
            prob = (count / total_draws) * 100 if total_draws > 0 else 0
            probs.append(prob)

        pattern_prob = generate_pattern_probabilities(probs)

        if (
            pattern_prob["5_main+1_lucky_special_1"] < PATTERN_PROB_THRESHOLD
            or pattern_prob["5_main+1_lucky_special_2"] < PATTERN_PROB_THRESHOLD
        ):
            iteration_check_dict["pattern_prob_threshold"] += 1
            tried_combined_combinations.add(combined_tuple)
            if debug:
                print(f"Iteration {iteration}: pattern_prob_threshold hit. Retrying...")
            continue

        avg_score = sum(probs) / len(probs)

        if avg_score > best_score:
            best_score = avg_score
            best_combination = combined_tuple
            best_pattern_prob = pattern_prob

        if avg_score >= min_score:
            print(
                f"Iteration {iteration}: Valid combination found with score {avg_score:.2f}%"
            )
            return best_combination, best_score, best_pattern_prob

    print(f"Max iterations reached. Best score so far: {best_score:.2f}%")
    return best_combination, best_score, best_pattern_prob
