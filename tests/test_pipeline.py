"""End-to-end test on synthetic NSE data (no network): scanner -> entry -> exit ->
time machine -> budget -> risk -> log, plus the NSE-specific rules.

    python3 -m unittest discover -s tests
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def script(skill, name):
    return os.path.join(ROOT, skill, name)


class Pipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.fx = os.path.join(cls.tmp, "fx")
        subprocess.run([sys.executable, "-I", os.path.join(HERE, "make_fixtures.py"), cls.fx], check=True,
                       capture_output=True)
        cls.work = os.path.join(cls.tmp, "work")
        os.makedirs(os.path.join(cls.work, "nse"))
        shutil.copy(script("nse-budget", "config.example.json"), os.path.join(cls.work, "nse", "config.json"))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def run_py(self, skill, name, *args):
        p = subprocess.run([sys.executable, "-I", script(skill, name)] + list(args), cwd=self.work,
                           capture_output=True, text=True)
        return p.returncode, p.stdout + p.stderr

    def test_1_universe_drops_indices(self):
        code, out = self.run_py("nse-scanner", "scan.py", "universe", "--offline", os.path.join(self.fx, "fo_mktlots.csv"))
        self.assertEqual(code, 0, out)
        syms = [l.split("|")[0] for l in open(os.path.join(self.work, "nse", "universe.txt"))]
        self.assertIn("M&M", syms)
        self.assertIn("BAJAJ-AUTO", syms)
        self.assertNotIn("NIFTY", syms)
        self.assertNotIn("BANKNIFTY", syms)

    def test_2_orb_scan_ist(self):
        code, out = self.run_py("nse-scanner", "scan.py", "orb", "--offline", os.path.join(self.fx, "intraday"),
                                "--now", "2026-10-28 10:30", "--no-write")
        self.assertEqual(code, 0, out)
        self.assertIn("9:15 to 9:30 AM", out)

    def test_3_holiday_and_early(self):
        code, out = self.run_py("nse-scanner", "scan.py", "orb", "--offline", os.path.join(self.fx, "intraday"),
                                "--now", "2026-11-10 10:30", "--no-write")
        self.assertEqual(code, 1)
        self.assertIn("Diwali", out)
        code, out = self.run_py("nse-scanner", "scan.py", "orb", "--offline", os.path.join(self.fx, "intraday"),
                                "--now", "2026-10-28 09:25", "--no-write")
        self.assertIn("9:35 AM", out)

    def test_4_full_trade(self):
        now = "2026-10-28 09:36"
        intraday = os.path.join(self.fx, "intraday")
        code, out = self.run_py("nse-entry", "entry.py", "check", "M&M", "--now", now, "--offline", intraday, "--write")
        self.assertEqual(code, 0, out)
        self.assertEqual(json.load(open(os.path.join(self.work, "nse", "entry.json")))["symbol"], "M&M")
        code, out = self.run_py("nse-exit", "exit.py", "plan", "--now", now, "--offline", intraday, "--write")
        self.assertEqual(code, 0, out)
        plan = json.load(open(os.path.join(self.work, "nse", "plan.json")))
        for k in ("stop", "target"):  # on the 0.10 tick for a ~1,480 stock
            v = float(plan[k])
            self.assertAlmostEqual(round(v / 0.10) * 0.10, v, places=6)
        code, out = self.run_py("nse-timemachine", "timemachine.py", "run", "--now", now,
                                "--offline", os.path.join(intraday, "M&M.NS.json"))
        self.assertEqual(code, 0, out)
        self.assertIn("3:30 PM", out)
        code, out = self.run_py("nse-budget", "size.py", "--now", now, "--write")
        self.assertEqual(code, 0, out)
        self.assertIn("SL-M", out)
        order = json.load(open(os.path.join(self.work, "nse", "orders.json")))["orders"][0]
        self.assertEqual(order["kite"][0]["product"], "MIS")
        code, out = self.run_py("nse-risk", "check.py", "--now", now)
        self.assertEqual(code, 0, out)
        code, out = self.run_py("nse-risk", "log.py", "--now", "2026-10-28T04:07:00Z", "placed")
        self.assertEqual(code, 0, out)
        code, out = self.run_py("nse-risk", "check.py", "--now", "2026-10-28 09:40", "--no-write")
        self.assertEqual(code, 1)
        self.assertIn("duplicate", out)
        code, out = self.run_py("nse-risk", "check.py", "--now", "2026-10-28 15:00", "--no-write")
        self.assertIn("no new entries after 14:45", out)

    def test_5_off_tick_blocked(self):
        path = os.path.join(self.work, "nse", "orders.json")
        if not os.path.exists(path):
            self.skipTest("needs test_4")
        with open(path) as fh:
            doc = json.load(fh)
        doc["orders"][0]["stop_loss_stop_price"] = "1474.53"
        bad = os.path.join(self.work, "bad.json")
        with open(bad, "w") as fh:
            json.dump(doc, fh)
        code, out = self.run_py("nse-risk", "check.py", "--now", "2026-10-28 09:36", "--orders", bad, "--no-write")
        self.assertEqual(code, 1)
        self.assertIn("tick", out)


if __name__ == "__main__":
    unittest.main()
