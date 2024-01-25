#!/bin/bash

path_base=/opt/spr-100k-logs
path_zipped_log=${path_base}/SHC_INB_LOG_inspur/SHC_INBOUND_LOG
path_unzipped_failed_log=${path_base}/shc_failed_log_inspur
path_working=${path_base}/working
path_processed_log=${path_base}/processed_log
path_prod_name_log=${path_base}/product_name_log
path_duration_abnormal_log=${path_base}/duration_abnormal_log
path_unzipped_log=${path_base}/unzipped_log
path_idas_log=${path_base}/idas_log
path_syslog_failure=${path_base}/syslog_failure
path_lock=/tmp/100k-log-lock
platform="" # default is empty for SPR, if it's EMR then it's '_emr'

function extract_to_working_space()
{
	fn=$1
	ext=$2
	rev=0

	echo "Extracting ${fn}.${ext}"

	mkdir ${path_working}/${fn}
	pushd ${path_working}/${fn}

	case ${ext} in
		tar)
			if ! tar xf ${path_zipped_log}/${fn}.${ext}; then
				echo "untar ${fn}.${ext} failed"
				rev=1
			fi
			;;
		tar.xz)
			if ! tar xf ${path_zipped_log}/${fn}.${ext}; then
				echo "untar ${fn}.${ext} failed"
				rev=1
			fi
			;;
		tar.gz)
			if ! tar xf ${path_zipped_log}/${fn}.${ext}; then
				echo "untar ${fn}.${ext} failed"
				rev=1
			fi
			;;
		tgz)
			if ! tar xf ${path_zipped_log}/${fn}.${ext}; then
				echo "untar ${fn}.${ext} failed"
				rev=1
			fi
			;;
		zip)
			if ! unzip ${path_zipped_log}/${fn}.${ext}; then
				echo "unzip ${fn}.${ext} failed"
				rev=1
			fi
			;;
		txt)
			echo "Ignore ${fn}.${ext}"
			rev=1
			;;
		*)
			echo "Can't handle ${fn}.${ext}"
			rev=1
			;;
	esac

	popd

	return $rev
}

function remove_from_working_space()
{
	fn=$1

	echo "Removing ${path_working}/${fn}"
	rm -rf ${path_working}/${fn}
}

function move_to_failed_path()
{
	fn=$1
	plt=$2

	echo "Moving to ${path_unzipped_failed_log}${plt}/${fn}"
	mv ${path_working}/${fn} ${path_unzipped_failed_log}${plt}
}

function move_to_duration_abnormal_path()
{
	fn=$1
	subdir=$2

	echo "Moving to ${path_duration_abnormal_log}/${subdir}/${fn}/"
	rm -rf ${path_working}/${fn}
	touch ${path_duration_abnormal_log}/${subdir}/${fn}
}

function any_failure()
{
	fn=$1
	result=0
	for x in $(find ${path_working}/${fn} -name report.txt); do
		if ! grep "^SHC OVERALL RESULTS" $x -A 2 | grep "^PASSED " > /dev/null; then 
			result=1
		fi
		if grep "^Cache stress test failed" $x; then
			result=1
		fi
	done

	echo "${result}"
}

function any_duration_abnormal()
{
	fn=$1
	result=0
	for x in $(find ${path_working}/${fn} -name report.txt); do
		if ! grep "^DURATION :" $x >/dev/null; then
			result=1
			continue
		fi
		duration_str=$(grep "^DURATION :" $x)
		regex_duration="^DURATION : ([0-9]+) Second.*"
		if [[ ${duration_str} =~ ${regex_duration} ]]; then
			duration=${BASH_REMATCH[1]}
			if [ ${duration} -lt 34200 ]; then
				result=2
			elif [ ${duration} -gt 37800 ]; then
				result=3
			fi
		fi
	done

	echo "${result}"
}

function any_bdat_ewl_captures()
{
	fn=$1
	result=0
	for x in $(find ${path_working}/${fn} -name BDAT.BIN) $(find ${path_working}/${fn} -name platform_bdat.bin); do
		/home/ysheng4/bin/bdat_parser.py --bdatfile $x >/tmp/bdat_data.txt
		if ! grep "Enhanced Warning Log Schema Decode" -A 13 /tmp/bdat_data.txt | grep "^FreeOffset.*No EWL Entries" >/dev/null; then
			result=1
		fi
	done

	echo "${result}"
}

function catch_calprit()
{
	fn=$1
	result=0
	calprits="0xbb52af276b8f082a"

	for calprit in ${calprits}
	do
		if ! grep "PPIN     :" `find ${path_working}/${fn} -name report.txt` | grep ${calprit} >/dev/null; then
			result=1
		fi
	done

	return ${result}
}

