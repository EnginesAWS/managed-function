import arrow
import attrs
import dateparser
import pandas as pd
import re
import streamlit as st

import mf04.main as ct
import mfmatch.main as mfm
import mfstratahub.main as mfhub
import mfstreamlit.main as mfst


canonical_base = 's3://mf-docs-limited'
canonical_url_base = 'https://mf-docs-limited.s3-ap-southeast-2.amazonaws.com'

ss = st.session_state


def configure_app(title):
    ss.metadata = ct.to_metadata(bucket='mf-abs', pipe='', folder='')
    mfst.safe_set('quote_request_fields', list(attrs.fields_dict(mfhub.QuoteRequest).keys()))
    mfst.safe_set('quote_response_fields', list(attrs.fields_dict(mfhub.QuoteResponse).keys()))
    mfst.safe_set('quote_request_ml_path', 's3://mf-abs/store/quote_request_ml')
    mfst.safe_set('quote_response_ml_path', 's3://mf-abs/store/quote_response_ml')
    mfst.safe_set('docpath', '')
    mfst.safe_set('request_link', '')
    mfst.safe_set('docpaths', default_type='list')
    mfst.safe_set('df', default_type='df')
    mfst.safe_set('show_sidebar', v=True, default_type='bool')
    mfst.safe_set('edit_fields', v=False, default_type='bool')
    ss.insurers = pd.DataFrame(mfhub.insurers)


def set_sidebar():
    ss.status_label = st.sidebar.selectbox('Hub activity', ['View strata properties', 'Label strata plans', 'Label quote responses'])
    if ss.status_label == 'View strata properties':
        ss.state = 'home_list'
    elif ss.status_label == 'Label strata plans':
        ss.state = 'label_request_list'
    elif ss.status_label == 'Label quote responses':
        ss.state = 'label_response_list'

    if st.sidebar.button('Go to Hub List'):
        ss.state = ''
        st.experimental_rerun()


def split_date_with_hyphens(text):
    text = f"{text}".strip()
    if len(text) == 8:
        return f"{text[0:4]}-{text[4:6]}-{text[6:8]}"
    else:
        return text


def get_insurer_from_extracted_text():
    domain_list = [
        {'axisunderwriting.com.au': 'axis'},
        {'chu.com.au': 'chu'},
        {'CHU Underwriting Agencies': 'chu'},
        {'flexinsurance.com.au': 'flex'},
        {'longitudeinsurance.com.au': 'long'},
        {'qus.com.au': 'qus'},
        {'qus strata insurance': 'qus'},
        {'sci.com.au': 'sci'},
        {'sura.com.au': 'sura'},
        {'suu.com.au': 'suu'},
        {'Strata Unit Underwriting Agency Pty Ltd': 'suu'}
    ]

    df_insurer = mfm.classify_list(ss.to_find, domain_list)
    insurer = df_insurer.iloc[0].value
    return insurer


def get_original_text():
    st.sidebar.header('Original document')
    st.sidebar.table(pd.DataFrame([st.session_state.to_find]).T.style.set_properties(**{'text-align': 'left'}))

