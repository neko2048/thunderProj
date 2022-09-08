for dBZ in 38 40 
do
	for prMin in 0 10 20 30 40 50 60 70 80 90
    do
		prMax=$(($prMin+10))
		echo 1 $dBZ $prMin $prMax 
		echo 1 $dBZ $prMin $prMax | python geoCorrelation.py #>> H$hour\D$dBZ$prMax$prMin.txt
	done
done
