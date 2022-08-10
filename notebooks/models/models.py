class BaseClf:
    def score_auc(self, p):
        try:
            predictions = self.predict(p["steps"])
            labels = [s[4] for s in p["steps"]]
            prop_auc = roc_auc_score(labels, predictions)
        except Exception as e:
            print(p)
            raise e
        return prop_auc

class RandomClassifier(BaseClf):
    def predict(self, X):
        return np.random.random(len(X))

class WeightClassifier(BaseClf):   
    def predict(self, X):
        predictions = list()
        for s in X:
            predictions.append(len(s[2].split(" ")))
        
        predictions = np.array(predictions)
        
        #Get max value and normalize by it
        max_pred = predictions.max()
        predictions = predictions / max_pred
        
        # The way it is the largest statement will get the value of 1
        # Here we will treat the negative class as the statement to be removed
        # So we need to invert the prediction with 1-pred     
        return 1 - predictions

class WeightDistClassifier(BaseClf):   
    def predict(self, X):
        predictions = list()
        for s in X:
            predictions.append(len(set(s[2].split(" "))))
        
        predictions = np.array(predictions)
        
        #Get max value and normalize by it
        max_pred = predictions.max()
        predictions = predictions / max_pred
        
        # The way it is the largest statement will get the value of 1
        # Here we will treat the negative class as the statement to be removed
        # So we need to invert the prediction with 1-pred     
        return 1 - predictions