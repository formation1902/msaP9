import json
import numpy as np
from threading import Lock

class User():
    global_tolerance = 3
    
    class threadSafeUsersIdManager():
        def __init__(self,msaList):
            self.known_user_ids = msaList
            self.lock = Lock()
            

        def handleNewUser(self):
            with self.lock:
                user_id = self.known_user_ids[-1]+1
                self.known_user_ids = np.append(self.known_user_ids,user_id)
            return user_id
        
    
    @staticmethod
    def init(known_users):
        User._userIdManager   = User.threadSafeUsersIdManager(known_users)
    
    def __init__(self,user_id,tolerance=None):
        self._new_user=None
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
        self.greeting = []
        self.is_a_specialist = False
        self._current_session_consulted_articles = {}

    def recordNewConsultation(self,article_id):
        if article_id in self._current_session_consulted_articles:
            self._current_session_consulted_articles.update({article_id:self._current_session_consulted_articles[article_id]+1})
        else:
            self._current_session_consulted_articles[article_id]=1
                                                        
    def getUserSessionInteractions(self):
        return self._current_session_consulted_articles
    def set_as_new_user(self):
        self._new_user = True
    
    def is_new_user(self):
        return self._new_user
        
    def setNewUserId(self):
        assert self.user_id==-1,"You and I, we got a pb"
        self.user_id = User._userIdManager.handleNewUser()
        
    def setUserPreferredCategories(self,user_pcs_as_list):
        self.user_pcs = user_pcs_as_list
    
    def setUserGreeting(self,greeting):
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
            'user_ra':  [str(article.article_id) for article in self.user_ra],
            'user_ra_cbrs':[article.article_id for article in self.user_ra_cbrs],
            'user_ra_cfrs':[article.article_id for article in self.user_ra_cfrs],
            "current_session_consulted_articles" : self._current_session_consulted_articles
        })