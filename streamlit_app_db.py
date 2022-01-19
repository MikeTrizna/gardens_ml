from sqlite3.dbapi2 import connect
import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode
import pandas as pd
import sqlite3

st.set_page_config(
     page_title="SI Gardens Tree Annotator",
     page_icon="🌳",
     layout="wide"
 )

st.markdown('## SI Gardens Tree Annotator')

def fetch_data():
    con = sqlite3.connect("si_garden_trees_testing.db")
    meta_df = pd.read_sql_query("SELECT * from tree_metadata", con)
    image_df = pd.read_sql_query("SELECT * from tree_images", con)
    con.close()
    return meta_df, image_df

def display_table(df):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection('single', use_checkbox=False)
    gb.configure_pagination(paginationAutoPageSize=True)
    gridOptions = gb.build()
    return AgGrid(
        df, 
        gridOptions=gridOptions,
        height=500, 
        width='100%',
        return_mode='AS_INPUT',
        update_mode='SELECTION_CHANGED',
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True, #Set it to True to allow jsfunction to be injected
        )

def record_annotations():
    response = {'test':'test'}
    return response

meta_df, image_df = fetch_data()

grid_response = display_table(meta_df)

st.markdown('## Tree Details')

if len(grid_response['selected_rows']):
    selected_tree = grid_response['selected_rows'][0]
    tree_id = selected_tree['accession_number']
    st.experimental_set_query_params(accession = tree_id)
else:
    query_params = st.experimental_get_query_params()
    if 'accession' in query_params:
        tree_id = query_params['accession'][0]
    else:
        tree_id = meta_df.at[0,'accession_number']

tree_col1, tree_col2 = st.columns(2)
with tree_col2:
    st.write(tree_id)
    selected_images = image_df[image_df['accession_number'] == tree_id][['ids_id','image_category']].to_dict(orient='records')
    if len(selected_images) > 0:
        im_to_show = st.radio('Image to show',
                              selected_images,
                               index=0)
with tree_col1:
    image_url = f'https://ids.si.edu/ids/deliveryService/id/{im_to_show}/500'
    st.image(image_url)

st.markdown('## Annotation')

with st.form(key = "annotation_form", clear_on_submit=True):
    evergreen = st.radio('Is the tree deciduous or evergreen?',
                        ['Deciduous','Evergreen','Unclear'],
                        index=2,
                        key='evergreen',
                        help='or broadleaf vs conifer??')
    pruning = st.radio('What type of pruning system is employed?',
                        ['Natural pruning system',
                        'Topiary pruning system',
                        'Specialty pruning system',
                        'Unclear'],
                        index=3,
                        help='Details on Question 2')
    st.markdown('---')
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.markdown('*Natural pruning questions*')
        stem = st.radio('What form is this tree?',
                        ['Single-stem',
                        'Multistem',
                        'Clump',
                        'Shrub',
                        'Unclear',
                        'N/A'],
                        index=5,
                    help='(generally initially trained to this form in the nursery)')
        tree_form = st.radio('Which training system is used?',
                            ['Managed - central leader form',
                             'Managed - other system',
                            'Unmanaged',
                            'Unclear',
                            'N/A'],
                            index=4,
                            help='Details on Question 5')
        branched = st.radio('Is the tree high-branched or low-branched?',
                            ['Low-branched',
                            'High-branched',
                            'Unclear',
                            'N/A'],
                            index=3,
                            help='Details on Question 4')
    with c2:
        st.markdown('*Topiary pruning questions*')
        hedge = st.radio('Is tree managed as hedge or individual specimen?',
                            ['Hedge',
                             'Individual',
                            'Unclear',
                            'N/A'],
                            index=3)
    with c3:
        st.markdown('*Specialty pruning questions*')
        specialty_pruning = st.radio('Which specialty pruning system is used?',
                        [' Pollarding',
                        ' Espalier (none currently present)',
                        'Pleeching (none currently present)',
                        'Unclear',
                        'N/A'],
                        index=4)
    st.markdown('---')
    annotator = st.radio('Who is annotating?',
                        ['Courtney','Jake','Kayleigh'])

    notes = st.text_area('Notes')

    submitted = st.form_submit_button("Submit")

    if submitted:
        response = record_annotations()
        st.write(response)

