import unittest

from openalex_taxicab.publisher_index import classify_row, domain_to_publisher, doi_prefix, prefix_to_publisher


class PublisherIndexTests(unittest.TestCase):
    def test_supported_prefixes_classify_without_network(self):
        cases = {
            "10.1002/chin.198035056": "wiley",
            "10.1016/j.aftran.2024.100020": "elsevier",
            "10.1088/1742-6596/2853/1/012065": "iop",
            "10.1039/b922668k": "rsc",
            "10.1055/s-2008-1041524": "thieme",
            "10.1159/000277292": "karger",
            "10.2139/ssrn.4398349": "ssrn",
            "10.4324/9780203370469-11": "taylor",
        }
        for doi, publisher in cases.items():
            with self.subTest(doi=doi):
                self.assertEqual(prefix_to_publisher(doi), publisher)
                self.assertEqual(classify_row({"DOI": doi, "Link": f"https://doi.org/{doi}"}), publisher)

    def test_domain_fallback_uses_resolved_url(self):
        row = {"DOI": "10.9999/example", "Link": "https://doi.org/10.9999/example"}
        self.assertEqual(classify_row(row, resolved_url="https://academic.oup.com/article/1"), "oxford")

    def test_unknown_stays_unknown(self):
        self.assertEqual(classify_row({"DOI": "10.9999/unknown", "Link": "https://example.invalid/x"}), "unknown")

    def test_domain_and_prefix_helpers(self):
        self.assertEqual(doi_prefix("https://doi.org/10.1002/example"), "10.1002")
        self.assertEqual(domain_to_publisher("https://www.nature.com/articles/test"), "springer")


if __name__ == "__main__":
    unittest.main()
