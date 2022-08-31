key = 0

set terminal wxt enhanced font 'Latin Modern Sans,10' persist

$data << EOD
0 73
1 8
2 32
3 45
4 106
5 10
6 14
7 5
8 120
9 0
10 0
11 69
12 55
13 59
14 71
15 23
16 13
17 47
18 62
19 83
20 79
21 14
22 2
23 4
24 2
25 5
EOD

stats "$data" using 1:2 name 'data' nooutput

set boxwidth 0.5
set style fill solid 0.8

set style line 1 lt 1 lc rgb '#c0392b' # pomegranate red
set style line 2 lt 1 lc rgb '#2980b9' # belize hole blue

set xtics ("A" 0, "B" 1, "C" 2, "D" 3, "E" 4, "F" 5, "G" 6, "H" 7, "I" 8, "J" 9, "K" 10, "L" 11, "M" 12, "N" 13, "O" 14, "P" 15, "Q" 16, "R" 17, "S" 18, "T" 19, "U" 20, "V" 21, "W" 22, "X" 23, "Y" 24, "Z" 25)

set xrange [ data_min_x - 0.5 : data_max_x + 0.5 ]
set yrange [ 0 : ceil(data_max_y * 1.2) ]
plot "$data" using ((ceil($1)+key)%26):($2) with boxes title "Letter count" linestyle 1
