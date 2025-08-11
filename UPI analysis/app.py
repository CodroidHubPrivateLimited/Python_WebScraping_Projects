from flask import Flask, render_template
import pandas as pd
import plotly
import plotly.graph_objects as go
import json

# Initialize the Flask application
app = Flask(__name__)

def create_core_plots():
    """Reads the analyzed data and creates the two main Plotly charts."""
    try:
        df = pd.read_csv('upi_analysis_output.csv')
        df['Date'] = pd.to_datetime(df['Date'])
    except FileNotFoundError:
        return None, None

    # Chart 1: Growth
    fig_growth = go.Figure()
    fig_growth.add_trace(go.Scatter(x=df['Date'], y=df['Volume_Absolute'] / 1e9, name='Volume (Billions)', yaxis='y1', line=dict(color='#4f46e5'))) # Indigo
    fig_growth.add_trace(go.Scatter(x=df['Date'], y=df['Value_Absolute_INR'] / 1e12, name='Value (₹ Trillion)', yaxis='y2', line=dict(color='#db2777'))) # Pink
    fig_growth.update_layout(
        title_text='<b>UPI Transaction Volume vs. Value</b>', title_x=0.5,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(title=dict(text='Volume (Billions)', font=dict(color='#4f46e5')), tickfont=dict(color='#4f46e5')),
        yaxis2=dict(title=dict(text='Value (₹ Trillion)', font=dict(color='#db2777')), tickfont=dict(color='#db2777'), overlaying='y', side='right')
    )

    # Chart 2: ATS
    fig_ats = go.Figure()
    fig_ats.add_trace(go.Scatter(x=df['Date'], y=df['ATS_INR'], name='Average Transaction Size', line=dict(color='#16a34a'))) # Green
    fig_ats.update_layout(
        title_text="<b>Declining Average Transaction Size (ATS)</b>", title_x=0.5,
        yaxis_title='Average Value per Transaction (in ₹)'
    )

    growth_chart_json = json.dumps(fig_growth, cls=plotly.utils.PlotlyJSONEncoder)
    ats_chart_json = json.dumps(fig_ats, cls=plotly.utils.PlotlyJSONEncoder)

    return growth_chart_json, ats_chart_json

def create_advanced_plots():
    """Creates new, advanced charts for deeper analysis."""
    try:
        df = pd.read_csv('upi_analysis_output.csv')
        df['Date'] = pd.to_datetime(df['Date'])
    except FileNotFoundError:
        return None, None

    # Chart 3: YoY Growth
    fig_yoy = go.Figure()
    fig_yoy.add_trace(go.Bar(
        x=df['Date'],
        y=df['YoY_Value_Growth_%'],
        name='YoY Value Growth',
        marker_color='#0891b2' # Cyan
    ))
    fig_yoy.update_layout(
        title_text="<b>Year-over-Year (YoY) Value Growth (%)</b>", title_x=0.5,
        yaxis_title='Growth Percentage (%)'
    )

    # Chart 4: Month-over-Month Volume Change
    df['MoM_Volume_Change_%'] = df['Volume_Absolute'].pct_change() * 100
    fig_mom = go.Figure()
    fig_mom.add_trace(go.Scatter(
        x=df['Date'],
        y=df['MoM_Volume_Change_%'],
        name='MoM Volume Change',
        line=dict(color='#ca8a04'), # Amber
        fill='tozeroy'
    ))
    fig_mom.update_layout(
        title_text="<b>Month-over-Month (MoM) Volume Change (%)</b>", title_x=0.5,
        yaxis_title='Percentage Change (%)'
    )

    yoy_chart_json = json.dumps(fig_yoy, cls=plotly.utils.PlotlyJSONEncoder)
    mom_chart_json = json.dumps(fig_mom, cls=plotly.utils.PlotlyJSONEncoder)

    return yoy_chart_json, mom_chart_json


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/story')
def story():
    return render_template('story.html')

@app.route('/analysis')
def analysis():
    growth_chart, ats_chart = create_core_plots()
    if growth_chart is None:
        return "Error: Could not load data.", 500
    return render_template('analysis.html', growth_chart=growth_chart, ats_chart=ats_chart)

# --- NEW ROUTE FOR ADVANCED ANALYSIS ---
@app.route('/advanced-analysis')
def advanced_analysis():
    yoy_chart, mom_chart = create_advanced_plots()
    if yoy_chart is None:
        return "Error: Could not load data.", 500
    return render_template('advanced_analysis.html', yoy_chart=yoy_chart, mom_chart=mom_chart)

@app.route('/data')
def data_explorer():
    try:
        df = pd.read_csv('upi_analysis_output.csv')
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%b %Y')
        df_display = df[['Date', 'Volume (in Mn)', 'Value (in Cr.)', 'ATS_INR']].copy()
        df_display.rename(columns={
            'Date': 'Month',
            'Volume (in Mn)': 'Volume (Millions)',
            'Value (in Cr.)': 'Value (₹ Crores)',
            'ATS_INR': 'Avg. Txn. Size (₹)',
        }, inplace=True)
        records = df_display.to_dict('records')
    except FileNotFoundError:
        return "Error: Could not load data.", 500
    return render_template('data.html', records=records)

@app.route('/conclusion')
def conclusion():
    return render_template('conclusion.html')

if __name__ == '__main__':
    app.run(debug=True)
