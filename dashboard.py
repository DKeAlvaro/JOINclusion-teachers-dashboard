import streamlit as st
import json
import pandas as pd
import plotly.express as px
from data_analysis import get_different_types, get_feature_vectors, filter_non_played
import plotly.graph_objects as go



st.title("JOINclusion Dashboard")
data = st.file_uploader("Choose a JSON file", type="json")


if data:
    data = json.load(data)
    size= 15 if len(data) > 15 else len(data)
    # index = random.randint(0, len(data)-size)
    index=0
    data = filter_non_played(data)[index:index+size]

    interaction_vectors, full_vectors, usernames, feature_names = get_feature_vectors(data)
    unique_backgrounds, unique_languages, unique_ethnicities = get_different_types(data)

    df = pd.DataFrame(full_vectors, columns=feature_names)
    # st.write(df)

    best_students = df.nlargest(5, "best_score")[["name", "best_score"]]
    worst_students = df.nsmallest(5, "best_score")[["name", "best_score"]]
    col1, col2 = st.columns(2)

    scenarios = ["Scenario 1", "Scenario 2"]
    for scenario in scenarios:
        score_column = "best_score_s1" if scenario == "Scenario 1" else "best_score_s2"
        scenario_df = df[["name", score_column]].sort_values(score_column, ascending=False)
        fig = px.bar(
            scenario_df,
            x="name",
            y=score_column,
            color=score_column,
            title=f"Scores for {scenario}"
        )
        fig.update_layout(xaxis_title=None)
        st.plotly_chart(fig)


    with col1:
        st.write("Highest score students:")
        st.write(best_students)

    with col2:
        st.write("Lowest score students:")
        st.write(worst_students)

    if 'student_names' not in st.session_state:
        st.session_state.student_names = df['name'].unique()

    selected_student = st.selectbox(
        'Select a student:',
        df['name'].unique(),
        index=0
    )

    student_data = df[df['name'] == selected_student]

    features_to_display = ['best_score', 'total_time_played', 'total_interactions', "total_helps"]

    cols = [st.columns(2), st.columns(2)]  

    for idx, feature in enumerate(features_to_display):
        row = idx // 2  
        col = idx % 2  
        with cols[row][col]:
            student_value = student_data[feature].iloc[0]
            # mean_value = df[feature].mean()
            # median_value = df[feature].median()
            fig = go.Figure()

            nbins = min(len(df[feature].unique()), 10)
            fig.add_trace(go.Histogram(
                x=df[feature],
                name='Distribution',
                marker=dict(color='lightblue'),
                opacity=0.75,
                nbinsx=nbins
            ))
            fig.add_trace(go.Scatter(
                x=[student_value],
                y=[0],
                mode='markers',
                marker=dict(size=32, color='red', symbol='line-ns-open', line=dict(width=2)),
                name=selected_student,
                hovertemplate=f"{selected_student}: <b>{student_value:,.0f}</b><extra></extra>"
            ))
            fig.update_layout(
                title=dict(
                    text=f"{feature.replace('_', ' ').title()}",
                    x=0.25
                ),
                xaxis=dict(title=feature.replace('_', ' ').title()),
                yaxis=dict(title='Count'),
                height=300,
                width=300,
                margin=dict(l=40, r=40, t=40, b=40),
                showlegend=False,
                bargap=0.1
            )
            st.plotly_chart(fig, use_container_width=False)

    features = ["best_score","best_score_s1","best_score_s2","total_time_played","total_interactions","num_sessions","total_helps"]
    optional = ["total_help_s1","total_help_s2","total_character_interactions_s1","total_character_interactions_s2","total_change_scene_interactions_s1","total_change_scene_interactions_s2","total_movement_interactions_s1","total_movement_interactions_s2"]

    include_optional = st.pills(
        '',
        options=['Overall','Detailed'],
        default = 'Overall'
    )
    if include_optional == 'Detailed':
        features.extend(optional)

    percentiles = {}
    for feature in features:
        student_value = student_data[feature].iloc[0]
        percentile = (df[feature] <= student_value).mean() * 100
        percentiles[feature] = percentile

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=[percentiles[feat] for feat in features],
        theta=features,
        fill='toself',
        name=selected_student,
        hovertemplate=f"{selected_student}"
    ))

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                tickfont=dict(size=12, color='gray'),
                range=[0, 100]
            )
        ),
        showlegend=False,
        title=f"Percentile Rankings for {selected_student}",
        height=500,
        width=800
    )
    st.plotly_chart(fig_radar, use_container_width=False)



    # correlation_matrix_features = ["best_score","num_sessions", "total_time_played", "total_interactions", "total_helps",
    #                                "age", "migration_age", "gender_sex"]
    # corr_matrix = df[correlation_matrix_features].corr()


    # fig_corr = px.imshow(corr_matrix.round(2),
    #                     x=correlation_matrix_features,
    #                     y=correlation_matrix_features,
    #                     color_continuous_scale='RdBu_r',
    #                     title="Feature Correlation Matrix",
    #                     height=600,
    #                     width=600,
    #                     text_auto=True) 

    # fig_corr.update_layout(
    #     xaxis_title_font=dict(size=16),  
    #     yaxis_title_font=dict(size=16),  
    #     title_font=dict(size=20),  
    #     xaxis=dict(tickfont=dict(size=14)), 
    #     yaxis=dict(tickfont=dict(size=14))  
    # )

    # st.plotly_chart(fig_corr, use_container_width=False)
