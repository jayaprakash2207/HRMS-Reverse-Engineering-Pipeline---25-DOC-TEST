# Fresh Run — Input Files Go Here

This folder is for the NEW pipeline run.
The original `results/` folder is NOT touched.

## Step 1 — Copy your input files into these exact locations:

```
results_fresh/
├── Business_Analysis/
│   ├── BA_Structural_Scout.md        ← copy here
│   └── BA_Deep_Analyst.md            ← copy here
├── Data_Analysis/
│   ├── DA_Data_Extractor.md          ← copy here
│   └── DA_Data_Reviewer.md           ← copy here
├── Technology_Analysis/
│   ├── TA_Stack_Scout.md             ← copy here
│   └── TA_Deep_Analyst.md            ← copy here
├── Application_Analysis/
│   ├── AA_App_Extractor.md           ← copy here
│   └── AA_Quality_Review.md          ← copy here
│
├── DEEP_SCAN_OUTPUT.md               ← optional (fallback)
└── file_cache.json                   ← optional (fallback)
```

## Step 2 — Run from the project root:

```
python fresh_run.py
```

## Output will appear in:

```
results_fresh/ForwardEngineering_Docs/     ← 20 documents
results_fresh/Foundation_KnowledgeGraph/   ← 5 documents
```

## Notes

- Do NOT copy anything from the old `results/` folder — those are old files
- The 8 files above come from your teammates who ran the full pipeline
- If any of the 8 are missing, place `DEEP_SCAN_OUTPUT.md` here as a fallback
