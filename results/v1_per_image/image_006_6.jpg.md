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

## Image 6: 6.jpg

**Path:** `/Users/andreas/Documents/Dokumenter – MacBook Air/UIO/master/Thesis/Project/testing/Image_search/test_images/6.jpg`

<img src="/Users/andreas/Documents/Dokumenter – MacBook Air/UIO/master/Thesis/Project/testing/Image_search/test_images/6.jpg" alt="6.jpg" style="max-width: 400px; max-height: 300px;">

### **WITH METADATA**

**Processing Time:** 34.80 seconds
**Timestamp:** 2026-01-26T17:50:02.638225

**Extracted Metadata:**
- Camera: Apple iPhone 6

### GPT Vision Direct

**Status:** ✅ Success
**Identified:** Painted Ladies, San Francisco, USA
**Confidence:** 90.0%
**Processing Time:** 7.10 seconds

**Details:**
```json
{
  "reasoning": "The image shows a row of Victorian houses with a city skyline in the background, which is characteristic of the Painted Ladies in San Francisco.",
  "features": [
    "Victorian architecture",
    "city skyline",
    "row of colorful houses"
  ],
  "location": "San Francisco, USA",
  "type": "landmark",
  "search_range_meters": 1000,
  "raw_response": "```json\n{\n    \"identified\": \"Painted Ladies\",\n    \"location\": \"San Francisco, USA\",\n    \"confidence\": 0.9,\n    \"reasoning\": \"The image shows a row of Victorian houses with a city skyline in the background, which is characteristic of the Painted Ladies in San Francisco.\",\n    \"features\": [\"Victorian architecture\", \"city skyline\", \"row of colorful houses\"],\n    \"type\": \"landmark\",\n    \"search_range_meters\": 1000\n}\n```",
  "camera": {
    "make": "Apple",
    "model": "iPhone 6"
  },
  "processing_time_seconds": 7.097351312637329
}
```

### GPT Vision + Search

**Status:** ✅ Success
**Identified:** Painted Ladies, San Francisco, San Francisco, USA
**Confidence:** 95.0%
**Processing Time:** 27.68 seconds

**Details:**
```json
{
  "reasoning": "The description matches the Painted Ladies in San Francisco, which are well-known Victorian-style houses with vibrant colors. The city skyline with a mix of modern and older skyscrapers, including the pyramid-shaped Transamerica Pyramid and the cylindrical Salesforce Tower, further supports this identification.",
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
  "description": "The image features a row of Victorian-style houses, characterized by their ornate facades and vibrant colors. These houses have steeply pitched roofs, decorative trims, and large windows. The background showcases a city skyline with a mix of modern and older skyscrapers. Notable features include a tall, pointed building resembling a pyramid and a distinctive, cylindrical skyscraper. The setting is urban, with a grassy foreground and clear blue sky.",
  "architectural_style": "Victorian",
  "search_backends_used": [
    "web"
  ],
  "camera": {
    "make": "Apple",
    "model": "iPhone 6"
  },
  "processing_time_seconds": 27.68027400970459
}
```

### Google Cloud Vision

**Status:** ✅ Success
**Identified:** The Painted Ladies (37.7763, -122.4328)
**Confidence:** 69.8%
**Processing Time:** 11.78 seconds

**Details:**
```json
{
  "source": "landmark_detection",
  "landmark_name": "The Painted Ladies",
  "coordinates": {
    "latitude": 37.7762528,
    "longitude": -122.4327556
  },
  "bounding_poly": [
    {
      "x": 0,
      "y": 0
    },
    {
      "x": 3264,
      "y": 0
    },
    {
      "x": 3264,
      "y": 2448
    },
    {
      "x": 0,
      "y": 2448
    }
  ],
  "context_labels": [
    "Building",
    "City",
    "Urban area",
    "Residential area",
    "Neighbourhood"
  ],
  "context_objects": [
    "Building"
  ],
  "web_entities": [
    {
      "name": "Skyscraper",
      "score": 0.5545304417610168
    },
    {
      "name": "Apartment",
      "score": 0.4879252314567566
    },
    {
      "name": "Public space",
      "score": 0.48000192642211914
    },
    {
      "name": "High-rise building",
      "score": 0.4112513065338135
    },
    {
      "name": "Campus",
      "score": 0.3507577180862427
    }
  ],
  "all_landmarks": [
    {
      "name": "The Painted Ladies",
      "score": 0.6983581185340881,
      "location": {
        "lat": 37.7762528,
        "lng": -122.4327556
      }
    },
    {
      "name": "Alamo Square",
      "score": 0.6263947486877441,
      "location": {
        "lat": 37.7763694,
        "lng": -122.43481899999999
      }
    },
    {
      "name": "Alamo Square Park",
      "score": 0.5908145308494568,
      "location": {
        "lat": 37.77635477156845,
        "lng": -122.43468327836396
      }
    }
  ],
  "processing_time_seconds": 11.777026653289795
}
```

### **WITHOUT METADATA**

**Processing Time:** 34.10 seconds
**Timestamp:** 2026-01-26T17:50:37.459169

### GPT Vision Direct

**Status:** ✅ Success
**Identified:** Painted Ladies, San Francisco, USA
**Confidence:** 90.0%
**Processing Time:** 6.45 seconds

**Details:**
```json
{
  "reasoning": "The image shows a row of Victorian houses with the San Francisco skyline in the background, which is characteristic of the Painted Ladies in Alamo Square.",
  "features": [
    "Victorian architecture",
    "San Francisco skyline"
  ],
  "location": "San Francisco, USA",
  "type": "landmark",
  "search_range_meters": 1000,
  "raw_response": "```json\n{\n    \"identified\": \"Painted Ladies\",\n    \"location\": \"San Francisco, USA\",\n    \"confidence\": 0.9,\n    \"reasoning\": \"The image shows a row of Victorian houses with the San Francisco skyline in the background, which is characteristic of the Painted Ladies in Alamo Square.\",\n    \"features\": [\"Victorian architecture\", \"San Francisco skyline\"],\n    \"type\": \"landmark\",\n    \"search_range_meters\": 1000\n}\n```",
  "processing_time_seconds": 6.449411869049072
}
```

### GPT Vision + Search

**Status:** ✅ Success
**Identified:** Painted Ladies and Transamerica Pyramid, San Francisco, San Francisco, USA
**Confidence:** 95.0%
**Processing Time:** 27.65 seconds

**Details:**
```json
{
  "reasoning": "The description matches the iconic Painted Ladies, a row of Victorian houses in San Francisco, known for their ornate facades and pastel colors. The distinctive pyramid-shaped skyscraper in the background is likely the Transamerica Pyramid, a well-known feature of the San Francisco skyline. The combination of Victorian architecture and modern skyscrapers fits the urban landscape of San Francisco, especially when viewed from Alamo Square Park.",
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
  "description": "The image features a row of Victorian-style houses in the foreground, characterized by their ornate facades, gabled roofs, and pastel color schemes. Each house displays intricate woodwork and decorative trim, typical of Victorian architecture. In the background, a city skyline is visible, dominated by modern skyscrapers and a distinctive pyramid-shaped building. The skyline includes a mix of architectural styles, with tall glass and steel structures alongside more traditional buildings. The scen",
  "architectural_style": "Victorian",
  "search_backends_used": [
    "web"
  ],
  "processing_time_seconds": 27.653037786483765
}
```

### Google Cloud Vision

**Status:** ✅ Success
**Identified:** The Painted Ladies (37.7763, -122.4328)
**Confidence:** 69.8%
**Processing Time:** 11.45 seconds

**Details:**
```json
{
  "source": "landmark_detection",
  "landmark_name": "The Painted Ladies",
  "coordinates": {
    "latitude": 37.7762528,
    "longitude": -122.4327556
  },
  "bounding_poly": [
    {
      "x": 0,
      "y": 0
    },
    {
      "x": 3264,
      "y": 0
    },
    {
      "x": 3264,
      "y": 2448
    },
    {
      "x": 0,
      "y": 2448
    }
  ],
  "context_labels": [
    "Building",
    "City",
    "Urban area",
    "Residential area",
    "Neighbourhood"
  ],
  "context_objects": [
    "Building"
  ],
  "web_entities": [
    {
      "name": "Skyscraper",
      "score": 0.543498694896698
    },
    {
      "name": "Apartment",
      "score": 0.49648118019104004
    },
    {
      "name": "Public space",
      "score": 0.47593408823013306
    },
    {
      "name": "High-rise building",
      "score": 0.4210430681705475
    },
    {
      "name": "Campus",
      "score": 0.34889939427375793
    }
  ],
  "all_landmarks": [
    {
      "name": "The Painted Ladies",
      "score": 0.6983439922332764,
      "location": {
        "lat": 37.7762528,
        "lng": -122.4327556
      }
    },
    {
      "name": "Alamo Square",
      "score": 0.6261947154998779,
      "location": {
        "lat": 37.7763694,
        "lng": -122.43481899999999
      }
    },
    {
      "name": "Alamo Square Park",
      "score": 0.5907548666000366,
      "location": {
        "lat": 37.77635477156845,
        "lng": -122.43468327836396
      }
    }
  ],
  "processing_time_seconds": 11.454264879226685
}
```

---
