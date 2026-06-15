import json
import tempfile
import unittest
from pathlib import Path

from openalex_taxicab.eval_harness import EvalRow
from openalex_taxicab.residual_clusters import (
    browserbase_candidates,
    cluster_rows,
    redact_url,
    write_cluster_artifacts,
    zyte_support_candidates,
)


def row(doi, category, publisher, host, support_candidate=True):
    return EvalRow(
        run_id="test",
        doi=doi,
        category=category,
        publisher=publisher,
        host=host,
        input_url=f"https://doi.org/{doi}",
        resolved_url=f"https://{host}/article/{doi}",
        status_code=200,
        content_type="text/html",
        size_bytes=100,
        title=f"title {doi}",
        evidence_snippet=f"evidence {doi}",
        support_candidate=support_candidate,
        uuid=f"uuid-{doi}",
        html_record_count=1,
        created_date="2026-06-11T00:00:00",
        duration_ms=1,
        mode="test",
        error="",
    )


class ResidualClusterTests(unittest.TestCase):
    def test_clusters_rank_by_estimated_recoverable_rows(self):
        rows = [
            row("10.1/a", "router_only", "mdpi", "mdpi.com"),
            row("10.1/b", "router_only", "mdpi", "mdpi.com"),
            row("10.1/c", "pdf_instead_of_html", "unknown", "unknown"),
            row("10.1/d", "pdf_instead_of_html", "unknown", "unknown"),
            row("10.1/e", "pdf_instead_of_html", "unknown", "unknown"),
            row("10.1/f", "good_html", "springer", "link.springer.com", support_candidate=False),
        ]

        clusters = cluster_rows(rows, sample_size=2)

        self.assertEqual(clusters[0].category, "router_only")
        self.assertEqual(clusters[0].publisher, "mdpi")
        self.assertEqual(clusters[0].host, "mdpi.com")
        self.assertEqual(clusters[0].count, 2)
        self.assertEqual(len(clusters[0].sample_rows), 2)
        self.assertGreater(clusters[0].estimated_recoverable_rows, clusters[1].estimated_recoverable_rows)

    def test_pdf_success_and_no_pdf_expected_are_not_residuals(self):
        rows = [
            row("10.1/a", "good_pdf", "springer", "link.springer.com", support_candidate=False),
            row("10.1/b", "no_pdf_expected", "elsevier", "unknown", support_candidate=False),
            row("10.1/c", "missing_pdf_harvest", "wiley", "unknown"),
        ]

        clusters = cluster_rows(rows, sample_size=5)

        self.assertEqual(len(clusters), 1)
        self.assertEqual(clusters[0].category, "missing_pdf_harvest")
        self.assertEqual(clusters[0].publisher, "wiley")

    def test_candidate_outputs_separate_lens_and_envoy_queues(self):
        clusters = cluster_rows(
            [
                row("10.1/a", "router_only", "mdpi", "mdpi.com"),
                row("10.1/b", "missing_harvest", "unknown", "unknown"),
                row("10.1/c", "bot_block_403", "iop", "iopscience.iop.org"),
            ],
            sample_size=1,
        )

        browser_rows = browserbase_candidates(clusters)
        zyte_rows = zyte_support_candidates(clusters)

        self.assertEqual([item["recommended_agent"] for item in browser_rows], ["Lens", "Lens"])
        self.assertEqual([item["recommended_agent"] for item in zyte_rows], ["Envoy", "Envoy"])
        self.assertNotIn("missing_harvest", {item["category"] for item in browser_rows})

    def test_write_cluster_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            rows_path = tmp_path / "rows.ndjson"
            out_dir = tmp_path / "out"
            rows = [
                row("10.1/a", "router_only", "mdpi", "mdpi.com").to_dict(),
                row("10.1/b", "empty_response", "elsevier", "jbc.org").to_dict(),
            ]
            rows_path.write_text("\n".join(json.dumps(item) for item in rows) + "\n")

            paths = write_cluster_artifacts(rows_path, out_dir, run_id="cluster-test", sample_size=1, top_n=10)

            payload = json.loads(paths["clusters_json"].read_text())
            self.assertEqual(payload["run_id"], "cluster-test")
            self.assertEqual(payload["non_good_rows"], 2)
            self.assertTrue(paths["clusters_csv"].exists())
            self.assertTrue(paths["browserbase_candidates"].exists())
            self.assertTrue(paths["zyte_support_candidates"].exists())

    def test_redacts_signed_and_challenge_query_values(self):
        url = (
            "https://pdf.example.org/main.pdf?"
            "X-Amz-" "Security-Token=secret&X-Amz-" "Signature=sig&pii=S123&bm-" "verify=challenge"
        )

        redacted = redact_url(url)

        self.assertIn("pii=S123", redacted)
        self.assertIn("redacted=1", redacted)
        self.assertNotIn("secret", redacted)
        self.assertNotIn("sig", redacted)
        self.assertNotIn("challenge", redacted)


if __name__ == "__main__":
    unittest.main()
