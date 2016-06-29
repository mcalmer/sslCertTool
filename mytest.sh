#!/bin/bash
set -xe

function error() {
    echo "failed"
    exit 1
}

rm -rf build1/
./cert-tool genca -d build1 -p hallo --set-common-name "SUSE CA" --set-state Bavaria --set-city Nuremberg --set-org "SUSE LLC" --set-email "suse@suse.com" --set-country "DE" -v --bits 4096 --cert-expiration 7000 --md sha512 || error
./cert-tool genserver -d build1 -p hallo --set-hostname "lesch.suse.de" --set-state Bavaria --set-city Nuremberg --set-org "SUSE LLC" --set-email "suse@suse.com" --set-country "DE" -v --bits 4096 --cert-expiration 700 --md sha512 --add-cname "www.suse.de" || error
./cert-tool genserver -d build1 -p hallo --set-hostname "lesch.suse.de" --set-state Bavaria --set-city Nuremberg --set-org "SUSE LLC" --set-email "suse@suse.com" --set-country "DE" -v --bits 4096 --cert-expiration 700 --md sha512 --add-cname "www.suse.de" || error
test -f build1/CA-PRIVATE-SSL-KEY || error
test -f build1/CA-TRUSTED-SSL-CERT || error
test -f build1/ca-trusted-ssl-cert-1.0-1.noarch.rpm || error
test -f build1/ca-trusted-ssl-cert-1.0-1.src.rpm || error
test -f build1/lesch/server.crt || error
test -f build1/lesch/server.csr || error
test -f build1/lesch/server.key || error
test -f build1/lesch/ssl-servercert-key-pair-lesch-1.0-2.noarch.rpm || error
test -f build1/lesch/ssl-servercert-key-pair-lesch-1.0-2.src.rpm || error
test -f build1/lesch/ssl-servercert-key-pair-lesch-1.0-1.noarch.rpm || error
test -f build1/lesch/ssl-servercert-key-pair-lesch-1.0-1.src.rpm || error
rm -rf build1/
