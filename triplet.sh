m=/home/arbazk/MTT/UniMelb/test/Felix_last/trunk/resources/tuw_chunked_data
mv $m.txt /home/arbazk/MTT/UniMelb/test/Felix_last/trunk/resources/tuw_chunked.txt
mv $m.ann /home/arbazk/MTT/UniMelb/test/Felix_last/trunk/resources/tuw_chunked.ann
cp /home/arbazk/MTT/UniMelb/newData/Chunked/description/chunked$1.txt $m.txt
cp /home/arbazk/MTT/UniMelb/newData/Chunked/description/chunked$1.ann $m.ann
cd /home/arbazk/MTT/UniMelb/test/Felix_last/trunk/bin/
python ler.py
crf_test -m model test > result0
perl -pne "s/\t/ /g" result0 > /home/arbazk/MTT/UniMelb/Code/Dependencies\ exploitation/test_cases/result$1.txt
mv /home/arbazk/MTT/UniMelb/test/Felix_last/trunk/resources/tuw_chunked.txt $m.txt
mv /home/arbazk/MTT/UniMelb/test/Felix_last/trunk/resources/tuw_chunked.ann $m.ann
cd /home/arbazk/MTT/UniMelb/Code/stanford-parser-2013-04-05/ 
java ParserDemo /home/arbazk/MTT/UniMelb/newData/campus$1.txt > /home/arbazk/MTT/UniMelb/Code/Dependencies\ exploitation/test_cases/campus$1.in
cd /home/arbazk/MTT/UniMelb/Code/Dependencies\ exploitation/
python gitStore/extract_LE.py test_cases/campus$1.in test_cases/result$1.txt 
 
