rm -rf ~/logs
ssh jeffreyz@10.10.1.2
scp -r logs jeffreyz@10.10.1.1:
logout
cp ~/logs ~/orca