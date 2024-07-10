cd frontend/
npm run build
rm ../ether_ghost/public -rf
mv dist ../ether_ghost/public
cd ../ether_ghost
# TODO: build etherGhost packages
