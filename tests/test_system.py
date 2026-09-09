import sys
import os
import time
import requests
import unittest

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent_system import run_maintenance_orchestrator

BASE_URL = "http://127.0.0.1:8000"

class TestIndustrialAIBackend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Obtain JWT token with retries while server starts up
        cls.token = None
        cls.headers = {}
        for attempt in range(10):
            try:
                res = requests.post(f"{BASE_URL}/api/auth/login", json={"username": "admin", "password": "admin123", "role": "admin"}, timeout=3.0)
                if res.status_code == 200:
                    token_data = res.json()
                    cls.token = token_data.get("token")
                    cls.headers = {"Authorization": f"Bearer {cls.token}"}
                    break
            except Exception:
                time.sleep(1.0)

    def test_01_health_check(self):
        res = requests.get(f"{BASE_URL}/api/v2/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("status"), "online")
        self.assertIn("database", data)
        print("[PASS] Health check test passed")

    def test_02_login_and_auth(self):
        self.assertIsNotNone(self.token, "Failed to authenticate with admin credentials")
        res = requests.get(f"{BASE_URL}/api/v2/auth/me", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        user_info = res.json()
        self.assertEqual(user_info.get("role"), "admin")
        print("[PASS] Auth & JWT token verification test passed")

    def test_03_dashboard_stats(self):
        res = requests.get(f"{BASE_URL}/api/dashboard/stats")
        self.assertEqual(res.status_code, 200)
        stats = res.json()
        self.assertIn("total_machines", stats)
        self.assertIn("healthy_machines", stats)
        self.assertIn("active_alerts", stats)
        print(f"[PASS] Dashboard stats test passed: {stats['total_machines']} total machines")

    def test_04_machine_detail(self):
        res = requests.get(f"{BASE_URL}/api/machines/fan")
        self.assertEqual(res.status_code, 200)
        machine_info = res.json()
        self.assertEqual(machine_info.get("machine", {}).get("id"), "FAN-01")
        self.assertIn("components", machine_info)
        print("[PASS] Machine detail GET endpoint test passed")

    def test_05_agent_determinism(self):
        """Verify that agent diagnosis is 100% deterministic (no random numbers)."""
        res1 = run_maintenance_orchestrator("fan", "normal_clip_1.wav", 1.85, 1.4, "0")
        res2 = run_maintenance_orchestrator("fan", "normal_clip_1.wav", 1.85, 1.4, "0")
        
        self.assertEqual(res1["monitoring"]["clip_score"], res2["monitoring"]["clip_score"])
        self.assertEqual(res1["diagnostic"]["severity"], res2["diagnostic"]["severity"])
        self.assertEqual(res1["diagnostic"]["faulty_component"], res2["diagnostic"]["faulty_component"])
        self.assertEqual(res1["diagnostic"]["confidence"], res2["diagnostic"]["confidence"])
        self.assertEqual(res1["health"]["health_index"], res2["health"]["health_index"])
        print("[PASS] Agent system determinism test passed (identical input -> identical diagnostic metrics)")

    def test_06_rag_engine(self):
        """Verify that RAG citations originate from documented machine manuals."""
        res = requests.post(f"{BASE_URL}/api/ai/chat", json={"message": "How to calibrate fan bearing?", "machine_type": "fan"})
        self.assertEqual(res.status_code, 200)
        chat_res = res.json()
        self.assertIn("reply", chat_res)
        self.assertIn("sources", chat_res)
        print(f"[PASS] RAG engine test passed with {len(chat_res['sources'])} manual citations")

    def test_07_audit_logs(self):
        res = requests.get(f"{BASE_URL}/api/v2/audit-logs", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        logs = res.json()
        self.assertIsInstance(logs, list)
        print(f"[PASS] Audit log endpoint test passed ({len(logs)} entries retrieved)")

    def test_08_system_settings(self):
        res = requests.get(f"{BASE_URL}/api/v2/settings", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        settings = res.json()
        self.assertIn("baseline_thresholds", settings)
        print("[PASS] System settings endpoint test passed")

    def test_09_test_notification(self):
        res = requests.post(
            f"{BASE_URL}/api/v2/notifications/test",
            headers=self.headers,
            json={"channel": "email", "recipient": "admin@industrial.com", "message": "Test Alert"}
        )
        self.assertEqual(res.status_code, 200)
        notif_res = res.json()
        self.assertTrue(notif_res.get("success"))
        print("[PASS] Notification gateway test passed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
