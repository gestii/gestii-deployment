git pull
pip install -r requirements.txt
echo %date%T%time% > update.lock
curl -X POST http://localhost:4567/message -d data=de
