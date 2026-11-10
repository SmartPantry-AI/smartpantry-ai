from unittest.mock import patch

from modules.supabase_client import get_supabase_client

def test_gte_supabase_client():
    """Verify that the client uses the configured credentials."""

    with patch("modules.supabase_client.load_dotenv"), \
        patch("modules.supabase_client.create_client") as mock_create, \
        patch.dict("os.environ", {
            "SUPABASE_URL": "https://example.supabase.co",
            "SUPABASE_KEY": "test-plublishable-key"
        }):

        result = get_supabase_client()

        mock_create.assert_called_once_with(
            "https://example.supabase.co",
            "test-plublishable-key"
        )

        assert result == mock_create.return_value

