import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import confusion_matrix, accuracy_score

df = pd.read_csv('2_aita_stratified.csv')
X = (df['title'] + df['body']).values

X = X.astype(str)
Y = df['verdict'].values

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)

print('Loaded data')

vectorizer = TfidfVectorizer(binary=False, max_df=0.95, stop_words='english')
X_train = vectorizer.fit_transform(X_train).toarray()
X_test = vectorizer.transform(X_test).toarray()

print('Vectorized data')


scikit_log_reg = LogisticRegression(verbose=1, solver='liblinear',random_state=0, C=5, penalty='l2',max_iter=1000)
model = scikit_log_reg.fit(X_train, Y_train)


"""
model = MultinomialNB().fit(X_train, Y_train)
"""

print('Finished training')

Y_pred = model.predict(X_test)

print("Accuracy:", accuracy_score(Y_test, Y_pred))
print(confusion_matrix(Y_test, Y_pred))