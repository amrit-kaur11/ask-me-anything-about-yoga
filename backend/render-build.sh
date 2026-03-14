#!/bin/bash
pip install -r storage/requirements.txt
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/paraphrase-MiniLM-L3-v2')"
```

Then in Render → Settings → **Build Command**, set:
```
chmod +x render-build.sh && ./render-build.sh
```

This downloads the model once during build and caches it in the image, so startup is instant.

---

**Fix 2: Set HuggingFace cache env var on Render**

In Render → Environment, add:
```
TRANSFORMERS_CACHE=/opt/render/project/src/.cache
HF_HOME=/opt/render/project/src/.cache
SENTENCE_TRANSFORMERS_HOME=/opt/render/project/src/.cache