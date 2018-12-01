echo "Generate WHL file"
cd wc3inside && python3 setup.py sdist bdist_wheel && cd ..

