def sign_in_user(client, email, password):
    """Authenticate a user with Supabase email and password."""

    response = client.auth.sign_in_with_password({
        "email": email,
        "password": password,
    })

    return response

def sign_out_user(client):
    """Sign out the authenticated Supabase user."""

    client.auth.sign_out()


def establish_invitation_session(client, access_token, refresh_token):
    """Establish and verify a Supabase invitation session."""

    response = client.auth.set_session(access_token, refresh_token)

    if response.user is None or response.session is None:
        raise ValueError("Unable to verify invitation session.")

    return response


def set_invited_user_password(client, password):
    """Set the password for an authenticated Supabase user."""

    if not client.auth.get_user().user:
        raise ValueError("An authenticated session is required.")

    return client.auth.update_user({"password": password})
