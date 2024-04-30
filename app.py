import streamlit as st
import pandas as pd
import pickle

#@st.cache()
def getData():
    player_df = pd.read_pickle('data/outfield.pkl')
    with open('data/player_ID.pkl','rb') as file:
        player_ID = pickle.load(file)
    with open('data/engine.pickle','rb') as file:
        engine = pickle.load(file)
    return [player_df, player_ID, engine]

outfield_data = getData()

header = st.container()
data_info1 = st.container()
params = st.container()
result = st.container()


with header:
    st.title('League One Player Similarity Tool')

with params:
    st.text(' \n')
    st.text(' \n')
    st.header('Tweak your search')
    
    col2, col3 = st.columns([2.2, 0.8])    
    with col2:
        df, player_ID, engine = outfield_data
        players = sorted(list(player_ID.keys()))
        age_default = (15, max(df['age']))
        query = st.selectbox('Player name', players, 
            help='Start typing a player name or club.')
    col4, col6, col7 = st.columns([0.7, 1, 1])
    with col4:
        res, val, step = (5, 20), 10, 5
        count = st.slider('Number of results', min_value=res[0], max_value=res[1], value=val, step=step)
    with col6:
        comparison = st.selectbox('Compare with', ['All positions', 'Same position'],
            help='You can search against all positions in the database, or just for the same position as your player.')
    with col7:
        age = st.slider('Age bracket', min_value=age_default[0], max_value=age_default[1], value=age_default, 
        help='Narrow down the age range of matches with the slider.')
    

    
with result:
    st.text(' \n')
    st.text(' \n')
    st.text(' \n')
    st.markdown('_The below players are most similar to:_ **{}**'.format(query))

def getRecommendations(metric, comparison='All positions', age=[0,23], count=25):
    df_res = df.iloc[:, [3, 5, 10, 11, 12]].copy()
    #df_res['Player'] = list(player_ID.keys())
    df_res.insert(0, 'Similarity', metric)
    df_res.insert(0,'Player', list(player_ID.keys()))
    df_res = df_res.sort_values(by=['Similarity'], ascending=False)
    metric = [str(num) + '%' for num in df_res['Similarity']]
    df_res['Similarity'] = metric
    # ignoring the top result
    df_res = df_res.iloc[1:, :]
    
    # comparison filtering
    if comparison == 'Same position':
        q_pos = list(df[df['Player']==query.split(' (')[0]].Pos)[0]
        df_res = df_res[df_res['Pos']==q_pos]
        
    # age filtering
    df_res = df_res[(df_res['age'] >= age[0]) & (df_res['age'] <= age[1])]

    # returning the final result
    df_res = df_res.iloc[:count, :].reset_index(drop=True)
    df_res.index = df_res.index + 1
    mp90 = [str(round(num, 1)) for num in df_res['minutes_90s']]
    df_res['minutes_90s'] = mp90
    df_res = df_res.astype({'goals':int,'assists':int})
    df_res.rename(columns={'position':'Position', 'age': 'Age','minutes_90s':'90s','goals':'Goals','assists':'Assists'}, inplace=True)
    return df_res

sims = engine[query]
recoms = getRecommendations(sims, age=age, count=count)
st.table(recoms)