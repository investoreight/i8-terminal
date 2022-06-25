Getting Started
===============

Introduction[](#introduction)
-----------------------------

i8 terminal is a modern python-based terminal application that gives you superior power and flexibility to understand and analyze the market. The interface is simple, efficient, and powerful: it's command-line!

**i8 Terminal is open-source and backed by the Investoreight Platform and currently covers major U.S. exchanges.**

Table of Contents
-----------------

*   [Introduction](#introduction)
*   [Installation](#installation)
    *   [Binary Installer](#binary-installer)
    *   [Installing with Python pip](#installing-with-python-pip)
    *   [Running from Code](#running-from-code)
*   [How to Run I8 Terminal](#how-to-run-i8-terminal)
*   [Sign Up / Sign In to the i8 Terminal Server](#signup-signin-to-the-i8-terminal-server)
*   [Subscription Plans](#subscription-plans)
*   [Your First Command](#your-first-command)

* * *

Installation[](#installation)
---------------------------------------------------------------

The I8 Terminal can be directly installed on your computer via our installation program. Within this section, you are guided through the installation process. If you are a developer, please have a look [here](https://https://github.com/investoreight/i8-terminal). If you struggle with the installation process, please visit our [contact page](https://www.i8terminal.io/contact).

### Binary Installer[](#binary-installer)

The process starts by downloading the installer, see below for how to download the most recent release:

1.  Go to [the i8terminal.io website download page](https://www.i8terminal.io/download)
2.  Click on the `Download For Windows` button in the Download i8 Terminal section

When the file is downloaded, use the following steps to run the I8 Terminal:

**Step 1: Double-click the `.msi` file that got downloaded to your `Downloads` folder**

You will most likely receive the error below stating “Windows protected your PC”. This is because the installer is still in the beta phase, and the team has not yet requested verification from Windows.

[![windows_protected_your_pc](https://www.investoreight.com/media/i8terminal-binaryinstaller-step1.png)](https://www.investoreight.com/media/i8terminal-binaryinstaller-step1.png)

**Step 2: Click on `More info` and select `Run anyway` to start the installation process**

Proceed by following the steps.

[![run_anyway](https://www.investoreight.com/media/i8terminal-binaryinstaller-step2.png)](https://www.investoreight.com/media/i8terminal-binaryinstaller-step2.png)

**Step 3: Select the destination directory you want to install I8 Terminal**

I8 Terminal is installed now!

[![select_destination](https://www.investoreight.com/media/i8terminal-binaryinstaller-step3.png)](https://www.investoreight.com/media/i8terminal-binaryinstaller-step3.png)

### Installing with Python pip[](#installing-with-python-pip)

If you have Python 3 installed, you can simply install the tool with Python pip:

    pip install i8-terminal

We recommend installing the I8 Terminal in an isolated virtual environment. This can be done as follows:

#### On Mac OS or Linux:

    python3 -m venv .venv
    source .venv/bin/activate
    pip install i8-terminal

#### On Windows (Using Git Bash):

    python3 -m venv .venv
    source .venv/Scripts/activate
    pip install i8-terminal

#### On Windows (Using Command Prompt or PowerShell):

    python3 -m venv .venv
    .venv\\Scripts\\activate
    pip install i8-terminal

### Running from Code[](#running-from-code)

The process starts by cloning the code, see below for how to run the terminal from the code:

**Step 1: Clone the repo**

    git clone git@github.com:investoreight/i8-terminal.git

**Step 2: Go to the directory**

    cd i8-terminal

**Step 3: Activate the isolated virtual environment**

#### Using Git Bash:

    python3 -m venv .venv
    source .venv/Scripts/activate

#### Using Command Prompt or PowerShell:

    python3 -m venv .venv
    .venv\\Scripts\\activate

**Step 4: Install required libraries**

    pip install -r requirements.dev

**Step 5: Run commands and enjoy!**

    python -m i8-terminal.main shell

How to Run I8 Terminal[](#how-to-run-i8-terminal)
---------------------------------------------------------------

You can verify whether the I8 Terminal is installed successfully by running the i8 script:

    i8

If you are using the application for the first time, you should first sign in. Run the following command, which will open a browser and redirect you to the Investoreight platform to sign in (or sign up):

    i8 user login

After a successful login, the most convenient way to use the I8 terminal is to use its own shell:

    i8 shell

You should now be able to run i8 commands. Check our documentation for more details.

[Read the Docs](https://docs.i8terminal.io)

Sign Up / Sign In to the i8 Terminal Server[](#signup-signin-to-the-i8-terminal-server)
---------------------------------------------------------------

If you want to use the I8 Terminal you should first sign in. Within this section, you are guided through the sign-in process.

[![user-sign-in](https://www.investoreight.com/media/i8terminal-signin-gif.gif)](https://www.investoreight.com/media/i8terminal-signin-gif.gif)

Also, you can sign in using the terminal with your email and password:

[![user-sign-in-with-terminal](https://www.investoreight.com/media/i8terminal-signin-with-terminal-gif.gif)](https://www.investoreight.com/media/i8terminal-signin-with-terminal-gif.gif)

Subscription Plans[](#subscription-plans)
---------------------------------------------------------------

In Free Edition you will have full access to DOW 30 Stocks.

For more features please have a look [here](https://www.i8terminal.io/#pricing).

Your First Command[](#your-first-command)
---------------------------------------------------------------

If you want to list financial metrics of Microsoft you can use the I8 Terminal Financials list command:

    financials list --identifier MSFT

[![your_first_command](https://www.investoreight.com/media/i8terminal-your-first-command.png)](https://www.investoreight.com/media/i8terminal-your-first-command.png)

For I8 Terminal more sample commands, please watch this video:

[I8 Terminal Sample Commands](https://youtu.be/NpOCqcb-RxY)