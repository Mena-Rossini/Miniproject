from flask import Flask, render_template
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.utils
import json

app = Flask(__name__)

# Load and preprocess data
responses_df = pd.read_csv('dataset.csv')
responses_df.drop_duplicates(inplace=True)
categorical_columns = responses_df.select_dtypes(include=['object']).columns
responses_df[categorical_columns] = responses_df[categorical_columns].fillna('No Response')
no_variance_cols = [col for col in responses_df.columns if responses_df[col].nunique() <= 1]
responses_df.drop(columns=no_variance_cols, inplace=True)
responses_df['Hours per Week (numeric)'] = responses_df['On average, how many hours per week do you spend using digital learning tools?'].map({
    '1-3 hours': 2, '4-6 hours': 5, '7-10 hours': 8, '11-15 hours': 13, 'More than 15 hours': 16})
responses_df['Improvement (binary)'] = responses_df['Do you feel that digital learning tools have helped improve your grades or academic performance?'].map({
    'Yes': 1, 'No': 0, 'Sometimes': 0.5})
responses_df['Engagement (numeric)'] = responses_df['How engaged do you feel during online classes or while using digital learning tools compared to traditional classroom settings?'].map({
    'Much more engaged': 2, 'Slightly more engaged': 1, 'About the same': 0, 'Slightly less engaged': -1, 'Much less engaged': -2})
responses_df['Hours_Improvement'] = responses_df['Hours per Week (numeric)'] * responses_df['Improvement (binary)']

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/histogram')
def histogram():
    fig = px.histogram(responses_df, x='Hours per Week (numeric)', nbins=10, title='Distribution of Hours Spent on Digital Learning Tools')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('histogram.html', plot=graphJSON)

@app.route('/countplot')
def countplot():
    fig = px.histogram(responses_df, x='Do you feel that digital learning tools have helped improve your grades or academic performance?', 
                       color='Do you feel that digital learning tools have helped improve your grades or academic performance?', title='Perception of Improvement in Academic Performance')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('countplot.html', plot=graphJSON)

@app.route('/heatmap')
def heatmap():
    corr_matrix = responses_df[['Hours per Week (numeric)', 'Improvement (binary)', 'Engagement (numeric)', 'Hours_Improvement']].corr()
    fig = go.Figure(data=go.Heatmap(z=corr_matrix.values, x=corr_matrix.columns, y=corr_matrix.columns, colorscale='Viridis'))  # Changed colorscale to 'Viridis'
    fig.update_layout(title='Correlation Heatmap of Numeric Features')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('heatmap.html', plot=graphJSON)

@app.route('/boxplot')
def boxplot():
    fig = px.box(responses_df, x='Do you feel that digital learning tools have helped improve your grades or academic performance?', 
                 y='Hours per Week (numeric)', title='Hours Spent vs Perceived Improvement in Academic Performance')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('boxplot.html', plot=graphJSON)

@app.route('/pairplot')
def pairplot():
    fig = px.scatter_matrix(responses_df, dimensions=['Hours per Week (numeric)', 'Improvement (binary)', 'Engagement (numeric)', 'Hours_Improvement'], 
                            color='Improvement (binary)', title='Pair Plot of Numeric Features')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('pairplot.html', plot=graphJSON)

if __name__ == '__main__':
    app.run(debug=True)
