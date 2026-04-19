import snowflake.connector
import pandas as pd

# Snowflake connection
def get_snowflake_connection():
   conn = snowflake.connector.connect(
    user= USER,
    password=PASSWORD,
    account= ACCOUNT,
    warehouse='COMPUTE_WH',
    database='FINANCE_AI',
    schema='CORE'
)
    return conn


class CustomerSupportChatbot:
    """AI-powered chatbot for customer support analytics using Snowflake Cortex"""
    
    def __init__(self):
        self.conn = get_snowflake_connection()
        self.cursor = self.conn.cursor()
        self.conversation_history = []
    
    def get_context(self):
        """Fetch current analytics context for the chatbot"""
        query = """
        SELECT 
            COUNT(*) as total_tickets,
            COUNT(DISTINCT AGENT_NAME) as total_agents,
            ROUND(AVG(CSAT_SCORE), 2) as avg_csat,
            COUNT(DISTINCT SUPERVISOR) as total_supervisors,
            COUNT(DISTINCT CHANNEL_NAME) as total_channels
        FROM CUSTOMER_SUPPORT
        """
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        return {
            'total_tickets': result[0],
            'total_agents': result[1],
            'avg_csat': result[2],
            'total_supervisors': result[3],
            'total_channels': result[4]
        }
    
    def get_low_performers(self, metric='csat'):
        """Get low performing agents/supervisors"""
        if metric == 'csat':
            query = """
            SELECT 
                AGENT_NAME,
                ROUND(AVG(CSAT_SCORE), 2) as avg_csat,
                COUNT(*) as tickets
            FROM CUSTOMER_SUPPORT
            WHERE AGENT_NAME IS NOT NULL
            GROUP BY AGENT_NAME
            ORDER BY avg_csat ASC
            LIMIT 5
            """
        elif metric == 'supervisor':
            query = """
            SELECT 
                SUPERVISOR,
                ROUND(AVG(CSAT_SCORE), 2) as avg_csat,
                COUNT(*) as tickets
            FROM CUSTOMER_SUPPORT
            WHERE SUPERVISOR IS NOT NULL
            GROUP BY SUPERVISOR
            ORDER BY avg_csat ASC
            LIMIT 5
            """
        
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        return results
    
    def get_problem_categories(self):
        """Get top problem categories"""
        query = """
        SELECT 
            CATEGORY,
            COUNT(*) as frequency,
            ROUND(AVG(CSAT_SCORE), 2) as avg_csat
        FROM CUSTOMER_SUPPORT
        WHERE CATEGORY IS NOT NULL
        GROUP BY CATEGORY
        ORDER BY frequency DESC
        LIMIT 10
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def ask_question(self, user_question):
        """Use Cortex AI_COMPLETE to answer user questions about customer support"""
        # Add to conversation history
        self.conversation_history.append({
            'role': 'user',
            'content': user_question
        })
        
        # Get analytics context
        context = self.get_context()
        low_agents = self.get_low_performers('csat')
        low_supervisors = self.get_low_performers('supervisor')
        categories = self.get_problem_categories()
        
        # Build context string
        context_str = f"""
        Customer Support Analytics Context:
        - Total Tickets: {context['total_tickets']}
        - Total Agents: {context['total_agents']}
        - Average CSAT: {context['avg_csat']}
        - Total Supervisors: {context['total_supervisors']}
        - Total Channels: {context['total_channels']}
        
        Top Problem Categories: {str(categories[:3])}
        Low Performing Agents: {str(low_agents[:3])}
        Low Performing Supervisors: {str(low_supervisors[:3])}
        """
        
        # Use Cortex to answer the question
        try:
            prompt = f"""
            You are an expert customer support analytics consultant. 
            Based on the following context data from a customer support system, 
            provide a helpful and insightful answer to the user's question.
            
            Context:
            {context_str}
            
            User Question: {user_question}
            
            Provide a comprehensive, actionable answer focused on improving customer satisfaction and team performance.
            """
            
            query = f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'mistral-large',
                '{prompt.replace("'", "''")}'
            ) as response
            """
            
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            response = result[0] if result else "Unable to generate response"
            
            # Add to conversation history
            self.conversation_history.append({
                'role': 'assistant',
                'content': response
            })
            
            return response
        
        except Exception as e:
            error_msg = f"Error processing question: {str(e)}"
            self.conversation_history.append({
                'role': 'assistant',
                'content': error_msg
            })
            return error_msg
    
    def get_recommendations(self):
        """Get AI-powered recommendations for improvement"""
        try:
            # Fetch data about key issues
            query = """
            SELECT 
                CATEGORY,
                COUNT(*) as ticket_count,
                ROUND(AVG(CSAT_SCORE), 2) as avg_csat,
                MIN(CSAT_SCORE) as lowest_csat
            FROM CUSTOMER_SUPPORT
            WHERE CSAT_SCORE < 4
            GROUP BY CATEGORY
            ORDER BY ticket_count DESC
            LIMIT 5
            """
            
            self.cursor.execute(query)
            low_satisfaction_data = self.cursor.fetchall()
            
            prompt = f"""
            Based on the following low satisfaction ticket data:
            {str(low_satisfaction_data)}
            
            Provide 5 specific, actionable recommendations to improve customer satisfaction and team performance.
            Format the recommendations as a numbered list with brief explanations for each.
            """
            
            query = f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'mistral-large',
                '{prompt.replace("'", "''")}'
            ) as recommendations
            """
            
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            return result[0] if result else "Unable to generate recommendations"
        
        except Exception as e:
            return f"Error generating recommendations: {str(e)}"
    
    def close(self):
        """Close database connection"""
        self.cursor.close()
        self.conn.close()


if __name__ == "__main__":
    # Test the chatbot
    chatbot = CustomerSupportChatbot()
    
    # Test questions
    test_questions = [
        "Which supervisors are struggling with team performance?",
        "What are the main reasons for low CSAT scores?",
        "How can we improve customer satisfaction?"
    ]
    
    for question in test_questions:
        print(f"\nUser: {question}")
        response = chatbot.ask_question(question)
        print(f"Bot: {response}")
    
    # Get recommendations
    print("\n=== AI Recommendations ===")
    recommendations = chatbot.get_recommendations()
    print(recommendations)
    
    chatbot.close()
