### 一、主要package版本
#### python:
- langchain==0.2.12  
- streamlit  
- subprocess
#### java:
- jdk18
### 二、配置ASDUS切分脚本路径
#### 方法一： 修改ASDUS代码路径
1、下载原java项目  
2、对DomainIndenpendentModel.java文件的以下路径修改成自定义路径  
![img.png](img.png)  
3、需要下载对应的jar包放置在Lib文件夹，可以直接从```html_agent_ui```文件取  
4、重新打包jar包放置到```html_agent_ui```原位置,按照顺序执行以下命令打包：  
```jar cvfe DomainIndependentModel.jar com.lab.model.DomainIndependentModel -C out .```  
```javac -d out -cp "lib/*" src/com/lab/model/*.java src/com/lab/utils/*.java```  
```javac -cp "lib/*" -d out src/com/lab/utils/*.java src/com/lab/model/DomainIndependentModel.java```

#### 方法二：直接在本地创建对应文件夹
1、用以下路径创建文件夹对应strParentFolder：  
```D:\WorkSpace\PycharmFile\html_agent_ui\data```  
2、并在以上文件夹内放置```english.conll.4class.distsim.crf.ser.gz```文件

### 三、启动  
1、run ```src/cleanup_url/Lab_Web_Service_KMeans.ipynb```  
2、在终端执行 ```streamlit run homepage.py``` 启动UI 进行问答

