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

## Image 7: 7.jpg

**Path:** `/Users/andreas/Documents/Dokumenter – MacBook Air/UIO/master/Thesis/Project/testing/Image_search/test_images/7.jpg`

<img src="/Users/andreas/Documents/Dokumenter – MacBook Air/UIO/master/Thesis/Project/testing/Image_search/test_images/7.jpg" alt="7.jpg" style="max-width: 400px; max-height: 300px;">

### **WITH METADATA**

**Processing Time:** 50.43 seconds
**Timestamp:** 2026-01-26T18:06:49.842059

**Extracted Metadata:**
- Camera: Apple iPhone 13 Pro

### GPT Vision Direct

**Status:** ✅ Success
**Identified:** Burums pub, Oslo, Norway
**Confidence:** 80.0%
**Processing Time:** 8.83 seconds

**Details:**
```json
{
  "reasoning": "The image shows a building with a sign for 'Burums', which appears to be a pub or restaurant. The architectural style and street layout suggest a European city, and the presence of tram tracks is consistent with Oslo.",
  "features": [
    "brick facade",
    "pub signage",
    "tram tracks"
  ],
  "location": "Oslo, Norway",
  "type": "building",
  "search_range_meters": 1000,
  "raw_response": "```json\n{\n    \"identified\": \"Burums pub\",\n    \"location\": \"Oslo, Norway\",\n    \"confidence\": 0.8,\n    \"reasoning\": \"The image shows a building with a sign for 'Burums', which appears to be a pub or restaurant. The architectural style and street layout suggest a European city, and the presence of tram tracks is consistent with Oslo.\",\n    \"features\": [\"brick facade\", \"pub signage\", \"tram tracks\"],\n    \"type\": \"building\",\n    \"search_range_meters\": 1000\n}\n```",
  "camera": {
    "make": "Apple",
    "model": "iPhone 13 Pro"
  },
  "processing_time_seconds": 8.825650930404663
}
```

### GPT Vision + Search

**Status:** ✅ Success
**Identified:** Modern building with red brick facade and green awning
**Confidence:** 50.0%
**Processing Time:** 41.60 seconds

**Details:**
```json
{
  "reasoning": "The description matches a modern architectural style with specific features like red brick facade and green awning. However, without specific names or location details from the search results, the identification remains general. The search results do not provide enough information to pinpoint a specific building or location.",
  "sources_used": [],
  "all_candidates": [
    "*URL*: ([en.wikipedia.org]())",
    "*URL*: ([en.wikipedia.org]())",
    "*URL*: ([en.wikipedia.org]())",
    "*URL*: ([en.wikipedia.org]())",
    "*URL*: ([en.wikipedia.org]())"
  ],
  "type": "building",
  "search_range_meters": 1000,
  "description": "The image depicts a multi-story building with a facade made of red brick. The building features several rectangular windows with black frames, arranged in a grid pattern. On the ground floor, there is a storefront with a green awning displaying text and symbols. The awning covers a section of the sidewalk, and there is a glass entrance beneath it. Adjacent to the building is a street with tram tracks and a pedestrian crosswalk. The street is lined with a few trees, and there is a traffic sign vi",
  "architectural_style": "Modern",
  "search_backends_used": [
    "web"
  ],
  "camera": {
    "make": "Apple",
    "model": "iPhone 13 Pro"
  },
  "processing_time_seconds": 41.601783752441406
}
```

### Google Cloud Vision

**Status:** ✅ Success
**Identified:** Wall
**Confidence:** 97.6%
**Processing Time:** 24.11 seconds

**Details:**
```json
{
  "source": "label",
  "all_candidates": [
    {
      "source": "label",
      "name": "Wall",
      "score": 0.9760168194770813
    },
    {
      "source": "label",
      "name": "Window",
      "score": 0.9721292853355408
    },
    {
      "source": "object",
      "name": "Building",
      "score": 0.5541192889213562
    },
    {
      "source": "web",
      "name": "ArchitectureM RIBA Chartered Practice",
      "score": 0.31200000643730164
    },
    {
      "source": "web",
      "name": "Commercial property",
      "score": 0.3043999969959259
    }
  ],
  "web_entities": [
    {
      "name": "ArchitectureM RIBA Chartered Practice",
      "score": 0.31200000643730164
    },
    {
      "name": "Commercial property",
      "score": 0.3043999969959259
    },
    {
      "name": "Commerce",
      "score": 0.3005000054836273
    },
    {
      "name": "Building",
      "score": 0.2800999879837036
    },
    {
      "name": "Architecture",
      "score": 0.27335602045059204
    }
  ],
  "objects": [
    {
      "name": "Building",
      "score": 0.5541192889213562
    }
  ],
  "labels": [
    {
      "name": "Wall",
      "score": 0.9760168194770813
    },
    {
      "name": "Building",
      "score": 0.9746548533439636
    },
    {
      "name": "Window",
      "score": 0.9721292853355408
    },
    {
      "name": "Apartment",
      "score": 0.8332988619804382
    },
    {
      "name": "Daylighting",
      "score": 0.627422571182251
    }
  ],
  "camera": {
    "make": "Apple",
    "model": "iPhone 13 Pro"
  },
  "processing_time_seconds": 24.10544991493225
}
```

### **WITHOUT METADATA**

**Processing Time:** 53.93 seconds
**Timestamp:** 2026-01-26T18:07:40.310827

### GPT Vision Direct

**Status:** ✅ Success
**Identified:** Burums, a building with a restaurant or bar
**Confidence:** 80.0%
**Processing Time:** 9.36 seconds

**Details:**
```json
{
  "reasoning": "The image shows a building with a sign for 'Burums', which appears to be a restaurant or bar. The architectural style is modern with brickwork and large windows.",
  "features": [
    "brick facade",
    "large windows",
    "restaurant sign"
  ],
  "location": null,
  "type": "building",
  "search_range_meters": 1000,
  "raw_response": "```json\n{\n    \"identified\": \"Burums, a building with a restaurant or bar\",\n    \"location\": null,\n    \"confidence\": 0.8,\n    \"reasoning\": \"The image shows a building with a sign for 'Burums', which appears to be a restaurant or bar. The architectural style is modern with brickwork and large windows.\",\n    \"features\": [\"brick facade\", \"large windows\", \"restaurant sign\"],\n    \"type\": \"building\",\n    \"search_range_meters\": 1000\n}\n```",
  "processing_time_seconds": 9.358970165252686
}
```

### GPT Vision + Search

**Status:** ✅ Success
**Identified:** BURUMS storefront in a contemporary building
**Confidence:** 70.0%
**Processing Time:** 44.57 seconds

**Details:**
```json
{
  "reasoning": "The description matches a storefront named 'BURUMS' with specific architectural features such as a red brick facade and green awning. However, there is no specific location or landmark name provided in the search results. The presence of tram tracks and pedestrian crossing suggests an urban setting, but without GPS coordinates or more detailed location information, the identification remains general.",
  "sources_used": [
    "wallpaper.com",
    "en.wikipedia.org"
  ],
  "all_candidates": [
    "*URL*: ([wallpaper.com]())",
    "*URL*: ([wallpaper.com]())",
    "*URL*: ([en.wikipedia.org]())",
    "*URL*: ([en.wikipedia.org]())",
    "*URL*: ([wallpaper.com]())"
  ],
  "type": "building",
  "search_range_meters": 1000,
  "description": "The image depicts a multi-story building with a facade made of red brick. The building features several rectangular windows with black frames, evenly spaced across its surface. On the ground floor, there is a storefront with a green awning displaying the word 'BURUMS' in white letters. The entrance is flanked by decorative elements, including green panels and gold diamond shapes. Above the entrance, there is a sign with a stylized logo. The street in front of the building has tram tracks and a p",
  "architectural_style": "Contemporary",
  "search_backends_used": [
    "web"
  ],
  "processing_time_seconds": 44.56934905052185
}
```

### Google Cloud Vision

**Status:** ✅ Success
**Identified:** Wall
**Confidence:** 97.6%
**Processing Time:** 24.86 seconds

**Details:**
```json
{
  "source": "label",
  "all_candidates": [
    {
      "source": "label",
      "name": "Wall",
      "score": 0.9760168194770813
    },
    {
      "source": "label",
      "name": "Window",
      "score": 0.9721292853355408
    },
    {
      "source": "object",
      "name": "Building",
      "score": 0.5541192889213562
    },
    {
      "source": "web",
      "name": "ArchitectureM RIBA Chartered Practice",
      "score": 0.31200000643730164
    },
    {
      "source": "web",
      "name": "Commercial property",
      "score": 0.3043999969959259
    }
  ],
  "web_entities": [
    {
      "name": "ArchitectureM RIBA Chartered Practice",
      "score": 0.31200000643730164
    },
    {
      "name": "Commercial property",
      "score": 0.3043999969959259
    },
    {
      "name": "Commerce",
      "score": 0.3005000054836273
    },
    {
      "name": "Building",
      "score": 0.2800999879837036
    },
    {
      "name": "Architecture",
      "score": 0.27335602045059204
    }
  ],
  "objects": [
    {
      "name": "Building",
      "score": 0.5541192889213562
    }
  ],
  "labels": [
    {
      "name": "Wall",
      "score": 0.9760168194770813
    },
    {
      "name": "Building",
      "score": 0.9746548533439636
    },
    {
      "name": "Window",
      "score": 0.9721292853355408
    },
    {
      "name": "Apartment",
      "score": 0.8332988619804382
    },
    {
      "name": "Daylighting",
      "score": 0.627422571182251
    }
  ],
  "processing_time_seconds": 24.864657878875732
}
```

---
