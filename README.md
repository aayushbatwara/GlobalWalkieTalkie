
# Global Walkie Talkie
### A Python-based 1-to-1 voice chat (Walkie-talkie style) with real-time translation on both ends

## Installation

1. Clone the repository:

   ```shell
   git clone https://github.com/aayushbatwara/GlobalWalkieTalkie.git
   ```

2. Create and activate a virtual environment:

   ```shell
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required dependencies using `pip`:

   ```shell
   pip install -r requirements.txt
   ```

## Usage

1. Make sure the virtual environment is activated:

   ```shell
   source venv/bin/activate
   ```

2. Run the app on one shell:

   ```shell
   python3 main.py
   ```

3. Run the app on another shell:

   ```shell
   python3 main.py
   ```
4. On one shell enter the port 2222

   ```shell
   Working on port:  1392
   Write port: 2222
   ```
5. On the other shell enter the port of the first shell

   ```shell
   Working on port:  1469
   Write port: 1392
   ```
6. Say 'Hello World' for the first message
7. Speak subsequent message. Couple short sentences are optimal because they are long enough for language and context detection. 