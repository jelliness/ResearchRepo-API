from flask import Blueprint, request, jsonify
from models import db, ResearchOutput, SDG, Keywords, Publication, ResearchOutputAuthor, Panel, UserProfile

paper = Blueprint('paper', __name__)

@paper.route('/add_paper', methods=['POST'])
def add_paper():
    # Extract data from the request JSON
    data = request.get_json()
    print("Request data:", data)
    
    # Validate required fields
    required_fields = ['research_id', 'college_id', 'program_id', 'title', 'abstract', 'date_approved', 'research_type']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
    
    try:
        # Create a new ResearchOutput record
        new_paper = ResearchOutput(
            research_id = data['research_id'],
            college_id=data['college_id'],
            program_id=data['program_id'],
            title=data['title'],
            abstract=data['abstract'],
            date_approved=data['date_approved'],
            research_type=data['research_type']
        )
        
        # Add to session and commit
        db.session.add(new_paper)
        db.session.commit()
        
        return jsonify({"message": "Research output added successfully", "research_id": new_paper.research_id}), 201
    
    except Exception as e:
        # Rollback in case of error
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500