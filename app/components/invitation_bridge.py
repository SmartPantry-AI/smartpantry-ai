import streamlit as st
import streamlit.components.v2 as components


def render_invitation_bridge(invitation_handled=False):
    bridge = components.component(
        "smartpantry_invitation_bridge",
        js="""

        export default async function(component) {

            const fragment = new URLSearchParams(window.location.hash.slice(1));

            const invitationDetected = fragment.get("type") === "invite";

            const hasAccessToken = fragment.has("access_token");
            const hasRefreshToken = fragment.has("refresh_token");

            const invitationReady =
                invitationDetected && hasAccessToken && hasRefreshToken;

            const invitationCredentials = invitationReady
                ? {
                    access_token: fragment.get("access_token"),
                    refresh_token: fragment.get("refresh_token")
                }
                : null;

            const invitationAlreadyHandled =
                component.data?.invitation_handled === true;

            if (invitationReady && !invitationAlreadyHandled) {
                component.setStateValue("invitation_credentials", invitationCredentials);
            }

            if (invitationReady && invitationAlreadyHandled) {
                clearInvitationUrl();
            }

            const runningInIframe = window.self !== window.top;

            function clearInvitationUrl() {
                const cleanUrl = window.location.pathname + window.location.search;
                window.history.replaceState(null, "", cleanUrl);
            }

            component.setStateValue("status", {
                invitationDetected,
                invitationReady,
                runningInIframe
            });
        }
        """,
    )

    return bridge(
        data={
            "invitation_handled": invitation_handled,
        }
    )


