import redis
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import os
from rq import Queue, Connection
from rq.worker import Worker

import tasks

_url = f"redis://:@localhost:6379"

_redis = redis.from_url(_url)


for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

mood_file_path = '/Users/Edmund/PycharmProjects/moodMaestro/data_moods.csv'
mood_data = pd.read_csv(mood_file_path)

feature_names = ['danceability', 'energy', 'valence',
                 'loudness', 'speechiness', 'tempo', 'key']
X = mood_data[feature_names]
y = mood_data.mood

# Happy = 0, Sad = 1, Energetic = 2, Calm = 3

train_X, val_X, train_y, val_y = train_test_split(X,y, random_state=1)

tasks.forest_model = RandomForestClassifier(random_state=1)
tasks.forest_model.fit(X, y)

with Connection(_redis):
    worker = Worker(
        ['default']
    )
    worker.work()