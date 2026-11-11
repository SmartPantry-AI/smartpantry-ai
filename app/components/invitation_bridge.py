import streamlit as st
import streamlit.components.v2 as components


def render_invitation_bridge():
    bridge = components.component(
        "smartpantry_invitation_bridge",
        js="""
        export default function(component) {
            const fragment = new URLSearchParams(window.location.hash.slice(1));

            const invitationDetected = fragment.get("type") === "invite";

            const hasAccessToken = fragment.has("access_token");
            const hasRefreshToken = fragment.has("refresh_token");

            const invitationReady =
                invitationDetected && hasAccessToken && hasRefreshToken;

            component.setStateValue("status", {
                invitationDetected,
                hasAccessToken,
                hasRefreshToken,
                invitationReady
            });
        }
        """,
    )

    return bridge()


