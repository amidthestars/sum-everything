python3 -m flake8 "." --config="flake8.cfg"
if [[ $? -eq 0 ]]; then
    echo "Style passed! :3"
else
    echo "Style failed. :("
    exitStatus=1
fi
exit ${exitStatus}