import unittest

from app.config import Settings, validate_production_runtime_settings


class ProductionRuntimeValidationTest(unittest.TestCase):
    def test_production_rejects_placeholder_secrets(self):
        settings = Settings(
            app_env="production",
            port=8000,
            database_url="sqlite:////data/app.db",
            jwt_secret="dev-secret",
            service_name="api-service",
            api_key_a="testkey-a",
            api_key_b="testkey-b",
        )

        with self.assertRaises(ValueError) as exc:
            validate_production_runtime_settings(settings)

        message = str(exc.exception)
        self.assertIn("JWT_SECRET", message)
        self.assertIn("API_KEY_A", message)
        self.assertIn("API_KEY_B", message)

    def test_production_rejects_missing_api_keys(self):
        settings = Settings(
            app_env="production",
            port=8000,
            database_url="sqlite:////data/app.db",
            jwt_secret="strong-prod-secret",
            service_name="api-service",
            api_key_a=None,
            api_key_b=None,
        )

        with self.assertRaises(ValueError) as exc:
            validate_production_runtime_settings(settings)

        message = str(exc.exception)
        self.assertIn("missing required production secrets", message)

    def test_non_production_allows_local_placeholder_values(self):
        settings = Settings(
            app_env="development",
            port=8000,
            database_url="sqlite:///./local.db",
            jwt_secret="dev-secret",
            service_name="api-service",
            api_key_a="testkey-a",
            api_key_b="testkey-b",
        )

        validate_production_runtime_settings(settings)

    def test_production_accepts_explicit_non_placeholder_values(self):
        settings = Settings(
            app_env="production",
            port=8000,
            database_url="sqlite:////data/app.db",
            jwt_secret="prod-secret-123",
            service_name="api-service",
            api_key_a="prod-key-a-123",
            api_key_b="prod-key-b-123",
        )

        validate_production_runtime_settings(settings)


if __name__ == "__main__":
    unittest.main()
