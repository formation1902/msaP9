import json

class User():
    global_tolerance = 3
    def __init__(self,user_id,tolerance=None):
        self.user_id = user_id
        self.user_pcs = {}
        if tolerance is None:
            self.tolerance = User.global_tolerance
        else:
            self.tolerance = int(tolerance)
        self.user_ra = []

    def setUserRA(self,ra_list):
        self.user_ra = ra_list[:5]
        
    def toJson(self):
        return json.dumps({
            'user_id':self.user_id,
            'user_ra':self.user_ra
        })