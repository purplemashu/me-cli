apt update -y && apt upgrade -y
apt install git -y
git clone https://github.com/arivpnstores/me-cli
cd me-cli
apt install -y python3 python3-pip
apt install -y python3-pil python3-pil.imagetk
apt install software-properties-common -y
add-apt-repository ppa:deadsnakes/ppa -y
apt install python3.11 python3.11-venv python3.11-dev -y
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirementsVPS.txt
python main.py
