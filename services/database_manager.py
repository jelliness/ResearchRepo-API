import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func, desc
from models import College, Program, ResearchOutput, Publication, Status, Conference, ResearchOutputAuthor, Account, UserProfile, Keywords, SDG
from services.data_fetcher import ResearchDataFetcher

class DatabaseManager:
    def __init__(self, database_uri):
        self.engine = create_engine(database_uri)
        self.Session = sessionmaker(bind=self.engine)
        self.df = None

        self.get_all_data()

    def get_data_from_model(self,model):
        fetcher = ResearchDataFetcher(model)
        data = fetcher.get_data_from_model()
        return data

    def get_all_data(self):
        session = self.Session()
        try:
            # Subquery to get the latest status for each publication
            latest_status_subquery = session.query(
                Status.publication_id,
                Status.status,
                func.row_number().over(
                    partition_by=Status.publication_id,
                    order_by=desc(Status.timestamp)
                ).label('rn')
            ).subquery()

            # Subquery to concatenate authors
            authors_subquery = session.query(
                ResearchOutputAuthor.research_id,
                func.string_agg(
                    func.concat(
                        UserProfile.last_name, ', ',  # Surname first
                        func.substring(UserProfile.first_name, 1, 1), '. ',  # First name initial
                        func.coalesce(func.substring(UserProfile.middle_name, 1, 1) + '.', '') 
                    ), '; '
                ).label('concatenated_authors')
            ).join(Account, ResearchOutputAuthor.author_id == Account.user_id) \
            .join(UserProfile, Account.user_id == UserProfile.researcher_id) \
            .group_by(ResearchOutputAuthor.research_id).subquery()

            # Subquery to concatenate keywords
            keywords_subquery = session.query(
                Keywords.research_id,
                func.string_agg(Keywords.keyword, '; ').label('concatenated_keywords')
            ).group_by(Keywords.research_id).subquery()

            # Subquery to concatenate SDG
            sdg_subquery = session.query(
                SDG.research_id,
                func.string_agg(SDG.sdg, '; ').label('concatenated_sdg')
            ).group_by(SDG.research_id).subquery()

            # Main query
            query = session.query(
                College.college_id,
                Program.program_id,
                Program.program_name,
                sdg_subquery.c.concatenated_sdg,
                ResearchOutput.research_id,
                ResearchOutput.title,
                ResearchOutput.date_approved,
                ResearchOutput.research_type,
                authors_subquery.c.concatenated_authors,
                keywords_subquery.c.concatenated_keywords,
                Publication.publication_name,
                Publication.journal,
                Publication.scopus,
                Publication.date_published,
                Conference.conference_venue,
                Conference.conference_title,
                Conference.conference_date,
                latest_status_subquery.c.status
            ).join(College, ResearchOutput.college_id == College.college_id) \
            .join(Program, ResearchOutput.program_id == Program.program_id) \
            .outerjoin(Publication, ResearchOutput.research_id == Publication.research_id) \
            .outerjoin(Conference, Publication.conference_id == Conference.conference_id) \
            .outerjoin(latest_status_subquery, (Publication.publication_id == latest_status_subquery.c.publication_id) & (latest_status_subquery.c.rn == 1)) \
            .outerjoin(authors_subquery, ResearchOutput.research_id == authors_subquery.c.research_id) \
            .outerjoin(keywords_subquery, ResearchOutput.research_id == keywords_subquery.c.research_id) \
            .outerjoin(sdg_subquery, ResearchOutput.research_id ==  sdg_subquery.c.research_id) \
            .distinct()

            result = query.all()

            # Formatting results into a list of dictionaries with safe handling for missing data
            data = [{
                'research_id': row.research_id if pd.notnull(row.research_id) else 'Unknown',
                'college_id': row.college_id if pd.notnull(row.college_id) else 'Unknown',
                'program_name': row.program_name if pd.notnull(row.program_name) else 'N/A',
                'program_id': row.program_id if pd.notnull(row.program_id) else None,
                'title': row.title if pd.notnull(row.title) else 'Untitled',
                'year': row.date_approved.year if pd.notnull(row.date_approved) else None,
                'date_approved': row.date_approved,
                'concatenated_authors': row.concatenated_authors if pd.notnull(row.concatenated_authors) else 'Unknown Authors',
                'concatenated_keywords': row.concatenated_keywords if pd.notnull(row.concatenated_keywords) else 'No Keywords',
                'sdg': row.concatenated_sdg if pd.notnull(row.concatenated_sdg) else 'Not Specified',
                'research_type': row.research_type if pd.notnull(row.research_type) else 'Unknown Type',
                'journal': row.journal if pd.notnull(row.journal) else 'unpublished',
                'scopus': row.scopus if pd.notnull(row.scopus) else 'N/A',
                'date_published': row.date_published,
                'published_year': int(row.date_published.year) if pd.notnull(row.date_published) else None,
                'conference_venue': row.conference_venue if pd.notnull(row.conference_venue) else 'Unknown Venue',
                'conference_title': row.conference_title if pd.notnull(row.conference_title) else 'No Conference Title',
                'conference_date': row.conference_date,
                'status': row.status if pd.notnull(row.status) else "READY",
                'country': row.conference_venue.split(",")[-1].strip() if pd.notnull(row.conference_venue) else 'Unknown Country'
            } for row in result]

            # Convert the list of dictionaries to a DataFrame
            self.df = pd.DataFrame(data)

        finally:
            session.close()

        return self.df

    def get_unique_values(self, column_name):
        if self.df is not None and column_name in self.df.columns:
            unique_values = self.df[column_name].dropna().unique()
            if len(unique_values) == 0:
                print(f"Warning: Column '{column_name}' exists but contains no values.")
            return unique_values
        else:
            return []  # Return an empty list if the column doesn't exist or has no values

    def get_columns(self):
        return self.df.columns.tolist() if self.df is not None else []

    def filter_data(self, column_name, value, invert=False):
        if self.df is not None:
            if column_name in self.df.columns:
                if invert:
                    return self.df[self.df[column_name] != value]
                else:
                    return self.df[self.df[column_name] == value]
            else:
                raise ValueError(f"Column '{column_name}' does not exist in the DataFrame.")
        else:
            raise ValueError("Data not loaded. Please call 'get_all_data()' first.")

    def filter_data_by_list(self, column_name, values, invert=False):
        if self.df is not None:
            if column_name in self.df.columns:
                if invert:
                    return self.df[~self.df[column_name].isin(values)]
                else:
                    return self.df[self.df[column_name].isin(values)]
            else:
                raise ValueError(f"Column '{column_name}' does not exist in the DataFrame.")
        else:
            raise ValueError("Data not loaded. Please call 'get_all_data()' first.")

    def get_min_value(self, column_name):
        if self.df is not None and column_name in self.df.columns:
            return self.df[column_name].min()
        else:
            raise ValueError(f"Column '{column_name}' does not exist in the DataFrame.")

    def get_max_value(self, column_name):
        if self.df is not None and column_name in self.df.columns:
            return self.df[column_name].max()
        else:
            raise ValueError(f"Column '{column_name}' does not exist in the DataFrame.")

    def get_filtered_data(self, selected_colleges, selected_status, selected_years):
        if self.df is not None:
            filtered_df = self.df[
                (self.df['college_id'].isin(selected_colleges)) & 
                (self.df['status'].isin(selected_status)) & 
                (self.df['year'].between(selected_years[0], selected_years[1]))
            ]
            return filtered_df
        else:
            raise ValueError("Data not loaded. Please call 'get_all_data()' first.")
