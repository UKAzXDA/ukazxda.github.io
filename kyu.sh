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
sed -i 's/@/'"'"'; KYU/g' Kyufix
cat Kyufix >> Kyubey.sh
sudo rm Kyufix Kyulist
echo "
find ON7XELTE -type d -empty -delete
" >> Kyubey.sh
sudo bash Kyubey.sh
}
#===================================================#
# LS <DIRETORIO QUE SERÁ LISTADO>
# CODE <CODIGO QUE SERÁ EXECUTADO SOBRE A LISTA>
# KYU <CRIARA O EXECUTAVEL> <KYU "$LS" "$CODE" "$FIX"> $SUBE$FILE
#===================================================#
# ALVO "LIB" e "ETC"

mkdir ON7XELTE
chmod -R 777 *

LS="kernel/kernel"
FIX="kernel\/kernel"
CODE='
clear
echo "
  ======================================
  =   By UKAz-XDA  v7.0  1.0.0.0.0     =
  =  Script para comparar arquivos.    =
  =  Busca por arquivos subistituidos. =
  =    v7.0 Suporte para Subpastas     =
  ======================================
"
if [ "`cat kernel/kernel/$SUBE$FILE`" = "`cat kernel/kernelon/$SUBE$FILE`" ];
	then echo "IDENTICO: $SUBE$FILE"; sudo echo "IDENTICO: $SUBE$FILE" >> IDENTICO.txt
	else echo "NADAIDENTICO: $SUBE$FILE"; sudo mkdir -p ON7XELTE/$SUBE; sudo cp kernel/kernelon/$SUBE$FILE ON7XELTE/$SUBE$FILE; sudo echo "NADAIDENTICO: $SUBE$FILE" >> NADAIDENTICO.txt
fi
'
KYU "$LS" "$CODE" "$FIX"

