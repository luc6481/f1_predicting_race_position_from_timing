import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

data = pd.read_csv("C:/Users/660638/OneDrive - Culver Educational Foundation/App of P2/combined.csv")
data = data[["FP1 Lap Time", "FP1 Position", "FP2 Lap Time", "FP2 Position", "FP3 Lap Time", "FP3 Position", "Qualifying Lap Time", "Qualifying Position", "Race Position"]]

x_std = StandardScaler().fit_transform(data)



x = data[["FP1 Lap Time", "FP1 Position", "FP2 Lap Time", "FP2 Position", "FP3 Lap Time", "FP3 Position", "Qualifying Lap Time", "Qualifying Position"]].values
y = data["Race Position"].values

xtrain, xtest, ytrain, ytest = train_test_split(x,y)
model = LinearRegression().fit(xtrain, ytrain)

print("Model Information:")
print("FP1 LT Coef:" , round(model.coef_[0],3))
print("FP1 P Coef:" , round(model.coef_[1],3))
print("FP2 LT Coef:" , round(model.coef_[2],3))
print("FP2 P Coef:" , round(model.coef_[3],3))
print("FP3 LT Coef:" , round(model.coef_[4],3))
print("FP3 P Coef:" , round(model.coef_[5],3))
print("Q LT Coef:" , round(model.coef_[6],3))
print("Q P Coef:" , round(model.coef_[7],3))
print("Intercept: ", round(model.intercept_, 3))
print("Score:", model.score(xtrain, ytrain))

print("Testing Results")
for index in range(len(xtest)):
    x = xtest[index]
    x = x.reshape(-1,2)
    ypred = round(float(model.predict(x)), 4)
    actual = round(ytest[index], 4)
    print("x data : " , round(xtest[index],2) , "\n predicted standing: " , ypred , "\n actual standing: " , actual)
    


plt.figure(figsize = (5,4))
plt.scatter(x, y, c = "purple", label = "FP1 Lap Time")
plt.scatter(z, y, c = "blue", label = "FP2 Lap Time")
plt.scatter(w, y, c = "green", label = "FP3 Lap Time")
plt.xlabel("Lap Time")
plt.ylabel("Race Position")
plt.title("FP1 and FP2 Lap Time with Final Race Position")
plt.show()



