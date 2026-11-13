import os
from supabase import create_client


def get_admin_client():
    supabase_url = os.environ["SUPABASE_URL"]
    service_role_key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

    return create_client(supabase_url, service_role_key)

def invite_user(client, email, redirect_url):
    response = client.auth.admin.invite_user_by_email(
        email,
        options={"redirect_to": redirect_url},
    )
    return response


def main():
    email = os.environ["SMARTPANTRY_INVITE_EMAIL"]
    redirect_url = os.environ["SMARTPANTRY_INVITE_REDIRECT_URL"]

    if not redirect_url.startswith("https://"):
        raise ValueError("Invitation redirect URL must use HTTPS.")

    client = get_admin_client()
    invite_user(client, email, redirect_url)

    print("Invitation request completed successfully.")


if __name__ == "__main__":
    main()