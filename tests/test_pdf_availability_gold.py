import csv
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from openalex_taxicab.pdf_availability_gold import (
    DENOM_FALSE,
    DENOM_REVIEW,
    DENOM_TRUE,
    PDF_AVAILABILITY_FIELDS,
    build_public_true_failure_queue,
    build_review_queue,
    generate_availability_rows,
    label_pdf_availability,
    read_sidecar,
    summarize_public_true_failures,
    write_csv_rows,
)
from openalex_taxicab.pdf_eval_harness import make_pdf_transport_row, summarize_pdf_rows
from scripts.pdf_availability_gold import main as sidecar_main


class PdfAvailabilityGoldTest(unittest.TestCase):
    def test_good_pdf_eval_row_is_public_denominator_true(self):
        label = label_pdf_availability(
            {"DOI": "10.5555/good", "PDF URL": "https://example.org/full.pdf"},
            eval_row={"doi": "10.5555/good", "category": "good_pdf"},
            checked_at="2026-06-23T00:00:00+00:00",
        )
        self.assertEqual(label.pdf_gold_status, "open_full_text_pdf_available")
        self.assertEqual(label.pdf_gold_include_in_public_denominator, DENOM_TRUE)
        self.assertEqual(label.pdf_gold_include_in_all_known_pdf_denominator, DENOM_TRUE)
        self.assertEqual(label.pdf_gold_review_needed, "FALSE")

    def test_paywalled_pdf_is_all_known_but_not_public(self):
        label = label_pdf_availability(
            {
                "DOI": "10.5555/paywall",
                "PDF URL": "https://publisher.example/full.pdf",
                "Notes": "Get access. Log into your institution or buy now.",
            },
            checked_at="2026-06-23T00:00:00+00:00",
        )
        self.assertEqual(label.pdf_gold_status, "paywalled_or_login_pdf_available")
        self.assertEqual(label.pdf_gold_include_in_public_denominator, DENOM_FALSE)
        self.assertEqual(label.pdf_gold_include_in_all_known_pdf_denominator, DENOM_TRUE)
        self.assertIn(label.pdf_gold_access_type, {"institution_login", "purchase_page"})

    def test_bot_check_goes_to_review(self):
        label = label_pdf_availability(
            {
                "DOI": "10.5555/bot",
                "PDF URL": "https://publisher.example/full.pdf",
                "Has Bot Check": "TRUE",
                "Notes": "The PDF link takes to a bot check directly.",
            },
            checked_at="2026-06-23T00:00:00+00:00",
        )
        self.assertEqual(label.pdf_gold_status, "unclear_needs_review")
        self.assertEqual(label.pdf_gold_include_in_public_denominator, DENOM_REVIEW)
        self.assertEqual(label.pdf_gold_review_needed, "TRUE")

    def test_missing_pdf_harvest_stays_review_without_explicit_no_pdf_evidence(self):
        label = label_pdf_availability(
            {
                "DOI": "10.5555/missing",
                "PDF URL": "https://publisher.example/full.pdf",
                "Has Bot Check": "FALSE",
                "Resolves To PDF": "FALSE",
            },
            eval_row={
                "doi": "10.5555/missing",
                "category": "missing_pdf_harvest",
                "error": "no pdf records",
                "evidence_snippet": "no pdf records",
            },
            checked_at="2026-06-23T00:00:00+00:00",
        )
        self.assertEqual(label.pdf_gold_status, "unclear_needs_review")
        self.assertEqual(label.pdf_gold_include_in_public_denominator, DENOM_REVIEW)
        self.assertIn("raw expected PDF miss", label.pdf_gold_review_reason)

    def test_seed_sidecar_label_is_reused(self):
        seed = {
            field: ""
            for field in PDF_AVAILABILITY_FIELDS
        }
        seed.update(
            {
                "DOI": "10.5555/seed",
                "pdf_gold_status": "html_full_text_only",
                "pdf_gold_include_in_public_denominator": DENOM_FALSE,
                "pdf_gold_include_in_all_known_pdf_denominator": DENOM_FALSE,
            }
        )
        label = label_pdf_availability(
            {"DOI": "https://doi.org/10.5555/seed", "PDF URL": "https://example.org/ignored.pdf"},
            seed_label=seed,
            checked_at="2026-06-23T00:00:00+00:00",
        )
        self.assertEqual(label.DOI, "10.5555/seed")
        self.assertEqual(label.pdf_gold_status, "html_full_text_only")
        self.assertEqual(label.pdf_gold_source, "seed_sidecar")

    def test_summary_reports_raw_public_and_all_known_metrics(self):
        rows = [
            make_pdf_transport_row(run_id="test", doi="10.5555/good", category="good_pdf"),
            make_pdf_transport_row(run_id="test", doi="10.5555/missing", category="missing_pdf_harvest"),
            make_pdf_transport_row(run_id="test", doi="10.5555/paywall", category="missing_pdf_harvest"),
            make_pdf_transport_row(run_id="test", doi="10.5555/review", category="missing_pdf_harvest"),
        ]
        sidecar = {
            "10.5555/good": {
                "pdf_gold_status": "open_full_text_pdf_available",
                "pdf_gold_include_in_public_denominator": DENOM_TRUE,
                "pdf_gold_include_in_all_known_pdf_denominator": DENOM_TRUE,
            },
            "10.5555/missing": {
                "pdf_gold_status": "open_full_text_pdf_available",
                "pdf_gold_include_in_public_denominator": DENOM_TRUE,
                "pdf_gold_include_in_all_known_pdf_denominator": DENOM_TRUE,
            },
            "10.5555/paywall": {
                "pdf_gold_status": "paywalled_or_login_pdf_available",
                "pdf_gold_include_in_public_denominator": DENOM_FALSE,
                "pdf_gold_include_in_all_known_pdf_denominator": DENOM_TRUE,
            },
            "10.5555/review": {
                "pdf_gold_status": "unclear_needs_review",
                "pdf_gold_include_in_public_denominator": DENOM_REVIEW,
                "pdf_gold_include_in_all_known_pdf_denominator": DENOM_REVIEW,
            },
        }
        summary = summarize_pdf_rows(rows, run_id="test", pdf_availability_by_doi=sidecar, pdf_availability_source="sidecar.csv")
        self.assertEqual(summary["raw_pdf_candidate_total"], 4)
        self.assertEqual(summary["raw_good_pdf"], 1)
        self.assertEqual(summary["public_pdf_denominator_total"], 2)
        self.assertEqual(summary["public_good_pdf"], 1)
        self.assertEqual(summary["all_known_pdf_denominator_total"], 3)
        self.assertEqual(summary["all_known_good_pdf"], 1)
        self.assertEqual(summary["pdf_gold_false_total"], 1)
        self.assertEqual(summary["pdf_gold_review_total"], 1)
        self.assertEqual(summary["excluded_by_pdf_gold_status"]["paywalled_or_login_pdf_available"], 1)

    def test_public_true_failure_queue_filters_to_latest_non_good(self):
        labels = generate_availability_rows(
            [
                {"DOI": "10.5555/good", "PDF URL": "https://example.org/good.pdf", "Resolves To PDF": "TRUE"},
                {"DOI": "10.5555/corrupt", "PDF URL": "https://onlinelibrary.wiley.com/full.pdf", "Resolves To PDF": "TRUE"},
                {"DOI": "10.5555/paywall", "PDF URL": "https://publisher.example/full.pdf", "Notes": "Get access"},
                {"DOI": "10.5555/review", "PDF URL": "https://publisher.example/review.pdf"},
            ],
            eval_rows_by_doi={
                "10.5555/good": {"doi": "10.5555/good", "category": "good_pdf"},
                "10.5555/corrupt": {
                    "doi": "10.5555/corrupt",
                    "category": "corrupt_or_truncated_pdf",
                    "publisher": "wiley",
                    "host": "",
                    "candidate_url": "https://onlinelibrary.wiley.com/doi/pdf/10.5555/corrupt",
                    "validation_errors": ["PdfReadError"],
                },
                "10.5555/paywall": {"doi": "10.5555/paywall", "category": "missing_pdf_harvest"},
                "10.5555/review": {"doi": "10.5555/review", "category": "missing_pdf_harvest"},
            },
            checked_at="2026-06-23T00:00:00+00:00",
        )
        queue = build_public_true_failure_queue(
            labels,
            eval_rows_by_doi={
                "10.5555/good": {"doi": "10.5555/good", "category": "good_pdf"},
                "10.5555/corrupt": {
                    "doi": "10.5555/corrupt",
                    "category": "corrupt_or_truncated_pdf",
                    "publisher": "wiley",
                    "host": "",
                    "candidate_url": "https://onlinelibrary.wiley.com/doi/pdf/10.5555/corrupt",
                    "validation_errors": ["PdfReadError"],
                },
                "10.5555/paywall": {"doi": "10.5555/paywall", "category": "missing_pdf_harvest"},
                "10.5555/review": {"doi": "10.5555/review", "category": "missing_pdf_harvest"},
            },
        )
        self.assertEqual([row["DOI"] for row in queue], ["10.5555/corrupt"])
        self.assertEqual(queue[0]["host"], "onlinelibrary.wiley.com")
        self.assertEqual(queue[0]["validation_errors"], "PdfReadError")
        summary = summarize_public_true_failures(queue)
        self.assertEqual(summary["total"], 1)
        self.assertEqual(summary["category_counts"]["corrupt_or_truncated_pdf"], 1)
        self.assertEqual(summary["top_hosts"][0]["host"], "onlinelibrary.wiley.com")

    def test_sidecar_cli_writes_draft_and_review_queue(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_csv = tmp_path / "human-goldie.csv"
            eval_rows = tmp_path / "rows.ndjson"
            draft = tmp_path / "human-goldie-pdf-availability.draft.csv"
            review = tmp_path / "human-goldie-pdf-review-queue.csv"
            summary = tmp_path / "summary.json"
            public_true_failures = tmp_path / "public-true-failures.csv"
            public_true_summary = tmp_path / "public-true-failures-summary.json"
            with input_csv.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["DOI", "Link", "PDF URL", "Notes", "Has Bot Check", "Resolves To PDF", "broken_doi"],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "DOI": "10.5555/good",
                        "Link": "https://doi.org/10.5555/good",
                        "PDF URL": "https://example.org/good.pdf",
                        "Notes": "",
                        "Has Bot Check": "FALSE",
                        "Resolves To PDF": "TRUE",
                        "broken_doi": "FALSE",
                    }
                )
                writer.writerow(
                    {
                        "DOI": "10.5555/bot",
                        "Link": "https://doi.org/10.5555/bot",
                        "PDF URL": "https://example.org/bot.pdf",
                        "Notes": "bot check",
                        "Has Bot Check": "TRUE",
                        "Resolves To PDF": "FALSE",
                        "broken_doi": "FALSE",
                    }
                )
                writer.writerow(
                    {
                        "DOI": "10.5555/corrupt",
                        "Link": "https://doi.org/10.5555/corrupt",
                        "PDF URL": "https://onlinelibrary.wiley.com/doi/pdf/10.5555/corrupt",
                        "Notes": "",
                        "Has Bot Check": "FALSE",
                        "Resolves To PDF": "TRUE",
                        "broken_doi": "FALSE",
                    }
                )
            eval_rows.write_text(
                "\n".join(
                    [
                        json.dumps({"doi": "10.5555/good", "category": "good_pdf"}),
                        json.dumps(
                            {
                                "doi": "10.5555/corrupt",
                                "category": "corrupt_or_truncated_pdf",
                                "publisher": "wiley",
                                "candidate_url": "https://onlinelibrary.wiley.com/doi/pdf/10.5555/corrupt",
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            with contextlib.redirect_stdout(io.StringIO()):
                code = sidecar_main(
                    [
                        "--input",
                        str(input_csv),
                        "--out",
                        str(draft),
                        "--review-queue",
                        str(review),
                        "--eval-rows",
                        str(eval_rows),
                        "--summary-json",
                        str(summary),
                        "--public-true-failures-out",
                        str(public_true_failures),
                        "--public-true-failures-summary-json",
                        str(public_true_summary),
                    ]
                )
            self.assertEqual(code, 0)
            self.assertTrue(draft.exists())
            self.assertTrue(review.exists())
            self.assertTrue(public_true_failures.exists())
            self.assertTrue(public_true_summary.exists())
            self.assertEqual(len(read_sidecar(draft)), 3)
            with review.open(encoding="utf-8") as handle:
                self.assertEqual(len(list(csv.DictReader(handle))), 1)
            with public_true_failures.open(encoding="utf-8") as handle:
                failure_rows = list(csv.DictReader(handle))
            self.assertEqual(len(failure_rows), 1)
            self.assertEqual(failure_rows[0]["DOI"], "10.5555/corrupt")
            summary_data = json.loads(summary.read_text())
            self.assertEqual(summary_data["review_queue_total"], 1)
            self.assertEqual(summary_data["public_true_failure_total"], 1)
            public_summary_data = json.loads(public_true_summary.read_text())
            self.assertEqual(public_summary_data["total"], 1)

    def test_csv_writer_sanitizes_control_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "rows.csv"
            write_csv_rows(out, [{"DOI": "10.5555/control", "evidence": "\x14U\x00bad\nline"}], ["DOI", "evidence"])
            text = out.read_text(encoding="utf-8")
            self.assertNotIn("\x14", text)
            self.assertNotIn("\x00", text)
            self.assertIn("U bad line", text)


if __name__ == "__main__":
    unittest.main()
