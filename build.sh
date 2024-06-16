cd frontend/
npm run build
rm ../guiren/public -rf
mv dist ../guiren/public
cd ../guiren
# TODO: build guiren packages
