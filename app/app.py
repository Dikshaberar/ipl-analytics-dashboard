from flask import Flask, render_template, jsonify
import pandas as pd
import plotly.express as px
import plotly.utils
import json

app = Flask(__name__)

matches = pd.read_csv('../data/matches.csv')
deliveries = pd.read_csv('../data/deliveries.csv')
matches = matches.dropna(subset=['winner'])

def make_chart(fig):
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/team_wins')
def team_wins():
    data = matches['winner'].value_counts().head(10).reset_index()
    data.columns = ['team', 'wins']
    data = data.sort_values('wins', ascending=True)
    fig = px.bar(data, x='wins', y='team', orientation='h',
                 color='wins', color_continuous_scale='Oranges',
                 title='🏆 Most Successful Teams', text='wins')
    fig.update_layout(plot_bgcolor='#0f0f0f', paper_bgcolor='#1a1a2e',
                      font_color='white', showlegend=False)
    fig.update_traces(textposition='outside', textfont_color='white')
    return jsonify(make_chart(fig))

@app.route('/api/top_batsmen')
def top_batsmen():
    data = deliveries.groupby('batter')['batsman_runs'].sum().reset_index()
    data.columns = ['batter', 'runs']
    data = data.sort_values('runs', ascending=False).head(10)
    fig = px.bar(data, x='batter', y='runs', color='runs',
                 color_continuous_scale='Oranges',
                 title='🏏 Top 10 Run Scorers', text='runs')
    fig.update_layout(plot_bgcolor='#0f0f0f', paper_bgcolor='#1a1a2e',
                      font_color='white', showlegend=False, xaxis_tickangle=30)
    fig.update_traces(textposition='outside', textfont_color='white')
    return jsonify(make_chart(fig))

@app.route('/api/top_bowlers')
def top_bowlers():
    w = deliveries[(deliveries['is_wicket'] == 1) &
                   (~deliveries['dismissal_kind'].isin(['run out', 'retired hurt']))]
    data = w.groupby('bowler')['is_wicket'].count().reset_index()
    data.columns = ['bowler', 'wickets']
    data = data.sort_values('wickets', ascending=False).head(10)
    fig = px.bar(data, x='bowler', y='wickets', color='wickets',
                 color_continuous_scale='Blues',
                 title='🎯 Top 10 Wicket Takers', text='wickets')
    fig.update_layout(plot_bgcolor='#0f0f0f', paper_bgcolor='#1a1a2e',
                      font_color='white', showlegend=False, xaxis_tickangle=30)
    fig.update_traces(textposition='outside', textfont_color='white')
    return jsonify(make_chart(fig))

@app.route('/api/toss_impact')
def toss_impact():
    matches['toss_won_match'] = matches['toss_winner'] == matches['winner']
    data = matches['toss_won_match'].value_counts().reset_index()
    data.columns = ['result', 'count']
    data['label'] = data['result'].map({True: 'Won Toss & Match', False: 'Won Toss, Lost Match'})
    fig = px.pie(data, values='count', names='label', hole=0.4,
                 title='🪙 Toss Impact on Match Result',
                 color_discrete_sequence=['#f97316', '#1e293b'])
    fig.update_layout(paper_bgcolor='#1a1a2e', font_color='white')
    return jsonify(make_chart(fig))

@app.route('/api/season_runs')
def season_runs():
    season_cols = matches[['id', 'season']].copy()
    merged = deliveries.merge(season_cols, left_on='match_id', right_on='id')
    data = merged.groupby('season')['total_runs'].sum().reset_index()
    data.columns = ['season', 'total_runs']
    fig = px.line(data, x='season', y='total_runs', markers=True,
                  title='📈 Season-wise Total Runs',
                  line_shape='spline',
                  labels={'total_runs': 'Total Runs', 'season': 'Season'})
    fig.update_traces(line_color='#f97316',
                      marker=dict(size=10, color='white',
                                  line=dict(width=2, color='#f97316')))
    fig.update_layout(plot_bgcolor='#0f0f0f', paper_bgcolor='#1a1a2e',
                      font_color='white', xaxis_tickangle=45)
    return jsonify(make_chart(fig))

@app.route('/api/potm')
def potm():
    data = matches['player_of_match'].value_counts().head(10).reset_index()
    data.columns = ['player', 'awards']
    data = data.sort_values('awards', ascending=True)
    fig = px.bar(data, x='awards', y='player', orientation='h',
                 color='awards', color_continuous_scale='Purples',
                 title='⭐ Most Player of the Match Awards', text='awards')
    fig.update_layout(plot_bgcolor='#0f0f0f', paper_bgcolor='#1a1a2e',
                      font_color='white', showlegend=False)
    fig.update_traces(textposition='outside', textfont_color='white')
    return jsonify(make_chart(fig))

if __name__ == '__main__':
    app.run(debug=True)