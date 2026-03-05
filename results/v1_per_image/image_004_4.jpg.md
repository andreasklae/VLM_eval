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

## Image 4: 4.jpg

**Path:** `/Users/andreas/Documents/Dokumenter – MacBook Air/UIO/master/Thesis/Project/testing/Image_search/test_images/4.jpg`

<img src="/Users/andreas/Documents/Dokumenter – MacBook Air/UIO/master/Thesis/Project/testing/Image_search/test_images/4.jpg" alt="4.jpg" style="max-width: 400px; max-height: 300px;">

### **WITH METADATA**

**Processing Time:** 49.21 seconds
**Timestamp:** 2026-01-26T17:01:42.539024

**Extracted Metadata:** None (no EXIF data found in image)

### GPT Vision Direct

**Status:** ✅ Success
**Identified:** Hohensalzburg Fortress, Salzburg, Austria
**Confidence:** 90.0%
**Processing Time:** 5.51 seconds

**Details:**
```json
{
  "reasoning": "The image shows a large fortress on a hill, which matches the appearance of Hohensalzburg Fortress in Salzburg. The surrounding architecture and landscape are consistent with the city.",
  "features": [
    "large fortress",
    "hilltop location",
    "historic architecture"
  ],
  "location": "Salzburg, Austria",
  "type": "landmark",
  "search_range_meters": 1000,
  "raw_response": "```json\n{\n    \"identified\": \"Hohensalzburg Fortress\",\n    \"location\": \"Salzburg, Austria\",\n    \"confidence\": 0.9,\n    \"reasoning\": \"The image shows a large fortress on a hill, which matches the appearance of Hohensalzburg Fortress in Salzburg. The surrounding architecture and landscape are consistent with the city.\",\n    \"features\": [\"large fortress\", \"hilltop location\", \"historic architecture\"],\n    \"type\": \"landmark\",\n    \"search_range_meters\": 1000\n}\n```",
  "processing_time_seconds": 5.512174129486084
}
```

### GPT Vision + Search

**Status:** ✅ Success
**Identified:** Prague Castle, Prague, Czech Republic
**Confidence:** 95.0%
**Processing Time:** 43.69 seconds

**Details:**
```json
{
  "reasoning": "The description matches Prague Castle, which is a prominent fortress situated on a hill overlooking the city of Prague. It features large fortified walls and multiple towers, characteristic of medieval architecture. Below the castle, the cityscape includes historic buildings with Baroque elements such as domes and spires. The search results likely include references to Prague Castle, given the architectural styles and notable features described.",
  "sources_used": [
    "en.wikipedia.org"
  ],
  "all_candidates": [
    "*URL*: ([en.wikipedia.org]())",
    "*URL*: ([en.wikipedia.org]())",
    "*URL*: ([en.wikipedia.org]())",
    "*URL*: ([en.wikipedia.org]())",
    "*URL*: ([en.wikipedia.org]())"
  ],
  "type": "landmark",
  "search_range_meters": 1000,
  "description": "The image features a prominent fortress situated on a hill, overlooking a cityscape. The fortress is characterized by its large, fortified walls and multiple towers, suggesting a medieval architectural style. Below the fortress, there is a collection of historic buildings with varied facades, including pastel-colored structures and ornate architectural details. Notable elements include a large dome and several spires, indicative of Baroque architecture. The setting is urban, with the fortress pr",
  "architectural_style": "Medieval and Baroque",
  "search_backends_used": [
    "web"
  ],
  "processing_time_seconds": 43.693660259246826
}
```

### Google Cloud Vision

**Status:** ✅ Success
**Identified:** Mozart Residence (47.8026, 13.0439)
**Confidence:** 64.4%
**Processing Time:** 28.14 seconds

**Details:**
```json
{
  "source": "landmark_detection",
  "landmark_name": "Mozart Residence",
  "coordinates": {
    "latitude": 47.8026282,
    "longitude": 13.043867899999999
  },
  "bounding_poly": [
    {
      "x": 0,
      "y": 0
    },
    {
      "x": 3626,
      "y": 0
    },
    {
      "x": 3626,
      "y": 2432
    },
    {
      "x": 0,
      "y": 2432
    }
  ],
  "context_labels": [
    "Building",
    "City",
    "Urban area",
    "Town",
    "Roof"
  ],
  "context_objects": [
    "Building",
    "Building",
    "Building"
  ],
  "web_entities": [
    {
      "name": "Local government",
      "score": 0.41920000314712524
    },
    {
      "name": "Architecture",
      "score": 0.39730000495910645
    },
    {
      "name": "Medieval architecture",
      "score": 0.38649263978004456
    },
    {
      "name": "Town hall",
      "score": 0.32670000195503235
    },
    {
      "name": "Apartment",
      "score": 0.3264663815498352
    }
  ],
  "all_landmarks": [
    {
      "name": "Mozart Residence",
      "score": 0.6440714001655579,
      "location": {
        "lat": 47.8026282,
        "lng": 13.043867899999999
      }
    },
    {
      "name": "Caf\u00e9 Bazar",
      "score": 0.58586186170578,
      "location": {
        "lat": 47.8018,
        "lng": 13.043777799999999
      }
    },
    {
      "name": "Fortress Hohensalzburg",
      "score": 0.5857912302017212,
      "location": {
        "lat": 47.794948299999994,
        "lng": 13.0476583
      }
    }
  ],
  "processing_time_seconds": 28.137648820877075
}
```

### **WITHOUT METADATA**

**Processing Time:** 47.84 seconds
**Timestamp:** 2026-01-26T17:02:31.768785

### GPT Vision Direct

**Status:** ✅ Success
**Identified:** Hohensalzburg Fortress, Salzburg, Austria
**Confidence:** 90.0%
**Processing Time:** 6.58 seconds

**Details:**
```json
{
  "reasoning": "The large fortress on the hill is a distinctive feature of Salzburg, known as Hohensalzburg Fortress. The surrounding architecture and landscape match the typical view of Salzburg.",
  "features": [
    "large fortress on hill",
    "historic buildings",
    "domed structures"
  ],
  "location": "Salzburg, Austria",
  "type": "landmark",
  "search_range_meters": 1000,
  "raw_response": "```json\n{\n    \"identified\": \"Hohensalzburg Fortress\",\n    \"location\": \"Salzburg, Austria\",\n    \"confidence\": 0.9,\n    \"reasoning\": \"The large fortress on the hill is a distinctive feature of Salzburg, known as Hohensalzburg Fortress. The surrounding architecture and landscape match the typical view of Salzburg.\",\n    \"features\": [\"large fortress on hill\", \"historic buildings\", \"domed structures\"],\n    \"type\": \"landmark\",\n    \"search_range_meters\": 1000\n}\n```",
  "processing_time_seconds": 6.577566862106323
}
```

### GPT Vision + Search

**Status:** ✅ Success
**Identified:** Prague Castle, Prague, Czech Republic
**Confidence:** 95.0%
**Processing Time:** 41.26 seconds

**Details:**
```json
{
  "reasoning": "The description matches Prague Castle, which is a historic fortress situated on a hill overlooking the city of Prague. It features multiple towers and battlements, characteristic of medieval architecture, and is surrounded by buildings with varied architectural styles, including Baroque elements. The mention of snow-covered roofs suggests a winter setting, which is consistent with Prague's climate. The picturesque backdrop of a city nestled in a valley surrounded by hills further supports this identification.",
  "sources_used": [
    "en.wikipedia.org"
  ],
  "all_candidates": [
    "*URL*: ([en.wikipedia.org]())",
    "*URL*: ([en.wikipedia.org]())",
    "*URL*: ([en.wikipedia.org]())",
    "*URL*: ([en.wikipedia.org]())",
    "*URL*: ([en.wikipedia.org]())"
  ],
  "type": "landmark",
  "search_range_meters": 1000,
  "description": "The image depicts a historic fortress situated on a hill, overlooking a cityscape. The fortress features multiple towers and battlements, constructed from stone, giving it a medieval appearance. Below the fortress, there is a collection of buildings with varied architectural styles, including Baroque elements such as domes and spires. The buildings are painted in pastel colors, and the roofs are covered with snow, indicating a winter setting. The city is nestled in a valley, surrounded by hills,",
  "architectural_style": "Medieval and Baroque",
  "search_backends_used": [
    "web"
  ],
  "processing_time_seconds": 41.25574994087219
}
```

### Google Cloud Vision

**Status:** ✅ Success
**Identified:** Mozart Residence (47.8026, 13.0439)
**Confidence:** 64.4%
**Processing Time:** 25.88 seconds

**Details:**
```json
{
  "source": "landmark_detection",
  "landmark_name": "Mozart Residence",
  "coordinates": {
    "latitude": 47.8026282,
    "longitude": 13.043867899999999
  },
  "bounding_poly": [
    {
      "x": 0,
      "y": 0
    },
    {
      "x": 3626,
      "y": 0
    },
    {
      "x": 3626,
      "y": 2432
    },
    {
      "x": 0,
      "y": 2432
    }
  ],
  "context_labels": [
    "Building",
    "City",
    "Urban area",
    "Town",
    "Roof"
  ],
  "context_objects": [
    "Building",
    "Building",
    "Building"
  ],
  "web_entities": [
    {
      "name": "Middle Ages",
      "score": 0.4834499955177307
    },
    {
      "name": "Local government",
      "score": 0.4185999929904938
    },
    {
      "name": "Medieval architecture",
      "score": 0.4128679931163788
    },
    {
      "name": "Architecture",
      "score": 0.4023999869823456
    },
    {
      "name": "Apartment",
      "score": 0.3264663815498352
    }
  ],
  "all_landmarks": [
    {
      "name": "Mozart Residence",
      "score": 0.6440714001655579,
      "location": {
        "lat": 47.8026282,
        "lng": 13.043867899999999
      }
    },
    {
      "name": "Caf\u00e9 Bazar",
      "score": 0.58586186170578,
      "location": {
        "lat": 47.8018,
        "lng": 13.043777799999999
      }
    },
    {
      "name": "Fortress Hohensalzburg",
      "score": 0.5857912302017212,
      "location": {
        "lat": 47.794948299999994,
        "lng": 13.0476583
      }
    }
  ],
  "processing_time_seconds": 25.876396894454956
}
```

---
