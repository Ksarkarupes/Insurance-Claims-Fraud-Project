import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import joblib
import os

# 1. Load Data
data_path = '/home/koustav/Documents/Development/Insurance-Claims-Fraud-Project/data/insurance_claims.csv'
if not os.path.exists(data_path):
    print(f"Error: {data_path} not found!")
    exit()

df = pd.read_csv(data_path)

# 2. Basic Cleaning
df.replace('?', np.nan, inplace=True)
df['collision_type'] = df['collision_type'].fillna(df['collision_type'].mode()[0])
df['property_damage'] = df['property_damage'].fillna(df['property_damage'].mode()[0])
df['police_report_available'] = df['police_report_available'].fillna(df['police_report_available'].mode()[0])

# Dropping unnecessary columns
to_drop = ['policy_number','policy_bind_date','policy_state','insured_zip','incident_location','incident_date',
           'incident_state','incident_city','insured_hobbies','auto_make','auto_model','auto_year', '_c39',
           'age','total_claim_amount']
df.drop(to_drop, inplace=True, axis=1)

# 3. Feature Engineering
X = df.drop('fraud_reported', axis=1)
y = df['fraud_reported']

# Encoding categorical variables
cat_df = X.select_dtypes(include=['object'])
cat_df = pd.get_dummies(cat_df, drop_first=True)
num_df = X.select_dtypes(include=['int64'])
X = pd.concat([num_df, cat_df], axis=1)

# 4. Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# 5. Scaling (The important part for your resume's "Data Analytics" claim)
scaler = StandardScaler()

# We only scale the numerical columns we identified earlier
cols_to_scale = ['months_as_customer', 'policy_deductable', 'umbrella_limit',
                 'capital-gains', 'capital-loss', 'incident_hour_of_the_day',
                 'number_of_vehicles_involved', 'bodily_injuries', 'witnesses', 
                 'injury_claim', 'property_claim', 'vehicle_claim']

X_train_scaled = X_train.copy()
X_test_scaled = X_test.copy()

X_train_scaled[cols_to_scale] = scaler.fit_transform(X_train[cols_to_scale])
X_test_scaled[cols_to_scale] = scaler.transform(X_test[cols_to_scale])

# 6. Training the Random Forest
rand_clf = RandomForestClassifier(criterion='entropy', max_depth=10, max_features='sqrt', 
                                  min_samples_leaf=1, min_samples_split=3, n_estimators=140)
rand_clf.fit(X_train_scaled, y_train)

# 7. Evaluation
y_pred = rand_clf.predict(X_test_scaled)
print(f"Training accuracy: {accuracy_score(y_train, rand_clf.predict(X_train_scaled))}")
print(f"Test accuracy: {accuracy_score(y_test, y_pred)}")
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))

# 8. THE EXPORT
# This saves them in the 'scripts' folder where your train_model.py lives
joblib.dump(rand_clf, '/home/koustav/Documents/Development/Insurance-Claims-Fraud-Project/scripts/fraud_model.pkl')
joblib.dump(scaler, '/home/koustav/Documents/Development/Insurance-Claims-Fraud-Project/scripts/scaler.pkl')
joblib.dump(X_train.columns.tolist(), '/home/koustav/Documents/Development/Insurance-Claims-Fraud-Project/scripts/model_columns.pkl')

print("\nSuccess: Model, Scaler, and Column Schema saved as .pkl files!")