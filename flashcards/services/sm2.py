from datetime  import timedelta
from django.utils import timezone

def sm2(review :"FlashCardReview", quality: int):
    """
    SM2, quelity should be between 0 and 5
    """

    #safe valid range
    quality = max(0,min(5, quality))

    review.total_review += 1

    if quality >= 3:
        review.correct_reviews  += 1

    """
    if the answer was bad
    """

    if quality < 3:
        review.repetitions = 0 
        review.interval = 1
        review.next_review_date = timezone.now() + timedelta(days=1)
        review.last_reviewed_at = timezone.now()
        review.save()

    """
    if the answer was good
    """
    if review.repetitions == 0:
        review.interval = 1
    elif review.repetitions == 1:
        review.interval = 6
    else:
        review.interval = int(review.interval * review.ef)


    """
    update ef
    """

    review.ef = review.ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if review.ef <1.3:
        review.ef = 1.3


    review.repetitions += 1
    
    """
new date for practice
    """
    review.next_review_date = timezone.now() + timedelta(days=review.interval)
    review.last_reviewed_at = timezone.now()

    review.save()
    return review


