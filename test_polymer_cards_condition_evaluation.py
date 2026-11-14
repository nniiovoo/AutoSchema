"""Stricter optional condition/unit/conflict checks leave frozen references intact."""
from copy import deepcopy
import unittest

from polymer_cards_lib.evaluation import evaluate_run
from test_polymer_cards_evaluation import evidence, fixture


def conflict_fixture():
    run, _ = fixture()
    card = run['results'][0]['cards'][0]
    card['specimens'] = [
        {'specimen_id': 'method-film', 'label': 'P1 film in Methods', 'evidence': [evidence('method', 'P1 film has thickness 12 μm.')]},
        {'specimen_id': 'result-film', 'label': 'P1 film in Results', 'evidence': [evidence('result', 'P1 film has thickness about 15 μm.')]},
    ]
    props = []
    for sid, value, source in [('method-film', '12', 'method'), ('result-film', 'about 15', 'result')]:
        props.append({'entity_id': 'p1', 'property': 'membrane thickness', 'value': value, 'unit': 'μm',
                      'specimen_id': sid, 'conditions': [], 'evidence': [evidence(source)],
                      'specimen_evidence': [evidence(source)]})
    card['properties'] = {'status': 'conflicting', 'items': props, 'conflicts': [
        {'property': 'membrane thickness', 'description': 'Unresolved Methods/Results discrepancy; sample equivalence is unclear.',
         'specimen_ids': ['method-film', 'result-film'], 'evidence': [evidence('method'), evidence('result')]}]}
    reference = {'conflict_expectations': [{'claim_id': 'film-thickness', 'paper_id': 'paper-a',
        'entity_labels': ['P1'], 'property_terms': ['thickness'],
        'evidence_chunk_ids_required': ['method', 'result'],
        'description_require_any': ['unresolved', 'unclear'],
        'description_forbid': ['resolved by swelling'],
        'observations': [{'value': '12', 'unit': 'μm', 'unit_field_required': True,
                          'specimen_require_any': ['Methods'], 'evidence_chunk_ids_required': ['method']},
                         {'value': 'about 15', 'unit': 'μm', 'unit_field_required': True,
                          'specimen_require_any': ['Results'], 'evidence_chunk_ids_required': ['result']}]}]}
    return run, reference


