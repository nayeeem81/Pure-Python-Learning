NumPy (Numerical Python) is the foundational package for scientific computing in Python. It provides a highly efficient multidimensional array object (ndarray) and tools for working with these arrays. It is the core building block for almost all Python AI and Data Science libraries, including Pandas, Scikit-Learn, and PyTorch.
------------------------------
## Why Use NumPy?
Standard Python lists can store any object type, making them slow and memory-heavy. NumPy arrays are homogenous (all elements must be the same type) and stored contiguously in memory. This allows NumPy to perform mathematical operations on huge datasets up to 100x faster than standard Python loops using a concept called vectorization.
First, import the library (by convention, as np):

	import numpy as np

	------------------------------
## 1. Creating Arrays
	You can initialize arrays from Python lists or use built-in functions to generate structured data.

	# Create a 1D array from a listarr_1d = np.array([1, 2, 3, 4, 5])
	# Create a 2D array (Matrix)arr_2d = np.array([[1, 2, 3], [4, 5, 6]])
	# Create an array filled with zeroszeros = np.zeros((2, 3))  # 2 rows, 3 columns
	# Create an array filled with onesones = np.ones((3, 3))
	# Create an array with a range of numbers (start, stop, step)range_arr = np.arange(0, 10, 2)  # [0, 2, 4, 6, 8]
	# Create evenly spaced numbers over a specified intervallinspace_arr = np.linspace(0, 1, 5)  # [0. , 0.25, 0.5 , 0.75, 1. ]

## 2. Inspecting Array Attributes
	Understanding the shape and type of your data is critical in AI applications.

	arr = np.array([[1, 2, 3], [4, 5, 6]])

	print(arr.ndim)   # Dimensions (Outputs: 2)
	print(arr.shape)  # Shape as a tuple (Outputs: (2, 3) -> 2 rows, 3 columns)
	print(arr.size)   # Total number of elements (Outputs: 6)
	print(arr.dtype)  # Data type of elements (Outputs: int64 or int32)

## 3. Array Indexing and Slicing
	Accessing data in NumPy is similar to Python lists but extends to multiple dimensions using a [row, column] syntax.

	matrix = np.array([,
	 ,
		[70, 80, 90]
	])
	# Get a specific element: [row, col] (0-indexed)
	print(matrix[1, 2])  # Outputs: 60 (Row 1, Column 2)
	# Slicing: [row_start:row_end, col_start:col_end]# Get the first two rows and the last two columns
	print(matrix[0:2, 1:3])# Outputs:# [[20, 30],#]
	# Get all rows, but only the first column
	print(matrix[:, 0])  # Outputs: [10, 40, 70]

## 4. Vectorized Math Operations
Instead of using loops to alter data, you apply the mathematical operation directly to the array.

	a = np.array([1, 2, 3])b = np.array([4, 5, 6])
	# Element-wise operations
	print(a + b)  # [5, 7, 9]
	print(a * b)  # [4, 10, 18]
	print(a ** 2) # [1, 4, 9]
	# Matrix multiplication (Dot product)matrix_a = np.array([[1, 2], [3, 4]])matrix_b = np.array([[5, 6], [7, 8]])result = np.dot(matrix_a, matrix_b)  # or matrix_a @ matrix_b

## 5. Reshaping Arrays
	In Deep Learning, you frequently need to rewrite the structural layout of images or datasets without altering the underlying data.

	flat_arr = np.array([1, 2, 3, 4, 5, 6])
	# Reshape 1D array into a 2D array (2 rows, 3 columns)grid = flat_arr.reshape(2, 3)
	print(grid)# [[1, 2, 3],#]
	# Flatten it back to 1Dflat_again = grid.flatten()

## 6. Statistical Functions
NumPy provides rapid computational methods over the whole array or specific axes (axis=0 for columns, axis=1 for rows).

	stats_arr = np.array([[1, 2], [3, 4]])

	print(np.max(stats_arr))        # Highest value: 4
	print(np.mean(stats_arr))       # Average: 2.5
	print(np.sum(stats_arr))        # Total sum: 10
	print(np.sum(stats_arr, axis=0)) # Column sums: [4, 6]

## 7. Filtering (Boolean Indexing)
You can search or filter elements based on conditions instantaneously.

	data = np.array([12, 45, 7, 23, 89, 14])
	# Create a boolean mask conditionmask = data > 20  # [False, True, False, True, True, False]
	# Filter data using the maskfiltered_data = data[mask]
	print(filtered_data)  # Outputs: [45, 23, 89]

------------------------------
Would you like to try a few interactive coding exercises using these NumPy operations, or should we move on to learning Pandas for handling spreadsheets and data tables?






