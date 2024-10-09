#dataset.py code (modified to include Keyword)
#created by Nicole Cabansag (Oct. 7, 2024)

from flask import Blueprint, jsonify
from sqlalchemy import func, desc
from models import College, Program, ResearchOutput, Publication, Status, Conference, ResearchOutputAuthor, Account, UserProfile, Keywords, db

dataset = Blueprint('dataset', __name__)

@dataset.route('/fetch_dataset', methods=['GET'])
def retrieve_dataset():
    #subquery to get the latest status for each publication
    latest_status_subquery = db.session.query(
        Status.publication_id,
        Status.status,
        func.row_number().over(
            partition_by=Status.publication_id,
            order_by=desc(Status.timestamp)
        ).label('rn')
    ).subquery()

    #subquery to concatenate authors
    middle_name = ''
    suffix = ''
    if UserProfile.middle_name:
        middle_name = UserProfile.middle_name+' '
    if UserProfile.suffix:
        suffix = ' '+UserProfile.suffix

    authors_subquery = db.session.query(
        ResearchOutputAuthor.research_id,
        func.string_agg(
            func.concat(UserProfile.first_name, ' ', middle_name, UserProfile.last_name, suffix),
            '; '
        ).label('concatenated_authors')
    ).join(Account, ResearchOutputAuthor.author_id == Account.user_id) \
     .join(UserProfile, Account.user_id == UserProfile.researcher_id) \
     .group_by(ResearchOutputAuthor.research_id).subquery()

    #subquery to concatenate keywords
    keywords_subquery = db.session.query(
        Keywords.research_id,
        func.string_agg(Keywords.keyword, '; ').label('concatenated_keywords')
    ).group_by(Keywords.research_id).subquery()

    #main query
    query = db.session.query(
        College.college_id,
        Program.program_name,
        ResearchOutput.sdg,
        ResearchOutput.title,
        ResearchOutput.date_approved,
        authors_subquery.c.concatenated_authors,
        keywords_subquery.c.concatenated_keywords,
        Publication.journal,
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
     .distinct()

    result = query.all()

    #formatting results into a list of dictionaries
    data = [{
        'college_id': row.college_id,
        'program_name': row.program_name,
        'sdg': row.sdg,
        'title': row.title,
        'date_approved': row.date_approved,
        'concatenated_authors': row.concatenated_authors,
        'concatenated_keywords': row.concatenated_keywords,
        'journal': row.journal,
        'date_published': row.date_published,
        'conference_venue': row.conference_venue,
        'conference_title': row.conference_title,
        'conference_date': row.conference_date,
        'status': row.status
    } for row in result]

    return jsonify(data)
