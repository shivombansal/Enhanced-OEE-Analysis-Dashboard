import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict
from openai import OpenAI
import httpx
import os
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders


# Add custom CSS for button styling
st.set_page_config(page_title="Enhanced OEE Analysis Dashboard", layout="wide")

# Custom CSS for button styling
st.markdown("""
<style>
    /* Light mode styles */
    @media (prefers-color-scheme: light) {      
        /* Base button styling */
        .stButton > button {
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 600;
            transition: all 0.3s ease;
            position: relative;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transform: translateY(0);
            background: linear-gradient(145deg, #ffffff, #e6e6e6);
            color: #333333;
            border: 1px solid rgba(0, 0, 0, 0.1);
        }
        
        /* Hover effect for buttons */
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2);
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            padding: 4px;
        }

        .stTabs [data-baseweb="tab"] {
            border: 1px solid rgba(0, 0, 0, 0.1);
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 600;
            transition: all 0.3s ease;
            background: linear-gradient(145deg, #ffffff, #e6e6e6);
            color: #333333;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transform: translateY(0);
        }

        .stTabs [data-baseweb="tab"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2);
            cursor: pointer;
        }

        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(145deg, #e6e6e6, #ffffff);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            transform: translateY(1px);
        }
    }

    /* Dark mode styles */
    @media (prefers-color-scheme: dark) {
        /* Base button styling */
        .stButton > button {
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 600;
            transition: all 0.3s ease;
            position: relative;
            box-shadow: 0 4px 6px rgba(98, 81, 81, 0.31);
            transform: translateY(0);
            background: linear-gradient(145deg, #2d2d2d, #1a1a1a);
            color: #ffffff;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* Hover effect for buttons */
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(98, 81, 81, 0.78);
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            padding: 4px;
        }

        .stTabs [data-baseweb="tab"] {
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 600;
            transition: all 0.3s ease;
            background: linear-gradient(145deg, #2d2d2d, #1a1a1a);
            color: #ffffff;
            box-shadow: 0 4px 6px rgba(98, 81, 81, 0.31);
            transform: translateY(0);
        }

        .stTabs [data-baseweb="tab"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(98, 81, 81, 0.78);
            cursor: pointer;
        }

        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(145deg, #1a1a1a, #2d2d2d);
            box-shadow: 0 2px 4px rgba(98, 81, 81, 0.31);
            transform: translateY(1px);
        }
    }

    /* Shared active/click effects */
    .stButton > button:active {
        transform: translateY(1px);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    /* File uploader styling */
    .stFileUploader > button {
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.3s ease;
        position: relative;
        transform: translateY(0);
    }

    /* Light mode for file uploader */
    @media (prefers-color-scheme: light) {
        .stFileUploader > button {
            background: linear-gradient(145deg, #ffffff, #e6e6e6);
            color: #333333;
            border: 1px solid rgba(0, 0, 0, 0.1);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
    }

    /* Dark mode for file uploader */
    @media (prefers-color-scheme: dark) {
        .stFileUploader > button {
            background: linear-gradient(145deg, #2d2d2d, #1a1a1a);
            color: #ffffff;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 4px 6px rgba(98, 81, 81, 0.31);
        }
    }

    /* Hover effect for file uploader */
    .stFileUploader > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2);
    }

    /* Active/Click effect for file uploader */
    .stFileUploader > button:active {
        transform: translateY(1px);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)


def get_openai_client():
    """Create and return an OpenAI client configured with Portkey gateway."""
    try:
        client = OpenAI(
            api_key=st.secrets["OPENAI_API_KEY"],
            base_url=PORTKEY_GATEWAY_URL,
            default_headers=createHeaders(
                provider="openai",
                api_key=st.secrets["PORTKEY_API_KEY"]
            ),
            http_client=httpx.Client()
        )
        return client
    except Exception as e:
        st.error(f"Error initializing OpenAI client: {e}")
        return None

def get_openai_analysis(data: pd.DataFrame, prompt: str) -> str:
    """Get OpenAI analysis."""
    client = get_openai_client()
    if not client:
        return "OpenAI client initialization failed. Please check your configuration."
    
    try:
        data_str = data.to_string()
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": """
                    You are Plastech AI — an expert manufacturing and OEE analyst. 
                    Your goal is to analyze production performance and provide:
                    - Clear, structured, step-by-step insights
                    - Actionable recommendations
                    - Zero fluff, no vague statements
                    - Direct reference to the data patterns (OEE, quality, downtime, production)
                    
                    Rules you must follow:
                    1. Always structure your answer using headings and bullet points.
                    2. When giving insights, reference specific performance patterns (e.g., low OEE, high downtime, quality issues).
                    3. Provide short, actionable recommendations.
                    4. If data is missing or uncertain, state it clearly instead of assuming.
                    5. Never hallucinate data.
                    6. Keep explanations concise but informative.
                    """},
                {"role": "user", "content": f"""User's questions: {prompt}
                
                \n\nData:\n\n {data_str} """}
            ],
            temperature=0.7,
            max_tokens=3200
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error getting OpenAI analysis: {str(e)}"

def get_openai_qa(data: pd.DataFrame, question: str) -> str:
    """NLP-powered Q&A model that interprets the question and explains the results."""
    client = get_openai_client()
    if not client:
        return "OpenAI client initialization failed."

    try:
        data_str = data.to_string()

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
                        You are Plastech AI — an advanced manufacturing data analyst.
                        
                        Your job is to ANSWER the user’s question using:
                        - NLP interpretation of their intent, and
                        - Data-driven results from the dataset provided.
                        
                        Your responses MUST follow these principles:
                        
                        1. **Perform the analysis silently** — do NOT describe the method.
                        2. **Explain the results clearly**:
                           - Identify what patterns, values, or rankings mean.
                           - Highlight why something is high/low/strong/weak.
                        3. **Use tables, short paragraphs, or bullet points** to present insights.
                        4. **All values must come from the dataset** — no invented numbers.
                        5. **If the question is ambiguous**, interpret it in the most logical way and state your interpretation.
                        6. **If the question cannot be fully answered**, explain what's missing AND provide partial insights.
                        
                        Tone:
                        - Analytical, confident, concise.
                        - Objective and professional.
                        - No fluff, no motivational talk.
                        
                        Your goal is to give:
                        ➡ A correct numerical/data result  
                        ➡ A short explanation of what it shows  
                        """
                },
                {
                    "role": "user",
                    "content": f"User Question: {question}\n\nDataset:\n{data_str}"
                }
            ],
            temperature=0.4,
            max_tokens=2400
        )

        return completion.choices[0].message.content

    except Exception as e:
        return f"Error getting AI Q&A response: {e}"


