apt update
apt install software-properties-common -y
add-apt-repository ppa:deadsnakes/ppa -y
apt update
apt install python3.11 python3.11-venv python3.11-dev -y
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirementsVPS.txt
python main.py
