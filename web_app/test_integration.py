import unittest
import os
import sys

# Add path to current directory (web_app)
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
# Add parent path for src access
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models import User, Organization

class TestIndustriSenseIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        
        # In create_app('testing'), db.create_all() is called
        # but we ensure they are clean for tests
        db.drop_all()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def test_ml_service_logic(self):
        """Test the core ML inference logic."""
        from app.services import ml_service as mls
        
        raw_telemetry = {
            'air_temp': 300.0,
            'process_temp': 310.0,
            'rpm': 1500,
            'torque': 40.0,
            'tool_wear': 50,
            'is_anomaly': 0
        }
        
        valid_data, error = mls.validate_telemetry(raw_telemetry)
        self.assertIsNone(error)
        
        df_clf, df_reg = mls.preprocess_input(raw_telemetry)
        self.assertEqual(len(df_clf), 1)

    def test_organization_fleet_scaling(self):
        """Test that machine count respects organization settings."""
        from app.services import ml_service as mls
        
        org = Organization(name='Test Org', domain='test.com', machine_count=25)
        db.session.add(org)
        db.session.commit()
        
        user = User(email='test@test.com', organization_id=org.id)
        user.set_password('test')
        db.session.add(user)
        db.session.commit()

        # Run analysis
        analysis = mls.perform_fleet_analysis(user.id)
        self.assertIsNotNone(analysis)
        self.assertEqual(analysis['fleet_stats']['total'], 25)

if __name__ == '__main__':
    unittest.main()
