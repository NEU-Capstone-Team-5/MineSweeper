echo " ------------ Running Tests Script ------------"
while test $# -gt 0; do
  case "$1" in
    -h|--help)
      echo "$0 - attempt to capture frames from multiple sensors"
      echo " "
      echo "$0 [options]"
      echo " "
      echo "options:"
      echo "-h, --help                show brief help"
      echo "-c, --clean               clears the data directory"
      exit 0
      ;;
    -c|--clean)
      echo "Attempting to clear data directory..."
      read -p "Are you sure? " -n 1 -r
      echo
      if [[ ! $REPLY =~ [Yy]$ ]]
      then
        echo "Cancelled clearing data directory"
        exit 1 || return 1 # handle exits from shell or function but don't exit interactive shell
      fi

      echo "Clearing data directory..."
      rm -r ./data
      exit 0 
      ;;
    *)
      break
      ;;
  esac
done

for file in ./tests/*.py;
  do
    echo "Executing $file";
    python3 $file
done


