from app.repositories import deportes_repository

def listar_deportes():
    return deportes_repository.find_all()
