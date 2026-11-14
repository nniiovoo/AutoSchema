"""Regression checks for numeric-notation, sample-link and evidence passthrough guards.

Sentences marked Guo/Pei/Chen are copied from the saved JATS-derived source
snapshots in examples/polymer_cards/guo_fixes_run_2026-11-06/sources.json.
"""
from copy import deepcopy
import unittest

from polymer_cards_lib import render
from polymer_cards_lib.evidence_spans import build_span_catalog
from polymer_cards_lib.validation import _literal, build_cards


SHA = "a" * 64
IDENTITY = "Polymer P1 was synthesized."


def document(*texts):
    return {"paper_id": "guards", "chunks": [
        {"chunk_id": "c%d" % i, "text": text, "source_part": "main", "locator": "L%d" % i,
         "document_sha256": SHA} for i, text in enumerate(texts)]}


def ev(*quotes, chunk="c0"):
    return [{"chunk_id": chunk, "quote": quote} for quote in quotes]


def entity(specimens=None, properties=None, name="P1", identity=IDENTITY, **groups):
    record = {"entity_id": "p1", "name": name, "identity_evidence": ev(identity),
              "classification": {"is_polymer": True, "reason": "Source calls it a polymer.",
                                 "evidence": ev(identity)},
              "specimens": specimens if specimens is not None else
              [{"specimen_id": "s", "label": "P1 film", "evidence": ev(identity)}]}
    if properties is not None:
        record["properties"] = {"status": "reported", "items": properties}
    for field, items in groups.items():
        record[field] = {"status": "reported", "items": items}
    return record


def prop(value, *quotes, unit=None, specimen_id="s", conditions=None, **extra):
    return {"entity_id": "p1", "property": "measurement", "value": value, "unit": unit,
            "specimen_id": specimen_id, "conditions": conditions or [], "evidence": ev(*quotes), **extra}


def run(doc, record):
    return build_cards(doc, {"paper_id": doc["paper_id"], "entities": [record]})


def accepted(result):
    return [(p["value"], p["unit"]) for p in result["cards"][0]["properties"]["items"]]


def reasons(result):
    return [item["reason"] for item in result["review_queue"]]


class TruncatedLegacyQuoteTests(unittest.TestCase):
    """Legacy quotes are judged at their position in the original chunk."""

    SOURCE = (IDENTITY + " P1 film had Mw/Mn = 1.77. "
              "P1 film conductivity was 6.5 × 10−5 S cm−1 at 30°C. "
              "P1 film displayed a wider electrochemical voltage beyond 5.0 V. "
              "The P1 film was stable at −20 °C. P1 film was 0.5mS/cm.")

    def check(self, value, quotes, unit=None):
        return run(document(self.SOURCE), entity(properties=[prop(value, *quotes, unit=unit)]))

    def test_quote_boundary_inside_a_number_or_after_a_qualifier_is_not_a_complete_value(self):
        for value, unit, quotes in [
                ("1.7", None, ["P1 film had Mw/Mn = 1.7"]),
                ("6.5", "S cm−1", ["P1 film conductivity was 6.5", "S cm−1"]),
                ("5.0", "V", ["5.0 V"]),
                ("20", "°C", ["20 °C"])]:
            with self.subTest(value=value, quotes=quotes):
                result = self.check(value, quotes, unit)
                self.assertEqual([], accepted(result))
                self.assertEqual(["property_value_not_in_original_evidence"], reasons(result))

    def test_complete_values_in_truncated_quotes_remain_valid(self):
        for value, unit, quotes in [
                ("1.77", None, ["P1 film had Mw/Mn = 1.77"]),
                ("6.5 × 10−5", "S cm−1", ["film conductivity was 6.5 × 10−5 S cm−1"]),
                ("−20", "°C", ["−20 °C"]),
                ("30", "°C", ["30°C"])]:
            with self.subTest(value=value, quotes=quotes):
                self.assertEqual([(value, unit)], accepted(self.check(value, quotes, unit)))

    def test_unit_prefix_is_judged_with_the_chunk_neighbour(self):
        result = self.check("0.5", ["P1 film was 0.5", "S/cm"], unit="S/cm")
        self.assertEqual(["property_unit_not_in_original_evidence"], reasons(result))

    def test_any_supporting_occurrence_of_a_repeated_quote_is_enough(self):
        doc = document(IDENTITY + " Sample A had 1.77 here. Sample A had 1.7 there.")
        result = run(doc, entity(properties=[prop("1.7", "Sample A had 1.7")]))
        self.assertEqual([("1.7", None)], accepted(result))

    def test_condition_quote_boundary_is_judged_in_context(self):
        sentence = "The P1 film retained 12 mAh at −20 °C."
        doc = document(IDENTITY + " " + sentence)
        condition = {"name": "temperature", "value": "20", "evidence": ev("20 °C")}
        result = run(doc, entity(properties=[prop("12", sentence, unit="mAh", conditions=[condition])]))
        self.assertEqual(["condition_value_not_in_original_evidence"], reasons(result))

    def test_quote_only_helper_is_unchanged_for_external_callers(self):
        self.assertTrue(_literal("1.7", "Mw/Mn = 1.7"))
        self.assertFalse(_literal("1.7", "Mw/Mn = 1.7", context="Mw/Mn = 1.77."))
        self.assertTrue(_literal("1.77", "Mw/Mn = 1.77", context="Mw/Mn = 1.77."))


