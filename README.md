# assessment-crivera
The below text contains the README writeup specified in the assignment.

### [Link to the Github repo source code](https://github.com/crivera2013/assessment-crivera)


### README: How to run the code

If you wish to run this code locally, please run the following the command line code:


1. `git clone https://github.com/crivera2013/assessment-crivera.git` to download the project to your local machine. (This assumes you have `git` installed)
2. `pipx install poetry` to install `poetry` which is a python virtual enviroment manager
3. `poetry install` to install all the python library dependencies
4. `poetry run python database_creation.py` to create the `pharo_assessment.db` database if you do not already have it
5. `poetry run python dv01_calc.py` to calculate the dv01 values and insert them into the database
6. `poetry run python main.py` which will activate the webserver application
7. Open a web browser and visit the locally run app on http://127.0.0.1:8050/


### README: File Explanation
- `database_creation.py`: code for desiging the schema, creating the database, and inserting data into the database
- `Dockerfile`: a shell script for instructing Google Cloud on how the docker container of this code runs
- `dv01_calc.py`: code for accessing the DB, calculating the daily DV01 of all the bonds, and inserting that calculated data back into the DB
- `main.py`: the entry point that creates the web application server as well as the top framework of HTML code
- `pharo_assessment.db`: the SQLite database that is accessed when displaying data on the web application
- `poetry.lock`: contains the specific compatible versions of all the dependencies and sub-dependencies of the code.
- `pyproject.toml`: a configuration file showing the top level dependencies meant to manage the python environment for this project so that it works on any machine.
- `tox.ini`: a configuration file, currently only used for configuring the linting rules of my IDE but can also be extended as a run script for automated testing of the codebase and stipulating requirements (code coverage %, linting) for what is considered a successful test of the code in a continous delivery software development environment.
- `refinitive_data/`: a folder containing the yield and bond characteristic data that is inserted in the SQL DB.
- `webpage/calculations.py`: a file for calculating the Value at Risk (VaR) values as well as portfolio level values
- `webpage/frontend.py`: python code specifying the HTML and javascript webpage (buttons, sliders, text, graphs, etc)
- `webpage/callbacks.py`: python code specifying what happens when a user interacts with the HTML: querying data, manipulating data, and then sending data to the webpage.
- `requirements.txt`: Google Cloud does not play nicely with `Poetry` yet so I also need a copy of the dependencies stored in `requirements.txt`

### README: Python Library Dependencies

All libraries used in this project were selected because they are scalable solutions and/or required in a professional setting.  That this application is running in a cloud environment and not on a local computer is testament to this fact.

For a list of the core dependencies, you can observe them in the file `pyproject.toml`

For a far more detailed list of the dependencies, sub-dependencies and specific versions used, you can take a look at the file `poetry.lock`.

I am going to list the main python dependencies specified in `pyproject.toml` and explain their uses.

- `Dash` is a web framework abstraction that enables a Python developer to write a JavaScript React frontend website with a Python Flask backend web server in a single file.  It also provides easier integration with `Plotly` a graphing library that is itself an abstraction of `D3.js`, the graphing library used by the New York Times for all of its interactive charts.  As such `Dash` is a useful webapp for data visualization.  There are some issues with scaling `Dash` around security features which may require that the app be split into two (a JavaScript React frontend and Python webserver backend) which removes the easy abstraction layer, but would be a scalable, professional solution.
- `NumPy`: A Linear Algebra library for performing functions on data organized in array, matrix, or tensor form.  `NumPy` is fast, vectorized, compiled C code and the library is the keystone of all quantiative programming in Python
- `Pandas`: An extension built on top of `NumPy` that lets you manipulate data organized like Excel files.  A one-stop shop for data ingestion and manipulation (especially for dates and times), `Pandas` was created by a quant at AQR who now works at Two Sigma so it is a safe bet that `Pandas` can handle hedge fund use cases
- `SciPy`: A scientific computing library built ontop of the `numpy` stack filled with statistics and optimizer functions among other features.  This is a core library of the quantitative computing python stack.
- `SQLAlchemy`: an Object Relational Mapper (ORM) that is used to design database schemas, create databases, and use databases exclusively through application code (in this case, Python).  It provides an abstraction layer such that the programmer need not worry which SQL database product they are creating or connecting to as the ORM API is the same.
- `flake8`: a linting tool that grades the programmer on the readability of his code.  It is used for standardizing how code is written among teams and is considered a necessary piece for working in a professional softtware development environment
- `black`: a code autoformatter developed by Facebook for standardizing the formatting of code among teams of software developers.
- `isort`: a code autoformatter that specializes in standardizing the order of imports at the top of python files to improve code readability.
- `Gunicorn`: is the defacto HTTP web server for python code and therefore necessary component for any backend Python web server.  It is a core component of Python web frameworks like `Django` and `Flask`
- `openpyxl`: a library for parsing Microsoft Excel files in Python.
- `NumPy-financial`: a fork of `NumPy` containing some financial math functions that were pruned out of `NumPy` a few versions back.

### README: Data initially in CSV files?
The data was retrieved throught the Refinitiv DataScope API, which takes the data inputs you provides and produces a CSV file which you then later download. If part of this project was to assess my web API accessing and general web scraping skills.  I can go back and provide you code of those abilities: API access with `requests` and/or webscraping with `BeautifulSoup` (for data in HTML) and `Selenium` (for data produced through JavaScript).

### README: Assumptions Made

Due to a lack of time and access to the relevant data all bonds in this app are assumed to be US dollar-denominated vanilla bonds:
- fixed rate
- no embedded options
- no rate adjustments
- no swaps
- no FX data
- coupon payments follow a fixed, standard schedule

The 5 bonds chosen were strictly US treasuries or American corporate bonds because of their simplicity.

Because of time constraints, I had to choose between creating and launching an interactive web application or less reproducible code that could handle more complicated Fixed Income and derivatives products.

For more complicated products, I would have included the external library `QuantLib` which has functionality for pricing swaps, options, etc, and managing yield curves as well as for calculating metrics of more complicated bonds.

This project

- a graph showing the yield
- a graph showing the yield change
- a graph showing DV01
-