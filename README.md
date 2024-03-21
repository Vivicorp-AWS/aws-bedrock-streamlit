# Streamlit Frontend for Amazon Bedrock

| 🚧 Under heavy construction 🚧

## Usage

### Launch

```bash
streamlit run main.py
```

### Launch with debug mode

Add query parameter "debug" ans assigned as "`true`" in the URL. E.g.: http://localhost:8501/?debug=true.

### Always rerun the program when script changes

```bash
streamlit run --server.runOnSave true main.py
```

### Pre-selected a AWS credential profile

Add query parameter "profile" and assigned as the name of the profile in the URL. E.g: http://localhost:8501/?profile=default

## Contribution / Developer Guides

### Determine whether to show debug information or not

Verify the query parameter "debug" is set in the URL:

```python
if st.query_params.get('debug'):
    # Show debug information widget
```

### Create clients from custom Session object

The AWS credential will assigned in the sidebar and stored as a Streamlit's Session State, fetch by calling `st.session_state['aws_session']` then create low-level client from that:

```python
# E.g.: Create a S3 client
s3 = st.session_state['aws_session'].client('s3')
```
