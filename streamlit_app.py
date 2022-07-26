from plotly.graph_objs import Layout, layout
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import boto3

client = boto3.client("s3")


@st.experimental_memo(ttl=600)
def read_file(username):
    local_filename = f"{username}.csv"
    client.download_file(
        "data.sapling.gg", f"data-points/{username}.csv", local_filename
    )
    return local_filename


def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
            st.session_state["username"] in st.secrets["passwords"]
            and st.session_state["password"]
            == st.secrets["passwords"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store username + password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 User not known or password incorrect")
        return False
    else:
        # Password correct.
        return True


def run(local_filename):
    df = pd.read_csv(local_filename)

    fig = go.Figure(
        data=[
            go.Scatter3d(
                x=df.x,
                y=df.y,
                z=df.z,
                mode="markers",
                marker=dict(size=1),
                showlegend=False,
            )
        ],
        layout=Layout(
            scene=dict(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False),
                aspectratio=dict(x=1, y=0.4, z=1),
            ),
        ),
    )
    st.plotly_chart(fig)


if check_password():
    if "username" in st.session_state:
        username = st.session_state["username"]
        st.write(username)
        local_filename = read_file(username)
        run(local_filename)
        st.session_state["username"] = username
