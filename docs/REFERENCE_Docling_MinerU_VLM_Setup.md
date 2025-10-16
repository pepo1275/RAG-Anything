# REFERENCE: Docling, MinerU, and VLM Setup Guide

**Last Updated:** 2025-10-16
**Purpose:** Quick reference to avoid re-investigating parser/VLM setup
**Context:** Image deduplication validation revealed confusion about what's installed

---

## 🎯 Quick Answer: What Do We Have?

| Component | Status | What It Does | CLI Works? |
|-----------|--------|--------------|------------|
| **Docling Python Library** | ✅ Installed | Parse Office/HTML documents | ❌ No |
| **MinerU Python Library** | ✅ Installed (v2.1.11) | Parse PDFs | ❌ No (Windows PATH issue) |
| **External VLM (gpt-4o)** | ✅ Active | Describe images via API | N/A |
| **Image Deduplication** | ✅ Working | Reduce VLM calls 30-50% | N/A |
| **Docling VLM (Granite)** | ❌ NOT Used | Local GPU-based vision | N/A |
| **Docker Server** | ❌ NOT Installed | N/A | N/A |

---

## ✅ Current Architecture (OPTIMAL)

```
PDF Document
    ↓
MinerU Parser (Python API) ──► Extract images/text/tables
    ↓
Image Deduplication (Perceptual Hash)
    ├─ Detect duplicates (threshold=5)
    └─ Mark UNIQUE images only
    ↓
For Each UNIQUE Image:
    ├─ Encode to base64
    ├─ Send to OpenAI gpt-4o API ($0.01-0.02/image)
    └─ Get description
    ↓
Store in LightRAG (Knowledge Graph)
```

**Cost Example:**
- 100 images total
- 40 duplicates detected
- 60 unique images × $0.015 = **$0.90** (vs $1.50 without dedup)
- **40% cost savings**

---

## 🔍 Installation Status Checks

### Check Docling (Python Library)
```bash
export PYTHONIOENCODING=utf-8 && python -c "from raganything.parser import DoclingParser; print('Docling OK' if DoclingParser().check_installation() else 'Docling missing')"
```
**Expected:** `Docling OK`

**What This Checks:**
```python
# From parser.py lines 1612-1636
import docling
from docling.document_converter import DocumentConverter
converter = DocumentConverter()  # Can instantiate
```

**Does NOT Check:**
- ❌ Docling CLI (`docling --version`)
- ❌ Docling VLM models
- ❌ Docker server

### Check MinerU (Python Library)
```bash
pip show mineru
```
**Expected:** Version 2.1.11 installed

### Check MinerU CLI (Expected to Fail on Windows)
```bash
mineru --version
```
**Expected:** `'mineru' is not recognized` ← This is NORMAL on Windows

**Why:** MinerU CLI not properly registered in Windows PATH (known issue)

**Workaround:** RAGAnything uses Python API directly, NOT CLI

---

## 🚫 Common Misconceptions

### Misconception 1: "Docling OK" means full VLM support
**Reality:** Only means Python library imported successfully
- ✅ Can parse Office/HTML documents
- ❌ Does NOT mean Granite VLM models are available
- ❌ Does NOT mean Docker server is running

### Misconception 2: Need to fix MinerU CLI
**Reality:** CLI is NOT needed for RAGAnything
- ✅ RAGAnything uses MinerU Python API
- ✅ Bypasses CLI entirely via `subprocess` calls
- ❌ Windows PATH fix unnecessary

### Misconception 3: Should deploy Docling VLM
**Reality:** External VLM (gpt-4o) is BETTER for this use case
- ✅ Higher quality descriptions
- ✅ No GPU requirement
- ✅ Already integrated
- ✅ Image deduplication already reduces costs

---

## 📚 Docling VLM Options (NOT Currently Used)

### When You Would Need Docling VLM

**Use Docling VLM if:**
1. You have local GPU or Apple Silicon M-series
2. You want ZERO API costs (quality trade-off)
3. You need VLM DURING parsing (not post-processing)
4. Document structure analysis is priority (not general vision)

**Don't use Docling VLM if:**
1. ✅ **You want best quality** (gpt-4o is superior)
2. ✅ **No GPU available**
3. ✅ **Current cost is acceptable** ($0.01-0.02/image with 30-50% dedup savings)
4. ✅ **Simple integration preferred**

### Docling VLM Deployment Options

#### Option 1: Docker Server (docling-serve)
```bash
docker run -d --name docling-serve-vlm \
  -p 9000:5001 \
  -e DOCLING_SERVE_ENABLE_UI=true \
  -e HF_HOME=/models/hf \
  -v ~/docling-models:/models \
  quay.io/docling-project/docling-serve:latest
```

**Models Available:**
- `granite-docling-258M-mlx` - Ultra-fast, Apple Silicon (258M params)
- `granite-vision-3.3-2b` - General vision (2B params)

**API Endpoint:**
```bash
curl -X POST "http://localhost:9000/v1/convert/source" \
  -H "Content-Type: application/json" \
  -d '{"options": {"pipeline": "vlm"}, "sources": [...]}'
```

#### Option 2: Python API with Inline VLM
```python
from docling.datamodel.pipeline_options import VlmPipelineOptions
from docling.datamodel.pipeline_options_vlm_model import InlineVlmOptions

pipeline_options = VlmPipelineOptions(
    vlm_options=InlineVlmOptions(
        repo_id="ibm-granite/granite-docling-258M-mlx",
        inference_framework=InferenceFramework.MLX
    )
)
```

