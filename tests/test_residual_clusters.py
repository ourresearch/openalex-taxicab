import json
import tempfile
import unittest
from pathlib import Path

from openalex_taxicab.eval_harness import EvalRow
from openalex_taxicab.pdf_eval_harness import PdfEvalRow
from openalex_taxicab.residual_clusters import (
    browserbase_candidates,
    cluster_rows,
    path_pattern,
    redact_url,
    residual_host,
    subcluster_priority,
    subcluster_rows_by_path,
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


def pdf_row(
    doi,
    category,
    publisher,
    host="unknown",
    candidate_url="",
    candidate_source="corpus_pdf_url",
    support_candidate=True,
):
    return PdfEvalRow(
        run_id="test",
        work_id=f"W{doi}",
        doi=doi,
        category=category,
        publisher=publisher,
        host=host,
        input_url=f"https://doi.org/{doi}",
        candidate_url=candidate_url,
        candidate_source=candidate_source,
        resolved_url="",
        status_code=None,
        content_type="",
        size_bytes=0,
        sha256="",
        pdf_magic=False,
        page_count=0,
        text_chars=0,
        title_overlap=0.0,
        doi_match=False,
        validation_errors=[],
        evidence_snippet="no pdf records",
        support_candidate=support_candidate,
        uuid="",
        pdf_record_count=0,
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

    def test_missing_pdf_harvest_uses_candidate_url_host(self):
        rows = [
            pdf_row(
                "10.1/a",
                "missing_pdf_harvest",
                "springer",
                candidate_url="https://link.springer.com/content/pdf/10.1/a.pdf?download=true",
            ),
            pdf_row(
                "10.1/b",
                "missing_pdf_harvest",
                "springer",
                candidate_url="https://link.springer.com/content/pdf/10.1/b.pdf",
            ),
            pdf_row(
                "10.1/c",
                "missing_pdf_harvest",
                "springer",
                candidate_url="https://media.springernature.com/full/springer-static/image/chp%3A10.1/c.pdf",
            ),
        ]

        clusters = cluster_rows(rows, sample_size=2)

        by_host = {cluster.host: cluster for cluster in clusters}
        self.assertEqual(by_host["link.springer.com"].count, 2)
        self.assertEqual(by_host["media.springernature.com"].count, 1)
        self.assertEqual(by_host["link.springer.com"].sample_rows[0]["host"], "link.springer.com")
        self.assertIn("candidate_url", by_host["link.springer.com"].sample_rows[0])

    def test_path_pattern_redacts_doi_and_ids_but_keeps_route_shape(self):
        self.assertEqual(
            path_pattern("https://link.springer.com/content/pdf/10.1007/s00125-026-12345-9.pdf?download=true"),
            "link.springer.com:/content/pdf/:doi/:id.pdf",
        )
        self.assertEqual(
            path_pattern("https://pubs.acs.org/doi/pdf/10.1021/acs.jpcc.6b12345"),
            "pubs.acs.org:/doi/pdf/:doi/:id",
        )
        self.assertEqual(
            path_pattern("https://example.org/download/12345678901234567890/full"),
            "example.org:/download/:num/full",
        )

    def test_subclusters_split_host_by_source_and_path_pattern(self):
        rows = [
            pdf_row(
                "10.1/a",
                "missing_pdf_harvest",
                "springer",
                candidate_url="https://link.springer.com/content/pdf/10.1007/a.pdf",
                candidate_source="corpus_pdf_url",
            ),
            pdf_row(
                "10.1/b",
                "missing_pdf_harvest",
                "springer",
                candidate_url="https://link.springer.com/content/pdf/10.1007/b.pdf",
                candidate_source="corpus_pdf_url",
            ),
            pdf_row(
                "10.1/c",
                "missing_pdf_harvest",
                "springer",
                candidate_url="https://link.springer.com/article/10.1007/s00125-026-12345-9",
                candidate_source="candidate_discovery",
            ),
        ]

        subclusters = subcluster_rows_by_path(rows)
        by_key = {(item.candidate_source, item.path_pattern): item for item in subclusters}

        self.assertEqual(by_key[("corpus_pdf_url", "link.springer.com:/content/pdf/:doi/:file.pdf")].count, 2)
        self.assertEqual(by_key[("candidate_discovery", "link.springer.com:/article/:doi/:id")].count, 1)
        self.assertNotIn("10.1007", by_key[("corpus_pdf_url", "link.springer.com:/content/pdf/:doi/:file.pdf")].path_pattern)

    def test_subcluster_priority_marks_prior_provider_lanes(self):
        status, band, decision = subcluster_priority(
            "missing_pdf_harvest",
            "springer",
            "link.springer.com",
            "link.springer.com:/content/pdf/:doi/:id.pdf",
        )

        self.assertEqual(status, "prior_negative_or_support_evidence")
        self.assertEqual(band, "provider_lane_do_not_duplicate")
        self.assertIn("provider/Zyte", decision)

    def test_subcluster_priority_marks_known_host_variants(self):
        status, band, _decision = subcluster_priority(
            "missing_pdf_harvest",
            "wiley",
            "onlinelibrary.wiley.com",
            "onlinelibrary.wiley.com:/doi/pdf/:doi/:id",
        )

        self.assertEqual(status, "prior_negative_or_support_evidence")
        self.assertEqual(band, "provider_lane_do_not_duplicate")

    def test_subcluster_priority_marks_existing_branch_candidates(self):
        status, band, decision = subcluster_priority(
            "missing_pdf_harvest",
            "acm",
            "dl.acm.org",
            "dl.acm.org:/doi/pdf/:doi/:id",
        )

        self.assertEqual(status, "acm_pdf_byte_branch_candidate")
        self.assertEqual(band, "confirm_existing_branch_candidate")
        self.assertIn("duplicate provider probe", decision)

    def test_subcluster_priority_marks_fresh_probe_candidates(self):
        status, band, decision = subcluster_priority(
            "missing_pdf_harvest",
            "unknown",
            "fresh.example.org",
            "fresh.example.org:/download/:file.pdf",
        )

        self.assertEqual(status, "fresh_probe_candidate")
        self.assertEqual(band, "probe_next")
        self.assertIn("bounded no-storage provider probe", decision)

    def test_subcluster_priority_marks_doi_resolver_routes_for_gold(self):
        status, band, decision = subcluster_priority(
            "missing_pdf_harvest",
            "elsevier",
            "doi.org",
            "doi.org:/:doi/:id",
        )

        self.assertEqual(status, "doi_resolver_pdf_route_needs_gold")
        self.assertEqual(band, "browserbase_or_zyte_gold_first")
        self.assertIn("Resolve the DOI route", decision)

    def test_residual_host_prefers_existing_non_unknown_host(self):
        item = pdf_row(
            "10.1/a",
            "missing_pdf_harvest",
            "springer",
            host="stored.example.org",
            candidate_url="https://link.springer.com/content/pdf/10.1/a.pdf",
        )

        self.assertEqual(residual_host(item), "stored.example.org")

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
                pdf_row(
                    "10.1/c",
                    "missing_pdf_harvest",
                    "springer",
                    candidate_url="https://link.springer.com/content/pdf/10.1/c.pdf",
                ).to_dict(),
            ]
            rows_path.write_text("\n".join(json.dumps(item) for item in rows) + "\n")

            paths = write_cluster_artifacts(rows_path, out_dir, run_id="cluster-test", sample_size=1, top_n=10)

            payload = json.loads(paths["clusters_json"].read_text())
            subcluster_payload = json.loads(paths["subclusters_json"].read_text())
            self.assertEqual(payload["run_id"], "cluster-test")
            self.assertEqual(payload["non_good_rows"], 3)
            self.assertEqual(subcluster_payload["run_id"], "cluster-test")
            self.assertGreaterEqual(subcluster_payload["subcluster_count"], 1)
            springer_subcluster = next(
                item
                for item in subcluster_payload["top_subclusters"]
                if item["path_pattern"].startswith("link.springer.com:/content/pdf/")
            )
            self.assertEqual(springer_subcluster["prior_evidence_status"], "prior_negative_or_support_evidence")
            self.assertIn("link.springer.com", paths["clusters_csv"].read_text())
            self.assertIn("path_pattern", paths["subclusters_csv"].read_text())
            self.assertIn("priority_band", paths["subclusters_csv"].read_text())
            self.assertTrue(paths["clusters_csv"].exists())
            self.assertTrue(paths["subclusters_csv"].exists())
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
