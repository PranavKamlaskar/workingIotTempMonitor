in t2micro

sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip git -y
sudo apt install python3-venv -y
python3 -m venv venv  
source venv/bin/activate   

mkdir iot-temp-monitor && cd iot-temp-monitor

vim requirements.txt       <!---refer file-->
pip3 install -r requirements.txt

vim app.py                 <!---refer file-->

mkdir templates/index.html      <!---refer file-->

python3 app.py        <!---test-->

Open your browser to:
http://<EC2_PUBLIC_IP>:5000

DHT11 VCC → 3.3V
DHT11 GND → GND
DHT11 DATA → D4 (GPIO2)

<!---refer misc--->
https://chatgpt.com/share/68126194-6ac8-8005-aac2-21dc21553d01

sudo apt install screen -y
screen -S flask
python3 app.py



