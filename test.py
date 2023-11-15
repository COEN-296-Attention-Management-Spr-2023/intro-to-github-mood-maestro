from redis import Redis
from rq import Queue
from tasks import job
from sklearn.model_selection import train_test_split
import time
import pandas as pd

q = Queue(connection=Redis())

mood_file_path = '/Users/Edmund/PycharmProjects/moodMaestro/data_moods.csv'
mood_data = pd.read_csv(mood_file_path)

feature_names = ['danceability', 'energy', 'valence',
                 'loudness', 'speechiness', 'tempo', 'key']
X = mood_data[feature_names]
y = mood_data.mood

train_X, val_X, train_y, val_y = train_test_split(X, y, random_state=1)

job = q.enqueue(job, val_X)
print(job.return_value())

time.sleep(2)

print(job.return_value())
