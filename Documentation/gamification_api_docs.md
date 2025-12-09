# Gamification API Documentation

A comprehensive REST API for managing user gamification features including streaks, points, achievements, and statistics.

## Table of Contents

- [Authentication](#authentication)
- [Base URL](#base-url)
- [Endpoints](#endpoints)
  - [Activity & Streaks](#activity--streaks)
  - [Points](#points)
  - [Achievements](#achievements)
  - [Statistics](#statistics)
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
/api/gamification/
```

---

## Endpoints

### Activity & Streaks

#### Register Activity

Records user activity for the day and updates their streak.

**Endpoint:** `POST /api/gamification/activity/`

**Request Body:**
```json
{}
```
*Note: No body required - authentication identifies the user*

**Success Response (200 OK):**
```json
{
  "streak": 5,
  "best_streak": 10
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `streak` | integer | Current consecutive days streak |
| `best_streak` | integer | All-time longest streak |

**Streak Logic:**
- **First activity**: Sets streak to 1
- **Same day**: No change to streak
- **Next day (consecutive)**: Increments streak by 1
- **Gap in days**: Resets streak to 1
- Automatically updates `longest_streak` if current streak exceeds it
- Creates/updates `DailyStatistic` record for the day

**Achievements Unlocked:**
- `streak_7`: 7 consecutive days
- `streak_30`: 30 consecutive days
- `streak_100`: 100 consecutive days

---

#### Get Current Streak

Retrieve the user's current streak information.

**Endpoint:** `GET /api/gamification/streak/`

**Success Response (200 OK):**
```json
{
  "streak": 5,
  "best_streak": 10,
  "last_practice_date": "2025-12-08"
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `streak` | integer | Current consecutive days streak |
| `best_streak` | integer | All-time longest streak |
| `last_practice_date` | date | Last date user registered activity (nullable) |

---

### Points

#### Get User Points

Retrieve the user's total accumulated points.

**Endpoint:** `GET /api/gamification/points/`

**Success Response (200 OK):**
```json
{
  "total_points": 5050
}
```

---

#### Add Points

Add points to the user's total and check for achievements.

**Endpoint:** `POST /api/gamification/points/add/`

**Request Body:**
```json
{
  "amount": 100
}
```

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `amount` | integer | Yes | Points to add (must be > 0) |

**Success Response (200 OK):**
```json
{
  "total_points": 5150
}
```

**Error Responses:**

*Invalid amount (non-integer):*
```json
{
  "error": "El valor 'amount' debe ser un número entero."
}
```
*Status: 400 Bad Request*

*Zero or negative amount:*
```json
{
  "error": "El valor 'amount' debe ser mayor a 0."
}
```
*Status: 400 Bad Request*

**Side Effects:**
- Updates user's `total_points`
- Creates/updates `DailyStatistic.points_earned` for today
- Checks and unlocks point-based achievements

**Achievements Unlocked:**
- `points_1000`: 1,000 total points
- `points_5000`: 5,000 total points
- `points_10000`: 10,000 total points

---

### Achievements

#### List User Achievements

Retrieve all achievements unlocked by the user.

**Endpoint:** `GET /api/gamification/achievements/`

**Success Response (200 OK):**
```json
[
  {
    "id": 3,
    "achievement_type": "points_5000",
    "achievement_name": "5,000 puntos",
    "achieved_at": "2025-12-08T16:45:23.456789Z"
  },
  {
    "id": 2,
    "achievement_type": "streak_7",
    "achievement_name": "7 días consecutivos",
    "achieved_at": "2025-12-08T10:30:15.123456Z"
  },
  {
    "id": 1,
    "achievement_type": "points_1000",
    "achievement_name": "1,000 puntos",
    "achieved_at": "2025-12-07T14:20:10.987654Z"
  }
]
```

**Response Format:**
| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Achievement record ID |
| `achievement_type` | string | Achievement type code |
| `achievement_name` | string | Human-readable achievement name |
| `achieved_at` | datetime | When the achievement was unlocked |

**Ordering:**
Results are ordered by `achieved_at` descending (most recent first).

---

### Statistics

*Note: Statistics endpoints are referenced in models but views are not yet implemented. The following documents the data models available.*

#### Daily Statistics Model

Daily statistics are automatically created/updated when users:
- Register activity (streak)
- Add points
- Practice phrases

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `date` | date | Date of the statistics |
| `phrases_practiced` | integer | Number of phrases practiced |
| `correct_answers` | integer | Number of correct answers |
| `practice_minutes` | integer | Minutes spent practicing |
| `points_earned` | integer | Points earned on this day |
| `streak_maintained` | boolean | Whether streak was maintained |

---

## Models

### UserAchievement

```python
{
  "id": integer,
  "achievement_type": string,
  "achievement_name": string,
  "achieved_at": datetime,
  "user_id": integer
}
```

**Available Achievement Types:**

| Type | Display Name | Condition |
|------|--------------|-----------|
| `streak_7` | 7 días consecutivos | Maintain 7-day streak |
| `streak_30` | 30 días consecutivos | Maintain 30-day streak |
| `streak_100` | 100 días consecutivos | Maintain 100-day streak |
| `phrases_50` | 50 frases guardadas | Save 50 phrases |
| `phrases_100` | 100 frases guardadas | Save 100 phrases |
| `phrases_500` | 500 frases guardadas | Save 500 phrases |
| `perfect_10` | 10 sesiones perfectas | Complete 10 perfect sessions |
| `speed_demon` | Contrarreloj < 2 min | Complete challenge under 2 minutes |
| `polyglot` | 3+ idiomas | Practice 3+ languages |
| `points_1000` | 1,000 puntos | Reach 1,000 total points |
| `points_5000` | 5,000 puntos | Reach 5,000 total points |
| `points_10000` | 10,000 puntos | Reach 10,000 total points |

*Note: Some achievements (phrases, perfect_10, speed_demon, polyglot) are defined but not yet implemented in services.*

---

### DailyStatistic

```python
{
  "id": integer,
  "user_id": integer,
  "date": date,
  "phrases_practiced": integer,
  "correct_answers": integer,
  "practice_minutes": integer,
  "points_earned": integer,
  "streak_maintained": boolean
}
```

**Computed Fields:**
- `accuracy`: Calculated as `(correct_answers / phrases_practiced) * 100`

---

### User Fields (Extended)

The gamification system adds these fields to the User model:

```python
{
  "total_points": integer,
  "current_streak": integer,
  "longest_streak": integer,
  "last_practice_date": date (nullable)
}
```

---

## Error Handling

### Standard Error Response Format

```json
{
  "error": "Error message description"
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
| `403` | Forbidden - insufficient permissions |
| `404` | Not found - resource doesn't exist |
| `500` | Internal server error |

---

## Usage Examples

### Complete Workflow Example

**1. Register daily activity:**
```bash
curl -X POST https://api.example.com/api/gamification/activity/ \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "streak": 1,
  "best_streak": 1
}
```

---

**2. Add points after completing a challenge:**
```bash
curl -X POST https://api.example.com/api/gamification/points/add/ \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100
  }'
```

**Response:**
```json
{
  "total_points": 100
}
```

---

**3. Check current streak:**
```bash
curl -X GET https://api.example.com/api/gamification/streak/ \
  -H "Authorization: Token your-token-here"
```

**Response:**
```json
{
  "streak": 1,
  "best_streak": 1,
  "last_practice_date": "2025-12-08"
}
```

---

**4. View unlocked achievements:**
```bash
curl -X GET https://api.example.com/api/gamification/achievements/ \
  -H "Authorization: Token your-token-here"
```

**Response:**
```json
[
  {
    "id": 1,
    "achievement_type": "points_1000",
    "achievement_name": "1,000 puntos",
    "achieved_at": "2025-12-08T15:30:00.123456Z"
  }
]
```

---

**5. Get total points:**
```bash
curl -X GET https://api.example.com/api/gamification/points/ \
  -H "Authorization: Token your-token-here"
```

**Response:**
```json
{
  "total_points": 1050
}
```

---

## Testing Scenarios

### Scenario 1: Building a 7-Day Streak

```bash
# Day 1
POST /api/gamification/activity/
# Response: {"streak": 1, "best_streak": 1}

# Day 2 (next day)
POST /api/gamification/activity/
# Response: {"streak": 2, "best_streak": 2}

# ... Continue for 7 days

# Day 7
POST /api/gamification/activity/
# Response: {"streak": 7, "best_streak": 7}
# Achievement "streak_7" unlocked!

GET /api/gamification/achievements/
# Shows streak_7 achievement
```

---

### Scenario 2: Unlocking Points Achievements

```bash
# Start with 0 points
POST /api/gamification/points/add/
Body: {"amount": 1000}
# Achievement "points_1000" unlocked!

POST /api/gamification/points/add/
Body: {"amount": 4000}
# Achievement "points_5000" unlocked!

POST /api/gamification/points/add/
Body: {"amount": 5000}
# Achievement "points_10000" unlocked!

GET /api/gamification/achievements/
# Shows all 3 points achievements
```

---

### Scenario 3: Breaking and Rebuilding Streak

```bash
# Day 1
POST /api/gamification/activity/
# Response: {"streak": 1, "best_streak": 1}

# Day 2
POST /api/gamification/activity/
# Response: {"streak": 2, "best_streak": 2}

# Skip Day 3 (no activity)

# Day 4 (gap detected)
POST /api/gamification/activity/
# Response: {"streak": 1, "best_streak": 2}
# Streak resets but best_streak is preserved!
```

---

## Important Notes

### Streak Mechanics
- Streaks must be consecutive days
- Multiple activities on the same day don't increase streak
- Missing even one day resets the streak to 1
- `longest_streak` is never decreased, only updated when current streak exceeds it

### Points System
- Points are cumulative and never decrease
- Negative or zero amounts are rejected
- Points immediately update `total_points` and today's `DailyStatistic`
- Achievement checks run automatically after adding points

### Achievements
- Each achievement can only be unlocked once per user
- Attempting to unlock the same achievement multiple times is safe (no duplicates)
- Achievements are checked automatically when relevant actions occur
- Achievement unlock failures are silently caught to avoid disrupting main operations

### Daily Statistics
- Automatically created for today when needed
- Uses `get_or_create` to prevent duplicates
- Statistics are user-specific and date-specific
- Accuracy calculation handles division by zero safely

---

## Future Enhancements

The following features are planned but not yet implemented:

- **Leaderboard**: Compare points with other users
- **Weekly/Monthly Statistics**: Aggregated statistics endpoints
- **Phrase-based Achievements**: Track phrases saved and practiced
- **Perfect Session Achievements**: Track error-free practice sessions
- **Speed Achievements**: Reward fast completion times
- **Multi-language Achievements**: Track languages practiced

---

## Support

For issues or questions, please open an issue on the GitHub repository.

---

## Changelog

### Version 1.0.0
- Initial release
- Streak tracking and achievements
- Points system and achievements
- Daily statistics tracking
- User achievements listing