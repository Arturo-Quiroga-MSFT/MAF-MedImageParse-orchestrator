#!/usr/bin/env python3
"""Generate synthetic DICOM files for testing.

Creates a small set of DICOM files (2D grayscale) with minimal required metadata.
Requires: pydicom, numpy

Usage:
    python scripts/generate_synthetic_dicoms.py --outdir /tmp/synth_dicoms --count 5
"""
from __future__ import annotations

import argparse
import os
import uuid
from pathlib import Path

import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import generate_uid, ExplicitVRLittleEndian
from datetime import datetime


def create_synthetic_dicom(path: Path, rows: int = 128, cols: int = 128) -> Path:
    meta = Dataset()
    meta.MediaStorageSOPClassUID = pydicom.uid.SecondaryCaptureImageStorage
    meta.MediaStorageSOPInstanceUID = generate_uid()
    meta.TransferSyntaxUID = ExplicitVRLittleEndian

    ds = FileDataset(str(path), {}, file_meta=meta, preamble=b"\0" * 128)
    ds.Modality = "OT"
    ds.ContentDate = datetime.now().strftime('%Y%m%d')
    ds.ContentTime = datetime.now().strftime('%H%M%S')

    # Minimal patient/study/series UIDs (synthetic)
    ds.PatientName = "Synthetic^Patient"
    ds.PatientID = str(uuid.uuid4())
    ds.StudyInstanceUID = generate_uid()
    ds.SeriesInstanceUID = generate_uid()
    ds.SOPInstanceUID = generate_uid()
    ds.SOPClassUID = pydicom.uid.SecondaryCaptureImageStorage

    # Image pixel data
    arr = (np.random.rand(rows, cols) * 255).astype(np.uint8)
    ds.Rows = rows
    ds.Columns = cols
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.BitsAllocated = 8
    ds.BitsStored = 8
    ds.HighBit = 7
    ds.PixelRepresentation = 0
    ds.PixelData = arr.tobytes()

    # Save
    path.parent.mkdir(parents=True, exist_ok=True)
    ds.is_little_endian = True
    ds.is_implicit_VR = False
    pydicom.filewriter.dcmwrite(str(path), ds)
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=str, default="./synthetic_dicoms")
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--rows", type=int, default=128)
    parser.add_argument("--cols", type=int, default=128)
    args = parser.parse_args()

    outdir = Path(args.outdir)
    created = []
    for i in range(args.count):
        fname = outdir / f"synthetic_{i+1:03d}.dcm"
        p = create_synthetic_dicom(fname, rows=args.rows, cols=args.cols)
        created.append(p)

    print(f"Created {len(created)} synthetic DICOM files in: {outdir}")
    for p in created:
        print(" -", p)


if __name__ == "__main__":
    main()
