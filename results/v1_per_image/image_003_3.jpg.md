# Image Recognition Batch Test Results

**Test Date:** January 26, 2026 (2026-01-26)
**Test Run Timestamp:** 2026-01-26T19:08:58.153476
**Server URL:** http://localhost:8000
**Test Directory:** /Users/andreas/Documents/Dokumenter – MacBook Air/UIO/master/Thesis/Project/testing/Image_search/test_images
**Total Images:** 211
**Total Tests:** 422 (each image tested with and without metadata)
**Approaches Used:** GPT Vision Direct, GPT Vision + Search, Google Cloud Vision, Google Maps Places
**Metadata Testing:** Each image tested with metadata=True and metadata=False

---

---

## Image 3: 3.jpg

**Path:** `/Users/andreas/Documents/Dokumenter – MacBook Air/UIO/master/Thesis/Project/testing/Image_search/test_images/3.jpg`

<img src="/Users/andreas/Documents/Dokumenter – MacBook Air/UIO/master/Thesis/Project/testing/Image_search/test_images/3.jpg" alt="3.jpg" style="max-width: 400px; max-height: 300px;">

### **WITH METADATA**

**Processing Time:** 99.01 seconds
**Timestamp:** 2026-01-26T16:36:44.326697

**Extracted Metadata:**
- Camera: FUJIFILM X-T30 II

### GPT Vision Direct

**Status:** ✅ Success
**Identified:** Vigeland Park sculpture, Oslo, Norway
**Confidence:** 80.0%
**Processing Time:** 8.00 seconds

**Details:**
```json
{
  "reasoning": "The image shows a sculpture with a distinct modern design, which resembles the style found in Vigeland Park, known for its unique and abstract sculptures.",
  "features": [
    "modern sculpture",
    "abstract design",
    "outdoor setting"
  ],
  "location": "Oslo, Norway",
  "type": "sculpture",
  "search_range_meters": 1000,
  "raw_response": "```json\n{\n    \"identified\": \"Vigeland Park sculpture\",\n    \"location\": \"Oslo, Norway\",\n    \"confidence\": 0.8,\n    \"reasoning\": \"The image shows a sculpture with a distinct modern design, which resembles the style found in Vigeland Park, known for its unique and abstract sculptures.\",\n    \"features\": [\"modern sculpture\", \"abstract design\", \"outdoor setting\"],\n    \"type\": \"sculpture\",\n    \"search_range_meters\": 1000\n}\n```",
  "camera": {
    "make": "FUJIFILM",
    "model": "X-T30 II"
  },
  "processing_time_seconds": 7.998392105102539
}
```

### GPT Vision + Search

**Status:** ✅ Success
**Identified:** Modern architectural structure with cylindrical element and staircase
**Confidence:** 60.0%
**Processing Time:** 91.01 seconds

**Details:**
```json
{
  "reasoning": "The description matches a modern architectural style with specific features such as an angular structure, cylindrical element, and metal staircase. However, without specific names or locations provided in the search results, the identification remains general. The search results do not provide a clear match to a known landmark or building, and the lack of GPS coordinates further limits specificity.",
  "sources_used": [
    "wallpaper.com",
    "apnews.com",
    "homesandgardens.com"
  ],
  "all_candidates": [
    "*URL*: ([wallpaper.com]())",
    "*URL*: ([apnews.com]())",
    "*URL*: ([wallpaper.com]())",
    "*URL*: ([en.wikipedia.org]())",
    "*URL*: ([homesandgardens.com]())"
  ],
  "type": "building",
  "search_range_meters": 1000,
  "description": "The image features a large, angular structure with a dark, textured surface, possibly made of stone or metal. Attached to this structure is a long, cylindrical element that extends horizontally, resembling a funnel or pipe. Below this cylindrical part is a staircase with metal railings, leading upwards and connecting to the structure. The staircase is composed of evenly spaced steps, and there is a sign visible near its base. The background shows a cloudy sky and a distant view of greenery, sugg",
  "architectural_style": "Modern",
  "search_backends_used": [
    "web"
  ],
  "camera": {
    "make": "FUJIFILM",
    "model": "X-T30 II"
  },
  "processing_time_seconds": 91.00816297531128
}
```

### Google Cloud Vision

**Status:** ❌ Failed
**Error:** API error: Bad image data.

### **WITHOUT METADATA**

**Processing Time:** 96.87 seconds
**Timestamp:** 2026-01-26T16:38:23.412754

### GPT Vision Direct

**Status:** ✅ Success
**Identified:** Vigeland Park Sculpture, Oslo, Norway
**Confidence:** 80.0%
**Processing Time:** 6.92 seconds

**Details:**
```json
{
  "reasoning": "The image shows a sculpture that resembles the style found in Vigeland Park, known for its unique and abstract sculptures.",
  "features": [
    "abstract sculpture",
    "metallic structure",
    "staircase leading to sculpture"
  ],
  "location": "Oslo, Norway",
  "type": "sculpture",
  "search_range_meters": 1000,
  "raw_response": "```json\n{\n    \"identified\": \"Vigeland Park Sculpture\",\n    \"location\": \"Oslo, Norway\",\n    \"confidence\": 0.8,\n    \"reasoning\": \"The image shows a sculpture that resembles the style found in Vigeland Park, known for its unique and abstract sculptures.\",\n    \"features\": [\"abstract sculpture\", \"metallic structure\", \"staircase leading to sculpture\"],\n    \"type\": \"sculpture\",\n    \"search_range_meters\": 1000\n}\n```",
  "processing_time_seconds": 6.918887138366699
}
```

### GPT Vision + Search

**Status:** ✅ Success
**Identified:** Contemporary architectural structure with cylindrical element
**Confidence:** 60.0%
**Processing Time:** 89.95 seconds

**Details:**
```json
{
  "reasoning": "The description matches contemporary architectural features, but no specific name or location is provided in the search results. The angular dark structure and cylindrical element suggest a modern design, possibly an installation or building. The search results do not provide a specific identification, but the contemporary style and features are consistent with the description.",
  "sources_used": [
    "en.wikipedia.org"
  ],
  "all_candidates": [
    "*URL*: ([wallpaper.com]())",
    "*URL*: ([apnews.com]())",
    "*URL*: ([stanislav-kondrashov.ghost.io]())",
    "*URL*: ([stanislav-kondrashov.ghost.io]())",
    "*URL*: ([en.wikipedia.org]())"
  ],
  "type": "building",
  "search_range_meters": 1000,
  "description": "The image features a large, dark, angular structure with a smooth surface, possibly made of metal or a similar material. Attached to this structure is a long, cylindrical element that extends outward horizontally. Below this cylinder is a staircase with metal railings, leading up to the cylindrical structure. The background shows a cloudy sky and a distant view of green, forested hills.",
  "architectural_style": "Contemporary",
  "search_backends_used": [
    "web"
  ],
  "processing_time_seconds": 89.94758605957031
}
```

### Google Cloud Vision

**Status:** ❌ Failed
**Error:** API error: Bad image data.

---
