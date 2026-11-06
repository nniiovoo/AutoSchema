"""Evaluation-only reference receipts and original-source checks; no model calls."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import unicodedata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--paper-manifest', type=Path, required=True,
                        help='Manifest resolving the original three XML files')
    args = parser.parse_args()
    directory = Path(__file__).resolve().parent
    repository = directory.parents[2]
    sys.path.insert(0, str(repository))
    from polymer_cards_lib.sources import load_documents
    receipt = json.loads((directory / 'source-check.json').read_text())
    hash_of = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert hash_of(directory / 'reference.json') == receipt['reference_sha256']
    assert hash_of(directory / 'source-excerpts.json') == receipt['source_excerpts_sha256']
    for item in receipt['frozen_reference_inputs']:
        assert hash_of(repository / item['path']) == item['sha256'], item['path']
    documents = load_documents(args.paper_manifest)
    originals = {c['chunk_id']: c for document in documents for c in document['chunks']}
    actual_hashes = {d['paper_id']: d['source_files'][0]['document_sha256'] for d in documents}
    for item in receipt['original_document_hashes_verified']:
        assert actual_hashes[item['paper_id']] == item['document_sha256']
    excerpts = json.loads((directory / 'source-excerpts.json').read_text())['chunks']
    for excerpt in excerpts:
        original = originals[excerpt['chunk_id']]
        for key in ('text', 'paper_id', 'source_part', 'locator', 'document_sha256', 'text_transformations'):
            assert excerpt[key] == original[key], (excerpt['chunk_id'], key)
    normal = lambda value: ' '.join(unicodedata.normalize('NFC', value).split())
    quote_count = 0

    def visit(value):
        nonlocal quote_count
        if isinstance(value, dict):
            if 'quote' in value and 'chunk_id' in value:
                assert normal(value['quote']) in normal(originals[value['chunk_id']]['text'])
                quote_count += 1
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    reference = json.loads((directory / 'reference.json').read_text())
    visit(reference)
    assert len(reference['measurement_expectations']) == receipt['measurement_cases']
    assert len(reference['guo_identities']) == receipt['identity_cases']
    assert len(reference['conflict_expectations']) == receipt['conflict_cases']
    print(json.dumps({'reference_hash_verified': True, 'frozen_reference_inputs_unchanged': True,
                      'original_xml_hashes_verified': len(documents),
                      'selected_chunks_match_fresh_original_conversion': len(excerpts),
                      'explicit_quote_spans_matched': quote_count,
                      'measurement_cases': len(reference['measurement_expectations']),
                      'identity_cases': len(reference['guo_identities']),
                      'conflict_cases': len(reference['conflict_expectations']),
                      'model_calls': 0}, indent=2))


if __name__ == '__main__':
    main()
