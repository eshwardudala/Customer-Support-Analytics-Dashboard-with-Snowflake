# Customer Support Analytics Dashboard

A professional analytics platform for customer support data using Snowflake Cortex AI and Streamlit.

## Overview

This application provides real-time customer support analytics with AI-powered insights, sentiment analysis, and an interactive chatbot. It helps support teams identify performance issues, track metrics, and prioritize improvements.

## Key Features

- **Real-time Analytics** – Core metrics across channels, agents, and categories
- **AI Sentiment Analysis** – Snowflake Cortex-powered customer sentiment detection
- **Performance Tracking** – Agent and channel performance with interactive visualizations
- **Issue Detection** – Identify communication gaps and negative sentiment automatically
- **Intelligent Chatbot** – Ask questions and get AI-powered responses based on your data
- **Priority Analysis** – See which issue categories need attention

## Dashboard Pages

1. **Overview** – Key metrics and data summary
2. **Channel Analytics** – Performance by communication channel
3. **Agent Performance** – Top agents ranked by CSAT
4. **CSAT Analysis** – Customer satisfaction score distribution
5. **Sentiment Analysis** – Customer sentiment trends (AI-powered)
6. **Unresponsive Customers** – Customers with negative sentiment
7. **Communication Gaps** – Potential clarity issues detected
8. **CSAT Improvements** – Priority categories for improvement
9. **AI Chatbot** – Interactive Q&A interface

## Prerequisites

- Python 3.11+
- Snowflake account with Cortex enabled
- Customer support data in CSV format

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Snowflake Connection

Edit `analytics.py` and `LiveData.py` with your Snowflake credentials:

```python
conn = snowflake.connector.connect(
    user='YOUR_USERNAME',
    password='YOUR_PASSWORD',
    account='YOUR_ACCOUNT_ID',
    warehouse='YOUR_WAREHOUSE',
    database='YOUR_DATABASE',
    schema='YOUR_SCHEMA'
)
```

### 3. Load Data

```bash
python LiveData.py
```

### 4. Run Dashboard

```bash
streamlit run dashboard.py
```

Access at `http://localhost:8502`

## Project Structure

```
Snowflake_project/
├── dashboard.py              # Main Streamlit app with 9 pages
├── analytics.py              # Snowflake queries & Cortex integration
├── chatbot.py                # AI chatbot module
├── LiveData.py               # CSV to Snowflake data loader
├── Customer_support_data.csv # Sample customer data
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit 1.56+ |
| Database | Snowflake |
| AI/ML | Snowflake Cortex |
| Visualization | Plotly 6.7+ |
| Data Processing | Pandas 3.0+, NumPy 2.4+ |
| Language | Python 3.13+ |

## Cortex AI Functions

The application uses three Snowflake Cortex functions:

- **SENTIMENT()** – Returns numeric sentiment score for text
- **EXTRACT_ANSWER()** – Extracts specific information from remarks
- **COMPLETE()** – Generates AI responses using mistral-large model

## Configuration

### Database Requirements

Your `CUSTOMER_SUPPORT` table should have these columns:

```
UNIQUE_ID, CUSTOMER_ID, CUSTOMER_REMARKS
CSAT_SCORE, AGENT_NAME, MANAGER, SUPERVISOR
CATEGORY, CHANNEL_NAME, AGENT_SHIFT, TENURE_BUCKET
CONNECTED_HANDLING_TIME (optional)
```

### Cortex Activation

Contact Snowflake support if Cortex is not available. Some pages require Cortex for sentiment analysis.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No data in dashboard | Run `python LiveData.py` to load CSV |
| Cortex errors | Verify Cortex is enabled in your account |
| Connection errors | Check Snowflake credentials and network access |
| Slow performance | Increase warehouse size or optimize query limits |

## Resources

- [Snowflake Documentation](https://docs.snowflake.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Snowflake Cortex Guide](https://docs.snowflake.com/en/user-guide/ml-overview)

---

**Last Updated:** April 19, 2026
