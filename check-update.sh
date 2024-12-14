#!/bin/sh
curl -s -L -A 'Mozilla/5.0 (X11; Linux x86_64)' http://www.stunnel.org/downloads.html |grep -E "href=.*stunnel-" |grep -v latest |sed -e "s,.*stunnel-,,;s,\.tar.*,," | tail -n1
