deploy:
	ssh root@10.0.0.101 'rm -rf /root/config/appdaemon/apps/*'
	scp -r ~/projects/appdaemon/conf/apps/ root@10.0.0.101:/root/config/appdaemon/apps/