import pandas as pd
import streamlit as st

import mfs3.main as mfs3

ss = st.session_state

def get_list():
    st.df = pd.DataFrame()
    ss.docpaths = mfs3.list_docs(f"{ss.metadata.input_path}")
    st.write(f"Number of strata plans to label: {len(ss.docpaths)}")
    cols = st.columns([3, 2, 5, 2])
    header_cols = cols.copy()
    header_cols[0].markdown('**Strata plan**')
    header_cols[1].markdown('**Inception Date**')
    for docpath in ss.docpaths:
        cols = st.columns([3, 7, 2])
        cols[0].write(f"Strata plan {docpath}")
        strata_plan_button = cols[-1].button('View plan', key=f"bt_strata_plan_{docpath}")
        if strata_plan_button:
            ss.show_sidebar = False
            ss.docpath = docpath
            ss.state = 'label_request_doc'
            ss.df = mfs3.read_doc(docpath)
            st.experimental_rerun()
            
