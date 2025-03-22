------PSE.END::LOG - [Endurance Logging]-------------

END::LOG is a CLI that safely encrypts and stores mission logs, with online/offline functionality, in JSON and Markdown format.
The end objective is to safely store documentation of mission logs or journals for active mission monitoring or posterity.


------Setup Instructions-----------------------------

```bash
git clone https://github.com/prismschism/PSE.END-LOG
cd PSE.END-LOG
python -m venv .venv
source .venv/bin/activate      # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py