function get_product_name()
{
	fn=$1
	result="_NA"
	regex="<info name=\"DMIProductName\" value=\"(.*)\"/>"
	for x in $(find ${path_working}/${fn} -name topology.xml); do
		prod_name=$(grep -e "DMIProductName" $x)
		if [[ ${prod_name} =~ ${regex} ]]; then
			result="_${BASH_REMATCH[1]}"
		fi
	done

	echo "${result}"

}

function compose_and_send()
{
        from=$1
        to=$2
        cc=$3
        subject=$4
        body=$5

        tmpfile=$(mktemp /tmp/XXXXXXXX.eml)
        >$tmpfile
        echo "From: $from" >>$tmpfile
        echo "To: $to" >>$tmpfile
        echo "CC: $cc" >>$tmpfile
        echo "Subject: $subject" >>$tmpfile
        #echo "" >>$tmpfile
        echo "Mime-Version: 1.0" >>$tmpfile
        echo "" >>$tmpfile
        cat $body >>$tmpfile
        /usr/sbin/sendmail -t <$tmpfile
        rm $tmpfile
}

function idas_processing()
{
	folder_name=$(echo $1 | sed 's/\.tar\.xz$//')
	prod_name=$(echo $2 | sed 's/^_//')
	plt=$3
	platform_str="spr"

	case ${plt} in
		_emr)
			platform_str=emr
			;;
		*)
			# default is SPR
			platform_str=spr
			;;
	esac

	fn=$(find ${path_unzipped_log}${plt}/${folder_name} -name idas_sutdump.json)
	if ! [[ ( -n $fn )]]
	then
		return 1
	fi
	fn=$(echo $fn | sed 's/\"/\\\"/g')

	if /home/ysheng4/Downloads/IDASAgentAnalyzer_release/IDASAgentAnalyzer -p ${platform_str} -f $fn -o json >/tmp/idas.decoded.json
	then
		#mr=$(compose_and_send "yongjie sheng <ysheng4@ysheng4-NP5570M5.sh.intel.com>" "yongjie.sheng@intel.com,karthikeyan.selvaraj@intel.com,lokeswar.seetharama.nandhagopal@intel.com,scott.allen.petersen@intel.com" "hongwei.yu@intel.com" "IDAS analyzing result on ${folder_name}" /tmp/idas.decoded.json)
		customer_name=$(python3 /home/ysheng4/bin/customer_name.py ${prod_name})
		mkdir -p ${path_idas_log}${plt}/${customer_name}/${folder_name}
		cat $fn | gzip > ${path_idas_log}${plt}/${customer_name}/${folder_name}/idas_sutdump.json.gz
		cp /tmp/idas.decoded.json ${path_idas_log}${plt}/${customer_name}/${folder_name}
	else
		mr=$(compose_and_send "yongjie sheng <ysheng4@ysheng4-NP5570M5.sh.intel.com>" "yongjie.sheng@intel.com,karthikeyan.selvaraj@intel.com,lokeswar.seetharama.nandhagopal@intel.com,scott.allen.petersen@intel.com" "hongwei.yu@intel.com" "Failed in parsing IDAS log on ${folder_name}" /tmp/idas.decoded.json)
	fi
	rm -f /tmp/idas.decoded.json
}

function share_logs()
{
	regex_date="[A-Za-z0-9\-]+_shc_report.*_([0-9]{4}-[0-9]+)-([0-9]+).*"
	fn=$1
	fn_with_prod_name=$2
	plt=$3
	target_path=${path_prod_name_log}
	
	if [[ $fn =~ $regex_date ]]; then
		ym=${BASH_REMATCH[1]}
		log_date=${ym}-${BASH_REMATCH[2]}
		target_path=${path_prod_name_log}/${log_date}
		mkdir -p ${target_path}
	fi

	cp $fn ${target_path}/${fn_with_prod_name}
	chmod a+r ${target_path}/${fn_with_prod_name}
}


if [ -f ${path_lock} ]; then
	echo "$(date) previous session is still running, yielding ..."
	exit 0
fi

touch ${path_lock}

processed_count=0

