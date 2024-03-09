
# Global Walkie Talkie
### A Python-based 1-to-1 voice chat (Walkie-talkie style) with real-time translation on both ends

## Installation

1. Clone the repository:

   ```shell
   git clone https://github.com/aayushbatwara/GlobalWalkieTalkie.git
   ```

2. Create and activate a virtual environment:

   ```shell
   cd GlobalWalkieTalkie
   python3.10-or-above-executable -m venv myEnv
   source myEnv/bin/activate
   ```

3. Install the required dependencies using `pip`:

   ```shell
   pip install -r requirements.txt
   ```

## Usage

1. Run the app on one device:

   ```shell
   python main.py
   ```

2. Run the app on another device:

   ```shell
   python main.py
   ```
3. Enter each other's IP address and ports. 

   ```shell
   Enter threshold: 1000
   Enter IP Address: 192.168.0.11
   Working on port:  1392
   Write port: 1469
   ```
   ```shell
   Enter threshold: 1000
   Enter IP Address: 192.168.0.77
   Working on port:  1469
   Write port: 1392
   ```
4. Speak. Couple short sentences are optimal because they are long enough for language and context detection. 
