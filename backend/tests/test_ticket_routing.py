import unittest

from graph.workflow import get_workflow_policy


class TicketRoutingPolicyTest(unittest.TestCase):
    def test_complex_ticket_triggers_split_only(self):
        policy = get_workflow_policy("COMPLEX")

        self.assertEqual(policy["agent_mode"], "split")
        self.assertEqual(policy["allowed_steps"], [1, 2])
        self.assertNotIn(3, policy["allowed_steps"])
        self.assertNotIn(4, policy["allowed_steps"])

    def test_simple_ticket_keeps_full_pipeline(self):
        policy = get_workflow_policy("SIMPLE")

        self.assertEqual(policy["agent_mode"], "full")
        self.assertEqual(policy["allowed_steps"], [1, 2, 3, 4, 5, 6])


if __name__ == "__main__":
    unittest.main()
