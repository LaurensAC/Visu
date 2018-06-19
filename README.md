# JBI100 (2017-4) Visualization

This is an implementation of visualization concepts. We focus on one specific
 illustrative scenario about designing and implementing interactive adjacency matrix visualizations with a focus on the comparison of eye movement data. 

### Prerequisites

This project requires an installation of Python 3.5.x or higher.

The preferred setup includes the creation and activation of a virtual 
environment, because you will have to install a lot of dependencies.

If needed, confirm your version with the following command:
```
python3 -V
```

### Installing

Please note the first two steps are optional.

1. Create a virtual environment by executing the command venv:

```
python3 -m venv /path/to/new/virtual/environment
```

2. Activate it:

| Platform | Shell | Command to activate virtual environment |
| -------- | ----- | --------------------------------------- |
| Posix | bash/zsh | $ source <venv>/bin/activate | 
| | fish | $ . <venv>/bin/activate.fish |
| | csh/tcsh | $ source <venv>/bin/activate.csh |
| Windows | cmd.exe | C:\> <venv>\Scripts\activate.bat |
| |PowerShell | PS C:\> <venv>\Scripts\Activate.ps1 |

3. Install the new standard of python distribution:

```
pip3 install wheel
```

And the other requirements:

```
pip3 install -r requirements.txt
```

Check if the following command lists the same packages that can be found in 
'requirements.txt'.

```
pip freeze
```

## Deployment

Navigate to the folder 'app_path' and run the application:

```
bokeh serve monolith.py
```

## Usage



## Built With

* [Bokeh](https://bokeh.pydata.org/en/latest/) - The visualization framework 
used

* [More stuff](https://canvas.tue.nl) - built with more stuff

## Authors

* s numbers and names

