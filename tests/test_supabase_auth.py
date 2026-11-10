from unittest.mock import MagicMock

from modules.supabase_auth import sign_in_user, sign_out_user

import pytest


def test_sign_in_user():
    """Verify that login sends the correct credentials."""

    mock_client = MagicMock()

    mock_response = MagicMock()
    mock_response.user.id = "test-user-123"

    mock_client.auth.sign_in_with_password.return_value = mock_response

    result = sign_in_user(
        mock_client,
        "test@example.com",
        "test-password"
    )

    mock_client.auth.sign_in_with_password.assert_called_once_with({
        "email": "test@example.com",
        "password": "test-password",
    })

    assert result.user.id == "test-user-123"


def test_sign_in_user_invalid_credentials():
    """Verify that authentication errors are not ignored."""

    mock_client = MagicMock()

    mock_client.auth.sign_in_with_password.side_effect = (
        ValueError("Invalid login credentials")
    )

    with pytest.raises(ValueError, match="Invalid login credentials"):
        sign_in_user(
            mock_client,
            "test@example.com",
            "wrong-password"
        )

    mock_client.auth.sign_in_with_password.assert_called_once()


def test_sign_out_user():
    """Verify that logout calls Supabase sign_out."""

    mock_client = MagicMock()

    sign_out_user(mock_client)

    mock_client.auth.sign_out.assert_called_once_with()


