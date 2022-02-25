pytest --workers 10
if [[ $? -eq 0 ]]; then
    echo "Unit tests pass"
else
    echo "Unit tests failure"
    exitStatus=1
fi

exit ${exitStatus}