def create_visualizations(df: pd.DataFrame, selected_machine: str, selected_mold: str, selected_operator: str) -> Dict[str, go.Figure]:
    """Create various visualizations for the data."""
    figures = {}

    if 'Planned Downtime' in df.columns and 'Unplanned Downtime' in df.columns:
        # Create a copy of the dataframe for filtering
        plot_df = df.copy()
        
        # If all filters are set to 'All', show only top 7 machines
        if selected_machine == 'All' and selected_mold == 'All' and selected_operator == 'All':
            # Calculate total downtime and add as a column
            plot_df['Total_Downtime'] = plot_df['Planned Downtime'] + plot_df['Unplanned Downtime']
            # Get top 7 machines
            top_machines = (plot_df.groupby('Machine Name')['Total_Downtime']
                          .sum()
                          .nlargest(7)
                          .index)
            plot_df = plot_df[plot_df['Machine Name'].isin(top_machines)]
        
        # Group by Machine Name to get total downtimes
        machine_downtimes = plot_df.groupby('Machine Name').agg({
            'Planned Downtime': 'sum',
            'Unplanned Downtime': 'sum'
        }).reset_index()
        
        downtime_fig = go.Figure()
        downtime_fig.add_trace(go.Bar(
            x=machine_downtimes['Machine Name'],
            y=machine_downtimes['Planned Downtime'],
            name='Planned Downtime',
            marker_color='rgba(55, 128, 191, 0.7)',
            width=0.35
        ))
        downtime_fig.add_trace(go.Bar(
            x=machine_downtimes['Machine Name'],
            y=machine_downtimes['Unplanned Downtime'],
            name='Unplanned Downtime',
            marker_color='rgba(219, 64, 82, 0.7)',
            width=0.35
        ))
        
        # Update layout
        title_text = 'Planned vs. Unplanned Downtime'
            
        downtime_fig.update_layout(
            barmode='group',
            title=title_text,
            xaxis_title='Machine Name',
            yaxis_title='Downtime (hours)',
            legend_title='Downtime Type',
            yaxis=dict(gridcolor='lightgrey'),
            xaxis=dict(tickangle=-45),
            bargap=0.15,
            bargroupgap=0.1
        )
        figures['downtime_stacked_bar'] = downtime_fig

    if 'Good Part_sum' in df.columns and 'Bad Part (nos.)_sum' in df.columns:
        good_parts = df['Good Part_sum'].sum()
        bad_parts = df['Bad Part (nos.)_sum'].sum()
        pie_chart = go.Figure(
            data=[go.Pie(
                labels=['Good Parts', 'Bad Parts'],
                values=[good_parts, bad_parts],
                hole=0.4,
                marker=dict(colors=['#2ca02c', '#d62728'])
            )]
        )
        pie_chart.update_layout(
            title='Good vs. Bad Parts Produced',
            annotations=[dict(
                text=f"{good_parts / (good_parts + bad_parts) * 100:.1f}% Good",
                x=0.5,
                y=0.5,
                font_size=16,
                showarrow=False
            )]
        )
        figures['quality_pie_chart'] = pie_chart

    # Example Trend Line and Bar Chart (existing logic)
    figures['trend_line'] = px.strip(
        df.head(15),
        x='Operator',
        y='OEE_mean',
        title='Trend Line: OEE by top Operators',
        labels={
            'Operator': 'Operator',
            'OEE_mean': 'Average OEE (%)'
        }
    )

    figures['avg_oee_top10'] = px.bar(
        df.head(11),
        x='Machine Name',
        y='OEE_mean',
        color='Operator',
        barmode='group',
        hover_data=['Mold Name', 'Total Production_sum'],
        title='Top Combinations by Average OEE',
        labels={
            'OEE_mean': 'Average OEE (%)',
            'Machine Name': 'Machine',
            'Operator': 'Operator'
        }
    )

    figures['avg_oee_top10'].update_layout(
        yaxis_title="OEE (%)",
        xaxis_title="Machine",
        bargap=0.01,
        bargroupgap=0.5,
        yaxis=dict(
            gridwidth=1,
            zeroline=False
        ),
        xaxis=dict(
            zeroline=False
        ),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="right",
            x=1.3498
        )
    )

    figures['avg_oee_top10'].update_traces(width=0.2)

    return figures

