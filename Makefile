deploy:
	cd conf/apps && cp apps.yaml apps.prod && sed -i '' -e 's/,on/,623/g' -e 's/,off/,on/g' -e 's/,623/,off/g' apps.prod	
	ssh root@10.0.0.101 'rm -rf /root/config/appdaemon/apps/*'
	scp -r ~/projects/appdaemon/conf/apps/ root@10.0.0.101:/root/config/appdaemon/apps/
	ssh root@10.0.0.101 'mv /root/config/appdaemon/apps/apps/apps.prod /root/config/appdaemon/apps/apps/apps.yaml'
	ssh root@10.0.0.101 'ha addon restart a0d7b954_appdaemon'