class QualifierTests(unittest.TestCase):
    def test_leading_and_trailing_bounds_and_approximations_are_not_bare_values(self):
        for value, quote in [
                ("2,000", "was ca. 2,000%"), ("5.0", "window of approx. 5.0 V"),
                ("5.0", "window of approx 5.0 V"), ("5.0", "window of around 5.0 V"),
                ("140", "stretched to nearly 140 times"), ("5.0", "almost 5.0 V"),
                ("100", "stable for over 100 cycles"), ("290", "decomposition temperature over 290 °C"),
                ("290", "temperature exceeding 290 °C"), ("60", "higher than 60 °C"),
                ("60", "lower than 60 °C"), ("5", "no more than 5 %"), ("5", "no less than 5 %"),
                ("5.0", "window of ∼5.0 V"), ("5.0", "window of ≃5.0 V"), ("5.0", "window of ≅5.0 V"),
                ("5.0", "window of ⩽5.0 V"), ("5.0", "window of ⩾5.0 V"),
                ("5.0", "window of ≲5.0 V"), ("5.0", "window of ≳5.0 V"),
                ("100", "stable for 100+ cycles"),
                ("5.0", "5.0 V or higher"), ("5.0", "5.0 V or more"), ("5.0", "5.0 V or above"),
                ("5.0", "5.0 V or less"), ("5.0", "5.0 V or lower"), ("10", "10 mA cm−2 or below")]:
            with self.subTest(value=value, quote=quote):
                self.assertFalse(_literal(value, quote))

    def test_qualified_raw_values_and_unqualified_values_remain_valid(self):
        for value, quote in [
                ("ca. 2,000%", "was ca. 2,000%,"), ("∼5.0", "window of ∼5.0 V"),
                ("100+", "stable for 100+ cycles"), ("90 +/- 3", "was 90 +/- 3 MPa"),
                ("5.0", "5.0 V and 4.0 V"), ("30", "at 30 or 60 °C"), ("2", "for 2 h"),
                # 'over' a swept range, and 'under' a test condition (Chen), are not bounds.
                ("2 Hz to 100 kHz", "measured over 2 Hz to 100 kHz"),
                ("1 C rate", "achieved 139 mAh·g⁻¹ under 1 C rate"), ("80", "after 2 h under 80 °C")]:
            with self.subTest(value=value, quote=quote):
                self.assertTrue(_literal(value, quote))

    def test_labels_ending_in_digits_are_not_treated_as_bare_numbers(self):
        for value, quote in [("P1", "P1+LiTFSI electrolyte"), ("P1", "- P1 film"), ("SHP2", "SHP2 or higher"),
                             ("P1", "between P1 and P2"), ("P2", "between P1 and P2")]:
            with self.subTest(value=value, quote=quote):
                self.assertTrue(_literal(value, quote))

    def test_guo_approximate_strain_is_held(self):
        # Guo: P5 strain at break.
        sentence = ("The strain at break of the P5 film (lack of SS) was ca. 2,000%, higher than "
                    "that of P2 but still much lower than that of P4 (14,000%).")
        doc = document("Polymer P5 was synthesized. " + sentence)
        record = entity(name="P5", identity="Polymer P5 was synthesized.",
                        specimens=[{"specimen_id": "s", "label": "P5 film", "evidence": ev(sentence)}],
                        properties=[prop("2,000", sentence, unit="%")])
        result = run(doc, record)
        self.assertEqual([], accepted(result))
        self.assertEqual(["property_value_not_in_original_evidence"], reasons(result))
        record["properties"]["items"] = [prop("ca. 2,000%", sentence, unit="%")]
        self.assertEqual([("ca. 2,000%", "%")], accepted(run(doc, record)))

    def test_guo_temperature_bound_is_not_a_condition_value(self):
        # Guo rheology sentence.
        sentence = ("But when the temperature is higher than 60 °C in Supplementary Fig. 8g–j, "
                    "G″ became greater than G^{′} suggesting the enhanced mobility of polymer upon heating.")
        doc = document(IDENTITY + " " + sentence)
        condition = {"name": "temperature", "value": 60, "evidence": ev(sentence)}
        p = prop("G″ became greater than G^{′}", sentence, conditions=[condition])
        result = run(doc, entity(properties=[p]))
        self.assertEqual(["condition_value_not_in_original_evidence"], reasons(result))
        condition["value"] = "higher than 60"
        self.assertEqual(1, len(accepted(run(doc, entity(properties=[p])))))