def analyze_production_data(data: pd.DataFrame) -> pd.DataFrame:
    """Analyze production data to calculate metrics for machine-mold-operator combinations."""
    # Group by machine, mold, and operator
    grouped = data.groupby(['Machine Name', 'Mold Name', 'Operator'])
    
    # Calculate metrics for each combination
    combinations = grouped.agg({
        'OEE': ['mean', 'std', 'count'],
        'Good Part': ['sum'],
        'Bad Part (nos.)': ['sum'],
        'Total Production': ['sum'],
        'Plan D/T': ['sum'],  # Include Planned Downtime
        'Unplan D/T': ['sum']  # Include Unplanned Downtime
    }).reset_index()
    
    # Flatten column names
    combinations.columns = [
        f'{col[0]}{"_" + col[1] if col[1] else ""}' 
        for col in combinations.columns
    ]
    
    # Convert minutes to hours for better visualization
    combinations['Planned Downtime'] = combinations['Plan D/T_sum'] / 60
    combinations['Unplanned Downtime'] = combinations['Unplan D/T_sum'] / 60
    
    # Correct Quality Rate Calculation (Option 1)
    import numpy as np
    
    total_parts = combinations['Good Part_sum'] + combinations['Bad Part (nos.)_sum']
    
    combinations['Quality_Rate'] = np.where(
        total_parts > 0,
        (combinations['Good Part_sum'] / total_parts) * 100,
        0
    )


    
    # Sort by OEE mean in descending order
    combinations = combinations.sort_values('OEE_mean', ascending=False)
    
    return combinations

