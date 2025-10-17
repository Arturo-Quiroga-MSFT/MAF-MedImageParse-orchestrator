# Public DICOM Data Sources

This short reference lists reliable public sources of medical images in DICOM format suitable for development and testing.

- The Cancer Imaging Archive (TCIA)
  - Large repository of cancer imaging collections (CT, MR, PET). Many collections (e.g., LIDC-IDRI, CPTAC) are available as DICOM.
  - Access: https://www.cancerimagingarchive.net/ — use the web UI, NBIA Data Retriever, or the TCIA REST API.
  - Notes: Collections are de-identified for research; check each collection's citation and license.

- LIDC-IDRI (via TCIA)
  - CT scans with lung nodule annotations; useful for lung research and segmentation.
  - Access via TCIA collection "LIDC-IDRI".

- MIMIC-CXR (PhysioNet)
  - Large chest x-ray dataset. Original DICOMs are available under controlled access via PhysioNet.
  - Access requires a PhysioNet account and completion of data use requirements: https://physionet.org/

- Grand Challenge / MICCAI challenge datasets
  - Focused challenge datasets (segmentation, detection) often provide DICOM downloads after registration.
  - Access: https://grand-challenge.org/ and challenge-specific pages.

- Kaggle and other mirrors
  - Some datasets appear on Kaggle; many are distributed as PNG/JPG derivatives. Check dataset metadata for DICOM availability.
  - Access: Kaggle requires an account and API token.

- Small sample DICOM bundles and pydicom examples
  - Use pydicom example datasets or small public DICOM test files when you only need a few files for smoke tests.

Guidance
- For realistic clinical data: TCIA is often the best starting point.
- For controlled datasets (MIMIC): follow the access and training steps before downloading.
- For CI and unit tests: prefer synthetic DICOMs (see the script in `scripts/`) to avoid PHI and external downloads.

If you'd like, I can add a small downloader that uses the TCIA REST API or generate synthetic DICOMs automatically for tests.
