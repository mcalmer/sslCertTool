#!/bin/bash
set -e

function error() {
    echo "TEST FAILED"
    exit 1
}

TESTDIR1=testdir1
TESTDIR2=testdir2
TESTDIR3=testdir3

rm -rf $TESTDIR1/
rm -rf $TESTDIR2/
rm -rf $TESTDIR3/
./cert-tool genca -d $TESTDIR1 -p hallo --set-common-name "SUSE CA" --set-state Bavaria --set-city Nuremberg --set-org "SUSE LLC" --set-email "suse@suse.com" --set-country "DE" -v --bits 4096 --cert-expiration 7000 --md sha512 || error
./cert-tool genserver -d $TESTDIR1 -p hallo --set-hostname "lesch.suse.de" --set-state Bavaria --set-city Nuremberg --set-org "SUSE LLC" --set-email "suse@suse.com" --set-country "DE" -v --bits 4096 --cert-expiration 700 --md sha512 --add-cname "www.suse.de" || error
./cert-tool genserver -d $TESTDIR1 -p hallo --set-hostname "lesch.suse.de" --set-state Bavaria --set-city Nuremberg --set-org "SUSE LLC" --set-email "suse@suse.com" --set-country "DE" -v --bits 4096 --cert-expiration 700 --md sha512 --add-cname "www.suse.de" || error
test -f $TESTDIR1/CA-PRIVATE-SSL-KEY || error
test -f $TESTDIR1/CA-TRUSTED-SSL-CERT || error
test -f $TESTDIR1/ca-trusted-ssl-cert-1.0-1.noarch.rpm || error
test -f $TESTDIR1/ca-trusted-ssl-cert-1.0-1.src.rpm || error
test -f $TESTDIR1/lesch/server.crt || error
test -f $TESTDIR1/lesch/server.csr || error
test -f $TESTDIR1/lesch/server.key || error
test -f $TESTDIR1/lesch/ssl-servercert-key-pair-lesch-1.0-2.noarch.rpm || error
test -f $TESTDIR1/lesch/ssl-servercert-key-pair-lesch-1.0-2.src.rpm || error
test -f $TESTDIR1/lesch/ssl-servercert-key-pair-lesch-1.0-1.noarch.rpm || error
test -f $TESTDIR1/lesch/ssl-servercert-key-pair-lesch-1.0-1.src.rpm || error

mkdir $TESTDIR2
cp $TESTDIR1/CA-* $TESTDIR2/
./cert-tool genca -d $TESTDIR2 --rpm-only -v || error
mkdir $TESTDIR2/lesch
cp $TESTDIR1/lesch/ssl-servercert-key-pair-lesch-1.0-* $TESTDIR2/lesch/
cp $TESTDIR1/lesch/server.{crt,key} $TESTDIR2/lesch/
./cert-tool genserver -d $TESTDIR2 --rpm-only -v --set-hostname "lesch.suse.de" || error
./cert-tool genserver -d $TESTDIR2 --rpm-only --set-hostname "" 2>&1 | grep "Require a machine name" >/dev/null || error

mkdir $TESTDIR3
mkdir $TESTDIR3/lesch
./cert-tool genca -d $TESTDIR3 --rpm-only 2>&1 | grep "does not exist" >/dev/null || error
./cert-tool genserver -d $TESTDIR3 --rpm-only 2>&1 | grep "does not exist" >/dev/null || error
rm -rf $TESTDIR1/
rm -rf $TESTDIR2/
rm -rf $TESTDIR3/
echo "SUCCESS"
