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
