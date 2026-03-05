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

## Image 9: 9.jpg

**Path:** `/Users/andreas/Documents/Dokumenter – MacBook Air/UIO/master/Thesis/Project/testing/Image_search/test_images/9.jpg`

<img src="/Users/andreas/Documents/Dokumenter – MacBook Air/UIO/master/Thesis/Project/testing/Image_search/test_images/9.jpg" alt="9.jpg" style="max-width: 400px; max-height: 300px;">

### **WITH METADATA**

**Processing Time:** 28.63 seconds
**Timestamp:** 2026-01-26T18:49:54.221520

**Extracted Metadata:**
- Camera: Apple iPhone 6

### GPT Vision Direct

**Status:** ✅ Success
**Identified:** Unconditional Surrender statue, San Diego, USA
**Confidence:** 90.0%
**Processing Time:** 5.46 seconds

**Details:**
```json
{
  "reasoning": "The statue depicts a sailor kissing a nurse, reminiscent of the famous V-J Day photograph. It is located near the USS Midway Museum in San Diego.",
  "features": [
    "sailor and nurse figures",
    "large scale",
    "waterfront location"
  ],
  "location": "San Diego, USA",
  "type": "statue",
  "search_range_meters": 1000,
  "raw_response": "```json\n{\n    \"identified\": \"Unconditional Surrender statue\",\n    \"location\": \"San Diego, USA\",\n    \"confidence\": 0.9,\n    \"reasoning\": \"The statue depicts a sailor kissing a nurse, reminiscent of the famous V-J Day photograph. It is located near the USS Midway Museum in San Diego.\",\n    \"features\": [\"sailor and nurse figures\", \"large scale\", \"waterfront location\"],\n    \"type\": \"statue\",\n    \"search_range_meters\": 1000\n}\n```",
  "camera": {
    "make": "Apple",
    "model": "iPhone 6"
  },
  "processing_time_seconds": 5.461458921432495
}
```

### GPT Vision + Search

**Status:** ✅ Success
**Identified:** Unconditional Surrender sculpture, San Diego, USA
**Confidence:** 95.0%
**Processing Time:** 23.16 seconds

**Details:**
```json
{
  "reasoning": "The description matches the 'Unconditional Surrender' sculpture, which depicts a sailor kissing a nurse, inspired by the famous photograph taken on V-J Day in Times Square. The sculpture is known for its dynamic pose and detailed clothing, and it is set on a circular pedestal. The search results from reputable sources confirm this identification, and the sculpture is located in San Diego, USA.",
  "sources_used": [
    "cbsnews.com",
    "en.wikipedia.org"
  ],
  "all_candidates": [
    "*URL*: ([cbsnews.com]())",
    "*URL*: ([en.wikipedia.org]())",
    "*URL*: ([sbs.com.au]())",
    "*URL*: ([statue.com]())",
    "*URL*: ([time.com]())"
  ],
  "type": "statue",
  "search_range_meters": 1000,
  "description": "The image features a large sculpture depicting a sailor passionately kissing a nurse. The sailor is dressed in a dark navy uniform, while the nurse is wearing a white dress and cap. The sculpture is highly detailed, capturing the folds in the clothing and the dynamic pose of the figures. The nurse is slightly bent backward, supported by the sailor's embrace, and her right foot is lifted off the ground, adding to the sense of movement. The sculpture is set on a circular pedestal with engraved tex",
  "architectural_style": "Realist",
  "search_backends_used": [
    "web"
  ],
  "camera": {
    "make": "Apple",
    "model": "iPhone 6"
  },
  "processing_time_seconds": 23.163334846496582
}
```

### Google Cloud Vision

**Status:** ✅ Success
**Identified:** Uss Midway Museum (32.7137, -117.1751)
**Confidence:** 61.9%
**Processing Time:** 9.09 seconds

**Details:**
```json
{
  "source": "landmark_detection",
  "landmark_name": "Uss Midway Museum",
  "coordinates": {
    "latitude": 32.7137398,
    "longitude": -117.17512649999999
  },
  "bounding_poly": [
    {
      "x": 0,
      "y": 0
    },
    {
      "x": 2448,
      "y": 0
    },
    {
      "x": 2448,
      "y": 3264
    },
    {
      "x": 0,
      "y": 3264
    }
  ],
  "context_labels": [
    "Sculpture",
    "Leisure",
    "Monument",
    "Romance",
    "Love"
  ],
  "context_objects": [
    "Shoe",
    "Person",
    "Shoe"
  ],
  "web_entities": [
    {
      "name": "Lil' Eddie",
      "score": 10.527000427246094
    },
    {
      "name": "Unconditional Surrender",
      "score": 1.0864500999450684
    },
    {
      "name": "Statue",
      "score": 0.8790589570999146
    },
    {
      "name": "V-J Day in Times Square",
      "score": 0.8568000197410583
    },
    {
      "name": "Photograph",
      "score": 0.5853000283241272
    }
  ],
  "all_landmarks": [
    {
      "name": "Uss Midway Museum",
      "score": 0.6190473437309265,
      "location": {
        "lat": 32.7137398,
        "lng": -117.17512649999999
      }
    },
    {
      "name": "Top Of The Market - San Diego",
      "score": 0.6080892086029053,
      "location": {
        "lat": 32.712463299999996,
        "lng": -117.17549740000001
      }
    },
    {
      "name": "The Fish Market - San Diego",
      "score": 0.57218337059021,
      "location": {
        "lat": 32.712301599999996,
        "lng": -117.17559920000001
      }
    },
    {
      "name": "National Salute To Bob Hope And The Military",
      "score": 0.5661230683326721,
      "location": {
        "lat": 32.7126953,
        "lng": -117.17551669999997
      }
    },
    {
      "name": "Tuna Harbor Park",
      "score": 0.5608280897140503,
      "location": {
        "lat": 32.712750400000004,
        "lng": -117.1746646
      }
    }
  ],
  "processing_time_seconds": 9.085941076278687
}
```

### **WITHOUT METADATA**

**Processing Time:** 28.76 seconds
**Timestamp:** 2026-01-26T18:50:22.887321

### GPT Vision Direct

**Status:** ✅ Success
**Identified:** Unconditional Surrender statue, San Diego, USA
**Confidence:** 90.0%
**Processing Time:** 5.88 seconds

**Details:**
```json
{
  "reasoning": "The statue depicts a sailor kissing a nurse, reminiscent of the famous photograph taken on V-J Day in Times Square. The presence of a naval ship in the background suggests a waterfront location, consistent with San Diego.",
  "features": [
    "sailor and nurse figures",
    "naval ship in background",
    "waterfront setting"
  ],
  "location": "San Diego, USA",
  "type": "statue",
  "search_range_meters": 1000,
  "raw_response": "```json\n{\n    \"identified\": \"Unconditional Surrender statue\",\n    \"location\": \"San Diego, USA\",\n    \"confidence\": 0.9,\n    \"reasoning\": \"The statue depicts a sailor kissing a nurse, reminiscent of the famous photograph taken on V-J Day in Times Square. The presence of a naval ship in the background suggests a waterfront location, consistent with San Diego.\",\n    \"features\": [\"sailor and nurse figures\", \"naval ship in background\", \"waterfront setting\"],\n    \"type\": \"statue\",\n    \"search_range_meters\": 1000\n}\n```",
  "processing_time_seconds": 5.881603002548218
}
```

### GPT Vision + Search

**Status:** ✅ Success
**Identified:** Unconditional Surrender statue, San Diego, California
**Confidence:** 100.0%
**Processing Time:** 22.88 seconds

**Details:**
```json
{
  "reasoning": "The description matches the 'Unconditional Surrender' statue, which depicts a sailor and nurse embracing in a kiss. The statue is located in San Diego's Tuna Harbor Park, near a naval ship, fitting the coastal setting described. The statue's large scale and specific depiction of a sailor and nurse are consistent with the search results for San Diego.",
  "sources_used": [
    "web"
  ],
  "all_candidates": [
    "**San Diego, California**: A 25-foot-tall version of the statue was installed in San Diego's Tuna Harbor Park. In 2013, it was replaced with a bronze version and relocated to the Port of San Diego\u2019s G",
    "**Sarasota, Florida**: A 26-foot-tall replica was unveiled in 2012 at Sarasota's Bayfront Park. In April 2012, the statue was damaged when a driver crashed into it. ([baynews9.com]())",
    "**New York City, New York**: A bronze sculpture of Frances Xavier Cabrini, a nurse and missionary, was unveiled in Battery Park City in 2020. While not directly depicting the V-J Day kiss, it honors t",
    "**Washington, D.C.**: The Vietnam Women's Memorial, dedicated in 1993, features three uniformed women assisting a wounded soldier, symbolizing the support and caregiving roles of women during the Viet",
    "**Copenhagen, Denmark**: The Humane Nurse statue, unveiled in 1941, depicts a nurse holding an infant, honoring the contributions of nurses. ([en.wikipedia.org]())"
  ],
  "type": "statue",
  "search_range_meters": 1000,
  "description": "The image depicts a large statue of a sailor and a nurse embracing in a kiss. The sailor is wearing a dark navy uniform, including a cap, while the nurse is dressed in a white uniform with a skirt and white shoes. The statue is positioned on a circular pedestal, surrounded by a paved area with engraved text. In the background, there is a large naval ship docked in the water, suggesting a coastal setting.",
  "architectural_style": "Modern",
  "search_backends_used": [
    "web"
  ],
  "processing_time_seconds": 22.875338077545166
}
```

### Google Cloud Vision

**Status:** ✅ Success
**Identified:** Uss Midway Museum (32.7137, -117.1751)
**Confidence:** 61.9%
**Processing Time:** 8.83 seconds

**Details:**
```json
{
  "source": "landmark_detection",
  "landmark_name": "Uss Midway Museum",
  "coordinates": {
    "latitude": 32.7137398,
    "longitude": -117.17512649999999
  },
  "bounding_poly": [
    {
      "x": 0,
      "y": 0
    },
    {
      "x": 2448,
      "y": 0
    },
    {
      "x": 2448,
      "y": 3264
    },
    {
      "x": 0,
      "y": 3264
    }
  ],
  "context_labels": [
    "Sculpture",
    "Leisure",
    "Monument",
    "Romance",
    "Love"
  ],
  "context_objects": [
    "Shoe",
    "Person",
    "Shoe"
  ],
  "web_entities": [
    {
      "name": "John Seward Johnson II",
      "score": 9.857999801635742
    },
    {
      "name": "Unconditional Surrender",
      "score": 1.0666499137878418
    },
    {
      "name": "Statue",
      "score": 0.8816249966621399
    },
    {
      "name": "V-J Day in Times Square",
      "score": 0.6775500178337097
    },
    {
      "name": "Sculpture",
      "score": 0.5885000228881836
    }
  ],
  "all_landmarks": [
    {
      "name": "Uss Midway Museum",
      "score": 0.6190473437309265,
      "location": {
        "lat": 32.7137398,
        "lng": -117.17512649999999
      }
    },
    {
      "name": "Top Of The Market - San Diego",
      "score": 0.6080892086029053,
      "location": {
        "lat": 32.712463299999996,
        "lng": -117.17549740000001
      }
    },
    {
      "name": "The Fish Market - San Diego",
      "score": 0.57218337059021,
      "location": {
        "lat": 32.712301599999996,
        "lng": -117.17559920000001
      }
    },
    {
      "name": "National Salute To Bob Hope And The Military",
      "score": 0.5661230683326721,
      "location": {
        "lat": 32.7126953,
        "lng": -117.17551669999997
      }
    },
    {
      "name": "Tuna Harbor Park",
      "score": 0.5608280897140503,
      "location": {
        "lat": 32.712750400000004,
        "lng": -117.1746646
      }
    }
  ],
  "processing_time_seconds": 8.8298978805542
}
```

---
