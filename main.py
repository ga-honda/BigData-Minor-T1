import streamlit as st

st.title("Avaliação de histórico de partidas de CS-GO:")
st.subheader("")

# Importando bibliotecas
import numpy as np
import pandas as pd


# Importando DataFrames
df_final = pd.read_csv('./data/df_final.csv', dtype='unicode')
df_players_f = pd.read_csv('./data/df_players_f.csv', dtype='unicode')
df_results_f = pd.read_csv('./data/df_results_f.csv', dtype='unicode')
df_stats_f = pd.read_csv('./data/df_stats_f.csv', dtype='unicode')
map_winner = pd.read_csv('./data/map_winner.csv', dtype='unicode')

#=========================================
#
# Mapas mais jogados por cada time
#
#=========================================
st.subheader("Mapas mais jogados por cada time")

teams0 = map_winner.team.unique()

team_selected0 = st.selectbox(
    'Escolha o time a ser analisado:', 
    teams0
)

map_winner2 = map_winner[['team', 'map', 'win_percentage', 'n_map']].loc[map_winner['team'] == team_selected0].sort_values(by = ['n_map'], ascending = False)

st.dataframe(map_winner2)
st.caption("Status do time em cada mapa")

#=========================================
#
# Ranking players
#
#=========================================
st.subheader("Ranking players")

# Atribuindo os tipos de variáveis para cada coluna de interesse
df_stats_f = df_stats_f.replace({'-': 0})
df_stats_f = df_stats_f.astype({
  'maps_played':'int64'
})
df_stats_f['hs_percentage'] = df_stats_f['hs_percentage'].str.rstrip('%').astype('float64')


columns = ['player_nick',
        'maps_played',
        'rounds_played',
        'dmg_round',
        'hs_percentage',
        'impact',
        'kd_ratio',
        'kills_round',
        'player_age',
        'rating_1',
        'total_kills',
        'total_deaths']

df_stats_f = df_stats_f[columns]


# Filtrando players que jogaram no mínimo 30 mapas
df_stats_f = df_stats_f[df_stats_f['maps_played'].notna()]
df_stats_f2 = df_stats_f.loc[(df_stats_f['maps_played'] > 30)]



# Seleção dos stats
stats = ['dmg_round',
        'hs_percentage',
        'impact',
        'kd_ratio',
        'kills_round',
        'player_age',
        'rating_1',
        'total_kills',
        'total_deaths',
        'survivability']

stats_selected = st.selectbox(
    'Escolha o stats a ser analisado:', 
    stats
)
df_stats_f2 = df_stats_f2.astype({
  'player_nick':'object',
  'dmg_round':'float64',
  'impact':'float64',
  'kd_ratio':'float64',
  'kills_round':'float64',
  'player_age':'int64',
  'rating_1':'float64',
  'total_kills':'int64',
  'total_deaths':'int64',
  'rounds_played':'int64',
  'maps_played':'int64'
})


if stats_selected == 'survivability':
  df_stats_f2 = df_stats_f2[['player_nick', 'total_deaths', 'rounds_played']].dropna()
  # Adicionando stats de survivability (Porcentagem de rounds que se manteve vivo no jogo)
  df_stats_f2['survivability'] = (1 - df_stats_f2.total_deaths/df_stats_f2.rounds_played)*100

top_players = df_stats_f2[['player_nick', stats_selected]].dropna()

#top_players[['player_nick', stats]].sort_values(by = stats, ascending= False)

st.dataframe(top_players.sort_values(by = stats_selected, ascending= False))
st.caption("Top players")


#=========================================
#
# Performance de times (timeline)
#
#=========================================
st.subheader("Performance de times (timeline)")

# Criando tabela contabilizando vitórias dos times no decorrer dos meses/anos
performance = df_results_f.groupby(['map_winner_name', 'year', 'month']).size().to_frame().unstack(fill_value=0).stack().rename(columns = {0:'n_wins'}).reset_index()
performance = performance.reset_index(drop = True)

# Seleção do time
teams = performance.map_winner_name.unique()

team_selected = st.selectbox(
    'Escolha o time a ser analisado:', 
    teams
)

