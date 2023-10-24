import streamlit as st
from urllib.parse import urlparse
import snowflake.connector
import pickle
from pathlib import Path


def decrypt_key(
    key: bytes, is_key_encrypted: bool, private_key_passphrase: str = None
) -> bytes:
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization

    p_key = serialization.load_pem_private_key(
        key,
        password=private_key_passphrase.encode() if is_key_encrypted else None,
        backend=default_backend(),
    )

    pkb = p_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    return pkb


def login_form(connection_option: str):
    connection_params = {}
    with st.form("Connection Options"):
        account = st.text_input(
            label="Account",
            help="You can use either the account locator or the account URL.",
        )
        parse_url = urlparse(account)
        if parse_url.netloc == "":
            connection_params["account"] = account
        elif ".snowflakecomputing.com" in parse_url.netloc:
            connection_params["account"] = parse_url.netloc.replace(
                ".snowflakecomputing.com", ""
            )
        username = st.text_input(label="Username")
        connection_params["user"] = username
        if connection_option == "Default":
            password = st.text_input(label="Password", type="password")
            connection_params["password"] = password
        if connection_option == "SSO":
            connection_params["authenticator"] = "externalbrowser"
        if connection_option == "KPA":
            private_key_path = st.file_uploader(label="Private Key Path")
            is_key_encrypted = st.checkbox("Is your key encrypted?", value=True)
            private_key_passphrase = st.text_input(
                label="Private Key Passphrase", type="password"
            )
        save = st.selectbox(
            "Would you like to save your connection?",
            ["", "Yes", "No"],
        )
        submitted = st.form_submit_button("Submit")
        if connection_option == "KPA":
            if submitted and is_key_encrypted:
                pkb = decrypt_key(
                    private_key_path.getvalue(),
                    is_key_encrypted,
                    private_key_passphrase,
                )
                connection_params["private_key"] = pkb
            elif submitted:
                pkb = decrypt_key(private_key_path.getvalue(), is_key_encrypted)
                connection_params["private_key"] = pkb
        return submitted, save, connection_params


@st.cache_resource
def connect(**connection_params) -> snowflake.connector.connection:
    conn = snowflake.connector.connect(**connection_params)
    return conn


def save_connection(connection_option: str, **connection_params):
    Path("env/").mkdir(exist_ok=True)
    with open(
        f"./env/{connection_option}_{connection_params.get('account')}_{connection_params.get('user')}.pickle",
        "wb",
    ) as f:
        pickle.dump(connection_params, f)


def load_connection() -> dict:
    conn_dict = {
        file: file.name.replace(file.suffix, "")
        for file in Path("./env/").glob("*.pickle")
    }
    connection = st.selectbox(
        label="Which connection would you like to use?",
        options=[""] + list(conn_dict.values()),
    )
    if connection != "":
        connection_path = list(conn_dict.keys())[
            list(conn_dict.values()).index(connection)
        ]
        with open(connection_path, "rb") as f:
            connection_params = pickle.load(f)
            return connection_params


def save_session_state(key: str, value):
    st.session_state[key] = value


def snowflake_login():
    option_selector = ["", "Default", "SSO", "KPA"]
    if len([file for file in Path("./env/").glob("*.pickle")]) > 0:
        option_selector.append("Existing Connection")

    connection_option = st.selectbox(
        "How would you like to connect?",
        option_selector,
    )
    if connection_option != "" and connection_option != "Existing Connection":
        _submitted, _save, connection_params = login_form(connection_option)
        if _submitted:
            conn = connect(**connection_params)
            st.write("Congrats, you're connected! 🎉")
            if _save == "Yes":
                save_connection(connection_option, **connection_params)
            save_session_state(key="conn", value=conn)
            return st.session_state.conn
    elif connection_option == "Existing Connection":
        connection_params = load_connection()
        if connection_params:
            conn = connect(**connection_params)
            save_session_state(key="conn", value=conn)
            st.write("Congrats, you're connected! 🎉")
            return st.session_state.conn


if __name__ == "__main__":
    conn = snowflake_login()