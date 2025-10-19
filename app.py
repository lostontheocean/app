import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Wczytywanie danych
@st.cache_data
def load_data():
    df1 = pd.read_excel('v2_M3_smaller_wyniki_25000.xlsx', index_col=[0, 1, 2, 3])
    df2 = pd.read_excel('v2_M3_smaller_wyniki_50000.xlsx', index_col=[0, 1, 2, 3])
    df = pd.concat([df1, df2]).reset_index()
    return df

df = load_data()

# Parametry
Qs = [25000, 50000]
Ls = [1, 2]
available_models = sorted(df['index'].unique())

# Interfejs użytkownika
st.title("Efficiency Curve Visualization")

st.markdown('''In this application we present the individual outputs for the results of the computation obtained in the manuscript (full details printed after the blind revision). The Methods to select are following:

- Method I assumes data generation according to model (3), 

- Method II relies on joint parameter estimation in equation (8), 

- Method III employs the GAS(1,1) model, 

- Method IV utilizes distributional forecasts generated via DeepAR, 

- Method V applies a two-step procedure without distributional assumptions, 

- Method VI is based on model (11), 

- Method VII presents outcomes obtained using the average of forecasts produced by Methods I–VI. 

To print one individual or multiple curves, select the model under proper settings of L and Q.''')

selected_Q = st.selectbox("Select demand quantity (Q):", Qs)
selected_L = st.selectbox("Select lead time (L):", [0,1])

unroman = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7}
available_models = list(unroman.keys())

selected_models = st.multiselect("Select Methods:", available_models, default=['II'])

unroman = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7}

# Rysowanie wykresu
if selected_models:
    maxes = []
    mins = []
    fig = go.Figure()
    
    for r_model in selected_models:
        model = unroman[r_model]
        data = df[(df['Q'] == selected_Q) & (df['L'] == selected_L+1) & (df['index'] == model)]
        fig.add_trace(go.Scatter(
            x=data['Mean inventory per demand unit'],
            y=data['FR'],
            mode='markers+lines',
            name=str(r_model),
            text=[f"Method {r_model}<br>FR: {fr:.3f}<br>Inventory: {inv:.3f}"
                  for fr, inv in zip(data['FR'], data['Mean inventory per demand unit'])],
            hoverinfo='text',
        ))
        maxes.append(max(data['Mean inventory per demand unit'] + .005))
        mins.append(min(data['Mean inventory per demand unit'] - .005))

    fig.update_layout(
        title=f'Efficiency Curves for Q = {selected_Q}, L = {selected_L}',
        xaxis=dict(range=[min(mins), 
                          max(maxes)]),
        xaxis_title='Mean inventory per demand unit',
        yaxis_title='Empirical FR',
        hovermode='closest',
        template='plotly_white'
    )

    # Dodanie poziomych linii referencyjnych
    for fr in [0.95, 0.975, 0.99, 0.995]:
        fig.add_shape(type='line',
                      x0=min(df['Mean inventory per demand unit'] - .005),
                      x1=max(df['Mean inventory per demand unit'] + .005),
                      y0=fr, y1=fr,
                      line=dict(color='gray', dash='dot'),
                      name=f'FR={fr}')

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Please select at least one method to generate the plot.")
