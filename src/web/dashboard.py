"""
Healthcare Data QA Dashboard

A Streamlit-based dashboard for:
1. Visualizing data quality metrics
2. Exploring healthcare data
3. Reviewing data quality reports
4. Monitoring data quality trends

Author: Robert Torres
"""

import os
import json
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path

# Import our validation framework
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.ml.healthcare_validator import HealthcareModelValidator

def load_config():
    """Load configuration from file."""
    config_path = "config.json"
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            st.warning(f"Config file {config_path} not found. Using default configuration.")
            return {
                "db_path": "data/healthcare.db",
                "reports_dir": "validation_results",
                "table_name": "insurance_data"
            }
    except Exception as e:
        st.error(f"Error loading configuration: {e}")
        return {}

def load_validation_results():
    """Load all validation results from the validation_results directory."""
    config = load_config()
    reports_dir = Path(config.get("reports_dir", "validation_results"))
    
    results = []
    for file in reports_dir.glob("*.json"):
        if file.name != "summary_report.md":
            try:
                with open(file, 'r') as f:
                    content = f.read()
                    # Skip empty or invalid files
                    if not content.strip():
                        st.warning(f"Empty file: {file}")
                        continue
                    result = json.loads(content)
                    # Verify required fields are present
                    if all(k in result for k in ['model_name', 'model_version', 'timestamp', 'metrics']):
                        result['filename'] = file.name
                        results.append(result)
                    else:
                        st.warning(f"Missing required fields in {file}")
            except json.JSONDecodeError as e:
                st.warning(f"Invalid JSON in {file}: {str(e)}")
            except Exception as e:
                st.error(f"Error loading {file}: {str(e)}")
    
    return sorted(results, key=lambda x: x.get('timestamp', ''), reverse=True)

def load_latest_data():
    """Load the latest healthcare dataset."""
    try:
        df = pd.read_csv("data/insurance.csv")
        return df
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        return None

def plot_data_quality_trends(results):
    """Plot trends in data quality metrics."""
    if not results:
        st.warning("No validation results available")
        return
    
    # Extract metrics over time
    metrics_data = []
    for result in results:
        metrics = result.get('metrics', {})
        timestamp = datetime.fromisoformat(result.get('timestamp', ''))
        metrics_data.append({
            'timestamp': timestamp,
            'r2_score': metrics.get('r2', 0),
            'mse': metrics.get('mse', 0),
            'mae': metrics.get('mae', 0)
        })
    
    df_metrics = pd.DataFrame(metrics_data)
    
    # Plot metrics trends
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_metrics['timestamp'], y=df_metrics['r2_score'],
                            mode='lines+markers', name='R² Score'))
    fig.add_trace(go.Scatter(x=df_metrics['timestamp'], y=df_metrics['mae']/df_metrics['mae'].max(),
                            mode='lines+markers', name='MAE (normalized)'))
    
    fig.update_layout(title='Data Quality Metrics Over Time',
                     xaxis_title='Timestamp',
                     yaxis_title='Metric Value')
    
    st.plotly_chart(fig)

def plot_bias_analysis(results):
    """Plot bias analysis results."""
    if not results:
        return
    
    latest_result = results[0]
    bias_analysis = latest_result.get('healthcare_bias', {})
    protected_attrs = bias_analysis.get('protected_attributes', {})
    
    # Create bias metrics visualization
    bias_data = []
    for attr, metrics in protected_attrs.items():
        for group, values in metrics.get('groups', {}).items():
            bias_data.append({
                'attribute': attr,
                'group': group,
                'mean_prediction': values.get('mean_prediction', 0),
                'prediction_rate': values.get('prediction_rate', 0)
            })
    
    df_bias = pd.DataFrame(bias_data)
    
    # Plot bias metrics
    fig = px.bar(df_bias, x='group', y='mean_prediction', color='attribute',
                 barmode='group', title='Prediction Distribution Across Protected Attributes')
    st.plotly_chart(fig)

def main():
    """Main dashboard application."""
    st.title("Healthcare Data Quality Dashboard")
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select Page", 
                           ["Overview", "Data Explorer", "Quality Metrics", "Bias Analysis"])
    
    # Load data
    results = load_validation_results()
    df = load_latest_data()
    
    if page == "Overview":
        st.header("Data Quality Overview")
        
        # Display latest validation summary
        if results:
            latest = results[0]
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("R² Score", f"{latest.get('metrics', {}).get('r2', 0):.2f}")
            
            with col2:
                st.metric("MAE", f"${latest.get('metrics', {}).get('mae', 0):.2f}")
            
            with col3:
                st.metric("Compliance Status", 
                         latest.get('healthcare_bias', {}).get('compliance_status', 'Unknown'))
        
        # Show recent validation history
        st.subheader("Recent Validation History")
        plot_data_quality_trends(results)
    
    elif page == "Data Explorer":
        st.header("Healthcare Data Explorer")
        
        if df is not None:
            # Data summary
            st.subheader("Dataset Summary")
            st.write(f"Total Records: {len(df)}")
            st.write(df.describe())
            
            # Data visualization
            st.subheader("Data Visualization")
            plot_type = st.selectbox("Select Plot Type", 
                                   ["Cost Distribution", "Age vs Cost", "BMI vs Cost"])
            
            if plot_type == "Cost Distribution":
                fig = px.histogram(df, x='charges', nbins=50,
                                 title='Distribution of Healthcare Costs')
                st.plotly_chart(fig)
            
            elif plot_type == "Age vs Cost":
                fig = px.scatter(df, x='age', y='charges', color='smoker',
                               title='Healthcare Costs by Age')
                st.plotly_chart(fig)
            
            elif plot_type == "BMI vs Cost":
                fig = px.scatter(df, x='bmi', y='charges', color='smoker',
                               title='Healthcare Costs by BMI')
                st.plotly_chart(fig)
    
    elif page == "Quality Metrics":
        st.header("Quality Metrics Analysis")
        
        if results:
            # Metrics over time
            st.subheader("Quality Metrics Trends")
            plot_data_quality_trends(results)
            
            # Detailed metrics table
            st.subheader("Detailed Metrics")
            metrics_data = []
            for result in results:
                metrics = result.get('metrics', {})
                metrics_data.append({
                    'Timestamp': result.get('timestamp', ''),
                    'R² Score': f"{metrics.get('r2', 0):.3f}",
                    'MSE': f"{metrics.get('mse', 0):.2f}",
                    'MAE': f"{metrics.get('mae', 0):.2f}"
                })
            
            st.table(pd.DataFrame(metrics_data))
    
    elif page == "Bias Analysis":
        st.header("Bias Analysis Dashboard")
        
        if results:
            # Plot bias analysis
            st.subheader("Prediction Disparities")
            plot_bias_analysis(results)
            
            # Display detailed bias metrics
            st.subheader("Detailed Bias Metrics")
            latest = results[0]
            bias_analysis = latest.get('healthcare_bias', {})
            
            for attr, metrics in bias_analysis.get('protected_attributes', {}).items():
                st.write(f"\n**{attr.title()} Analysis**")
                st.write("Disparity Metrics:")
                for metric, values in metrics.get('disparity_metrics', {}).items():
                    st.write(f"- {metric}: ratio = {values['ratio']:.2f}, "
                            f"difference = {values['difference']:.2f}")

if __name__ == "__main__":
    main()