
# Galaina

## Description
Within the course of the EU project Aggressotype, Machine2Learn BV developed a platform called Galaina to extract causal relationships from biological and medical databases that are in tabular format. Using the causal relationships from Galaina, we show that it is possible to derive subtypes, i.e., meaningful grouping of variables (here also called features) present in those databases. Galaina is a platform to read data, find causal associations, and generate a diagram that shows the causal relationships between features and subtypes. 

## Installation

### Python and R Path Settings
This part is common to all the operating systems.

#### Python

We assume that Python 3 is the default python interpreter. By running from the terminal the following command, all the required packages will be installed:
```bash
pip install -r requirements.txt
```

#### Local setup
The path to the `Rscript` executable is hard-coded in line 133 of file `config/config_writer.py`:
```python
            self.add_item('r_front_end', 'path_r_binary_command', '/usr/local/bin/Rscript')
```
Please replace the path to the `Rscript` file (which is the last string) according to your `R` installation.

### Linux (Ubuntu)

#### Terminal
Install v8 and some R packages

```bash
sudo apt install libv8-dev
sudo apt install r-bioc-rbgl r-cran-devtools r-cran-dplyr r-cran-shiny r-cran-ggplot2 r-cran-tidyr r-cran-caret r-cran-nnet r-cran-mvtnorm r-bioc-graph r-cran-gridextra r-cran-psych
```

#### R console

```r
install.packages(c("dagitty", "infotheo", "sbgcop"))
library(devtools)  # to use install_github
install_github("cran/BDgraph@2.44")  # Install version 2.44 of BDgraph
source("http://bioconductor.org/biocLite.R") 
biocLite("Rgraphviz")  # for visualizing causal discovery results (a graph) 
install.packages(c("latex2exp", "polycor", "pcalg", "gRain", "bnlearn", "ConfigParser", "stringi", "ggplotify"))
```


### MacOS 

#### Terminal
Install v8 via Homebrew
```bash
brew install v8@3.15
```

#### R console

```r
source("http://bioconductor.org/biocLite.R") 
biocLite("RBGL")
install.packages(c("devtools", "dplyr", "shiny", "ggplot2", "tidyr", "caret", "nnet"), dependencies=TRUE)
install.packages(c("mvtnorm"))
install.packages(c("dagitty", "infotheo", "sbgcop"))
library(devtools)  # to use install_github
install_github("cran/BDgraph@2.44")  # Install version 2.44 of BDgraph
source("http://bioconductor.org/biocLite.R") 
biocLite("Rgraphviz")  # for visualizing causal discovery results (a graph) 
```

## Usage

### Activation

1. In a terminal, execute the following command (Python 3 is the assumed python interpreter):
```python
python main.py
```
2. Now the internal web-server is active and it can be accessed by a web browser (preferably Chrome or Firefox). The default URL is `http://127.0.0.1:5000/`.
3. Sign in with the following credentials:
   * Username: `test`
   * Passowrwd: `test12345`
4. Upload the data and factor model files, edit the configurations accordingly, and run.

### File formats
#### Data
Data must be privided as a CSV file

#### Factor models
We assume that each variable has one and only one factor with non-zero loading. 
    <!-- Variable_value = Loading_matrix(Variable, Factor) * Factor_value -->

Factor models are provided via a CSV file. The variables must be indicated with the column names of the input data file. 
A variable can be a factor only if no other variables have it as a factor.
The factor model file must satisfy one of the following formats:
1. Factor Loading Matrix
    CSV file s.t. each cell contain the factor loading for the related variable/factor combination.
    <!-- `cell_value = Loading_matrix(Variable, Factor)` -->
    First must contain the string `Variable`

    Example:

    | *Variable* | Factor01 | Factor02 | Factor02 | ... |
    | -------- | --------- | --------- | --------- | --- |
    | Var01   | 0.5       | 0         | 0         | ... |
    | Var02   | 0.5       | 0         | 0         | ... |
    | Var03   | 0         | 0         | 0.25      | ... |

1. Factor Table
    CSV file with 3 columns listing the loading for each variable/factor combination. 
    Header is fixed and must containing the column names `Variable`, `Factor`, `Loading`.

    Example:
	
    | *Variable* | *Factor* | *Loading* |
    | --- | --- | --- |
    | Var01    | Factor01 | 0.5 |
    | Var02    | Factor01 | 0.5 |
    | Var03    | Factor02 | 0.25 |
    | ... | ... | ... |

1. Factor Variable List
    CSV file with 2 columns listing for each factor the associated linear combinations of variables.
    Header is fixed and must containing the column names `Variable`, `Factor`, `Loading`.

    Example:

    | *Factor*| *Variable_list* |
    | --- | --- |
    | Factor01 | Var01 + Var02 |
    | Factor02 | Var03 |
    | ... | ... |


## Acknowledgement and Disclaimer 

This project has received funding from the European Union's Seventh Framework Programme for research, technological development and demonstration under grant agreement no 602805.
The research leading to these results has received funding from the European Community's Seventh Framework Programme (FP7/2007-2013) under Grant Agreement no 278948.
This project is co-funded by the Ambient Assisted Living (AAL) Joint programme, by the german BMBF, the French ANR, the Austrian BMVIT.
