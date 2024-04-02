deploy:
	cd conf/apps && cp apps.yaml apps.prod && sed -i '' -e 's/,on/,623/g' -e 's/,off/,on/g' -e 's/,623/,off/g' apps.prod	
	ssh yepdev@10.0.0.100 'rm -rf /home/yepdev/apps/appdaemon/conf/apps/*'
	scp -r ~/projects/appdaemon/conf/apps/ yepdev@10.0.0.100:/home/yepdev/apps/appdaemon/conf/
	ssh yepdev@10.0.0.100 'mv /home/yepdev/apps/appdaemon/conf/apps/apps.prod /home/yepdev/apps/appdaemon/conf/apps/apps.yaml'

deploy-ha:
	cd conf/apps && cp apps.yaml apps.prod && sed -i '' -e 's/,on/,623/g' -e 's/,off/,on/g' -e 's/,623/,off/g' apps.prod	
	ssh root@10.0.0.101 'rm -rf /addon_configs/a0d7b954_appdaemon/apps/*'
	scp -r ~/projects/appdaemon/conf/apps/ root@10.0.0.101:/addon_configs/a0d7b954_appdaemon/apps/
	ssh root@10.0.0.101 'mv /addon_configs/a0d7b954_appdaemon/apps/apps/apps.prod /addon_configs/a0d7b954_appdaemon/apps/apps/apps.yaml'
	ssh root@10.0.0.101 'ha addon restart a0d7b954_appdaemon'