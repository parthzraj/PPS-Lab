
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats


np.random.seed(42)


math_scores = np.random.normal(loc=70, scale=10, size=100)
science_scores = np.random.normal(loc=65, scale=12, size=100)


data = pd.DataFrame({
    'Math': math_scores,
    'Science': science_scores
})

print("First 5 rows of dataset:")
print(data.head())


print("\nStatistical Summary:")
print(data.describe())


correlation = data.corr()
print("\nCorrelation between subjects:")
print(correlation)


corr, p_value = stats.pearsonr(data['Math'], data['Science'])

print("\nSciPy Pearson Correlation:")
print(f"Correlation Coefficient: {corr}")
print(f"P-value: {p_value}")


plt.figure()


plt.scatter(data['Math'], data['Science'])


slope, intercept, _, _, _ = stats.linregress(data['Math'], data['Science'])
line = slope * data['Math'] + intercept
plt.plot(data['Math'], line)

plt.xlabel("Math Scores")
plt.ylabel("Science Scores")
plt.title("Math vs Science Scores")

plt.show()