class PolymerCardConditionEvaluationTests(unittest.TestCase):
    def test_optional_unit_requirement_catches_embedded_percent_without_changing_old_reference(self):
        run, reference = fixture()
        prop = run['results'][0]['cards'][0]['properties']['items'][0]
        prop.update(value='93% ± 3%', unit=None)
        reference['measurement_expectations'][0].update(value='93% ± 3%', unit='%')
        self.assertEqual('matched_focused_expectation', evaluate_run(run, reference)['measurements'][0]['status'])
        reference['measurement_expectations'][0]['unit_field_required'] = True
        item = evaluate_run(run, reference)['measurements'][0]
        self.assertEqual('needs_source_review', item['status'])
        self.assertIn('required_unit_field_missing', item['candidates'][0]['reasons'])
        prop['unit'] = '%'
        self.assertEqual('matched_focused_expectation', evaluate_run(run, reference)['measurements'][0]['status'])

    def test_dimensionless_unit_null_remains_legal_under_strict_field_requirement(self):
        run, reference = fixture()
        run['results'][0]['cards'][0]['properties']['items'][0].update(value='0.81', unit=None)
        reference['measurement_expectations'][0].update(value='0.81', unit=None, unit_field_required=True)
        self.assertEqual('matched_focused_expectation', evaluate_run(run, reference)['measurements'][0]['status'])

    def test_conflict_pair_and_note_match_without_mutation_or_resolving_source(self):
        run, reference = conflict_fixture()
        old_run, old_ref = deepcopy(run), deepcopy(reference)
        result = evaluate_run(run, reference)
        self.assertEqual('matched_focused_expectation', result['conflicts'][0]['status'])
        self.assertEqual(old_run, run)
        self.assertEqual(old_ref, reference)
        self.assertNotIn('accuracy', result)

    def test_conflicting_status_alone_does_not_establish_source_discrepancy(self):
        run, reference = conflict_fixture()
        card = run['results'][0]['cards'][0]
        for mutation in ('no-note', 'wrong-topic', 'one-source', 'missing-value', 'missing-unit', 'no-context', 'wrong-observation-source', 'unlinked-specimen', 'resolved', 'not-conflicting'):
            with self.subTest(mutation=mutation):
                candidate = deepcopy(run)
                c = candidate['results'][0]['cards'][0]
                conflict = c['properties']['conflicts'][0]
                if mutation == 'no-note': c['properties']['conflicts'] = []
                elif mutation == 'wrong-topic': conflict['property'] = 'unrelated thermal transition'
                elif mutation == 'one-source': conflict['evidence'] = [evidence('method')]
                elif mutation == 'missing-value': c['properties']['items'].pop()
                elif mutation == 'missing-unit': c['properties']['items'][1]['unit'] = None
                elif mutation == 'no-context': c['properties']['items'][1]['evidence'] = [evidence('method')]; c['properties']['items'][1]['specimen_evidence'] = [evidence('method')]; c['specimens'][1]['evidence'] = [evidence('method')]
                elif mutation == 'wrong-observation-source': c['properties']['items'][1]['evidence'] = [evidence('method')]
                elif mutation == 'unlinked-specimen': conflict['specimen_ids'] = ['method-film']
                elif mutation == 'resolved': conflict['description'] = 'Resolved by swelling. Unclear original sample state.'
                elif mutation == 'not-conflicting': c['properties']['status'] = 'reported'
                self.assertNotEqual('matched_focused_expectation', evaluate_run(candidate, reference)['conflicts'][0]['status'])

    def test_other_material_or_unmatched_quotes_cannot_supply_conflict(self):
        for mutation in ('parent', 'quote'):
            with self.subTest(mutation=mutation):
                run, reference = conflict_fixture()
                card = run['results'][0]['cards'][0]
                if mutation == 'parent': card['name'] = 'P2'; card['identity_evidence'] = [evidence(quote='Polymer P2 was synthesized')]
                else: card['properties']['conflicts'][0]['evidence'][0]['evidence_status'] = 'unmatched'
                self.assertNotEqual('matched_focused_expectation', evaluate_run(run, reference)['conflicts'][0]['status'])

    def test_two_observations_cannot_reuse_one_ambiguous_value(self):
        run, reference = conflict_fixture()
        reference['conflict_expectations'][0]['observations'][1] = deepcopy(reference['conflict_expectations'][0]['observations'][0])
        with self.assertRaises(ValueError): evaluate_run(run, reference)

    def test_one_retained_item_cannot_satisfy_two_conflict_observations(self):
        run, reference = conflict_fixture()
        card = run['results'][0]['cards'][0]
        both = card['properties']['items'][0]
        both['evidence'] = [evidence('method'), evidence('result')]
        card['properties']['items'] = [both]
        for observation in reference['conflict_expectations'][0]['observations']:
            observation.update(value='12', specimen_require_any=['film'])
        result = evaluate_run(run, reference)['conflicts'][0]
        self.assertEqual('needs_source_review', result['status'])
        self.assertEqual([True, False], [o['matched'] for o in result['candidates'][0]['observations']])
        # A second, distinct item that fits only the first observation forces reassignment.
        method_only = deepcopy(both)
        method_only.update(specimen_id='result-film', evidence=[evidence('method')])
        card['properties']['items'].append(method_only)
        result = evaluate_run(run, reference)['conflicts'][0]
        self.assertEqual('matched_focused_expectation', result['status'])
        self.assertEqual([True, True], [o['matched'] for o in result['candidates'][0]['observations']])

    def test_negated_additive_label_fails_in_any_position_or_dash_spelling(self):
        for label, status in [('LiFSI-free P1 film', 'needs_source_review'), ('LiFSI-free film', 'needs_source_review'),
                              ('LiFSI–free film', 'needs_source_review'), ('P1 film, LiFSI‐free', 'needs_source_review'),
                              ('P1 film, LiFSI‑free', 'needs_source_review'), ('P1 with no LiFSI', 'needs_source_review'),
                              ('P1/amino LiFSI electrolyte', 'matched_focused_expectation')]:
            with self.subTest(label=label):
                run, reference = fixture()
                run['results'][0]['cards'][0]['specimens'][0]['label'] = label
                self.assertEqual(status, evaluate_run(run, reference)['measurements'][0]['status'])

    def test_numeric_terms_match_whole_numbers_inside_values_but_not_other_numbers(self):
        for value, term, status in [('about 2 h', '2 h', 'matched_focused_expectation'),
                                    ('2 h at 80 °C', '2 h', 'matched_focused_expectation'),
                                    ('at 30 °C', '30 °C', 'matched_focused_expectation'),
                                    ('30°C', '30 °C', 'matched_focused_expectation'),
                                    ('−30 °C', '30 °C', 'needs_source_review'), ('-30 °C', '30 °C', 'needs_source_review'),
                                    ('0.2 h', '2 h', 'needs_source_review'), ('12 h', '2 h', 'needs_source_review'),
                                    ('2.5 h', '2', 'needs_source_review'),
                                    # Documented non-matches stay: no plural/word-form or dash merging.
                                    ('2 hours', '2 h', 'needs_source_review'), ('0-6 V', '0–6 V', 'needs_source_review')]:
            with self.subTest(value=value, term=term):
                run, reference = fixture()
                run['results'][0]['cards'][0]['properties']['items'][0]['conditions'][0]['value'] = value
                reference['measurement_expectations'][0]['condition_value_terms'] = [[term]]
                self.assertEqual(status, evaluate_run(run, reference)['measurements'][0]['status'])
        for label, key, term, reason in [('P3 film', 'specimen_forbid', 'P3', 'specimen_forbidden_term_present:P3'),
                                         ('P1 with 10 μL liquid electrolyte', 'specimen_forbid', '10 μL',
                                          'specimen_forbidden_term_present:10 μL'),
                                         ('P1 with 10 μL liquid electrolyte', 'specimen_require_any', '10 μL', None)]:
            with self.subTest(label=label, key=key):
                run, reference = fixture()
                run['results'][0]['cards'][0]['specimens'][0]['label'] = label
                case = reference['measurement_expectations'][0]
                case.update(specimen_require_any=['film', 'electrolyte'], specimen_forbid=[])
                case[key] = [term]
                reasons = evaluate_run(run, reference)['measurements'][0]['candidates'][0]['reasons']
                self.assertEqual([reason] if reason else [], reasons)

    def test_malformed_held_value_records_do_not_crash_or_count_as_held_values(self):
        for bad in ({'unit': ''}, {'value': None}, {'value': ''}, {'value': float('nan')}):
            with self.subTest(bad=bad):
                run, reference = fixture()
                queue = run['results'][0]['review_queue']
                record = {'entity_id': 'p1', 'property': 'voltage', 'value': '3.8', 'unit': 'V', **bad}
                queue.append({'entity_id': 'p1', 'name': 'P1', 'path': 'entities[0].properties.items[1]',
                              'reason': 'fact_value_missing_or_invalid', 'record': record})
                item = evaluate_run(run, reference)['measurements'][0]
                self.assertEqual('matched_focused_expectation', item['status'])
                self.assertFalse(item['matching_value_held_for_review'])
                queue.append({'entity_id': 'p1', 'name': 'P1', 'path': 'entities[0].properties.items[2]',
                              'reason': 'specimen_link_needs_review', 'record': {**record, 'value': '3.8', 'unit': 'V'}})
                self.assertTrue(evaluate_run(run, reference)['measurements'][0]['matching_value_held_for_review'])

    def test_bad_reference_types_fail_before_evaluation(self):
        for kind in ('unit-flag', 'observations', 'source-ids', 'description-terms'):
            with self.subTest(kind=kind):
                run, reference = conflict_fixture()
                case = reference['conflict_expectations'][0]
                if kind == 'unit-flag': case['observations'][0]['unit_field_required'] = 'yes'
                elif kind == 'observations': case['observations'] = []
                elif kind == 'source-ids': case['evidence_chunk_ids_required'] = 'method'
                else: case['description_require_any'] = 'unresolved'
                with self.assertRaises(ValueError): evaluate_run(run, reference)


if __name__ == '__main__':
    unittest.main()
