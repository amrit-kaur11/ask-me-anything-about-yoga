#!/bin/bash
set -e

# Debug: show where we are and what files exist
echo "Current directory: $(pwd)"
find . -name "requirements.txt" 2>/dev/null

# Install from wherever requirements.txt is found
pip install -r storage/requirements.txt

python -c "
import os
os.environ['SENTENCE_TRANSFORMERS_HOME'] = '/opt/render/project/src/.cache'
from sentence_transformers import SentenceTransformer
SentenceTransformer('sentence-transformers/paraphrase-MiniLM-L3-v2')
print('Model cached successfully')
"