from datetime import timedelta
from django.utils import timezone

def sm2(review, quality: int):
    """
    SM-2 spaced repetition algorithm
    
    Args:
        review: FlashcardReview instance
        quality: Integer 0-5 where:
            0: Complete blackout
            1: Incorrect response (but remembered)
            2: Correct with difficulty
            3: Correct after hesitation
            4: Correct with moderate effort
            5: Perfect recall
    
    Returns:
        Updated FlashcardReview instance
    
    Raises:
        ValueError: If quality is not 0-5
    """
    # Validate quality parameter
    if not isinstance(quality, int):
        raise ValueError("Quality must be an integer")
    
    if not 0 <= quality <= 5:
        raise ValueError("Quality must be between 0 and 5")
    
    # Store original values for debugging if needed
    original_ef = review.ef
    original_interval = review.interval
    original_repetitions = review.repetitions
    
    # Increment total reviews counter
    review.total_reviews += 1
    
    # Increment correct reviews if quality >= 3
    if quality >= 3:
        review.correct_reviews += 1
    
    # Handle incorrect answers (quality < 3)
    if quality < 3:
        # Reset progress for incorrect answers
        review.repetitions = 0
        review.interval = 1
        # Next review in 1 day
        review.next_review_date = timezone.now() + timedelta(days=1)
    
    # Handle correct answers (quality >= 3)
    else:
        # Determine new interval based on repetitions
        if review.repetitions == 0:
            # First correct answer: 1 day interval
            review.interval = 1
        elif review.repetitions == 1:
            # Second correct answer: 6 days interval
            review.interval = 6
        else:
            # Subsequent correct answers: interval * EF
            review.interval = int(review.interval * review.ef)
        
        # Increment repetition counter for correct answers
        review.repetitions += 1
    
    # Update ease factor (EF) using SM-2 formula
    # EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    ef_change = (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    review.ef = review.ef + ef_change
    
    # Minimum ease factor is 1.3
    if review.ef < 1.3:
        review.ef = 1.3
    
    # Set next review date based on new interval
    # (This overrides the 1-day interval set for incorrect answers)
    review.next_review_date = timezone.now() + timedelta(days=review.interval)
    
    # Update last reviewed timestamp
    review.last_reviewed_at = timezone.now()
    
    # Save changes to database
    review.save()
    
    
    print(f"SM-2 Update: "
          f"Quality={quality}, "
          f"EF: {original_ef:.2f}→{review.ef:.2f}, "
          f"Interval: {original_interval}→{review.interval}, "
          f"Reps: {original_repetitions}→{review.repetitions}")
    
    return review