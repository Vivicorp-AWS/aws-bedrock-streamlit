import streamlit as st
import boto3
import jsonpickle

# Widgets for user to select AWS credentials
def display_credential_widget():
    with st.expander("AWS Credential Settings", expanded=False):
        # Prepare the options, including the existing profiles
        options_credential = ["None (Use instance profile)", "Enter manually"]
        options_credential[1:1] = [f"Profile: {profile_name}" for profile_name in boto3.session.Session().available_profiles]  # Add "Profile: " prefix to highlight the profile name
        # Create a drop-down list to assign AWS credential
        aws_credential = st.selectbox(
            "Enter manually or select from available profiles:",
            options=options_credential,
            # If the profile name is pre-selected as URL's query parameter, select that one
            index=options_credential.index(f"Profile: {st.query_params.get("profile")}") if st.query_params.get("profile") else 0,
            placeholder="None (Use instance profile)",
        )
        # Create Boto3's Session object
        if aws_credential == "None (Use instance profile)":
            aws_session = boto3.session.Session()
        elif aws_credential == "Enter manually":
            st.text_input("Access Key ID", key="aws_access_key_id")
            st.text_input("Secret Access Key", key="aws_secret_access_key", type="password")
            st.text_input("Region", key="aws_region")
            aws_session = boto3.session.Session(
                aws_access_key_id=st.session_state["aws_access_key_id"],
                aws_secret_access_key=st.session_state["aws_secret_access_key"],
                region_name=st.session_state["aws_region"],
                )
        else:
            profile_name = aws_credential.replace("Profile: ", "")  # Remove "Profile: " prefix
            aws_session = boto3.session.Session(profile_name=profile_name)
        
        # Store Boto3 Session object into Streamlit Session State
        st.session_state["aws_session"] = aws_session  

        # Debug information
        if st.query_params.get('debug') == "true":
            st.caption("Debug Information - AWS Credentials")
            st.write({
                "query_params_profile": st.query_params.get("profile") if st.query_params.get("profile") else None,
                "aws_access_key_id": st.session_state["aws_access_key_id"] if st.session_state.get("aws_access_key_id") else None,
                "aws_secret_access_key": st.session_state["aws_secret_access_key"] if st.session_state.get("aws_secret_access_key") else None,
                "aws_region": st.session_state["aws_region"] if st.session_state.get("aws_region") else None,
                "aws_session": st.session_state["aws_session"] if st.session_state.get("aws_session") else None,
            })
