for hour in 1 3
do
    for dBZ in $(seq 35 40)
    do
        nohup echo $hour\ $dBZ | python correlationLog.py >> H$hour\D$dBZ_log.txt & 
    done
done
