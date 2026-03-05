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

## Image 2: 2.jpg

**Path:** `/Users/andreas/Documents/Dokumenter – MacBook Air/UIO/master/Thesis/Project/testing/Image_search/test_images/2.jpg`

<img src="/Users/andreas/Documents/Dokumenter – MacBook Air/UIO/master/Thesis/Project/testing/Image_search/test_images/2.jpg" alt="2.jpg" style="max-width: 400px; max-height: 300px;">

### **WITH METADATA**

**Processing Time:** 55.08 seconds
**Timestamp:** 2026-01-26T16:08:27.796051

**Extracted Metadata:** None (no EXIF data found in image)

### GPT Vision Direct

**Status:** ✅ Success
**Identified:** Milan Cathedral, Milan, Italy
**Confidence:** 95.0%
**Processing Time:** 5.80 seconds

**Details:**
```json
{
  "reasoning": "The image shows a large Gothic cathedral with intricate spires and detailed stonework, characteristic of the Milan Cathedral, known for its elaborate facade and numerous spires.",
  "features": [
    "Gothic architecture",
    "intricate spires",
    "detailed stonework"
  ],
  "location": "Milan, Italy",
  "type": "landmark",
  "search_range_meters": 1000,
  "raw_response": "```json\n{\n    \"identified\": \"Milan Cathedral\",\n    \"location\": \"Milan, Italy\",\n    \"confidence\": 0.95,\n    \"reasoning\": \"The image shows a large Gothic cathedral with intricate spires and detailed stonework, characteristic of the Milan Cathedral, known for its elaborate facade and numerous spires.\",\n    \"features\": [\"Gothic architecture\", \"intricate spires\", \"detailed stonework\"],\n    \"type\": \"landmark\",\n    \"search_range_meters\": 1000\n}\n```",
  "processing_time_seconds": 5.797594785690308
}
```

### GPT Vision + Search

**Status:** ✅ Success
**Identified:** Milan Cathedral, Milan, Italy
**Confidence:** 95.0%
**Processing Time:** 49.27 seconds

**Details:**
```json
{
  "reasoning": "The description matches the architectural style and features of the Milan Cathedral, known for its Gothic architecture with pointed spires, ornate carvings, and marble facade. Milan Cathedral is a prominent example of Gothic architecture and fits the description of being bathed in warm sunlight, highlighting its intricate details. The search results from architecturaldigest.com and touropia.com likely reference this well-known landmark.",
  "sources_used": [
    "architecturaldigest.com",
    "touropia.com"
  ],
  "all_candidates": [
    "*URL:* ([architecturaldigest.com]())",
    "*URL:* ([architecturaldigest.com]())",
    "*URL:* ([touropia.com]())",
    "*URL:* ([touropia.com]())",
    "*URL:* ([en.wikipedia.org]())"
  ],
  "type": "landmark",
  "search_range_meters": 1000,
  "description": "The image depicts a grand Gothic cathedral bathed in warm sunlight, highlighting its intricate architectural details. The facade is adorned with numerous pointed spires and pinnacles, each intricately carved with ornate designs. Large arched windows are visible, featuring detailed tracery and stained glass. The stone exterior showcases a mix of light and shadow, emphasizing the depth of the carvings and the verticality of the structure. The building's surface is predominantly made of marble, con",
  "architectural_style": "Gothic",
  "search_backends_used": [
    "web"
  ],
  "processing_time_seconds": 49.27207016944885
}
```

### Google Cloud Vision

**Status:** ✅ Success
**Identified:** Spire
**Confidence:** 93.9%
**Processing Time:** 32.15 seconds

**Details:**
```json
{
  "source": "label",
  "all_candidates": [
    {
      "source": "label",
      "name": "Spire",
      "score": 0.9385775923728943
    },
    {
      "source": "label",
      "name": "Place of worship",
      "score": 0.9080190062522888
    },
    {
      "source": "web",
      "name": "Gothic architecture",
      "score": 0.6586238741874695
    },
    {
      "source": "web",
      "name": "Spire",
      "score": 0.5935999751091003
    },
    {
      "source": "web",
      "name": "",
      "score": 0.5935999751091003
    }
  ],
  "web_entities": [
    {
      "name": "Gothic architecture",
      "score": 0.6586238741874695
    },
    {
      "name": "Spire",
      "score": 0.5935999751091003
    },
    {
      "name": "",
      "score": 0.5935999751091003
    },
    {
      "name": "Medieval architecture",
      "score": 0.5629820823669434
    },
    {
      "name": "Architecture",
      "score": 0.5171999931335449
    }
  ],
  "objects": [],
  "labels": [
    {
      "name": "Spire",
      "score": 0.9385775923728943
    },
    {
      "name": "Landmark",
      "score": 0.9299407601356506
    },
    {
      "name": "Place of worship",
      "score": 0.9080190062522888
    },
    {
      "name": "Church",
      "score": 0.9020929932594299
    },
    {
      "name": "Medieval architecture",
      "score": 0.8819015622138977
    }
  ],
  "processing_time_seconds": 32.15498495101929
}
```

### **WITHOUT METADATA**

**Processing Time:** 54.11 seconds
**Timestamp:** 2026-01-26T16:09:22.905550

### GPT Vision Direct

**Status:** ✅ Success
**Identified:** Milan Cathedral, Milan, Italy
**Confidence:** 95.0%
**Processing Time:** 5.42 seconds

**Details:**
```json
{
  "reasoning": "The image shows a large Gothic cathedral with intricate spires and detailed stonework, characteristic of the Milan Cathedral, known for its elaborate facade and numerous spires.",
  "features": [
    "Gothic architecture",
    "intricate spires",
    "detailed stonework"
  ],
  "location": "Milan, Italy",
  "type": "landmark",
  "search_range_meters": 1000,
  "raw_response": "```json\n{\n    \"identified\": \"Milan Cathedral\",\n    \"location\": \"Milan, Italy\",\n    \"confidence\": 0.95,\n    \"reasoning\": \"The image shows a large Gothic cathedral with intricate spires and detailed stonework, characteristic of the Milan Cathedral, known for its elaborate facade and numerous spires.\",\n    \"features\": [\"Gothic architecture\", \"intricate spires\", \"detailed stonework\"],\n    \"type\": \"landmark\",\n    \"search_range_meters\": 1000\n}\n```",
  "processing_time_seconds": 5.419774770736694
}
```

### GPT Vision + Search

**Status:** ✅ Success
**Identified:** Cathedral Basilica of the Assumption, Covington, Kentucky, USA
**Confidence:** 95.0%
**Processing Time:** 48.69 seconds

**Details:**
```json
{
  "reasoning": "The Cathedral Basilica of the Assumption in Covington, Kentucky is described as having a French Gothic-inspired architecture, which matches the Gothic style and features described in the image. The nickname 'America's Notre Dame' suggests a grand and intricate design similar to the description. The search result with the highest score directly mentions this cathedral, making it the most likely identification.",
  "sources_used": [
    "apnews.com"
  ],
  "all_candidates": [
    "*Snippet*: The Cathedral Basilica of the Assumption in Covington, Kentucky\u2014nicknamed \"America's Notre Dame\"\u2014is undergoing a $7.8 million, two-year restoration to preserve its French Gothic-inspired ar",
    "*URL*: ([apnews.com]())",
    "*Snippet*: The Primatial Metropolitan Cathedral of Saint Mary of the Assumption is a Roman Catholic cathedral in Toledo, Spain. It is the seat of the Metropolitan Archdiocese of Toledo and is consider",
    "*URL*: ([en.wikipedia.org]())",
    "*Snippet*: Magdeburg Cathedral, officially called the Cathedral of Saints Maurice and Catherine, is a Lutheran cathedral in Germany and the oldest Gothic cathedral in the country. It is the principal "
  ],
  "type": "landmark",
  "search_range_meters": 1000,
  "description": "The image depicts a grand cathedral with an intricate Gothic architectural style. The facade features numerous pointed spires and pinnacles, characteristic of Gothic design. The exterior is adorned with detailed stone carvings and statues, adding to the elaborate decoration. Large arched windows are visible, some with tracery, and the building is constructed primarily from light-colored stone. The sunlight casts a warm glow on the structure, highlighting its ornate details against a clear blue s",
  "architectural_style": "Gothic",
  "search_backends_used": [
    "web"
  ],
  "processing_time_seconds": 48.68699908256531
}
```

### Google Cloud Vision

**Status:** ✅ Success
**Identified:** Spire
**Confidence:** 93.9%
**Processing Time:** 32.86 seconds

**Details:**
```json
{
  "source": "label",
  "all_candidates": [
    {
      "source": "label",
      "name": "Spire",
      "score": 0.9385775923728943
    },
    {
      "source": "label",
      "name": "Place of worship",
      "score": 0.9080190062522888
    },
    {
      "source": "web",
      "name": "Gothic architecture",
      "score": 0.6641707420349121
    },
    {
      "source": "web",
      "name": "",
      "score": 0.5939000248908997
    },
    {
      "source": "web",
      "name": "Spire",
      "score": 0.5939000248908997
    }
  ],
  "web_entities": [
    {
      "name": "Gothic architecture",
      "score": 0.6641707420349121
    },
    {
      "name": "",
      "score": 0.5939000248908997
    },
    {
      "name": "Spire",
      "score": 0.5939000248908997
    },
    {
      "name": "Medieval architecture",
      "score": 0.583708643913269
    },
    {
      "name": "Architecture",
      "score": 0.5242000222206116
    }
  ],
  "objects": [],
  "labels": [
    {
      "name": "Spire",
      "score": 0.9385775923728943
    },
    {
      "name": "Landmark",
      "score": 0.9299407601356506
    },
    {
      "name": "Place of worship",
      "score": 0.9080190062522888
    },
    {
      "name": "Church",
      "score": 0.9020929932594299
    },
    {
      "name": "Medieval architecture",
      "score": 0.8819015622138977
    }
  ],
  "processing_time_seconds": 32.85999298095703
}
```

---
