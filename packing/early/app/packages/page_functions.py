import pandas as pd
import streamlit as st

from cattrs import structure, unstructure
import mf04.main as ct
import mfs3.main as mfs3
import mfstratahub.main as mfhub
import mfsstextractor.main as mfss
import packages.general_functions as gf

canonical_base = 's3://mf-docs-limited'
canonical_url_base = 'https://mf-docs-limited.s3-ap-southeast-2.amazonaws.com'

ss = st.session_state


def return_to_request_doc():
    ss.state = 'home_doc'
    ss.docpath = ss.return_docpath
    ss.df = mfs3.read_doc(ss.docpath)


def write_header():

    ss.strata_plan_number = mfhub.return_numbers(f"{ss.df[ss.df.label=='insured_name'].iloc[0].prediction}")
    ss.inception_date, ss.expiry_date = mfhub.fill_inception_and_expiry_dates(ss.df, return_dates_only=True)

    column_widths = [2, 4, 2]
    cols = st.columns(column_widths)
    cols[0].write('**Strata Plan**')
    cols[1].write(ss.strata_plan_number)
    cols[0].write('**Inception Date**')
    cols[1].write(ss.inception_date)
    ss.edit_fields = cols[2].checkbox('Edit fields')

    column_widths = [6, 2]
    cols = st.columns(column_widths)
    cols[0].write(f"[Link to quote request]({ct.canonical_url_base}/{ss.request_link.split('/')[-1]})")

    if ss.state == 'home_doc':
        column_widths = [6, 2]
        cols = st.columns(column_widths)
        if cols[1].button('Return to list'):
            ss.show_sidebar = True
            ss.state = ss.state.replace('_doc', '_list')
            gf.set_sidebar()
            st.experimental_rerun()

    st.write('---')


def get_fields_to_show():
    if 'response' in ss.state.lower():
        fields_to_show = ss.quote_response_fields
        ss.to_find = mfs3.read_doc(f"{ss.quote_response_ml_path}/1_raw_data/{ss.docpath.split('/')[-1]}")['to_find']
    else:
        fields_to_show = ss.quote_request_fields
        ss.to_find = mfs3.read_doc(f"{ss.quote_request_ml_path}/1_raw_data/{ss.docpath.split('/')[-1]}")['to_find']
    return fields_to_show


def update_training_data():
    # st.write(ss.quote_request_fields)
    # st.write(ss.quote_response_fields)

    list_to_return_to = ss.state.replace('_doc', '_list')

    fields_to_show = get_fields_to_show()

    if ss.edit_fields:
        gf.get_original_text()

    column_widths = [3, 4, 1]

    if ss.state == 'response_detail':
        col0, col1, col2 = st.columns(column_widths)
        col0.subheader(f"{ss.insurer.upper()}")
        col1.write(f"[Link to quote response]({ss.response_link})")
        col1.write(f"[Link to quote email]({ss.response_link.split('_')[0]})")

        if col2.button('Return to request'):
            return_to_request_doc()
            st.experimental_rerun()

    if ss.edit_fields:
        column_widths = [1, 2, 2, 2, 1]
        st.markdown('***')
        col0, col1, col2, col3, col4 = st.columns(column_widths)
        col1.markdown('**FIELD NAME**')
        col2.markdown('**EXTRACTED TEXT**')
        col3.markdown('**LINE NUMBER**')
    else:
        column_widths = [1, 1, 2, 1]
        st.markdown('***')
        col0, col1, col2, col3 = st.columns(column_widths)
        col1.markdown('**FIELD NAME**')
        col2.markdown('**EXTRACTED TEXT**')

    all_rows = []

    for row_name in fields_to_show:
        try:
            row = ss.df[ss.df.label == row_name].iloc[0]
        except:
            row = pd.Series(unstructure(mfhub.LabelledLine(label=row_name)))

        if row.prediction or ss.edit_fields:
            all_rows.append(match_row(row))
        else:
            all_rows.append(row)
    ss.df = pd.DataFrame(all_rows)

    mfs3.save_doc(ss.df, ss.docpath)
    mfss.save_df_predictions(ss.df, ss.docpath, ss.metadata, full_class=fields_to_show)

    if ss.edit_fields:
        if st.button('Update training data'):
            if ss.state != 'response_detail':
                insurer = gf.get_insurer_from_extracted_text()
                if '/quote_request/' in ss.docpath:
                    mfs3.save_doc(ss.df, f"s3://mf-abs/store/quote_request_ml/2_all_predictions/{ss.docpath.split('/')[-1]}")
                    mfs3.move_to_hub(ss.df, ss.docpath, ss.metadata, 'request', ss.strata_plan_number, f"{ss.inception_date.replace('/', '')}/{insurer}")
                elif '/quote_response/' in ss.docpath:
                    mfs3.save_doc(ss.df, f"s3://mf-abs/store/quote_response_ml/2_all_predictions/{ss.docpath.split('/')[-1]}")
                    mfs3.move_to_hub(ss.df, ss.docpath, ss.metadata, 'response', ss.strata_plan_number, f"{ss.inception_date.replace('/', '')}/{insurer}")
            else:
                mfs3.save_doc(ss.df, ss.docpath)


def match_row(row):
    if ss.edit_fields:
        column_widths = [1, 2, 2, 2, 1]
        col0, col1, col2, col3, col4 = st.columns(column_widths)
    else:
        column_widths = [1, 1, 2, 1]
        col0, col1, col2, col3 = st.columns(column_widths)

    col0.write('')
    col1.write('')
    col1.write('')

    if ss.edit_fields:
        if int(row.new_index) >= 0:
            tooltip = f"{ss.to_find[max(0, int(row.new_index) - 1)]} || {ss.to_find[int(row.new_index)]} || {ss.to_find[min(len(ss.to_find) - 1, int(row.new_index) + 1)]}"
        else:
            tooltip = ''

        line_to_find = col3.number_input('', value=int(row.new_index), key=f"line_{row.label}", step=1, help=tooltip)

        if 0 <= line_to_find <= len(ss.to_find):
            row.prediction = ss.to_find[line_to_find]
            row.new_index = line_to_find
        else:
            row.prediction = ''
            row.new_index = -1

    col2.write('')
    col2.write('')
    if row.new_index >= 0:
        col2.success(row.prediction)
    row_name_normalised = ' '.join(row.label.split('_')).title()
    col1.write(row_name_normalised)
    return row.to_dict()