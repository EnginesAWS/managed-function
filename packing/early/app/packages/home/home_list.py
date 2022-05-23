import pandas as pd
import streamlit as st
import packages.general_functions as gf

import mfs3.main as mfs3

ss = st.session_state

def get_list():
    st.df = pd.DataFrame()
    ss.docpaths = mfs3.list_docs(f"{ss.metadata.hub_path}/request")
    st.write(f"Number of strata plans in hub: {len(ss.docpaths)}")
    cols = st.columns([3, 2, 5, 2])
    header_cols = cols.copy()
    header_cols[0].markdown('**Strata plan**')
    header_cols[1].markdown('**Inception Date**')
    for docpath in ss.docpaths:
        path_parts = docpath.split('/')
        cols = st.columns([3, 2, 5, 2])
        cols[0].write(f"Strata plan {path_parts[5]}")
        cols[1].write(gf.split_date_with_hyphens(path_parts[6]))
        strata_plan_button = cols[-1].button('View plan', key=f"bt_strata_plan_{docpath}")
        if strata_plan_button:
            ss.show_sidebar = False
            ss.docpath = docpath
            ss.state = 'home_doc'
            ss.df = mfs3.read_doc(docpath)
            ss.df.new_index = ss.df.new_index.astype(float)
            st.experimental_rerun()
            
