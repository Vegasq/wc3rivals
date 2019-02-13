echo "Generate WHL file"
cd wc3rivals_backend && python3 setup.py sdist bdist_wheel && cd ..
echo "Build VUE app"
git rm -r wc3rivals_vue/dist/
cd wc3rivals_vue &&  npm run build && cd ..
git add wc3rivals_vue/dist/
git add wc3rivals_backend/dist/

echo "Now run docker-compose up --build"
