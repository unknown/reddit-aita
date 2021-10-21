import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('aita_stratified.csv')

X = (df['title'] + df['body']).values
X = X.astype(str)

Y = df['verdict'].values
Y = np.asarray(Y).astype(np.int32)

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)

print('Loaded data')

vocab_size = 10000
oov_token = '<OOV>'
max_length = 500

tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_token)
tokenizer.fit_on_texts(X_train)

X_train = tokenizer.texts_to_sequences(X_train)
X_test = tokenizer.texts_to_sequences(X_test)

X_train = pad_sequences(X_train, maxlen=max_length, padding='post', truncating='post')
X_test = pad_sequences(X_test, maxlen=max_length, padding='post', truncating='post')

word_index = tokenizer.word_index
print('Tokenized data,', len(word_index), 'words')

def create_embedding_matrix(filepath, word_index, embedding_dim):
    vocab_size = len(word_index) + 1
    embedding_matrix = np.zeros((vocab_size, embedding_dim))

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            word, *vector = line.split()
            if word in word_index:
                idx = word_index[word]
                embedding_matrix[idx] = np.array(vector, dtype=np.float32)[:embedding_dim]

    return embedding_matrix

embedding_dim = 100
embedding_matrix = create_embedding_matrix('glove.twitter.27B.100d.txt', word_index, embedding_dim)

nonzero_elements = np.count_nonzero(np.count_nonzero(embedding_matrix, axis=1))
embedding_accuracy = nonzero_elements / (len(word_index) + 1)
print('Embedding accuracy: ' + str(embedding_accuracy))

model = keras.Sequential()
model.add(layers.Embedding(len(word_index) + 1, embedding_dim, weights=[embedding_matrix], input_length=max_length, trainable=False))
model.add(layers.Conv1D(128, 5, activation='relu'))
model.add(layers.Dropout(0.7))
model.add(layers.GlobalMaxPooling1D())
model.add(layers.Dense(16, activation='relu'))
model.add(layers.Dense(1, activation='sigmoid'))
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

res = model.fit(X_train, Y_train, epochs=20, verbose=True, validation_data=(X_test, Y_test), batch_size=512)


plt.plot(res.history['accuracy'])
plt.plot(res.history['val_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='upper left')
plt.show()

Y_pred = model.predict(X_test, verbose=1)

x_ax = range(len(Y_pred))
plt.scatter(x_ax, Y_test, s=5, color='blue', label='original')
plt.plot(x_ax, Y_pred, lw=0.8, color='red', label='predicted')
plt.legend()
plt.show()

cf_matrix = confusion_matrix(Y_test, (Y_pred > 0.5).astype(np.int32))
print(cf_matrix)
sns.heatmap(cf_matrix, annot=True)
plt.show()

model.save('aita_classifier')