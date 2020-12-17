# Alva
## Installation
### Prerequisites
Python version >=3.7.4 installed. Check can be performed by running ```python --version``` in terminal.

### Dependencies
To be able to develop the Django application, the dependencies from the requirements.txt need to be installed either on the system installation of Python, or on a virtual environment:

#### ---- On system path
```bash
pip install -r requirements.txt
```

#### ---- On virtual environment - See [this](https://docs.python.org/3/tutorial/venv.html/) article - <b><u>If you choose this approach don't forget to add the env folder to the gitignore!</u></b>
1. Set up venv. It is recommended that it is in the root of the project.
```bash
python -m venv <env_name>
```
2. Activate the virtual environment. <b><u>Do this from the Windows Command Prompt!</u></b>
```bash
<env_name>\Scripts\activate.bat
```
3. Confirm that env is active. Bash should look like this:
```bash
(<env_name>) C:\Users\<user>\...  Alternatively, run:
```
```bash
where python  And you should see the path to the env .exe
```
4. Install dependencies
```bash
pip install -r requirements.txt
```

## Django commands
### Running local server
To run the emulated local server, execute this command in the terminal:
```bash
python manage.py runserver
```
It defaults to localhost with port 8000 - http://localhost:8000

## VS Code setting for those developing with it
### Linting
Once the dependencies have been installed from the <i><b>requirements.txt</b></i>, you can set up flake 8 from user preferences which are opened by pressing <i>Ctrl+Shift+P</i>. In them, add:
```json
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
```
If you do not use VS Code and still want to utilize flake8, I suggest researching your IDE to enable the support. Alternatively, to check for style issues with a file or a whole python directory, simply run the following command from the terminal:
```bash
flake8 <filename> or flake8 <directory>
```
This will bring up the changes which are advised to be made to the code so that we can follow the same stylistic conventions.
### Python interpreter
To select the Python interpreter, hti <i>Ctrl+Shift+P</i> and write <i>Select Interpreter</i>. There you will see the different Python .exe locations on your machine. You can choose the default system installation or a virtual environment that you have created. <b><u>Important: You need the Python extension from VS Code to make this work</u></b>.
### Debugging
Debugging can be done in the terminal by setting break points in the code, like this:
```python
import pdb

... Some code
pdb.set_trace()
...
```
For pdb commands, see - https://docs.python.org/3/library/pdb.html

Alternatively, the VS Code Python extension offers a way to debug from the IDE. For setting this up, see: https://code.visualstudio.com/docs/python/debugging

## Contributing
For each new functionality, the creation of a branch is advised. Once the features are done, open a pull request which will be reviewed before the branch is merged with master. Don't forget to pull.