# Tabela apenas com Year-Month e vezes jogadas
idx = df_results_f.index[(df_results_f["team_1_name"] == team_selected) | (df_results_f["team_2_name"] == team_selected)].tolist()
games_played = df_results_f.loc[idx].groupby(['year', 'month']).size().to_frame().rename(columns = {0:'games_played'}).reset_index()
games_played = games_played.reset_index(drop = True)


# Unindo colunas de datas para o formato Year-Month
cols = ['year', 'month']
performance['date'] = performance[cols].apply(lambda x: '-'.join(x.values.astype(str)), axis = 'columns')
performance['date'] = pd.to_datetime(performance['date'])
performance = performance.loc[performance['map_winner_name'] == team_selected].reset_index(drop = True)

games_played['date'] = games_played[cols].apply(lambda x: '-'.join(x.values.astype(str)), axis = 'columns')
games_played['date'] = pd.to_datetime(games_played['date'])

# Ordenando por data
performance = performance.sort_values(by = ['date']).reset_index(drop = True)
games_played = games_played.sort_values(by = ['date']).reset_index(drop = True)

# Unindo ambos os DF
df_merge = performance[['map_winner_name', 'year', 'month', 'n_wins', 'date']].merge(games_played[['games_played', 'date']], on='date', how='right')

# Streamlit
st.dataframe(df_merge[['map_winner_name', 'year', 'month', 'n_wins', 'games_played']])
st.caption("Histórico de vitórias do time")
st.line_chart(data = df_merge, x = 'date', y = ['n_wins', 'games_played'])


#=========================================
#
# Winrate TR e CT
#
#=========================================
st.subheader("Winrate TR e CT")

# Filtrando mapas com maior número de jogos jogados
mapas = ['Overpass', 'Inferno', 'Mirage', 'Vertigo', 'Nuke', 'Dust2', 'Train', 'Cobblestone', 'Cache']
df_results_f2 = df_results_f.loc[df_results_f.map.isin(mapas)].reset_index(drop = True)


team_1 = df_results_f2[['team_1_id', 'team_1_name']].rename(columns = {"team_1_id": 'id', "team_1_name": 'teams'})
team_2 = df_results_f2[['team_2_id', 'team_2_name']].rename(columns = {"team_2_id": 'id', "team_2_name": 'teams'})
team_total = pd.concat([team_1, team_2], ignore_index = True).drop_duplicates()
teams2 = team_total.teams.unique()

# Selecionando o time a ser analisado
selected_options = st.multiselect(
    'Escolha o time a ser analisado:', 
    teams2
)
all_options = st.checkbox("Selecionar todas as opções")

if all_options:
  df_results_f3 = df_results_f2
else:
  idx2 = []
  for i in selected_options:
    list = (df_results_f2.index[(df_results_f2["team_1_name"] == i) | (df_results_f2["team_2_name"] == i)].tolist())
    idx2.extend(list)
  df_results_f3 = df_results_f2.loc[idx2]#.reset_index(drop = .True)

# Número de vezes jogadas para cada mapa
n_mapas = df_results_f3.groupby(['map']).size()
n_mapas = n_mapas.to_frame().rename(columns = {0:'n_maps'}).reset_index().sort_values(by = ['map'], ascending=True)

# Criando tabela com os resultados
n_tr = df_results_f3.groupby(['map', 'side_winner']).size()
n_tr = n_tr.sort_values(ascending=False).to_frame()
n_tr = n_tr.reset_index().sort_values(by=['map', 'side_winner']).rename(columns = {0:'wins'})

# Inserindo coluna de Win Percentage
win_perc = [0]*n_tr.shape[0]
for i in range(n_tr.shape[0]):
  if i%2 == 0:
    k = int(i/2)
    win_perc[i] = n_tr.iloc[i,2]/n_mapas.iloc[k,1]*100
  else:
    k = int((i-1)/2)
    win_perc[i] = n_tr.iloc[i,2]/n_mapas.iloc[k,1]*100

n_tr = n_tr.reset_index(drop = True)
n_tr['win_perc'] = win_perc

# Mostrando tabela no Streamlit
st.dataframe(n_tr)
st.caption("Porcentagem de vitórias de CT e TR em cada mapa")