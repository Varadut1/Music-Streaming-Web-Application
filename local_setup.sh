#! /bin/bash
echo "========================================================="
echo "Virtual env setup."
echo "And libraries"
echo "---------------------------------------------------------"
if [ -d "venv" ];
then 
	echo "venv folder exists. Installing using pip"
else
	echo "creating venv and insall using pip."
	python -m venv venv
fi

#Activate venv
. venv/Scripts/activate

#upgrade pip
pip install --upgrade pip
pip install -r requirements.txt
#Done
deactivate