for hour in 1 3
do
    for dBZ in $(seq 35 40)
    do
        nohup echo $hour\ $dBZ | python correlation.py >> H$hour\D$dBZ.txt & 
    done
done
