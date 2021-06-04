#!/sbin/sh
#[=============================]#
#[       U K Λ z - X D Λ       ]#
#[=============================]#
#           My Kyubey.          #
#[=============================]#

interface="${1}"
updater_fd="${2}"
ui_print() {
	echo -en "ui_print ${1}\n" > /proc/self/fd/"${updater_fd}"
	echo -en "ui_print\n" > /proc/self/fd/"${updater_fd}"
}

mkdir -p /tmp/ukazxda/Kyubey
KYU=/tmp/ukazxda/Kyubey
KYUPROP=/tmp/ukazxda/Kyubey.prop
AROMA=/tmp/aroma;APPS=$AROMA/APPS.prop
CONFIG=$AROMA/CONFIG.prop;CUSTOM=$AROMA/CUSTOM.prop
OFICIAL=`awk -F= -v key="oficial" '$1==key {print $2}' $KYUPROP`
MAGIA1=$1;MAGIA2=$2;MAGIA3=$3
>> $KYUPROP

if [ $MAGIA1 = "set_prop" ]; then
prop=$3;arg=$4;concat="${prop}=";FILE=$2
	if grep -Fq $prop $FILE ; then
		sed -i "/$concat/c $prop=$arg" "$FILE"  
		else echo $prop=$arg >> $FILE
	fi
exit
fi

if [ $MAGIA3 = "check_device" ]; then
	if [ `getprop ro.boot.bootloader | grep 'G610'` ];  then echo SM-G610F > $KYU/device
	if [ `getprop ro.boot.bootloader | grep 'G610F'` ]; then echo SM-G610F > $KYU/device; fi
	if [ `getprop ro.boot.bootloader | grep 'G610M'` ]; then echo SM-G610M > $KYU/device; fi
	if [ `getprop ro.boot.bootloader | grep 'G610Y'` ]; then echo SM-G610Y > $KYU/device; fi
	if [ `getprop ro.boot.bootloader | grep 'G610L'` ]; then echo SM-G610L > $KYU/device; fi
	if [ `getprop ro.boot.bootloader | grep 'G610K'` ]; then echo SM-G610K > $KYU/device; fi
	if [ `getprop ro.boot.bootloader | grep 'G610S'` ]; then echo SM-G610S > $KYU/device; fi
	echo check_device=1 >> $KYUPROP; exit; fi; echo check_device=0 >> $KYUPROP
rm /tmp/ukazxda/kyubey.sh
exit
fi

if [ $MAGIA1 = "check_oficial" ]; then
	SYSROT=/system/system/etc/$OFICIAL
	SYSARM=/system/etc/$OFICIAL
	VENTRA=/vendor/etc/$OFICIAL
	SYSTEM=`awk -F= -v key="SYSTEM" '$1==key {print $2}' $CONFIG`
	VENDOR=`awk -F= -v key="VENDOR" '$1==key {print $2}' $CONFIG`
	KERNEL=`awk -F= -v key="KERNEL" '$1==key {print $2}' $CONFIG`
	echo 'SYSTEM=1' > $KYU/install_system.prop
	echo 'VENDOR=1' > $KYU/install_vendor.prop
	echo 'KERNEL=1' > $KYU/install_kernel.prop
	if [ -e $SYSARM ]; then
	echo SYSTEM=$SYSTEM > $KYU/install_system.prop
	echo VENDOR=$VENDOR > $KYU/install_vendor.prop
	echo KERNEL=$KERNEL > $KYU/install_kernel.prop
	echo system_oficial=1 >> $KYUPROP
	else if [ -e $SYSROT ]; then
	echo SYSTEM=$SYSTEM > $KYU/install_system.prop
	echo VENDOR=$VENDOR > $KYU/install_vendor.prop
	echo KERNEL=$KERNEL > $KYU/install_kernel.prop
	echo system_oficial=1 >> $KYUPROP
	else echo SYSTEM=1 > $KYU/install_system.prop
	echo KERNEL=1 > $KYU/install_kernel.prop
	echo aa=aa > $KYU/pre_wipe_data
	echo system_oficial=0 >> $KYUPROP
	fi; fi; if [ -e $VENTRA ]; then
	echo VENDOR=$VENDOR > $KYU/install_vendor.prop
	echo vendor_oficial=1 >> $KYUPROP
	else echo VENDOR=1 > $KYU/install_vendor.prop
	echo vendor_oficial=0 >> $KYUPROP
	fi
