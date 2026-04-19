import snowflake.connector
import pandas as pd
from datetime import datetime

# Snowflake connection
def get_snowflake_connection():
    conn = snowflake.connector.connect(
        user='ESHWARDUDALA0',
        password='Telangana@5617',
        account='HZCTIQT-PRC84963',
        warehouse='COMPUTE_WH',
        database='FINANCE_AI',
        schema='CORE'
    )
    return conn

# Analytics queries with Cortex functions
class SnowflakeCortexAnalytics:
    def __init__(self):
        self.conn = get_snowflake_connection()
        self.cursor = self.conn.cursor()
    
    def get_csat_distribution(self):
        """Get CSAT score distribution"""
        query = """
        SELECT 
            CSAT_SCORE,
            COUNT(*) as COUNT,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as PERCENTAGE
        FROM CUSTOMER_SUPPORT
        WHERE CSAT_SCORE IS NOT NULL
        GROUP BY CSAT_SCORE
        ORDER BY CSAT_SCORE DESC
        """
        self.cursor.execute(query)
        return pd.DataFrame(self.cursor.fetchall(), columns=['CSAT_Score', 'Count', 'Percentage'])
    
    def get_channel_performance(self):
        """Get performance by channel"""
        query = """
        SELECT 
            CHANNEL_NAME,
            COUNT(*) as TOTAL_TICKETS,
            ROUND(AVG(CSAT_SCORE), 2) as AVG_CSAT,
            COUNT(DISTINCT AGENT_NAME) as UNIQUE_AGENTS,
            ROUND(AVG(CONNECTED_HANDLING_TIME), 2) as AVG_HANDLING_TIME
        FROM CUSTOMER_SUPPORT
        WHERE CHANNEL_NAME IS NOT NULL
        GROUP BY CHANNEL_NAME
        ORDER BY TOTAL_TICKETS DESC
        """
        self.cursor.execute(query)
        return pd.DataFrame(self.cursor.fetchall(), columns=['Channel', 'Total_Tickets', 'Avg_CSAT', 'Unique_Agents', 'Avg_Handling_Time'])
    
    def get_category_insights(self):
        """Get insights by category"""
        query = """
        SELECT 
            CATEGORY,
            COUNT(*) as TOTAL_ISSUES,
            ROUND(AVG(CSAT_SCORE), 2) as AVG_CSAT,
            MAX(CSAT_SCORE) as MAX_CSAT,
            MIN(CSAT_SCORE) as MIN_CSAT
        FROM CUSTOMER_SUPPORT
        WHERE CATEGORY IS NOT NULL
        GROUP BY CATEGORY
        ORDER BY TOTAL_ISSUES DESC
        """
        self.cursor.execute(query)
        return pd.DataFrame(self.cursor.fetchall(), columns=['Category', 'Total_Issues', 'Avg_CSAT', 'Max_CSAT', 'Min_CSAT'])
    
    def get_agent_performance(self):
        """Get top performing agents"""
        query = """
        SELECT 
            AGENT_NAME,
            COUNT(*) as TICKETS_HANDLED,
            ROUND(AVG(CSAT_SCORE), 2) as AVG_CSAT,
            ROUND(AVG(CONNECTED_HANDLING_TIME), 2) as AVG_HANDLING_TIME,
            MANAGER,
            SUPERVISOR
        FROM CUSTOMER_SUPPORT
        WHERE AGENT_NAME IS NOT NULL
        GROUP BY AGENT_NAME, MANAGER, SUPERVISOR
        ORDER BY AVG_CSAT DESC, TICKETS_HANDLED DESC
        LIMIT 20
        """
        self.cursor.execute(query)
        return pd.DataFrame(self.cursor.fetchall(), columns=['Agent_Name', 'Tickets_Handled', 'Avg_CSAT', 'Avg_Handling_Time', 'Manager', 'Supervisor'])
    

    def get_sentiment_summary(self):
        """Get sentiment summary using Cortex"""
        query = """
        SELECT 
            CASE 
                WHEN SNOWFLAKE.CORTEX.SENTIMENT(CUSTOMER_REMARKS) > 0.5 THEN 'Positive'
                WHEN SNOWFLAKE.CORTEX.SENTIMENT(CUSTOMER_REMARKS) < -0.5 THEN 'Negative'
                ELSE 'Neutral'
            END as SENTIMENT,
            COUNT(*) as COUNT,
            ROUND(AVG(CSAT_SCORE), 2) as AVG_CSAT
        FROM CUSTOMER_SUPPORT
        WHERE CUSTOMER_REMARKS IS NOT NULL AND CUSTOMER_REMARKS != ''
        GROUP BY SENTIMENT
        """
        try:
            self.cursor.execute(query)
            return pd.DataFrame(self.cursor.fetchall(), columns=['Sentiment', 'Count', 'Avg_CSAT'])
        except Exception as e:
            print(f"Sentiment summary error: {e}")
            return None
    

    def analyze_unresponsive_customers(self):
        """Identify customers not responding nicely using Cortex sentiment analysis"""
        query = """
        SELECT 
            UNIQUE_ID,
            CUSTOMER_REMARKS,
            CSAT_SCORE,
            AGENT_NAME,
            CATEGORY,
            SNOWFLAKE.CORTEX.SENTIMENT(CUSTOMER_REMARKS) as SENTIMENT_SCORE,
            SNOWFLAKE.CORTEX.EXTRACT_ANSWER(CUSTOMER_REMARKS, 'What is the main complaint?') as MAIN_ISSUE
        FROM CUSTOMER_SUPPORT
        WHERE CUSTOMER_REMARKS IS NOT NULL 
        AND SNOWFLAKE.CORTEX.SENTIMENT(CUSTOMER_REMARKS) < -0.3
        ORDER BY SNOWFLAKE.CORTEX.SENTIMENT(CUSTOMER_REMARKS) ASC
        LIMIT 50
        """
        try:
            self.cursor.execute(query)
            return pd.DataFrame(self.cursor.fetchall(), columns=['Customer_ID', 'Remarks', 'CSAT', 'Agent', 'Category', 'Sentiment_Score', 'Main_Issue'])
        except Exception as e:
            print(f"Unresponsive customers analysis error: {e}")
            return pd.DataFrame()
    
    def supervisor_performance_ranking(self):
        """Rank supervisors from worst to best based on team CSAT"""
        # Try multiple query strategies to handle different column names
        queries = [
            # Strategy 1: Using SUPERVISOR column with all available fields
            """
            SELECT 
                SUPERVISOR,
                COUNT(*) as TICKETS_MANAGED,
                ROUND(AVG(CSAT_SCORE), 2) as TEAM_AVG_CSAT,
                COUNT(DISTINCT AGENT_NAME) as TEAM_SIZE,
                ROUND(AVG(CONNECTED_HANDLING_TIME), 2) as AVG_RESPONSE_TIME,
                ROUND(COUNT(CASE WHEN CSAT_SCORE >= 4 THEN 1 END) * 100.0 / COUNT(*), 1) as CSAT_4_ABOVE_PERCENT
            FROM CUSTOMER_SUPPORT
            WHERE SUPERVISOR IS NOT NULL
            GROUP BY SUPERVISOR
            ORDER BY TEAM_AVG_CSAT ASC
            """,
            # Strategy 2: Using SUPERVISOR without CONNECTED_HANDLING_TIME
            """
            SELECT 
                SUPERVISOR,
                COUNT(*) as TICKETS_MANAGED,
                ROUND(AVG(CSAT_SCORE), 2) as TEAM_AVG_CSAT,
                COUNT(DISTINCT AGENT_NAME) as TEAM_SIZE,
                0 as AVG_RESPONSE_TIME,
                ROUND(COUNT(CASE WHEN CSAT_SCORE >= 4 THEN 1 END) * 100.0 / COUNT(*), 1) as CSAT_4_ABOVE_PERCENT
            FROM CUSTOMER_SUPPORT
            WHERE SUPERVISOR IS NOT NULL
            GROUP BY SUPERVISOR
            ORDER BY TEAM_AVG_CSAT ASC
            """,
            # Strategy 3: Using MANAGER as fallback for SUPERVISOR
            """
            SELECT 
                MANAGER as SUPERVISOR,
                COUNT(*) as TICKETS_MANAGED,
                ROUND(AVG(CSAT_SCORE), 2) as TEAM_AVG_CSAT,
                COUNT(DISTINCT AGENT_NAME) as TEAM_SIZE,
                0 as AVG_RESPONSE_TIME,
                ROUND(COUNT(CASE WHEN CSAT_SCORE >= 4 THEN 1 END) * 100.0 / COUNT(*), 1) as CSAT_4_ABOVE_PERCENT
            FROM CUSTOMER_SUPPORT
            WHERE MANAGER IS NOT NULL
            GROUP BY MANAGER
            ORDER BY TEAM_AVG_CSAT ASC
            """
        ]
        
        for idx, query in enumerate(queries):
            try:
                self.cursor.execute(query)
                results = self.cursor.fetchall()
                if results:  # If we got results, create and return DataFrame
                    df = pd.DataFrame(results, columns=['Supervisor', 'Tickets_Managed', 'Avg_CSAT', 'Team_Size', 'Avg_Response_Time', 'CSAT_4_Above_Pct'])
                    print(f"Supervisor ranking retrieved successfully (Strategy {idx + 1})")
                    return df
                else:
                    print(f"Strategy {idx + 1}: No supervisor data found")
            except Exception as e:
                print(f"Supervisor ranking error (Strategy {idx + 1}): {e}")
                continue
        
        # If all strategies fail, log and return empty DataFrame with correct columns
        print("⚠️ WARNING: Could not retrieve supervisor data with any strategy. Returning empty DataFrame.")
        return pd.DataFrame(columns=['Supervisor', 'Tickets_Managed', 'Avg_CSAT', 'Team_Size', 'Avg_Response_Time', 'CSAT_4_Above_Pct'])
    
    def detect_communication_gaps(self):
        """Detect communication gaps using Cortex text analysis"""
        query = """
        SELECT 
            UNIQUE_ID,
            CATEGORY,
            CUSTOMER_REMARKS,
            CSAT_SCORE,
            AGENT_NAME,
            SNOWFLAKE.CORTEX.EXTRACT_ANSWER(CUSTOMER_REMARKS, 'Was the customer confused or unclear about something?') as CONFUSION_INDICATOR
        FROM CUSTOMER_SUPPORT
        WHERE CUSTOMER_REMARKS IS NOT NULL 
        AND (CSAT_SCORE <= 2 OR SNOWFLAKE.CORTEX.SENTIMENT(CUSTOMER_REMARKS) < -0.5)
        ORDER BY CSAT_SCORE ASC
        LIMIT 100
        """
        try:
            self.cursor.execute(query)
            return pd.DataFrame(self.cursor.fetchall(), columns=['Customer_ID', 'Category', 'Remarks', 'CSAT', 'Agent', 'Confusion_Indicator'])
        except Exception as e:
            print(f"Communication gaps analysis error: {e}")
            return pd.DataFrame()
    
    def csat_improvement_trends(self):
        """Analyze CSAT improvement suggestions using Cortex"""
        query = """
        SELECT 
            CATEGORY,
            COUNT(CASE WHEN CSAT_SCORE <= 2 THEN 1 END) as LOW_CSAT_COUNT,
            COUNT(CASE WHEN CSAT_SCORE BETWEEN 3 AND 4 THEN 1 END) as MEDIUM_CSAT_COUNT,
            COUNT(CASE WHEN CSAT_SCORE >= 5 THEN 1 END) as HIGH_CSAT_COUNT,
            ROUND(AVG(CSAT_SCORE), 2) as AVG_CSAT,
            COUNT(*) as TOTAL_TICKETS
        FROM CUSTOMER_SUPPORT
        WHERE CUSTOMER_REMARKS IS NOT NULL
        GROUP BY CATEGORY
        ORDER BY AVG_CSAT ASC
        """
        try:
            self.cursor.execute(query)
            return pd.DataFrame(self.cursor.fetchall(), columns=['Category', 'Low_CSAT', 'Medium_CSAT', 'High_CSAT', 'Avg_CSAT', 'Total_Tickets'])
        except Exception as e:
            print(f"CSAT improvement analysis error: {e}")
            return pd.DataFrame()
    
    def ask_cortex(self, question):
        """Ask Cortex a question about customer support data"""
        query = f"""
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            'mistral-large',
            'You are a customer support analytics expert. Answer this question based on the context provided: {question}',
            'Based on customer support data analysis'
        ) as RESPONSE
        """
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            return result[0] if result else "Unable to get response from Cortex"
        except Exception as e:
            print(f"Cortex question error: {e}")
            return f"Error: {str(e)}"
    


    def get_summary_stats(self):
        """Get summary statistics"""
        query = """
        SELECT 
            COUNT(*) as TOTAL_TICKETS,
            COUNT(DISTINCT AGENT_NAME) as TOTAL_AGENTS,
            ROUND(AVG(CSAT_SCORE), 2) as AVG_CSAT,
            MIN(CSAT_SCORE) as MIN_CSAT,
            MAX(CSAT_SCORE) as MAX_CSAT,
            COUNT(DISTINCT CHANNEL_NAME) as TOTAL_CHANNELS
        FROM CUSTOMER_SUPPORT
        """
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        return {
            'total_tickets': result[0],
            'total_agents': result[1],
            'avg_csat': result[2],
            'min_csat': result[3],
            'max_csat': result[4],
            'total_channels': result[5]
        }
    
    def close_connection(self):
        self.cursor.close()
        self.conn.close()


# Function to generate insights
def generate_all_insights():
    """Generate business-critical analytics insights"""
    analytics = SnowflakeCortexAnalytics()
    
    insights = {
        'summary': analytics.get_summary_stats(),
        'csat_distribution': analytics.get_csat_distribution(),
        'channel_performance': analytics.get_channel_performance(),
        'category_insights': analytics.get_category_insights(),
        'agent_performance': analytics.get_agent_performance(),
        'sentiment_summary': analytics.get_sentiment_summary(),
        'unresponsive_customers': analytics.analyze_unresponsive_customers(),
        'communication_gaps': analytics.detect_communication_gaps(),
        'csat_improvements': analytics.csat_improvement_trends()
    }
    
    analytics.close_connection()
    return insights


if __name__ == "__main__":
    print("Generating analytics insights...")
    insights = generate_all_insights()
    
    print("\n=== Summary Statistics ===")
    for key, value in insights['summary'].items():
        print(f"{key}: {value}")
    
    print("\n=== CSAT Distribution ===")
    print(insights['csat_distribution'])
    
    print("\n=== Channel Performance ===")
    print(insights['channel_performance'])
    
    print("\n=== Category Insights ===")
    print(insights['category_insights'])
