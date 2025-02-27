from config import Session
from sqlalchemy import text

import numpy as np

def get_aggregated_user_engagement():
    # Create a session
    session = Session()

    try:
        # Execute the SQL query to get aggregated user engagement data
        result = session.execute(
            text("""
                SELECT 
                    DATE(timestamp) AS engagement_date, 
                    research_id,
                    COUNT(DISTINCT user_id) AS total_unique_views,  
                    SUM(view) AS total_views,                       
                    SUM(download) AS total_downloads                
                FROM user_engagement
                GROUP BY DATE(timestamp), research_id
                ORDER BY engagement_date, research_id;
            """)
        )

        # Process the result, assuming it returns a list of tuples or dictionaries
        engagement_data = [row for row in result]
        return engagement_data
    finally:
        session.close()


def get_engagement_summary(start_date, end_date, college_filter=None):
    session = Session()
    """
    Fetches aggregated user engagement summary between given dates, with an optional college filter.
    
    :param session: SQLAlchemy session object
    :param start_date: Start date for filtering engagement data
    :param end_date: End date for filtering engagement data
    :param college_filter: Optional college ID filter
    :return: List of dictionaries containing engagement summary
    """
    try:
        # Prepare the SQL query
        query = text("""
            SELECT * 
            FROM get_engagement_kpi(:start_date, :end_date, :college_filter)
        """
        )

        # Execute the query
        result = session.execute(query, {
            'start_date': start_date,
            'end_date': end_date,
            'college_filter': college_filter if college_filter is not None else None
        })

        # Process the result into a list of dictionaries
        return [dict(row) for row in result.mappings()]
    finally:
        session.close()

def get_engagement_kpi(start_date, end_date, college_filter=None):
    """
    Fetches engagement KPI summary between given dates, with an optional college filter.
    
    :param start_date: Start date for filtering engagement data
    :param end_date: End date for filtering engagement data
    :param college_filter: Optional college filter (list of colleges)
    :return: List of dictionaries containing engagement KPI summary
    """
    session = Session()
    
    try:
        # Prepare the SQL query to call the function
        query = text("""
            SELECT * 
            FROM get_engagement_kpi(:start_date, :end_date, :college_filter)
        """)

        # Execute the query with the parameters
        result = session.execute(query, {
            'start_date': start_date,
            'end_date': end_date,
            'college_filter': college_filter if college_filter is not None else None
        })

        # Return the result as a list of dictionaries
        return [dict(row) for row in result.mappings()]
    finally:
        session.close()


def get_engagement_over_time(start_date, end_date, college_filter=None):
    """Fetches user engagement metrics over time within a date range, optionally filtering by college."""
    
    session = Session()
    try:
        query = text("""
            SELECT 
                engagement_date,
                total_views,
                total_unique_views,
                total_downloads
            FROM get_engagement_over_time(:start_date, :end_date, :college_filter)
        """)

        result = session.execute(query, {
            'start_date': start_date,
            'end_date': end_date,
            'college_filter': college_filter
        })

        engagement_data = [dict(row) for row in result.mappings()]
        return engagement_data
    finally:
        session.close()


def get_engagement_by_day_of_week(start_date, end_date, college_filter=None):
    """Fetches user engagement metrics grouped by the day of the week within a date range, optionally filtering by college."""
    
    # Ensure that college_filter is a list, not a numpy.ndarray
    if isinstance(college_filter, np.ndarray):
        college_filter = college_filter.tolist()

    session = Session()
    try:
        query = text("""
            SELECT 
                day_of_week,
                total_views,
                total_downloads,
                total_unique_views
            FROM get_engagement_by_day_of_week(:start_date, :end_date, :college_filter)
        """)

        result = session.execute(query, {
            'start_date': start_date,
            'end_date': end_date,
            'college_filter': college_filter  # Pass as a list, not an ndarray
        })

        engagement_data = [dict(row) for row in result.mappings()]
        return engagement_data
    finally:
        session.close()



def get_funnel_data(start_date, end_date, college_ids=None):
    """Fetches engagement funnel data (Views, Unique Views, and Downloads) within a date range, optionally filtering by college."""
    
    session = Session()
    try:
        # Ensure college_ids is a list if it's a numpy ndarray
        if isinstance(college_ids, np.ndarray):
            college_ids = college_ids.tolist()

        # If college_ids is provided, leave it as a list (PostgreSQL will handle conversion to array)
        # If no college_ids is provided, leave it as None for PostgreSQL
        if college_ids is None:
            college_ids = None

        # Prepare the query to call the get_funnel_data SQL function
        query = text("""
            SELECT 
                stage, 
                total_views 
            FROM get_funnel_data(:start_date, :end_date, :college_ids)
        """)

        # Execute the query with parameters
        result = session.execute(query, {
            'start_date': start_date,
            'end_date': end_date,
            'college_ids': college_ids  # Pass the list directly
        })

        # Convert the result into a list of dictionaries
        funnel_data = [dict(row) for row in result.mappings()]
        return funnel_data

    except Exception as e:
        # Log the error for debugging
        print(f"An error occurred while fetching the funnel data: {e}")
        return []

    finally:
        # Always close the session
        session.close()



