"""Simple TCIA query example.

This script queries TCIA for collections and series metadata and can save a small CSV manifest.
It is intended for discovery; it does not perform bulk DICOM downloads.

Usage:
    python scripts/tcia_example_query.py --list-collections
    python scripts/tcia_example_query.py --collection LIDC-IDRI --save-manifest out.csv
"""
from __future__ import annotations

import argparse
import csv
from urllib.parse import urljoin
import requests

BASE = 'https://services.cancerimagingarchive.net/services/v4/TCIA/query/'


def get_collections() -> list:
    url = urljoin(BASE, 'getCollectionValues')
    resp = requests.get(url, params={'format': 'json'})
    resp.raise_for_status()
    return resp.json()


def get_series(collection_name: str) -> list:
    url = urljoin(BASE, 'getSeries')
    params = {'Collection': collection_name, 'format': 'json'}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()


def save_manifest(series_list: list, outpath: str) -> None:
    fieldnames = ['SeriesInstanceUID', 'StudyInstanceUID', 'Modality', 'SeriesDescription']
    with open(outpath, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for s in series_list:
            w.writerow({k: s.get(k, '') for k in fieldnames})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--list-collections', action='store_true')
    parser.add_argument('--collection', type=str)
    parser.add_argument('--save-manifest', type=str)
    args = parser.parse_args()

    if args.list_collections:
        cols = get_collections()
        print('Collections (sample 50):')
        for c in cols[:50]:
            print(' -', c)
        return

    if args.collection:
        series = get_series(args.collection)
        print(f'Found {len(series)} series for collection {args.collection} (sample 10):')
        for s in series[:10]:
            print(' SeriesInstanceUID:', s.get('SeriesInstanceUID'), ' Modality:', s.get('Modality'))
        if args.save_manifest:
            save_manifest(series, args.save_manifest)
            print('Saved manifest to', args.save_manifest)
        return

    parser.print_help()


if __name__ == '__main__':
    main()
