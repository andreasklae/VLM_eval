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

## Image 5: 5.jpg

**Path:** `/Users/andreas/Documents/Dokumenter – MacBook Air/UIO/master/Thesis/Project/testing/Image_search/test_images/5.jpg`

<img src="/Users/andreas/Documents/Dokumenter – MacBook Air/UIO/master/Thesis/Project/testing/Image_search/test_images/5.jpg" alt="5.jpg" style="max-width: 400px; max-height: 300px;">

### **WITH METADATA**

**Processing Time:** 94.84 seconds
**Timestamp:** 2026-01-26T17:15:37.690805

**Extracted Metadata:**
- Camera: FUJIFILM X-T30 II

### GPT Vision Direct

**Status:** ✅ Success
**Identified:** Colorful hanging decorations in an urban area
**Confidence:** 70.0%
**Processing Time:** 8.35 seconds

**Details:**
```json
{
  "reasoning": "The image shows colorful decorations hanging above a street, with brick buildings in the background. The decorations appear to be made of fabric or similar materials, and are strung along wires. This suggests a festive or artistic installation in an urban environment.",
  "features": [
    "colorful hanging decorations",
    "brick buildings",
    "urban street"
  ],
  "location": null,
  "type": "art installation",
  "search_range_meters": 1000,
  "raw_response": "```json\n{\n    \"identified\": \"Colorful hanging decorations in an urban area\",\n    \"location\": null,\n    \"confidence\": 0.7,\n    \"reasoning\": \"The image shows colorful decorations hanging above a street, with brick buildings in the background. The decorations appear to be made of fabric or similar materials, and are strung along wires. This suggests a festive or artistic installation in an urban environment.\",\n    \"features\": [\"colorful hanging decorations\", \"brick buildings\", \"urban street\"],\n    \"type\": \"art installation\",\n    \"search_range_meters\": 1000\n}\n```",
  "camera": {
    "make": "FUJIFILM",
    "model": "X-T30 II"
  },
  "processing_time_seconds": 8.349700927734375
}
```

### GPT Vision + Search

**Status:** ✅ Success
**Identified:** Carnaby Street, London, London, United Kingdom
**Confidence:** 85.0%
**Processing Time:** 86.48 seconds

**Details:**
```json
{
  "reasoning": "The description matches Carnaby Street in London, known for its vibrant decorations and festive atmosphere. The street is characterized by its narrow layout, industrial-style buildings, and modern elements, fitting the description of red brick buildings with glass structures. Carnaby Street is famous for its colorful decorations, especially during festive seasons, which often include tassels or pom-poms. The presence of strings of lights further supports this identification.",
  "sources_used": [
    "en.wikipedia.org",
    "interface.com"
  ],
  "all_candidates": [
    "*URL*: ([en.wikipedia.org]())",
    "*URL*: ([en.wikipedia.org]())",
    "*URL*: ([en.wikipedia.org]())",
    "*URL*: ([interface.com]())",
    "*URL*: ([etsy.com]())"
  ],
  "type": "landmark",
  "search_range_meters": 1000,
  "description": "The image depicts a vibrant urban scene with colorful hanging decorations. These decorations are made of fluffy materials and are suspended across the street, resembling tassels or pom-poms in various colors including blue, pink, red, and yellow. The setting is a narrow street flanked by industrial-style buildings constructed with red brick and large glass windows. Above, strings of lights are visible, adding to the festive atmosphere. The background includes modern architectural elements like m",
  "architectural_style": "Industrial with modern elements",
  "search_backends_used": [
    "web"
  ],
  "camera": {
    "make": "FUJIFILM",
    "model": "X-T30 II"
  },
  "processing_time_seconds": 86.47996425628662
}
```

### Google Cloud Vision

**Status:** ❌ Failed
**Error:** API error: Bad image data.

### **WITHOUT METADATA**

**Processing Time:** 95.03 seconds
**Timestamp:** 2026-01-26T17:17:12.580380

### GPT Vision Direct

**Status:** ✅ Success
**Identified:** Brick industrial-style building with colorful hanging decorations
**Confidence:** 70.0%
**Processing Time:** 7.72 seconds

**Details:**
```json
{
  "reasoning": "The image shows a brick building with large windows, typical of industrial architecture. The colorful decorations hanging across the street suggest a festive or artistic installation.",
  "features": [
    "brick facade",
    "large windows",
    "colorful hanging decorations"
  ],
  "location": null,
  "type": "building",
  "search_range_meters": 1000,
  "raw_response": "```json\n{\n    \"identified\": \"Brick industrial-style building with colorful hanging decorations\",\n    \"location\": null,\n    \"confidence\": 0.7,\n    \"reasoning\": \"The image shows a brick building with large windows, typical of industrial architecture. The colorful decorations hanging across the street suggest a festive or artistic installation.\",\n    \"features\": [\"brick facade\", \"large windows\", \"colorful hanging decorations\"],\n    \"type\": \"building\",\n    \"search_range_meters\": 1000\n}\n```",
  "processing_time_seconds": 7.722700119018555
}
```

### GPT Vision + Search

**Status:** ✅ Success
**Identified:** Umbrella Sky Project in Águeda, Portugal, Águeda, Portugal
**Confidence:** 95.0%
**Processing Time:** 87.30 seconds

**Details:**
```json
{
  "reasoning": "The description matches the Umbrella Sky Project, known for its colorful installations suspended above pedestrian walkways. The industrial aesthetic with brick buildings and arched glass structures aligns with the urban setting in \u00c1gueda, Portugal, where this project is prominently featured. The vibrant and festive atmosphere described is characteristic of this installation.",
  "sources_used": [
    "designboom.com",
    "en.wikipedia.org"
  ],
  "all_candidates": [
    "*URL*: ([designboom.com]())",
    "*URL*: ([en.wikipedia.org]())",
    "*URL*: ([en.wikipedia.org]())",
    "*URL*: ([en.wikipedia.org]())",
    "*URL*: ([en.wikipedia.org]())"
  ],
  "type": "art installation",
  "search_range_meters": 1000,
  "description": "The image depicts a vibrant urban scene with colorful hanging installations suspended above a pedestrian walkway. These installations consist of clusters of fabric or yarn in various colors, including blue, pink, red, and orange. They are strung along wires, creating a festive and artistic atmosphere. The background features a brick building with large windows and an arched glass structure, suggesting an industrial or renovated warehouse aesthetic. The setting is lively, with people walking alon",
  "architectural_style": "Industrial",
  "search_backends_used": [
    "web"
  ],
  "processing_time_seconds": 87.30142617225647
}
```

### Google Cloud Vision

**Status:** ❌ Failed
**Error:** API error: Bad image data.

---
