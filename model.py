from sklearn.neural_network import MLPClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
import pandas as pd

# donnees synthetiques
# n_samples = 300
# n_features = 5
# n_classes = 2
# X, y = make_classification(n_samples=n_samples, n_features=n_features, n_classes=n_classes)
# X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, random_state=1)

training_data_df = pd.read_csv(
    filepath_or_buffer=r"data\training_data.csv",
    sep=',',
    header=0)

# original_headers = list(training_data_df.columns.values)

# numpy_array = training_data_df.as_matrix()
X = training_data_df.drop(columns=['DISPONIBLE']).to_numpy()
y = training_data_df['DISPONIBLE'].to_numpy()
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, random_state=1)

# perceptron
hidden_layer_sizes = (88,4)
clf = MLPClassifier(random_state=42, max_iter=2000).fit(X_train, y_train)
