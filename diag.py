import falcon

import rpy2.situation
import rpy2.robjects.packages as rpackages
import rpy2.robjects as robjects
import sys

# import R's utility package
utils = rpackages.importr('utils')

# select a mirror for R packages
utils.chooseCRANmirror(ind=1) # select the first mirror in the list

# Finally, import BlockTools
bt = rpackages.importr('blockTools')

# Falcon follows the REST architectural style, meaning (among
# other things) that you think in terms of resources and state
# transitions, which map to HTTP verbs.
class DiagResource(object):
    def on_get(self, req, resp):
        """Handles GET requests"""
        resp.status = falcon.HTTP_200  # This is the default status
        
        # capture each of the blocking vars
        cap_age = req.params["age"]
        cap_gender = req.params["gender"]
        cap_ethnicity = req.params["ethnicity"]
        cap_party = req.params["party"]
        cap_employment = req.params["employment"]
        cap_education = req.params["education"]
        cap_shock = req.params["shock"]
        cap_id = req.params["id"]
        py_session = req.params["session"] + ".RData"
        
        py_exact_var = ["age", "gender", "ethnicity", "party", "employment", "education"]
        py_exact_val = [cap_age, cap_gender, cap_ethnicity, cap_party, cap_employment, cap_education, cap_shock]
        
        robjects.r('''
                       f <- function(id, exact_var, exact_val, session) {

                        # the session has not been seen before, then the corresponding file doesn't exist
                        # and this must be the first assignment
                        if(!file.exists(session)) {
                            seqout <- seqblock(query = FALSE
                                            , id.vars = "ID"
                                            , id.vals = id
                                            , n.tr = 4
                                            , tr.names = c("T1", "T2", "T3", "Placebo") 
                                            , assg.prob = c(1/4, 1/4, 1/4, 1/4)
                                            , exact.vars = exact_var
                                            , exact.vals = exact_val
                                            , file.name = session)
                        }
                        else {
                            seqout <- seqblock(query = FALSE
                                            , object = session
                                            , id.vals = id
                                            , n.tr = 4
                                            , tr.names = c("T1", "T2", "T3", "Placebo") 
                                            , assg.prob = c(1/4, 1/4, 1/4, 1/4)
                                            , exact.vals = exact_val
                                            , file.name = session)
                        }
                        seqout$x[seqout$x['ID'] == id , "Tr"]
                        }
                       ''')

        r_f = robjects.r['f']
        out = r_f(cap_id, py_exact_var, py_exact_val, py_session)
        resp.body = 'Treatment=' + str(out[0])

            
# falcon.API instances are callable WSGI apps
app = falcon.API()

app.add_route('/test', DiagResource())
