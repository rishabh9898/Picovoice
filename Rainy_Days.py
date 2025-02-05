from typing import Sequence

def prob_rain_at_least_n(p: Sequence[float], n: int) -> float:
    """
    Returns the probability that it rains on at least n days
    in a 365-day period, where p[i] is the probability of rain
    on day i (0 <= i < 365).
    """
    # Number of days (assumed 365 in the problem statement)
    days = len(p)
    
    # dp[k] will store the probability that exactly k days have been rainy
    # after we process a certain number of days.
    # We allocate days+1 slots because k can range from 0 up to 'days'.
    dp = [0.0] * (days + 1)
    
    # Initially, before we process any days, the probability of exactly 0 rainy days is 1.0
    dp[0] = 1.0

    # We iterate through each day
    for i in range(days):
        # We update dp[k] in reverse order (from k = i+1 down to k = 1)
        # This ensures that we don't overwrite the dp values we still need
        # from the previous iteration.
        for k in range(i+1, 0, -1):
            # dp[k] can be formed in two ways:
            # 1) It was already k rainy days before this day (dp[k]), and it does not rain today (1 - p[i]).
            # 2) It was k-1 rainy days before this day (dp[k-1]), and it rains today (p[i]).
            dp[k] = dp[k] * (1 - p[i]) + dp[k-1] * p[i]

        # For k=0, the only way to stay at 0 rainy days is if it doesn't rain on this day.
        dp[0] = dp[0] * (1 - p[i])
    
    # Finally, we sum up the probabilities of having >= n rainy days.
    # dp[k] is the probability of having exactly k rainy days, so we sum dp[n], dp[n+1], ..., dp[days].
    return sum(dp[n:])
