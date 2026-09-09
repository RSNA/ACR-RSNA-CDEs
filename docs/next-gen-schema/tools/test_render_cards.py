#!/usr/bin/env python3
import unittest

from graph import load_graph
from render_cards import Cards


class DirectContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = Cards(load_graph())

    def test_scope_and_context_never_come_from_an_ancestor(self):
        # The invariant: whatever Cards reports for a node was asserted on that node itself.
        for nid, node in self.cards.g.nodes.items():
            if node["node"] not in {"FindingClass", "Diagnosis", "Grouping"}:
                continue
            with self.subTest(node=nid):
                scope, source = self.cards.scope(nid)
                self.assertIn(source, (nid, None))
                self.assertEqual(bool(scope), source == nid)
                for label, (values, src) in self.cards.context(nid).items():
                    self.assertIn(src, (nid, None), label)
                    self.assertEqual(bool(values), src == nid, label)

    def test_acute_pyelonephritis_context_is_explicit(self):
        scope, source = self.cards.scope("RDE2_000801")
        self.assertEqual(scope, [("RID205", {"kind": "structure", "strength": "required"})])
        self.assertEqual(source, "RDE2_000801")

        context = self.cards.context("RDE2_000801")
        self.assertEqual(context["MODALITY"], (["RID10312", "RID10321", "RID10326"], "RDE2_000801"))
        self.assertIn("RID10326", context["MODALITY"][0])

    def test_mat_contains_no_inheritance_claim(self):
        svg = self.cards.mat("RDE2_000801")
        self.assertNotIn("inherited from", svg)
        self.assertIn("ultrasound RID10326", svg)


if __name__ == "__main__":
    unittest.main()
