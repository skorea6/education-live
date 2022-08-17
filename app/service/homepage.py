from app.database.models.homepage import t_homepage


def get_homepage(session):
    return session.query(t_homepage).first()