def get_top_10_research_ids_by_views(start_date, end_date, college_id=None, view_type='total_unique_views'):
    """Fetches the top 10 research outputs by views (total or unique) within a date range, optionally filtering by college,
    and compares current period's views with the previous period's views."""
    
    session = Session()
    try:
        query = text("""
            SELECT 
                research_id, 
                total_value, 
                previous_value, 
                change_status
            FROM get_top_10_research_ids_by_views(:start_date, :end_date, :college_id, :view_type)
        """)

        result = session.execute(query, {
            'start_date': start_date,
            'end_date': end_date,
            'college_id': college_id,
            'view_type': view_type
        })

        # Map results into a list of dictionaries
        top_research = [dict(row) for row in result.mappings()]
        return top_research
    finally:
        session.close()

def get_top_10_research_ids_by_downloads(start_date, end_date, college_ids=None):
    """Fetches the top 10 research outputs by downloads within a date range, optionally filtering by college."""
    
    # Ensure college_ids is passed as a list or None
    if isinstance(college_ids, np.ndarray):  # If it's a numpy array, convert it to a list
        college_ids = college_ids.tolist()

    session = Session()
    try:
        # Execute the query with parameters
        query = text("""
            SELECT 
                research_id, 
                total_downloads,
                previous_total_downloads,
                trend
            FROM get_top_10_research_ids_by_downloads(:start_date, :end_date, :college_ids)
        """)

        # Execute the query, passing the list directly (not formatted as a string)
        result = session.execute(query, {
            'start_date': start_date,
            'end_date': end_date,
            'college_ids': college_ids  # Passing the list of college IDs
        })

        # Extract the results as a list of dictionaries
        top_downloads = [dict(row) for row in result.mappings()]
        return top_downloads
    finally:
        session.close()
def get_top_10_users_by_engagement(start_date, end_date, college_ids=None):
    """Fetches the top 10 users by engagement within a date range, optionally filtering by college."""

    # Ensure college_ids is passed as a list or None
    if isinstance(college_ids, np.ndarray):  # If it's a numpy array, convert it to a list
        college_ids = college_ids.tolist()

    session = Session()
    try:
        # Execute the query with parameters
        query = text("""
            SELECT 
                user_id, 
                total_views
            FROM get_top_10_users_by_engagement(:start_date, :end_date, :college_ids)
        """)

        # Execute the query, passing the list directly (not formatted as a string)
        result = session.execute(query, {
            'start_date': start_date,
            'end_date': end_date,
            'college_ids': college_ids  # Passing the list of college IDs
        })

        # Extract the results as a list of dictionaries
        top_users = [dict(row) for row in result.mappings()]
        return top_users
    finally:
        session.close()

def get_research_funnel_data(start_date, end_date, college_ids=None):
    """Fetches research-focused engagement funnel data (Total Views, Unique Views, Downloads) within a date range, optionally filtering by college."""
    
    session = Session()
    try:
        # Convert numpy array to list (if applicable)
        if isinstance(college_ids, np.ndarray):
            college_ids = college_ids.tolist()

        # Prepare the SQL function call
        query = text("""
            SELECT 
                stage, 
                total 
            FROM get_research_funnel_data(:start_date, :end_date, :college_ids)
        """)

        # Execute query with parameters
        result = session.execute(query, {
            'start_date': start_date,
            'end_date': end_date,
            'college_ids': college_ids
        })

        # Convert result to list of dictionaries
        funnel_data = [dict(row) for row in result.mappings()]
        return funnel_data

    except Exception as e:
        print(f"Error fetching research funnel data: {e}")
        return []

    finally:
        session.close()

