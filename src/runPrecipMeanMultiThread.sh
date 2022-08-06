startYears=(1980 1990 2000 2010)
endYears=(1989 1999 2009 2020)


for ((i=0;i<${#startYears[@]};i++)); do
    echo ${startYears[i]} ${endYears[i]}
    nohup echo ${startYears[i]} ${endYears[i]} | python precipMean.py >> precipLog_${startYears[i]}.txt & 
done
