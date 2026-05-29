#!/usr/bin/env python3
"""Offline tests for ns-attribute. STDLIB ONLY (unittest). No live target contact.

Self-test of record: a SASE/networking operator pair must cluster together on the
shared distinctive tokens {aicore, common, sdwan, nvo, oms, xcd, numaflow-system}.
Uses synthetic RFC5737 fixtures so no harvested data lives in the repo.
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
    """The load-bearing self-test, on synthetic RFC5737 fixtures (no harvested data)."""

    # Two hosts share the distinctive SASE token set (must cluster); a third is a
    # helmValues byte-twin of the first (one cluster behind two LBs); a fourth is
    # unrelated (must NOT cluster). IPs are RFC5737 documentation addresses.
    ROWS = [
        {"ip": "203.0.113.10", "cluster_id": "site-a", "helmvalues_bytes": 19304,
         "namespaces": ["aicore", "common", "sdwan", "nvo", "oms", "xcd",
                        "numaflow-system", "kube-system", "monitoring", "__idle__"]},
        {"ip": "203.0.113.11", "cluster_id": "site-a", "helmvalues_bytes": 19304,
         "namespaces": ["aicore", "common", "sdwan", "nvo", "oms", "xcd",
                        "numaflow-system", "kube-system"]},
        {"ip": "203.0.113.20", "cluster_id": "site-b", "helmvalues_bytes": 18040,
         "namespaces": ["aicore", "common", "sdwan", "nvo", "oms", "xcd",
                        "numaflow-system", "kafka", "wips"]},
        {"ip": "198.51.100.5", "helmvalues_bytes": 5000,
         "namespaces": ["jenkins", "sonarqube", "kube-system", "monitoring", "default"]},
    ]

    @classmethod
    def setUpClass(cls):
        hosts = na.normalize(cls.ROWS)
        cls.report = na.build_report(hosts, threshold=0.5, stoplist=na.build_stoplist())

    def _group_containing(self, ip):
        for g in self.report["operator_candidate_groups"]:
            if ip in g["member_ips"]:
                return g
        return None

    def test_sase_pair_clusters_together(self):
        g = self._group_containing("203.0.113.10")
        self.assertIsNotNone(g, "203.0.113.10 not in any operator group")
        self.assertIn("203.0.113.20", g["member_ips"],
                      "second SASE host did not cluster with the first")

    def test_sase_pair_shared_tokens(self):
        g = self._group_containing("203.0.113.10")
        expected = {"aicore", "common", "sdwan", "nvo", "oms", "xcd", "numaflow-system"}
        self.assertTrue(
            expected.issubset(set(g["shared_distinctive_tokens"])),
            f"shared tokens missing some of {expected}; got {g['shared_distinctive_tokens']}")

    def test_sase_pair_confidence_set(self):
        # confidence depends on corpus-wide token rarity; on a tiny synthetic corpus
        # just assert it is computed to a valid label, not the specific tier.
        g = self._group_containing("203.0.113.10")
        self.assertIn(g["confidence"], ("high", "medium", "low"))

    def test_helm_byte_duplicate(self):
        # the two byte-twins (19304) = one cluster behind two LoadBalancers
        dups = self.report["helmvalues_duplicates"]
        hit = [d for d in dups if d["helmvalues_bytes"] == 19304]
        self.assertTrue(hit, "expected a 19304-byte helm duplicate set")
        self.assertEqual(set(hit[0]["member_ips"]), {"203.0.113.10", "203.0.113.11"})

    def test_unrelated_host_excluded(self):
        g = self._group_containing("198.51.100.5")
        if g is not None:
            self.assertNotIn("203.0.113.10", g["member_ips"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
