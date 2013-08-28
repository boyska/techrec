#!/bin/bash

# TODO: mettere le vars in un file di configurazione con le funzioni

# Liquidsoap's archive
W_F_BASEDIR="/rec/ror/"

# file to handle
W_F_FIFODIR="/tmp/rorrec/"
W_F_LOGDIR="/var/log/techrec/"

function err {
	echo -e $1
	exit
}

function err2file { 
	echo -e "$1" >> "$2"
}


if test -z "`which ffmpeg`"; then
	err "Install ffmpeg"
fi


if test -z "`which inotifywatch `"; then
    err "Install ffmpeg"
fi


# ESEMPIO: /rec/ror/2012-11/14/rec-2012-11-14-10-00-00-ror.mp3
function get_basedir {
	# $1 anno
	# $2 mese
	# $3 giorno
	echo "${W_F_BASEDIR}/${1}-${2}/${3}/"
}

function get_filename  {
	# $1 anno
	# $2 mese
	# $3 giorno
	# $4 ora
	echo "`get_basedir ${1} ${2} ${3}`/rec-${1}-${2}-${3}-${4}-00-00-ror.mp3"
}

function mp3extractor {
	echo "COMPUTE MP3extator with $1"

	sleep 2 # support inotify latency .. 

	source $1
	# s="$1"
	# e="$2"
	# outfile="$3"


	# Create dir for filess
	outdir="`dirname ${outfile}`"
	mkdir -p ${outdir}/ &>/dev/null
	chmod g+w -R ${outdir}
    logfile="${outfile}.log"

	echo "S: $s -- E: $e -- OUTFILE:${outfile} -- LOGFILE:${logfile}"
	
	if test -z "${s}"  -o  -z "${e}"  -o  -z "${outfile}"; then 
	  err "$0 <starttime> <endtime> <outfile>\n\t$0 2012-11-14-10-20 2012-11-14-12-12 file.mp3\n"
	fi	 
	
	sa=`date -d "${s}" +%Y`
	sm=`date -d "${s}" +%m`
	sg=`date -d "${s}" +%d`
	so=`date -d "${s}" +%H`
	si=`date -d "${s}" +%M`
	s_u=`date -d "${s}" +%s`
	
	ea=`date -d "${e}" +%Y`
	em=`date -d "${e}" +%m`
	eg=`date -d "${e}" +%d`
	eo=`date -d "${e}" +%H`
	ei=`date -d "${e}" +%M`
	e_u=`date -d "${e}" +%s`
	
	if test ${s_u} -gt ${e_u}; then
		err2file "Start TIME >> END TIME" "${logfile}"
		err "Start TIME >> END TIME"
	fi 
	
	# echo "STARTTIME ${sa} ${sm} ${sg} ${so} ${si} ${s_u}"
	# echo "ENDTIME ${ea} ${em} ${eg} ${eo} ${ei} ${e_u}"
	
	# check starttime and endtime dir
	sdir="`get_basedir ${sa} ${sm} ${sg}`"
	edir="`get_basedir ${ea} ${em} ${eg}`"
	
	test ! -d "${sdir}" && err "starttime dir (${sdir}) error"
	test ! -d "${edir}" && err "endtime dir (${edir}) error" 
	
	sf=`get_filename ${sa} ${sm} ${sg} ${so}`
	ef=`get_filename ${ea} ${em} ${eg} ${eo}`

	duration_u=`expr ${e_u} - ${s_u}`
	
	echo ""
	echo -e "\tStart file ${sf}"
	echo -e "\tEnd file ${ef}"
	echo -e "\tDuration: ${duration_u} seconds"
	
	if test ${duration_u} -ge `expr 120 \* 60`; then
		err2file "MP3 richiesto > 2 ore..." "${logfile}"
		err "$0 works only with two files!"
	fi
		
	# Se inizio == fine, mi basta un solo comando
	if test "${sf}" =  "${ef}" ; then
		
		duration=`expr ${ei} - ${si}`
		echo "INIZIO = FINE .. durata (${ei} - ${si}) ${duration}"
		
		cmd="ffmpeg -i ${sf} -acodec copy -t 00:${duration}:00 -ss 00:${si}:00  ${outfile}"
		echo "EXEC: ${cmd}"
	
		${cmd}

		ret=$?
        echo "EXEC RET: $ret"
        err2file "CMD: $cmd -- RET: $ret" "${logfile}"
		[ $ret -ne 0 ] && err2file "ERRORE INIZIO=FINE" "${logfile}"

		rm $1

		exit
	fi 
	
	intro="/tmp/intro-`basename "${outfile}"`.mp3" # Aggiungere casualita' per esecuzioni concorrenti
	coda="/tmp/coda-`basename "${outfile}"`.mp3"
	
	echo ""
	echo "Compute intro.."
	cmd="ffmpeg -i ${sf} -acodec copy -ss 00:${si}:00 -t 00:`expr 60 - ${si}`:00 ${intro}"
	echo "EXEC: ${cmd}"
	
	${cmd}
	ret=$?
    err2file "CMD: $cmd -- RET: $ret" "${logfile}"
	[ $ret -ne 0 ] &&  err "ERRORE ESTRAZIONE INTRO"
			
	echo "Compute end.."
	cmd="ffmpeg -i ${ef} -acodec copy -ss 00:00:00 -t 00:${ei}:00 ${coda}"
	echo "EXEC: ${cmd}"
	
	${cmd}
	ret=$?
    err2file "CMD: $cmd -- RET: $ret" "${logfile}"
	[ $ret -ne 0 ] &&  err "ERRORE ESTRAZIONE CODA"
			
	
	# MERGE
	ffmpeg -i concat:${intro}\|${coda} -acodec copy ${outfile}
	ret=$?
    err2file "CMD: $cmd -- RET: $ret" "${logfile}"
	
	rm ${intro} ${coda}
	[ $ret -ne 0 ] && err2file "ERRORE CONCAT" "${outfile}"

    # DELETE FIFO FILES::::
    
    rm $1
	
	exit
}

