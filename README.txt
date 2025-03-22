------PSE.END::LOG - [Endurance Logging]-------------

END::LOG is a CLI terminal that safely encrypts and stores mission logs, with online/offline functionality, in JSON and Markdown format.
The end objective is to safely store documentation of mission logs or journals for active mission monitoring or posterity.
The logging system is planned to adopt modular expansion, with the aim of supporting field tagging and other mission critical documentation.


------Tech Stack------------------------------------- 
END::LOG is a mission logging system built with Python, Textual, and Rich.



------Setup Instructions-----------------------------

```bash
git clone https://github.com/prismschism/PSE.END-LOG
cd PSE.END-LOG
python -m venv .venv
source .venv/bin/activate      # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py