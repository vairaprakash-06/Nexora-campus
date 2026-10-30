"""Offline unit tests for the Nexora Campus Agent & Tools."""
import unittest
from agent.core import AgentExecutor
from agent.llm import DryRunLLM
from tools import build_tools

class TestAgent(unittest.TestCase):
    def setUp(self):
        self.tools = build_tools()
        self.llm = DryRunLLM()
        self.agent = AgentExecutor(self.llm, self.tools)

    def test_dry_run_basic(self):
        answer, trace = self.agent.run("test", verbose=False)
        self.assertIn("Dry run OK", answer)
        self.assertTrue(len(trace) >= 1)

    def test_dry_run_campus_disruption(self):
        query = "AI Lab 01 is unavailable on Monday from 09:00 AM to 11:00 AM because of equipment failure."
        answer, trace = self.agent.run(query, verbose=False)
        self.assertIn("AI Lab 01", answer)
        self.assertIn("AI-LAB-02", answer)
        self.assertTrue(any(t["tool"] == "solve_campus_recovery" for t in trace))

    def test_tools_registered(self):
        self.assertIn("scan_campus_disruptions", self.tools)
        self.assertIn("solve_campus_recovery", self.tools)
        self.assertIn("calculator", self.tools)
        self.assertIn("list_files", self.tools)

if __name__ == "__main__":
    unittest.main()
