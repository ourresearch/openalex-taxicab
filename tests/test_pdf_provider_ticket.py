import json
import tempfile
import unittest
from pathlib import Path

from openalex_taxicab.pdf_eval_harness import PdfEvalRow
from openalex_taxicab.pdf_provider_ticket import (
    build_ticket_payload,
    group_provider_lanes,
    render_markdown,
    write_provider_ticket,
)


def pdf_row(
    doi,
    category,
    publisher,
    candidate_url,
    *,
    candidate_source="corpus_pdf_url",
    evidence_snippet="no pdf records",
    validation_errors=None,
):
    return PdfEvalRow(
        run_id="test",
        work_id=f"W{doi}",
        doi=doi,
        category=category,
        publisher=publisher,
        host="",
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
        validation_errors=validation_errors or ["no pdf records"],
        evidence_snippet=evidence_snippet,
        support_candidate=True,
        uuid="",
        pdf_record_count=0,
        duration_ms=1,
        mode="test",
        error="",
    )


class PdfProviderTicketTests(unittest.TestCase):
    def test_groups_residual_rows_by_provider_lane(self):
        rows = [
            pdf_row("10.1/a", "missing_pdf_harvest", "springer", "https://link.springer.com/content/pdf/10.1/a.pdf"),
            pdf_row("10.1/b", "missing_pdf_harvest", "springer", "https://link.springer.com/content/pdf/10.1/b.pdf"),
            pdf_row("10.1/c", "good_pdf", "springer", "https://link.springer.com/content/pdf/10.1/c.pdf"),
        ]

        lanes = group_provider_lanes(rows)

        self.assertEqual(len(lanes), 1)
        self.assertEqual(lanes[0].count, 2)
        self.assertEqual(lanes[0].publisher, "springer")
        self.assertEqual(lanes[0].path_pattern, "link.springer.com:/content/pdf/:doi/:file.pdf")

    def test_payload_redacts_signed_and_challenge_query_values(self):
        signed_query = "X-Amz-" "Signature=secret"
        challenge_query = "bm-" "verify=challenge"
        rows = [
            pdf_row(
                "10.1/a",
                "missing_pdf_harvest",
                "elsevier",
                f"https://pdf.example.org/main.pdf?{signed_query}&{challenge_query}&pii=S1",
                evidence_snippet=f"blocked {challenge_query} {signed_query}",
            )
        ]

        payload = build_ticket_payload(rows, run_id="ticket-test", top_lanes=1, samples_per_lane=1)
        sample = payload["top_lanes"][0]["samples"][0]

        self.assertIn("pii=S1", sample["candidate_url"])
        self.assertIn("redacted=1", sample["candidate_url"])
        payload_text = json.dumps(payload)
        self.assertNotIn(signed_query, payload_text)
        self.assertNotIn(challenge_query, payload_text)

    def test_render_markdown_marks_packet_private(self):
        payload = build_ticket_payload(
            [
                pdf_row(
                    "10.1/a",
                    "corrupt_or_truncated_pdf",
                    "wiley",
                    "https://onlinelibrary.wiley.com/doi/pdfdirect/10.1/a",
                    validation_errors=["no page objects found"],
                )
            ],
            run_id="ticket-test",
            top_lanes=1,
            samples_per_lane=1,
        )

        markdown = render_markdown(payload)

        self.assertIn("Private Taxicab PDF Zyte Provider Ticket", markdown)
        self.assertIn("Do not commit or publish", markdown)
        self.assertIn("no page objects found", markdown)
        self.assertIn("provider_pdf_probe.py", markdown)

    def test_write_provider_ticket_outputs_manifest_and_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            rows_path = tmp_path / "rows.ndjson"
            rows_path.write_text(
                json.dumps(
                    pdf_row(
                        "10.1/a",
                        "missing_pdf_harvest",
                        "springer",
                        "https://link.springer.com/content/pdf/10.1/a.pdf",
                    ).to_dict()
                )
                + "\n",
                encoding="utf-8",
            )

            paths = write_provider_ticket(rows_path, tmp_path / "out", run_id="ticket-test")

            self.assertTrue(paths["manifest"].exists())
            self.assertTrue(paths["packet"].exists())
            self.assertIn("ticket-test", paths["packet"].read_text())


if __name__ == "__main__":
    unittest.main()