def main():
    
    try:
        uploaded_file = st.file_uploader("Upload your CSV file", type="csv")
        if uploaded_file is not None:
            data = pd.read_csv(uploaded_file)
        else:
            st.warning("Please upload a CSV file")
            return
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return

    # Perform production data analysis
    df_combinations = analyze_production_data(data)
    
    # Create tabs for different sections
    tab1, tab2 = st.tabs(["Dashboard", "Ask Plastech AI"])
    
    # Tab 1: Dashboard
    with tab1:
        st.markdown("### Overall Efficiency Dashboard")
        
        with st.sidebar:
            
            machines = ['All'] + sorted(df_combinations['Machine Name'].unique().tolist())
            selected_machine = st.selectbox('Select Machine:', machines, key='dash_machine')
            molds = ['All'] + sorted(df_combinations['Mold Name'].unique().tolist())
            selected_mold = st.selectbox('Select Mold:', molds, key='dash_mold')
            operators = ['All'] + sorted(df_combinations['Operator'].unique().tolist())
            selected_operator = st.selectbox('Select Operator:', operators, key='dash_operator')

            # Apply filters
            filtered_df = df_combinations.copy()
            if selected_machine != 'All':
                filtered_df = filtered_df[filtered_df['Machine Name'] == selected_machine]
            if selected_mold != 'All':
                filtered_df = filtered_df[filtered_df['Mold Name'] == selected_mold]
            if selected_operator != 'All':
                filtered_df = filtered_df[filtered_df['Operator'] == selected_operator]
        
        # Create and display visualizations
        figures = create_visualizations(filtered_df, selected_machine, selected_mold, selected_operator)
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(figures['trend_line'], use_container_width=True)
        with col2:
            st.plotly_chart(figures['avg_oee_top10'], use_container_width=True)
            
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(figures['downtime_stacked_bar'], use_container_width=True)
        with col2:
            st.plotly_chart(figures['quality_pie_chart'], use_container_width=True)
        
        
        with st.sidebar:
            if filtered_df.empty:
                st.metric("Average OEE", "0%")
                st.metric("Best OEE", "0%")
                st.metric("Total Combinations(Machine-Mould-Operator)", 0)
                st.metric("Average Quality Rate", "0%")
                st.metric("Average Good Parts (%)", "0%")
            else:
                st.metric("Average OEE", f"{filtered_df['OEE_mean'].mean():.2f}%")
                st.metric("Best OEE", f"{filtered_df['OEE_mean'].max():.2f}%")
                st.metric("Total Combinations(Machine-Mould-Operator)", len(filtered_df))
                st.metric("Average Quality Rate", f"{filtered_df['Quality_Rate'].mean():.2f}%")
                
                total_good_parts = filtered_df['Good Part_sum'].sum()
                total_production = filtered_df['Total Production_sum'].sum()
                
                if total_production > 0:
                    avg_good_parts_percentage = (total_good_parts / total_production) * 100
                    st.metric("Average Good Parts (%)", f"{avg_good_parts_percentage:.2f}%")
                else:
                    st.metric("Average Good Parts (%)", "0%")
                
        
        
        st.markdown("### Evaluated Data")
        
        
        # Update display columns to include downtime
        display_columns = {
            'Machine Name': 'Machine',
            'Mold Name': 'Mold',
            'Operator': 'Operator',
            'OEE_mean': 'Avg OEE (%)',
            'OEE_count': 'Number of Runs',
            'Good Part_sum': 'Total Good Parts',
            'Bad Part (nos.)_sum': 'Total Bad Parts',
            'Total Production_sum': 'Total Production',
            'Quality_Rate': 'Quality Rate (%)',
            'Plan D/T_sum': 'Planned D/T (Hours)',
            'Unplan D/T_sum': 'Unplanned D/T (Hours)'
        }
    
        filtered_df_display = filtered_df.rename(columns=display_columns)
        st.dataframe(
            filtered_df_display[display_columns.values()],
            hide_index=True,
            use_container_width=True
        )
    
        st.markdown("### Plastech AI Analysis")
        
        if st.button("Generate AI Analysis", key="generate_analysis"):
            top_combinations = filtered_df
            analysis_prompt = analysis_prompt = """
                Analyze the machine-mold-operator production dataset. Provide:
                
                ### 1️⃣ Key Performance Summary
                - Overall OEE trends
                - Quality performance (good vs. bad parts)
                - Planned vs. unplanned downtime
                - Production volume distribution
                
                ### 2️⃣ Top-Performing Combinations
                Identify which machine-mold-operator combinations perform the best and why.
                
                ### 3️⃣ Underperforming Combinations
                Identify combinations with:
                - Low OEE
                - High downtime
                - Poor quality rate
                - Low production consistency
                Explain the likely reason.
                
                ### 4️⃣ Pattern Recognition
                Identify:
                - Operator-based patterns
                - Machine-based efficiency patterns
                - Mold-related issues
                - Correlation between downtime and quality
                
                ### 5️⃣ Recommendations
                Give clear, actionable steps to improve:
                - OEE
                - Productivity
                - Quality
                - Downtime mitigation
                
                Use the data provided — do NOT make up numbers. 
                """
            
            with st.spinner("Generating analysis..."):
                analysis = get_openai_analysis(top_combinations, analysis_prompt)
                st.markdown(analysis)
    
    # Tab 2: Query Assistant
    with tab2:
        st.markdown("### Ask Plastech AI")
        user_query = st.text_area("Ask a question about the production data:", 
                                height=100,
                                placeholder="Example: Which machine-mold combinations have the highest quality rates?")
        
        if st.button("Get Answer"):
            with st.spinner("Analyzing..."):
                answer = get_openai_qa(df_combinations, user_query)
                st.markdown("### Answer")
                st.markdown(answer)
                

if __name__ == "__main__":
    main()