#
#
# ::: MAIN :::
#
#

# TODO: GESTIRE IL PROBLEMA DEI PERMESSI
mkdir -p ${W_F_LOGDIR} ${W_F_FIFODIR} &> /dev/null

chown www-data -R ${W_F_LOGDIR} ${W_F_FIFODIR}

if test ! -d "${W_F_BASEDIR}"; then
	err "No AUdio file dir (${W_F_BASEDIR})"
fi 


s="$1"
e="$2"
outfile="$3"

# err "$0 <starttime> <endtime> <outfile>\n\t$0 2012-11-14-10-20 2012-11-14-12-12 file.mp3\n
if test  ! -z "${s}" -a  ! -z "${e}" -a ! -z "${outfile}" ; then 

	echo "direct call"
	
	echo -e "s=\"${s}\"\ne=\"${e}\"\noutfile=\"${outfile}\"\n" > /tmp/tmpfile

	mp3extractor /tmp/tmpfile

	exit
	
fi

echo "No input parameter.. inotify mode"
echo "es: $0 \"2013/04/11 11:25\" \"2013/04/11 11:30\" outfile.mp3"

# esempio:
# mp3wrapper "2012/11/14 10:20" "2012/11/14 10:25"
while [ 1 = 1 ]; do 

	res=`inotifywait ${W_F_FIFODIR} 2> /dev/null` 
	
	echo ${res}
	
	if test `echo ${res} | grep -c CREATE` -eq 0; then
		echo "No relevant task - ${res}"
		continue
	fi 
	
	newfile=`echo ${res} | grep CREATE | sed -e 's/\ CREATE\ //g'`
	echo "Newfile: ${newfile}"
	mp3extractor "${newfile}" >> ${W_F_LOGDIR}/access.log & 

done 

exit 