class RangeAndSignFragmentTests(unittest.TestCase):
    def test_range_uncertainty_and_sign_fragments_are_rejected(self):
        for value, quote in [
                ("1.0", "between 1.0 and 3.0 V"), ("3.0", "between 1.0 and 3.0 V"),
                ("4.3", "between 4.3 V and 3.0 V"), ("3.0", "between 4.3 V and 3.0 V"),
                ("30", "30~60 °C"), ("60", "30~60 °C"), ("30", "30 ~ 60 °C"), ("30", "30∼60 °C"),
                ("30", "30‒60 °C"), ("30", "30―60 °C"), ("30", "30〜60 °C"), ("60", "30‒60 °C"),
                ("0.5", "12.3 (±0.5) MPa"), ("12.3", "12.3 (±0.5) MPa"), ("0.5", "uncertainty of ±0.5 MPa"),
                ("0.5", "uncertainty of ∓0.5 MPa"),
                ("45", "Tg was − 45 °C"), ("45", "Tg was − 45 °C"), ("0.83", "(ΔE = − 0.83 eV)"),
                ("20", "stable at －20 °C"), ("20", "stable at ‒20 °C"), ("20", "stable at ‐20 °C"),
                ("20", "stable at ﹣20 °C")]:
            with self.subTest(value=value, quote=quote):
                self.assertFalse(_literal(value, quote))

    def test_complete_range_uncertainty_and_signed_values_remain_valid(self):
        for value, quote in [
                ("1.0 and 3.0", "between 1.0 and 3.0 V"), ("30~60", "30~60 °C"), ("30‒60", "30‒60 °C"),
                ("12.3 (±0.5)", "12.3 (±0.5) MPa"), ("±0.5", "uncertainty of ±0.5 MPa"),
                ("− 45", "Tg was − 45 °C"), ("－20", "stable at －20 °C"),
                ("30", "at 30 and 60 °C"), ("60", "at 30 and 60 °C"), ("45", "cast for 45 min")]:
            with self.subTest(value=value, quote=quote):
                self.assertTrue(_literal(value, quote))

    def test_pei_cycling_window_endpoint_is_not_a_condition_value(self):
        # Pei cycling sentence (shortened after the window).
        sentence = ("after activation at 0.05 C (1 C = 1000 mAh g_{SPAN}⁻¹) between 1.0 and 3.0 V, "
                    "SPAN|P1|Li delivered an initial discharge capacity of 602 mAh g_{SPAN}⁻¹ at 0.3 C.")
        doc = document(IDENTITY + " " + sentence)
        for window, expected in (("1.0", 0), ("3.0", 0), ("1.0 and 3.0", 1)):
            with self.subTest(window=window):
                condition = {"name": "voltage window", "value": window, "evidence": ev(sentence)}
                p = prop("602", sentence, unit="mAh g_{SPAN}⁻¹", conditions=[condition])
                self.assertEqual(expected, len(accepted(run(doc, entity(properties=[p])))))


