# Flashcards & Practice Sessions API Documentation

A comprehensive REST API for spaced repetition flashcards and interactive practice sessions with gamification features.

## Table of Contents

- [Authentication](#authentication)
- [Base URL](#base-url)
- [Features](#features)
- [Endpoints](#endpoints)
  - [Flashcards Management](#flashcards-management)
  - [Practice Sessions](#practice-sessions)
  - [Game Modes](#game-modes)
- [Models](#models)
- [Error Handling](#error-handling)

---

## Authentication

All endpoints require authentication using Django REST Framework's token authentication.

**Header Required:**
```
Authorization: Token <your-auth-token>
```

---

## Base URL

```
/api/flashcards/
```

---

## Features

- **Spaced Repetition (SM-2 Algorithm)** - Intelligent scheduling for optimal learning
- **Multiple Practice Modes** - Flashcards, Timed challenges, Matching games, Quizzes
- **Progress Tracking** - Detailed statistics and performance analytics
- **Gamification** - Points system and achievement tracking
- **Real-time Feedback** - Instant validation and scoring

---

## Endpoints

### Flashcards Management

#### List/Create Flashcards

Retrieve all flashcards or create a new one.

**Endpoints:**
- `GET /api/flashcards/` - List all user's flashcards
- `POST /api/flashcards/` - Create new flashcard

**GET Request Example:**
```
GET /api/flashcards/
```

**GET Response (200 OK):**
```json
[
  {
    "id": 1,
    "phrase": {
      "id": 15,
      "original_text": "Good morning",
      "translated_text": "Buenos días"
    },
    "repetitions": 3,
    "interval": 7,
    "ef": 2.6,
    "next_review_date": "2024-12-14T10:00:00Z",
    "total_reviews": 5,
    "correct_reviews": 4,
    "last_reviewed_at": "2024-12-07T10:00:00Z"
  }
]
```

**POST Request Example:**
```json
{
  "phrase": 15,
  "ef": 2.5
}
```

**POST Response (201 Created):**
```json
{
  "id": 2,
  "phrase": 15,
  "repetitions": 0,
  "interval": 1,
  "ef": 2.5,
  "next_review_date": "2024-12-07T10:00:00Z",
  "total_reviews": 0,
  "correct_reviews": 0
}
```

---

#### Retrieve/Update/Delete Flashcard

Manage a specific flashcard.

**Endpoints:**
- `GET /api/flashcards/{id}/` - Retrieve flashcard details
- `PUT /api/flashcards/{id}/` - Full update
- `PATCH /api/flashcards/{id}/` - Partial update
- `DELETE /api/flashcards/{id}/` - Delete flashcard

**GET Request Example:**
```
GET /api/flashcards/1/
```

**GET Response (200 OK):**
```json
{
  "id": 1,
  "phrase": {
    "id": 15,
    "original_text": "Good morning",
    "translated_text": "Buenos días"
  },
  "repetitions": 3,
  "interval": 7,
  "ef": 2.6,
  "next_review_date": "2024-12-14T10:00:00Z",
  "total_reviews": 5,
  "correct_reviews": 4,
  "last_reviewed_at": "2024-12-07T10:00:00Z",
  "created_at": "2024-11-01T10:00:00Z",
  "updated_at": "2024-12-07T10:00:00Z"
}
```

**DELETE Response (204 No Content)**

---

#### Get Due Flashcards

Retrieve flashcards scheduled for review using the SM-2 spaced repetition algorithm.

**Endpoint:** `GET /api/flashcards/due/`

**Features:**
- Automatically filters by authenticated user
- Returns only cards where `next_review_date ≤ current time`
- Limited to 20 cards per request
- Ordered by review priority (earliest first)

**Request Example:**
```
GET /api/flashcards/due/
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "phrase": {
      "id": 15,
      "original_text": "Good morning",
      "translated_text": "Buenos días"
    },
    "repetitions": 2,
    "interval": 3,
    "ef": 2.5,
    "next_review_date": "2024-12-07T08:00:00Z",
    "total_reviews": 3,
    "correct_reviews": 2
  },
  {
    "id": 2,
    "phrase": {
      "id": 20,
      "original_text": "Thank you",
      "translated_text": "Gracias"
    },
    "repetitions": 0,
    "interval": 1,
    "ef": 2.5,
    "next_review_date": "2024-12-07T09:30:00Z",
    "total_reviews": 1,
    "correct_reviews": 0
  }
]
```

---

#### Answer Flashcard (SM-2)

Submit an answer to a flashcard and update its spaced repetition schedule.

**Endpoint:** `POST /api/flashcards/{phrase_id}/answer/`

**SM-2 Quality Scale:**
| Quality | Meaning | Effect |
|---------|---------|--------|
| 0 | Complete blackout | Reset to day 1 |
| 1 | Incorrect, but familiar | Reset to day 1 |
| 2 | Incorrect, but easy to recall | Reset to day 1 |
| 3 | Correct with difficulty | Increase interval slightly |
| 4 | Correct with hesitation | Increase interval moderately |
| 5 | Perfect recall | Increase interval significantly |

**Request Body:**
```json
{
  "quality": 5
}
```

**Parameters:**
| Field | Type | Required | Range | Description |
|-------|------|----------|-------|-------------|
| `quality` | integer | Yes | 0-5 | Answer quality rating |

**Response (200 OK):**
```json
{
  "message": "Flashcard updated successfully.",
  "interval_days": 10,
  "ef": 2.6,
  "repetitions": 4,
  "next_review": "2024-12-17T10:00:00Z"
}
```

**Example Flow:**
```bash
# 1. Get cards due for review
GET /api/flashcards/due/

# 2. User answers card (perfect recall)
POST /api/flashcards/15/answer/
{"quality": 5}

# 3. SM-2 algorithm schedules next review
# → Next review in 10 days
```

---

### Practice Sessions

#### Start Practice Session

Create a new practice session for any game mode.

**Endpoint:** `POST /api/flashcards/practice-sessions/start/`

**Request Body:**
```json
{
  "session_type": "quiz"
}
```

**Session Types:**
| Type | Description |
|------|-------------|
| `flashcard` | Traditional flashcard review |
| `timed` | Time-limited challenge mode |
| `matching` | Match pairs game |
| `quiz` | Multiple choice quiz |

**Response (201 Created):**
```json
{
  "id": 1,
  "user": 5,
  "session_type": "quiz",
  "phrases_practiced": 0,
  "correct_answers": 0,
  "incorrect_answers": 0,
  "points_earned": 0,
  "duration_seconds": 0,
  "completed": false,
  "started_at": "2024-12-07T10:00:00Z",
  "completed_at": null,
  "mode_data": {}
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "not valid cause is not in session_type"
}
```

---

#### List Practice Sessions

Retrieve all practice sessions for the authenticated user.

**Endpoint:** `GET /api/flashcards/practice-sessions/`

**Features:**
- Ordered by most recent first
- Includes all session types
- Shows completion status

**Response (200 OK):**
```json
[
  {
    "id": 10,
    "session_type": "timed",
    "phrases_practiced": 15,
    "correct_answers": 12,
    "incorrect_answers": 3,
    "points_earned": 144,
    "duration_seconds": 180,
    "completed": true,
    "started_at": "2024-12-07T14:30:00Z",
    "completed_at": "2024-12-07T14:33:00Z"
  },
  {
    "id": 9,
    "session_type": "matching",
    "phrases_practiced": 8,
    "correct_answers": 8,
    "incorrect_answers": 0,
    "points_earned": 64,
    "duration_seconds": 45,
    "completed": true,
    "started_at": "2024-12-07T12:00:00Z",
    "completed_at": "2024-12-07T12:00:45Z"
  }
]
```

---

#### Get Practice Session Details

Retrieve detailed information about a specific session including all answers.

**Endpoint:** `GET /api/flashcards/practice-sessions/{id}/`

**Response (200 OK):**
```json
{
  "id": 1,
  "user": 5,
  "session_type": "quiz",
  "phrases_practiced": 10,
  "correct_answers": 8,
  "incorrect_answers": 2,
  "points_earned": 80,
  "duration_seconds": 120,
  "completed": true,
  "started_at": "2024-12-07T10:00:00Z",
  "completed_at": "2024-12-07T10:02:00Z",
  "mode_data": {},
  "details": [
    {
      "id": 1,
      "phrase": {
        "id": 15,
        "original_text": "Good morning",
        "translated_text": "Buenos días"
      },
      "was_correct": true,
      "response_time_seconds": 3,
      "answered_at": "2024-12-07T10:00:05Z"
    }
  ]
}
```

---

#### Add Practice Detail

Record an individual answer during a practice session.

**Endpoint:** `POST /api/flashcards/practice-sessions/{session_id}/detail/`

**Request Body:**
```json
{
  "phrase_id": 456,
  "was_correct": true,
  "response_time_seconds": 2.5
}
```

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `phrase_id` | integer | Yes | ID of the phrase being practiced |
| `was_correct` | boolean | Yes | Whether answer was correct |
| `response_time_seconds` | float | No | Time taken to answer |

**Response (201 Created):**
```json
{
  "id": 1,
  "practice_session": 1,
  "phrase": {
    "id": 456,
    "original_text": "Hello",
    "translated_text": "Hola"
  },
  "was_correct": true,
  "response_time_seconds": 2.5,
  "answered_at": "2024-12-07T10:00:05Z"
}
```

**Points Awarded:**
- Correct answer: +10 points
- Session statistics updated in real-time

**Error Responses:**
- `404 Not Found` - Session or phrase not found
```json
{
  "error": "session not found"
}
```

---

#### Complete Practice Session

Mark a session as completed and calculate final statistics.

**Endpoint:** `POST /api/flashcards/practice-sessions/{session_id}/complete/`

**Request Body:**
```json
{}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user": 5,
  "session_type": "quiz",
  "phrases_practiced": 10,
  "correct_answers": 8,
  "incorrect_answers": 2,
  "points_earned": 80,
  "duration_seconds": 120,
  "completed": true,
  "started_at": "2024-12-07T10:00:00Z",
  "completed_at": "2024-12-07T10:02:00Z"
}
```

**Error Responses:**
- `404 Not Found` - Session not found
- `400 Bad Request` - Session already completed
```json
{
  "error": "The session is finished"
}
```

---

### Game Modes

#### Matching Game

##### Start Matching Game

Initialize a new matching pairs game session.

**Endpoint:** `POST /api/flashcards/matching/start/`

**Request Body:**
```json
{
  "pairs": 8
}
```

**Parameters:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `pairs` | integer | No | 8 | Number of pairs (recommended 4-8) |

**Response (201 Created):**
```json
{
  "session": {
    "id": 1,
    "session_type": "matching",
    "started_at": "2024-12-07T10:00:00Z",
    "completed": false,
    "mode_data": {
      "pairs": [15, 20, 25, 30, 35, 40, 45, 50],
      "right_order": [30, 15, 45, 20, 50, 35, 25, 40]
    }
  },
  "left": [
    {"id": 15, "text": "Good morning"},
    {"id": 20, "text": "Thank you"},
    {"id": 25, "text": "Goodbye"},
    {"id": 30, "text": "Please"}
  ],
  "right": [
    {"id": 30, "text": "Por favor"},
    {"id": 15, "text": "Buenos días"},
    {"id": 25, "text": "Adiós"},
    {"id": 20, "text": "Gracias"}
  ]
}
```

**Note:** The `right` array is randomly shuffled for gameplay.

---

##### Check Matching Pairs

Validate user's matched pairs and update score.

**Endpoint:** `POST /api/flashcards/matching/check/`

**Request Body:**
```json
{
  "session_id": 1,
  "matches": [
    {"left_id": 15, "right_id": 15},
    {"left_id": 20, "right_id": 30},
    {"left_id": 25, "right_id": 25}
  ]
}
```

**Response (200 OK):**
```json
{
  "results": [
    {
      "left_id": 15,
      "right_id": 15,
      "correct": true
    },
    {
      "left_id": 20,
      "right_id": 30,
      "correct": false
    },
    {
      "left_id": 25,
      "right_id": 25,
      "correct": true
    }
  ],
  "summary": {
    "id": 1,
    "phrases_practiced": 3,
    "correct_answers": 2,
    "incorrect_answers": 1,
    "points_earned": 16
  }
}
```

**Points System:**
- Correct match: +8 points
- Incorrect match: 0 points

---

##### Finish Matching Game

Complete the matching game session.

**Endpoint:** `POST /api/flashcards/matching/finish/`

**Request Body:**
```json
{
  "session_id": 1
}
```

**Response (200 OK):**
```json
{
  "session": {
    "id": 1,
    "session_type": "matching",
    "phrases_practiced": 8,
    "correct_answers": 7,
    "incorrect_answers": 1,
    "points_earned": 56,
    "duration_seconds": 45,
    "completed": true,
    "started_at": "2024-12-07T10:00:00Z",
    "completed_at": "2024-12-07T10:00:45Z"
  }
}
```

---

#### Timed Challenge Mode

##### Start Timed Challenge

Begin a time-limited practice session.

**Endpoint:** `POST /api/flashcards/timed/start/`

**Request Body:**
```json
{
  "seconds": 60,
  "count": 20
}
```

**Parameters:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `seconds` | integer | No | 60 | Time limit in seconds |
| `count` | integer | No | 20 | Number of questions |

**Response (201 Created):**
```json
{
  "session": {
    "id": 1,
    "session_type": "timed",
    "started_at": "2024-12-07T10:00:00Z",
    "completed": false,
    "mode_data": {
      "time_limit_seconds": 60,
      "question_ids": [15, 20, 25, 30, 35],
      "current_index": 0,
      "start_ts": "2024-12-07T10:00:00Z"
    }
  },
  "questions": [
    {"id": 15, "original_text": "Good morning"},
    {"id": 20, "original_text": "Thank you"},
    {"id": 25, "original_text": "Goodbye"}
  ],
  "time_limit_seconds": 60
}
```

---

##### Submit Timed Answer

Submit an answer during the timed challenge.

**Endpoint:** `POST /api/flashcards/timed/answer/`

**Request Body:**
```json
{
  "session_id": 1,
  "phrase_id": 15,
  "user_answer": "buenos dias",
  "elapsed_seconds": 3.5
}
```

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | integer | Yes | Active session ID |
| `phrase_id` | integer | Yes | Current question ID |
| `user_answer` | string | Yes | User's translation attempt |
| `elapsed_seconds` | float | No | Time taken for this answer |

**Validation Logic:**
- Exact match (case-insensitive)
- Partial match (contains expected text)
- Flexible comparison for typos

**Response (200 OK):**
```json
{
  "detail": {
    "id": 1,
    "phrase": {
      "id": 15,
      "original_text": "Good morning",
      "translated_text": "Buenos días"
    },
    "was_correct": true,
    "response_time_seconds": 3.5,
    "answered_at": "2024-12-07T10:00:03Z"
  },
  "correct": true,
  "session": {
    "id": 1,
    "phrases_practiced": 1,
    "correct_answers": 1,
    "incorrect_answers": 0,
    "points_earned": 12
  }
}
```

**Points System:**
- Correct answer: +12 points
- Incorrect answer: 0 points

---

##### Finish Timed Challenge

Complete the timed challenge session.

**Endpoint:** `POST /api/flashcards/timed/finish/`

**Request Body:**
```json
{
  "session_id": 1
}
```

**Response (200 OK):**
```json
{
  "session": {
    "id": 1,
    "session_type": "timed",
    "phrases_practiced": 20,
    "correct_answers": 16,
    "incorrect_answers": 4,
    "points_earned": 192,
    "duration_seconds": 58,
    "completed": true,
    "started_at": "2024-12-07T10:00:00Z",
    "completed_at": "2024-12-07T10:00:58Z"
  }
}
```

---

## Models

### FlashcardReview

Tracks individual flashcard progress using the SM-2 spaced repetition algorithm.

```python
{
  "id": integer,
  "user": integer (user_id),
  "phrase": integer (phrase_id),
  "repetitions": integer,           # Number of successful reviews
  "interval": integer,               # Days until next review
  "ef": float,                       # Ease Factor (2.5 default)
  "next_review_date": datetime,      # When to review next
  "total_reviews": integer,          # Total review attempts
  "correct_reviews": integer,        # Successful reviews
  "last_reviewed_at": datetime,
  "created_at": datetime,
  "updated_at": datetime
}
```

**SM-2 Algorithm Fields:**
- `repetitions`: Consecutive correct answers
- `interval`: Current interval in days (1, 6, 10, 15, etc.)
- `ef`: Ease factor affecting interval growth (1.3 - 2.5+)

---

### PracticeSession

Represents a complete practice session of any type.

```python
{
  "id": integer,
  "user": integer (user_id),
  "session_type": string,           # flashcard|timed|matching|quiz
  "mode_data": object,               # Mode-specific configuration
  "phrases_practiced": integer,
  "correct_answers": integer,
  "incorrect_answers": integer,
  "points_earned": integer,
  "duration_seconds": integer,
  "completed": boolean,
  "started_at": datetime,
  "completed_at": datetime
}
```

**Session Types:**
- `flashcard` - Traditional spaced repetition
- `timed` - Time-limited translation challenge
- `matching` - Match original text with translations
- `quiz` - Multiple choice questions

---

### PracticeSessionDetail

Individual answer record within a practice session.

```python
{
  "id": integer,
  "practice_session": integer (session_id),
  "phrase": object (Phrase details),
  "was_correct": boolean,
  "response_time_seconds": float,
  "answered_at": datetime
}
```

---

## Error Handling

### Standard Error Response Format

```json
{
  "error": "Error message description",
  "detail": "Additional context (optional)"
}
```

### Common HTTP Status Codes

| Code | Description |
|------|-------------|
| `200` | Success |
| `201` | Created successfully |
| `204` | Deleted successfully (no content) |
| `400` | Bad request - invalid input data |
| `401` | Unauthorized - authentication required |
| `404` | Not found - resource doesn't exist |

---

## Usage Examples

### Complete Flashcard Review Workflow

```bash
# 1. Get cards due for review
GET /api/flashcards/due/
→ Returns 5 cards scheduled for today

# 2. User reviews first card - perfect recall
POST /api/flashcards/15/answer/
{"quality": 5}
→ Next review scheduled in 10 days

# 3. User reviews second card - struggled
POST /api/flashcards/20/answer/
{"quality": 3}
→ Next review scheduled in 3 days

# 4. Check remaining due cards
GET /api/flashcards/due/
→ Returns 3 remaining cards
```

---

### Complete Matching Game Workflow

```bash
# 1. Start matching game with 6 pairs
POST /api/flashcards/matching/start/
{"pairs": 6}
→ Returns shuffled left/right arrays

# 2. User matches all pairs
POST /api/flashcards/matching/check/
{
  "session_id": 1,
  "matches": [
    {"left_id": 15, "right_id": 15},
    {"left_id": 20, "right_id": 20}
  ]
}
→ Returns correctness results + score

# 3. Complete the game
POST /api/flashcards/matching/finish/
{"session_id": 1}
→ Returns final statistics
```

---

### Complete Timed Challenge Workflow

```bash
# 1. Start 60-second challenge with 20 questions
POST /api/flashcards/timed/start/
{"seconds": 60, "count": 20}
→ Returns questions and timer config

# 2. User answers questions rapidly
POST /api/flashcards/timed/answer/
{
  "session_id": 1,
  "phrase_id": 15,
  "user_answer": "buenos dias",
  "elapsed_seconds": 2.3
}
→ Returns immediate feedback

# 3. Time expires or all questions answered
POST /api/flashcards/timed/finish/
{"session_id": 1}
→ Returns final score and statistics
```

---

## Points System

| Action | Points | Notes |
|--------|--------|-------|
| Correct answer (standard) | +10 | Default practice mode |
| Correct answer (timed) | +12 | Bonus for speed challenge |
| Correct match | +8 | Matching game |
| Incorrect answer | 0 | No penalty |

---

## Best Practices

1. **Spaced Repetition**: Always use the `due/` endpoint to get optimally scheduled cards
2. **Quality Ratings**: Be honest with quality ratings (0-5) for best learning outcomes
3. **Session Management**: Always call `complete/` endpoint to properly close sessions
4. **Error Handling**: Handle 404 errors gracefully when phrases/sessions are deleted
5. **Performance**: Limit matching pairs to 4-8 for optimal user experience

---

## Notes

- All endpoints require authentication
- Flashcards are user-specific and isolated
- SM-2 algorithm automatically adjusts based on performance
- Sessions must be completed to save statistics
- All datetime fields use ISO 8601 format
- Response times are tracked for analytics

---

## Support

For issues or questions, please open an issue on the GitHub repository.