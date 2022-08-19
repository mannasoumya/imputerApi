# Data Imputer API in Python

[![Generic badge](https://img.shields.io/badge/imputerApi-passing-<COLOR>.svg)](https://pypi.org/project/ImputerApi/)
[![Downloads](https://pepy.tech/badge/imputerapi)](https://pepy.tech/project/imputerapi)
[![Downloads](https://pepy.tech/badge/imputerapi/month)](https://pepy.tech/project/imputerapi)


Check out the [Wiki](<https://en.wikipedia.org/wiki/Imputation_(statistics)>) here.

### <a href="https://mannasoumya.github.io/imputerApi/" target="_blank"> 'imputerApi' Documentation. </a>

## Currently Supported Strategies:

- Mean
- Median
- Most-Frequent
- Constant
- K Nearest Neighbors

## Usage:

#### Read from csv file:

```python
from imputerApi import ImputerApi
# Create instance of class
imm_api = ImputerApi(path_to_file="data.csv",strategy='mean', headers=True)
# Print data in console
imm_api.print_table(imm_api.data)
# Transform data by replacing missing values with mean
# and selecting only columns Age and Salary with indexes 1 and 2
replaced_data = imm_api.transform(column_indexes=[1, 2])
# Print repalced data in console
imm_api.print_table(replaced_data)
# Write new data to csv file
imm_api.dump_data_to_csv('datanew_mean.csv', replaced_data,use_header_from_data=True, override=True)
```

#### Read from a Two Dimensional Matrix (Python List):

```python
from imputerApi import ImputerApi
matrix_2d = [
    ['Country', 'Age', 'Salary', 'Purchased'],
    ['France', 44, 72000, 'No'],
    ['Spain', 27, 48000, 'Yes'],
    ['Germany', 30, 54000, 'No'],
    ['Spain', 38, 61000, 'No'],
    ['Germany', 40, '', 'Yes'],
    ['France', 35, 58000, 'Yes'],
    ['Spain', '', 52000, 'No'],
    ['France', 48, 79000, 'Yes'],
    ['Germany', 50, 83000, 'No'],
    ['France', 37, 67000, 'Yes']
]
# Create instance of class
imm_api = ImputerApi(matrix_2D=matrix_2d, strategy='median', headers=True)
# Print data in console
imm_api.print_table(imm_api.data)
# Transform data by replacing missing values with median
# and selecting only columns Age and Salary
replaced_data = imm_api.transform(columns_by_header_name=["Age","Salary"])
# Print repalced data in console
imm_api.print_table(replaced_data)
# Write new data to csv file
imm_api.dump_data_to_csv('datanew_median.csv', replaced_data,use_header_from_data=True,override=True)
# Create instance with strategy most-frequent
imm_api_most_freq = ImputerApi(path_to_file='datanew_median.csv',strategy="most-frequent",headers=True)
imm_api_most_freq.print_table(imm_api_most_freq.data)
# Transform data by replacing missing values with most-frequent
# and selecting only column Purchased
replaced_data = imm_api_most_freq.transform(columns_by_header_name=["Purchased"])
imm_api_most_freq.print_table(replaced_data)
# Write new table to csv file
imm_api_most_freq.dump_data_to_csv('datanew_most_frequent.csv', replaced_data,
                         use_header_from_data=True, override=True)
```

#### Integrating with pandas,numpy:

```python
from imputerApi import ImputerApi
import numpy as np
import pandas as pd
# Read csv data as Pandas DataFrame
df = pd.read_csv('data.csv')
# Convert Pandas Dataframe to Numpy Array
arr = df.values
# Convert Numpy Array to Python List 
arr_list = arr.tolist()
# Pass List to ImputerApi in parameter matrix_2D ; headers = False since it is 2D array
imputer_api = ImputerApi(matrix_2D=arr_list,strategy="mean",headers=False)
# Replacing missing value 'np.nan' with mean
replaced_data = imputer_api.transform(column_indexes=[1,2],missing_value=np.nan)
# Print to console
imputer_api.print_table(arr_2D=replaced_data)
# Write data to CSV file2
imputer_api.dump_data_to_csv("data2.csv",replaced_data,override=True)

```

#### Using K-Nearest Neighbors

```python
# Loading Data
imputer_api= ImputerApi("data.csv",strategy="knn",headers=True)
# Imputing Purchased Column containing Text Categorical Values 
# using knn technique and distance method 'Levenshtein'
replaced_data = imputer_api.transform(columns_by_header_name=["Purchased"],missing_value="",knn_method="levenshtein",knn_selection="most-frequent")
# Creating new instance of ImputerApi using replaced_data
imputer_api2 = ImputerApi(matrix_2D=replaced_data,strategy="knn",headers=False)
# Imputing colums 1 and 2 using knn and distance method 'Eucilidian'
replaced_data = imputer_api2.transform(column_indexes=[1,2],missing_value="",knn_method="Euclidian",knn_selection="median")
# Writing replaced data to file
imputer_api.dump_data_to_csv("data2.csv",replaced_data,override=True,use_header_from_data=True)
```