**Requires:**
- Model downloads (~500MB-2GB)
- Apple Silicon or CUDA GPU
- `pip install docling[vlm]`

---

## 🛠️ Troubleshooting

### Issue: "MinerU CLI not found"
**Status:** Expected on Windows
**Fix:** None needed - RAGAnything uses Python API

### Issue: "Docling missing"
**Fix:**
```bash
pip install docling
```

### Issue: "VLM quality is poor"
**Check:** Are you using External VLM (gpt-4o) or Docling VLM?
- If using gpt-4o: Should be high quality
- If using Granite: Expected - model is smaller/faster not smarter

### Issue: "Too many VLM API calls"
**Check:** Is image deduplication enabled?
```python
# In processor.py
config.enable_image_deduplication = True  # Default
config.image_dedup_threshold = 5  # Recommended
```

---

## 📊 Performance Comparison

### External VLM (gpt-4o) - CURRENT
- **Quality:** ⭐⭐⭐⭐⭐ Excellent
- **Speed:** ~2-3 sec/image (API latency)
- **Cost:** $0.01-0.02/image
- **GPU:** Not required
- **Integration:** Simple (API key only)

### Docling VLM (Granite-258M)
- **Quality:** ⭐⭐⭐ Good for doc structure
- **Speed:** ~2-3 sec/page (local)
- **Cost:** $0 (model download + GPU)
- **GPU:** Required (or Apple Silicon)
- **Integration:** Complex (Docker or model setup)

### Docling VLM (Granite-3.3-2B)
- **Quality:** ⭐⭐⭐⭐ Good general vision
- **Speed:** ~8-12 sec/page (local)
- **Cost:** $0 (model download + GPU)
- **GPU:** Required (or Apple Silicon)
- **Integration:** Complex (Docker or model setup)

---

## 🎓 Key Learnings

### Learning 1: Don't Assume CLI is Needed
**Context:** MinerU CLI fails on Windows → Assumed blocking issue
**Reality:** RAGAnything uses Python API, CLI unnecessary
**Takeaway:** Check `check_installation()` implementation before assuming requirements

### Learning 2: "Installed" Doesn't Mean "Full Featured"
**Context:** "Docling OK" → Assumed VLM support
**Reality:** Only Python library, no VLM models
**Takeaway:** Clarify what installation checks actually verify

### Learning 3: External VLM is Often Better
**Context:** Considered deploying Docling VLM
**Reality:** gpt-4o superior quality, simpler integration
**Takeaway:** Local VLM only makes sense for specific use cases (GPU available, zero cost requirement)

---

## 📁 Related Files

**Parser Implementation:**
- `raganything/parser.py` - Lines 1612-1636 (Docling check)
- `raganything/parser.py` - Lines 550-736 (MinerU implementation)
- `raganything/parser.py` - Lines 1167-1637 (DoclingParser)

**VLM Integration:**
- `raganything/modalprocessors.py` - Lines 782-970 (Image processor with VLM)
- `raganything/query.py` - Lines 294-348 (VLM-enhanced queries)

**Examples:**
- `examples/raganything_example.py` - Lines 130-180 (gpt-4o vision setup)
- `examples/gemini_example.py` - Lines 128-146 (Gemini vision)

**Documentation:**
- `docs/docling-serve-doc/docling_vlm_investigation.md` - VLM research
- `docs/docling-serve-doc/deployment.md` - Docker deployment
- `docs/docling-serve-doc/docling-serve-update.md` - Granite model updates

---

## 🚀 Quick Commands Reference

### Verify Current Setup
```bash
# Check Docling
export PYTHONIOENCODING=utf-8 && python -c "from raganything.parser import DoclingParser; print('OK' if DoclingParser().check_installation() else 'Missing')"

# Check MinerU Python package
pip show mineru

# Check image deduplication
python -c "from raganything.utils import ImageDeduplicator; print('OK')"
```

### Process Document with Current Setup
```python
from raganything import RAGAnything, RAGAnythingConfig

config = RAGAnythingConfig(
    parser="docling",  # or "mineru" (both use Python API)
    enable_image_deduplication=True,  # ← Reduces VLM calls
    image_dedup_threshold=5  # ← Recommended
)

rag = RAGAnything(
    config=config,
    llm_model_func=llm_func,
    vision_model_func=vision_func,  # ← gpt-4o
    embedding_func=embedding_func
)

await rag.process_document_complete(
    file_path="document.pdf",
    output_dir="./output"
)
```

---

## 📝 Decision Matrix

**Should I deploy Docling VLM?**

| Your Situation | Recommendation |
|----------------|----------------|
| Using gpt-4o, costs acceptable | ❌ Keep current setup |
| Have NVIDIA GPU, want zero cost | ✅ Consider Docling VLM |
| Have Apple Silicon M1+, want speed | ✅ Consider Docling VLM (MLX) |
| No GPU, want quality | ❌ Keep gpt-4o |
| Processing <1000 images/month | ❌ Keep gpt-4o (cost ~$15) |
| Processing >10000 images/month | ✅ Consider Docling VLM (cost savings) |

---

**Status:** 📚 **REFERENCE DOCUMENTED** - Consult this file before re-investigating
**Next Time:** Check this file FIRST before assuming installation issues
