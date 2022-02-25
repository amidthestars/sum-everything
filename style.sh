python3 -m flake8 "." --config=".ci/flake8.cfg"
if [[ $? -eq 0 ]]; then
    echo "Python style passed! :3"
else
    echo 'Python style failed! ~~~~~~~~~~ Run:  "autopep8 --global-config .ci/flake8.cfg --max-line-length 100 --in-place --recursive -a ."'
    exitStatus=1
fi

npx prettier --config ".ci/.prettierrc" --check .
if [[ $? -eq 0 ]]; then
    echo "JS/CSS/HTML style passed! :3"
else
    echo 'JS/CSS/HTML style failed! ~~~~~~~~~~ Run:  "npx prettier --config .ci/.prettierrc --write ."'
    exitStatus=1
fi

exit ${exitStatus}