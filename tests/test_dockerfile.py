from pathlib import Path
import unittest


class DockerfileTests(unittest.TestCase):
    def test_gunicorn_uses_threaded_workers_for_health_check_headroom(self):
        dockerfile = Path(__file__).resolve().parents[1] / "Dockerfile"
        text = dockerfile.read_text()

        self.assertIn('"gunicorn"', text)
        self.assertIn('"--worker-class", "gthread"', text)
        self.assertIn('"--threads", "4"', text)
        self.assertIn('"--workers", "4"', text)


if __name__ == "__main__":
    unittest.main()