class SpaceGroupedThousandsTests(unittest.TestCase):
    def test_thin_narrow_and_no_break_space_thousands_are_one_number(self):
        for sep in (" ", " ", " ", " "):
            sentence = "The P1 film had M_{n} of 14" + sep + "000 g mol⁻¹ and an elongation of 2" + sep + "000%."
            doc = document(IDENTITY + " " + sentence)
            with self.subTest(separator=hex(ord(sep))):
                props = [prop("14", sentence, unit="g mol⁻¹"), prop("2", sentence, unit="%"),
                         prop("000", sentence, unit="%")]
                self.assertEqual([], accepted(run(doc, entity(properties=props))))
                complete = [prop("14" + sep + "000", sentence, unit="g mol⁻¹"),
                            prop("2" + sep + "000%", sentence, unit="%")]
                self.assertEqual(2, len(accepted(run(doc, entity(properties=complete)))))

    def test_ordinary_spaced_numbers_are_not_thousands(self):
        for value, quote in [("12", "P1 film 12 MPa"), ("25", "25 °C for 2 h"), ("2", "25 °C for 2 h"),
                             ("1000", "for 1000 h"), ("1.5", "1.5 000"), ("10", "cell 10 1000 h"),
                             ("2", "Fig. 2 1200% strain")]:
            with self.subTest(value=value, quote=quote):
                self.assertTrue(_literal(value, quote))
        self.assertFalse(_literal("1 000", "1 000 000 cycles"))
        self.assertTrue(_literal("1 000 000", "1 000 000 cycles"))


def span_ref(doc, text):
    entry = next(e for e in build_span_catalog(doc) if e["text"] == text)
    return [{"chunk_id": entry["chunk_id"], "span_id": entry["span_id"]}]


class SampleLinkGuardTests(unittest.TestCase):
    def link_case(self, link, label="P1 film", sibling=None, unit="mS cm⁻¹"):
        result_sentence = "The P1 film showed a conductivity of 1.2 mS cm⁻¹."
        doc = document(IDENTITY + " " + link + " " + result_sentence)
        specimens = [{"specimen_id": "s", "label": label, "evidence": ev(IDENTITY)}]
        if sibling:
            specimens.append({"specimen_id": "salted", "label": sibling, "evidence": ev(IDENTITY)})
        p = prop("1.2", result_sentence, unit=unit, specimen_evidence=ev(link))
        return run(doc, entity(specimens=specimens, properties=[p]))

    def test_plural_cell_stack_is_not_an_additive_form(self):
        for link in ("The SS/P1/Li asymmetric cells were assembled for testing.",
                     "Li/P1/Li symmetric cells were assembled to test the P1 film.",
                     "Symmetric cells (SS/P1/SS) were assembled with the P1 film."):
            with self.subTest(link=link):
                self.assertEqual(1, len(accepted(self.link_case(link))))

    def test_property_symbols_after_with_are_not_additives(self):
        for link in ("P1 with Mw of 6 × 10⁵ g mol⁻¹ was dissolved in acetonitrile and cast into a film.",
                     "P1 with Mn = 12 kDa was cast into a film.",
                     "P1 with Tg of −45 °C was cast into a film.",
                     "P1 with PDI of 1.8 was cast into a film.",
                     "P1 with Đ of 1.8 was cast into a film.",
                     "P1 with M_{w} of 6 kDa was cast into a film.",
                     "P1 with Ea of 0.3 eV was cast into a film."):
            with self.subTest(link=link):
                self.assertEqual(1, len(accepted(self.link_case(link))))

    def test_additive_forms_after_with_are_still_quarantined(self):
        for link in ("P1 with LiTFSI was cast into a film.",
                     "P1 with EO:Li = 20:1 was cast into a film.",
                     "The P1/LiFSI symmetric cells were assembled."):
            with self.subTest(link=link):
                self.assertEqual(["property_sample_evidence_names_alternate_form"],
                                 reasons(self.link_case(link)))

    def test_link_quote_whitespace_is_normalized_before_the_form_check(self):
        identity = "The SHP network polymer was synthesized."
        result_sentence = "The SHP network showed a stability window of 4.6 V."
        for sep in (" ", "\n", "  ", " "):
            link = "The SHP" + sep + "network/LiBOB electrolyte membrane was prepared for testing."
            doc = document(identity + " " + link + " " + result_sentence)
            for with_sibling in (True, False):
                specimens = [{"specimen_id": "s", "label": "SHP network membrane", "evidence": span_ref(doc, identity)}]
                if with_sibling:
                    specimens.append({"specimen_id": "salted", "label": "SHP network/LiBOB electrolyte",
                                      "evidence": span_ref(doc, link)})
                p = prop("4.6", result_sentence, unit="V")
                p["evidence"] = span_ref(doc, result_sentence)
                p["specimen_evidence"] = span_ref(doc, link)
                record = entity(name="SHP network", specimens=specimens, properties=[p])
                record["identity_evidence"] = record["classification"]["evidence"] = span_ref(doc, identity)
                with self.subTest(separator=repr(sep), sibling=with_sibling):
                    self.assertEqual(["property_sample_evidence_names_alternate_form"], reasons(run(doc, record)))


