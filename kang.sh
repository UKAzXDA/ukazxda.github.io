#!/bin/bash
#========================#
# By UKAz-XDA 25/10/2023 #
#    (C) K Y U B E Y     #
#========================#

exec 2> /dev/null
clear
echo "
  ======================================
  =   By UKAz-XDA  v7.0  1.0.0.0.0     =
  =  Script para comparar arquivos.    =
  =  Busca por arquivos subistituidos. =
  =    v7.0 Suporte para Subpastas     =
  ======================================
"
function KYU() {
> Kyubey.sh; sudo chmod 777 Kyubey.sh
> Kyulist; sudo chmod 777 Kyulist
> Kyufix; sudo chmod 777 Kyufix
echo "#!/bin/bash
#========================#
# By UKAz-XDA 25/10/2023 #
#    (C) K Y U B E Y     #
#========================#
exec 2> /dev/null
function KYU() {
$2
}

#========================#
#          DATA          #
#========================#
" >> Kyubey.sh

ls -R -F -Z $1 >> Kyulist
awk '!/\?/ || !/\//' Kyulist >> Kyufix
sed -i 's/'$3'\//SUBE='"'"'/g' Kyufix
sed -i 's/:/\/'"'"'/g' Kyufix
sed -i '1d' Kyufix
sed -i 's/? /FILE='"'"'/g' Kyufix
sed -i 's/*/'"'"'; KYU/g' Kyufix
# sed -i 's/@/'"'"'; KYU/g' Kyufix
cat Kyufix >> Kyubey.sh
sudo rm Kyufix Kyulist
echo "
find KANG-BUILD -type d -empty -delete
" >> Kyubey.sh
sudo bash Kyubey.sh
}
#===================================================#
# LS <DIRETORIO QUE SERÁ LISTADO>
# CODE <CODIGO QUE SERÁ EXECUTADO SOBRE A LISTA>
# KYU <CRIARA O EXECUTAVEL> <KYU "$LS" "$CODE" "$FIX"> $SUBE$FILE
#===================================================#

sudo mkdir -p STOCK/KYUBEY
sudo mkdir -p CUSTOM/KYUBEY
sudo mkdir -p KANG-BUILD/CUSTOM-BUILD
sudo mkdir -p KANG-BUILD/DEBLOAT-STOCK
sudo mkdir -p KANG-BUILD/ADICIONADO-CUSTOM

#===================================================#
LS="STOCK/KYUBEY"
FIX="STOCK\/KYUBEY"
CODE='
clear
if [ -e "CUSTOM/KYUBEY/$SUBE$FILE" ]; then
	echo
else
	sudo echo "rm STOCK/KYUBEY/$SUBE$FILE" >> KANG-BUILD/CUSTOM-BUILD/Debloat.sh
	sudo mkdir -p KANG-BUILD/DEBLOAT-STOCK/$SUBE
	sudo cp STOCK/KYUBEY/$SUBE$FILE KANG-BUILD/DEBLOAT-STOCK/$SUBE$FILE
fi
'
KYU "$LS" "$CODE" "$FIX"
#===================================================#
LS="CUSTOM/KYUBEY"
FIX="CUSTOM\/KYUBEY"
CODE='
clear
if [ -e "STOCK/KYUBEY/$SUBE$FILE" ]; then
	echo
else
	sudo echo "ADICIONADO: CUSTOM/KYUBEY/$SUBE$FILE" >> KANG-BUILD/CUSTOM-BUILD/Adicionado.txt
	sudo sudo mkdir -p KANG-BUILD/ADICIONADO-CUSTOM/$SUBE
	sudo cp CUSTOM/KYUBEY/$SUBE$FILE KANG-BUILD/ADICIONADO-CUSTOM/$SUBE$FILE
fi
'
KYU "$LS" "$CODE" "$FIX"
#===================================================#
LS="STOCK/KYUBEY"
FIX="STOCK\/KYUBEY"
CODE='
clear
if cmp -s "STOCK/KYUBEY/$SUBE$FILE" "CUSTOM/KYUBEY/$SUBE$FILE"; then
    echo
else
	sudo mkdir -p KANG-BUILD/CUSTOM-BUILD/$SUBE
	sudo cp CUSTOM/KYUBEY/$SUBE$FILE KANG-BUILD/CUSTOM-BUILD/$SUBE$FILE
fi
'
KYU "$LS" "$CODE" "$FIX"
#===================================================#