# this loop is not re-entry proof, please make sure to hold the ${path_lock}
for x in ${path_zipped_log}/*; do
	filename=$(basename -- $x)
	extname=${filename#*.}
	filename=${filename%%.*}

	regex_p="([A-Za-z0-9\-]+)_shc_report_(.*)"

	if [ -e ${path_processed_log}/${filename}.${extname} ]; then
		continue
	fi

	let processed_count=$processed_count+1

	chmod a+r $x
	if ! extract_to_working_space ${filename} ${extname}; then
		continue
	fi

	report_txt=$(find ${path_working}/${filename} -name report.txt | head -n 1)
	if ! [[ ( -n ${report_txt} ) ]]; then
		echo "No valid report.txt in ${filename}"
		continue
	fi

	cpu_type_str=$(grep "^CPU Type" ${report_txt} | awk -F ":" '{ print $2 }')
	case ${cpu_type_str} in
		*SPR*)
			platform=""
			;;
		*EMR*)
			platform="_emr"
			;;
		*)
			echo "Unknown platform name ${cpu_type_str}"
			continue
			;;
	esac

	catch_calprit ${filename}
	if (( 0 == $? )); then
		echo "Caught a calprit ${filename}"
		mr=$(compose_and_send "yongjie sheng <ysheng4@ysheng4-NP5570M5.sh.intel.com>" "yongjie.sheng@intel.com" "yongjie.sheng@intel.com" "Caught a calprit ${filename}" /home/ysheng4/default-mail.txt)
		touch ${path_unzipped_failed_log}/${filename}.ppin 
	fi

	result=$(any_failure ${filename})
	result_duration="x"
	prod_name=$(get_product_name ${filename})
	prod_name=$(echo $prod_name | sed 's/ /-/g') # replace space with -

	bdat_result=$(any_bdat_ewl_captures ${filename})
	if [ "$bdat_result" != "0" ]; then
		mr=$(compose_and_send "yongjie sheng <ysheng4@ysheng4-NP5570M5.sh.intel.com>" "yongjie.sheng@intel.com" "yongjie.sheng@intel.com" "Got BDAT failure ${filename} with prod name ${prod_name}" /tmp/bdat_data.txt)
	fi

	case ${result} in
		"0")
			result_duration=$(any_duration_abnormal ${filename})
			;;
		"1")
			echo "Got failed log ${filename}"
			move_to_failed_path ${filename} ${platform}
			touch ${path_processed_log}${platform}/${filename}.${extname}
			mr=$(compose_and_send "yongjie sheng <ysheng4@ysheng4-NP5570M5.sh.intel.com>" "yongjie.sheng@intel.com" "hongwei.yu@intel.com" "Got failed log ${filename} with prod name ${prod_name}" /home/ysheng4/default-mail.txt)
			;;
		*)
			echo "Unexpected failure ${result}"
			;;
	esac

	case ${result_duration} in
		"0")
			remove_from_working_space ${filename}
			touch ${path_processed_log}/${filename}.${extname}
			;;
		"1")
			echo "unknown duration error"
			move_to_duration_abnormal_path ${filename} ""
			touch ${path_processed_log}/${filename}.${extname}
			mr=$(compose_and_send "yongjie sheng <ysheng4@ysheng4-NP5570M5.sh.intel.com>" "yongjie.sheng@intel.com" "hongwei.yu@intel.com" "Got unknown duration log ${filename} with prod name ${prod_name}" /home/ysheng4/default-mail.txt)
			;;
		"2")
			echo "duration is too small"
			move_to_duration_abnormal_path ${filename} "less"
			touch ${path_processed_log}/${filename}.${extname}
			;;
		"3")
			echo "duration is too big"
			move_to_duration_abnormal_path ${filename} "more"
			touch ${path_processed_log}/${filename}.${extname}
			;;
		"x")
			remove_from_working_space ${filename}
			touch ${path_processed_log}/${filename}.${extname}
			;;
		*)
			echo "Unexpected failure ${result_duration}"
			remove_from_working_space ${filename}
			;;
	esac

	if [[ ${filename}.${extname} =~ $regex_p ]]; then
		fn_with_prod_name=${BASH_REMATCH[1]}_${prod_name}_shc_report_${BASH_REMATCH[2]}
		echo "${fn_with_prod_name}"
		share_logs $x ${fn_with_prod_name} ${platform}

		folder_name=$(echo ${fn_with_prod_name} | sed 's/\.tar\.xz$//')
		if ! [ -d ${path_unzipped_log}${platform}/${folder_name} ]; then 
			mkdir ${path_unzipped_log}${platform}/${folder_name}
			pushd ${path_unzipped_log}${platform}/${folder_name} 1>/dev/null
			tar xf $x; 
			popd 1>/dev/null 
		fi

		cp $x ${path_working}/tmp
		if ! /usr/bin/python3 /home/ysheng4/bin/shc_analy_detect.py -d ${path_working}/tmp -o /tmp/results.json; then
			echo ${x} >> ${path_syslog_failure}/list.log
			mr=$(compose_and_send "yongjie sheng <ysheng4@ysheng4-NP5570M5.sh.intel.com>" "yongjie.sheng@intel.com" "hongwei.yu@intel.com" "Got syslog failure v2 on ${folder_name}" /tmp/results.json)
			cat /tmp/results.json
		fi
		rm ${path_working}/tmp/*

		idas_processing ${fn_with_prod_name} ${prod_name} ${platform}
	else
		echo "Can't handle name $x"
	fi
done

rm -f ${path_lock}
if [[ "$processed_count" -ne "0" ]]; then
	mr=$(compose_and_send "yongjie sheng <ysheng4@ysheng4-NP5570M5.sh.intel.com>" "yongjie.sheng@intel.com" "yongjie.sheng@intel.com" "Processed ${processed_count} logs $(date)" /home/ysheng4/default-mail.txt)
fi
