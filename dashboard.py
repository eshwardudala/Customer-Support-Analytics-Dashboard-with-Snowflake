import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from analytics import generate_all_insights, SnowflakeCortexAnalytics
from chatbot import CustomerSupportChatbot
import time

# Page configuration
st.set_page_config(
    page_title="Customer Support Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .header-text {
        color: #1f77b4;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Dashboard Navigation")
page = st.sidebar.radio(
    "Select View:",
    ["📈 Overview", "📞 Channel Analytics", "👥 Agent Performance", "😊 CSAT Analysis", 
     "💬 Sentiment Analysis",  "🤖 AI Chatbot"]
)

# Load data once
@st.cache_data
def load_insights():
    """Load insights from Snowflake"""
    return generate_all_insights()

try:
    with st.spinner("Loading analytics from Snowflake..."):
        insights = load_insights()
    
    # PAGE 1: OVERVIEW
    if page == "📈 Overview":
        st.markdown('<p class="header-text">📊 Customer Support Analytics Overview</p>', unsafe_allow_html=True)
        
        # Summary metrics
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.metric(
                label="Total Tickets",
                value=insights['summary']['total_tickets'],
                delta="lifetime"
            )
        
        with col2:
            st.metric(
                label="Total Agents",
                value=insights['summary']['total_agents']
            )
        
        with col3:
            st.metric(
                label="Avg CSAT Score",
                value=f"{insights['summary']['avg_csat']:.2f}/5.0",
                delta="Quality Metric"
            )
        
        with col4:
            st.metric(
                label="Min CSAT",
                value=insights['summary']['min_csat']
            )
        
        with col5:
            st.metric(
                label="Max CSAT",
                value=insights['summary']['max_csat']
            )
        
        with col6:
            st.metric(
                label="Total Channels",
                value=insights['summary']['total_channels']
            )
        
        st.divider()
        
        # CSAT Distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("CSAT Score Distribution")
            csat_data = insights['csat_distribution']
            if not csat_data.empty:
                fig_csat = px.bar(
                    csat_data,
                    x='CSAT_Score',
                    y='Count',
                    color='Percentage',
                    hover_data={'Percentage': ':.2f%'},
                    color_continuous_scale='RdBu',
                    title="Distribution of Customer Satisfaction Scores"
                )
                fig_csat.update_layout(height=400, showlegend=True)
                st.plotly_chart(fig_csat, use_container_width=True)
        
        with col2:
            st.subheader("Tickets by Channel")
            channel_data = insights['channel_performance']
            if not channel_data.empty:
                fig_channel = px.pie(
                    channel_data,
                    values='Total_Tickets',
                    names='Channel',
                    title="Ticket Distribution by Channel",
                    hole=0.3
                )
                fig_channel.update_layout(height=400)
                st.plotly_chart(fig_channel, use_container_width=True)
        
        # Channel Performance Table
        st.subheader("Channel Performance Metrics")
        if not insights['channel_performance'].empty:
            st.dataframe(insights['channel_performance'], use_container_width=True)
        
        # Category Insights
        st.subheader("Category Performance")
        if not insights['category_insights'].empty:
            fig_cat = px.bar(
                insights['category_insights'],
                x='Category',
                y='Avg_CSAT',
                color='Total_Issues',
                hover_data={'Avg_CSAT': ':.2f', 'Total_Issues': ':',},
                title="Average CSAT by Category (Size = Issue Count)",
                color_continuous_scale='Viridis'
            )
            fig_cat.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig_cat, use_container_width=True)
    
    # PAGE 2: CHANNEL ANALYTICS
    elif page == "📞 Channel Analytics":
        st.markdown('<p class="header-text">📞 Channel Performance Analytics</p>', unsafe_allow_html=True)
        
        channel_data = insights['channel_performance']
        
        if not channel_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("CSAT Score by Channel")
                fig1 = px.bar(
                    channel_data,
                    x='Channel',
                    y='Avg_CSAT',
                    color='Avg_CSAT',
                    color_continuous_scale='RdBu',
                    hover_data={'Avg_CSAT': ':.2f'},
                    title="Average CSAT by Channel"
                )
                fig1.update_layout(height=400)
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                st.subheader("Handling Time by Channel")
                fig2 = px.bar(
                    channel_data,
                    x='Channel',
                    y='Avg_Handling_Time',
                    color='Total_Tickets',
                    hover_data={'Avg_Handling_Time': ':.2f'},
                    color_continuous_scale='Blues',
                    title="Average Handling Time by Channel"
                )
                fig2.update_layout(height=400)
                st.plotly_chart(fig2, use_container_width=True)
            
            st.subheader("Detailed Channel Metrics")
            display_channel_data = channel_data.fillna('-')
            st.dataframe(display_channel_data, use_container_width=True)
    
    # PAGE 3: AGENT PERFORMANCE
    elif page == "👥 Agent Performance":
        st.markdown('<p class="header-text">👥 Top Performing Agents</p>', unsafe_allow_html=True)
        
        agent_data = insights['agent_performance']
        
        if not agent_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Agent CSAT Scores (Top 15)")
                top_agents = agent_data.head(15).sort_values('Avg_CSAT')
                fig_agents = px.bar(
                    top_agents,
                    y='Agent_Name',
                    x='Avg_CSAT',
                    color='Avg_CSAT',
                    color_continuous_scale='RdBu',
                    hover_data={'Avg_CSAT': ':.2f'},
                    title="Top Agents by CSAT",
                    orientation='h'
                )
                fig_agents.update_layout(height=500)
                st.plotly_chart(fig_agents, use_container_width=True)
            
            with col2:
                st.subheader("Tickets Handled by Agent (Top 15)")
                top_by_tickets = agent_data.head(15).sort_values('Tickets_Handled')
                fig_tickets = px.bar(
                    top_by_tickets,
                    y='Agent_Name',
                    x='Tickets_Handled',
                    color='Avg_CSAT',
                    color_continuous_scale='Viridis',
                    hover_data={'Tickets_Handled': ':'},
                    title="Tickets Handled by Agent",
                    orientation='h'
                )
                fig_tickets.update_layout(height=500)
                st.plotly_chart(fig_tickets, use_container_width=True)
            
            st.subheader("Detailed Agent Performance")
            # Fill NaN values and format properly
            display_agent_data = agent_data.fillna('-')
            st.dataframe(display_agent_data, use_container_width=True)
    
    # PAGE 4: CSAT ANALYSIS
    elif page == "😊 CSAT Analysis":
        st.markdown('<p class="header-text">😊 CSAT Score Analysis</p>', unsafe_allow_html=True)
        
        csat_data = insights['csat_distribution']
        
        if not csat_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig_csat_dist = px.bar(
                    csat_data,
                    x='CSAT_Score',
                    y='Count',
                    color='CSAT_Score',
                    color_continuous_scale='RdBu',
                    hover_data={'Count': ':', 'Percentage': ':.2f%'},
                    title="CSAT Score Distribution"
                )
                fig_csat_dist.update_layout(height=400)
                st.plotly_chart(fig_csat_dist, use_container_width=True)
            
            with col2:
                fig_csat_pie = px.pie(
                    csat_data,
                    values='Count',
                    names='CSAT_Score',
                    title="CSAT Score Composition",
                    color_discrete_sequence=px.colors.sequential.Greens
                )
                fig_csat_pie.update_layout(height=400)
                st.plotly_chart(fig_csat_pie, use_container_width=True)
            
            # Statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Responses", csat_data['Count'].sum())
            with col2:
                satisfied_count = csat_data[csat_data['CSAT_Score'] >= 4]['Count'].sum()
                st.metric("Satisfied (4-5)", f"{satisfied_count:,}")
            with col3:
                neutral_count = csat_data[csat_data['CSAT_Score'] == 3]['Count'].sum()
                st.metric("Neutral (3)", f"{neutral_count:,}")
            with col4:
                dissatisfied_count = csat_data[csat_data['CSAT_Score'] < 3]['Count'].sum()
                st.metric("Dissatisfied (<3)", f"{dissatisfied_count:,}")
            
            st.subheader("Detailed CSAT Data")
            display_csat_data = csat_data.fillna('-')
            st.dataframe(display_csat_data, use_container_width=True)
    
    # PAGE 5: SENTIMENT ANALYSIS
    elif page == "💬 Sentiment Analysis":
        st.markdown('<p class="header-text">💬 Sentiment Analysis Using Cortex</p>', unsafe_allow_html=True)
        
        sentiment_data = insights['sentiment_summary']
        
        if sentiment_data is not None and not sentiment_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Sentiment Distribution")
                fig_sentiment = px.pie(
                    sentiment_data,
                    values='Count',
                    names='Sentiment',
                    title="Customer Remarks Sentiment Distribution",
                    color_discrete_map={'Positive': '#2ecc71', 'Neutral': '#95a5a6', 'Negative': '#e74c3c'}
                )
                fig_sentiment.update_layout(height=400)
                st.plotly_chart(fig_sentiment, use_container_width=True)
            
            with col2:
                st.subheader("Sentiment vs CSAT")
                fig_sentiment_csat = px.bar(
                    sentiment_data,
                    x='Sentiment',
                    y='Avg_CSAT',
                    color='Count',
                    color_continuous_scale='RdBu',
                    hover_data={'Avg_CSAT': ':.2f', 'Count': ':'},
                    title="Average CSAT by Sentiment"
                )
                fig_sentiment_csat.update_layout(height=400)
                st.plotly_chart(fig_sentiment_csat, use_container_width=True)
            
            st.subheader("Sentiment Summary")
            st.dataframe(sentiment_data, use_container_width=True)
        else:
            st.warning("Sentiment analysis data not available. Please ensure Cortex is enabled in your Snowflake account.")
    
    # PAGE 6: UNRESPONSIVE CUSTOMERS
    elif page == "⚠️ Unresponsive Customers":
        st.markdown('<p class="header-text">⚠️ Customers Not Responding Nicely</p>', unsafe_allow_html=True)
        
        unresponsive = insights.get('unresponsive_customers')
        
        if unresponsive is not None and not unresponsive.empty:
            st.warning(f"⚠️ Found {len(unresponsive)} customers with negative sentiment remarks")
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                avg_sentiment = unresponsive['Sentiment_Score'].mean()
                st.metric("Avg Sentiment Score", f"{avg_sentiment:.2f}")
            with col2:
                avg_csat = unresponsive['CSAT'].mean()
                st.metric("Avg CSAT", f"{avg_csat:.2f}")
            with col3:
                negative_count = len(unresponsive[unresponsive['Sentiment_Score'] < -0.5])
                st.metric("Highly Negative", negative_count)
            with col4:
                st.metric("Total Records", len(unresponsive))
            
            st.divider()
            
            # Sentiment distribution
            col1, col2 = st.columns(2)
            with col1:
                fig_neg = px.histogram(
                    unresponsive,
                    x='Sentiment_Score',
                    nbins=20,
                    color='CSAT',
                    color_continuous_scale='Reds',
                    title="Sentiment Score Distribution"
                )
                st.plotly_chart(fig_neg, use_container_width=True)
            
            with col2:
                fig_cat = px.bar(
                    unresponsive.groupby('Category').size().reset_index(name='Count'),
                    x='Category',
                    y='Count',
                    color='Count',
                    color_continuous_scale='Reds',
                    title="Issues Category Distribution"
                )
                st.plotly_chart(fig_cat, use_container_width=True)
            
            st.subheader("Detailed Unresponsive Customer Records")
            display_unresponsive = unresponsive[['Customer_ID', 'Remarks', 'CSAT', 'Agent', 'Category', 'Sentiment_Score']].fillna('-')
            st.dataframe(display_unresponsive, use_container_width=True)
        else:
            st.info("No unresponsive customers found or data not available")
    
    # PAGE 7: COMMUNICATION GAPS
    elif page == "🔗 Communication Gaps":
        st.markdown('<p class="header-text">🔗 Analysis of Communication Gaps</p>', unsafe_allow_html=True)
        
        comm_gaps = insights.get('communication_gaps')
        
        if comm_gaps is not None and not comm_gaps.empty:
            st.warning(f"📢 Detected {len(comm_gaps)} cases with potential communication issues (Low CSAT ≤ 2 or Negative Sentiment)")
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Records Analyzed", len(comm_gaps))
            with col2:
                very_low = len(comm_gaps[comm_gaps['CSAT'] <= 1])
                st.metric("CSAT ≤ 1", very_low)
            with col3:
                unclear = len(comm_gaps[comm_gaps['Confusion_Indicator'].notna()])
                st.metric("Confusion Detected", unclear)
            with col4:
                avg_csat_gap = comm_gaps['CSAT'].mean()
                st.metric("Avg CSAT (Gap Cases)", f"{avg_csat_gap:.2f}")
            
            st.divider()
            
            # Visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                category_gaps = comm_gaps.groupby('Category').size().reset_index(name='Count')
                fig_cat = px.bar(
                    category_gaps.sort_values('Count'),
                    x='Count',
                    y='Category',
                    color='Count',
                    color_continuous_scale='Reds',
                    title="Communication Gaps by Category",
                    orientation='h'
                )
                st.plotly_chart(fig_cat, use_container_width=True)
            
            with col2:
                fig_csat_dist = px.histogram(
                    comm_gaps,
                    x='CSAT',
                    nbins=5,
                    color='Category',
                    title="CSAT Distribution in Gap Cases",
                    barmode='group'
                )
                st.plotly_chart(fig_csat_dist, use_container_width=True)
            
            st.subheader("Detailed Communication Gap Records")
            display_gaps = comm_gaps[['Customer_ID', 'Category', 'Remarks', 'CSAT', 'Agent', 'Confusion_Indicator']].fillna('-')
            st.dataframe(display_gaps, use_container_width=True)
        else:
            st.info("No communication gaps detected or data not available")
    
    # PAGE 8: CSAT IMPROVEMENTS
    elif page == "📈 CSAT Improvements":
        st.markdown('<p class="header-text">📈 CSAT Improvement Opportunities</p>', unsafe_allow_html=True)
        
        improvements = insights.get('csat_improvements')
        
        if improvements is not None and not improvements.empty:
            st.info("📊 Analysis of CSAT improvement opportunities by category")
            
            # Add improvement recommendations
            improvements['Improvement_Score'] = (
                improvements['Low_CSAT'] * 1.0 + 
                improvements['Medium_CSAT'] * 0.5
            ) / improvements['Total_Tickets']
            improvements = improvements.sort_values('Improvement_Score', ascending=False)
            
            # KPI summary
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_low = improvements['Low_CSAT'].sum()
                st.metric("Total Low CSAT Cases", int(total_low))
            with col2:
                avg_overall = improvements['Avg_CSAT'].mean()
                st.metric("Overall Avg CSAT", f"{avg_overall:.2f}")
            with col3:
                most_improved_cat = improvements.iloc[0]['Category']
                st.metric("Highest Priority Category", most_improved_cat)
            with col4:
                total_opportunity = improvements['Medium_CSAT'].sum() + improvements['Low_CSAT'].sum()
                st.metric("Improvement Opportunities", int(total_opportunity))
            
            st.divider()
            
            # Visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                fig_imp = px.bar(
                    improvements.sort_values('Avg_CSAT'),
                    x='Avg_CSAT',
                    y='Category',
                    color='Avg_CSAT',
                    color_continuous_scale='RdBu',
                    hover_data={'Low_CSAT': ':', 'Total_Tickets': ':'},
                    title="Average CSAT by Category (Priority Areas)",
                    orientation='h'
                )
                st.plotly_chart(fig_imp, use_container_width=True)
            
            with col2:
                # Stacked bar chart
                improvement_melted = improvements[['Category', 'Low_CSAT', 'Medium_CSAT', 'High_CSAT']].head(10)
                fig_stack = px.bar(
                    improvement_melted,
                    x='Category',
                    y=['Low_CSAT', 'Medium_CSAT', 'High_CSAT'],
                    barmode='stack',
                    color_discrete_map={'Low_CSAT': '#e74c3c', 'Medium_CSAT': '#f39c12', 'High_CSAT': '#2ecc71'},
                    title="CSAT Distribution by Category",
                    labels={'value': 'Count', 'variable': 'CSAT Level'}
                )
                st.plotly_chart(fig_stack, use_container_width=True)
            
            st.subheader("Category Improvement Details")
            display_imp = improvements[['Category', 'Low_CSAT', 'Medium_CSAT', 'High_CSAT', 'Avg_CSAT', 'Total_Tickets']].fillna('-')
            st.dataframe(display_imp, use_container_width=True)
        else:
            st.info("CSAT improvement data not available")
    
    # PAGE 9: AI CHATBOT
    elif page == "🤖 AI Chatbot":
        st.markdown('<p class="header-text">🤖 AI-Powered Customer Support Analytics Chatbot</p>', unsafe_allow_html=True)
        
        st.write("Ask the AI chatbot any questions about your customer support analytics. It uses Snowflake Cortex AI to provide insights.")
        
        # Initialize chatbot session
        if 'chatbot' not in st.session_state:
            st.session_state.chatbot = CustomerSupportChatbot()
        
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # Display chat history
        st.subheader("Chat History")
        chat_container = st.container(height=400)
        
        with chat_container:
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    st.markdown(f"**You:** {message['content']}")
                else:
                    st.markdown(f"**Bot:** {message['content']}")
        
        st.divider()
        
        # Input area
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_input(
                "Ask a question about customer support analytics:",
                placeholder="e.g., Which supervisors are struggling? What are the main reasons for low CSAT?"
            )
        
        with col2:
            send_button = st.button("Send", use_container_width=True)
        
        # Process user input
        if send_button and user_input:
            with st.spinner("🤔 Thinking..."):
                response = st.session_state.chatbot.ask_question(user_input)
                st.session_state.chat_history.append({'role': 'user', 'content': user_input})
                st.session_state.chat_history.append({'role': 'assistant', 'content': response})
            
            # Rerun to update chat display
            st.rerun()
        
        st.divider()
        
        # Quick question buttons
        st.subheader("💡 Suggested Analysis Questions")
        
        quick_questions = [
            "Identify which agents are demonstrating improvement trends and should be promoted as mentors to struggling team members. What are their key success factors?",
            "Analyze the communication patterns and characteristics that consistently lead to high customer satisfaction. What can other agents learn from these interactions?",
            "Which customers show signs of dissatisfaction or are at risk of not returning based on their sentiment analysis and CSAT scores?",
            "Compare performance metrics across different communication channels - which channels have the best first-contact resolution rates and CSAT scores?",
            "What are the most critical training topics and skill gaps that would have the highest impact on overall CSAT improvement?",
            "Identify specific shifts, time periods, and days when team performance drops - what are the contributing factors?",
            "Which product/issue categories represent the biggest quality challenges and revenue risk? What are the repeat complaint patterns?",
            "What are the root causes and common complaints driving negative customer sentiment in our highest-volume categories?",
            "Based on interaction patterns and customer remarks, who are the customers most at risk of churn and what would help retain them?",
            "What specific best practices, handling techniques, and communication styles are top performers using that could be standardized across the team?"
        ]
        
        # Organize questions in rows of 2
       
        
        col1, col2 = st.columns(2)
        
        if col1.button("⚠️ At-Risk Customers", use_container_width=True):
            with st.spinner("🤔 Analyzing..."):
                response = st.session_state.chatbot.ask_question(quick_questions[2])
                st.session_state.chat_history.append({'role': 'user', 'content': quick_questions[2]})
                st.session_state.chat_history.append({'role': 'assistant', 'content': response})
            st.rerun()
        
        if col2.button("📱 Channel Performance Comparison", use_container_width=True):
            with st.spinner("🤔 Analyzing..."):
                response = st.session_state.chatbot.ask_question(quick_questions[3])
                st.session_state.chat_history.append({'role': 'user', 'content': quick_questions[3]})
                st.session_state.chat_history.append({'role': 'assistant', 'content': response})
            st.rerun()
        
        col1, col2 = st.columns(2)
        
        if col1.button("🎓 Training & Skill Gaps", use_container_width=True):
            with st.spinner("🤔 Analyzing..."):
                response = st.session_state.chatbot.ask_question(quick_questions[4])
                st.session_state.chat_history.append({'role': 'user', 'content': quick_questions[4]})
                st.session_state.chat_history.append({'role': 'assistant', 'content': response})
            st.rerun()
        
        if col2.button("⏰ Shift & Time Analysis", use_container_width=True):
            with st.spinner("🤔 Analyzing..."):
                response = st.session_state.chatbot.ask_question(quick_questions[5])
                st.session_state.chat_history.append({'role': 'user', 'content': quick_questions[5]})
                st.session_state.chat_history.append({'role': 'assistant', 'content': response})
            st.rerun()
        
        col1, col2 = st.columns(2)
        
        if col1.button("📊 Category Quality Issues", use_container_width=True):
            with st.spinner("🤔 Analyzing..."):
                response = st.session_state.chatbot.ask_question(quick_questions[6])
                st.session_state.chat_history.append({'role': 'user', 'content': quick_questions[6]})
                st.session_state.chat_history.append({'role': 'assistant', 'content': response})
            st.rerun()
        
        if col2.button("😠 Negative Sentiment Root Cause", use_container_width=True):
            with st.spinner("🤔 Analyzing..."):
                response = st.session_state.chatbot.ask_question(quick_questions[7])
                st.session_state.chat_history.append({'role': 'user', 'content': quick_questions[7]})
                st.session_state.chat_history.append({'role': 'assistant', 'content': response})
            st.rerun()
        
        col1, col2 = st.columns(2)
        
        if col1.button("🔄 Customer Churn Risk", use_container_width=True):
            with st.spinner("🤔 Analyzing..."):
                response = st.session_state.chatbot.ask_question(quick_questions[8])
                st.session_state.chat_history.append({'role': 'user', 'content': quick_questions[8]})
                st.session_state.chat_history.append({'role': 'assistant', 'content': response})
            st.rerun()
        
        if col2.button("⭐ Best Practices Share", use_container_width=True):
            with st.spinner("🤔 Analyzing..."):
                response = st.session_state.chatbot.ask_question(quick_questions[9])
                st.session_state.chat_history.append({'role': 'user', 'content': quick_questions[9]})
                st.session_state.chat_history.append({'role': 'assistant', 'content': response})
            st.rerun()
        
        st.divider()
        
        # Get AI recommendations
        if st.button("📊 Generate Strategic Recommendations", use_container_width=True):
            with st.spinner("🤔 Generating recommendations..."):
                recommendations = st.session_state.chatbot.get_recommendations()
                st.session_state.chat_history.append({
                    'role': 'user',
                    'content': 'Generate strategic improvement recommendations for the entire organization'
                })
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': recommendations
                })
            st.rerun()
    
    # Footer
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption("📊 Data Source: Snowflake Customer Support Database")
    with col2:
        st.caption("🤖 Powered by Snowflake Cortex AI")
    with col3:
        st.caption(f"⏰ Last Updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")

except Exception as e:
    st.error(f"❌ Error loading data: {str(e)}")
    st.info("Please ensure:")
    st.write("1. Snowflake connection is configured correctly")
    st.write("2. Customer support data is loaded in the CUSTOMER_SUPPORT table")
    st.write("3. Your Snowflake account has Cortex enabled (for sentiment analysis)")
