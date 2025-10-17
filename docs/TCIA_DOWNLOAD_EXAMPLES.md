# Programmatic access to TCIA (example patterns)

This document shows safe, programmatic examples for querying The Cancer Imaging Archive (TCIA) REST API to discover collections and series. For bulk DICOM downloads prefer the NBIA Data Retriever desktop tool or the TCIA web UI. This doc provides query examples (safe) and guidance — do not rely on this script to perform automated bulk downloads without reviewing TCIA policies and collection-specific requirements.

Official TCIA resources
- TCIA homepage: https://www.cancerimagingarchive.net/
- TCIA REST API documentation (site): search TCIA REST API or use the services endpoint prefix shown below.

Basic workflow (recommended)
1. Browse TCIA collections on the web UI and accept any collection-specific Data Use Agreements if required.
2. Use the TCIA REST API to list series for the chosen collection; identify SeriesInstanceUID(s) of interest.
3. Use NBIA Data Retriever to download DICOMs for selected series, or request single-series downloads via the API if available for that collection.

Example endpoints (service base)
```
https://services.cancerimagingarchive.net/services/v4/TCIA/query/
```

Common query endpoints
- getCollectionValues — list available collections
- getSeries — list series for a collection (filter by PatientID, StudyInstanceUID, Modality, etc.)

Python example: query collections and series (safe discovery)

The following example shows how to query TCIA for collections and series metadata. It performs HTTP GETs and prints results for inspection. It does not perform bulk image downloads.

```python
import requests
from urllib.parse import urljoin

BASE = 'https://services.cancerimagingarchive.net/services/v4/TCIA/query/'

def get_collections():
    url = urljoin(BASE, 'getCollectionValues')
    resp = requests.get(url, params={'format': 'json'})
    resp.raise_for_status()
    return resp.json()

def get_series(collection_name, limit=50):
    url = urljoin(BASE, 'getSeries')
    params = {'Collection': collection_name, 'format': 'json'}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()

if __name__ == '__main__':
    collections = get_collections()
    print('Found collections (sample):', collections[:10])
    if collections:
        coll = collections[0]
        print(f'Querying series for collection: {coll}')
        series = get_series(coll)
        print(f'Found {len(series)} series (sample 5):')
        for s in series[:5]:
            print(' SeriesInstanceUID:', s.get('SeriesInstanceUID'), ' Modality:', s.get('Modality'))
```

Notes & best practices
- Some TCIA collections are large; prefer using NBIA Data Retriever for robust, resumable downloads.
- Respect any citation or usage instructions per-collection.
- The TCIA API sometimes returns XML or JSON depending on parameters; use the `format=json` parameter where supported.
- If you need programmatic bulk downloads, consider using the manifest download approach and feeding the manifest to NBIA Data Retriever.

If you'd like, I can add a small script `scripts/tcia_example_query.py` that implements the example above and saves a CSV manifest of SeriesInstanceUIDs for your review.
