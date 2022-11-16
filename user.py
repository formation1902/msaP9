import json

class User():
    global_tolerance = 3
    def __init__(self,user_id,tolerance=None):
        self.user_id = user_id
        self.user_pcs = []
        if tolerance is None:
            self.tolerance = User.global_tolerance
        else:
            self.tolerance = int(tolerance)
        self.user_ra = []
        self.user_ra_cbrs = []
        self.user_ra_cfrs = []
        self.user_region = -1
        self.greeting = 'who are you and what are you doing here !!!'
        self.is_a_specialist = False

    def setUserPreferredCategories(self,user_pcs_as_list):
        self.user_pcs = user_pcs_as_list
    
    def setUserGreeting(self,greeting):
        self.greeting = greeting
                
    def addUserGreeting(self,greeting):
        self.greeting = [self.greeting]
        self.greeting.append(greeting)
                    
    def setUserRA(self,ra_list):
        self.user_ra = ra_list[:5]
        
    def setUser_cbrs(self,smth):
        self.user_ra_cbrs = smth[:5]
    
    def setUser_cfrs(self,smth):
        self.user_ra_cfrs = smth[:5]
        
    def setUserRegion(self,region_id):
        self.user_region = region_id
    
    def set_as_specialist(self):
        self.is_a_specialist = True


    def toJson(self):
        return json.dumps({
            'user_id':self.user_id,
            'user_region':self.user_region,
            'user_pcs':self.user_pcs,
            'user_ra':self.user_ra
        })