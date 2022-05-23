import streamlit as st

import packages.general_functions as gf

import mfs3.main as mfs3
import mfstratahub.main as mfhub

ss = st.session_state


def get_premium_type(df):
    df = df[df.label.str.contains('gross_premium')]
    df = df.sort_values(by=['probability'], ascending=False)
    df = df[df.prediction!='']
    if df.shape[0]:
        # st.write(df)
        if 'yes' in df.iloc[0].label:
            return 'Gross'
        else:
            return 'Net'
    else:
        return ''


def build_response_summary():
    insurer_list = []

    df_output = mfs3.read_doc('s3://mf-abs/hub/output/14861/20220225/output.parquet')

    for insurer_object in mfhub.insurers:
        folder_path = f"{ss.metadata.hub_path}/response/{ss.strata_plan_number}/{ss.inception_date.replace('-', '')}/{insurer_object['shortname']}"
        responses = mfs3.list_docs(folder_path)
        if responses:
            differences = df_output[df_output['index']==insurer_object['shortname']].iloc[0].differences.split(',')
            response_path = responses[0]
            df_response = mfs3.read_doc((response_path))
            insurer_list.append({'insurer': insurer_object['shortname'],
             'total_premium': df_response[df_response.label=='total_premium'].iloc[0].prediction,
             'net_gross': get_premium_type(df_response),
             'link': f"https://mf-docs-limited.s3-ap-southeast-2.amazonaws.com/{response_path.split('/')[-1]}",
             'differences': differences,
             'response_path': response_path})
        else:
            insurer_list.append({'insurer': insurer_object['shortname'], 'response_path': ''})
            # st.write(df_response)
    return insurer_list


def display_responding_insurers():
    insurer_list = build_response_summary()

    cols = st.columns(9)

    for i, insurer in enumerate(insurer_list):
        cols[i].write(f"**{insurer['insurer'].upper()}**")
        cols[i].write(f"{insurer.get('total_premium', '')}")
        cols[i].write(f"{insurer.get('net_gross', '')}")
        if insurer.get('link', ''):
            cols[i].write(f"[Link]({insurer.get('link', '')})")
            dif = False
            for d in insurer.get('differences', []):
                # cols[i].write(d)
                if d in 'building_sum_insured':
                    cols[i].warning('Building sum insured')
                    dif = True
                if d in 'catastrophe_limit':
                    cols[i].warning('Catastrophe')
                    dif = True
                if d in 'equipment_breakdown_limit':
                    cols[i].warning('Equipment breakdown')
                    dif = True
            if cols[i].button('View', key=f"view_{insurer['insurer']}"):
                ss.return_docpath = ss.docpath
                ss.insurer = insurer['insurer']
                ss.response_link = insurer.get('link', '')
                ss.show_sidebar = False
                ss.docpath = insurer['response_path']
                ss.state = 'response_detail'
                ss.df = mfs3.read_doc(insurer['response_path'])
                ss.df.new_index = ss.df.new_index.astype(float)
                st.experimental_rerun()
        cols[i].write()





