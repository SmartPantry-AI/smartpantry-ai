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

