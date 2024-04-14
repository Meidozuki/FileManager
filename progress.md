v0.1 roadmap

1. ~~从本地读取到df~~
2. ~~df转换为tableview所需~~
3. ~~加上view剩下的~~
4. view的美观调整先剩下
5. ~~找到一个稳定的从TableItem到view的显示~~
6. ~~之后才能考虑对tags进行过滤~~
7. ~~增加、设置图片、保存、读取功能~~


最初使用TableWidget和TableWidgetItem，对于Button用setCellWidget

但是发现模型比较复杂，需要进一步解耦

于是用了TableView和StandardItemModel来显示

通信逻辑分以下几层：

用户交互，Qt的Signal和Slot(Qt到View层)

数据显示，Qt的TableView和Model(View到Viewmodel层)

数据压缩和存储，Viewmodel层到Model层

v0.2 roadmap

1. ~~增加working dir，文件路径用偏移量表示~~
2. 增加添加文件夹功能
3. ~~对于失效文件的处理，目前直接报错，不显示~~
4. ~~增加config.json~~和savedata目录
5. ~~自动检测图片~~