class MolecularWeightCompositionTests(unittest.TestCase):
    def composition(self, value):
        doc = document(IDENTITY + " " + value)
        item = {"entity_id": "p1", "value": value, "basis": "component_amounts", "specimen_id": None,
                "evidence": ev(value)}
        return run(doc, entity(specimens=[], composition=[item]))

    def test_standalone_molecular_weight_statements_are_held(self):
        for value in ("Mw = 4,600 g mol⁻¹", "Mn ≈ 4,600 g mol⁻¹", "Mn ~ 4600 g/mol", "Mn ∼ 4600 g/mol",
                      "Mw of 4,600 g/mol", "molecular weight of 2,000 g mol⁻¹",
                      "number-average molecular weight of 2,000 g mol⁻¹", "Mw = 4.6 kg mol⁻¹",
                      "Mw = 4600 g·mol⁻¹", "Mn = 14 000 g mol⁻¹", "Mw = 6 × 10⁵ g mol⁻¹", "Mn = 12 kDa"):
            with self.subTest(value=value):
                result = self.composition(value)
                self.assertEqual([], result["cards"][0]["composition"]["items"])
                self.assertEqual(["composition_contains_molecular_weight_only"], reasons(result))

    def test_ingredient_amounts_with_a_molecular_weight_remain_composition(self):
        for value in ("PEO, Mw = 6 × 10⁵ g mol⁻¹", "LiTFSI, mass ratio 2:1", "PEG (Mn = 2,000 g mol⁻¹), 2.0 g"):
            with self.subTest(value=value):
                self.assertEqual(1, len(self.composition(value)["cards"][0]["composition"]["items"]))


