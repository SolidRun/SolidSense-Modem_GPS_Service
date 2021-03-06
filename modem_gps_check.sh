#!/bin/sh

count=0
SLEEP=0.1
MAX_COUNT=200

while (/bin/true) ; do
	val=$(journalctl -xab -u modem_gps.service | grep MODEM_OK)
	if [ -n "${val}" ]; then
		break
	else
		sleep "${SLEEP}"
		count=$((count + 1))
	fi
	if [ "${count}" -gt "${MAX_COUNT}" ] ; then
		slept=$(echo "${SLEEP} * ${MAX_COUNT}" | bc)
		logger -i --priority crit --tag modem_gps_check "MAX_COUNT:SLEEP:TIME <${MAX_COUNT}:${SLEEP}:${slept}s> exceeded!"
		break
	fi
done
