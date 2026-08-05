# SmileyMath

A minimalist tool for kids to practice elementary math operations. 
The only gadget is the printing of an ascii art picture from one of the following themes: animals, Star Wars, Harry Potter.

## Challenge Categories

* Adding two numbers
* Subtracting two numbers
* Complementing to 10
* Multiplying
* Dividing (with or without remainder)
* Adding times
* Subtracting times

You can define the number of challenges as well as a maximum time to respond.

## Usage

To start the GUI interface:

```
smileymath
```

To start a predefined program:

```
smileymath --ce1
smileymath --cm1
```

## Installation

### From PyPI

```bash
pip3 install smileymath
```

> **Note:** On modern Linux distributions (Debian 12+, Ubuntu 23.04+, Fedora), installing with `pip` outside a virtual environment may be blocked. Use one of the methods below instead.

### Using pipx (recommended)

[pipx](https://pipx.pypa.io/) installs Python CLI tools in isolated environments while making the command available system-wide:

```bash
# Install pipx if not already available
sudo apt install pipx   # Debian/Ubuntu
pipx ensurepath

# Install smileymath
pipx install smileymath
```

### From source (system-wide)

Clone the repository and run the install script:

```bash
git clone https://gitlab.com/mglt/smileymath.git
cd smileymath
./install.sh
```

This creates a dedicated virtual environment in `/opt/smileymath` and symlinks the `smileymath` command to `/usr/local/bin/` so it's available for all users. No manual venv activation required.

To uninstall:

```bash
./uninstall.sh
```

### From source (development)

```bash
git clone https://gitlab.com/mglt/smileymath.git
cd smileymath
python3 -m venv venv
source venv/bin/activate
pip install -e .
```
