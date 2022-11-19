import numpy as np
import pandas as pd

def from_promotion(category_top_articles,n):
    #
    # definir une strategie appropriée
    #
    promoted_categories   = category_top_articles[category_top_articles.top_articles.str.count(',')==2].index.tolist()

    res = []
    for i in range(n):
        random_idx = np.random.randint(2)
        icat = np.random.choice(promoted_categories,1)[0]
        res.append(eval(category_top_articles.loc[icat][0])[random_idx])
    return res

def recommend_from_user_pc(category_top_articles,user_pc):
    #
    #
    assert len(user_pc)>0,"--> empty user_pcs"
    ur_list=[]
    n1 = 5 % len(user_pc)
    n2 = int(5 / len(user_pc))
    ur_list=[]
    n = lambda e: n2+n1 if e==0 else n2
    retardataire = 0
    for i,category in enumerate(user_pc):
        smth = eval(category_top_articles.loc[category][0])[:n(i)]
        if len(smth)<n(i):
            retardataire += n(i) - len(smth)
        ur_list.extend(smth)
    ur_list.extend(from_promotion(category_top_articles,retardataire))
    return str(ur_list)

def RS_knowledge_based(region_top_articles,category_top_articles,region=None,user_pc=[]):
    #
    # On recommande, dans l'ordre de priorité et ses la disponibilité e l'information
    #  - 5 articles distribuées equitablement sur les categories (de 0 a 3) preferrees de l'utilisateur
    #  - 5 articles de la region de l'utilisateur
    #  - les 5 articles les plus populaires de tous les articles 
    #
        if len(user_pc)>0:
            return recommend_from_user_pc(category_top_articles,user_pc)
        elif region!=None:
            return region_top_articles.loc[region][0]
        else:
            return "You got a problem!!! nothing to fear!"