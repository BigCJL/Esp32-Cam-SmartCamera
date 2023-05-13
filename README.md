# esp32-webcam-apps
基于esp32cam的智能网络摄像服务，micropython+python/c++服务端+java客户端，部署到阿里云公网服务器。

# 文件夹说明
Esp32_App：micropython代码，需要在esp32-cam板子上运行  
Client_App：python编写的上位机客户端  
esp32-server:Java编写的服务端代码，已部署至公网，可访问：http://139.224.133.71:9999/record/all， 查看操作记录和最新存储的视频记录。

![image](https://github.com/BigCJL/Esp32-Cam-SmartCamera/assets/79361803/6725927b-2e54-4cc6-b9cd-1c1e3f84f090)


# 使用方法
esp32-cam正确连接两个mg90s数字舵机
![image](https://github.com/BigCJL/Esp32-Cam-SmartCamera/assets/79361803/0791847a-a2f6-46de-a4fb-5a11e8f52068)

使用thonny将Esp32_App文件夹下的代码写入单片机，命名为main.py即可上电自动执行，Cam.py中，需要修改上位机的IP为自己的电脑、同时修改wifi账号和密码。
闪光灯闪烁一下，则说明连接成功。  

* 上位机软件界面如图，提供了保存、遥控、自动追踪等功能，同时可以自动上传操作记录和视频到云端。
![image](https://github.com/BigCJL/Esp32-Cam-SmartCamera/assets/79361803/cb1fbbd7-6bf1-445d-98d3-4c9c2d72242f)

