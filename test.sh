echo "Running Tests"
for file in ./tests/*.py;
do
    echo "Executing $file";
    python3 $file
done
