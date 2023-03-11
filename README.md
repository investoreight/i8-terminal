# i8 Terminal: Modern Market Research powered by the Command-Line

[i8 terminal](https://www.i8terminal.io) is a modern python-based terminal application that gives you superior power and flexibility to understand and analyze the market. The interface is simple, efficient, and powerful: it's command-line!

i8 Terminal is backed by the [Investoreight Platform](https://www.investoreight.com) and currently covers major U.S. exchanges.

## Features and Highlights
- Prompt Market Insights and Analysis
- Custom Charting, Reporting, and Visualizations
- Powerful and Customizable Screening
- Easy-to-Use and Extendable
- Backed by the [Investoreight Platform](https://www.investoreight.com)

![i8 Terminal Features](https://www.i8terminal.io/img/gif/i8-terminal-demo.gif)

## i8 Terminal Commands
i8 Terminal offers some built-in commands to analyze and research the market. You can also create your own custom commands or extend the existing command. Find an overview of commands [here](https://i8terminal.io/#commands).

Check out the following video to see some more commands from i8 Terminal:

[![i8 Terminal Sample Commands](https://img.youtube.com/vi/NpOCqcb-RxY/0.jpg)](https://www.youtube.com/watch?v=NpOCqcb-RxY)


## Installing i8 Terminal
**Note**: i8 Terminal currently only supports Python 3.9+

If you have Python 3 installed, you can simply install the tool with Python pip:

```
pip install i8-terminal
```

We recommend installing i8 terminal in an isolated virtual environment. This can be done as follows:

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
On Windows, you can also install i8 Terminal using the Windows executable. Check [here](https://i8terminal.io/download) if you want to download the windows executable.


## How to Contribute i8 Terminal
The preferred workflow for contributing to i8 Terminal is to clone the
[GitHub repository](https://github.com/investoreight/i8-terminal), develop on a branch and make a Pull Request.

See [here](https://github.com/investoreight/i8-terminal/blob/main/CONTRIBUTING.md) for guidelines for contributors.

i8 Terminal is built on top of the [Investoreight Core API](https://github.com/investoreight/investor8-sdk).

## How to Run i8 Terminal
You can verify whether i8 Terminal is installed successfully by running i8 script:

```
i8
```

If you are using the application for the first time, you should first sign in. Run the following command, which will open a browser and redirect you to the investoreight platform to sign in (or sign up):

```
i8 user login
```

After a successful login, the most convenient way to use i8 terminal is to use its own shell:

```
i8 shell
```

You should now be able to run i8 commands. Check our [documentation](https://docs.i8terminal.io/) for more details.

## Documentation
Click [here](https://docs.i8terminal.io/) to find more details about the commands.
