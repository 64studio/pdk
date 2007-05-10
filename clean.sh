# $Progeny$

find . -name "*.pyc" -o -name "*.pyo" -o -name "*~" \
    -o -name "*.snap.tar.gz" -o -name "*.html" -o -name "*.fw.sh" \
    -o -name "*.lis" | xargs -r rm -f
rm -f pdk.1
rm -rf build/
rm -rf atest.log.d
rm -f atest.log future.log
[ -e debian/files ] && fakeroot ./debian/rules clean || true

# vim:set ai et sw=4 ts=4 tw=75:
