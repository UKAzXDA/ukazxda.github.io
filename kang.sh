#!/bin/bash
echo "
  ======================================
  =   By UKAz-XDA  v7.0  1.0.0.0.0     =
  =  Script para comparar arquivos.    =
  =  Busca por arquivos subistituidos. =
  =    v7.0 Suporte para Subpastas     =
  ======================================
"
sudo chmod -R 777 *
function KYU() {
> Kyubey.sh; sudo chmod 777 Kyubey.sh
> Kyulist; sudo chmod 777 Kyulist
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

	listar_arquivos() {
		local diretorio="$1"
		local subdiretorio="$2"
		for item in "$diretorio"/*; do
			if [ -d "$item" ]; then
				listar_arquivos "$item" "$subdiretorio/${item##*/}"
			elif [ -f "$item" ]; then
				echo "SUBE=\"$subdiretorio\"; FILE=\"${item##*/}\"; KYU" >> Kyulist
				sed -i s/'SUBE="\/'/'SUBE="'/g Kyulist
			fi
		done
	}
	listar_arquivos "$LISTA" ""
	cat Kyulist >> Kyubey.sh
	sudo rm Kyulist
	echo "find $3 -type d -empty -delete" >> Kyubey.sh
	sudo bash Kyubey.sh
}
#===================================================#
# LISTA <DIRETORIO QUE SERÁ LISTADO>
# CODE <CODIGO QUE SERÁ EXECUTADO SOBRE A LISTA>
# KYU <CRIARA O EXECUTAVEL> <KYU "$LS" "$CODE"
# DIRETORIO <$SUBE> || ARQUIVO <$FILE>
#===================================================#

sudo rm -rf KANG-BUILD
sudo mkdir -p STOCK/KYUBEY
sudo mkdir -p CUSTOM/KYUBEY
sudo mkdir -p KANG-BUILD/CUSTOM-BUILD
sudo mkdir -p KANG-BUILD/DEBLOAT-STOCK
sudo mkdir -p KANG-BUILD/ADICIONADO-CUSTOM

#===================================================#
LISTA="STOCK/KYUBEY"
LIMPE="KANG-BUILD"
CODE='
clear
echo "
  ======================================
  =   By UKAz-XDA  v7.0  1.0.0.0.0     =
  =  Script para comparar arquivos.    =
  =  Busca por arquivos subistituidos. =
  =    v7.0 Suporte para Subpastas     =
  ======================================
  PROCESSANDO.. $SUBE/$FILE
"
if [ -e "CUSTOM/KYUBEY/$SUBE/$FILE" ]; then
	echo
else
	sudo echo "rm STOCK/KYUBEY/$SUBE/$FILE" >> KANG-BUILD/Debloat.sh
	sudo mkdir -p KANG-BUILD/DEBLOAT-STOCK/$SUBE
	sudo cp STOCK/KYUBEY/$SUBE/$FILE KANG-BUILD/DEBLOAT-STOCK/$SUBE/$FILE
fi
'
KYU "$LISTA" "$CODE" "$LIMPE"
#===================================================#
LISTA="CUSTOM/KYUBEY"
LIMPE="KANG-BUILD"
CODE='
clear
echo "
  ======================================
  =   By UKAz-XDA  v7.0  1.0.0.0.0     =
  =  Script para comparar arquivos.    =
  =  Busca por arquivos subistituidos. =
  =    v7.0 Suporte para Subpastas     =
  ======================================
  PROCESSANDO.. $SUBE/$FILE
"
if [ -e "STOCK/KYUBEY/$SUBE/$FILE" ]; then
	echo
else
	sudo echo "ADICIONADO: CUSTOM/KYUBEY/$SUBE/$FILE" >> KANG-BUILD/Adicionado.txt
	sudo sudo mkdir -p KANG-BUILD/ADICIONADO-CUSTOM/$SUBE
	sudo cp CUSTOM/KYUBEY/$SUBE/$FILE KANG-BUILD/ADICIONADO-CUSTOM/$SUBE/$FILE
fi
'
KYU "$LISTA" "$CODE" "$LIMPE"
#===================================================#
LISTA="STOCK/KYUBEY"
LIMPE="KANG-BUILD"
CODE='
clear
echo "
  ======================================
  =   By UKAz-XDA  v7.0  1.0.0.0.0     =
  =  Script para comparar arquivos.    =
  =  Busca por arquivos subistituidos. =
  =    v7.0 Suporte para Subpastas     =
  ======================================
  PROCESSANDO.. $SUBE/$FILE
"
if cmp -s "STOCK/KYUBEY/$SUBE/$FILE" "CUSTOM/KYUBEY/$SUBE/$FILE"; then
    echo
else
	sudo mkdir -p KANG-BUILD/CUSTOM-BUILD/$SUBE
	sudo cp CUSTOM/KYUBEY/$SUBE/$FILE KANG-BUILD/CUSTOM-BUILD/$SUBE/$FILE
fi
'
KYU "$LISTA" "$CODE" "$LIMPE"
#===================================================#
