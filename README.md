# MTG AI
A site for creating MTG cards from a neural network AI. This assumes you have a working neural net installation from [github](https://github.com/billzorn/mtg-rnn). Reports so far show that this is only working in linux,

## Install
Installation instructions assume you have a working understanding of installing software in linux. Depending on your distribution some of these dependencies may already be installed.
1. Install Python 3
2. Install Pip
3. Install git
4. Clone this repository: `git clone https://github.com/croxis/mtgai.git`
5. (Optional) Create and activate a python 3 virtual environment
6. Change directory: `cd mtgai`
7. Install dependencies: `pip install -r requirements.txt` You may need to use sudo if not using a virtual environment.
8. Copy sample_hs_v3.1.lua in the lua directory to where the card generator directory is

## Configure
1. Open config.py with your favorite editor.
2. Change the SECRET_KEY to text of your choice.
3. Change SNAPSHOTS_PATH to point to the directory you store your snapshots in. Subdirectory names can be used to group snapshot types together.
4. Change GENERATOR_PATH to point to the directory that houses sample.lua, train.lua, and the sample_hs_v2.lua file you just moves

## Test
1. Run the server: `python3 manage.py run`
2. Point your favorite web browser to `http://localhost:5000` and cry over the sad state of the site.

