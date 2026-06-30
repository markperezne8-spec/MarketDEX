class BaseRepository:
    def add(self, obj): raise NotImplementedError
    def update(self, obj): raise NotImplementedError
    def delete(self, obj_id): raise NotImplementedError
    def get(self, obj_id): raise NotImplementedError
    def get_all(self): raise NotImplementedError
