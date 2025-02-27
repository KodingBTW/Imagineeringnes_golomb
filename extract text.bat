:: Edit with config
:: Example file
echo "Imagineering NES games decompressor"
set romName="Barbie (USA).nes"
set outFile="script.bin"
set tblFile="decode.tbl"
Imagineering_golomb.py -d %romName% %outFile% %tblFile%
pause