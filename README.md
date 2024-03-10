# Virtual Bot

This is a simple virtual robot made with PyGame and OpenAI.

## Setup
To install the required libraries, run: `pip3 install -r requirements.txt`.
Input your OpenAI api key as the first value of the `settings.env`, and change the rest as you like
And then, simply run the main script (`python3 main.py`)

## Use
When you run the script, a window will open with 2 eyeballs. The position of the iris will depend on the position of the recognized face (it watches you and you will never escape from it).
When the eyeballs appear, you may speak into your microphone, the input and the output will be printed onto the terminal. It will also speak the output of ChatGPT aloud.
![Screenshot of window](./.github/images/Screenshot%202024-03-10%20at%2015.47.58.png)
![Screenshot of window](./.github/images/Screenshot%202024-03-10%20at%2015.48.04.png)

## License
This project is licensed under the GPL-3.0 license.
Read more [here](LICENSE)