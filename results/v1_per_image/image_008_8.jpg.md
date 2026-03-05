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

## Image 8: 8.jpg

**Path:** `/Users/andreas/Documents/Dokumenter – MacBook Air/UIO/master/Thesis/Project/testing/Image_search/test_images/8.jpg`

<img src="/Users/andreas/Documents/Dokumenter – MacBook Air/UIO/master/Thesis/Project/testing/Image_search/test_images/8.jpg" alt="8.jpg" style="max-width: 400px; max-height: 300px;">

### **WITH METADATA**

**Processing Time:** 48.59 seconds
**Timestamp:** 2026-01-26T18:35:54.718132

**Extracted Metadata:** None (no EXIF data found in image)

### GPT Vision Direct

**Status:** ✅ Success
**Identified:** St. Mary's Basilica, Kraków, Poland
**Confidence:** 90.0%
**Processing Time:** 8.08 seconds

**Details:**
```json
{
  "reasoning": "The image shows a large brick church with two towers of differing heights, which is characteristic of St. Mary's Basilica in Krak\u00f3w. The Gothic architectural style and the location in a busy square further support this identification.",
  "features": [
    "two towers",
    "Gothic architecture",
    "brick construction"
  ],
  "location": "Krak\u00f3w, Poland",
  "type": "landmark",
  "search_range_meters": 1000,
  "raw_response": "```json\n{\n    \"identified\": \"St. Mary's Basilica\",\n    \"location\": \"Krak\u00f3w, Poland\",\n    \"confidence\": 0.9,\n    \"reasoning\": \"The image shows a large brick church with two towers of differing heights, which is characteristic of St. Mary's Basilica in Krak\u00f3w. The Gothic architectural style and the location in a busy square further support this identification.\",\n    \"features\": [\"two towers\", \"Gothic architecture\", \"brick construction\"],\n    \"type\": \"landmark\",\n    \"search_range_meters\": 1000\n}\n```",
  "processing_time_seconds": 8.083547830581665
}
```

### GPT Vision + Search

**Status:** ✅ Success
**Identified:** Maria am Gestade, Vienna, Austria
**Confidence:** 60.0%
**Processing Time:** 40.50 seconds

**Details:**
```json
{
  "reasoning": "The description matches the Gothic architectural style and features such as towers and spires. Maria am Gestade is known for its Gothic architecture and prominent towers, fitting the description well. Although the confidence is moderate due to other potential matches, the specific mention of Maria am Gestade's Gothic style and tower height aligns closely with the description provided.",
  "sources_used": [
    "en.wikipedia.org"
  ],
  "all_candidates": [
    "*Snippet*: The Cathedral Basilica of the Assumption in Covington, Kentucky\u2014nicknamed \"America's Notre Dame\"\u2014is undergoing a $7.8 million, two-year restoration to preserve its French Gothic-inspired ar",
    "*URL*: ([apnews.com]())",
    "*Snippet*: The Church of Sant'Agnese is a Gothic-style, Augustinian church in Lodi, Lombardy, Italy. Celebrated as representing a great moment in Lombard Gothic Architecture, it features a polygonal a",
    "*URL*: ([en.wikipedia.org]())",
    "*Snippet*: Maria am Gestade is a Gothic church in Vienna, Austria, one of the oldest in the city. Built between 1394 and 1414, it is known for its 56-meter high open-work tower and was traditionally u"
  ],
  "type": "landmark",
  "search_range_meters": 1000,
  "description": "The image depicts a large, historic brick church with two prominent towers. The towers are adorned with spires and have a Gothic architectural style, characterized by pointed arches and detailed stonework. The facade features vertical lines of windows and decorative elements, including a large, ornate entrance with a pointed arch and intricate carvings. Adjacent to the church is a smaller building with a Baroque-style facade, featuring decorative gables and ornate window frames. In front of the ",
  "architectural_style": "Gothic",
  "search_backends_used": [
    "web"
  ],
  "processing_time_seconds": 40.50331687927246
}
```

### Google Cloud Vision

**Status:** ✅ Success
**Identified:** Rynek Główny (50.0619, 19.9368)
**Confidence:** 58.2%
**Processing Time:** 23.17 seconds

**Details:**
```json
{
  "source": "landmark_detection",
  "landmark_name": "Rynek G\u0142\u00f3wny",
  "coordinates": {
    "latitude": 50.0618971,
    "longitude": 19.936756
  },
  "bounding_poly": [
    {
      "x": 0,
      "y": 0
    },
    {
      "x": 2433,
      "y": 0
    },
    {
      "x": 2433,
      "y": 3573
    },
    {
      "x": 0,
      "y": 3573
    }
  ],
  "context_labels": [
    "City",
    "Public space",
    "Facade",
    "Landmark",
    "Pedestrian"
  ],
  "context_objects": [
    "Wheel",
    "Clothing",
    "Wheel"
  ],
  "web_entities": [
    {
      "name": "Horse",
      "score": 0.7630459070205688
    },
    {
      "name": "Buggy",
      "score": 0.46268486976623535
    },
    {
      "name": "Building",
      "score": 0.3245045840740204
    },
    {
      "name": "Tourism",
      "score": 0.3001999855041504
    }
  ],
  "all_landmarks": [
    {
      "name": "Rynek G\u0142\u00f3wny",
      "score": 0.5821816325187683,
      "location": {
        "lat": 50.0618971,
        "lng": 19.936756
      }
    },
    {
      "name": "Bugle Tower",
      "score": 0.5120522975921631,
      "location": {
        "lat": 50.061848499999996,
        "lng": 19.9390361
      }
    }
  ],
  "processing_time_seconds": 23.169094800949097
}
```

### **WITHOUT METADATA**

**Processing Time:** 53.05 seconds
**Timestamp:** 2026-01-26T18:36:43.358285

### GPT Vision Direct

**Status:** ✅ Success
**Identified:** St. Mary's Basilica, Kraków, Poland
**Confidence:** 90.0%
**Processing Time:** 10.60 seconds

**Details:**
```json
{
  "reasoning": "The image shows a large brick church with two towers of different heights, which is characteristic of St. Mary's Basilica in Krak\u00f3w. The architectural style and the presence of horse-drawn carriages in the square further support this identification.",
  "features": [
    "brick facade",
    "two towers",
    "horse-drawn carriages"
  ],
  "location": "Krak\u00f3w, Poland",
  "type": "landmark",
  "search_range_meters": 1000,
  "raw_response": "```json\n{\n    \"identified\": \"St. Mary's Basilica\",\n    \"location\": \"Krak\u00f3w, Poland\",\n    \"confidence\": 0.9,\n    \"reasoning\": \"The image shows a large brick church with two towers of different heights, which is characteristic of St. Mary's Basilica in Krak\u00f3w. The architectural style and the presence of horse-drawn carriages in the square further support this identification.\",\n    \"features\": [\"brick facade\", \"two towers\", \"horse-drawn carriages\"],\n    \"type\": \"landmark\",\n    \"search_range_meters\": 1000\n}\n```",
  "processing_time_seconds": 10.602287292480469
}
```

### GPT Vision + Search

**Status:** ✅ Success
**Identified:** Maria am Gestade, Vienna, Austria
**Confidence:** 80.0%
**Processing Time:** 42.45 seconds

**Details:**
```json
{
  "reasoning": "The description matches the Gothic architectural style and features such as towers and spires. Maria am Gestade is a known Gothic church in Vienna, Austria, with a high tower and historical significance, fitting the description of a historic brick church with Gothic elements. The presence of horse-drawn carriages and a statue in an urban square aligns with Vienna's historical ambiance. The other search results either do not match the location or architectural details as closely.",
  "sources_used": [
    "en.wikipedia.org"
  ],
  "all_candidates": [
    "*Snippet:* The Cathedral Basilica of the Assumption in Covington, Kentucky\u2014nicknamed \"America's Notre Dame\"\u2014is undergoing a $7.8 million, two-year restoration to preserve its French Gothic-inspired ar",
    "*URL:* ([apnews.com]())",
    "*Snippet:* The Church of Sant'Agnese is a Gothic-style, Augustinian church in Lodi, Lombardy, Italy. Celebrated as representing a great moment in Lombard Gothic Architecture, it features a polygonal a",
    "*URL:* ([en.wikipedia.org]())",
    "*Snippet:* Maria am Gestade is a Gothic church in Vienna, Austria, one of the oldest in the city. Notable for its 56-meter high open-work tower built between 1419 and 1428, it is recognized from a gre"
  ],
  "type": "landmark",
  "search_range_meters": 1000,
  "description": "The image features a large, historic brick church with two prominent towers. The towers are adorned with spires and decorative elements, showcasing a Gothic architectural style. The facade includes pointed arches and a large, ornate window surrounded by intricate stonework. Adjacent to the church is a statue with a green patina, possibly made of bronze, set on a pedestal. The setting is an urban square with cobblestone pavement, and there are horse-drawn carriages in the foreground, adding to th",
  "architectural_style": "Gothic",
  "search_backends_used": [
    "web"
  ],
  "processing_time_seconds": 42.450884103775024
}
```

### Google Cloud Vision

**Status:** ✅ Success
**Identified:** Rynek Główny (50.0619, 19.9368)
**Confidence:** 58.2%
**Processing Time:** 23.66 seconds

**Details:**
```json
{
  "source": "landmark_detection",
  "landmark_name": "Rynek G\u0142\u00f3wny",
  "coordinates": {
    "latitude": 50.0618971,
    "longitude": 19.936756
  },
  "bounding_poly": [
    {
      "x": 0,
      "y": 0
    },
    {
      "x": 2433,
      "y": 0
    },
    {
      "x": 2433,
      "y": 3573
    },
    {
      "x": 0,
      "y": 3573
    }
  ],
  "context_labels": [
    "City",
    "Public space",
    "Facade",
    "Landmark",
    "Pedestrian"
  ],
  "context_objects": [
    "Wheel",
    "Clothing",
    "Wheel"
  ],
  "web_entities": [
    {
      "name": "Horse",
      "score": 0.7630459070205688
    },
    {
      "name": "Buggy",
      "score": 0.46268486976623535
    },
    {
      "name": "Building",
      "score": 0.3245045840740204
    },
    {
      "name": "Tourism",
      "score": 0.3001999855041504
    }
  ],
  "all_landmarks": [
    {
      "name": "Rynek G\u0142\u00f3wny",
      "score": 0.5819901823997498,
      "location": {
        "lat": 50.0618971,
        "lng": 19.936756
      }
    },
    {
      "name": "Bugle Tower",
      "score": 0.5119684934616089,
      "location": {
        "lat": 50.061848499999996,
        "lng": 19.9390361
      }
    }
  ],
  "processing_time_seconds": 23.657446146011353
}
```

---
