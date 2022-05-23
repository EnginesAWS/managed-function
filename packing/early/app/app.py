import streamlit as st

import mf04.main as ct

import packages.general_functions as gf
import packages.page_functions as pf
import packages.home.home_list as home_list
import packages.home.home_doc as home_doc
import packages.label_request.label_request_list as label_request_list
import packages.label_response.label_response_list as label_response_list

title = 'ABS Strata Quote Hub'
st.set_page_config(page_title=title, page_icon="", layout="wide")
ss = st.session_state
 
def run_streamlit_app():
    
    if not ss.get('state'):
        ss.state = 'home_list'
        ss.metadata = ct.to_metadata(bucket='mf-abs', pipe='', folder='')

    gf.configure_app(title)

    st.title(title)
    
    if ss.show_sidebar:
        gf.set_sidebar()

    ss.metadata = ct.to_metadata(bucket='mf-abs', pipe='', folder='')

    if ss.state == 'home_list':
        home_list.get_list()
    elif ss.state == 'home_doc':
        ss.request_link = ss.docpath
        pf.write_header()
        home_doc.display_responding_insurers()
        pf.update_training_data()
    elif ss.state == 'label_request_list':
        ss.metadata = ct.to_metadata(bucket='mf-abs', pipe='quote_request', folder='enhanced_quote_requests')
        label_request_list.get_list()
    elif ss.state == 'label_request_doc':
        ss.request_link = ss.docpath
        ss.metadata = ct.to_metadata(bucket='mf-abs', pipe='quote_request', folder='enhanced_quote_requests')
        pf.write_header()
        pf.update_training_data()
    elif ss.state == 'label_response_list':
        ss.metadata = ct.to_metadata(bucket='mf-abs', pipe='quote_response', folder='enhanced_quote_responses')
        label_response_list.get_list()
    elif ss.state == 'label_response_doc':
        ss.metadata = ct.to_metadata(bucket='mf-abs', pipe='quote_response', folder='enhanced_quote_responses')
        pf.write_header()
        pf.update_training_data()
    elif ss.state == 'response_detail':
        ss.metadata = ct.to_metadata(bucket='mf-abs', pipe='', folder='')
        pf.write_header()
        pf.update_training_data()

    # st.write(ss)
    
if __name__ == "__main__":
    if 1 == 0:
        metadata = ct.to_metadata(bucket='mf-abs', pipe='', folder='')
        run_streamlit_app()