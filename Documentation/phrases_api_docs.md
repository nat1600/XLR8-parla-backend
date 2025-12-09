# Phrases API Documentation

A comprehensive REST API for managing Phrases endpoints

## Table of Contents

- [Authentication](#authentication)
- [Base URL](#base-url)
- [Endpoints](#endpoints)
  - [Translation](#translation)
  - [Phrases](#phrases)
  - [Categories](#categories)
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
/api/phrases/
```

---

## Endpoints

### Translation

#### Translate Text

Provides real-time translation between supported languages.

**Endpoint:** `POST /api/phrases/translate/`

**Request Body:**
```json
{
  "text": "dog",
  "source_lang": "en",
  "target_lang": "es"
}
```

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | Yes | Text to translate |
| `source_lang` | string | Yes | Source language code (e.g., "en") |
| `target_lang` | string | Yes | Target language code (e.g., "es") |

**Success Response (200 OK):**
```json
{
  "original": "dog",
  "translation": "perro",
  "pronunciation": null,
  "source_lang": "en",
  "target_lang": "es"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid input data
- `503 Service Unavailable` - Translation service failed

**Example Error Response:**
```json
{
  "detail": "Translation failed",
  "error": "Service timeout"
}
```

---

### Phrases

#### List Phrases

Retrieve all phrases for the authenticated user with optional filtering and search.

**Endpoint:** `GET /api/phrases/phrases/`

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `source_language` | integer | Filter by source language ID |
| `target_language` | integer | Filter by target language ID |
| `source_type` | string | Filter by phrase source type |
| `search` | string | Search in original_text and translated_text |
| `ordering` | string | Sort by field (e.g., `-created_at`, `updated_at`) |
| `page` | integer | Page number for pagination |

**Examples:**
```
GET /api/phrases/phrases/
GET /api/phrases/phrases/?source_language=1&target_language=2
GET /api/phrases/phrases/?search=hello
GET /api/phrases/phrases/?ordering=-created_at
```

**Success Response (200 OK):**
```json
{
  "count": 42,
  "next": "http://api.example.com/api/phrases/phrases/?page=2",
  "previous": null,
  "results": [
    {
      "id": 15,
      "original_text": "Good morning",
      "translated_text": "Buenos días",
      "source_language": "en",
      "target_language": "es",
      "created_at": "2024-12-07T10:30:00Z"
    }
  ]
}
```
NOTE: We did not work in sourcelange different to: "en". 

---

#### Create Phrase

Save a new phrase to the user's collection.

**Endpoint:** `POST /api/phrases/phrases/`

**Request Body:**
```json
{
  "original_text": "Good morning",
  "translated_text": "Buenos días",
  "source_language": 1,
  "target_language": 2,
  "categories": [1, 3],
  "pronunciation": null,
  "notes": "Common greeting used before noon"
}
```

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `original_text` | string | Yes | Original phrase text |
| `translated_text` | string | Yes | Translated phrase text |
| `source_language` | integer | Yes | Source language ID |
| `target_language` | integer | Yes | Target language ID |
| `categories` | array | No | Array of category IDs |
| `pronunciation` | string | No | Pronunciation guide |
| `notes` | string | No | Additional notes |

**Success Response (201 Created):**
```json
{
  "id": 15,
  "original_text": "Good morning",
  "translated_text": "Buenos días",
  "source_language": "en",
  "target_language": "es",
  "categories": [
    {
      "id": 1,
      "name": "Greetings",
      "type": "theme"
    }
  ],
  "pronunciation": null,
  "notes": "Common greeting used before noon",
  "created_at": "2024-12-07T10:30:00Z",
  "updated_at": "2024-12-07T10:30:00Z"
}
```

---

#### Retrieve Phrase

Get details of a specific phrase.

**Endpoint:** `GET /api/phrases/phrases/{id}/`

**Success Response (200 OK):**
```json
{
  "id": 15,
  "original_text": "Good morning",
  "translated_text": "Buenos días",
  "source_language": "en",
  "target_language": "es",
  "categories": [
    {
      "id": 1,
      "name": "Greetings",
      "type": "theme"
    }
  ],
  "pronunciation": null,
  "notes": "Common greeting used before noon",
  "source_type": "YouTube",
  "created_at": "2024-12-07T10:30:00Z",
  "updated_at": "2024-12-07T10:30:00Z"
}
```

---

#### Update Phrase

Update an existing phrase (full update).

**Endpoint:** `PUT /api/phrases/phrases/{id}/`

**Request Body:**
```json
{
  "original_text": "Good morning",
  "translated_text": "Buenos días",
  "source_language": 1,
  "target_language": 2,
  "categories": [1, 3],
  "pronunciation": null,
  "notes": "Updated notes"
}
```

**Success Response (200 OK):**
Returns the updated phrase object.

---

#### Partial Update Phrase

Update specific fields of a phrase.

**Endpoint:** `PATCH /api/phrases/phrases/{id}/`

**Request Body:**
```json
{
  "notes": "Updated notes only",
  "categories": [1, 2, 5]
}
```

**Success Response (200 OK):**
Returns the updated phrase object.

---

#### Delete Phrase

Remove a phrase from the user's collection.

**Endpoint:** `DELETE /api/phrases/phrases/{id}/`

**Success Response (204 No Content):**
No response body.

---

### Categories

#### List Categories

Retrieve all available phrase categories.

**Endpoint:** `GET /api/phrases/categories/`

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `type` | string | Filter by category type (`grammar` or `theme`) |
| `page` | integer | Page number for pagination |

**Examples:**
```
GET /api/phrases/categories/
GET /api/phrases/categories/?type=grammar
GET /api/phrases/categories/?type=theme
```

**Success Response (200 OK):**
```json
{
  "count": 20,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Greetings",
      "type": "theme",
      "description": "Common greetings and salutations"
    },
    {
      "id": 2,
      "name": "Verbs",
      "type": "grammar",
      "description": "Action words and verb conjugations"
    }
  ]
}
```

---

#### Retrieve Category

Get details of a specific category.

**Endpoint:** `GET /api/phrases/categories/{id}/`

**Success Response (200 OK):**
```json
{
  "id": 1,
  "name": "Greetings",
  "type": "theme",
  "description": "Common greetings and salutations"
}
```

---

## Models

### Phrase
```python
{
  "id": integer,
  "original_text": string,
  "translated_text": string,
  "source_language": string (language code),
  "target_language": string (language code),
  "categories": array of Category objects,
  "pronunciation": string (optional),
  "notes": string (optional),
  "source_type": string,
  "created_at": datetime,
  "updated_at": datetime
}
```

### Category
```python
{
  "id": integer,
  "name": string,
  "type": string ("grammar" or "theme"),
  "description": string
}
```

### Language
```python
{
  "id": integer,
  "code": string (e.g., "en", "es"),
  "name": string (e.g., "English", "Spanish")
}
```

---

## Error Handling

### Standard Error Response Format

```json
{
  "detail": "Error message",
  "error": "Additional error details (optional)"
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
| `503` | Service unavailable - external service failure |

---

## Usage Examples

### Complete Workflow Example

**1. Translate a phrase:**
```bash
curl -X POST https://api.example.com/api/phrases/translate/ \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world",
    "source_lang": "en",
    "target_lang": "es"
  }'
```

**2. Save the translated phrase:**
```bash
curl -X POST https://api.example.com/api/phrases/phrases/ \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "original_text": "Hello world",
    "translated_text": "Hola mundo",
    "source_language": 1,
    "target_language": 2,
    "categories": [1]
  }'
```

**3. Search your saved phrases:**
```bash
curl -X GET "https://api.example.com/api/phrases/phrases/?search=hello" \
  -H "Authorization: Token your-token-here"
```

---

## Notes

- All endpoints require authentication
- Phrases are user-specific - users can only access their own phrases
- Pagination is enabled on list endpoints (default page size configured in settings)

---

## Support

For issues or questions, please open an issue on the GitHub repository.
