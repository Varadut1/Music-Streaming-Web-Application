#! /bin/bash
echo "======================================================================="
echo "run"
echo "------------------------------------------------------------------------"
if [ -d "venv" ];
then 
	echo "Enabling venv"
else
	echo "No venv run setup"
	exit N
fi

#Activate
. venv/Scripts/activate
export ENV=development
python main.py
deactivate