exit
fi

if [ $MAGIA1 = "wipe_check" ]; then
WIPEDATA=`awk -F= -v key="WIPEDATA" '$1==key {print $2}' $CONFIG`
	if [ -e /data/$OFICIAL ]; then
		rm $KYU/pre_wipe_data
		else echo aa=aa > $KYU/pre_wipe_data
	fi
	if [ -e $KYU/pre_wipe_data ]; then
		echo wipe_data=1 > $KYU/wipe_data.prop
		else echo wipe_data=$WIPEDATA > $KYU/wipe_data.prop
	fi
exit
fi

if [ $MAGIA1 = "certifique" ]; then
	echo 'AROMA:OFICIAL:'$OFICIAL'' > /system/system/etc/$OFICIAL
	echo 'AROMA:OFICIAL:'$OFICIAL'' > /system/etc/$OFICIAL
	echo 'AROMA:OFICIAL:'$OFICIAL'' > /data/$OFICIAL
	echo 'AROMA:OFICIAL:'$OFICIAL'' > /vendor/etc/$OFICIAL
exit
fi

if [ $MAGIA1 = "check_rom" ]; then
SYSTEM=`awk -F= -v key="system_check" '$1==key {print $2}' $KYUPROP`
VENDOR=`awk -F= -v key="vendor_check" '$1==key {print $2}' $KYUPROP`
	if [ -e /system/build.prop ]; then
	echo system_check=1 >> $KYUPROP
	else if [ -e /system/system/build.prop ]; then
	echo system_check=1 >> $KYUPROP
	else echo system_check=0 >> $KYUPROP
	fi; fi; if [ -e /vendor/build.prop ]; then
	echo vendor_check=1 >> $KYUPROP
	else echo vendor_check=0 >> $KYUPROP; fi
	FILE1=/system/system/build.prop
	FILE2=/system/build.prop
	prop=ro.product.model
	arg=`cat $KYU/device`
	concat="${prop}="
	#sed -i "/$concat/c $prop=$arg" "$FILE1" 
	#sed -i "/$concat/c $prop=$arg" "$FILE2" 
exit
fi

