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

## Image 1: 1.jpg

**Path:** `/Users/andreas/Documents/Dokumenter – MacBook Air/UIO/master/Thesis/Project/testing/Image_search/test_images/1.jpg`

<img src="/Users/andreas/Documents/Dokumenter – MacBook Air/UIO/master/Thesis/Project/testing/Image_search/test_images/1.jpg" alt="1.jpg" style="max-width: 400px; max-height: 300px;">

### **WITH METADATA**

**Processing Time:** 31.68 seconds
**Timestamp:** 2026-01-26T13:29:54.589134

**Extracted Metadata:** None (no EXIF data found in image)

### GPT Vision Direct

**Status:** ✅ Success
**Identified:** Cemetery with mountain backdrop
**Confidence:** 80.0%
**Processing Time:** 5.01 seconds

**Details:**
```json
{
  "reasoning": "The image shows a cemetery with various gravestones and monuments. In the background, there is a distinctive mountain, suggesting a scenic location. The presence of trees and a house indicates a rural or semi-rural setting.",
  "features": [
    "gravestones",
    "monuments",
    "mountain",
    "trees",
    "house"
  ],
  "location": null,
  "type": "landscape",
  "search_range_meters": 1000,
  "raw_response": "```json\n{\n    \"identified\": \"Cemetery with mountain backdrop\",\n    \"location\": null,\n    \"confidence\": 0.8,\n    \"reasoning\": \"The image shows a cemetery with various gravestones and monuments. In the background, there is a distinctive mountain, suggesting a scenic location. The presence of trees and a house indicates a rural or semi-rural setting.\",\n    \"features\": [\"gravestones\", \"monuments\", \"mountain\", \"trees\", \"house\"],\n    \"type\": \"landscape\",\n    \"search_range_meters\": 1000\n}\n```",
  "processing_time_seconds": 5.005910158157349
}
```

### GPT Vision + Search

**Status:** ✅ Success
**Identified:** Lakewood Cemetery, Minneapolis, USA
**Confidence:** 90.0%
**Processing Time:** 26.67 seconds

**Details:**
```json
{
  "reasoning": "The description matches Lakewood Cemetery, which is known for its traditional gravestones and monuments, and is set against a backdrop that includes a mountainous landscape. The presence of a white picket fence and varied gravestone designs aligns with the features of Lakewood Cemetery. The search result with the highest score directly references Lakewood Cemetery, suggesting it is the most likely identification.",
  "sources_used": [
    "lakewoodcemetery.org",
    "en.wikipedia.org"
  ],
  "all_candidates": [
    "*URL*: ([lakewoodcemetery.org]())",
    "*URL*: ([en.wikipedia.org]())",
    "*URL*: ([en.wikipedia.org]())",
    "*URL*: ([en.wikipedia.org]())",
    "*URL*: ([en.wikipedia.org]())"
  ],
  "type": "cemetery",
  "search_range_meters": 1000,
  "description": "The image depicts a cemetery with various gravestones and monuments set against a backdrop of a mountainous landscape. The cemetery is enclosed by a white picket fence, and the gravestones vary in design, including traditional headstones and obelisks. Some monuments have intricate carvings and inscriptions. The setting is lush with green grass and trees, and the sunlight casts a warm glow, suggesting early morning or late afternoon. In the background, there is a distinct mountain range with rugg",
  "architectural_style": "Traditional",
  "search_backends_used": [
    "web"
  ],
  "processing_time_seconds": 26.667818069458008
}
```

### Google Cloud Vision

**Status:** ✅ Success
**Identified:** Landscape
**Confidence:** 92.6%
**Processing Time:** 11.83 seconds

**Details:**
```json
{
  "source": "label",
  "all_candidates": [
    {
      "source": "label",
      "name": "Landscape",
      "score": 0.9257569313049316
    },
    {
      "source": "label",
      "name": "Grave",
      "score": 0.8618772625923157
    },
    {
      "source": "label",
      "name": "Headstone",
      "score": 0.8603689074516296
    },
    {
      "source": "web",
      "name": "Cemetery",
      "score": 0.38938549160957336
    },
    {
      "source": "web",
      "name": "Tree",
      "score": 0.36115968227386475
    }
  ],
  "web_entities": [
    {
      "name": "Cemetery",
      "score": 0.38938549160957336
    },
    {
      "name": "Tree",
      "score": 0.36115968227386475
    },
    {
      "name": "Gravestone",
      "score": 0.3236764967441559
    },
    {
      "name": "M-tree",
      "score": 0.2540999948978424
    }
  ],
  "objects": [],
  "labels": [
    {
      "name": "Landscape",
      "score": 0.9257569313049316
    },
    {
      "name": "Grave",
      "score": 0.8618772625923157
    },
    {
      "name": "Headstone",
      "score": 0.8603689074516296
    },
    {
      "name": "Morning",
      "score": 0.8370806574821472
    },
    {
      "name": "Cemetery",
      "score": 0.8104405403137207
    }
  ],
  "processing_time_seconds": 11.832020282745361
}
```

### **WITHOUT METADATA**

**Processing Time:** 32.04 seconds
**Timestamp:** 2026-01-26T13:30:26.306096

### GPT Vision Direct

**Status:** ✅ Success
**Identified:** Mountain landscape with cemetery in foreground
**Confidence:** 80.0%
**Processing Time:** 6.07 seconds

**Details:**
```json
{
  "reasoning": "The image shows a cemetery with various gravestones and monuments in the foreground, and a distinctive mountain landscape in the background. The style and setting suggest a rural area, possibly in a region known for mountainous terrain.",
  "features": [
    "cemetery",
    "mountains",
    "gravestones",
    "trees"
  ],
  "location": null,
  "type": "landscape",
  "search_range_meters": 1000,
  "raw_response": "```json\n{\n    \"identified\": \"Mountain landscape with cemetery in foreground\",\n    \"location\": null,\n    \"confidence\": 0.8,\n    \"reasoning\": \"The image shows a cemetery with various gravestones and monuments in the foreground, and a distinctive mountain landscape in the background. The style and setting suggest a rural area, possibly in a region known for mountainous terrain.\",\n    \"features\": [\"cemetery\", \"mountains\", \"gravestones\", \"trees\"],\n    \"type\": \"landscape\",\n    \"search_range_meters\": 1000\n}\n```",
  "processing_time_seconds": 6.066365003585815
}
```

### GPT Vision + Search

**Status:** ✅ Success
**Identified:** Green Mount Cemetery, Baltimore, Maryland, USA
**Confidence:** 60.0%
**Processing Time:** 25.97 seconds

**Details:**
```json
{
  "reasoning": "The search results include a specific mention of Green Mount Cemetery, which matches the description of a cemetery with traditional monuments and gravestones. Although the description includes a mountain landscape, which is not typical for Baltimore, the presence of a cemetery with obelisks and traditional headstones surrounded by a fence aligns with Green Mount Cemetery's characteristics. The other search results do not provide specific names or locations that match the description as closely.",
  "sources_used": [
    "greenmountcemetery.com"
  ],
  "all_candidates": [
    "*URL*: ([en.wikipedia.org]())",
    "*URL*: ([en.wikipedia.org]())",
    "*URL*: ([en.wikipedia.org]())",
    "*URL*: ([en.wikipedia.org]())",
    "*URL*: ([greenmountcemetery.com]())"
  ],
  "type": "landmark",
  "search_range_meters": 1000,
  "description": "The image depicts a cemetery in the foreground with various gravestones and monuments. The gravestones vary in design, including traditional headstones and obelisks. The cemetery is surrounded by a white picket fence. In the background, there is a picturesque mountain landscape with rugged peaks, partially obscured by mist or clouds. The setting is lush and green, with trees scattered throughout the area, suggesting a rural or semi-rural environment. The lighting indicates it is either early mor",
  "architectural_style": "Traditional cemetery monuments",
  "search_backends_used": [
    "web"
  ],
  "processing_time_seconds": 25.969848155975342
}
```

### Google Cloud Vision

**Status:** ✅ Success
**Identified:** Landscape
**Confidence:** 92.6%
**Processing Time:** 11.93 seconds

**Details:**
```json
{
  "source": "label",
  "all_candidates": [
    {
      "source": "label",
      "name": "Landscape",
      "score": 0.9257569313049316
    },
    {
      "source": "label",
      "name": "Grave",
      "score": 0.8618772625923157
    },
    {
      "source": "label",
      "name": "Headstone",
      "score": 0.8603689074516296
    },
    {
      "source": "web",
      "name": "Cemetery",
      "score": 0.38938549160957336
    },
    {
      "source": "web",
      "name": "Tree",
      "score": 0.36115968227386475
    }
  ],
  "web_entities": [
    {
      "name": "Cemetery",
      "score": 0.38938549160957336
    },
    {
      "name": "Tree",
      "score": 0.36115968227386475
    },
    {
      "name": "Gravestone",
      "score": 0.3236764967441559
    },
    {
      "name": "M-tree",
      "score": 0.2540999948978424
    }
  ],
  "objects": [],
  "labels": [
    {
      "name": "Landscape",
      "score": 0.9257569313049316
    },
    {
      "name": "Grave",
      "score": 0.8618772625923157
    },
    {
      "name": "Headstone",
      "score": 0.8603689074516296
    },
    {
      "name": "Morning",
      "score": 0.8370806574821472
    },
    {
      "name": "Cemetery",
      "score": 0.8104405403137207
    }
  ],
  "processing_time_seconds": 11.932494878768921
}
```

---
