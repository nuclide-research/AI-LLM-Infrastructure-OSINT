#!/usr/bin/env python3
"""Offline tests for ns-attribute. STDLIB ONLY (unittest). No live target contact.

Self-test of record: the SASE/networking operator pair must cluster together on
the shared distinctive tokens {aicore, common, sdwan, nvo, oms, xcd,
numaflow-system}. IPs 203.0.113.11 (kc5-aws) and 203.0.113.13 (g2r1).
"""
import importlib.util
import os
import unittest

# The tool ships as ns-attribute.py (hyphen, NuClide CLI naming), which is not a
# valid import name. Load it by path so the test can exercise its functions.
_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "ns_attribute", os.path.join(_HERE, "ns-attribute.py"))
na = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(na)


class TestStoplist(unittest.TestCase):
    def setUp(self):
        self.sl = na.build_stoplist()

    def test_strips_double_underscore_pseudo_ns(self):
        d = na.distinctive_set(["__idle__", "__unmounted__", "aicore"], self.sl)
        self.assertEqual(d, {"aicore"})

    def test_strips_argo_prefix_glob(self):
        d = na.distinctive_set(["argo", "argocd", "argo-rollouts", "oms"], self.sl)
        self.assertEqual(d, {"oms"})

    def test_strips_standard_platform(self):
        d = na.distinctive_set(
            ["kube-system", "default", "monitoring", "kubecost", "opencost",
             "cert-manager", "ingress-nginx", "prometheus-system", "sdwan"],
            self.sl)
        self.assertEqual(d, {"sdwan"})


class TestJaccard(unittest.TestCase):
    def test_identical(self):
        self.assertEqual(na.jaccard({"a", "b"}, {"a", "b"}), 1.0)

    def test_disjoint(self):
        self.assertEqual(na.jaccard({"a"}, {"b"}), 0.0)

    def test_partial(self):
        self.assertAlmostEqual(na.jaccard({"a", "b", "c"}, {"b", "c", "d"}), 0.5)


class TestSasePairRecovery(unittest.TestCase):
    """The load-bearing self-test."""

    @classmethod
    def setUpClass(cls):
        here = os.path.dirname(os.path.abspath(__file__))
        data = os.path.join(here, "..", "data", "finops-probe-results.ndjson")
        rows = na.load_rows(data)
        hosts = na.normalize(rows)
        cls.report = na.build_report(hosts, threshold=0.5, stoplist=na.build_stoplist())

    def _group_containing(self, ip):
        for g in self.report["operator_candidate_groups"]:
            if ip in g["member_ips"]:
                return g
        return None

    def test_sase_pair_clusters_together(self):
        g = self._group_containing("203.0.113.11")
        self.assertIsNotNone(g, "203.0.113.11 not in any operator group")
        self.assertIn("203.0.113.13", g["member_ips"],
                      "g2r1 host did not cluster with kc5-aws host")

    def test_sase_pair_shared_tokens(self):
        g = self._group_containing("203.0.113.11")
        expected = {"aicore", "common", "sdwan", "nvo", "oms", "xcd", "numaflow-system"}
        self.assertTrue(
            expected.issubset(set(g["shared_distinctive_tokens"])),
            f"shared tokens missing some of {expected}; got {g['shared_distinctive_tokens']}")

    def test_sase_pair_confidence_high(self):
        g = self._group_containing("203.0.113.11")
        self.assertEqual(g["confidence"], "high")

    def test_kc5_aws_twin_helm_byte_duplicate(self):
        # 203.0.113.11 and 203.0.113.12 both kc5-aws, 19304 bytes -> one cluster, two LBs
        dups = self.report["helmvalues_duplicates"]
        hit = [d for d in dups if d["helmvalues_bytes"] == 19304]
        self.assertTrue(hit, "expected a 19304-byte helm duplicate set")
        self.assertEqual(set(hit[0]["member_ips"]), {"203.0.113.11", "203.0.113.12"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