class UnvalidatedEvidencePassthroughTests(unittest.TestCase):
    SOURCE = IDENTITY + " P1/LiFSI electrolyte was prepared at a mass ratio of 2:1. The P1 film was transparent."
    FORGED = [{"chunk_id": "c0", "quote": "INVENTED: P1 was annealed at 300 C", "evidence_status": "quote_matched"}]

    def test_undefined_evidence_bearing_keys_are_not_rendered_as_matched(self):
        doc = document(self.SOURCE)
        record = entity(specimens=[{"specimen_id": "salted", "label": "P1/LiFSI",
                                    "evidence": ev("P1/LiFSI electrolyte was prepared")}],
                        composition=[{"entity_id": "p1", "value": "P1/LiFSI 2:1", "basis": "mass_ratio",
                                      "specimen_id": "salted", "evidence": ev("mass ratio of 2:1"),
                                      "specimen_evidence": deepcopy(self.FORGED),
                                      "conditions": [{"name": "annealing", "value": "300 C",
                                                      "evidence": deepcopy(self.FORGED)}],
                                      "support": {"evidence": deepcopy(self.FORGED)}}])
        record["description"] = {"value": "A polymer.", "evidence": ev(IDENTITY),
                                 "specimen_evidence": deepcopy(self.FORGED)}
        before = deepcopy(record)
        result = run(doc, record)
        self.assertEqual(before, record)
        card = result["cards"][0]
        item = card["composition"]["items"][0]
        for key in ("specimen_evidence", "conditions", "support"):
            self.assertNotIn(key, item)
        self.assertNotIn("specimen_evidence", card["description"])
        self.assertEqual("mass_ratio", item["basis"])
        html = render._fact_html(item, doc, card, "composition")
        self.assertNotIn("INVENTED", html)
        self.assertNotIn("Sample-link evidence", html)

    def test_property_keeps_validated_context_and_drops_other_evidence_keys(self):
        doc = document(self.SOURCE)
        sentence = "The P1 film was transparent"
        p = prop("transparent", sentence, specimen_evidence=ev(sentence),
                 method_evidence=deepcopy(self.FORGED),
                 conditions_review_status="captured_not_scientifically_verified")
        item = run(doc, entity(properties=[p]))["cards"][0]["properties"]["items"][0]
        self.assertEqual(sentence, item["specimen_evidence"][0]["quote"])
        self.assertNotIn("method_evidence", item)
        self.assertNotIn("conditions_review_status", item)
        self.assertEqual([], item["conditions"])


class AttributionWarningBaseTests(unittest.TestCase):
    TEXT = (IDENTITY + " A P1 film was cast. P1/LiFSI electrolyte was prepared. "
            "P1 showed a stability window of 3.8 V. The neat P1 showed 3.9 V.")

    def warnings(self, chosen, sibling, quote="P1 showed a stability window of 3.8 V", value="3.8"):
        specimens = [{"specimen_id": "s", "label": chosen, "evidence": ev("A P1 film was cast")},
                     {"specimen_id": "salted", "label": sibling, "evidence": ev("P1/LiFSI electrolyte was prepared")}]
        result = run(document(self.TEXT), entity(specimens=specimens, properties=[prop(value, quote, unit="V")]))
        self.assertEqual([(value, "V")], accepted(result))
        return [w["reason"] for w in result["attribution_warnings"]]

    def test_bare_form_labels_use_the_specimen_stem_and_guard_separator(self):
        for chosen, sibling in [("P1", "P1/LiFSI"), ("P1 film", "P1/LiFSI"), ("neat P1", "P1/LiFSI"),
                                ("pure P1", "P1/LiFSI"), ("salt-free P1", "P1/LiFSI"),
                                ("P1 electrolyte", "P1/LiFSI electrolyte"), ("P1 polymer", "P1/LiFSI"),
                                ("P1 neat film", "P1/LiFSI"), ("P1", "P1 / LiFSI"), ("P1", "P1 + LiFSI")]:
            with self.subTest(chosen=chosen, sibling=sibling):
                self.assertEqual(["specimen_form_ambiguous"], self.warnings(chosen, sibling))

    def test_explicit_neat_quote_and_unrelated_labels_do_not_warn(self):
        self.assertEqual([], self.warnings("neat P1", "P1/LiFSI", quote="The neat P1 showed 3.9 V", value="3.9"))
        self.assertEqual([], self.warnings("P1 film", "P1 membrane"))
        self.assertEqual([], self.warnings("P1", "P10/LiFSI"))

    def test_attribution_quotes_are_whitespace_normalized(self):
        text = "The SHP network polymer was synthesized. The neat SHP\nnetwork showed 4.6 V."
        doc = document(text)
        quote = "The neat SHP\nnetwork showed 4.6 V"
        specimens = [{"specimen_id": "s", "label": "SHP network membrane", "evidence": ev(quote)},
                     {"specimen_id": "salted", "label": "SHP network/LiBOB", "evidence": ev(quote)}]
        record = entity(name="SHP network", identity="The SHP network polymer", specimens=specimens,
                        properties=[prop("4.6", quote, unit="V")])
        result = run(doc, record)
        self.assertEqual([("4.6", "V")], accepted(result))
        self.assertEqual([], result["attribution_warnings"])


if __name__ == "__main__":
    unittest.main()
