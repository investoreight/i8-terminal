# i8 Terminal: Modern Market Research with the Power of Command-Line

[i8 terminal](https://www.i8terminal.io) is a modern python-based terminal application that gives you a superior power and flexibility to understand and analyze the market. The interface is simple, efficient, and powerful: it's command-line!

i8 Terminal is backed by the [Investoreight Platform](https://www.investoreight.com) and currently covers major U.S. exchanges.

## Installing i8 Terminal
**Note**: i8 Terminal currenly only supports Python 3.9+

If you have Python 3 installed, you can simply install the tool with Python pip:

```
pip install i8-terminal
```

We recommend to install i8 terminal in an isolated virtual environment. This can be done as follows:

#### On Mac OS or Linux:

```
python3 -m venv .venv 
source .venv/bin/activate 
pip install i8-terminal
```

#### On Windows:

```
python3 -m venv .venv 
source .venv/Script/activate 
pip install i8-terminal
```

### Install i8 Terminal using the Windows Installer
On Windows you can also install i8 Terminal using the windows executable. Check [here](https://i8terminal.io/download) if you want to download the windows executable.


## How to Run i8 Terminal
You can verify whether i8 Terminal is installed succefully by running i8 script:

```
i8
```

If you are using the application for the first time, you should first sign in. Run the following command, which will open a browser and redirects you to the investoreight platform to sing in (or sign up):

```
i8 user login
```

After a succesful login, the most convenient way to use i8 terminal is to use its own shell:

```
i8 shell
```

You should now be able to run i8 commands. Check our [documentation](https://docs.i8terminal.io/) for more details.

## Documentation
Click [here](https://docs.i8terminal.io/) to find more details about the commands.
