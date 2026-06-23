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
    build_review_pack,
    build_review_queue,
    classify_review_note,
    generate_availability_rows,
    label_pdf_availability,
    read_evidence_rows,
    read_sidecar,
    sanitize_url_for_artifact,
    summarize_public_true_failures,
    summarize_review_pack,
    summarize_review_queue,
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

    def test_auth_wall_notes_are_all_known_but_not_public(self):
        label = label_pdf_availability(
            {
                "DOI": "10.5555/authwall",
                "PDF URL": "https://link.springer.com/content/pdf/10.5555/authwall.pdf",
                "Notes": "closed_at=tier_a_reharvest;verdict=auth_wall_confirmed",
            },
            checked_at="2026-06-23T00:00:00+00:00",
        )
        self.assertEqual(label.pdf_gold_status, "paywalled_or_login_pdf_available")
        self.assertEqual(label.pdf_gold_access_type, "institution_login")
        self.assertEqual(label.pdf_gold_include_in_public_denominator, DENOM_FALSE)
        self.assertEqual(label.pdf_gold_include_in_all_known_pdf_denominator, DENOM_TRUE)
        self.assertEqual(label.pdf_gold_review_needed, "FALSE")

    def test_paywalled_notes_are_all_known_but_not_public(self):
        label = label_pdf_availability(
            {
                "DOI": "10.5555/paywalled",
                "PDF URL": "https://onlinelibrary.wiley.com/doi/pdf/10.5555/paywalled",
                "Notes": "iter-R:paywalled=wiley",
            },
            checked_at="2026-06-23T00:00:00+00:00",
        )
        self.assertEqual(label.pdf_gold_status, "paywalled_or_login_pdf_available")
        self.assertEqual(label.pdf_gold_include_in_public_denominator, DENOM_FALSE)
        self.assertEqual(label.pdf_gold_include_in_all_known_pdf_denominator, DENOM_TRUE)
        self.assertEqual(label.pdf_gold_review_needed, "FALSE")

    def test_auth_wall_without_pdf_url_is_not_all_known_pdf(self):
        label = label_pdf_availability(
            {
                "DOI": "10.5555/authwall-no-url",
                "Link": "https://doi.org/10.5555/authwall-no-url",
                "Notes": "closed_at=tier_a_reharvest;verdict=auth_wall_confirmed",
            },
            checked_at="2026-06-23T00:00:00+00:00",
        )
        self.assertEqual(label.pdf_gold_status, "no_full_text_pdf_found")
        self.assertEqual(label.pdf_gold_include_in_public_denominator, DENOM_FALSE)
        self.assertEqual(label.pdf_gold_include_in_all_known_pdf_denominator, DENOM_FALSE)
        self.assertEqual(label.pdf_gold_review_needed, "FALSE")

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

    def test_no_pdf_expected_without_pdf_url_beats_bot_review(self):
        label = label_pdf_availability(
            {
                "DOI": "10.5555/no-pdf-bot-page",
                "Link": "https://doi.org/10.5555/no-pdf-bot-page",
                "Has Bot Check": "TRUE",
                "Notes": "closed_at=tier_b_local_chrome;verdict=approved",
            },
            eval_row={
                "doi": "10.5555/no-pdf-bot-page",
                "category": "no_pdf_expected",
            },
            checked_at="2026-06-23T00:00:00+00:00",
        )
        self.assertEqual(label.pdf_gold_status, "no_full_text_pdf_found")
        self.assertEqual(label.pdf_gold_include_in_public_denominator, DENOM_FALSE)
        self.assertEqual(label.pdf_gold_include_in_all_known_pdf_denominator, DENOM_FALSE)
        self.assertEqual(label.pdf_gold_review_needed, "FALSE")

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

    def test_provider_paywall_evidence_moves_missing_row_out_of_review(self):
        label = label_pdf_availability(
            {
                "DOI": "10.5555/provider-paywall",
                "PDF URL": "https://link.springer.com/content/pdf/10.5555/provider-paywall.pdf",
            },
            eval_row={
                "doi": "10.5555/provider-paywall",
                "category": "missing_pdf_harvest",
            },
            evidence_row={
                "doi": "10.5555/provider-paywall",
                "category": "interstitial_or_paywall",
                "candidate_url": "https://link.springer.com/content/pdf/10.5555/provider-paywall.pdf",
            },
            checked_at="2026-06-23T00:00:00+00:00",
        )
        self.assertEqual(label.pdf_gold_status, "paywalled_or_login_pdf_available")
        self.assertEqual(label.pdf_gold_include_in_public_denominator, DENOM_FALSE)
        self.assertEqual(label.pdf_gold_include_in_all_known_pdf_denominator, DENOM_TRUE)
        self.assertEqual(label.pdf_gold_review_needed, "FALSE")
        self.assertIn("provider_evidence_category=interstitial_or_paywall", label.pdf_gold_evidence)

    def test_provider_good_pdf_evidence_beats_raw_missing_row(self):
        label = label_pdf_availability(
            {
                "DOI": "10.5555/provider-good",
                "PDF URL": "https://example.org/full.pdf",
            },
            eval_row={
                "doi": "10.5555/provider-good",
                "category": "missing_pdf_harvest",
            },
            evidence_row={
                "doi": "10.5555/provider-good",
                "category": "good_pdf",
                "candidate_url": "https://example.org/full.pdf",
            },
            checked_at="2026-06-23T00:00:00+00:00",
        )
        self.assertEqual(label.pdf_gold_status, "open_full_text_pdf_available")
        self.assertEqual(label.pdf_gold_include_in_public_denominator, DENOM_TRUE)
        self.assertEqual(label.pdf_gold_include_in_all_known_pdf_denominator, DENOM_TRUE)
        self.assertEqual(label.pdf_gold_review_needed, "FALSE")

    def test_read_evidence_rows_keeps_best_strategy_row_per_doi(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rows.ndjson"
            path.write_text(
                "\n".join(
                    [
                        json.dumps({"doi": "10.5555/evidence", "category": "interstitial_or_paywall"}),
                        json.dumps({"doi": "10.5555/evidence", "category": "good_pdf"}),
                        json.dumps({"doi": "10.5555/other", "category": "bot_block_403"}),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            rows = read_evidence_rows([path])
        self.assertEqual(rows["10.5555/evidence"]["category"], "good_pdf")
        self.assertEqual(rows["10.5555/other"]["category"], "bot_block_403")

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

    def test_review_queue_summary_explains_goldie_approved_notes_without_relabeling(self):
        rows = [
            {
                "pdf_gold_status": "unclear_needs_review",
                "pdf_gold_access_type": "unknown",
                "pdf_gold_review_reason": "raw expected PDF miss needs gold availability review before denominator exclusion",
                "pdf_gold_host": "link.springer.com",
                "latest_taxicab_category": "missing_pdf_harvest",
                "Notes": "closed_at=tier_a_reharvest;verdict=approved",
            },
            {
                "pdf_gold_status": "unclear_needs_review",
                "pdf_gold_access_type": "unknown",
                "pdf_gold_review_reason": "raw expected PDF miss needs gold availability review before denominator exclusion",
                "pdf_gold_host": "link.springer.com",
                "latest_taxicab_category": "missing_pdf_harvest",
                "Notes": "",
            },
            {
                "pdf_gold_status": "unclear_needs_review",
                "pdf_gold_access_type": "js_required",
                "pdf_gold_review_reason": "JS flow needs browser/gold evidence before denominator decision",
                "pdf_gold_host": "europepmc.org",
                "latest_taxicab_category": "js_redirect_unresolved",
                "Notes": "closed_at=terminal;verdict=needs_live_fetch",
            },
        ]
        summary = summarize_review_queue(rows)
        self.assertEqual(summary["total"], 3)
        self.assertEqual(
            summary["note_class_counts"]["goldie_content_approved_not_pdf_availability"],
            1,
        )
        self.assertEqual(summary["note_class_counts"]["no_existing_note"], 1)
        self.assertEqual(summary["top_hosts"][0]["host"], "link.springer.com")
        self.assertIn("does not prove", summary["top_hosts"][0]["why_not_recovered_yet"])
        self.assertEqual(classify_review_note("closed_at=tier_a_reharvest;verdict=approved"), "goldie_content_approved_not_pdf_availability")

    def test_review_pack_stratifies_top_hosts_without_relabeling(self):
        rows = [
            {
                "DOI": "10.5555/springer-a",
                "pdf_gold_host": "link.springer.com",
                "pdf_gold_priority_host_count": "4",
                "latest_taxicab_category": "missing_pdf_harvest",
                "Notes": "",
            },
            {
                "DOI": "10.5555/springer-b",
                "pdf_gold_host": "link.springer.com",
                "pdf_gold_priority_host_count": "4",
                "latest_taxicab_category": "missing_pdf_harvest",
                "Notes": "closed_at=tier_a_reharvest;verdict=approved",
            },
            {
                "DOI": "10.5555/springer-c",
                "pdf_gold_host": "link.springer.com",
                "pdf_gold_priority_host_count": "4",
                "latest_taxicab_category": "html_instead_of_pdf",
                "Notes": "closed_at=tier_a_reharvest;verdict=approved",
            },
            {
                "DOI": "10.5555/wiley-a",
                "pdf_gold_host": "onlinelibrary.wiley.com",
                "pdf_gold_priority_host_count": "2",
                "latest_taxicab_category": "missing_pdf_harvest",
                "Notes": "",
            },
            {
                "DOI": "10.5555/wiley-b",
                "pdf_gold_host": "onlinelibrary.wiley.com",
                "pdf_gold_priority_host_count": "2",
                "latest_taxicab_category": "missing_pdf_harvest",
                "Notes": "closed_at=terminal;verdict=needs_live_fetch",
            },
        ]
        pack = build_review_pack(rows, max_rows=3, per_host=2)
        self.assertEqual(len(pack), 3)
        self.assertEqual([row["review_pack_rank"] for row in pack], [1, 2, 3])
        self.assertEqual([row["pdf_gold_host"] for row in pack[:2]], ["link.springer.com", "link.springer.com"])
        self.assertIn("review_pack_next_action", pack[0])
        self.assertEqual(
            {row["review_note_class"] for row in pack[:2]},
            {"no_existing_note", "goldie_content_approved_not_pdf_availability"},
        )
        summary = summarize_review_pack(pack)
        self.assertEqual(summary["total"], 3)
        self.assertEqual(summary["top_hosts"][0]["host"], "link.springer.com")

    def test_sidecar_cli_writes_draft_and_review_queue(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_csv = tmp_path / "human-goldie.csv"
            eval_rows = tmp_path / "rows.ndjson"
            draft = tmp_path / "human-goldie-pdf-availability.draft.csv"
            review = tmp_path / "human-goldie-pdf-review-queue.csv"
            summary = tmp_path / "summary.json"
            review_summary = tmp_path / "review-summary.json"
            review_pack = tmp_path / "review-pack.csv"
            review_pack_summary = tmp_path / "review-pack-summary.json"
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
                        "--review-summary-json",
                        str(review_summary),
                        "--review-pack-out",
                        str(review_pack),
                        "--review-pack-summary-json",
                        str(review_pack_summary),
                        "--review-pack-size",
                        "10",
                        "--review-pack-per-host",
                        "2",
                        "--public-true-failures-out",
                        str(public_true_failures),
                        "--public-true-failures-summary-json",
                        str(public_true_summary),
                    ]
                )
            self.assertEqual(code, 0)
            self.assertTrue(draft.exists())
            self.assertTrue(review.exists())
            self.assertTrue(review_summary.exists())
            self.assertTrue(review_pack.exists())
            self.assertTrue(review_pack_summary.exists())
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
            self.assertEqual(summary_data["review_queue_summary"]["total"], 1)
            review_summary_data = json.loads(review_summary.read_text())
            self.assertEqual(review_summary_data["total"], 1)
            with review_pack.open(encoding="utf-8") as handle:
                pack_rows = list(csv.DictReader(handle))
            self.assertEqual(len(pack_rows), 1)
            self.assertEqual(pack_rows[0]["review_pack_rank"], "1")
            review_pack_summary_data = json.loads(review_pack_summary.read_text())
            self.assertEqual(review_pack_summary_data["total"], 1)
            self.assertEqual(summary_data["review_pack_total"], 1)
            self.assertEqual(summary_data["public_true_failure_total"], 1)
            public_summary_data = json.loads(public_true_summary.read_text())
            self.assertEqual(public_summary_data["total"], 1)

    def test_sidecar_cli_can_build_review_pack_from_existing_queue(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            review_queue = tmp_path / "review-queue.csv"
            review_pack = tmp_path / "review-pack.csv"
            review_pack_summary = tmp_path / "review-pack-summary.json"
            with review_queue.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=[
                        *PDF_AVAILABILITY_FIELDS,
                        "pdf_gold_priority_host_count",
                        "pdf_gold_host",
                        "latest_taxicab_category",
                        "Link",
                        "PDF URL",
                        "Notes",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "DOI": "10.5555/review-a",
                        "pdf_gold_status": "unclear_needs_review",
                        "pdf_gold_host": "link.springer.com",
                        "latest_taxicab_category": "missing_pdf_harvest",
                        "Notes": "",
                    }
                )
                writer.writerow(
                    {
                        "DOI": "10.5555/review-b",
                        "pdf_gold_status": "unclear_needs_review",
                        "pdf_gold_host": "link.springer.com",
                        "latest_taxicab_category": "missing_pdf_harvest",
                        "Notes": "closed_at=tier_a_reharvest;verdict=approved",
                    }
                )
            with contextlib.redirect_stdout(io.StringIO()):
                code = sidecar_main(
                    [
                        "--review-pack-from-queue",
                        str(review_queue),
                        "--review-pack-out",
                        str(review_pack),
                        "--review-pack-summary-json",
                        str(review_pack_summary),
                        "--review-pack-size",
                        "10",
                        "--review-pack-per-host",
                        "2",
                    ]
                )
            self.assertEqual(code, 0)
            with review_pack.open(encoding="utf-8") as handle:
                pack_rows = list(csv.DictReader(handle))
            self.assertEqual(len(pack_rows), 2)
            summary_data = json.loads(review_pack_summary.read_text())
            self.assertEqual(summary_data["review_queue_total"], 2)
            self.assertEqual(summary_data["total"], 2)

    def test_csv_writer_sanitizes_control_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "rows.csv"
            write_csv_rows(out, [{"DOI": "10.5555/control", "evidence": "\x14U\x00bad\nline"}], ["DOI", "evidence"])
            text = out.read_text(encoding="utf-8")
            self.assertNotIn("\x14", text)
            self.assertNotIn("\x00", text)
            self.assertIn("U bad line", text)

    def test_csv_writer_strips_signed_and_challenge_url_material(self):
        amz = "X-Amz-"
        bm = "bm-" "verify"
        challenge_host = "hcvalidate" ".perfdrive.com"
        signed_url = (
            "https://pdf.sciencedirectassets.com/main.pdf?"
            f"{amz}Algorithm=AWS4-HMAC-SHA256&{amz}Credential=secret&"
            f"{amz}Security-Token=token&{amz}Signature=signature&pid=S123"
        )
        challenge_url = f"https://{challenge_host}/?ssa=challenge-token"
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "rows.csv"
            write_csv_rows(
                out,
                [
                    {
                        "DOI": "10.5555/signed",
                        "pdf_gold_url": signed_url,
                        "PDF URL": signed_url,
                        "Link": challenge_url,
                        "Notes": f"blocked by {bm}=challengevalue and {signed_url}",
                    }
                ],
                ["DOI", "pdf_gold_url", "PDF URL", "Link", "Notes"],
            )
            text = out.read_text(encoding="utf-8")
            self.assertIn("https://pdf.sciencedirectassets.com/main.pdf", text)
            self.assertIn("https://hcvalidate.perfdrive.com/", text)
            self.assertNotIn("X-Amz-", text)
            self.assertNotIn("secret", text)
            self.assertNotIn("signature", text)
            self.assertNotIn("challenge-token", text)
            self.assertNotIn(f"{challenge_host}/?ssa=", text)
            self.assertNotIn(f"{bm}=challengevalue", text)

    def test_url_sanitizer_keeps_safe_query_but_strips_signed_query(self):
        amz = "X-Amz-"
        self.assertEqual(
            sanitize_url_for_artifact("https://example.org/full.pdf?download=1"),
            "https://example.org/full.pdf?download=1",
        )
        self.assertEqual(
            sanitize_url_for_artifact(f"https://example.org/full.pdf?{amz}Signature=secret&download=1#page=2"),
            "https://example.org/full.pdf",
        )


if __name__ == "__main__":
    unittest.main()