if [ $MAGIA1 = "wipe_data" ]; then
	cd /data
	for i in `ls -a` ; do
	if [ "$i" != "media" ] ; then
		if [ "$i" != "multiboot" ] ; then
			rm -fR "$i"
		fi
	fi
	done
	rm -fR /data/media/0/.*
	rm -fR /data/media/0/Android
	rm -fR /data/media/0/data
	rm -fR /data/media/obb/*
	synai
exit
fi

if [ $MAGIA3 = "check_vendor" ]; then
ZIP=/tmp/ukazxda/vendor.zip
cd /tmp
rm -rf META-INF spaget
unzip -o "$ZIP"
cd spaget
chmod 777 *
oldsize=/efs/spaget/syss

#   on7xelte
	syspart=21
	cacpart=22
	hidpart=23

if [ -z `./parted /dev/block/mmcblk0 p | grep VENDOR` ]
	then
	partition=0
	else
	partition=1
fi
if [ -z `cat /etc/recovery.fstab | grep VENDOR` ]
	then
	recovery=0
	else
	recovery=1
fi

if [ $partition = "1" ]; then
	if [ $recovery = "1" ]; then
		echo 'check_vendor=1' >> $KYUPROP
		exit
	fi
fi

echo 'check_vendor=0' >> $KYUPROP
FALSE=$KYU/vendor_false; if [ -e $FALSE ]; then exit;fi
ui_print "<@center><b><#4c1239>Kyubey</#></b>"
ui_print "<@center><b>@xda-developers</b></#>"
ui_print "<@center>Exynos7870 CreateVendor"
ui_print "<@center>Modded by Ananjaser1211"
ui_print "<@center>Coded by corsicanu"
ui_print " "
sleep 2

if [ -e $KYU/pt ]; then ui_print "<@center><#19441d>Criando partição do vendor...</#>"; fi
if [ -e $KYU/en ]; then ui_print "<@center><#19441d>Creating vendor partition...</#>"; fi
sleep 2

if [ -e $KYU/pt ]; then ui_print "<@center>Calculando partições originais"; fi
if [ -e $KYU/en ]; then ui_print "<@center>Calculating original partitions"; fi
	syss=`./parted /dev/block/mmcblk0 p | grep RESERVED2 | cut -c17-22 | tr 'MB' ' '`
	syse=`./parted /dev/block/mmcblk0 p | grep SYSTEM | cut -c17-22 | tr 'MB' ' '`
	cacs=`./parted /dev/block/mmcblk0 p | grep SYSTEM | cut -c17-22| tr 'MB' ' '`
	cace=`./parted /dev/block/mmcblk0 p | grep CACHE | cut -c17-22| tr 'MB' ' '`
	hids=`./parted /dev/block/mmcblk0 p | grep CACHE | cut -c17-22| tr 'MB' ' '`
	hide=`./parted /dev/block/mmcblk0 p | grep CP_DEBUG | cut -c7-16 | tr 'MB' ' '`

if [ $partition = "0" ]; then
if [ -e $KYU/pt ]; then ui_print "<@center>Fazendo backup de partições originais"; fi
if [ -e $KYU/en ]; then ui_print "<@center>Backing up original partitions"; fi

	mount /efs
	mkdir -p /efs/spaget
	echo $syss > /efs/spaget/syss
	echo $syse > /efs/spaget/syse
	echo $cacs > /efs/spaget/cacs
	echo $cace > /efs/spaget/cace
	echo $hids > /efs/spaget/hids
	echo $hide > /efs/spaget/hide
	umount /efs
	sync
fi

	umount /system
	umount /cache
	umount /hidden
	umount /vendor

if [ $partition = "0" ]; then
if [ -e $KYU/pt ]; then ui_print "<@center>patching partições"; fi
if [ -e $KYU/en ]; then ui_print "<@center>patching partitions"; fi
	cd /tmp/spaget

	# Load sizes
	syss=`./parted /dev/block/mmcblk0 p | grep RESERVED2 | cut -c17-22 | tr 'MB' ' '`
	syse=`./parted /dev/block/mmcblk0 p | grep SYSTEM | cut -c17-22 | tr 'MB' ' '`
	cacs=`./parted /dev/block/mmcblk0 p | grep SYSTEM | cut -c17-22| tr 'MB' ' '`
	cace=`./parted /dev/block/mmcblk0 p | grep CACHE | cut -c17-22| tr 'MB' ' '`
	hids=`./parted /dev/block/mmcblk0 p | grep CACHE | cut -c17-22| tr 'MB' ' '`
	hide=`./parted /dev/block/mmcblk0 p | grep CP_DEBUG | cut -c7-16 | tr 'MB' ' '`

	# Cut sizes
	syse=$(($syse - 150))	
	cacs=$syse	
	cace=$(($cacs + 20))	
	hids=$cace

	# Format partitions
	./parted /dev/block/mmcblk0 rm $syspart Yes -s	
	./parted /dev/block/mmcblk0 rm $cacpart Yes -s
	./parted /dev/block/mmcblk0 rm $hidpart Yes -s
	# Make System
	./parted /dev/block/mmcblk0 mkpart ext4 $syss $syse --s	
	./parted /dev/block/mmcblk0 name $syspart SYSTEM --s	
	# Make Cache	
	./parted /dev/block/mmcblk0 mkpart ext4 $cacs $cace --s	
	./parted /dev/block/mmcblk0 name $cacpart CACHE --s		
	# Make Vendor		
	./parted /dev/block/mmcblk0 mkpart ext4 $hids $hide --s	
	./parted /dev/block/mmcblk0 name $hidpart VENDOR --s		
	# Write disk label
	./parted /dev/block/mmcblk0 set $syspart msftdata on --s	
	./parted /dev/block/mmcblk0 set $cacpart msftdata on --s			
	./parted /dev/block/mmcblk0 set $hidpart msftdata on --s

	mke2fs -b 4096 -T ext4 /dev/block/mmcblk0p$syspart
	mke2fs -b 4096 -T ext4 /dev/block/mmcblk0p$cacpart
	mke2fs -b 4096 -T ext4 /dev/block/mmcblk0p$hidpart
fi
	if [ $recovery = "0" ]; then
		ui_print "<@center>patching recovery"
		sleep 5
	fi
	if [ $recovery = "0" ]; then
		cd /tmp/spaget
		unzip /tmp/spaget/spaget.zip META-INF/com/google/android/* -d /tmp/spaget
		chmod 755 META-INF/com/google/android/update-binary
		exec META-INF/com/google/android/update-binary "dummy" "0" /tmp/spaget/spaget.zip
	fi
sync
fi
