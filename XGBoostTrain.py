import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
import joblib  # For saving the model
import shap    # For SHAP value explanation

# Load dataset
file_path = "cardio_train.csv"  # Make sure the file is in the same directory
df = pd.read_csv(file_path)

# Define features and target
X = df.drop(columns=['cardio', 'id'])  # Drop 'id' during training
y = df['cardio']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

# Handle class imbalance using SMOTE
smote = SMOTE(random_state=42, k_neighbors=5)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

# Train XGBoost model
model = xgb.XGBClassifier(
    objective='binary:logistic',
    tree_method='hist',
    eval_metric='logloss',
    random_state=42
)
model.fit(X_train_resampled, y_train_resampled)

# Save trained model
joblib.dump(model, "heart_failure_xgb_model.pkl")
print("Model trained and saved as 'heart_failure_xgb_model.pkl'")

# Create SHAP explainer for the trained model
explainer = shap.TreeExplainer(model)

# Optional: Save the SHAP explainer too (not mandatory, but helps load faster later)
joblib.dump(explainer, "shap_explainer.pkl")
print("SHAP explainer saved as 'shap_explainer.pkl'")

# Optional: Save feature list for reference or consistency checking
with open("features_used.txt", "w") as f:
    f.write("\n".join(X_train.columns.tolist()))
print("Features used in training saved to 'features_used.txt'")