def get_user_funnel_data(start_date, end_date, college_ids=None):
    """Fetches user-focused engagement funnel data (Total Interactions, Unique Users, Downloads) within a date range, optionally filtering by college."""
    
    session = Session()
    try:
        # Convert numpy array to list (if applicable)
        if isinstance(college_ids, np.ndarray):
            college_ids = college_ids.tolist()

        # Prepare the SQL function call
        query = text("""
            SELECT 
                stage, 
                total 
            FROM get_user_funnel_data(:start_date, :end_date, :college_ids)
        """)

        # Execute query with parameters
        result = session.execute(query, {
            'start_date': start_date,
            'end_date': end_date,
            'college_ids': college_ids
        })

        # Convert result to list of dictionaries
        funnel_data = [dict(row) for row in result.mappings()]
        return funnel_data

    except Exception as e:
        print(f"Error fetching user funnel data: {e}")
        return []

    finally:
        session.close()

def get_top_10_users_by_engagement(start_date, end_date, college_ids=None):
    """Fetches the top 10 users by engagement (total views) within a date range, optionally filtering by college."""
    
    # Ensure college_ids is passed as a list or None
    if isinstance(college_ids, np.ndarray):  # If it's a numpy array, convert it to a list
        college_ids = college_ids.tolist()

    session = Session()
    try:
        # Prepare the query to call the get_top_10_users_by_engagement SQL function
        query = text("""
            SELECT 
                user_id, 
                total_views
            FROM get_top_10_users_by_engagement(:start_date, :end_date, :college_ids)
        """)

        # Execute the query, passing the list directly (not formatted as a string)
        result = session.execute(query, {
            'start_date': start_date,
            'end_date': end_date,
            'college_ids': college_ids  # Passing the list of college IDs
        })

        # Extract the results as a list of dictionaries
        top_users = [dict(row) for row in result.mappings()]
        return top_users

    finally:
        session.close()

def get_top_10_users_by_downloads(start_date, end_date, college_ids=None):
    """Fetches the top 10 users by downloads within a date range, optionally filtering by college."""
    
    # Ensure college_ids is passed as a list or None
    if isinstance(college_ids, np.ndarray):  # If it's a numpy array, convert it to a list
        college_ids = college_ids.tolist()

    session = Session()  # Assuming you have a session created through SQLAlchemy
    try:
        # Prepare the query to call the get_top_10_users_by_downloads SQL function
        query = text("""
            SELECT 
                user_id, 
                total_downloads
            FROM get_top_10_users_by_downloads(:start_date, :end_date, :college_ids)
        """)

        # Execute the query, passing the list directly (not formatted as a string)
        result = session.execute(query, {
            'start_date': start_date,
            'end_date': end_date,
            'college_ids': college_ids  # Passing the list of college IDs
        })

        # Extract the results as a list of dictionaries
        top_users = [dict(row) for row in result.mappings()]
        return top_users

    finally:
        session.close()

def get_top_10_users_by_unique_views(start_date, end_date, college_ids=None):
    """Fetches the top 10 users by distinct research views within a date range, optionally filtering by college."""

    # Ensure college_ids is passed as a list or None
    if isinstance(college_ids, np.ndarray):  # If it's a numpy array, convert it to a list
        college_ids = college_ids.tolist()

    session = Session()  # Assuming you have a session created through SQLAlchemy
    try:
        # Prepare the query to call the get_top_10_users_by_unique_views SQL function
        query = text("""
            SELECT 
                full_name, 
                distinct_research_count
            FROM get_top_10_users_by_unique_views(:start_date, :end_date, :college_ids)
        """)

        # Execute the query, passing the list directly (not formatted as a string)
        result = session.execute(query, {
            'start_date': start_date,
            'end_date': end_date,
            'college_ids': college_ids  # Passing the list of college IDs
        })

        # Extract the results as a list of dictionaries
        top_users = [dict(row) for row in result.mappings()]
        return top_users

    finally:
        session.close()

def get_user_engagement_summary(start_date, end_date, college_ids=None):
    """Fetches the user engagement summary within a date range, optionally filtering by college."""

    # Ensure college_ids is passed as a list or None
    if isinstance(college_ids, np.ndarray):  # If it's a numpy array, convert it to a list
        college_ids = college_ids.tolist()

    session = Session()  # Assuming you have a session created through SQLAlchemy
    try:
        # Prepare the query to call the get_user_engagement_summary SQL function
        query = text("""
            SELECT 
                engagement_day, 
                user_id, 
                total_engagements
            FROM get_user_engagement_summary(:start_date, :end_date, :college_ids)
        """)

        # Execute the query, passing the list of college IDs (if provided)
        result = session.execute(query, {
            'start_date': start_date,
            'end_date': end_date,
            'college_ids': college_ids  # Passing the list of college IDs or None
        })

        # Extract the results as a list of dictionaries
        engagement_summary = [dict(row) for row in result.mappings()]
        return engagement_summary

    finally:
        session.close()

