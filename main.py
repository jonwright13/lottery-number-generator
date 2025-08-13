from src.generate import generate_valid_number_set, iteration_check_dict
from src.threshold_criteria import Threshold_Criteria
from src.utils import (
    get_latest_lottery_numbers,
)


def run():
    lottery_numbers = get_latest_lottery_numbers()

    threshold_criteria = Threshold_Criteria(lottery_numbers, debug=False)

    print("\nObtaining threshold criteria from lottery numbers")
    ODD_RANGE = threshold_criteria.ODD_RANGE
    SUM_MIN = threshold_criteria.SUM_MIN
    SUM_MAX = threshold_criteria.SUM_MAX
    MAX_MAIN_GAP_THRESHOLD = threshold_criteria.MAX_MAIN_GAP_THRESHOLD
    MAX_LUCKY_GAP_THRESHOLD = threshold_criteria.MAX_LUCKY_GAP_THRESHOLD
    MAX_MULTIPLES_ALLOWED = threshold_criteria.MAX_MULTIPLES_ALLOWED

    best_combination, best_score, pattern_prob = generate_valid_number_set(
        lottery_numbers,
        min_score=10,
        max_iterations=100000000,
        SUM_MIN=SUM_MIN,
        SUM_MAX=SUM_MAX,
        MAX_MAIN_GAP_THRESHOLD=MAX_MAIN_GAP_THRESHOLD,
        MAX_LUCKY_GAP_THRESHOLD=MAX_LUCKY_GAP_THRESHOLD,
        MAX_MULTIPLES_ALLOWED=MAX_MULTIPLES_ALLOWED,
        ODD_RANGE=ODD_RANGE,
        PATTERN_PROB_THRESHOLD=8,
        debug=False,
    )

    print(f"\nCombination: {best_combination}")
    print(f"Probability Score: {best_score:.2f}%")

    print("\nIteration Check")
    for k, v in iteration_check_dict.items():
        print(f"{k:<30}: {v}")

    print("\nPattern Probabilities")
    for k, v in pattern_prob.items():
        print(f"{k:<30}: {v:.2f}%")


if __name__ == "__main__":
    run()
