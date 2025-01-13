from . import db

class ArchiveManus(db.Model):
    __tablename__ = 'archive_manus'
    timestamp = db.Column(db.TIMESTAMP, primary_key=True)
    research_id = db.Column(db.String(15), db.ForeignKey('research_outputs.research_id'))
    full_manuscript = db.Column(db.String(100))