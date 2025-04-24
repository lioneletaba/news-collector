import asyncio
from datetime import datetime, timedelta
import streamlit as st
from loguru import logger

from src.services.news_service import NewsService
from src.utils.config import get_settings
from src.utils.exceptions import NewsAutomationError
from src.models.database import create_db_and_tables

settings = get_settings()

def init_session_state():
    """Initialize session state variables."""
    if 'articles' not in st.session_state:
        st.session_state.articles = []
    if 'selected_articles' not in st.session_state:
        st.session_state.selected_articles = []

def render_article_card(article, index):
    """Render an article card with selection checkbox."""
    with st.container():
        col1, col2 = st.columns([1, 6])
        
        with col1:
            # Selection checkbox
            is_selected = st.checkbox(
                "Select",
                key=f"select_{index}",
                value=article in st.session_state.selected_articles
            )
            if is_selected and article not in st.session_state.selected_articles:
                st.session_state.selected_articles.append(article)
            elif not is_selected and article in st.session_state.selected_articles:
                st.session_state.selected_articles.remove(article)
        
        with col2:
            # Article content
            st.markdown(f"### [{article.title}]({article.url})")
            st.markdown(f"**Source:** {article.source}")
            st.markdown(f"**Published:** {article.publication_date.strftime('%Y-%m-%d %H:%M:%S')}")
            st.markdown(f"**Topic:** {article.topic}")
            with st.expander("Content"):
                st.write(article.content[:500] + "..." if len(article.content) > 500 else article.content)
        
        st.divider()

def init_session_state():
    if "articles" not in st.session_state:
        st.session_state.articles = []
    if "selected_articles" not in st.session_state:
        st.session_state.selected_articles = []

def main():
    """Main Streamlit application."""

    print("Creating database and tables...")
    create_db_and_tables()
    print("Database and tables created.")



    st.set_page_config(
        page_title="News Automation",
        page_icon="📰",
        layout="wide"
    )
    
    # Initialize session state
    init_session_state()
    
    # Initialize service
    service = NewsService()
    
    # Sidebar
    with st.sidebar:
        st.title("News Automation")
        
        # Source input
        source = st.text_input(
            "News Source",
            placeholder="e.g., bbc.com",
            help="Enter the domain name without 'https://' or trailing slash"
        )
        
        # Topic input
        topic = st.text_input(
            "Topic",
            value=settings.default_topic,
            help="Enter the topic to filter articles by"
        )
        
        # Date range
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now().date() - timedelta(days=1),
                help="Start date for article search"
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime.now().date(),
                help="End date for article search"
            )
        
        # Fetch button
        if st.button("Fetch Articles", type="primary"):
            if not source:
                st.error("Please enter a news source")
                return
            
            try:
                with st.spinner("Fetching and filtering articles..."):
                    # Convert dates to datetime
                    start_dt = datetime.combine(start_date, datetime.min.time())
                    end_dt = datetime.combine(end_date, datetime.max.time())
                    
                    # Collect and filter articles
                    st.session_state.articles = asyncio.run(
                        service.collect_and_filter_articles(
                            source=source,
                            topic=topic,
                            start_date=start_dt,
                            end_date=end_dt
                        )
                    )
                    
                    if st.session_state.articles:
                        st.success(f"Found {len(st.session_state.articles)} relevant articles!")
                    else:
                        st.info("No relevant articles found")
                    
            except NewsAutomationError as e:
                st.error(f"Error: {str(e)}")
                logger.error(f"Failed to fetch articles: {e}")
    
    # Main content
    if st.session_state.articles:
        st.title(f"Articles about {topic}")
        
        # Article list
        for i, article in enumerate(st.session_state.articles):
            render_article_card(article, i)
        
        # PDF generation
        if st.session_state.selected_articles:
            if st.button("Generate PDF Report"):
                try:
                    with st.spinner("Generating PDF report..."):
                        pdf_path = service.generate_pdf_report(
                            st.session_state.selected_articles,
                            topic
                        )
                        
                        # Provide download link
                        with open(pdf_path, "rb") as f:
                            st.download_button(
                                "Download PDF Report",
                                f,
                                file_name=pdf_path.name,
                                mime="application/pdf"
                            )
                        
                except NewsAutomationError as e:
                    st.error(f"Error generating PDF: {str(e)}")
                    logger.error(f"Failed to generate PDF: {e}")

if __name__ == "__main__":
    main()
