:: Edit with config
:: Example file
echo "Imagineering NES games compressor"
set romName="Barbie (USA).nes"
set outFile="script.bin"
set tblFile="encode.tbl"
:loop
	pause
	Imagineering_golomb.py -c %outFile% %romName% %tblFile%
goto :loop

